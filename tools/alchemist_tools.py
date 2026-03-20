from core.tools import BaseTool
from core.alchemist.transmuter import alchemist

class TransmuteTool(BaseTool):
    def __init__(self):
        super().__init__("TransmuteFile", "Converts any file to any format using Graph Theory pathfinding. Input: 'path', 'target_format'.")

    def execute(self, path=None, target_format=None, payload=None):
        p = path or (payload.get('path') if payload else None)
        t = target_format or (payload.get('target_format') if payload else None)
        
        if not p or not t: return "Path and Target Format required."
        
        try:
            result = alchemist.transmute(p, t)
            return f"[The Alchemist] {result}"
        except Exception as e:
            return f"[The Alchemist] Failed: {e}"
