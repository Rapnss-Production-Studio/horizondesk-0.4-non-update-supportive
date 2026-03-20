from core.tools import BaseTool
from core.diplomat.engine import diplomat

class PersuadeTool(BaseTool):
    def __init__(self):
        super().__init__("Persuade", "Generates a psychologically tailored argument. Input: 'goal', 'target_sample' (optional text from target).")

    def execute(self, goal=None, target_sample=None, payload=None):
        g = goal or (payload.get('goal') if payload else None)
        ts = target_sample or (payload.get('target_sample') if payload else None)
        
        if not g: return "Goal required."
        
        text, strategy = diplomat.formulate_argument(g, ts)
        return f"[The Diplomat] Strategy Used: {strategy}\n\n{text}"

class NegotiateLimitTool(BaseTool):
    def __init__(self):
        super().__init__("NegotiateRateLimit", "Generates a formal request to increase API limits. Input: 'api_name'.")

    def execute(self, api_name=None, payload=None):
        an = api_name or (payload.get('api_name') if payload else None)
        if not an: return "API Name required."
        
        text = diplomat.negotiate_rate_limit(an)
        return f"[The Diplomat] Negotiation Draft:\n\n{text}"
