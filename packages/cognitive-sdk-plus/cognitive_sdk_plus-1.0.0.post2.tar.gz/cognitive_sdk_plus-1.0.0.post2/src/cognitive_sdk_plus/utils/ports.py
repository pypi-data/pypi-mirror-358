# cognitive_sdk/utils/ports.py
import socket
import threading

class PortManager:
    _used_ports = set()
    _lock = threading.Lock()

    @classmethod
    def get_free_port(cls):
        with cls._lock:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(("", 0))
            port = s.getsockname()[1]
            s.close()
            if port in cls._used_ports:
                # Just recursively call again
                return cls.get_free_port()
            cls._used_ports.add(port)
        return port

    @classmethod
    def release_port(cls, port):
        with cls._lock:
            cls._used_ports.discard(port)