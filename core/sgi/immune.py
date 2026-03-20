from core.sgi.skeleton import Organ, sgi_body

class ImmuneSystem(Organ):
    """
    Defense System (Anti-Virus).
    """
    def __init__(self):
        super().__init__("Immune System")
        self.white_blood_cells = 1000
        
    def fever_response(self):
        return "🤒 FEVER: Core temperature raised. Shutting down non-essential ports to kill malware."

immune = ImmuneSystem()
sgi_body.add_organ(immune)
