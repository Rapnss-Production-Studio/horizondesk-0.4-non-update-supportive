import pywinauto
import pyautogui
import subprocess
from core.tools import BaseTool

class KeyboardTool(BaseTool):
    def __init__(self):
        super().__init__("Type", "Types text securely. Input: JSON key 'text'.")

    def execute(self, text=None, payload=None):
        content = text or payload
        if not content:
            return "Error: No text provided."
        
        try:
            if isinstance(content, dict):
                content = content.get('text', '')
            
            # small delay to ensure focus
            import time
            time.sleep(0.5)
            pyautogui.write(str(content), interval=0.05)
            return f"Typed: {content}"
        except Exception as e:
            return f"Error typing: {e}"

        except Exception as e:
            return f"Error typing: {e}"

class PressKeyTool(BaseTool):
    def __init__(self):
        super().__init__("PressKey", "Presses a specific key (e.g., 'enter', 'esc', 'tab'). Input: JSON key 'key'.")

    def execute(self, key=None, payload=None):
        target = key or payload
        if not target: return "Error: No key provided."
        
        if isinstance(target, dict):
            target = target.get('key')
            
        try:
            target = str(target).lower().strip()
            if "+" in target:
                keys = target.split("+")
                pyautogui.hotkey(*keys)
                return f"Pressed hotkey: {target}"
            else:
                pyautogui.press(target)
                return f"Pressed key: {target}"
        except Exception as e:
            return f"Error pressing key: {e}"

class LaunchAppTool(BaseTool):
    def __init__(self):
        super().__init__("LaunchApp", "Launches a desktop application. Input: JSON with key 'app_name' (e.g., 'notepad', 'calc').")
        self.apps_map = {}
        self._cache_apps()

    def _cache_apps(self):
        """Scans Start Menu for installed apps."""
        import os
        
        paths = [
            os.path.join(os.environ.get("ProgramData", "C:\\ProgramData"), r"Microsoft\Windows\Start Menu\Programs"),
            os.path.join(os.environ.get("APPDATA", ""), r"Microsoft\Windows\Start Menu\Programs")
        ]
        
        for path in paths:
            if not os.path.exists(path): continue
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.lower().endswith(".lnk") or file.lower().endswith(".exe"):
                        name = os.path.splitext(file)[0].lower()
                        full_path = os.path.join(root, file)
                        self.apps_map[name] = full_path

    def execute(self, app_name=None, command=None, payload=None):
        import difflib
        import os
        import subprocess
        
        target = app_name or command or payload
        if not target:
            return "Error: No app name provided."
        
        if isinstance(target, dict):
            target = target.get('app_name') or target.get('command') or target.get('url') or target.get('link') or target.get('text')
            
        if not target:
             return "Error: No valid app or URL found in input."

        # Auto-detect URL
        target_str = str(target).strip()
        if target_str.startswith("http") or target_str.startswith("www"):
            os.system(f"start {target_str}")
            return f"Opened URL: {target_str}"
            
        aliases = {
            "calculator": "calc",
            "calc": "calc",
            "notepad": "notepad",
            "paint": "mspaint",
            "explorer": "explorer",
            "cmd": "start cmd",
            "terminal": "start cmd",
            "browser": "start chrome",
            "chrome": "start chrome",
            "google chrome": "start chrome",
            "firefox": "start firefox",
            "edge": "start msedge",
            "code": "code",
            "vscode": "code"
        }
        
        target_lower = target_str.lower()
        
        def verify_launch(launch_func, name):
            import time
            try:
                import pygetwindow as gw
                windows_before = set(w.title for w in gw.getAllWindows() if w.title)
            except ImportError:
                gw = None
                windows_before = set()

            try:
                launch_func()
            except Exception as e:
                return f"Error launching {name}: {e}\nAre you sure it's installed?"

            # Wait for app to launch
            time.sleep(2)
            
            if gw:
                windows_after = set(w.title for w in gw.getAllWindows() if w.title)
                new_windows = windows_after - windows_before
                if new_windows:
                    return f"Successfully launched {name}. New window detected: '{list(new_windows)[0]}'"
                else:
                    return f"Attempted to launch {name}, but no new window appeared. It might be running in the background or failed to start."
            else:
                 return f"Launched {name} (Window verification disabled - pygetwindow not installed)."

        # 1. Exact Match in Aliases
        if target_lower in aliases:
            cmd = aliases[target_lower]
            return verify_launch(lambda: os.system(cmd), cmd)
        
        # 2. Exact Match in Scanned Apps
        if not self.apps_map:
            self._cache_apps()
            
        if target_lower in self.apps_map:
            path = self.apps_map[target_lower]
            return verify_launch(lambda: os.startfile(path), path)

        # 3. Fuzzy Match
        matches = difflib.get_close_matches(target_lower, self.apps_map.keys(), n=1, cutoff=0.6)
        if matches:
            best_match = matches[0]
            path = self.apps_map[best_match]
            import time
            try:
                os.startfile(path)
                time.sleep(2)
                return f"App '{target_str}' not found. Did you mean '{best_match}'? Launching '{best_match}'..."
            except Exception as e:
                return f"Error launching {best_match}: {e}"
        
        # 4. Fallback to system start
        try:
            os.system(f"start {target_str}")
            return f"Launched {target_str} (System default)"
        except Exception as e:
            return f"Error launching app: {e}"

