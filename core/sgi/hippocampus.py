from core.sgi.skeleton import Organ, sgi_body

class Hippocampus(Organ):
    """
    Memory System.
    """
    def __init__(self):
        super().__init__("Hippocampus")
        self.memories = []
        
    def recall(self, query):
        return f"🐘 HIPPOCAMPUS: Retrieving memory trace for '{query}'..."
        
    def encode(self, info):
        self.memories.append(info)
        return "🐘 HIPPOCAMPUS: Memory encoded."

hippocampus = Hippocampus()
sgi_body.add_organ(hippocampus)
