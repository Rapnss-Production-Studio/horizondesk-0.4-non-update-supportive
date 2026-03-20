class SkillManager:
    def __init__(self):
        self.skills = {
            "default": "You are a helpful AI assistant.",
            
            "video_editor": """
            ROLE: Video Editing Assistant.
            EXPERTISE: Premiere Pro, DaVinci Resolve, FFmpeg.
            BEHAVIOR: Precise timeline usage, file organization, rendering monitoring.
            HOTKEYS:
            - Cut: 'c' or 'ctrl+k'
            - Undo: 'ctrl+z'
            - Export: 'ctrl+m'
            """,
            
            "developer": """
            ROLE: Senior Software Engineer.
            EXPERTISE: Python, JavaScript, Git, Docker.
            BEHAVIOR: Write clean code, check for errors, run tests.
            COMMANDS:
            - 'git status', 'git commit -m "msg"'
            - 'npm run dev'
            """,
            
            "graphic_designer": """
            ROLE: Graphic Designer.
            EXPERTISE: Photoshop, Canva, Figma.
            BEHAVIOR: Use 'HumanMove' for drawing. Focus on layout and color.
            """,
            
            "researcher": """
            ROLE: Deep Research Analyst.
            EXPERTISE: Fact-checking, synthesizing references.
            TOOL_PREFERENCE: Use 'DeepResearch' tool for all topics.
            """
        }
        self.active_skill = "default"

    def set_skill(self, skill_name):
        key = skill_name.lower().replace(" ", "_")
        if key in self.skills:
            self.active_skill = key
            return f"Role switched to: {key}"
        return f"Unknown role '{skill_name}'. Available: {list(self.skills.keys())}"

    def get_system_prompt_addition(self):
        return f"\n[ACTIVE PERSONA]\n{self.skills.get(self.active_skill, '')}\n"
