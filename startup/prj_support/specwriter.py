
"""
a BlueSky callback that writes SPEC data files
"""


from collections import OrderedDict
import datetime
import os
from databroker import Broker


class SpecWriterCallback(object):
    """
    collect data from BlueSky RunEngine documents to write as SPEC data
    
    This gathers data form all documents and writes the file when the 
    "stop" document is received.  Only one scan is written to a data file.
    A flag could be added to the callback to write more than one scan 
    to a single data file.
    
    EXAMPLE::
    
        specwriter = SpecWriterCallback(path)
        RE.subscribe(specwriter.receiver)

    """
    
    def __init__(self, path=None, auto_write=True):
        self.clear()
        self.path = path or os.getcwd()
        self.auto_write = auto_write
        self.file_suffix = ".dat"
        self.uid_short_length = 8

    def clear(self):
        self.uid = None
        self.spec_filename = None   # TODO: refactor into a header class
        self.spec_epoch = None      # for both #E & #D line in header, also offset for all scans
        self.time = None            # full time from document
        self.spec_comment = None    # for first #C line in header
        self.comments = dict(start=[], event=[], descriptor=[], stop=[])
        self.data = OrderedDict()           # data in the scan
        self.detectors = OrderedDict()      # names of detectors in the scan
        self.hints = OrderedDict()          # why?
        self.metadata = OrderedDict()       # #MD lines in header
        self.motors = OrderedDict()         # names of motors in the scan
        self.positioners = OrderedDict()    # names in #O, values in #P
        self.columns = OrderedDict()        # #L in scan
        self.scan_command = None            # #S line

    def receiver(self, key, document):
        """receive all documents for handling"""
        xref = dict(
            start = self.start,
            descriptor = self.descriptor,
            event = self.event,
            bulk_events = self.bulk_events,
            stop = self.stop,
        )
        if key in xref:
            xref[key](document)
        else:
            print("custom_callback encountered:", key, document)
        return
    
    def start(self, doc):
        known_properties = """
            uid time project sample scan_id group owner
            detectors hints
            plan_type plan_name plan_args
        """.split()

        #print("start", doc["uid"])
        self.clear()
        self.uid = doc["uid"]
        self.spec_filename = self._build_file_name(doc)
        self.time = doc["time"]
        self.spec_epoch = int(self.time)
        self.spec_comment = "BlueSky  uid = " + self.uid
        self.T_or_M = "T"           # TODO: how to get this from the document stream?
        self.T_or_M_value = 1
        self.comments["start"].append("!!! #T line must be fixed !!!")
        dt = datetime.datetime.fromtimestamp(self.time)
        self.comments["start"].append("time = " + str(dt))
        
        # metadata
        for key in sorted(doc.keys()):
            if key not in known_properties:
                self.metadata[key] = doc[key]
        
        # various dicts
        for item in "detectors hints motors".split():
            if item in doc:
                obj = self.__getattribute__(item)
                for key in doc.get(item):
                    obj[key] = None         # TODO: get the contents
        
        self.comments["start"].insert(0, "plan_type = " + doc["plan_type"])
        self.scan_command = self._rebuild_scan_command(doc)
    
    def _build_file_name(self, doc):
        # TODO: better name?
        s = self.uid[:self.uid_short_length]
        s += self.file_suffix
        return s

    def _rebuild_scan_command(self, doc):
        s = str(doc.get("scan_id") or 1)    # TODO: improve the default
        s += "  " + doc.get("plan_name", "") + " "

        # FIXME: too much content, use names only for detectors and motors
        obj = doc["plan_args"]
        s += "[" + " ".join(obj["detectors"]) + "]"
        for k, v in obj.items():
            if k not in ("detectors",):
                s += " " + k + "=" + str(v)   # FIXME: not general, not at all
        return s
        
    def descriptor(self, doc):
        #print("descriptor", doc["uid"])
        if doc["name"] == "primary":        # TODO: general?
            for k in doc["data_keys"].keys():
                self.data[k] = []
            self.data["Epoch"] = []
            self.data["Epoch_float"] = []
        
            # SPEC data files have implied defaults
            # SPEC default: X axis in 1st column and Y axis in last column
            where = len(self.motors) > 0
            self.data.move_to_end("Epoch_float", last=where)
            self.data.move_to_end("Epoch")
            if len(self.motors) > 0:
                # find 1st motor and move to last
                motor_name = list(self.motors.keys())[0]
                self.data.move_to_end(motor_name, last=False)
            # monitor (detector) in next to last position but how can we get that name here?
            if len(self.detectors) > 0:
                # find 1st detector and move to last
                det_name = list(self.detectors.keys())[0]
                self.data.move_to_end(det_name)

    def event(self, doc):
        #print("event", doc["uid"])
        for k in self.data.keys():
            if k == "Epoch":
                v = int(doc["time"] - self.time)
            elif k == "Epoch_float":
                v = doc["time"] - self.time
            else:
                v = doc["data"][k]
            self.data[k].append(v)
    
    def bulk_events(self, doc):
        #print("bulk_events", doc["uid"])
        pass
    
    def stop(self, doc):
        #print("stop", doc["uid"])
        if "num_events" in doc:
            for k, v in doc["num_events"].items():
                self.comments["stop"].append("num_events_{} = {}".format(k, v))
        if "time" in doc:
            dt = datetime.datetime.fromtimestamp(doc["time"])
            self.comments["stop"].append("time = " + str(dt))
        if "exit_status" in doc:
            self.comments["stop"].append("exit_status = " + doc["exit_status"])
        else:
            self.comments["stop"].append("exit_status = not available")

        if self.auto_write:
            self.write_file()

    def write_file(self):
        dt = datetime.datetime.fromtimestamp(self.spec_epoch)
        lines = []
        lines.append("#F " + self.spec_filename)
        lines.append("#E " + str(self.spec_epoch))
        lines.append("#D " + datetime.datetime.strftime(dt, "%c"))
        lines.append("#C " + self.spec_comment)
        # TODO: #O line(s)
        for k, v in self.metadata.items():
            lines.append("#MD {} = {}".format(k, v))    # "#MD" is our ad hoc SPEC data tag

        lines.append("")
        lines.append("#S " + self.scan_command)
        lines.append("#D " + datetime.datetime.strftime(dt, "%c"))
        lines.append("#{} {}".format(self.T_or_M, self.T_or_M_value))
        self.T_or_M = "T"           # TODO: how to get this from the document stream?
        self.T_or_M_value = 1

        # TODO: #P line(s)
        for v in self.comments["start"]:
            lines.append("#C " + v)
        n = len(self.data["Epoch"])
        for v in self.comments["descriptor"]:
            lines.append("#C " + v)

        lines.append("#N " + str(n))
        lines.append("#L " + "  ".join(self.data.keys()))
        for i in range(n):
            s = [str(self.data[k][i]) for k in self.data.keys()]
            lines.append(" ".join(s))

        for v in self.comments["event"]:
            lines.append("#C " + v)

        for v in self.comments["stop"]:
            lines.append("#C " + v)

        #print("\n".join(lines))
        fname = os.path.join(self.path, self.spec_filename)
        with open(fname, "w") as f:
            f.write("\n".join(lines))
            print("wrote SPEC file: " + fname)
