import time
from core.sgi.skeleton import Organ, sgi_body

class Heart(Organ):
    """
    Cardiovascular System (Time/Rhythm).
    """
    def __init__(self):
        super().__init__("Heart")
        self.bpm = 60
        
    def beat(self):
        return f"❤️ LUB-DUB. System Pulse Active at {self.bpm} BPM. Time: {time.time()}"
        
    def adrenaline_rush(self):
        self.bpm = 120
        return "💉 ADRENALINE SURGE! Clock speed doubled."

heart = Heart()
sgi_body.add_organ(heart)
