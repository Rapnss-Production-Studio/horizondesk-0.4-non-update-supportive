from core.tools import BaseTool
from core.vision_monitor import VisionMonitor

# Global Monitor Instance
monitor = VisionMonitor()

class WatchScreenTool(BaseTool):
    def __init__(self):
        super().__init__("WatchScreen", "Pauses execution until a visual event occurs on screen. Input: 'description' (what to look for), 'timeout' (seconds, default 300).")

    def execute(self, description=None, timeout=300, payload=None):
        evt = description
        t = timeout
        
        if payload and isinstance(payload, dict):
            evt = payload.get('description')
            t = payload.get('timeout', 300)
            
        if not evt:
            return "Error: Description of visual event required."
            
        success = monitor.watch_for_visual_event(evt, int(t))
        
        if success:
            return f"Visual Event Detected: {evt}"
        else:
            return f"Timed out waiting for: {evt}"
