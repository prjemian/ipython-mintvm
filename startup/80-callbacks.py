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
    
    def __init__(self, host=None, port=None, detector=None, signal_name=None):
        self.talker = ZMQ_Pair(host or "localhost", port or "5556")
        self.detector = detector
        self.signal_name = signal_name
    
    def end(self):
        """ZMQ client tells the server to end the connection"""
        self.talker.end()

    def receiver(self, key, document):
        """receive from RunEngine, send from 0MQ talker"""
        mona_zmq_sender(self.talker, key, document, self.detector, self.signal_name)


def demo_start_mona_callback_as_zmq_client():
    """
    show how to use this code with the MONA project
    First: be sure the ZMQ server code is already running (outside of BlueSky).
    Then, run this code.  If the server is not running, this code may fail.
    """
    for key in "doc_collector specwriter zmq_talker BestEffortCallback".split():
        if key in callback_db:
            RE.unsubscribe(callback_db[key])
            del callback_db[key]
    zmq_talker = MonaCallback0MQ(
        detector=adsimdet.image,
        signal_name=adsimdet.image.array_counter.name)
    callback_db['zmq_talker'] = RE.subscribe(zmq_talker.receiver)
    
    calc2 = calcs.calc2
    swait_setup_incrementer(calc1)
    swait_setup_random_number(calc2)
    ad_continuous_setup(adsimdet, acq_time=0.1)
    scaler.preset_time.put(0.5)
    scaler.channels.read_attrs = ['chan1', 'chan2', 'chan3', 'chan6']
    # plan = bp.count([adsimdet], num=3)
    # monitors = [calc1.val, calc2.val]

    plan = bp.count([scaler], num=3)
    monitors = [adsimdet.image.array_counter, calc1.val, calc2.val]
    
    @bpp.monitor_during_decorator(monitors)
    def _the_plan(detectors, acquire, num=1):
        acquire.put(1)
        yield from bp.count(detectors, num=num)
        acquire.put(0)
    
    RE(_the_plan([scaler], adsimdet.cam.acquire, num=3))

    return zmq_talker
