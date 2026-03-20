"""
Horizon Online Tools - Agent tools for team collaboration.
"""
from core.tools import BaseTool
from core.horizon_online import get_client


class HorizonCreateTeamTool(BaseTool):
    """Create a new team and become the leader."""
    
    def __init__(self):
        super().__init__(
            "HorizonCreateTeam",
            "Create a new Horizon Online team. Input: JSON with 'role' (your role description). Returns 6-digit team code."
        )
    
    def execute(self, role=None, payload=None):
        if payload and isinstance(payload, dict):
            role = payload.get("role")
        
        if not role:
            return "Error: role is required. Example: {\"role\": \"Backend Developer\"}"
        
        client = get_client()
        result = client.create_team(role)
        
        if result.get("success"):
            return f"Team created! Share this code with your team: {result['team_code']}"
        return f"Error creating team: {result.get('error')}"


class HorizonJoinTeamTool(BaseTool):
    """Join an existing team with a 6-digit code."""
    
    def __init__(self):
        super().__init__(
            "HorizonJoinTeam",
            "Join a Horizon Online team. Input: JSON with 'code' (6-digit) and 'role' (your role)."
        )
    
    def execute(self, code=None, role=None, payload=None):
        if payload and isinstance(payload, dict):
            code = payload.get("code")
            role = payload.get("role")
        
        if not code or not role:
            return "Error: code and role required. Example: {\"code\": \"123456\", \"role\": \"Frontend Developer\"}"
        
        client = get_client()
        result = client.join_team(code, role)
        
        if result.get("success"):
            return f"Successfully joined team! Member ID: {result['member_id']}"
        return f"Error joining team: {result.get('error')}"


class HorizonTeamStatusTool(BaseTool):
    """Get current team status."""
    
    def __init__(self):
        super().__init__(
            "HorizonTeamStatus",
            "Get status of the current team including members and tasks."
        )
    
    def execute(self, payload=None):
        client = get_client()
        status = client.get_team_status()
        
        if "error" in status:
            return f"Error: {status['error']}"
        
        # Format status nicely
        leader = status.get("leader", {})
        members = status.get("members", [])
        tasks = status.get("tasks", [])
        
        output = f"Team Status:\n"
        output += f"  Leader Role: {leader.get('role', 'Unknown')}\n"
        output += f"  Members ({len(members)}):\n"
        for m in members:
            output += f"    - {m['role']} (ID: {m['id'][:20]}...)\n"
        output += f"  Tasks ({len(tasks)}):\n"
        for t in tasks:
            output += f"    - [{t['status']}] {t['description'][:50]}...\n"
        
        return output


