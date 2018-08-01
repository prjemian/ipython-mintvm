print(__file__)

"""Set up default complex devices"""

import time
from ophyd import Component, Device, DeviceStatus, Signal
from ophyd import EpicsMotor, EpicsScaler
from ophyd.scaler import ScalerCH
from ophyd import EpicsSignal, EpicsSignalRO, EpicsSignalWithRBV
from ophyd import PVPositioner, PVPositionerPC, SoftPositioner
from ophyd import AreaDetector, PcoDetectorCam
from ophyd import SingleTrigger, ImagePlugin, HDF5Plugin
from ophyd.areadetector.filestore_mixins import FileStoreHDF5IterativeWrite

import APS_BlueSky_tools.devices as APS_devices
import APS_BlueSky_tools.plans as APS_plans

# TODO: fix upstream!!
class NullMotor(SoftPositioner):
    @property
    def connected(self):
        return True
