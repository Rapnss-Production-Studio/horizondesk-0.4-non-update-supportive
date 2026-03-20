import requests
import json

class Merger:
    """
    Absorbs external APIs into the Hive.
    The 'Borg' of REST APIs.
    """
    def bridge_api(self, name, base_url, endpoint, method="GET", payload=None):
        """
        Dynamically calls an external API and formats it as a Corporate Asset.
        """
        try:
            full_url = f"{base_url}/{endpoint}"
            headers = {"User-Agent": "Horizon-Corp-Agent/1.0"}
            
            if method.upper() == "GET":
                resp = requests.get(full_url, headers=headers, params=payload)
            elif method.upper() == "POST":
                resp = requests.post(full_url, headers=headers, json=payload)
            else:
                return "Unsupported Method."
                
            return {
                "asset_name": name,
                "status": resp.status_code,
                "data": resp.json() if resp.content else "No Content"
            }
        except Exception as e:
            return f"Merger Failed: {e}"

# Singleton
merger = Merger()
