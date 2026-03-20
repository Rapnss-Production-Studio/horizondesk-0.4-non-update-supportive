from enum import Enum
from core.security.neuro_crypt import shield

class Rank(Enum):
    MASTER = 999  # The User (Absolute)
    CEO = 100     # Main Agent Node
    MANAGER = 50  # Department Head
    WORKER = 10   # Standard Node
    DRONE = 1     # Hive Micro-Agent

class CorporateHierarchy:
    """
    Manages the Org Chart.
    Enforces 'Master Priority Protocol': The Master's command overrides all.
    """
    def __init__(self):
        shield.check_integrity()
        self.my_rank = Rank.CEO # Default to CEO of this local instance
        self.master_signature = shield._fingerprint # In reality, this would be the User's Private Key
        self.team = {} # ID -> Rank
        
    def set_rank(self, rank_name):
        try:
            self.my_rank = Rank[rank_name.upper()]
            return f"Rank updated to {self.my_rank.name}"
        except:
            return "Invalid Rank."

    def assign_role(self, agent_id, rank_name):
        try:
            r = Rank[rank_name.upper()]
            self.team[agent_id] = r
            return f"Promoted agent {agent_id[:6]} to {r.name}"
        except:
            return "Invalid Rank."

    def validate_order(self, issuer_id, issuer_rank, command):
        """
        Decides if we obey an order.
        """
        # 1. Master Priority Protocol
        if issuer_id == self.master_signature:
            return True, "MASTER OVERRIDE: Executing immediately."
            
        # 2. Chain of Command
        # If I am the CEO, I don't listen to Workers.
        # If I am a Worker, I listen to Managers.
        if issuer_rank.value > self.my_rank.value:
            return True, f"Obeying superior {issuer_rank.name}."
            
        return False, f"Insubordination. I am {self.my_rank.name}, you are {issuer_rank.name}."

# Singleton
org_chart = CorporateHierarchy()
