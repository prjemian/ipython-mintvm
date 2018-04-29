print(__file__)

"""ophyd Flyer example with the busy record fly scan"""

import os
from enum import Enum


logger = logging.getLogger(os.path.split(__file__)[-1])

BUSY_PV = 'prj:mybusy'
TIME_WAVE_PV = 'prj:t_array'
X_WAVE_PV = 'prj:x_array'
Y_WAVE_PV = 'prj:y_array'


class BusyStatus(str, Enum):
    busy = "Busy"
    done = "Done"


class MyCalc(Device):
    """swait record simulates a signal"""
    result = Component(EpicsSignal, "")
    calc = Component(EpicsSignal, ".CALC")
    proc = Component(EpicsSignal, ".PROC")


class MyWaveform(Device):
    """waveform records store fly scan data"""
    wave = Component(EpicsSignalRO, "")
    number_elements = Component(EpicsSignalRO, ".NELM")
    number_read = Component(EpicsSignalRO, ".NORD")


class BusyFlyerDevice(Device):
    """
    support a fly scan that is triggered by a busy record
    """

    busy = Component(EpicsSignal, BUSY_PV, string=True)
    time = Component(MyWaveform, TIME_WAVE_PV)
    axis = Component(MyWaveform, X_WAVE_PV)
    signal = Component(MyWaveform, Y_WAVE_PV)
    
    def __init__(self, *args, **kwargs):
        super().__init__('', parent=None, **kwargs)
        self.complete_status = None
        self.t0 = time.time()
        self.waves = (self.time, self.axis, self.signal)

    def kickoff(self):
        """
        Start this Flyer
        """
        logger.info("kickoff()")
        self.complete_status = DeviceStatus(self.busy)
        
        def cb(*args, **kwargs):
            if self.busy.value in (BusyStatus.done):
                self.complete_status._finished(success=True)
        
        self.t0 = time.time()
        self.busy.put(BusyStatus.busy)
        self.busy.subscribe(cb)

        kickoff_status = DeviceStatus(self)
        kickoff_status._finished(success=True)
        return kickoff_status

    def complete(self):
        """
        Wait for flying to be complete
        """
        logger.info("complete(): " + str(self.complete_status))
        return self.complete_status

    def describe_collect(self):
        """
        Describe details for ``collect()`` method
        """
        logger.info("describe_collect()")
        schema = {}
        for item in self.waves:
            structure = dict(
                source = item.wave.pvname,
                dtype = "number",
                shape = (1,)
            )
            schema[item.name] = structure
        return {self.name: schema}

    def collect(self):
        """
        Start this Flyer
        """
        logger.info("collect(): " + str(self.complete_status))
        self.complete_status = None
        for i in range(int(self.time.number_read.value)):
            data = {}
            timestamps = {}
            t = time.time()
            for item in self.waves:
                data[item.name] = item.wave.value[i]
                timestamps[item.name] = t
            
            # demo: offset time instead (removes large offset)
            data[self.time.name] -= self.t0
            
            yield dict(time=time.time(), data=data, timestamps=timestamps)


bfly = BusyFlyerDevice(name="bfly")


# RE(bp.fly([bfly], md=dict(purpose="develop busy flyer model")))
# https://github.com/NSLS-II/bluesky/blob/master/bluesky/plans.py#L1415
