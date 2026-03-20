import os

class SecretStorage:
    """
    Secure access to user-defined secrets.
    Prevents direct .env manipulation by plugin developers.
    """
    @staticmethod
    def get_secret(key):
        """
        Retrieves a secret from the environment.
        In production, this can be bridged to a secure vault or encrypted storage.
        """
        # In this implementation, we read from env vars which are loaded by OmniAgent
        # Developers should use this rather than os.getenv for future-proofing
        return os.getenv(key)

    @staticmethod
    def redact_pii(text):
        """
        Basic helper to redact potential PII (emails, IPs) before sending to external workers.
        """
        import re
        # Redact emails
        text = re.sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', '[REDACTED_EMAIL]', text)
        # Redact IPs
        text = re.sub(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', '[REDACTED_IP]', text)
        return text
