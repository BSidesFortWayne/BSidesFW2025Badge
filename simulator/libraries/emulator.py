import sys
import socket
import json
import time
import _thread

class EmulatorCommunication:
    def __init__(self):
        self.socket = socket.socket()
        self.socket.connect(socket.getaddrinfo('127.0.0.1', 4455)[0][-1])
        self.lock = _thread.allocate_lock()  # ensures only one sender at a time

    def send(self, data):
        with self.lock:
            # Send data
            self.socket.send(data)
            # Receive response
            raw_response = self.socket.recv(1024)
        return json.loads(raw_response)

def get_socket():
    # Singleton pattern so we only create once
    if hasattr(sys.modules[__name__], '_s'):
        return sys.modules[__name__]._s

    s = EmulatorCommunication()
    setattr(sys.modules[__name__], '_s', s)
    return s

def send_command(module, command, **kwargs):
    payload = {
        'module': module,
        'command': command,
        'parameters': kwargs
    }
    return get_socket().send(json.dumps(payload).encode() + b'\n')
