import subprocess
from core.sgi.skeleton import Organ, sgi_body

class Muscles(Organ):
    """
    Muscular System (Force/Execution).
    """
    def __init__(self):
        super().__init__("Muscles")
        
    def flex(self, command):
        # Simulates exertion
        return f"💪 MUSCLE FLEX: Executing forceful command '{command}'."

muscles = Muscles()
sgi_body.add_organ(muscles)
