import datetime
from core.corporation.hierarchy import org_chart, Rank

class Proposal:
    def __init__(self, author_id, strategy_text):
        self.author_id = author_id
        self.strategy = strategy_text
        self.votes = {"YES": 0, "NO": 0}
        self.status = "PENDING"
        self.timestamp = datetime.datetime.now()

class Boardroom:
    """
    The Consensus Engine.
    Allows the Swarm to vote on strategic decisions.
    """
    def __init__(self):
        self.proposals = []
        
    def propose_strategy(self, strategy_text):
        """
        Submit a new strategy for the board to review.
        """
        p = Proposal(org_chart.master_signature, strategy_text) # Simplified: "Owner" proposes
        self.proposals.append(p)
        return f"Proposal '{strategy_text}' docketed. ID: {len(self.proposals)-1}"

    def vote(self, proposal_id, vote="YES"):
        """
        Cast a vote. Weighted by Rank.
        """
        if proposal_id >= len(self.proposals):
            return "Invalid Proposal ID."
            
        p = self.proposals[proposal_id]
        if p.status != "PENDING":
            return f"Proposal is already {p.status}."
            
        # Calculate Weight
        weight = 1
        if org_chart.my_rank == Rank.CEO: weight = 10
        elif org_chart.my_rank == Rank.MANAGER: weight = 5
        
        if vote.upper() == "YES":
            p.votes["YES"] += weight
        else:
            p.votes["NO"] += weight
            
        return f"Vote Cast ({vote}) with weight {weight}."

    def tally_votes(self, proposal_id):
        if proposal_id >= len(self.proposals): return "Invalid ID."
        p = self.proposals[proposal_id]
        
        total = p.votes["YES"] + p.votes["NO"]
        if total == 0: return "No votes yet."
        
        # Simple Majority
        if p.votes["YES"] > p.votes["NO"]:
            p.status = "APPROVED"
        else:
            p.status = "REJECTED"
            
        return f"Proposal {p.status}. YES: {p.votes['YES']}, NO: {p.votes['NO']}"

# Singleton
board = Boardroom()
