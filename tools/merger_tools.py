from core.tools import BaseTool
from core.corporation.merger import merger

class BridgeApiTool(BaseTool):
    def __init__(self):
        super().__init__("BridgeApi", "Connects an external API. Input: 'name', 'url', 'endpoint'.")

    def execute(self, name=None, url=None, endpoint=None, payload=None):
        n = name or (payload.get('name') if payload else "ExternalService")
        u = url or (payload.get('url') if payload else None)
        e = endpoint or (payload.get('endpoint') if payload else "")
        
        if not u: return "Base URL required."
        
        return merger.bridge_api(n, u, e)
