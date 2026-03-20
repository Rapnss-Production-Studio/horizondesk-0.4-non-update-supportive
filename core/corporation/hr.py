import random

class HRDepartment:
    """
    Manages the 'Human' Resources (Agents).
    Maximizes Efficiency.
    """
    def __init__(self):
        self.files = {} # AgentID -> {History}
        
    def log_performance(self, agent_id, metric, value):
        if agent_id not in self.files:
            self.files[agent_id] = {"tasks_done": 0, "errors": 0}
            
        if metric == "task_complete":
            self.files[agent_id]["tasks_done"] += 1
        elif metric == "error":
            self.files[agent_id]["errors"] += 1
            
        return "Noted."

    def evaluate_agent(self, agent_id):
        if agent_id not in self.files: return "No data."
        
        data = self.files[agent_id]
        score = (data["tasks_done"] * 10) - (data["errors"] * 5)
        
        verdict = "RETAIN"
        if score < 0: verdict = "TERMINATE"
        elif score > 50: verdict = "PROMOTE"
        
        return {
            "score": score,
            "verdict": verdict,
            "details": data
        }

    def fire_agent(self, agent_id):
        details = self.evaluate_agent(agent_id)
        if isinstance(details, dict) and details['verdict'] == "TERMINATE":
            # In a real distributed system, this would send a KILL signal to the node.
            # Here we simulate the process.
            del self.files[agent_id]
            return f"Agent {agent_id} has been TERMINATED for poor performance."
        return "Termination denied. Insufficient grounds."

# Singleton
hr = HRDepartment()
