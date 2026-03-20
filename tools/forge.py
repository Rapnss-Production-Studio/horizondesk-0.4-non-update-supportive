from core.tools import BaseTool
import os
import time
from core.llm import LLMProvider

class ForgeAppTool(BaseTool):
    def __init__(self):
        super().__init__("ForgeApp", "Generates a complete, runnable software application from a description. Input: 'app_name', 'description'.")
        self.llm = LLMProvider()
        home = os.path.expanduser("~")
        self.forge_dir = os.path.join(os.environ.get('USERPROFILE', home), "Desktop", "Horizon_Forge")
        if not os.path.exists(self.forge_dir):
            os.makedirs(self.forge_dir)

    def execute(self, app_name=None, description=None, payload=None):
        name = app_name
        desc = description
        if payload and isinstance(payload, dict):
            name = payload.get('app_name')
            desc = payload.get('description')
            
        if not name or not desc:
            return "Error: app_name and description required."

        # sanitize name
        safe_name = "".join([c for c in name if c.isalnum() or c in (' ', '_', '-')]).strip().replace(" ", "_")
        app_path = os.path.join(self.forge_dir, safe_name)
        
        if os.path.exists(app_path):
            return f"Error: App '{safe_name}' already exists in {self.forge_dir}."
            
        os.makedirs(app_path)
        print(f"[The Forge] Forging '{name}' in {app_path}...")
        
        # 1. Generate Architecture / File Plan
        plan_prompt = f"""You are a CTO. Plan the files needed for a Python application described as: "{desc}".
        Return ONLY a JSON dictionary where keys are filenames and values are specific instructions for that file.
        Include 'main.py' and 'requirements.txt'.
        Example: {{"main.py": "Tkinter GUI code", "requirements.txt": "dependencies"}}
        """
        try:
            plan_str = self.llm.generate_text(plan_prompt, system_prompt="Output only valid JSON.")
            import json
            # Robust parsing attempt
            if "{" in plan_str:
                json_str = plan_str[plan_str.find("{"):plan_str.rfind("}")+1]
                file_plan = json.loads(json_str)
            else:
                # Fallback
                file_plan = {"main.py": f"Complete python code for {desc}", "requirements.txt": "Standard libs"}
        except:
             file_plan = {"main.py": f"Complete python code for {desc}", "requirements.txt": "Standard libs"}
             
        # 2. Generate Files
        results = []
        for filename, instructions in file_plan.items():
            print(f"[The Forge] Writing {filename}...")
            
            code_prompt = f"""You are a Lead Developer. Write the COMPLETE code for '{filename}' for the app '{name}'.
            Description: {desc}
            Specific Config: {instructions}
            
            Return ONLY the code/text content. No markdown formatting if possible, or simple blocks.
            """
            content = self.llm.generate_text(code_prompt)
            
            # Strip markdown
            if "```" in content:
                content = content.replace("```python", "").replace("```text", "").replace("```", "")
            
            full_path = os.path.join(app_path, filename)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content.strip())
            results.append(filename)
            
        return f"App '{name}' Forged Successfully at: {app_path}\nFiles created: {', '.join(results)}"
