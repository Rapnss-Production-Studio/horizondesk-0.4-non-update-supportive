import gc
from core.sgi.skeleton import Organ, sgi_body

class Kidneys(Organ):
    """
    Waste Management (Garbage Collection).
    """
    def __init__(self):
        super().__init__("Kidneys")
        
    def flush(self):
        n = gc.collect()
        return f"💧 KIDNEYS: Flushed {n} objects from memory."

kidneys = Kidneys()
sgi_body.add_organ(kidneys)
