from core.tools import BaseTool
from core.quantum.engine import QuantumCore
import json

# Global Quantum Core Singleton
q_core = QuantumCore()

class QuantumDecideTool(BaseTool):
    def __init__(self):
        super().__init__("QuantumDecide", "Uses Quantum Probability to pick the best option from a list. Input: 'context', 'options' (list).")

    def execute(self, context=None, options=None, payload=None):
        if payload and isinstance(payload, dict):
             context = payload.get('context')
             options = payload.get('options')
             
        if not options or not isinstance(options, list):
            return "Error: 'options' must be a list of strings."
            
        best_option = q_core.decide(context or "General State", options)
        return f"Quantum Collapse Result: The best path is '{best_option}'."
