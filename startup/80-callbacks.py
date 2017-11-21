print(__file__)

# custom callbacks

import APS_BlueSky_tools.callbacks
import APS_BlueSky_tools.filewriters
from APS_BlueSky_tools.zmq_pair import ZMQ_Pair


doc_collector = APS_BlueSky_tools.callbacks.DocumentCollectorCallback()
callback_db['doc_collector'] = RE.subscribe(doc_collector.receiver)

specwriter = APS_BlueSky_tools.filewriters.SpecWriterCallback()
specwriter.newfile(os.path.join("/tmp", specwriter.spec_filename))
callback_db['specwriter'] = RE.subscribe(specwriter.receiver)
print("SPEC data file:", specwriter.spec_filename)



class MyCallback0MQ(object):
    """
    My BlueSky 0MQ talker to send *all* documents emitted
    """
    
    def __init__(self, host=None, port=None, detector=None):
        self.talker = ZMQ_Pair(host or "localhost", port or "5556")
        self.detector = detector
    
    def end(self):
        self.talker.send_string(self.talker.eot_signal_text.decode())

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

#try:
#    zmq_talker = MyCallback0MQ(detector=plainsimdet.image)
#    callback_db['zmq_talker'] = RE.subscribe(zmq_talker.receiver)
#except Exception:
#    pass
