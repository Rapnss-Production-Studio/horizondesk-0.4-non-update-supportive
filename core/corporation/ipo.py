import json
import time

class IPO:
    """
    Global Operations.
    """
    def __init__(self):
        self.nodes = 1
        self.last_sync = 0
        
    def scale_nodes(self, count):
        self.nodes += count
        return f"Spinning up {count} new virtual nodes. Total Fleet: {self.nodes}"

    def sync_global_state(self, corp_data):
        """
        Pushes local state to the Global Ledger.
        """
        # In reality, this pushes to a Redis/postgres cluster.
        dump_file = "global_state_snapshot.json"
        
        state = {
            "timestamp": time.time(),
            "nodes_active": self.nodes,
            "data": corp_data
        }
        
        with open(dump_file, "w") as f:
            json.dump(state, f, indent=2)
            
        self.last_sync = time.time()
        return f"Global State Synced to {dump_file}. Timestamp: {self.last_sync}"

# Singleton
ipo = IPO()
