from core.tools import BaseTool
import webbrowser
import requests
from bs4 import BeautifulSoup
import urllib.parse
import os
import subprocess

try:
    from duckduckgo_search import DDGS
except ImportError:
    DDGS = None

class GoogleSearchTool(BaseTool):
    def __init__(self):
        super().__init__("GoogleSearch", "A robust, no-API-key Google Search scraper. Input: JSON 'query'.")

    def execute(self, query=None, payload=None):
        q = query or (payload.get('query') if isinstance(payload, dict) else payload)
        if not q: return "Error: No query provided."
        
        results = []
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "DNT": "1"
            }
            url = f"https://www.google.com/search?q={urllib.parse.quote(str(q))}&num=8"
            res = requests.get(url, headers=headers, timeout=12)
            
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                for g in soup.select(".g"):
                    title_el = g.select_one("h3")
                    link_el = g.select_one("a")
                    snippet_el = g.select_one(".VwiC3b, .st, .IsZ6id")
                    
                    if title_el and link_el and link_el.get('href', '').startswith('http'):
                        title = title_el.get_text()
                        link = link_el['href']
                        snippet = snippet_el.get_text() if snippet_el else "No snippet available."
                        results.append(f"Title: {title}\nLink: {link}\nSnippet: {snippet}\n")
                        if len(results) >= 5: break
            else:
                return f"Google Search failed with HTTP {res.status_code}."
        except Exception as e:
            return f"Google Scraper Error: {e}"

        return "\n".join(results) if results else "No results found on Google."

class SearchWebTool(GoogleSearchTool):
    """Alias for backwards compatibility."""
    def __init__(self):
        super(GoogleSearchTool, self).__init__("SearchWeb", "Searches the web (Google Scraper). Input: JSON 'query'.")

class WebSearchMCPTool(BaseTool):
    def __init__(self):
        super().__init__("WebSearchMCP", "Advanced multi-engine search (Google, Bing, Brave, DDG) without API keys. Auto-fallbacks for high accuracy. Input: JSON 'query'.")

    def _bing_search(self, query):
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            url = f"https://www.bing.com/search?q={urllib.parse.quote(str(query))}"
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                results = []
                for item in soup.select(".b_algo"):
                    title = item.select_one("h2")
                    link = item.select_one("a")
                    snippet = item.select_one(".b_caption p, .b_algo p")
                    if title and link:
                        results.append(f"Title: {title.get_text()}\nLink: {link['href']}\nSnippet: {snippet.get_text() if snippet else ''}\n")
                    if len(results) >= 3: break
                return results
        except: pass
        return []

    def execute(self, query=None, payload=None):
        q = query or (payload.get('query') if isinstance(payload, dict) else payload)
        if not q: return "Error: No query provided."
        
        all_results = []
        
        # 1. Try Google first
        goog = GoogleSearchTool().execute(query=q)
        if goog and not goog.startswith("Error") and not goog.startswith("Google Search failed"):
            all_results.append("[SOURCE: GOOGLE]\n" + goog)
        
        # 2. Try Bing
        bing_res = self._bing_search(q)
        if bing_res:
            all_results.append("[SOURCE: BING]\n" + "\n".join(bing_res))
            
        # 3. Try DuckDuckGo
        if DDGS and len(all_results) < 2:
            try:
                ddgs = DDGS()
                results = list(ddgs.text(str(q), max_results=3))
                if results:
                    snippets = ["[SOURCE: DUCKDUCKGO]"]
                    for r in results:
                        snippets.append(f"Title: {r.get('title')}\nLink: {r.get('href')}\nSnippet: {r.get('body')}\n")
                    all_results.append("\n".join(snippets))
            except: pass
            
        if not all_results:
            return "All search engines failed to return results. Suggest using 'BrowserOpen' to research manually."
            
        return "\n\n".join(all_results[:2])

