from core.tools import BaseTool
from core.corporation.project_manager import pm

class CreateTicketTool(BaseTool):
    def __init__(self):
        super().__init__("CreateTicket", "Creates a new task ticket. Input: 'title', 'description'.")

    def execute(self, title=None, description=None, payload=None):
        t = title or (payload.get('title') if payload else None)
        d = description or (payload.get('description') if payload else "No desc")
        if not t: return "Title required."
        return pm.create_ticket(t, d)

class AssignTicketTool(BaseTool):
    def __init__(self):
        super().__init__("AssignTicket", "Assigns a ticket to an agent. Input: 'ticket_id', 'agent_id'.")

    def execute(self, ticket_id=None, agent_id=None, payload=None):
        tid = ticket_id or (payload.get('ticket_id') if payload else None)
        aid = agent_id or (payload.get('agent_id') if payload else None)
        if not tid or not aid: return "IDs required."
        return pm.assign_ticket(tid, aid)

class CheckProjectStatusTool(BaseTool):
    def __init__(self):
        super().__init__("CheckProjectStatus", "Reports on ticket progress. Input: None.")

    def execute(self, payload=None):
        return pm.get_status()
