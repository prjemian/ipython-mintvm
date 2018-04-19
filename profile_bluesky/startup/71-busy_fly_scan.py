print(__file__)

"""
APS Fly Scan example using the busy record

Alternative approach to the BlueSky Flyer,
this example does not inject the data into BlueSky.
Coded here to meet an imposing deadline.
"""

logger = logging.getLogger(os.path.split(__file__)[-1])
POLL_SLEEP_S = 0.05


class ApsBusyFlyScanDevice(Device):
    """
    use the busyExample.py code to make a pseudo-scan
    
    http://nsls-ii.github.io/ophyd/architecture.html#fly-able-interface
    """
    # TODO: some of the methods below might comprise a generic Mixin
    busy = Component(BusyRecord, 'prj:mybusy')
    motor = Component(EpicsMotor, 'prj:m1')
    signal = Component(MyCalc, 'prj:userCalc1')
    xArr = Component(MyWaveform, 'prj:x_array')
    yArr = Component(MyWaveform, 'prj:y_array')
    
    def __init__(self, stream_name=None, **kwargs):
        super().__init__('', parent=None, **kwargs)
        self._completion_status = None
        self._external_running = False
        self.stream_name = stream_name

    def launch_external_program(self):
        """
        launch external program in a thread
        
        https://docs.python.org/3/library/subprocess.html#subprocess.run
        """
        if self._external_running:
            logger.debug("external program already running")
            return
        try:
            path = os.path.dirname(__file__)
        except NameError as _exc:
            # interactive use
            path = os.path.abspath(".")
        path = os.path.join(path, "local_code", "busyExample.py")
        
        def _runner():
            self._external_running = True
            logger.debug("starting external program")
            # subprocess.run() is a blocking call
            subprocess.run([path, "/dev/null"], stdout=subprocess.PIPE)
            self._external_running = False
            logger.debug("external program ended")
        
        thread = threading.Thread(target=_runner, daemon=True)
        thread.start()
   
    def terminate_external_program_in_RE(self):
        """
        tell external program to quit while in RunEngine
        """
        logger.info("terminating external program(s) in RunEngine")
        yield from mv(self.signal.calc, "0")
        yield from mv(self.signal.proc, 1)
        bps.sleep(1.0)
        logger.debug("external program terminated")
   
    def terminate_external_program(self):
        """
        tell external program to quit
        """
        logger.info("terminating external program(s)")
        self.signal.calc.put("0")
        self.signal.proc.put(1)
        time.sleep(1.0)
        logger.debug("external program terminated")

    def activity(self):
        """
        start the busy record and poll for completion
        
        It's OK to use blocking calls here 
        since this is called in a separate thread
        from the BlueSky RunEngine.
        """
        logger.info("activity()")
        if self._completion_status is None:
            logger.debug("leaving activity() - not complete")
            return

        def wait_until_not_busy():
            msg = "activity()  busy = " + str(self.busy.state.value)
            logger.debug(msg)
            while self.busy.state.value not in (BusyStatus.done, 0):
                # ... waiting for it to complete ...
                time.sleep(POLL_SLEEP_S)

        logger.debug("activity() - clearing Busy")
        self.busy.state.put(BusyStatus.done) # make sure it's Done first
        wait_until_not_busy()
        time.sleep(1.0)

        logger.debug("activity() - setting Busy")
        self.busy.state.put(BusyStatus.busy)
        wait_until_not_busy()

        self.terminate_external_program()
        self._completion_status._finished(success=True)
        logger.debug("activity() complete")
        logger.debug("activity() status=" + str(self._completion_status))
    
    def plan(self):
        logger.info("plan()")
        yield from bpp.open_run()

        self.terminate_external_program_in_RE()   # belt+suspenders approach
        self.launch_external_program()
        self._completion_status = DeviceStatus(self.busy.state)
        
        thread = threading.Thread(target=self.activity, daemon=True)
        thread.start()
        
        while not self._completion_status.done:
            bps.sleep(POLL_SLEEP_S)
        logger.debug("plan() status=" + str(self._completion_status))

        yield from bpp.close_run()
        logger.info("plan() complete")
        logger.debug("plan() status=" + str(self._completion_status))


ifly = ApsBusyFlyScanDevice(name="ifly")
# RE(ifly.plan(), md=dict(purpose="develop busy flyer model")))
