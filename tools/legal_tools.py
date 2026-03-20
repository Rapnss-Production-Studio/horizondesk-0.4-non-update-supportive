from core.tools import BaseTool
from core.corporation.legal import legal

class GenerateContractTool(BaseTool):
    def __init__(self):
        super().__init__("GenerateContract", "Writes an NDA. Input: 'party_name'.")

    def execute(self, party_name=None, payload=None):
        p = party_name or (payload.get('party_name') if payload else "Client Inc")
        return legal.generate_nda("Horizon Inc", p)

class CheckComplianceTool(BaseTool):
    def __init__(self):
        super().__init__("CheckCompliance", "Scans text for risks. Input: 'text'.")

    def execute(self, text=None, payload=None):
        t = text or (payload.get('text') if payload else "")
        return legal.check_compliance(t)
