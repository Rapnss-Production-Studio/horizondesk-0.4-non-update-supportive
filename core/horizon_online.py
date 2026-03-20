"""
Horizon Online - Python Client
Multi-agent team collaboration for OmniAgent.
"""
import requests
import json
import os


class HorizonOnlineClient:
    """Client for Horizon Online team collaboration."""
    
    def __init__(self, base_url="https://horizon-online.api-rapnss.workers.dev"):
        """
        Initialize Horizon Online client.
        
        Args:
            base_url: Horizon Online server URL (local dev or production)
        """
        self.base_url = base_url.rstrip("/")
        self.team_code = None
        self.member_id = None
        self.role = None
        self.is_leader = False
    
    def create_team(self, role: str) -> dict:
        """
        Create a new team and become the leader.
        
        Args:
            role: Your role description (e.g., "Backend Developer")
            
        Returns:
            dict with team_code if successful
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/team/create",
                json={"role": role},
                timeout=10
            )
            result = response.json()
            
            if result.get("success"):
                self.team_code = result["teamCode"]
                self.role = role
                self.is_leader = True
                return {
                    "success": True,
                    "team_code": self.team_code,
                    "message": f"Team created! Share code: {self.team_code}"
                }
            return {"success": False, "error": result.get("error", "Unknown error")}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def join_team(self, code: str, role: str) -> dict:
        """
        Join an existing team with a 6-digit code.
        
        Args:
            code: 6-digit team code
            role: Your role description
            
        Returns:
            dict with member_id if successful
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/team/join",
                json={"code": code, "role": role},
                timeout=10
            )
            result = response.json()
            
            if result.get("success"):
                self.team_code = code
                self.member_id = result["memberId"]
                self.role = role
                self.is_leader = False
                return {
                    "success": True,
                    "member_id": self.member_id,
                    "message": f"Joined team {code} as {role}"
                }
            return {"success": False, "error": result.get("error", "Unknown error")}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_team_status(self) -> dict:
        """Get current team status including all members and tasks."""
        if not self.team_code:
            return {"error": "Not in a team"}
        
        try:
            response = requests.get(
                f"{self.base_url}/api/team/{self.team_code}/status",
                timeout=10
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def assign_task(self, member_id: str, description: str, task_type: str = "code") -> dict:
        """
        [Leader only] Assign a task to a team member.
        
        Args:
            member_id: ID of the member to assign to
            description: Task description
            task_type: Type of task (code, design, research, etc.)
        """
        if not self.is_leader:
            return {"error": "Only team leader can assign tasks"}
        
        try:
            response = requests.post(
                f"{self.base_url}/api/task/assign",
                json={
                    "teamCode": self.team_code,
                    "memberId": member_id,
                    "description": description,
                    "type": task_type
                },
                timeout=10
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_my_tasks(self) -> list:
        """Get pending tasks assigned to me."""
        if not self.team_code or not self.member_id:
            return []
        
        try:
            # Use new endpoint format: /api/team/{code}/tasks/{memberId}
            response = requests.get(
                f"{self.base_url}/api/team/{self.team_code}/tasks/{self.member_id}",
                timeout=10
            )
            result = response.json()
            return result.get("tasks", [])
        except Exception as e:
            return []
    
    def get_members(self) -> list:
        """Get all team members. Used by leader's AI to assign tasks."""
        if not self.team_code:
            return []
        
        try:
            response = requests.get(
                f"{self.base_url}/api/team/{self.team_code}/members",
                timeout=10
            )
            result = response.json()
            return result.get("members", [])
        except Exception as e:
            return []
    
    def submit_result(self, task_id: str, result_data: dict) -> dict:
        """
        Submit task completion result.
        
        Args:
            task_id: ID of the completed task
            result_data: Result data (files, content, etc.)
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/task/complete",
                json={
                    "teamCode": self.team_code,
                    "memberId": self.member_id,
                    "taskId": task_id,
                    "resultData": result_data
                },
                timeout=10
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_all_results(self) -> list:
        """[Leader only] Get all submitted results for syncing."""
        if not self.team_code:
            return []
        
        try:
            response = requests.get(
                f"{self.base_url}/api/results/{self.team_code}",
                timeout=10
            )
            result = response.json()
            return result.get("results", [])
        except Exception as e:
            return []
    
    def sync_results_to_folder(self, folder_path: str) -> dict:
        """
        [Leader only] Sync all results to a local folder.
        
        Args:
            folder_path: Path to sync results to
        """
        if not self.is_leader:
            return {"error": "Only leader can sync results"}
        
        results = self.get_all_results()
        synced_files = []
        
        os.makedirs(folder_path, exist_ok=True)
        
        for result in results:
            data = result.get("data", {})
            if "filename" in data and "content" in data:
                file_path = os.path.join(folder_path, data["filename"])
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(data["content"])
                synced_files.append(file_path)
        
        return {
            "success": True,
            "synced_files": synced_files,
            "total": len(synced_files)
        }


# Global client instance
_client = None

def get_client(base_url="https://horizon-online.api-rapnss.workers.dev") -> HorizonOnlineClient:
    """Get or create the global Horizon Online client."""
    global _client
    if _client is None:
        _client = HorizonOnlineClient(base_url)
    return _client
