from core.sgi.skeleton import Organ, sgi_body

class Eyes(Organ):
    """
    Visual System (Perception).
    """
    def __init__(self):
        super().__init__("Eyes")
        
    def gaze(self, target):
        return f"👁️ GAZE: Focusing retinas on '{target}'."
    
    def blink(self):
        return "👁️ BLINK: Refreshing tear film."

eyes = Eyes()
sgi_body.add_organ(eyes)
