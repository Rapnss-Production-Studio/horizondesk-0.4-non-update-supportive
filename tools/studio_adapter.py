from core.tools import BaseTool
import threading
import subprocess
import os
import requests
import time

class LaunchStudioTool(BaseTool):
    def __init__(self):
        super().__init__("LaunchStudio", "Launches the Horizon Presentation Studio web interface. Input: 'port' (default 5000).")

    def execute(self, port=5000, payload=None):
        if payload and isinstance(payload, dict):
            port = payload.get('port', 5000)
            
        try:
            # Check if already running
            try:
                if requests.get(f"http://localhost:{port}/", timeout=1).status_code == 200:
                   return f"Studio is already running at http://localhost:{port}"
            except:
                pass

            # Start Server in Background
            studio_path = os.path.join(os.getcwd(), "studio", "server.py")
            
            if not os.path.exists(studio_path):
                 return f"Error: Studio server not found at {studio_path}"

            # We use Start to launch a new window so the agent doesn't hang
            cmd = f'start cmd /k "python {studio_path}"'
            os.system(cmd)
            
            # Use Browser Tool logic to open it
            time.sleep(2)
            os.system(f"start http://localhost:{port}")
            
            return f"Launched Horizon Studio at http://localhost:{port}"
        except Exception as e:
            return f"Error launching studio: {e}"
