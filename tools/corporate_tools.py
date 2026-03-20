from core.tools import BaseTool
from core.corporation.mesh import mesh

class ConnectMeshTool(BaseTool):
    def __init__(self):
        super().__init__("ConnectMesh", "Activates P2P Discovery to find other Agents. Input: None.")

    def execute(self, payload=None):
        msg = mesh.start_discovery()
        return f"[The Corporation] {msg}\nSearching for peers on port 58440..."

class ListPeersTool(BaseTool):
    def __init__(self):
        super().__init__("ListPeers", "Lists all discovered Agents on the network. Input: None.")

    def execute(self, payload=None):
        peers = mesh.list_peers()
        if not peers: return "[The Corporation] No peers found yet."
        return f"[The Corporation] Active Peers:\n{peers}"
