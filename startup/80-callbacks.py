print(__file__)

# custom callbacks

import APS_BlueSky_tools.callbacks
import APS_BlueSky_tools.filewriters
from APS_BlueSky_tools.zmq_pair import ZMQ_Pair, mona_zmq_sender


doc_collector = APS_BlueSky_tools.callbacks.DocumentCollectorCallback()
callback_db['doc_collector'] = RE.subscribe(doc_collector.receiver)

specwriter = APS_BlueSky_tools.filewriters.SpecWriterCallback()
specwriter.newfile(os.path.join("/tmp", specwriter.spec_filename))
callback_db['specwriter'] = RE.subscribe(specwriter.receiver)
print("SPEC data file:", specwriter.spec_filename)



class MonaCallback0MQ(object):
    """
    My BlueSky 0MQ talker to send *all* documents emitted
    """
    
    def __init__(self, host=None, port=None, detector=None):
        self.talker = ZMQ_Pair(host or "localhost", port or "5556")
        self.detector = detector
    
    def end(self):
        """ZMQ client tells the server to end the connection"""
        self.talker.end()

    def receiver(self, key, document):
        """receive from RunEngine, send from 0MQ talker"""
        mona_zmq_sender(self.talker, key, document, self.detector)


def demo_start_mona_callback_as_zmq_client():
    """
    show how to use this code with the MONA project
    First: be sure the ZMQ server code is already running (outside of BlueSky).
    Then, run this code.  If the server is not running, this code may fail.
    """
    for key in "doc_collector specwriter zmq_talker".split():
        if key in callback_db:
            RE.unsubscribe(callback_db[key])
            del callback_db[key]
    zmq_talker = MonaCallback0MQ(detector=plainsimdet.image)
    callback_db['zmq_talker'] = RE.subscribe(zmq_talker.receiver)
    RE(bp.count([plainsimdet], num=2))
    return zmq_talker
