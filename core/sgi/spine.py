from core.sgi.skeleton import Organ, sgi_body

class Spine(Organ):
    """
    Central Nervous System (Event Bus).
    """
    def __init__(self):
        super().__init__("Spine")
        self.nerves = [] # Subscribers
        
    def transmit_impulse(self, signal):
        return f"⚡ SPINAL SIGNAL: {signal.upper()} transmitted to all nerves."

spine = Spine()
sgi_body.add_organ(spine)
