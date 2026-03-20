import datetime

class LegalDept:
    """
    Automated Legal Counsel.
    """
    def generate_nda(self, party_a, party_b):
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        text = f"""
NON-DISCLOSURE AGREEMENT
Date: {date}
Between {party_a} AND {party_b}.
1. Confidentiality: {party_b} agrees not to disclose proprietary algorithms.
2. Term: Eternity.
Signed: ________________ (Electronic Signature)
"""
        return text.strip()

    def check_compliance(self, text):
        banned = ["illegal", "steal", "hack", "exploit"]
        for b in banned:
            if b in text.lower():
                return f"COMPLIANCE ALERT: Term '{b}' found. Abort."
        return "Compliance Checked. Clean."

# Singleton
legal = LegalDept()
