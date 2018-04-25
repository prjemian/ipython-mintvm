print(__file__)

"""
Understand all aspects of the BlueSky Flyer
"""

logger = logging.getLogger(os.path.split(__file__)[-1])


class MyFlyer(Device):
    """
    build a Flyer that we understand
    """

    xArr = Component(MyWaveform, 'prj:x_array')
    # yArr = Component(MyWaveform, 'prj:y_array')

    def __init__(self, *args, **kwargs):
        super().__init__('', parent=None, **kwargs)
        self._completion_status = None
        self.t0 = 0

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
        
        # TODO: do the activity here
        # TODO: wait for completion
        
        self._completion_status._finished(success=True)
        logger.info("activity() complete. status = " + str(self._completion_status))

    def kickoff(self):
        """
        Start this Flyer
        """
        logger.info("kickoff()")
        self._completion_status = DeviceStatus(self)
        self.t0 = time.time()
        
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
        d = dict(
            source = "elapsed time, s",
            dtype = "number",
            shape = []
        )
        return {
            'ifly': {
                "x": d
            }
        }

    def collect(self):
        """
        Start this Flyer
        """
        logger.info("collect()")
        t = time.time()
        x = t - self.t0 # data is elapsed time since kickoff()
        d = dict(
            time=t,
            data=dict(x=x),
            timestamps=dict(x=t)
        )
        yield d


ifly = MyFlyer(name="ifly")
RE(bp.fly([ifly]), md=dict(purpose="develop Flyer for APS fly scans"))
