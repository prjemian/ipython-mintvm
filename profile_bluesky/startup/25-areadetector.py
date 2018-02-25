print(__file__)

from ophyd import SingleTrigger, AreaDetector, SimDetector, HDF5Plugin, ImagePlugin
from ophyd.areadetector.trigger_mixins import SingleTrigger
from ophyd.areadetector.filestore_mixins import FileStoreHDF5IterativeWrite
from ophyd import Component, Device, EpicsSignalWithRBV
from ophyd.areadetector import ADComponent


image_file_path = "/tmp"


class MyHDF5Plugin(HDF5Plugin, FileStoreHDF5IterativeWrite):
    
    file_number_sync = None     # AD 2.5
    
    def get_frames_per_point(self):     # AD 2.5
        return self.parent.cam.num_images.get()


class MyHdf5Detector(SimDetector, SingleTrigger):
    
    image = Component(ImagePlugin, suffix="image1:")
    hdf1 = Component(
        MyHDF5Plugin,
        suffix='HDF1:', 
        root='/',                               # for databroker
        write_path_template=image_file_path,    # for EPICS AD,
        reg=db.reg
    )

# trigger first, then base class
# otherwise, cannot use continuous mode for detector
class MyPlainSimDetector(SingleTrigger, SimDetector):
    image = Component(ImagePlugin, suffix="image1:")


try:
    simdet = MyHdf5Detector('13SIM1:', name='simdet')
    simdet.read_attrs = ['hdf1', 'cam']
    simdet.hdf1.read_attrs = []  # 'image' *should be* added dynamically
except TimeoutError as msg:
    print("Could not connect 13SIM1: simdet detector: ", msg)

try:
    adsimdet = MyPlainSimDetector(
        '13SIM1:', 
        name='adsimdet',
        read_attrs=['cam', 'image'])
    # adsimdet.read_attrs = ['cam', 'image']
    # https://github.com/BCDA-APS/APS_BlueSky_tools/issues/9
    adsimdet.cam.read_attrs = []
    adsimdet.image.read_attrs = ['array_counter']    
except TimeoutError as msg:
    print("Could not connect 13SIM1: adsimdet detector: ", msg)


def demo_count_simdet():
    simdet.describe_configuration()
    RE(bp.count([simdet]))
    cfg = simdet.hdf1.read_configuration()
    file_name = cfg["simdet_hdf1_full_file_name"]['value']
    for ev in db[-1].events():
        print(ev["data"][simdet.hdf1.name+"_full_file_name"])


def ad_continuous_setup(det, acq_time=0.1, acq_period=0.005):
    det.cam.acquire_time.put(acq_time)
    det.cam.acquire_period.put(acq_period)
    det.cam.image_mode.put("Continuous")


def setup_det_trigger(motor, det, motion_calc, trigger_calc, increment=2.5):
    """
    Prepare to trigger simulated area detector when motor is moved.
    Trigger only in positive direction.
    motion_calc.B is increment of motor motion that triggers an image frame.
    """
    motion_calc.reset()
    motion_calc.desc.put("motion increment")
    motion_calc.channels.A.input_pv.put(motor.user_readback.pvname)
    motion_calc.channels.B.value.put(increment)
    motion_calc.calc.put("floor(A/B)")
    motion_calc.oopt.put("Every Time")
    motion_calc.scan.put("I/O Intr")

    trigger_calc.reset()
    trigger_calc.desc.put("detector trigger")
    trigger_calc.channels.A.input_pv.put(trigger_calc.channels.B.value.pvname)
    trigger_calc.channels.B.input_pv.put(motion_calc.val.pvname)
    trigger_calc.channels.C.input_pv.put(motor.direction_of_travel.pvname)
    trigger_calc.calc.put("C&&(A!=B)")
    trigger_calc.oopt.put("Transition To Non-zero")
    trigger_calc.outn.put(det.cam.prefix + "Acquire")
    trigger_calc.scan.put("I/O Intr")
    
    det.cam.image_mode.put("Single")
    det.hdf1.enable.put("Disable")
    """
    typical acquisition sequence:
    
        det_pre_acquire(det)
        det.cam.acquire.put()       # as many frames as needed
        det_post_acquire(det)
    """


def det_pre_acquire(det, max_frames=10000):
    # enable the HDF5 plugin
    det.hdf1.enable.put("Enable")
    
    # prepare to capture a stream of image frames in one array
    det.hdf1.file_write_mode.put("Capture")
    
    # collect as many as this number
    det.hdf1.num_capture.put(max_frames)
    
    # start to capture the stream
    det.hdf1.capture.put("Capture")


def det_post_acquire(det):
    # stream is now fully captured
    det.hdf1.capture.put("Done")
    
    # write the HDF5 file
    det.hdf1.write_file.put(1)
    
    # reset the HDF5 plugin to some default settings
    det.hdf1.file_write_mode.put("Single")
    det.hdf1.num_capture.put(1)
    det.hdf1.enable.put("Disable")

try:
    setup_det_trigger(m3, simdet, calcs.calc3, calcs.calc4)
except NameError:
    pass

# TODO: set up a flyer to move the motor, acquire images, and finish up
