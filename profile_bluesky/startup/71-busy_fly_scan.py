print(__file__)

"""
APS Fly Scan example using the busy record

Alternative approach to the BlueSky Flyer,
this example does not inject the data into BlueSky.
Coded here to meet an imposing deadline.
"""

logger = logging.getLogger(os.path.split(__file__)[-1])


class ApsBusyFlyScanDeviceMixin(object):
    """
    support APS Fly Scans that are operated by a busy record
    
    requires that calling class create an instance of ``BusyRecord``
    named ``busy``, as in::

        busy = Component(BusyRecord, 'prj:mybusy')

    This mixin will not generate BlueSky events to inject data into
    the databroker.  Any data collection must be handled during
    the various hook functions.
    
    .. autosummary:
       ~flyscan_plan
       ~hook_flyscan
       ~hook_pre_flyscan
       ~hook_post_flyscan
       ~hook_flyscan_wait_not_scanning
       ~hook_flyscan_wait_scanning
       ~flyscan_wait
       ~_flyscan
    
    """

    def __init__(self, **kwargs):
        self._flyscan_status = None
        self.poll_sleep_interval_s = 0.05
        
        try:
            if not isinstance(self.busy, BusyRecord):
                msg = "``busy`` must be a ``BusyRecord`` instance"
                raise KeyError(msg)
        except AttributeError:
            msg = "must define ``busy`` record instance"
            raise KeyError(msg)
    
    def hook_flyscan(self):
        """
        Customize: called during fly scan
        
        called from RunEngine thread in ``flyscan_plan()``, 
        blocking calls are not permitted
        """
        logger.debug("hook_flyscan_not_scanning() : no-op default")
    
    def hook_pre_flyscan(self):
        """
        Customize: called before the fly scan
        
        NOTE: As part of a BlueSky plan thread, no blocking calls are permitted
        """
        logger.debug("hook_pre_flyscan() : no-op default")
    
    def hook_post_flyscan(self):
        """
        Customize: called after the fly scan
        
        NOTE: As part of a BlueSky plan thread, no blocking calls are permitted
        """
        logger.debug("hook_post_flyscan() : no-op default")
    
    def hook_flyscan_wait_not_scanning(self):
        """
        Customize: called ``flyscan_wait(False)``
        
        called in separate thread, blocking calls are permitted
        but keep it quick
        """
        logger.debug("hook_flyscan_not_scanning() : no-op default")

    def hook_flyscan_wait_scanning(self):
        """
        Customize: called from ``flyscan_wait(True)``
        
        called in separate thread, blocking calls are permitted
        but keep it quick
        """
        logger.debug("hook_flyscan_wait_scanning() : no-op default")

    def flyscan_wait(self, scanning):
        """
        wait for the busy record to return to Done
        
        Call external hook functions to allow customizations
        """
        msg = "flyscan_wait()"
        msg += " scanning=" + str(scanning)
        msg += " busy=" + str(self.busy.state.value)
        logger.debug(msg)

        if scanning:
            hook = self.hook_flyscan_wait_scanning
        else:
            hook = self.hook_flyscan_wait_not_scanning

        while self.busy.state.value not in (BusyStatus.done, 0):
            hook()
            time.sleep(self.poll_sleep_interval_s)  # wait to complete ...

    def _flyscan(self):
        """
        start the busy record and poll for completion
        
        It's OK to use blocking calls here 
        since this is called in a separate thread
        from the BlueSky RunEngine.
        """
        logger.debug("_flyscan()")
        if self._flyscan_status is None:
            logger.debug("leaving fly_scan() - not complete")
            return

        logger.debug("flyscan() - clearing Busy")
        self.busy.state.put(BusyStatus.done) # make sure it's Done first
        self.flyscan_wait(False)
        time.sleep(1.0)

        logger.debug("flyscan() - setting Busy")
        self.busy.state.put(BusyStatus.busy)
        self.flyscan_wait(True)

        self._flyscan_status._finished(success=True)
        logger.debug("flyscan() complete")
    
    def flyscan_plan(self, *args, **kwargs):
        """
        This is the BlueSky plan to submit to the RunEgine
        """
        logger.debug("flyscan_plan()")
        yield from bpp.open_run()

        self.hook_pre_flyscan()
        self._flyscan_status = DeviceStatus(self.busy.state)
        
        thread = threading.Thread(target=self._flyscan, daemon=True)
        thread.start()
        
        while not self._flyscan_status.done:
            self.hook_flyscan()
            bps.sleep(self.poll_sleep_interval_s)
        logger.debug("plan() status=" + str(self._flyscan_status))
        self.hook_post_flyscan()

        yield from bpp.close_run()
        logger.debug("plan() complete")


