from core.tools import BaseTool
from core.corporation.devops import devops

class RunPipelineTool(BaseTool):
    def __init__(self):
        super().__init__("RunPipeline", "Runs CI/CD tests. Input: None.")

    def execute(self, payload=None):
        return devops.run_tests()

class DeployTool(BaseTool):
    def __init__(self):
        super().__init__("Deploy", "Deploys code to a server. Input: 'ip'.")

    def execute(self, ip=None, payload=None):
        i = ip or (payload.get('ip') if payload else "192.168.1.100")
        return devops.deploy_to_cloud(i)
