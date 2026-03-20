from core.tools import BaseTool
from core.corporation.recruiter import recruiter

class AssessHardwareTool(BaseTool):
    def __init__(self):
        super().__init__("AssessHardware", "Scans the current machine to determine its optimal Rank. Input: None.")

    def execute(self, payload=None):
        specs = recruiter.assess_specs()
        return f"""[The Recruiter] Hardware Assessment:
Cores: {specs['cores']}
RAM: {specs['ram_gb']} GB
OS: {specs['os']}
RECOMMENDED RANK: {specs['recommended_rank']}"""

class GenerateInstallerTool(BaseTool):
    def __init__(self):
        super().__init__("GenerateInstaller", "Creates a deployment script to install the agent on a new machine. Input: 'path'.")

    def execute(self, path="agent_installer.py", payload=None):
        p = path or (payload.get('path') if payload else "agent_installer.py")
        return recruiter.generate_installer(p)
