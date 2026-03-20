from core.tools import BaseTool
from core.hive.queen import queen

class DeploySwarmTool(BaseTool):
    def __init__(self):
        super().__init__("DeploySwarm", "Spawns a Hive of micro-agents. Input: 'count' (default 100).")

    def execute(self, count=100, payload=None):
        c = int(count) if count else (int(payload.get('count')) if payload and payload.get('count') else 100)
        
        num = queen.spawn_swarm(c)
        return f"[Hive Sovereign] Swarm Active. {num} Drones on standby. Awaiting orders."

class SwarmTaskTool(BaseTool):
    def __init__(self):
        super().__init__("SwarmTask", "Distributes a task across the swarm. Input: 'task_type', 'data' (comma separated list).")

    def execute(self, task_type=None, data=None, payload=None):
        tt = task_type or (payload.get('task_type') if payload else None)
        d = data or (payload.get('data') if payload else None)
        
        if not tt or not d: return "Task Type and Data required."
        
        # Parse data
        if "," in d:
             items = [x.strip() for x in d.split(",")]
        else:
             items = d.split()
             
        res = queen.distributed_task(tt, items)
        return f"[Hive Sovereign] Result:\n{res}"
