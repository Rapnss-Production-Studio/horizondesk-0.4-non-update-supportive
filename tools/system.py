import subprocess
from core.tools import BaseTool

class RunCommandTool(BaseTool):
    def __init__(self):
        super().__init__("RunCommand", "Executes a shell command. Input: JSON 'command' (e.g., 'pip install package'). Use carefully.")

    def execute(self, command=None, payload=None):
        cmd = command
        if payload and isinstance(payload, dict):
            cmd = payload.get('command')
        elif payload:
             cmd = payload
             
        if not cmd:
            return "Error: No command provided."
            
        try:
            # Run command and capture output
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
            output = result.stdout + "\n" + result.stderr
            return f"Command executed.\nOutput:\n{output[:2000]}" # Truncate log
        except Exception as e:
            return f"Error running command: {e}"
