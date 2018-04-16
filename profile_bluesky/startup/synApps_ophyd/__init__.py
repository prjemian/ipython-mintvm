
"""
Ophyd support for synApps configuration of EPICS records

Support the default structures as provided by the 
synApps template XXX IOC.

EXAMPLES
========

    import synApps_ophyd
    scans = synApps_ophyd.EpicsSscanDevice("xxx:", name="scans")
    calcs = synApps_ophyd.EpicsUserCalcsDevice("xxx:", name="calcs")

    calc1 = calcs.calc1
    synApps_ophyd.swait_setup_random_number(calc1)

    synApps_ophyd.swait_setup_incrementer(calcs.calc2)
    
    calc1.reset()

Compare this effort with a similar project:
https://github.com/klauer/recordwhat
"""


from .synApps_sscan import *
from .synApps_swait import *
