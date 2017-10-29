
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
    calc1.desc.put("uniform random numbers")

    synApps_ophyd.swait_setup_incrementer(calcs.calc2)
    calcs.calc2.desc.put("incrementer")
    
    calc1.reset()

"""


from .synApps_sscan import *
from .synApps_swait import *
