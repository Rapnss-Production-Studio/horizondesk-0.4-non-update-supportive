import os
import time
from core.holodeck.anchor import anchor

class VirtualFileSystem:
    def __init__(self):
        self.tree = {} # Path -> Type (FILE/DIR)
        
    def mirror_real_directory(self, path):
        """Scans real disk and builds a phantom tree."""
        for root, dirs, files in os.walk(path):
            self.tree[root] = "DIR"
            for d in dirs:
                self.tree[os.path.join(root, d)] = "DIR"
            for f in files:
                self.tree[os.path.join(root, f)] = "FILE"

    def exists(self, path):
        return path in self.tree

    def delete(self, path):
        if path in self.tree:
            # Determine impact
            is_dir = self.tree[path] == "DIR"
            del self.tree[path]
            # If dir, rudimentary feedback (doesn't recursively delete in this lightweight VFS for speed, but concept stands)
            return True, "Directory Removed" if is_dir else "File Removed"
        return False, "Not Found"

    def create(self, path, is_dir=False):
        self.tree[path] = "DIR" if is_dir else "FILE"
        return True

class HolodeckEngine:
    def __init__(self):
        self.vfs = VirtualFileSystem()
        self.active_simulation = False
        self.simulation_log = []
        
    def initialize_simulation(self, target_path):
        """Boot up the Holodeck."""
        if not anchor.verify_anchor():
             return "Error: Reality Collapse."
             
        self.vfs.tree = {} # Reset
        self.vfs.mirror_real_directory(target_path)
        self.active_simulation = True
        self.simulation_log = []
        
        # Calculate Initial Entropy (Total Nodes)
        self.initial_nodes = len(self.vfs.tree)
        return f"Holodeck Initialized. Mirrored {self.initial_nodes} entities from {target_path}."

    def simulate_command(self, action, target):
        """
        Run a command in the simulation.
        Action: 'delete', 'create_file', 'create_dir'
        """
        if not self.active_simulation:
            return "Error: No simulation running. Initialize first."
            
        success = False
        msg = ""
        
        if action == "delete":
            success, msg = self.vfs.delete(target)
        elif action == "create_file":
            success = self.vfs.create(target, is_dir=False)
            msg = "File Created"
        elif action == "create_dir":
            success = self.vfs.create(target, is_dir=True)
            msg = "Dir Created"
            
        if success:
            self.simulation_log.append(f"{action} -> {target}")
            
        return f"[SIMULATION] {msg}"

    def calculate_chaos(self):
        """
        Returns the Chaos Metric (0.0 - 1.0).
        How much has the state changed?
        """
        current_nodes = len(self.vfs.tree)
        diff = abs(current_nodes - self.initial_nodes)
        if self.initial_nodes == 0: return 0.0
        return min(1.0, diff / self.initial_nodes)

    def shutdown(self):
        """Securely wipe the simulation."""
        self.vfs.tree = {}
        self.active_simulation = False
        return "Holodeck Purged."

# Singleton
holodeck = HolodeckEngine()
