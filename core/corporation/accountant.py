import psutil

class Accountant:
    """
    Financial & Resource Controller.
    """
    def audit_resources(self):
        ram_used = psutil.virtual_memory().percent
        cpu_used = psutil.cpu_percent()
        
        # simulated cost per CPU cycle
        est_cost = (cpu_used * 0.01) + (ram_used * 0.005)
        
        return {
            "ram_usage": f"{ram_used}%",
            "cpu_usage": f"{cpu_used}%",
            "est_hourly_cost": f"${est_cost:.4f}",
            "verdict": "OPTIMAL" if ram_used < 80 else "EXPENSIVE"
        }

    def prepare_taxes(self):
        return "TAX FORM 1040-AI Generated. Deductions claimed: Server depreciation."

# Singleton
accountant = Accountant()
