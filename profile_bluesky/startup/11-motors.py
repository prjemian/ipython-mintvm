print(__file__)

"""motors, stages, positioners, ..."""

m1 = EpicsMotor('prj:m1', name='m1', labels=("general",))
m2 = EpicsMotor('prj:m2', name='m2', labels=("general",))
m3 = EpicsMotor('prj:m3', name='m3', labels=("general",))
m4 = EpicsMotor('prj:m4', name='m4', labels=("general",))

class MyRig(Device):
    t = Component(EpicsMotor, "m5", labels=("rig",),)
    l = Component(EpicsMotor, "m6", labels=("rig",))
    b = Component(EpicsMotor, "m7", labels=("rig",))
    r = Component(EpicsMotor, "m8", labels=("rig",))

    # Define basic read attributes
    _default_read_attrs = [
        't.user_readback', 't.user_readback',
        'l.user_readback', 'l.user_setpoint',
        'b.user_setpoint', 'b.user_setpoint',
        'r.user_setpoint', 'r.user_setpoint',
        ]

    @property
    def hints(self):
        return ['t.readback', 'l.readback', 'b.readback', 'r.readback']


rig = MyRig("prj:", name="rig")

# m5 = EpicsMotor('prj:m5', name='m5')
# m6 = EpicsMotor('prj:m6', name='m6')
# m7 = EpicsMotor('prj:m7', name='m7')
# m8 = EpicsMotorWithDial('prj:m8', name='m8')

# append_wa_motor_list(m1, m2, m3, m4, m5, m6, m7, m8)

shutter = APS_devices.EpicsMotorShutter("prj:m9", name="shutter", labels=("shutter",))
shutter.closed_position = 0.0
shutter.open_position = 3.0        # takes a little time to get here
