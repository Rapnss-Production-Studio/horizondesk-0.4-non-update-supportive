import time
import uuid

class ProjectManager:
    """
    Autonomous Jira.
    Manages Tasks (Tickets) across the Swarm.
    """
    def __init__(self):
        self.tickets = {} # ID -> {details}
        
    def create_ticket(self, title, description, priority="MEDIUM"):
        tid = str(uuid.uuid4())[:8]
        self.tickets[tid] = {
            "title": title,
            "desc": description,
            "priority": priority,
            "status": "TODO",
            "assignee": None,
            "created_at": time.time()
        }
        return f"Ticket created: [{tid}] {title}"

    def assign_ticket(self, ticket_id, agent_id):
        if ticket_id not in self.tickets: return "Ticket not found."
        self.tickets[ticket_id]["assignee"] = agent_id
        self.tickets[ticket_id]["status"] = "IN_PROGRESS"
        return f"Ticket [{ticket_id}] assigned to Agent {agent_id}"

    def complete_ticket(self, ticket_id):
        if ticket_id not in self.tickets: return "Ticket not found."
        self.tickets[ticket_id]["status"] = "DONE"
        return f"Ticket [{ticket_id}] marked CLOSED."

    def get_status(self):
        todo = len([t for t in self.tickets.values() if t['status']=='TODO'])
        wip = len([t for t in self.tickets.values() if t['status']=='IN_PROGRESS'])
        done = len([t for t in self.tickets.values() if t['status']=='DONE'])
        return f"Status: {todo} TODO, {wip} IN PROGRESS, {done} COMPOLETED."

# Singleton
pm = ProjectManager()
