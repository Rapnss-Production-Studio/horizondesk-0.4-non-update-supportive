import subprocess
import sys
from core.agent import AgentTool

class RunPythonTool(AgentTool):
    def __init__(self):
        super().__init__(
            name="run_python",
            description="Executes a Python script or code snippet.",
            parameters={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "The Python code to execute."
                    },
                    "file_path": {
                        "type": "string",
                        "description": "Path to a Python file to execute."
                    }
                }
            }
        )

    def execute(self, **kwargs):
        code = kwargs.get('code')
        file_path = kwargs.get('file_path')

        if file_path:
            try:
                result = subprocess.run(
                    [sys.executable, file_path],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            except Exception as e:
                return f"Error executing file: {e}"
        
        if code:
            try:
                # Execute code snippet in a separate process for safety/isolation
                # Or just exec() if sufficient trust. For now, let's use subprocess with -c
                result = subprocess.run(
                    [sys.executable, "-c", code],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            except Exception as e:
                return f"Error executing code: {e}"

        return "Error: No code or file_path provided."
