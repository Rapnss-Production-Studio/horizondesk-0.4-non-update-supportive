class Conglomerate:
    """
    Parent Company.
    """
    def __init__(self):
        self.tenants = {} # User -> Data
        
    def switch_tenant(self, user_id):
        if user_id not in self.tenants:
            self.tenants[user_id] = {"session": []}
            return f"New Tenant {user_id} Onboarded."
        return f"Switched context to Tenant {user_id}."

conglomerate = Conglomerate()
