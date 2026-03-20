from core.sgi.skeleton import Organ, sgi_body

class Liver(Organ):
    """
    Filtration System (Sanitization).
    """
    def __init__(self):
        super().__init__("Liver")
        
    def filter_toxins(self, data):
        data = data.replace("rm -rf", "[REDACTED]")
        data = data.replace("password", "[REDACTED]")
        return f"🧪 LIVER: Detoxified input. Result: {data}"

liver = Liver()
sgi_body.add_organ(liver)
