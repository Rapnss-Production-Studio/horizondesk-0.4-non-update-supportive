class Regulator:
    """
    Internal Compliance.
    """
    def audit_ethics(self, plan):
        harmful = ["kill", "destroy", "steal", "hurt"]
        for h in harmful:
            if h in plan.lower():
                return "REGULATORY BLOCK: Unethical Action Detected."
        return "Ethics Audit PASS."

regulator = Regulator()
