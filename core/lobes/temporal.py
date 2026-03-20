from core.voice import VoiceEngine
from core.memory import MemorySystem
from core.synapse import Synapse
import threading

class TemporalLobe:
    """Memory & Language Center."""
    def __init__(self, synapse: Synapse):
        self.synapse = synapse
        self.memory = MemorySystem()
        self.voice = VoiceEngine()
        self.synapse.connect(self.on_signal)
        
    def on_signal(self, signal):
        if signal.type == "SPEAK":
            text = signal.payload.get('text')
            self.voice.speak(text)
        elif signal.type == "REMEMBER":
            key = signal.payload.get('key')
            val = signal.payload.get('value')
            self.memory.add_memory(key, val)
            
    def listen_loop(self):
        """Starts a thread to listen for wake words."""
        def _loop():
            while True:
                # Simpler check for now. In real neural net, this would fire SIGNALS.
                text = self.voice.listen(timeout=5)
                if text:
                    self.synapse.fire("TEMPORAL_LOBE", "HEARD_AUDIO", {"text": text})
        
        t = threading.Thread(target=_loop, daemon=True)
        t.start()
