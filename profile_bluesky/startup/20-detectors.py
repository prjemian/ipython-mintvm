print(__file__)

"""various detectors and other signals"""

from APS_BlueSky_tools.examples import SynPseudoVoigt

noisy = EpicsSignalRO('prj:userCalc1', name='noisy')
scaler = EpicsScaler('prj:scaler1', name='scaler')
#sc2 = ScalerCH('prj:scaler1', name='sc2')


spvoigt = SynPseudoVoigt(
    'spvoigt', m1, 'm1', 
    center=-1.5 + 0.5*np.random.uniform(), 
    eta=0.2 + 0.5*np.random.uniform(), 
    sigma=0.001 + 0.05*np.random.uniform(), 
    scale=1e5,
    bkg=0.01*np.random.uniform())

#  RE(bp.scan([spvoigt], m1, -2, 0, 219))
