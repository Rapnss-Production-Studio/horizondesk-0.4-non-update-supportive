from core.tools import BaseTool
from core.bard.composer import bard
import os

class CreativeWriteTool(BaseTool):
    def __init__(self):
        super().__init__("CreativeWrite", "Writes novels, poems, or screenplays derived from system entropy. Input: 'prompt', 'type' (novel/poem/screenplay).")

    def execute(self, prompt=None, type="novel", payload=None):
        p = prompt or (payload.get('prompt') if payload else None)
        t = type or (payload.get('type') if payload else 'novel')
        
        if not p: return "Prompt required."
        
        text = bard.write_masterpiece(p, t)
        return f"[The Bard] Generated {t}:\n\n{text}"

class ComposeMusicTool(BaseTool):
    def __init__(self):
        super().__init__("ComposeMusic", "Composes a unique MIDI symphony based on mood. Input: 'mood' (happy/sad), 'filename'.")

    def execute(self, mood="happy", filename=None, payload=None):
        m = mood or (payload.get('mood') if payload else 'happy')
        f = filename or (payload.get('filename') if payload else f"opus_{os.urandom(4).hex()}.mid")
        
        if not f.endswith(".mid"): f += ".mid"
        
        try:
            res = bard.compose_music(m, f)
            return f"[The Bard] {res}"
        except Exception as e:
            return f"Composition Error: {e}"