class MouseClickTool(BaseTool):
    def __init__(self):
        super().__init__("MouseClick", "Clicks the mouse. Input: 'x', 'y', 'button' ('left', 'right', 'middle').")

    def execute(self, x=0, y=0, button='left', payload=None):
        try:
            if payload and isinstance(payload, dict):
                x = int(payload.get('x', 0))
                y = int(payload.get('y', 0))
                button = payload.get('button', 'left')
            
            pyautogui.click(x, y, button=button)
            return f"Clicked {button} at {x}, {y}"
        except Exception as e:
            return f"Error clicking: {e}"

class TakeScreenshotTool(BaseTool):
    def __init__(self):
        super().__init__("TakeScreenshot", "Takes a screenshot. Input: Optional 'filename', otherwise auto-generated in AppData.")

    def execute(self, filename=None, payload=None):
        import os
        import uuid
        import glob
        import time
        
        # Define base Storage Path
        user_profile = os.environ.get('USERPROFILE') or "C:\\Users\\User"
        base_dir = os.path.join(user_profile, "AppData", "Local", "Omniagent", "Screenshot")
        
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        # Cleanup: Delete files older than 2 days
        now = time.time()
        for f in glob.glob(os.path.join(base_dir, "*")):
            if os.stat(f).st_mtime < now - 2 * 86400: # 2 days in seconds
                try:
                    os.remove(f)
                except: pass

        # Generate unique 8-char name if not provided
        if not filename:
            unique_id = str(uuid.uuid4())[:8]
            filename = f"{unique_id}.png"
        
        # If filename provided doesn't have full path, put it in base_dir
        if not os.path.isabs(filename):
            full_path = os.path.join(base_dir, filename)
        else:
            full_path = filename

        try:
            screenshot = pyautogui.screenshot()
            screenshot.save(full_path)
            return f"Screenshot saved to {full_path}"
        except Exception as e:
            return f"Error taking screenshot: {e}"

class WaitTool(BaseTool):
    def __init__(self):
        super().__init__("Wait", "Waits for a specified duration. Input: 'seconds' (int).")

    def execute(self, seconds=None, payload=None):
        import time
        import re
        try:
            val = seconds
            if payload and isinstance(payload, dict):
                val = payload.get('seconds')
            elif payload:
                val = payload # Handle direct value
            
            if not val:
                return "Error: Seconds required."
            
            # Extract number from string (e.g., "2 seconds" -> 2)
            val_str = str(val)
            match = re.search(r'\d+(\.\d+)?', val_str)
            if not match:
                return f"Error: Could not parse seconds from '{val}'"
                
            sec = float(match.group())
            time.sleep(sec)
            return f"Waited {sec} seconds."
        except Exception as e:
            return f"Error waiting: {e}"
