from core.tools import BaseTool
from core.corporation.watchtower import watchtower

class ScanSecurityTool(BaseTool):
    def __init__(self):
        super().__init__("ScanSecurity", "Checks system integrity. Input: None.")

    def execute(self, payload=None):
        return watchtower.scan_network_integrity()
