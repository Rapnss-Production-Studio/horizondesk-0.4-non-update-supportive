
from core.tools import BaseTool
import threading
import time
import os

class PlaywrightManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(PlaywrightManager, cls).__new__(cls)
                cls._instance.playwright = None
                cls._instance.browser = None
                cls._instance.context = None
                cls._instance.page = None
                cls._instance.is_active = False
        return cls._instance

    def start(self, headless=False):
        from playwright.sync_api import sync_playwright
        
        # Detect if we are in an asyncio loop (which breaks sync_playwright)
        import asyncio
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                print(f"[Playwright] WARNING: Asyncio loop detected! This will break Sync Playwright.")
                # We can't fix this easily without nest_asyncio or threads. 
                # Attempt to apply nest_asyncio if available
                try:
                    import nest_asyncio
                    nest_asyncio.apply()
                    print(f"[Playwright] Applied nest_asyncio patch.")
                except ImportError:
                    print(f"[Playwright] nest_asyncio not found. Attempting to proceed (will likely fail).")
        except RuntimeError:
            pass

        if not self.is_active:
            try:
                self.playwright = sync_playwright().start()
            except Exception as e:
                print(f"[Playwright] Failed to start Playwright driver: {e}")
                self.is_active = False
                return

            # Use REAL Chrome User Data Directory to access Main Profile
            import os
            local_app_data = os.environ.get('LOCALAPPDATA')
            if not local_app_data:
                # Fallback
                user_profile = os.environ.get('USERPROFILE')
                local_app_data = os.path.join(user_profile, "AppData", "Local")
            
            # Detect default Windows browser via registry
            def get_default_windows_browser():
                import winreg
                try:
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice")
                    prog_id, _ = winreg.QueryValueEx(key, "ProgId")
                    prog_id = prog_id.lower()
                    if "chrome" in prog_id: return "chrome"
                    if "edge" in prog_id: return "msedge"
                    if "firefox" in prog_id: return "firefox"
                except Exception:
                    pass
                return "msedge" # Safe fallback on Windows
            
            default_browser = get_default_windows_browser()
            print(f"[Playwright] Detected default Windows browser: {default_browser}")

            # Try launching default browser first, then fallback, then bundled Chromium
            channels = [
                ("chrome", os.path.join(local_app_data, "Google", "Chrome", "User Data")),
                ("msedge", os.path.join(local_app_data, "Microsoft", "Edge", "User Data"))
            ]
            
            # Prioritize default browser
            if default_browser == "msedge":
                channels_to_try = [channels[1], channels[0], (None, None)]
            elif default_browser == "chrome":
                channels_to_try = [channels[0], channels[1], (None, None)]
            else:
                # If firefox or unknown, we just stick to chrome -> edge -> bundled for chromium engine compatibility
                channels_to_try = [channels[0], channels[1], (None, None)]
            
            for channel, user_data_dir in channels_to_try:
                try:
                    if channel:
                        print(f"[Playwright] Attempting to attach to {channel.upper()} Profile: {user_data_dir}")
                        self.context = self.playwright.chromium.launch_persistent_context(
                            user_data_dir,
                            headless=headless,
                            channel=channel, 
                            viewport={'width': 1280, 'height': 720},
                            args=['--remote-debugging-port=9222', '--no-startup-window'],
                            ignore_default_args=["--enable-automation"]
                        )
                    else:
                        print(f"[Playwright] Attempting to launch bundled Chromium (Guest Profile)")
                        self.browser = self.playwright.chromium.launch(headless=headless)
                        self.context = self.browser.new_context(viewport={'width': 1280, 'height': 720})
                    
                    # Successfully launched!
                    break
                    
                except Exception as e:
                    err_msg = str(e)
                    print(f"[Playwright] {channel or 'Chromium'} Launch Error: {err_msg}")
                    
                    if "Target closed" in err_msg or "SingletonLock" in err_msg or "generic_error" in err_msg:
                        print(f"[Playwright] ERROR: Could not lock {channel} Profile. \n>> PLEASE CLOSE ALL {channel.upper()} WINDOWS AND TRY AGAIN. <<")
                        # This is a locking error, not a missing installation, so don't try other browsers if user specifically uses this one
                        if channel == "chrome": break 
            
            if not self.context:
                print("[Playwright] FATAL: All browser launch attempts failed.")
                try: 
                    self.playwright.stop() 
                    self.playwright = None
                except: pass
                self.is_active = False
                return

            self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
            self.is_active = True
            print("[Playwright] Main Browser Context started.")

    def stop(self):
        if self.is_active:
            if self.context: self.context.close()
            if self.browser: self.browser.close()
            if self.playwright: self.playwright.stop()
            self.is_active = False
            print("[Playwright] Browser stopped.")

    def ensure_active(self):
        # Check if the existing page or context was closed by the user
        if self.is_active:
            try:
                # In python Playwright, is_closed is a property on Page.
                is_page_closed = getattr(self.page, 'is_closed', True)
                if self.page and is_page_closed:
                    # Try to get another open page
                    if self.context and getattr(self.context, 'pages', []):
                        open_pages = [p for p in self.context.pages if not getattr(p, 'is_closed', True)]
                        if open_pages:
                            self.page = open_pages[0]
                        else:
                            print("[Playwright] Browser or context was closed manually. Restarting...")
                            self.stop()
                    else:
                        print("[Playwright] Context lost. Restarting...")
                        self.stop()
            except Exception as e:
                # If checking throws (e.g., disconnected session), force restart
                print(f"[Playwright] Session disconnected: {e}. Restarting...")
                self.stop()

        if not self.is_active:
            self.start(headless=False) # Default to visible
            
        # Guarantee page exists
        try:
            if self.page and getattr(self.page, 'is_closed', True):
                self.page = self.context.new_page()
        except: pass
            
        return self.page

