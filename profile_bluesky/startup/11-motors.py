print(__file__)

"""motors, stages, positioners, ..."""

# m1 = MyEpicsMotorWithDial('prj:m1', name='m1')
m1 = EpicsMotor('prj:m1', name='m1')
m2 = EpicsMotor('prj:m2', name='m2')
m3 = EpicsMotor('prj:m3', name='m3')
m4 = EpicsMotor('prj:m4', name='m4')
m5 = EpicsMotor('prj:m5', name='m5')
m6 = EpicsMotor('prj:m6', name='m6')
m7 = EpicsMotor('prj:m7', name='m7')
m8 = EpicsMotor('prj:m8', name='m8')

append_wa_motor_list(m1, m2, m3, m4, m5, m6, m7, m8)
