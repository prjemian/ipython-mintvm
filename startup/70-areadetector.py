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
        'HDF1:', 
        root='/',                               # for databroker
        write_path_template=image_file_path,    # for EPICS AD,
        reg=db.reg
    )


try:

    simdet = MyHdf5Detector('13SIM1:', name='simdet')
    simdet.read_attrs = ['hdf1', 'cam']
    simdet.hdf1.read_attrs = []  # 'image' gets added dynamically

except TimeoutError:
    print("Could not connect 13SIM1: sim detector")

"""
example::

    simdet.describe_configuration()
    RE(bp.count([simdet]))
    cfg = simdet.hdf1.read_configuration()
    file_name = cfg["simdet_hdf1_full_file_name"]['value']
    cfg.get('simdet_image', 'not found')
    data_uid = cfg['simdet_image']['value']
    db.reg.retrieve(data_uid)                                                    

    db[-1].data("simdet_image")
    images = list(_)
    images[0]
    images[0][0]
    simdet.cam.num_images.set(2)
    RE(bp.count([simdet]))
    db[-1].data("simdet_image")
    images = list(_)
    images[0][0]
    images[0]
    images[0][1]


"""