# --- Tools ---

class BrowserOpenTool(BaseTool):
    def __init__(self):
        super().__init__("BrowserOpen", "Opens the browser. Input: JSON 'url' (optional).")

    def execute(self, url=None, payload=None):
        if payload:
            if isinstance(payload, dict):
                url = payload.get('url')
            elif isinstance(payload, str):
                import json
                try:
                    data = json.loads(payload)
                    if isinstance(data, dict): url = data.get('url')
                except: pass
        
        manager = PlaywrightManager()
        page = manager.ensure_active()
        
        if url:
            try:
                page.goto(url, timeout=30000)
                return f"Browser opened and navigated to {url}"
            except Exception as e:
                return f"Browser opened but navigation failed: {e}"
        return "Browser opened."

class BrowserNavigateTool(BaseTool):
    def __init__(self):
        super().__init__("BrowserNavigate", "Navigates to a URL. Input: JSON 'url'.")

    def execute(self, url=None, payload=None):
        target = url
        if payload:
            if isinstance(payload, dict):
                target = payload.get('url')
            elif isinstance(payload, str):
                import json
                try:
                    data = json.loads(payload)
                    if isinstance(data, dict): target = data.get('url')
                except: pass
                
        if not target: return "Error: URL required."
        
        manager = PlaywrightManager()
        if not manager.is_active: return "Error: Browser not open. Use BrowserOpen first."
        
        try:
            manager.page.goto(target, timeout=30000)
            return f"Navigated to {target}"
        except Exception as e:
            return f"Error navigating: {e}"

class BrowserClickTool(BaseTool):
    def __init__(self):
        super().__init__("BrowserClick", "Clicks an element. Input: JSON 'selector' (CSS or XPath).")

    def execute(self, selector=None, payload=None):
        target = selector
        if payload:
            if isinstance(payload, dict):
                target = payload.get('selector')
            elif isinstance(payload, str):
                import json
                try:
                    data = json.loads(payload)
                    if isinstance(data, dict): target = data.get('selector')
                except: pass
                
        if not target: return "Error: Selector required."
        
        manager = PlaywrightManager()
        if not manager.is_active: return "Error: Browser not open."
        
        try:
            manager.page.click(target, timeout=5000)
            return f"Clicked element '{target}'"
        except Exception as e:
            return f"Error clicking '{target}': {e}"

