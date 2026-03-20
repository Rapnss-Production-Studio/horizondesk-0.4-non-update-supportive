from core.tools import BaseTool
from core.holodeck.engine import holodeck
import os

class SimulateActionTool(BaseTool):
    def __init__(self):
        super().__init__("SimulateAction", "Runs an action in the Holodeck to test outcome/chaos. Input: 'action' (delete/create_file), 'path'.")

    def execute(self, action=None, path=None, payload=None):
        a = action or (payload.get('action') if payload else None)
        p = path or (payload.get('path') if payload else None)
        
        if not a or not p: return "Action and Path required."
        
        # 1. Initialize (Lazy Mirroring of parent dir)
        parent = os.path.dirname(p)
        if not parent: parent = os.getcwd()
        
        # If simulation not active or looking at a different execution context, reboot it
        # (Simplification for tool usage: we re-init per call for safety in this version)
        init_msg = holodeck.initialize_simulation(parent)
        
        # 2. Simulate
        result = holodeck.simulate_command(a, p)
        
        # 3. Analyze
        chaos = holodeck.calculate_chaos()
        risk = "LOW"
        if chaos > 0.1: risk = "MEDIUM"
        if chaos > 0.5: risk = "EXTREME"
        
        holodeck.shutdown()
        
        return f"""[The Holodeck]
Init: {init_msg}
Action: {a} {p}
Result: {result}
Chaos Metric: {chaos:.2%} ({risk})
Recommendation: {"PROCEED" if chaos < 0.2 else "CAUTION"}"""
