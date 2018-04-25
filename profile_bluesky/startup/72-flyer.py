print(__file__)

"""
Understand all aspects of the BlueSky Flyer
"""

logger = logging.getLogger(os.path.split(__file__)[-1])


class MyFlyer(Device):
    """
    build a Flyer that we understand
    """

    def __init__(self, *args, **kwargs):
        super().__init__('', parent=None, **kwargs)
        self._completion_status = None

    def my_activity(self):
        """
        start the "fly scan" here, could wait for completion
        
        It's OK to use blocking calls here 
        since this is called in a separate thread
        from the BlueSky RunEngine.
        """
        logger.info("activity()")
        if self._completion_status is None:
            logger.debug("leaving activity() - not complete")
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
        self._completion_status = DeviceStatus(self.busy.state)
        
        thread = threading.Thread(target=self.my_activity, daemon=True)
        thread.start()

        status = DeviceStatus(self.busy.state)
        status._finished(success=True)
        return status

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
        return {'ifly': {}
        }

    def collect(self):
        """
        Start this Flyer
        """
        logger.info("collect()")
