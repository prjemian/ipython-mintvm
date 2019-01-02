print(__file__)

"""ADSimDetector"""

from ophyd import SingleTrigger, AreaDetector, SimDetector
from ophyd import HDF5Plugin, ImagePlugin
from ophyd.areadetector.trigger_mixins import SingleTrigger
from ophyd.areadetector.filestore_mixins import FileStoreIterativeWrite
from ophyd import Component, Device, EpicsSignalWithRBV
from ophyd.areadetector import ADComponent


image_file_path = "/tmp/simdet/%Y/%m/%d/"


class myHdf5EpicsIterativeWriter(
        APS_devices.AD_EpicsHdf5FileName, 
        FileStoreIterativeWrite): pass
class myHDF5FileNames(HDF5Plugin, myHdf5EpicsIterativeWriter): pass
    

class MySingleTriggerHdf5SimDetector(SingleTrigger, SimDetector): 
       
    image = Component(ImagePlugin, suffix="image1:")
    hdf1 = Component(
        myHDF5FileNames,
        suffix='HDF1:', 
        root='/',                               # for databroker
        write_path_template=image_file_path,    # for EPICS AD
    )


try:
    _ad_prefix = "13SIM1:"
    
    # Preset the FrameType mbbo records for the HDF5 addresses
    # to store each type of acquisition.  Coordinates with
    # configuration in the attributes and layout XML files for AD.
    class MyMbboLabels(Device):
        label0 = Component(EpicsSignal, ".ZRST")
        label1 = Component(EpicsSignal, ".ONST")
        label2 = Component(EpicsSignal, ".TWST")
    mbbo     = MyMbboLabels(_ad_prefix+"cam1:FrameType",     name="mbbo")
    mbbo_rbv = MyMbboLabels(_ad_prefix+"cam1:FrameType_RBV", name="mbbo_rbv")
    for obj in (mbbo, mbbo_rbv):                # original values
        obj.label0.put("/exchange/data")        # Normal
        obj.label1.put("/exchange/data_dark")   # Background
        obj.label2.put("/exchange/data_white")  # FlatField
    del mbbo, mbbo_rbv, obj, MyMbboLabels       # dispose temporary items
        
    adsimdet = MySingleTriggerHdf5SimDetector(_ad_prefix, name='adsimdet')
    adsimdet.read_attrs.append("hdf1")
    # option: 
    # del adsimdet.hdf1.stage_sigs["array_counter"]
    adsimdet.hdf1.stage_sigs["file_template"] = '%s%s_%3.3d.h5'
    # adsimdet.hdf1.file_name.put("test")

except TimeoutError:
    print(f"Could not connect {_ad_prefix} sim detector")


def demo_count_simdet(det, count_time=0.2):
    det.cam.stage_sigs["acquire_time"] = count_time
    RE(bp.count([det]))


def ad_continuous_setup(det, acq_time=0.1, acq_period=0.005):
    det.cam.acquire_time.put(acq_time)
    det.cam.acquire_period.put(acq_period)
    det.cam.image_mode.put("Continuous")
