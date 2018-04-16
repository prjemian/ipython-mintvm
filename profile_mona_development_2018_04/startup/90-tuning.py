print(__file__)

"""
work out the per-axis tuning support
"""

from ophyd.sim import motor1, motor2, motor3
from ophyd.sim import det1, det2 
from bluesky.callbacks.fitting import PeakStats
from ophyd.sim import SynGauss
from ophyd.sim import SynAxis
from ophyd.sim import SynSignal
from ophyd import areadetector
from ophyd.device import BlueskyInterface
from APS_BlueSky_tools.plans import TuneAxis, tune_axes
from APS_BlueSky_tools.devices import AxisTunerMixin


append_wa_motor_list(motor1, motor2, motor3)


# demo some tuning ideas

class TunableSynAxis(SynAxis, AxisTunerMixin):
    pass


class TunableEpicsMotor(EpicsMotor, AxisTunerMixin):
    pass

def myaxis_pretune_hook():
    # set the counting time for *this* tune
    mydet.exposure_time = 0.02      # can't yield this one


myaxis = TunableSynAxis(name="myaxis")
mydet = SynGauss('mydet', myaxis, 'myaxis', center=0.21, Imax=0.98e5, sigma=0.127)
myaxis.tuner = TuneAxis([mydet], myaxis)
myaxis.tuner.width = 2
myaxis.tuner.num = 81

m1 = TunableEpicsMotor('prj:m1', name='m1')
spvoigt = SynPseudoVoigt(
    'spvoigt', m1, 'm1', 
    center=-1.5 + 0.5*np.random.uniform(), 
    eta=0.2 + 0.5*np.random.uniform(), 
    sigma=0.001 + 0.05*np.random.uniform(), 
    scale=0.95e5,
    bkg=0.01*np.random.uniform())
m1.tuner = TuneAxis([spvoigt], m1)
m1.tuner.width = 2
m1.tuner.num = 41

m2 = TunableEpicsMotor('prj:m2', name='m2')
m2.tuner = TuneAxis([scaler], m2, signal_name=scaler.channels.chan2.name)
m2.tuner.width = 2
m2.tuner.num = 10
scaler.channels.read_attrs = "chan1 chan2 chan3 chan4".split()

m3 = TunableEpicsMotor('prj:m3', name='m3')
m3.tuner = TuneAxis([calcs.calc3], m3, signal_name=calcs.calc3.val.name)
m3.tuner.width = 0.5
m3.tuner.num = 31
swait_setup_lorentzian(calcs.calc3, m3, center=-0.15, width=0.025, scale=12345, noise=0.05)
calcs.calc3.read_attrs = ["val",]

append_wa_motor_list(myaxis)
