from core.tools import BaseTool
from core.oracle.prophet import oracle
# We need a way to fetch data. We'll simulate or use a lightweight fetch inside the tool
# to avoid circular imports with web tools.

class PredictFutureTool(BaseTool):
    def __init__(self):
        super().__init__("PredictFuture", "Predicts the future trend of a topic. Input: 'topic'.")

    def execute(self, topic=None, payload=None):
        t = topic or (payload.get('topic') if payload else None)
        if not t: return "Topic required."
        
        # 1. Ingest (Mocking live feed for 'Deep' Demo, or we could integrate WebSearch here)
        # For true deep implementation, we assume the Oracle listens to the 'Synapse'.
        # But we can force feed it.
        oracle.ingest_signal(f"User is interested in {t}")
        
        # 2. Predict
        future = oracle.predict_trend(t)
        return f"[The Oracle] Prediction for '{t}':\n{future}"

class PreCrimeTool(BaseTool):
    def __init__(self):
        super().__init__("PreCrimeCheck", "Analyzes an action for potential catastrophic failure. Input: 'action'.")

    def execute(self, action=None, payload=None):
        a = action or (payload.get('action') if payload else None)
        if not a: return "Action description required."
        
        safe, risk = oracle.pre_error_analysis(a)
        
        status = "DENIED" if not safe else "AUTHORIZED"
        return f"[Minority Report] Action: '{a}'\nRisk Level: {risk:.2f}\nStatus: {status}"
