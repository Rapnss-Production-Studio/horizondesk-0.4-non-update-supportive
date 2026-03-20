from core.tools import BaseTool
from core.ghost.cloak import ghost
from core.ghost.scrubber import scrubber

class VanishTool(BaseTool):
    def __init__(self):
        super().__init__("Vanish", "Engages Ghost Protocol: Shifts identity and sanitizes RAM. Input: None.")

    def execute(self, payload=None):
        msg1 = ghost.engage_cloak()
        msg2 = scrubber.purge_memory()
        return f"[The Ghost] Protocol Active.\n{msg1}\n{msg2}"

class SecureDeleteTool(BaseTool):
    def __init__(self):
        super().__init__("SecureDelete", "Permanently obliterates a file (DoD 3-Pass). Irrecoverable. Input: 'path'.")

    def execute(self, path=None, payload=None):
        p = path or (payload.get('path') if payload else None)
        if not p: return "Path required."
        
        return scrubber.secure_delete(p)
