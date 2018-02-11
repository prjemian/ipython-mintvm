print(__file__)

"""
Demo of Flyer to simulate MONA tomo fly scan

:see: http://nsls-ii.github.io/ophyd/architecture.html#fly-able-interface
"""


class BusyRecord(Device):
    state = Component(EpicsSignal, "")
    output_link = Component(EpicsSignal, ".OUT")
    forward_link = Component(EpicsSignal, ".FLNK")
    

mybusy = BusyRecord("prj:mybusy", name="mybusy")


class SpinFlyer(object):
    """
    one spin of the tomo stage, run as ophyd Flyer object
    
    Kickoff
    
    * motor starts at initial position
    * moved to pre-start (taxi) position
    * detector prepared for acquisition on motor increments
    * motion started towards end position (fly) in separate thread
    
    Complete
    
    * motor monitored for not moving status
    
    Collect
    
    * success = motor has reached end position
    * detector data saved
    """
    name = "spin_flyer"
    parent = None
    
    def __init__(self, motor, detector, busy, pre_start=-0.5, pos_start=-20, pos_finish=20, increment=2.5):
        self.status = None
        self.motor = motor
        self.detector = detector
        self.busy = busy
        self.pre_start = pre_start
        self.pos_premove = motor.position
        self.pos_start = pos_start
        self.pos_finish = pos_finish
        self.increment = increment
    
    def taxi(self):
        # pre_start position is far enough before pos_start to ramp up to speed
        position = self.pos_start + self.pre_start
        self.motor.move(position)
    
    def fly(self):
        self.motor.move(self.pos_finish)

    def set(self, value):       # interface for BlueSky plans
        """value is either Taxi or Fly"""
        if str(value).lower() not in ("fly", "taxi", "return"):
            msg = "value should be either Taxi, Fly, or Return."
            msg + " received " + str(value)
            raise ValueError(msg)

        if self.busy.value:
            raise RuntimeError("spin is operating")

        status = DeviceStatus(self)
        
        def action():
            """the real action of ``set()`` is here"""
            if str(value).lower() == "taxi":
                self.taxi()
            elif str(value).lower() == "fly":
                det_pre_acquire(self.detector)
                self.fly()
                det_post_acquire(self.detector)
            elif str(value).lower() == "return":
                self.motor.move(self.pos_premove)

        def run_and_wait():
            """handle the ``action()`` in a thread"""
            self.busy.put(True)
            action()
            self.busy.put(False)
            status._finished(success=True)
        
        threading.Thread(target=run_and_wait, daemon=True).start()
        return status

    def kickoff(self):
        """
        Start a flyer
        """
        self.status = DeviceStatus(device=self)
        return self.status

    def describe_collect(self):
        """
        Provide schema & meta-data from ``collect()``
        """
        return {'stream_name': {}}

    def read_configuration(self):
        """
        """
        return OrderedDict()

    def describe_configuration(self):
        """
        """
        return OrderedDict()

    def complete(self):
        """
        Wait for flying to be complete
        """
        return self.status
    
    def collect(self):
        """
        Retrieve data from the flyer as *proto-events*
        """
        # TODO: refactor
        for i in range(100):
            yield {'data': {}, 'timestamps': {}, 'time': i, 'seq_num': i}
    
    def stop(self, *, success=False):
        """
        """
        pass


spin_flyer = SpinFlyer(m3, simdet, mybusy.state)

def example_planB():
    spin_flyer.pos_premove = spin_flyer.motor.position
    yield from mv(spin_flyer, "Taxi")
    yield from mv(spin_flyer, "Fly")
    yield from mv(spin_flyer, "Return")


def det_pre_acquire(det, max_frames=10000):
    # enable the HDF5 plugin
    det.hdf1.enable.put("Enable")
    
    # prepare to capture a stream of image frames in one array
    det.hdf1.file_write_mode.put("Capture")
    
    # collect as many as this number
    det.hdf1.num_capture.put(max_frames)
    
    # start to capture the stream
    det.hdf1.capture.put("Capture")


def det_post_acquire(det):
    # stream is now fully captured
    det.hdf1.capture.put("Done")
    
    # write the HDF5 file
    det.hdf1.write_file.put(1)
    
    # reset the HDF5 plugin to some default settings
    det.hdf1.file_write_mode.put("Single")
    det.hdf1.num_capture.put(1)
    det.hdf1.enable.put("Disable")


setup_det_trigger(m3, simdet, calcs.calc3, calcs.calc4)
