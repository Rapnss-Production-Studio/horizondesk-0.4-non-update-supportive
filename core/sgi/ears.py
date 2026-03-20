from core.sgi.skeleton import Organ, sgi_body

class Ears(Organ):
    """
    Auditory System.
    """
    def __init__(self):
        super().__init__("Ears")
        
    def listen(self):
        return "👂 LISTENING: Analyzing audio stream for keywords..."

ears = Ears()
sgi_body.add_organ(ears)
