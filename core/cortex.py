from core.synapse import Synapse
from core.lobes.frontal import FrontalLobe
from core.lobes.temporal import TemporalLobe
import time

class Cortex:
    """The Biological Brain. Manages Lobes."""
    def __init__(self):
        self.synapse = Synapse()
        
        print("[Cortex] Initializing Neural Network...")
        self.frontal = FrontalLobe(self.synapse)
        self.temporal = TemporalLobe(self.synapse)
        # Add Occipital/Parietal later
        
        print("[Cortex] Brain Online.")

    def conscious_loop(self):
        """The Main Life Loop."""
        self.synapse.fire("CORTEX", "AWAKE")
        
        # Start Ears
        self.temporal.listen_loop()
        
        try:
            while True:
                time.sleep(1) # maintain consciousness
        except KeyboardInterrupt:
            print("[Cortex] Going to sleep...")
            
    def process_input(self, user_text):
        """Injects input into the nervous system."""
        self.synapse.fire("SENSORY", "USER_INPUT", {"text": user_text})
