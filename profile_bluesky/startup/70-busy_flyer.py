print(__file__)

"""Flyer example with the busy record"""

from collections import deque, OrderedDict
import os
import subprocess
from ophyd.utils import OrderedDefaultDict


class BusyRecord(Device):
    """a busy record sets the fly scan into action"""
    state = Component(EpicsSignal, "")
    output_link = Component(EpicsSignal, ".OUT")
    forward_link = Component(EpicsSignal, ".FLNK")


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


class BusyFlyer(Device):
    """
    use the busyExample.py code to make a pseudo-scan
    
    http://nsls-ii.github.io/ophyd/architecture.html#fly-able-interface
    """
    busy = Component(BusyRecord, 'prj:mybusy')
    motor = Component(EpicsMotor, 'prj:m1')
    signal = Component(MyCalc, 'prj:userCalc1')
    xArr = Component(MyWaveform, 'prj:x_array')
    yArr = Component(MyWaveform, 'prj:y_array')
    
    def __init__(self, stream_name=None, **kwargs):
        super().__init__('', parent=None, **kwargs)
        self._completion_status = None
        self._data = deque()
        self._external_running = False
        self.stream_name = stream_name

    def launch_external_program(self):
        """
        launch external program in a thread
        
        https://docs.python.org/3/library/subprocess.html#subprocess.run
        """
        if self._external_running:
            logging.info("external program already running")
            return
        try:
            path = os.path.dirname(__file__)
        except NameError as _exc:
            # interactive use
            path = os.path.abspath(".")
        path = os.path.join(path, "local_code", "busyExample.py")
        
        def _runner():
            self._external_running = True
            logging.info("starting external program")
            # subprocess.run() is a blocking call
            subprocess.run([path, "/dev/null"], stdout=subprocess.PIPE)
            self._external_running = False
            logging.info("external program ended")
        
        thread = threading.Thread(target=_runner, daemon=True)
        thread.start()
   
    def terminate_external_program_in_RE(self):
        """
        tell external program to quit while in RunEngine
        """
        logging.debug("terminating external program(s) in RunEngine")
        yield from mv(self.signal.calc, "0")
        yield from mv(self.signal.proc, 1)
        sleep(1.0)
        logging.debug("external program terminated")
   
    def terminate_external_program(self):
        """
        tell external program to quit
        """
        logging.debug("terminating external program(s)")
        self.signal.calc.put("0")
        self.signal.proc.put(1)
        time.sleep(1.0)
        logging.debug("external program terminated")

    def activity(self):
        """
        start the busy record and poll for completion
        
        It's OK to use blocking calls here 
        since this is called in a separate thread
        from the BlueSky RunEngine.
        """
        logging.info("activity()")
        if self._completion_status is None:
            logging.debug("leaving activity() - not complete")
            return

        def wait_until_done():
            msg = "activity()  busy = " + str(self.busy.state.value)
            logging.debug(msg)
            while self.busy.state.value not in ("Done", 0):
                # ... waiting for it to complete ...
                time.sleep(0.05)

        logging.debug("activity() - clearing Busy")
        self.busy.state.put("Done") # make sure it's Done first
        wait_until_done()
        time.sleep(1.0)

        logging.debug("activity() - setting Busy")
        self.busy.state.put("Busy")
        wait_until_done()

        self.terminate_external_program()
        self._completion_status._finished(success=True)
        logging.debug("activity() complete")

    def kickoff(self):
        """
        Start this Flyer
        """
        logging.info("kickoff()")
        # https://github.com/NSLS-II/ophyd/blob/master/ophyd/flyers.py#L126

        self._collected_data = OrderedDefaultDict(lambda: {'values': [],
                                                           'timestamps': []})

        self.terminate_external_program_in_RE()   # belt+suspenders approach
        self.launch_external_program()
        self._completion_status = DeviceStatus(self.busy.state)
        
        thread = threading.Thread(target=self.activity, daemon=True)
        thread.start()

        status = DeviceStatus(self.busy.state)
        status._finished(success=True)
        return status
    
    def complete(self):
        """
        Wait for flying to be complete
        """
        logging.info("complete()")
        if self._completion_status is None:
            raise RuntimeError("No collection in progress")

        st = DeviceStatus(self)
        st._finished(success=True)
        return st
    
    def pause(self):
        '''Pause acquisition'''
        logging.info("pause()")
        super().pause()

    def resume(self):
        '''Resume acquisition'''
        logging.info("resume()")
        super().resume()

    def describe_collect(self):
        """
        Describe details for ``collect()`` method
        """
        logging.info("describe_collect()")
        collectors = "xArr yArr".split()
        desc = self._describe_attr_list(collectors)
        return {self.stream_name: desc}
    
    def collect(self):
        """
        Retrieve data from the Flyer as *proto-events*

        Yields::
        
            event_data : dict
                Must have the keys {'time', 'timestamps', 'data'}.

        """
        logging.info("collect()")
        logging.info("collect() stream_name={}".format(self.stream_name))
        for i in range(len(self.xArr.wave.value)):
            logging.info("collect() #{}".format(i+1))
            data_dict = {}
            ts_dict = {}
            t = time.time()     # fake these for now
            logging.info("collect() time={}".format(t))
            for arr in (self.xArr, self.yArr):
                data_dict[arr.wave.name] = arr.wave.value[i]
                ts_dict[arr.wave.name] = t
            logging.info("collect() data={}".format(data_dict))
            yield dict(data=data_dict, timestamps=ts_dict, time=t)
            logging.info("collect() after yield")

    def stop(self, *, success=False):
        """
        halt activity (motion) before it is complete
        """
        logging.info("stop()")
        yield from mv(busy.state, 0)
        yield from mv(motor.stop, 0)


ifly = BusyFlyer(name="ifly")


# RE(bp.fly([ifly], md=dict(purpose="develop busy flyer model")))
# https://github.com/NSLS-II/bluesky/blob/master/bluesky/plans.py#L1415
