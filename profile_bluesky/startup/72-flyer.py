print(__file__)

"""
Understand all aspects of the BlueSky Flyer
"""

logger = logging.getLogger(os.path.split(__file__)[-1])


class MyFlyer(Device):
    """
    build a Flyer that we understand
    """

    busy = Component(BusyRecord, 'prj:mybusy')
    tArr = Component(MyWaveform, 'prj:t_array')
    xArr = Component(MyWaveform, 'prj:x_array')
    yArr = Component(MyWaveform, 'prj:y_array')

    def __init__(self, *args, **kwargs):
        super().__init__('', parent=None, **kwargs)
        self._completion_status = None
        self.poll_sleep_interval_s = 0.05
        self.t0 = 0

    def wait_busy(self, target = None):
        """
        wait for the busy record to return to the target value
        """
        logger.debug("wait_busy()")
        target = target or BusyStatus.done

        while self.busy.state.value not in (BusyStatus.done, 0):
            time.sleep(self.poll_sleep_interval_s)  # wait to complete ...
 
    def my_activity(self):
        """
        start the "fly scan" here, could wait for completion
        
        It's OK to use blocking calls here 
        since this is called in a separate thread
        from the BlueSky RunEngine.
        """
        logger.info("activity()")
        if self._completion_status is None:
            logger.info("leaving activity() - not complete")
            return
        
        # do the activity here
        self.busy.state.put(BusyStatus.done) # make sure it's Done first
        self.wait_busy()

        # wait for completion
        self.t0 = time.time()
        self.busy.state.put(BusyStatus.busy)
        self.wait_busy()
        
        self._completion_status._finished(success=True)
        logger.info("activity() complete. status = " + str(self._completion_status))

    def kickoff(self):
        """
        Start this Flyer
        """
        logger.info("kickoff()")
        self._completion_status = DeviceStatus(self)
        
        thread = threading.Thread(target=self.my_activity, daemon=True)
        thread.start()

        return self._completion_status

    def complete(self):
        """
        Wait for flying to be complete
        """
        logger.info("complete()")
        if self._completion_status is None:
            raise RuntimeError("No collection in progress")

        st = DeviceStatus(self)
        st._finished(success=True)
        return st

    def describe_collect(self):
        """
        Describe details for ``collect()`` method
        """
        logger.info("describe_collect()")
        return {
            self.name: dict(
                ifly_xArr = dict(
                    source = self.xArr.wave.pvname,
                    dtype = "number",
                    shape = (1,)
                ),
                ifly_yArr = dict(
                    source = self.yArr.wave.pvname,
                    dtype = "number",
                    shape = (1,)
                ),
                ifly_tArr = dict(
                    source = self.tArr.wave.pvname,
                    dtype = "number",
                    shape = (1,)
                )
            )
        }

    def collect(self):
        """
        Start this Flyer
        """
        logger.info("collect()")
        for i in range(len(ifly.tArr.wave.value)):
            t = ifly.tArr.wave.value[i]
            x = ifly.xArr.wave.value[i]
            y = ifly.yArr.wave.value[i]
            d = dict(
                time=time.time(),
                data=dict(
                    ifly_tArr = time.time() - self.t0,
                    ifly_xArr = x,
                    ifly_yArr = y,
                ),
                timestamps=dict(
                    ifly_tArr = t,
                    ifly_xArr = t,
                    ifly_yArr = t,
                )
            )
            yield d


ifly = MyFlyer(name="ifly")
"""
RE(bp.fly([ifly]), md=dict(purpose="develop Flyer for APS fly scans"))
list(db[-1].documents())
db[-1].table("ifly")
"""