class BrowserTypeTool(BaseTool):
    def __init__(self):
        super().__init__("BrowserType", "Types text into an element. Input: JSON 'selector', 'text'.")

    def execute(self, selector=None, text=None, payload=None):
        sel = selector
        txt = text
        if payload:
            if isinstance(payload, dict):
                sel = payload.get('selector')
                txt = payload.get('text')
            elif isinstance(payload, str):
                import json
                try:
                    data = json.loads(payload)
                    if isinstance(data, dict):
                        sel = data.get('selector')
                        txt = data.get('text')
                except: pass
            
        if not sel or not txt: return "Error: Selector and text required."
        
        manager = PlaywrightManager()
        if not manager.is_active: return "Error: Browser not open."
        
        try:
            manager.page.fill(sel, txt, timeout=5000)
            return f"Typed '{txt}' into '{sel}'"
        except Exception as e:
            return f"Error typing: {e}"

class BrowserScrollTool(BaseTool):
    def __init__(self):
        super().__init__("BrowserScroll", "Scrolls the page. Input: 'direction' ('up', 'down', 'bottom', 'top').")

    def execute(self, direction='down', payload=None):
        d = direction
        if payload:
            if isinstance(payload, dict):
                d = payload.get('direction', 'down')
            elif isinstance(payload, str):
                import json
                try:
                    data = json.loads(payload)
                    if isinstance(data, dict): d = data.get('direction', 'down')
                except: pass
        
        manager = PlaywrightManager()
        if not manager.is_active: return "Error: Browser not open."
        
        try:
            if d == 'down':
                manager.page.evaluate("window.scrollBy(0, 500)")
            elif d == 'up':
                manager.page.evaluate("window.scrollBy(0, -500)")
            elif d == 'bottom':
                manager.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            elif d == 'top':
                manager.page.evaluate("window.scrollTo(0, 0)")
            return f"Scrolled {d}"
        except Exception as e:
            return f"Error scrolling: {e}"

class BrowserScreenshotTool(BaseTool):
    def __init__(self):
        super().__init__("BrowserScreenshot", "Takes a screenshot of the current page. Input: 'filename' (optional).")

    def execute(self, filename=None, payload=None):
        fname = filename
        if payload and isinstance(payload, dict): fname = payload.get('filename')
        
        manager = PlaywrightManager()
        if not manager.is_active: return "Error: Browser not open."
        
        import uuid
        user_profile = os.environ.get('USERPROFILE') or "C:\\Users\\User"
        base_dir = os.path.join(user_profile, "AppData", "Local", "Omniagent", "Screenshot")
        if not os.path.exists(base_dir): os.makedirs(base_dir)
        
        if not fname:
            fname = f"web_{str(uuid.uuid4())[:8]}.png"
        
        full_path = os.path.join(base_dir, fname) if not os.path.isabs(fname) else fname
        
        try:
            manager.page.screenshot(path=full_path)
            return f"Screenshot saved to {full_path}"
        except Exception as e:
            return f"Error taking screenshot: {e}"

class BrowserScrapeTool(BaseTool):
    def __init__(self):
        super().__init__("BrowserScrape", "Get page content. Input: 'type' ('text', 'html'). Default text.")

    def execute(self, type='text', payload=None):
        t = type
        if payload and isinstance(payload, dict): t = payload.get('type', 'text')
        
        manager = PlaywrightManager()
        if not manager.is_active: return "Error: Browser not open."
        
        try:
            if t == 'html':
                return manager.page.content()[:10000] # Truncate for LLM
            else:
                return manager.page.inner_text('body')[:10000]
        except Exception as e:
            return f"Error scraping: {e}"
