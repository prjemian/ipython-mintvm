print(__file__)

from ophyd import SingleTrigger, AreaDetector, SimDetector
from ophyd.areadetector.plugins import HDF5Plugin
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
    
    hdf1 = Component(
        MyHDF5Plugin,
        suffix='HDF1:', 
        root='/',                               # for databroker
        write_path_template=image_file_path,    # for EPICS AD,
        reg=db.reg
    )


try:

    simdet = MyHdf5Detector('13SIM1:', name='simdet')
    simdet.read_attrs = ['hdf1', 'cam']
    simdet.hdf1.read_attrs = []  # 'image' gets added dynamically
    # put these things in each event document
    # only first 3 characters show in the LiveTable callback.  So what?
    simdet.hdf1.read_attrs.append("file_name")
    simdet.hdf1.read_attrs.append("file_path")
    simdet.hdf1.read_attrs.append("full_file_name")

except TimeoutError:
    print("Could not connect 13SIM1: sim detector")


"""
example::

    simdet.describe_configuration()
    RE(bp.count([simdet]))
    cfg = simdet.hdf1.read_configuration()
    file_name = cfg["simdet_hdf1_full_file_name"]['value']
    for ev in db[-1].events():
        print(ev["data"][simdet.hdf1.name+"_full_file_name"])

"""
