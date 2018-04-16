print(__file__)

"""Flyer example with the busy record"""

from collections import deque, OrderedDict
import os
import subprocess


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
    
    def __init__(self, **kwargs):
        super().__init__('', parent=None, **kwargs)
        self._completion_status = None
        self._data = deque()
        self._external_running = False
   
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
   
    def terminate_external_program(self):
        """
        tell external program to quit
        """
        logging.debug("terminating external program(s)")
        yield from mv(self.signal.calc, "0")
        yield from mv(self.signal.proc, 1)
        logging.debug("external program terminated")

    def activity(self):
        """
        start the busy record and poll for completion
        
        It's OK to use blocking calls here 
        since this is called in a separate thread
        from the BlueSky RunEngine.
        """
        logging.debug("activity()")
        print("activity()")
        if self._completion_status is None:
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

    def fly(self):
        """
        use this method to run the fly scan
        
        As in::
        
            ifly = BusyFlyer()
            RE(ifly.fly())
        
        """
        yield from mv(self, "fly")
        
    def set(self, value):
        """
        Prepare this Flyer
        """
        logging.info('set("{}")'.format(value))
        if value in ("fly",):
            self.terminate_external_program()   # belt+suspenders approach
            self.launch_external_program()
    
            self._data = deque()

            self._completion_status = DeviceStatus(device=self)

            logging.debug('set() starting thread')
            thread = threading.Thread(target=self.activity, daemon=True)
            thread.start()
            logging.debug(str(self._completion_status))

            return self._completion_status

    def kickoff(self):
        """
        Start this Flyer
        """
        logging.debug("kickoff()")
        if self._completion_status is not None:
            raise RuntimeError("Already kicked off.")
        yield from mv(self.busy.state, "Busy")
    
    def describe_collect(self):
        """
        Provide schema & meta-data from ``collect()``
        """
        logging.info("describe_collect()")
        pass
    
    def complete(self):
        """
        Wait for flying to be complete
        """
        if self._completion_status is None:
            raise RuntimeError("No collection in progress")
        
        # TODO: something?
        logging.info("complete()")

        return self._completion_status
    
    def collect(self):
        """
        Retrieve data from the Flyer as *proto-events*

        Yields:	

        event_data : dict

            Must have the keys {‘time’, ‘timestamps’, ‘data’}.

        """
        # TODO: want to monitor the two arrays
        logging.info("collect()")
        pass

    def stop(self, *, success=False):
        """
        halt activity (motion) before it is complete
        """
        logging.info("stop()")
        yield from mv(busy.state, 0)
        yield from mv(motor.stop, 0)


def fly_it(flyer):
    yield from flyer.fly()


ifly = BusyFlyer(name="ifly")