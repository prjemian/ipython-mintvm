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
from APS_BlueSky_tools.devices import userCalcsDevice
# from APS_BlueSky_tools.synApps_ophyd import *


class MotorDialValuesDevice(Device):
    value = Component(EpicsSignalRO, ".DRBV")
    setpoint = Component(EpicsSignal, ".DVAL")


class MyEpicsMotorWithDial(EpicsMotor):
    dial = Component(MotorDialValuesDevice, "")


class ServoRotationStage(EpicsMotor):
    """extend basic motor support to enable/disable the servo loop controls"""
    
    # values: "Enable" or "Disable"
    servo = Component(EpicsSignal, ".CNEN", string=True)


# TODO: fix upstream!!
class NullMotor(SoftPositioner):
    @property
    def connected(self):
        return True
