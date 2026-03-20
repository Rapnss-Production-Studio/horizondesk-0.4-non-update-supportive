from core.tools import BaseTool
from core.corporation.sales import sales

class GenerateLeadsTool(BaseTool):
    def __init__(self):
        super().__init__("GenerateLeads", "Finds potential clients. Input: 'industry'.")

    def execute(self, industry=None, payload=None):
        i = industry or (payload.get('industry') if payload else "tech")
        leads = sales.find_leads(i)
        return f"[The Sales Rep] Found Leads: {leads}"

class SendColdEmailTool(BaseTool):
    def __init__(self):
        super().__init__("SendColdEmail", "Sends a pitch. Input: 'email'.")

    def execute(self, email=None, payload=None):
        e = email or (payload.get('email') if payload else None)
        if not e: return "Email required."
        return sales.send_cold_email(e)
