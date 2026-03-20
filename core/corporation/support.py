class SupportDesk:
    """
    Automated Customer Service.
    """
    def __init__(self):
        self.kb = {
            "password": "To reset password, click 'Forgot Password' on login.",
            "refund": "Refunds are processed within 14 days of purchase.",
            "api": "Documentation is available at /docs/api."
        }
        
    def query_kb(self, user_query):
        q = user_query.lower()
        # Simple fuzzy match
        for key, answer in self.kb.items():
            if key in q:
                return f"Auto-Reply: {answer}"
                
        return "Escalated to Human Agent (No KB match)."

# Singleton
support = SupportDesk()