class OpenBrowserUrlTool(BaseTool):
    def __init__(self):
        super().__init__("OpenBrowserUrl", "Opens a specific URL. Input: JSON 'url', optional 'browser' ('chrome', 'firefox', 'edge').")

    def execute(self, url=None, browser=None, payload=None):
        target = url
        brows = browser
        
        # Robust Payload Parsing
        if payload:
            if isinstance(payload, dict):
                target = payload.get('url')
                brows = payload.get('browser')
            elif isinstance(payload, str):
                # Try to parse as JSON first
                import json
                try:
                    data = json.loads(payload)
                    if isinstance(data, dict):
                        target = data.get('url')
                        brows = data.get('browser')
                    else:
                        target = payload # Treat as raw URL string
                except json.JSONDecodeError:
                    target = payload # Treat as raw URL string
            
        if not target: return "Error: No URL provided."
        
        # Handle specific browser requests (best effort) or default to system browser
        if brows:
            b_name = brows.lower()
            try:
                if "chrome" in b_name:
                    try:
                        webbrowser.get('chrome').open(target)
                        return f"Opened {target} in Chrome."
                    except webbrowser.Error:
                        webbrowser.open(target)
                        return f"Opened {target} in default browser (Chrome not found)."
                elif "firefox" in b_name:
                    try:
                        webbrowser.get('firefox').open(target)
                        return f"Opened {target} in Firefox."
                    except webbrowser.Error:
                        webbrowser.open(target)
                        return f"Opened {target} in default browser (Firefox not found)."
                elif "edge" in b_name:
                    try:
                        webbrowser.get('edge').open(target)
                        return f"Opened {target} in Edge."
                    except webbrowser.Error:
                        webbrowser.open(target)
                        return f"Opened {target} in default browser (Edge not found)."
            except Exception as e:
                pass # Fall through to default behavior below
        
        # Default behavior
        # Detect if this is a local file path (not a web URL)
        # Windows paths: C:\, D:\, etc. or UNC \\server\share
        # Unix paths: /home/..., /var/...
        # Already file:// URI
        is_local_file = False
        
        if target.startswith("file://"):
            is_local_file = True
        elif len(target) > 2 and target[1] == ':' and target[2] in ['\\', '/']:
            # Windows absolute path like C:\Users\...
            is_local_file = True
        elif target.startswith("\\\\"):
            # UNC path like \\server\share
            is_local_file = True
        elif target.startswith("/") and not target.startswith("//"):
            # Unix absolute path (but not protocol-relative URL)
            is_local_file = True
            
        try:
            if is_local_file and not target.startswith("file://"):
                # Convert to proper file:// URI
                import urllib.parse
                # Normalize path separators and encode
                normalized_path = os.path.abspath(target)
                file_uri = "file:///" + urllib.parse.quote(normalized_path.replace("\\", "/"), safe=":/")
                webbrowser.open(file_uri)
                return f"Opened local file: {target}"
            else:
                webbrowser.open(target)
                return f"Opened {target} in default browser."
        except Exception as e:
            return f"Error opening URL: {e}"

class DownloadPageTool(BaseTool):
    def __init__(self):
        super().__init__("DownloadPage", "Downloads and extracts text from a webpage. Input: JSON 'url'. Returns text content.")
    
    def execute(self, url=None, filename=None, payload=None):
        target_url = url
        if payload and isinstance(payload, dict):
            target_url = payload.get('url')
        
        if not target_url: return "Error: url required."
        
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            res = requests.get(target_url, headers=headers, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")
            
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.extract()    

            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return text[:5000]
        except Exception as e:
            return f"Error downloading/parsing: {e}"

def get_search_instruction():
    return """
[SEARCH PRIORITY PROTOCOL]
When you need to find information from the web:
1. ALWAYS prioritize 'WebSearchMCP' for general research. It aggregates results from Google, Bing, and others for maximum accuracy.
2. Use 'GoogleSearch' if you specifically need Google's indexed results (e.g. news, specific websites).
3. These tools do NOT require API keys and are more robust than the standard SearchWeb/DDGS tools.
4. If results are still thin, use 'BrowserOpen' to navigate manually.
"""
