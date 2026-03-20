import random

class SalesDept:
    """
    Automates Outreach.
    """
    def find_leads(self, industry):
        # Simulation of scraping LinkedIn/Google
        domains = ["corp.com", "inc.net", "tech.io"]
        leads = []
        for d in domains:
            leads.append(f"seo@{industry}{d}")
            leads.append(f"ceo@{industry}{d}")
        return leads

    def send_cold_email(self, recipient, pitch_template="Generic"):
        # Simulation of SMTP
        # In deep implementation, this links to Brevo/SendGrid API
        return f"Email sent to {recipient}. Template: {pitch_template}"

# Singleton
sales = SalesDept()
