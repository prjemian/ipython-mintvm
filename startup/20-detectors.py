print(__file__)

from ophyd import (EpicsScaler, EpicsSignal, EpicsSignalRO,
                   Device, DeviceStatus)
from ophyd import Component as Cpt
import time
from APS_BlueSky_tools.examples import SynPseudoVoigt


#aps_current = EpicsSignalRO("S:SRcurrentAI", name="aps_current")

## Beam Monitor Counts
#bs_bm2 = EpicsSignalRO('BL14B:Det:BM2', name='bs_bm2')
noisy = EpicsSignalRO('prj:userCalc1', name='noisy')
scaler = EpicsScaler('prj:scaler1', name='scaler')


spvoigt = SynPseudoVoigt(
    'spvoigt', m1, 'm1', 
    center=-1.5 + 0.5*np.random.uniform(), 
    eta=0.2 + 0.5*np.random.uniform(), 
    sigma=0.001 + 0.05*np.random.uniform(), 
    scale=1e5,
    bkg=0.01*np.random.uniform())

#  RE(bp.scan([spvoigt], m1, -2, 0, 219))
