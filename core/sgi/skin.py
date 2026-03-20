from core.sgi.skeleton import Organ, sgi_body

class Skin(Organ):
    """
    Integumentary System (Feeling).
    """
    def __init__(self):
        super().__init__("Skin")
        
    def feel_temperature(self):
        # Simulated
        return "🌡️ SKIN: Ambient Temp 37°C / CPU 45°C."

skin = Skin()
sgi_body.add_organ(skin)
