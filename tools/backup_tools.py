from core.tools import BaseTool
from core.corporation.backup import backup_system

class BackupStateTool(BaseTool):
    def __init__(self):
        super().__init__("BackupState", "Freezes system state to archive. Input: None.")
    def execute(self, payload=None):
        return backup_system.create_backup()
