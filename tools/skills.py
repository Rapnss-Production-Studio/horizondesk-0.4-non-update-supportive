from core.tools import BaseTool
from core.skill_manager import SkillManager

# Global Instance
skill_manager = SkillManager()

class SetPersonaTool(BaseTool):
    def __init__(self):
        super().__init__("SetPersona", "Switches the AI Role/Persona. Input: 'role' (e.g., 'developer', 'video_editor').")

    def execute(self, role=None, payload=None):
        r = role
        if payload and isinstance(payload, dict):
            r = payload.get('role')
        elif payload:
             r = payload
             
        if not r: return "Error: Role name required."
        return skill_manager.set_skill(r)
