import time
import uuid

class Signal:
    def __init__(self, source, type, payload=None):
        self.id = str(uuid.uuid4())
        self.timestamp = time.time()
        self.source = source
        self.type = type
        self.payload = payload or {}
    
    def __repr__(self):
        return f"[Signal] {self.source} -> {self.type}: {self.payload}"

class Synapse:
    """The Nervous System. Handles Event Bus."""
    def __init__(self):
        self.listeners = [] # List of callbacks
        self.history = []
    
    def connect(self, callback):
        self.listeners.append(callback)
    
    def fire(self, source, type, payload=None):
        sig = Signal(source, type, payload)
        self.history.append(sig)
        # Broadcast
        for callback in self.listeners:
             try:
                 callback(sig)
             except Exception as e:
                 print(f"[Synapse Error] {e}")
        return sig
