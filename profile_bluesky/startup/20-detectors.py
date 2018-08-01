print(__file__)

"""various detectors and other signals"""

# noisy = EpicsSignalRO('prj:userCalc1', name='noisy')
# scaler = EpicsScaler('prj:scaler1', name='scaler')

scaler = ScalerCH('prj:scaler1', name='scaler')
scaler.match_names()
use_EPICS_scaler_channels(scaler)
