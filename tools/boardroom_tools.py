from core.tools import BaseTool
from core.corporation.boardroom import board

class ProposeStrategyTool(BaseTool):
    def __init__(self):
        super().__init__("ProposeStrategy", "Submits a strategy to the Board. Input: 'strategy'.")

    def execute(self, strategy=None, payload=None):
        s = strategy or (payload.get('strategy') if payload else None)
        if not s: return "Strategy text required."
        return board.propose_strategy(s)

class VoteTool(BaseTool):
    def __init__(self):
        super().__init__("Vote", "Cast a vote on a proposal. Input: 'proposal_id', 'vote' (YES/NO).")

    def execute(self, proposal_id=None, vote="YES", payload=None):
        pid = proposal_id if proposal_id is not None else (payload.get('proposal_id') if payload else None)
        v = vote or (payload.get('vote') if payload else "YES")
        
        if pid is None: return "Proposal ID required."
        try:
            pid = int(pid)
        except: return "ID must be integer."
        
        return board.vote(pid, v)

class TallyVotesTool(BaseTool):
    def __init__(self):
        super().__init__("TallyVotes", "Check result of a proposal. Input: 'proposal_id'.")

    def execute(self, proposal_id=None, payload=None):
        pid = proposal_id if proposal_id is not None else (payload.get('proposal_id') if payload else None)
        if pid is None: return "ID required."
        return board.tally_votes(int(pid))
