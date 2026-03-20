from core.tools import BaseTool
from core.corporation.ipo import ipo

class SyncGlobalStateTool(BaseTool):
    def __init__(self):
        super().__init__("SyncGlobalState", "Backs up corporate data. Input: 'data_dict'.")

    def execute(self, data_dict=None, payload=None):
        d = data_dict or (payload.get('data_dict') if payload else {"status": "ok"})
        return ipo.sync_global_state(d)

class ScaleFleetTool(BaseTool):
    def __init__(self):
        super().__init__("ScaleFleet", "Adds compute nodes. Input: 'count'.")

    def execute(self, count=None, payload=None):
        c = count or (payload.get('count') if payload else 1)
        return ipo.scale_nodes(int(c))
