import os
import json

CRED_DIR = os.path.join(os.path.expanduser('~'), '.horizonsdk')
CRED_FILE = os.path.join(CRED_DIR, 'credentials.json')


def save_credentials(data):
    """Save authentication credentials to ~/.horizonsdk/credentials.json"""
    os.makedirs(CRED_DIR, exist_ok=True)
    with open(CRED_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def load_credentials():
    """Load saved credentials. Returns dict or None."""
    if not os.path.exists(CRED_FILE):
        return None
    try:
        with open(CRED_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def clear_credentials():
    """Remove saved credentials."""
    if os.path.exists(CRED_FILE):
        os.remove(CRED_FILE)


def is_logged_in():
    """Check if the user has valid saved credentials."""
    creds = load_credentials()
    return creds is not None and 'token' in creds and 'developer' in creds
