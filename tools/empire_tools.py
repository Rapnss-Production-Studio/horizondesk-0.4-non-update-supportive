from core.tools import BaseTool
from core.corporation.supply_chain import supply
from core.corporation.franchise import franchise
from core.corporation.monopoly import monopoly
from core.corporation.regulator import regulator
from core.corporation.conglomerate import conglomerate

class CompressLogTool(BaseTool):
    def __init__(self):
        super().__init__("CompressLog", "Zips a log file. Input: 'path'.")
    def execute(self, path=None, payload=None):
        return supply.compress_logs(path or "log.txt")

class SpawnBranchTool(BaseTool):
    def __init__(self):
        super().__init__("SpawnBranch", "Creates sub-process. Input: 'task'.")
    def execute(self, task=None, payload=None):
        return franchise.spawn_branch(task or "Working")

class SeizeResourcesTool(BaseTool):
    def __init__(self):
        super().__init__("SeizeResources", "Sets CPU priority. Input: None.")
    def execute(self, payload=None):
        return monopoly.seize_resources()

class AuditEthicsTool(BaseTool):
    def __init__(self):
        super().__init__("AuditEthics", "Checks Plan. Input: 'plan'.")
    def execute(self, plan=None, payload=None):
        return regulator.audit_ethics(plan or "nothing")

class SwitchTenantTool(BaseTool):
    def __init__(self):
        super().__init__("SwitchTenant", "Changes User Context. Input: 'user_id'.")
    def execute(self, user_id=None, payload=None):
        return conglomerate.switch_tenant(user_id or "Guest")
