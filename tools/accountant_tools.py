from core.tools import BaseTool
from core.corporation.accountant import accountant

class AuditResourcesTool(BaseTool):
    def __init__(self):
        super().__init__("AuditResources", "Checks operating costs. Input: None.")

    def execute(self, payload=None):
        return accountant.audit_resources()
