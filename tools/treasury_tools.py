from core.tools import BaseTool
from core.corporation.treasury import treasury

class CheckBalanceTool(BaseTool):
    def __init__(self):
        super().__init__("CheckBalance", "Checks corporate funds. Input: None.")

    def execute(self, payload=None):
        return f"[The Treasury] Balance: ${treasury.balance:.2f} | Wallet: {treasury.wallet_address}"

class CreateInvoiceTool(BaseTool):
    def __init__(self):
        super().__init__("CreateInvoice", "Bills a client. Input: 'client', 'amount'.")

    def execute(self, client=None, amount=None, payload=None):
        c = client or (payload.get('client') if payload else None)
        a = amount or (payload.get('amount') if payload else 0)
        
        if not c: return "Client name required."
        return treasury.create_invoice(c, float(a), "Consulting")
