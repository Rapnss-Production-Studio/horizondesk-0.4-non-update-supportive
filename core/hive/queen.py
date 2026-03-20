import threading
import hashlib
import time
from concurrent.futures import ThreadPoolExecutor
from core.hive.drone import HiveDrone
from core.security.neuro_crypt import shield

class HiveQueen:
    """
    The Sovereign. Controls the Botnet.
    """
    def __init__(self):
        shield.check_integrity()
        self.encryption_key = shield._fingerprint # Use HWID as private key
        self.drones = []
        self.pool = ThreadPoolExecutor(max_workers=50) # Simulate scale
        
    def spawn_swarm(self, count=100):
        """Hatch new drones."""
        print(f"[Queen] Spawning {count} polymorphic drones...")
        self.drones = [HiveDrone(self.encryption_key) for _ in range(count)]
        return len(self.drones)

    def sign_command(self, command):
        return hashlib.sha256((command + self.encryption_key).encode()).hexdigest()

    def distributed_task(self, task_type, data_list):
        """
        MapReduce: Split data amongst drones.
        """
        if not self.drones:
            return "Error: No swarm active."

        # 1. Consensus Check (Safety)
        # Verify 5% of drones are responsive and secure
        sample = self.drones[:int(len(self.drones)*0.05) + 1]
        for d in sample:
            if not d.verify_command("PING", self.sign_command("PING")):
                return "CRITICAL: Swarm Compromised. Integrity Check Failed."
                
        # 2. Distribute
        results = []
        futures = []
        
        # Simple round-robin distribution
        drone_idx = 0
        sig = self.sign_command(task_type)
        
        start = time.time()
        for item in data_list:
            d = self.drones[drone_idx % len(self.drones)]
            # Async execution
            futures.append(self.pool.submit(d.execute, f"{task_type}::{item}", sig))
            drone_idx += 1
            
        # 3. Gather
        for f in futures:
            res = f.result()
            if res: results.append(res)
            
        elapsed = time.time() - start
        return f"Swarm finished {len(data_list)} items in {elapsed:.2f}s using {len(self.drones)} drones."

# Singleton
queen = HiveQueen()
