from core.tools import BaseTool
from core.corporation.hierarchy import org_chart

class AssignRoleTool(BaseTool):
    def __init__(self):
        super().__init__("AssignRole", "Assigns a rank to an Agent ID. Input: 'agent_id', 'rank' (CEO/MANAGER/WORKER).")

    def execute(self, agent_id=None, rank=None, payload=None):
        aid = agent_id or (payload.get('agent_id') if payload else None)
        r = rank or (payload.get('rank') if payload else None)
        
        if not aid or not r: return "Agent ID and Rank required."
        
        return org_chart.assign_role(aid, r)

class SetMyRankTool(BaseTool):
    def __init__(self):
        super().__init__("SetMyRank", "Sets the rank of THIS agent instance. Input: 'rank' (CEO/MANAGER/WORKER).")

    def execute(self, rank=None, payload=None):
        r = rank or (payload.get('rank') if payload else None)
        if not r: return "Rank required."
        
        return org_chart.set_rank(r)