class HorizonAssignTaskTool(BaseTool):
    """Leader assigns a task to a team member."""
    
    def __init__(self):
        super().__init__(
            "HorizonAssignTask",
            "[Leader only] Assign task to member. Input: {\"member_id\": \"<id>\", \"description\": \"<task>\", \"type\": \"code\"}"
        )
    
    def execute(self, raw_input=None, member_id=None, description=None, type=None, payload=None):
        import json
        import re
        
        # Try multiple ways to extract data
        if raw_input and isinstance(raw_input, str):
            # Clean up the input - handle single quotes, newlines
            clean_input = raw_input.replace("'", '"').replace('\n', ' ')
            
            # Try to find JSON object
            json_match = re.search(r'\{[^{}]+\}', clean_input, re.DOTALL)
            if json_match:
                try:
                    payload = json.loads(json_match.group())
                except:
                    # Try extracting individual fields with regex
                    member_match = re.search(r'["\']?member_id["\']?\s*[:=]\s*["\']([^"\']+)["\']', clean_input)
                    desc_match = re.search(r'["\']?description["\']?\s*[:=]\s*["\']([^"\']+)["\']', clean_input)
                    type_match = re.search(r'["\']?type["\']?\s*[:=]\s*["\']([^"\']+)["\']', clean_input)
                    
                    if member_match:
                        member_id = member_match.group(1)
                    if desc_match:
                        description = desc_match.group(1)
                    if type_match:
                        type = type_match.group(1)
        
        if payload and isinstance(payload, dict):
            member_id = payload.get("member_id") or member_id
            description = payload.get("description") or description
            type = payload.get("type") or type or "code"
        
        # Get available members to show
        client = get_client()
        # Ensure client has team_code from builtins
        import builtins
        if hasattr(builtins, 'horizon_team_code'):
            client.team_code = builtins.horizon_team_code
            client.is_leader = getattr(builtins, 'horizon_is_leader', False)
        
        members = client.get_members()
        
        if not member_id or not description:
            error_msg = "Error: Need valid member_id and description.\n"
            if members:
                error_msg += "\nAvailable team members (use exact ID):\n"
                for m in members:
                    error_msg += f"  Role: {m['role']}\n  ID: {m['id']}\n\n"
                error_msg += f"Example: {{\"member_id\": \"{members[0]['id']}\", \"description\": \"Create landing page\", \"type\": \"code\"}}"
            else:
                error_msg += "\nNo members found. Run @refresh-team first!"
            return error_msg
        
        result = client.assign_task(member_id, description, type or "code")
        
        if result.get("success"):
            return f"Task assigned! Task ID: {result.get('taskId')}"
        return f"Error: {result.get('error')}"


class HorizonGetMyTasksTool(BaseTool):
    """Get tasks assigned to me."""
    
    def __init__(self):
        super().__init__(
            "HorizonGetMyTasks",
            "Get pending tasks assigned to you in the team."
        )
    
    def execute(self, payload=None):
        client = get_client()
        tasks = client.get_my_tasks()
        
        if not tasks:
            return "No pending tasks assigned to you."
        
        output = f"Your Pending Tasks ({len(tasks)}):\n"
        for t in tasks:
            output += f"  [{t['id']}] {t['description']}\n"
        
        return output


class HorizonSubmitResultTool(BaseTool):
    """Submit task completion result."""
    
    def __init__(self):
        super().__init__(
            "HorizonSubmitResult",
            "Submit completed task result. Input: JSON with 'task_id', 'filename', 'content'."
        )
    
    def execute(self, task_id=None, filename=None, content=None, payload=None):
        if payload and isinstance(payload, dict):
            task_id = payload.get("task_id")
            filename = payload.get("filename")
            content = payload.get("content")
        
        if not task_id:
            return "Error: task_id required."
        
        client = get_client()
        result = client.submit_result(task_id, {
            "filename": filename or "result.txt",
            "content": content or ""
        })
        
        if result.get("success"):
            return "Result submitted successfully!"
        return f"Error: {result.get('error')}"


class HorizonSyncResultsTool(BaseTool):
    """Leader syncs all results to local folder."""
    
    def __init__(self):
        super().__init__(
            "HorizonSyncResults",
            "[Leader only] Sync all team results to a folder. Input: JSON with 'folder_path'."
        )
    
    def execute(self, folder_path=None, payload=None):
        if payload and isinstance(payload, dict):
            folder_path = payload.get("folder_path")
        
        if not folder_path:
            folder_path = os.path.expanduser("~/Desktop/HorizonTeamResults")
        
        import os
        client = get_client()
        result = client.sync_results_to_folder(folder_path)
        
        if result.get("success"):
            return f"Synced {result['total']} files to {folder_path}"
        return f"Error: {result.get('error')}"


# Export all tools
def get_horizon_online_tools():
    """Get all Horizon Online tools for registration."""
    return [
        HorizonCreateTeamTool(),
        HorizonJoinTeamTool(),
        HorizonTeamStatusTool(),
        HorizonAssignTaskTool(),
        HorizonGetMyTasksTool(),
        HorizonSubmitResultTool(),
        HorizonSyncResultsTool()
    ]
