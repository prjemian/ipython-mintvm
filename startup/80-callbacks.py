print(__file__)

# custom callbacks


class CustomCallbackCollector(object):
    """
    My BlueSky support to collect *all* documents emitted
    """
    
    def __init__(self):
        self.documents = {}

    def receiver(self, key, document):
        """keep all documents from recent plan in memory"""
        if key == "start":
            self.documents = {key: document}
        elif key in ("descriptor", "event"):
            if key not in self.documents:
                self.documents[key] = []
            self.documents[key].append(document)
        elif key == "stop":
            self.documents[key] = document
            print("exit status:", document["exit_status"])
            if "descriptor" in self.documents:
                print("# descriptor(s):", len(self.documents["descriptor"]))
            if "event" in self.documents:
                print("# event(s):", len(self.documents["event"]))
        else:
            print("custom_callback (unhandled):", key, document)
        return


cb_collector = CustomCallbackCollector()
callback_db['cb_collector'] = RE.subscribe(cb_collector.receiver)


from prj_support.zmq_pair import ZMQ_Pair

class MyCallback0MQ(object):
    """
    My BlueSky 0MQ talker to send *all* documents emitted
    """
    
    eot_signal_text = b"END OF TRANSMISSION"
    
    def __init__(self, host=None, port=None, detector=None):
        self.talker = ZMQ_Pair(host or "localhost", port or "5556")
        self.detector = detector
    
    def end(self):
        self.talker.send_string(self.talker.eot_signal_text.decode)

    def receiver(self, key, document):
        """receive from RunEngine, send from 0MQ talker"""
        self.talker.send_string(key)
        self.talker.send_string(document)
        if key == "event" and self.detector is not None:
            # Is it faster to pick this up by EPICS CA?
            # Using 0MQ, no additional library is needed
            self.talker.send_string("rank")
            self.talker.send_string(str(len(self.detector.image.shape)))
            self.talker.send_string("shape")
            self.talker.send_string(str(self.detector.image.shape))
            self.talker.send_string("image")
            self.talker.send(self.detector.image)

try:
    zmq_talker = MyCallback0MQ(detector=plainsimdet.image)
    callback_db['zmq_talker'] = RE.subscribe(zmq_talker.receiver)
except Exception:
    pass
