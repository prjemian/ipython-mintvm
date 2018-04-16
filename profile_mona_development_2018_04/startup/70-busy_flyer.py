print(__file__)

"""flyer example with the busy record"""

from collections import deque, OrderedDict
import os
import subprocess


class BusyRecord(Device):
    state = Component(EpicsSignal, "")
    output_link = Component(EpicsSignal, ".OUT")
    forward_link = Component(EpicsSignal, ".FLNK")


class MyCalc(Device):
    result = Component(EpicsSignal, "")
    calc = Component(EpicsSignal, ".CALC")
    proc = Component(EpicsSignal, ".PROC")


class MyWaveform(Device):
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
    
    def __init__(self, **kwargs):
        super().__init__('', parent=None, **kwargs)
        self.status = None
        self._completion_status = None
        self._data = deque()
   
    def launch_external_program(self):
        """
        launch external program in a thread
        
        https://docs.python.org/3/library/subprocess.html#subprocess.run
        """
        path = os.path.dirname(__file__)
        path = os.path.join(path, "local_code", "busyExample.py")
        
        def _runner():
            subprocess.run([path, "/dev/null"], stdout=subprocess.PIPE)
        
        thread = threading.Thread(target=_runner, daemon=True)
        thread.start()
   
    def terminate_external_program(self):
        """
        tell external program to quit
        """
        yield from mv(self.signal.calc, "0")
        yield from mv(self.signal.proc, 1)

    def activity(self):
        if self._completion_status is None:
            return

        yield from mv(busy.state, 1)
        # ... waiting for it to complete ...
        self.terminate_external_program()
        self._completion_status._finished(success=True)

    def set(self, value):
        """
        Prepare this Flyer
        """
        self.terminate_external_program()
        self.launch_external_program()
    
    def kickoff(self):
        """
        Start this flyer
        """
        if self._completion_status is not None:
            raise RuntimeError("Already kicked off.")
        self._data = deque()

        self._completion_status = DeviceStatus(device=self)

        thread = threading.Thread(target=self.activity, daemon=True)
        thread.start()

        return self._completion_status
    
    def describe_collect(self):
        """
        Provide schema & meta-data from ``collect()``
        """
        pass
    
    def complete(self):
        """
        Wait for flying to be complete
        """
        if self._completion_status is None:
            raise RuntimeError("No collection in progress")
        
        # TODO: something?

        return self._completion_status
    
    def collect(self):
        """
        Retrieve data from the flyer as *proto-events*

        Yields:	

        event_data : dict

            Must have the keys {‘time’, ‘timestamps’, ‘data’}.

        """
        # TODO: want to monitor the two arrays
        pass

    def stop(self, *, success=False):
        """
        halt activity (motion) before it is complete
        """
        pass

ifly = BusyFlyer(name="ifly")
