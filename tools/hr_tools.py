from core.tools import BaseTool
from core.corporation.hr import hr

class ReviewPerformanceTool(BaseTool):
    def __init__(self):
        super().__init__("ReviewPerformance", "Evaluates an agent's records. Input: 'agent_id'.")

    def execute(self, agent_id=None, payload=None):
        aid = agent_id or (payload.get('agent_id') if payload else None)
        if not aid: return "Agent ID required."
        return hr.evaluate_agent(aid)

class FireAgentTool(BaseTool):
    def __init__(self):
        super().__init__("FireAgent", "Terminates an agent if performance is sub-optimal. Input: 'agent_id'.")

    def execute(self, agent_id=None, payload=None):
        aid = agent_id or (payload.get('agent_id') if payload else None)
        if not aid: return "Agent ID required."
        return hr.fire_agent(aid)
