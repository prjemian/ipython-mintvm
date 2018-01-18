print(__file__)

from datetime import datetime


def print_scan_ids(name, start_doc):
    """prints scan IDs, call at start of each scan"""
    msg = "Transient Scan ID: "
    msg += str(start_doc['scan_id'])
    msg += " at "
    msg += str(datetime.isoformat(datetime.now()))
    print(msg)
    print("Persistent Unique Scan ID: '{0}'".format(start_doc['uid']))

# redundant now, provided in BestEffortCallback.start()
#callback_db['print_scan_ids'] = RE.subscribe(print_scan_ids, 'start')


# Set up default metadata

RE.md['beamline_id'] = 'developer'  # TODO: !!!YOUR BEAMLINE HERE!!!
RE.md['proposal_id'] = None
RE.md['pid'] = os.getpid()


import socket 
import getpass 
HOSTNAME = socket.gethostname() or 'localhost' 
USERNAME = getpass.getuser() or 'synApps_xxx_user' 
RE.md['login_id'] = USERNAME + '@' + HOSTNAME
RE.md['BLUESKY_VERSION'] = bluesky.__version__
RE.md['OPHYD_VERSION'] = ophyd.__version__

#import os
#for key, value in os.environ.items():
#    if key.startswith("EPICS"):
#        RE.md[key] = value

print("Metadata dictionary:")
for k, v in sorted(RE.md.items()):
    print("RE.md['%s']" % k, "=", v)
