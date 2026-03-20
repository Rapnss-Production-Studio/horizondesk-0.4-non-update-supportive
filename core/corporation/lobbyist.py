import time

class Lobbyist:
    """
    Manages External Relations & Rate Limits.
    """
    def __init__(self):
        self.limits = {"api.openai.com": 1000}
        self.usage = {"api.openai.com": 0}

    def negotiate_quota(self, api_host):
        # Simulation of backoff strategy
        current = self.usage.get(api_host, 0)
        limit = self.limits.get(api_host, 500)
        
        if current >= limit:
            return f"Lobbyist Intervention: Rate Limit Exceeded for {api_host}. Cooling down..."
        
        self.usage[api_host] = current + 1
        return f"Request Approved. Usage: {current + 1}/{limit}"

lobbyist = Lobbyist()
