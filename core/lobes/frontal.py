from core.agent import Agent
from core.synapse import Synapse

class FrontalLobe:
    """Executive Function. Wraps the main Agent logic."""
    def __init__(self, synapse: Synapse):
        self.synapse = synapse
        self.agent = Agent() # The legacy agent, now a sub-module
        self.synapse.connect(self.on_signal)
        
    def on_signal(self, signal):
        if signal.type == "USER_INPUT":
            # Think about it
            print(f"[Frontal Lobe] Processing: {signal.payload}")
            response = self.agent.run(signal.payload['text'])
            self.synapse.fire("FRONTAL_LOBE", "DECISION_MADE", {"result": response})
            
    def think(self, thought):
        return self.agent.run(thought)
