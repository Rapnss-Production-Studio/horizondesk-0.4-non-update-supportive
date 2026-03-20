import os
import requests
from core.tools import BaseTool

class BraveSearchTool(BaseTool):
    def __init__(self):
        super().__init__("BraveSearch", "Searches the web using Brave Search API. High quality results. Input: JSON 'query'.")

    def execute(self, query=None, payload=None):
        q = query or (payload.get('query') if isinstance(payload, dict) else payload)
        if not q: return "Error: No query provided."
        
        api_key = os.getenv("BRAVE_SEARCH_API_KEY")
        if not api_key:
            return "Error: BRAVE_SEARCH_API_KEY not found in .env. Please provide a key to use this tool."

        url = f"https://api.search.brave.com/res/v1/web/search?q={requests.utils.quote(str(q))}"
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": api_key
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                results = data.get("web", {}).get("results", [])
                snippets = []
                for r in results[:5]:
                    snippets.append(f"Title: {r['title']}\nLink: {r['url']}\nSnippet: {r['description']}\n")
                return "\n".join(snippets) if snippets else "No results found."
            else:
                return f"Error: Brave Search returned HTTP {response.status_code}"
        except Exception as e:
            return f"Error connecting to Brave Search: {e}"

class FirecrawlScrapeTool(BaseTool):
    def __init__(self):
        super().__init__("FirecrawlScrape", "Crawl or scrape a website using Firecrawl (returns clean Markdown/JSON). Input: JSON 'url'.")

    def execute(self, url=None, payload=None):
        target = url or (payload.get('url') if isinstance(payload, dict) else payload)
        if not target: return "Error: No URL provided."
        
        api_key = os.getenv("FIRECRAWL_API_KEY")
        if not api_key:
            return "Error: FIRECRAWL_API_KEY not found in .env. Please provide a key to use this tool."

        # Firecrawl Scrape Endpoint
        scrape_url = "https://api.firecrawl.dev/v0/scrape"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "url": target,
            "pageOptions": {"onlyMainContent": True}
        }

        try:
            response = requests.post(scrape_url, json=data, headers=headers, timeout=20)
            if response.status_code == 200:
                res_data = response.json()
                if res_data.get("success"):
                    content = res_data.get("data", {}).get("markdown", "")
                    return content[:5000] # Truncate for LLM
                return f"Firecrawl Error: {res_data.get('error')}"
            else:
                return f"Error: Firecrawl returned HTTP {response.status_code}"
        except Exception as e:
            return f"Error connecting to Firecrawl: {e}"
