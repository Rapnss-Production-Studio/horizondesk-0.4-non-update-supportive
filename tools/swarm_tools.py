from core.tools import BaseTool
from core.swarm import SwarmManager

manager = SwarmManager()

class SpawnAgentTool(BaseTool):
    def __init__(self):
        super().__init__("SpawnSwarmAgent", "Spawns a background agent to perform a task asynchronously. Input: 'task'. Returns Job ID.")

    def execute(self, task=None, payload=None):
        t = task
        if payload and isinstance(payload, dict):
            t = payload.get('task')
        elif payload:
            t = payload
            
        if not t: return "Error: Task description required."
        
        return manager.start_worker(t)

class SwarmStatusTool(BaseTool):
    def __init__(self):
        super().__init__("SwarmStatus", "Checks the status of background jobs. Input: 'job_id' (optional, if empty lists all).")

    def execute(self, job_id=None, payload=None):
        jid = job_id
        if payload and isinstance(payload, dict):
             jid = payload.get('job_id')
        elif payload:
             jid = payload
             
        status = manager.get_status(jid)
        return str(status)
