print(__file__)

"""Set up default complex devices"""

import time
from ophyd import Component, Device, DeviceStatus
from ophyd import EpicsMotor, EpicsScaler
from ophyd import EpicsSignal, EpicsSignalRO, EpicsSignalWithRBV
from ophyd import PVPositioner, PVPositionerPC, SoftPositioner
from ophyd import AreaDetector, PcoDetectorCam
from ophyd import SingleTrigger, ImagePlugin, HDF5Plugin
from ophyd.areadetector.filestore_mixins import FileStoreHDF5IterativeWrite
from APS_BlueSky_tools.devices import *


# TODO: import from APS_BlueSky_tools.devices
class EpicsMotorWithDial(EpicsMotor):
    """
    add motor record's dial coordinates to EpicsMotor
    
    USAGE::
    
        m1 = EpicsMotorWithDial('xxx:m1', name='m1')
    
    """
    dial = Component(EpicsSignal, ".DRBV", write_pv=".DVAL")
    raw = Component(EpicsSignal, ".RRBV", write_pv=".RVAL")


# TODO: fix upstream!!
class NullMotor(SoftPositioner):
    @property
    def connected(self):
        return True
