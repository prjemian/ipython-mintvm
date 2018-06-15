print(__file__)

"""ADSimDetector"""

from ophyd import SingleTrigger, AreaDetector, SimDetector
from ophyd import HDF5Plugin, ImagePlugin
from ophyd.areadetector.trigger_mixins import SingleTrigger
from ophyd.areadetector.filestore_mixins import FileStoreHDF5IterativeWrite
from ophyd import Component, Device, EpicsSignalWithRBV
from ophyd.areadetector import ADComponent


image_file_path = "/tmp/simdet/%Y/%m/%d/"


class MyHDF5Plugin(HDF5Plugin, FileStoreHDF5IterativeWrite):
    """
    """
    

class MySingleTriggerHdf5SimDetector(SingleTrigger, SimDetector): 
       
    image = Component(ImagePlugin, suffix="image1:")
    hdf1 = Component(
        MyHDF5Plugin,
        suffix='HDF1:', 
        root='/',                               # for databroker
        write_path_template=image_file_path,    # for EPICS AD
    )

try:
    _ad_prefix = "13SIM1:"
    adsimdet = MySingleTriggerHdf5SimDetector(_ad_prefix, name='adsimdet')
    adsimdet.read_attrs.append("hdf1")

except TimeoutError:
    print(f"Could not connect {_ad_prefix} sim detector")


def demo_count_simdet(det=None, count_time=0.2):
    det.cam.stage_sigs["acquire_time"] = count_time
    det.describe_configuration()
    RE(bp.count([det]))
    for i, ev in enumerate(db[-1].events()):
        print(i, ev["data"][det.hdf1.name+"_full_file_name"])


def ad_continuous_setup(det, acq_time=0.1, acq_period=0.005):
    det.cam.acquire_time.put(acq_time)
    det.cam.acquire_period.put(acq_period)
    det.cam.image_mode.put("Continuous")
