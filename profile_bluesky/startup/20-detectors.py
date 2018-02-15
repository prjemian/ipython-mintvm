print(__file__)

"""various detectors and other signals"""

from APS_BlueSky_tools.examples import SynPseudoVoigt

# this is DEMO work only
# do these before connecting (autosave not configured yet)
_xref = dict(
    NM1 = 'clock',
    NM2 = 'I0',
    NM3 = 'I',
    NM4 = 'other',
    NM5 = 'other',
    NM6 = 'one space',
    NM8 = 'many    spaces',
)
_channel_names = []
#for k, v in _xref.items():
#    epics.caput('prj:scaler1.'+k, v)
#    k = 'chan%02d' % int(k.lstrip('NM'))
#    _channel_names.append(k)

noisy = EpicsSignalRO('prj:userCalc1', name='noisy')
scaler = EpicsScaler('prj:scaler1', name='scaler')
sc2 = ScalerCH('prj:scaler1', name='sc2')
#sc2.channels.read_attrs = _channel_names
#sc2.channels.configuration_attrs = _channel_names

spvoigt = SynPseudoVoigt(
    'spvoigt', m1, 'm1', 
    center=-1.5 + 0.5*np.random.uniform(), 
    eta=0.2 + 0.5*np.random.uniform(), 
    sigma=0.001 + 0.05*np.random.uniform(), 
    scale=1e5,
    bkg=0.01*np.random.uniform())

#  RE(bp.scan([spvoigt], m1, -2, 0, 219))