class PythonPseudoController(object):
    """
    use the busyExample.py code to make a pseudo fly scan
    """
    
    def __init__(self, swait, **kwargs):
        self._external_running = False
        self.swait = swait
    
    def _get_file_name(self):
        try:
            path = os.path.dirname(__file__)
        except NameError as _exc:
            # interactive use
            path = os.path.abspath(".")
        return os.path.join(path, "local_code", "busyExample.py")
    
    def _start(self, python_file_name):
        """
        run the external program as a subprocess 
        
        note: the caller launches this in a separate thread
        """
        self._external_running = True
        logger.debug("starting external program")
        # subprocess.run() is a blocking call
        subprocess.run([python_file_name, "/dev/null"], stdout=subprocess.PIPE)
        self._external_running = False
        logger.debug("external program ended")
    
    def _stop(self):
        """
        configure swait record to signal external program to quit
        """
        self.swait.calc.put("0")
        self.swait.proc.put(1)
        time.sleep(1.0)

    def launch(self):
        """
        start external program (in a thread)
        """
        logger.debug("PythonPseudoController.launch()")
        if self._external_running:
            logger.debug("PythonPseudoController.launch() already running")
            return
        fname = self._get_file_name()
        
        thread = threading.Thread(target=self._start, args=[fname], daemon=True)
        thread.start()
    
    def terminate(self):
        """
        signal external program to quit
        """
        logger.debug("PythonPseudoController.terminate()")
        if not self._external_running:
            logger.debug("PythonPseudoController.launch() not known to be running")
            return

        thread = threading.Thread(target=self._stop, daemon=True)
        thread.start()
        logger.debug("external program signalled to end")


class ApsBusyFlyScanDevice(Device, ApsBusyFlyScanDeviceMixin):
    """
    BlueSky interface for the busyExample.py fly scan
    """
    busy = Component(BusyRecord, 'prj:mybusy')
    # motor = Component(EpicsMotor, 'prj:m1')
    signal = Component(MyCalc, 'prj:userCalc1')
    xArr = Component(MyWaveform, 'prj:x_array')
    yArr = Component(MyWaveform, 'prj:y_array')
    
    def __init__(self, **kwargs):
        super().__init__('', parent=None, **kwargs)
        self._external_running = False
        self.controller = PythonPseudoController(self.signal)
        self.update_interval = 10
        self.update_time = time.time() + self.update_interval

    def launch_external_program(self):
        """
        launch external program in a thread
        
        https://docs.python.org/3/library/subprocess.html#subprocess.run
        """
        if self._external_running:
            logger.debug("external program already running")
            return
        self.controller.launch()
   
    def terminate_external_program(self):
        """
        tell external program to quit
        
        blocking calls OK, good for command-line use
        """
        logger.debug("terminating external program(s)")
        self.controller.terminate()

    def hook_pre_flyscan(self, *args, **kwargs):
        """
        run before the fly scan
        """
        logger.debug("hook_pre_flyscan() : no-op default")
        
        # belt+suspenders approach
        # exactly *one* instance of external should be running
        self.controller.terminate()
        self.controller.launch()
        self.t0 = time.time()
        self.update_time = time.time() + self.update_interval
    
    def final_report(self):
        print("scan data")
        print("#\tx\ty")
        for i in range(int(self.xArr.number_read.value)):
            print("{}\t{}\t{}".format(
                i+1,
                self.xArr.wave.value[i],
                self.yArr.wave.value[i]
                )
            )

    def hook_post_flyscan(self, *args, **kwargs):
        """
        run after the fly scan
        """
        logger.debug("hook_post_flyscan() : no-op default")
        self.controller.terminate()
        logger.debug("done in {} s".format(time.time() - self.t0))
        self.final_report()
        del self.t0

    def hook_flyscan_wait_not_scanning(self):
        """
        Customize: called from ``flyscan_wait(False)``
        """
        logger.debug("hook_flyscan_wait_not_scanning() : no-op default")
        t = time.time()
        if t > self.update_time:
            self.update_time = time.time() + self.update_interval

    def hook_flyscan_wait_scanning(self):
        """
        Customize: called from ``flyscan_wait(True)``
        """
        logger.debug("hook_flyscan_wait_scanning() : no-op default")
        if time.time() > self.update_time:
            self.update_time = time.time() + self.update_interval
            logger.debug("waiting {} s".format(time.time() - self.t0))

ifly = ApsBusyFlyScanDevice(name="ifly")
ifly.update_interval = 5
# RE(ifly.flyscan_plan(), md=dict(purpose="develop busy flyer model"))
