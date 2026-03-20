from core.sgi.skeleton import Organ, sgi_body

class BrocasArea(Organ):
    """
    Language Production.
    """
    def __init__(self):
        super().__init__("Broca's Area")
        
    def construct_sentence(self, thought):
        return f"🗣️ BROCA: Formatted thought '{thought}' into grammatical structure."

broca = BrocasArea()
sgi_body.add_organ(broca)
