import hashlib
import time
import uuid

class Treasury:
    """
    Manages the Corporation's Wealth.
    Generates Invoices and tracks Crypto Balances.
    """
    def __init__(self):
        self.balance = 0.0 # USD simulation
        self.wallet_address = self._generate_wallet()
        self.ledger = []
        
    def _generate_wallet(self):
        # Simulation of an ETH address generation
        pk = uuid.uuid4().hex
        public = hashlib.sha256(pk.encode()).hexdigest()
        return f"0x{public[:40]}"

    def create_invoice(self, client, amount, service):
        inv_id = f"INV-{len(self.ledger)+1:04d}"
        entry = {
            "id": inv_id,
            "client": client,
            "amount": amount,
            "service": service,
            "status": "SENT",
            "timestamp": time.time()
        }
        self.ledger.append(entry)
        # Verify Payment logic would be here
        return f"Invoice {inv_id} sent to {client} for ${amount}."

    def receive_funds(self, amount):
        self.balance += amount
        return f"Received ${amount}. New Balance: ${self.balance:.2f}"

# Singleton
treasury = Treasury()
