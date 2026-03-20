from core.sgi.skeleton import Organ, sgi_body

class Hands(Organ):
    """
    Manipulation System (Dexterity).
    """
    def __init__(self):
        super().__init__("Hands")
        
    def grab(self, object_path):
        return f"🖐️ GRAB: Holding object '{object_path}'."
        
    def drop(self):
        return "🖐️ DROP: Released object."

hands = Hands()
sgi_body.add_organ(hands)
