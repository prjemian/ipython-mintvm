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
