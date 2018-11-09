
from ophyd.sim import SynSignal, SynSignalRO
from ophyd import Component, Device, DeviceStatus, FormattedComponent


class SimulatedApsPssShutterWithStatus(Device):
    """
    Simulated APS PSS shutter
    """
    open_bit = Component(SynSignal)
    close_bit = Component(SynSignal)
    pss_state = FormattedComponent(SynSignal)

    # strings the user will use
    open_str = 'open'
    close_str = 'close'

    # pss_state PV values from EPICS
    open_val = 1
    close_val = 0

    # simulated response time for PSS status
    response_time = 0.5

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.open_bit.set(0)
        self.close_bit.set(0)
        self.pss_state.set(self.close_val)

    def open(self, timeout=10):
        """request the shutter to open"""
        self.set(self.open_str)

    def close(self, timeout=10):
        """request the shutter to close"""
        self.set(self.close_str)

    def set(self, value, **kwargs):
        """set the shutter to "close" or "open" """
        # first, validate the input value
        acceptables = (self.close_str, self.open_str)
        if value not in acceptables:
            msg = "value should be one of " + " | ".join(acceptables)
            msg += " : received " + str(value)
            raise ValueError(msg)

        command_signal = {
            self.open_str: self.open_bit, 
            self.close_str: self.close_bit
        }[value]
        expected_value = {
            self.open_str: self.open_val, 
            self.close_str: self.close_val
        }[value]

        working_status = DeviceStatus(self)
        simulate_delay = self.pss_state.value != expected_value
        
        def shutter_cb(value, timestamp, **kwargs):
            self.pss_state.clear_sub(shutter_cb)
            if simulate_delay:
                time.sleep(self.response_time)
            self.pss_state.set(expected_value)
            working_status._finished()
        
        self.pss_state.subscribe(shutter_cb)
        
        command_signal.put(1)
        
        # finally, make sure both signals are reset
        self.open_bit.put(0)
        self.close_bit.put(0)
        return working_status

    @property
    def isOpen(self):
        """is the shutter open?"""
        if self.pss_state.value is None:
            self.pss_state.set(self.close_val)
        return self.pss_state.value == self.open_val
    
    @property
    def isClosed(self):
        """is the shutter closed?"""
        if self.pss_state.value is None:
            self.pss_state.set(self.close_val)
        return self.pss_state.value == self.close_val


sim = SimulatedApsPssShutterWithStatus(name="sim")
