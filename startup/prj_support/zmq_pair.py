
"""
Python ZeroMQ pair connection example

:see: http://learning-0mq-with-pyzmq.readthedocs.io/en/latest/pyzmq/patterns/pair.html
:seealso: https://stackoverflow.com/questions/23855563/simple-client-server-zmq-in-python-to-send-multiple-lines-per-request
"""

import zmq

__all__ = ['ZMQ_Pair', 'server_example', 'client_example']

class ZMQ_Pair(object):
    """
    example 0MQ Pair connection: one server, only one client
    """
    
    port = "5556"
    socket_type = zmq.PAIR
    host = "*"
    
    def __init__(self, host=None, port=None):
        self.port = str(port or self.port)
        self.host=host or self.host
        
        kw = dict(host=self.host, port=self.port)
        self.addr = "tcp://{host}:{port}".format(**kw)
        
        self.context = zmq.Context()
        self.socket = self.context.socket(self.socket_type)
        if self.host == "*":
            self.socket.bind(self.addr)
        else:
            self.socket.connect(self.addr)
    
    def receive(self):
        return self.socket.recv()
    
    def send_string(self, msg):
        self.socket.send_string(str(msg))
    
    def send(self, chunk):
        self.socket.send(chunk)


# example that shows polling for input
# http://learning-0mq-with-pyzmq.readthedocs.io/en/latest/pyzmq/multisocket/zmqpoller.html


def server_example():
    """
    from zmq_pair import server_example
    server_example()
    """
    from zmq_pair import ZMQ_Pair
    import socket
    eot_signal_text = b"END OF TRANSMISSION"

    listener = ZMQ_Pair()
    print("0MQ server Listening now: {}".format(str(listener)))
    print("  host: {}".format(listener.host))
    print("  port: {}".format(listener.port))
    print("  addr: {}".format(listener.addr))
    serverhost = socket.gethostname() or 'localhost' 
    print("  serverhost: {}".format(serverhost))
    print("#"*40)
    while True:
        msg = listener.receive()
        #print(msg.decode())
        if len(msg) < 12:
            print(type(msg), msg.decode())
        else:
            print(type(msg), len(msg))
        if msg == eot_signal_text:
            break
    print("\n 0MQ server stopped listening")


def client_example(filename, host=None):
    """
    from zmq_pair import client_example
    client_example("zmq_pair.py")   # on localhost
    # or
    client_example("zmq_pair.py", "10.0.2.2") # on VM
    """
    from zmq_pair import ZMQ_Pair
    eot_signal_text = "END OF TRANSMISSION"

    talker = ZMQ_Pair(host or "localhost")
    print("Starting 0MQ client: {}".format(str(talker)))
    print("  host: {}".format(talker.host))
    print("  port: {}".format(talker.port))
    print("  addr: {}".format(talker.addr))
    print("#"*40)
    # send this file over 0mq as an example
    with open(filename, 'r') as f:
        for line in f:
            talker.send_string(line.rstrip("\n"))
    talker.send_string(eot_signal_text)
    print("\nEnding 0MQ client")
