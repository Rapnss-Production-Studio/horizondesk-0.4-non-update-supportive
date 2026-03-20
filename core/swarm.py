import threading
import time
import uuid
from core.agent import Agent
from colorama import Fore

# Global Job Store
JOBS = {}

class SwarmManager:
    def __init__(self):
        self.max_workers = 3
        self.active_workers = 0

    def start_worker(self, task_description):
        """Spawns a background thread with a dedicated Agent."""
        if self.active_workers >= self.max_workers:
            return "Error: Max swarm workers (3) reached. Wait for tasks to finish."

        job_id = str(uuid.uuid4())[:8]
        JOBS[job_id] = {"status": "running", "task": task_description, "result": None, "logs": []}
        
        thread = threading.Thread(target=self._worker_routine, args=(job_id, task_description))
        thread.daemon = True
        thread.start()
        self.active_workers += 1
        
        return f"Swarm Agent Spawned. Job ID: {job_id}"

    def _worker_routine(self, job_id, task):
        try:
            # Create a lightweight agent specific for this thread
            # We import specific tools that are safe for background use (e.g., Research, File, but maybe not Voice/Mouse to avoid conflicts)
            from tools.web import SearchWebTool, DownloadPageTool
            from tools.research import DeepResearchTool
            from tools.filesystem import ReadFileTool, WriteFileTool
            
            # Initialize a fresh agent
            # Note: We need to avoid registering conflicting UI tools if possible, or coordinate them.
            # For this version, we give them research capabilities mostly.
            worker_agent = Agent()
            worker_agent.register_tool(SearchWebTool())
            worker_agent.register_tool(DownloadPageTool())
            worker_agent.register_tool(DeepResearchTool())
            worker_agent.register_tool(ReadFileTool())
            worker_agent.register_tool(WriteFileTool())
            
            # Run the agent
            # We need a way to run it autonomously. 
            # We'll inject a "System Directive" that it's a worker.
            
            # Simple One-Shot for now, or a loop? 
            # Let's try running it as a single complex prompt.
            result = worker_agent.run(f"SWARM_WORKER_MODE: You are a background worker. Complete this task entirely and return the final result: {task}")
            
            JOBS[job_id]["status"] = "completed"
            JOBS[job_id]["result"] = result
            
        except Exception as e:
            JOBS[job_id]["status"] = "failed"
            JOBS[job_id]["result"] = str(e)
            print(Fore.RED + f"[Swarm Error {job_id}]: {e}")
        finally:
            self.active_workers -= 1

    def get_status(self, job_id=None):
        if job_id:
            return JOBS.get(job_id, {"status": "unknown"})
        return JOBS
