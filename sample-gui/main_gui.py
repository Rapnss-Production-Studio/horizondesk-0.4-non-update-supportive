import webview
import os
import sys

# Initialize global window variable to fix lint errors
window = None

# Force UTF-8 output so emoji/unicode in print() don't crash on Windows cp1252
reconfig_stdout = getattr(sys.stdout, 'reconfigure', None)
if reconfig_stdout:
    reconfig_stdout(encoding='utf-8', errors='replace')
reconfig_stderr = getattr(sys.stderr, 'reconfigure', None)
if reconfig_stderr:
    reconfig_stderr(encoding='utf-8', errors='replace')
import subprocess
import threading
import time
import urllib.parse
import urllib.request
import ctypes
import tempfile
import zipfile
import shutil
from http.server import HTTPServer, BaseHTTPRequestHandler

import psutil
import requests
import webbrowser
from colorama import init, Fore, Style
from dotenv import load_dotenv

# ---------------------------------------------------------------
# PyInstaller-safe path resolver
# When frozen: files live under sys._MEIPASS (temp extract dir)
# When running from source: use the normal filesystem paths
# ---------------------------------------------------------------
def resource_path(*relative_parts):
    """Return absolute path to a resource, works for dev and PyInstaller."""
    if getattr(sys, 'frozen', False):
        # Running inside a PyInstaller bundle
        base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    else:
        # Running from source — base is the project root (one level up from sample-gui/)
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    return os.path.join(base, *relative_parts)

# Load .env (works from both source and bundle)
load_dotenv(resource_path('.env'))

# Ensure core/, tools/, and root main.py are importable
# In frozen mode, PyInstaller puts them in sys._MEIPASS which is already on sys.path.
# In source mode, insert the project root explicitly.
if not getattr(sys, 'frozen', False):
    sys.path.insert(0, resource_path())

# Initialize colorama
init(autoreset=True)

# (sys.path insertion handled above by resource_path setup)
# Agent framework is loaded via root main.py's get_initialized_agent()
# Only import what's directly needed by HorizonApi itself
from core.input_manager import InputManager
from core.memory import MemorySystem
import json

# Helper for consistent rounding that satisfies static analyzers
def safe_round(val, digits):
    try:
        # Some analyzers fail to find the round(float, int) overload
        # We use a explicit float cast and string formatting as a fallback if needed
        # but here we'll try to be as direct as possible.
        return round(float(val), digits)
    except (Exception, TypeError, ValueError):
        return 0.0

# API Logic — GUI Shell Only
# All AI agent logic lives in root/main.py
class HorizonApi:
    def __init__(self):
        # Shared InputManager (for keyboard blocking during agent runs)
        self.input_manager = None
        self.agents = {} # Track agents per pane for interruption
        try:
            print("Initializing Input Manager...")
            self.input_manager = InputManager()
        except Exception as e:
            print(f"Could not initialize Input Manager: {e}")

    def _get_or_create_agent(self, pane_id):
        """Internal helper to get or initialize an agent for a specific workspace pane."""
        if pane_id not in self.agents:
            from main import get_initialized_agent
            self.agents[pane_id] = get_initialized_agent(self.input_manager)
        return self.agents[pane_id]

    def run_agent_prompt(self, pane_id, prompt):
        """
        Thin bridge: receives a prompt from the GUI workspace and forwards it
        entirely to main.py's run_agent_prompt() which owns all agent logic.
        """
        print(f"[GUI] Prompt from pane '{pane_id}': {prompt[:80]}...")
        try:
            from main import run_agent_prompt as _run
            # We wrap this in our log system
            self.emit_log(f"Starting task in {pane_id}: {prompt[:40]}...", "command")
            result = _run(pane_id, prompt, self.input_manager)
            self.emit_log(f"Task finished in {pane_id}.", "info")
            return result
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.emit_log(f"Error in {pane_id}: {str(e)}", "error")
            return f"Error: {e}"

    def minimize(self):
        print("Minimizing window...")
        if window:
            window.minimize()

    def close(self):
        print("Closing window...")
        if window:
            window.destroy()

    def get_system_metrics(self):
        """Return real system metrics for the Monitor UI."""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=0.2)
            cpu_count = psutil.cpu_count(logical=True)
            cpu_freq = psutil.cpu_freq()
            cpu_freq_mhz = int(cpu_freq.current) if cpu_freq else 0
            # RAM
            ram = psutil.virtual_memory()
            ram_total_gb = safe_round(ram.total / (1024 ** 3), 1)
            ram_used_gb = safe_round(ram.used / (1024 ** 3), 2)
            ram_cached_gb = safe_round(getattr(ram, 'cached', 0) / (1024 ** 3), 2)
            ram_free_gb = safe_round(ram.available / (1024 ** 3), 2)
            ram_percent = ram.percent
 
            # Disk
            disk = psutil.disk_usage('/')
            disk_total_gb = safe_round(disk.total / (1024 ** 3), 1)
            disk_used_gb = safe_round(disk.used / (1024 ** 3), 1)
            disk_free_gb = safe_round(disk.free / (1024 ** 3), 1)
            disk_percent = disk.percent
            # Disk I/O
            d1 = psutil.disk_io_counters()
            time.sleep(0.2)
            d2 = psutil.disk_io_counters()
            if d1 and d2:
                disk_read_mb = safe_round((d2.read_bytes - d1.read_bytes) / (1024 ** 2) / 0.2, 2)
                disk_write_mb = safe_round((d2.write_bytes - d1.write_bytes) / (1024 ** 2) / 0.2, 2)
            else:
                disk_read_mb = 0.0
                disk_write_mb = 0.0
 
            # Network
            n1 = psutil.net_io_counters()
            time.sleep(0.2)
            n2 = psutil.net_io_counters()
            if n1 and n2:
                net_up_mbps = safe_round((n2.bytes_sent - n1.bytes_sent) * 8 / (1024 ** 2) / 0.2, 2)
                net_down_mbps = safe_round((n2.bytes_recv - n1.bytes_recv) * 8 / (1024 ** 2) / 0.2, 2)
            else:
                net_up_mbps = 0.0
                net_down_mbps = 0.0

            import datetime
            now = datetime.datetime.now().strftime("%I:%M:%S %p")

            return {
                "success": True,
                "time": now,
                "cpu": {
                    "percent": cpu_percent,
                    "cores": cpu_count,
                    "freq_mhz": cpu_freq_mhz
                },
                "ram": {
                    "total_gb": ram_total_gb,
                    "used_gb": ram_used_gb,
                    "cached_gb": ram_cached_gb,
                    "free_gb": ram_free_gb,
                    "percent": ram_percent
                },
                "disk": {
                    "total_gb": disk_total_gb,
                    "used_gb": disk_used_gb,
                    "free_gb": disk_free_gb,
                    "percent": disk_percent,
                    "read_mb": disk_read_mb,
                    "write_mb": disk_write_mb
                },
                "net": {
                    "up_mbps": net_up_mbps,
                    "down_mbps": net_down_mbps,
                    "total_mbps": safe_round(net_up_mbps + net_down_mbps, 2)
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_plugins(self):
        # Allow returning list of plugins to UI
        if hasattr(self, 'plugin_manager') and self.plugin_manager:
            return [f"{name} (v{meta.get('version')})" for name, meta in self.plugin_manager.plugins.items()]
        return ["MathWizard (Built-in)", "ChemHelper (Demo)"]
        
    def install_plugin(self, name, download_url):
        print(f"[GUI] Installing plugin: {name} from {download_url}")
        try:
            # Determine if it's a zip or a direct .raf / .py file
            is_zip = download_url.lower().endswith('.zip')
            
            # Use a sanitized folder name from the plugin name
            folder_name = name.replace(" ", "_").replace(".", "").strip()
            plugins_dir = resource_path('plugins')
            target_plugin_dir = os.path.join(plugins_dir, folder_name)

            if not os.path.exists(plugins_dir):
                os.makedirs(plugins_dir)

            if is_zip:
                # 1. Download zip to a temporary file
                tmp_zip = os.path.join(tempfile.gettempdir(), f"plugin_{int(time.time())}.zip")
                print(f"[Installer] Downloading zip to {tmp_zip}...")
                urllib.request.urlretrieve(download_url, tmp_zip)
                
                print(f"[Installer] Extracting into {plugins_dir}...")
                with zipfile.ZipFile(tmp_zip, 'r') as zip_ref:
                    # We extract into a specific folder if the zip doesn't have one, 
                    # but typically zips are expected to have their own top-level folder.
                    # For safety, we extract to the specific target_plugin_dir if it's a "flat" zip.
                    zip_ref.extractall(plugins_dir)
                os.remove(tmp_zip)
            else:
                # 2. Direct file download (likely a .raf file)
                if not os.path.exists(target_plugin_dir):
                    os.makedirs(target_plugin_dir)
                
                filename = "horizon_plugin.raf" if download_url.lower().endswith('.raf') else os.path.basename(download_url)
                download_path = os.path.join(target_plugin_dir, filename)
                
                print(f"[Installer] Downloading direct file to {download_path}...")
                urllib.request.urlretrieve(download_url, download_path)
            
            # 3. Hot-reload the agent's plugin manager
            from main import _gui_agents
            reloaded_count = 0
            for pane_id, agent in _gui_agents.items():
                from core.plugin_manager import PluginManager
                pm = PluginManager(agent)
                pm.load_plugins(force_reload=True)
                print(f"[Installer] Reloaded plugins for agent pane '{pane_id}'.")
                reloaded_count += 1
                
            return {"success": True, "message": f"Plugin {name} installed & loaded!"}
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"[Installer] Error installing plugin: {e}")
            return {"success": False, "error": str(e)}

    def get_installed_plugins(self):
        """Bridge to PluginManager.get_installed_plugins"""
        try:
            # We can use the globals from main.py or just re-init
            from main import _gui_agents
            # Try to get it from the first available agent
            for agent in _gui_agents.values():
                if hasattr(agent, 'plugin_manager'):
                    return agent.plugin_manager.get_installed_plugins()
            
            # Fallback: re-init a temp one if needed
            from core.plugin_manager import PluginManager
            class MockAgent: tools = {}
            pm = PluginManager(MockAgent())
            return pm.get_installed_plugins()
        except Exception as e:
            return []

    def open_plugin_folder(self, folder_name):
        """Bridge to PluginManager.open_plugin_folder"""
        try:
            from core.plugin_manager import PluginManager
            pm = PluginManager(None) # agent not needed for this
            return pm.open_plugin_folder(folder_name)
        except:
            return False

    def get_settings(self):
        print("Fetching settings from DB...")
        try:
            mem = MemorySystem()
            def b(key, default="false"):
                return mem.get_setting(key, default) == "true"
            def s(key, default=""):
                return mem.get_setting(key, default)
            settings = {
                # Appearance
                "darkMode": b("darkMode", "true"),
                "accentColor": s("accentColor", "#10b981"),
                "uiDensity": s("uiDensity", "comfortable"),
                "fontSize": int(s("fontSize", "50")),
                "animationsEnabled": b("animationsEnabled", "true"),
                # Workspace
                "workspaceName": s("workspaceName", "Horizon Desk"),
                "language": s("language", "English (US)"),
                "timezone": s("timezone", "India (UTC+5:30)"),
                "country": s("country", "United States"),
                # Automation / AI
                "agentName": s("agentName", "Horizon Agent"),
                "model": s("model", "Rapnss Inference Engine"),
                "customApiUrl": s("customApiUrl", ""),
                "groqApiKey": s("groqApiKey", ""),
                "canvaApiKey": s("canvaApiKey", ""),
                "enableBackgroundAgents": b("enableBackgroundAgents", "true"),
                "autoTaskExecution": b("autoTaskExecution", "false"),
                "taskRetryLimit": b("taskRetryLimit", "true"),
                # Notifications
                "notificationsEnabled": b("notificationsEnabled", "true"),
                "desktopNotifications": b("desktopNotifications", "true"),
                "taskCompletionAlerts": b("taskCompletionAlerts", "true"),
                "agentActivityAlerts": b("agentActivityAlerts", "true"),
                "dailySummaryEmail": b("dailySummaryEmail", "false"),
                # Automation quick-toggle
                "automationEnabled": b("automationEnabled", "true"),
            }
            return settings
        except Exception as e:
            print(f"Error fetching settings: {e}")
            return {}

    def save_settings(self, settings_json):
        print(f"Saving settings...")
        try:
            settings = json.loads(settings_json) if isinstance(settings_json, str) else settings_json
            mem = MemorySystem()
            for key, value in settings.items():
                if isinstance(value, bool):
                    val_str = "true" if value else "false"
                elif isinstance(value, (int, float)):
                    val_str = str(value)
                else:
                    val_str = str(value)
                mem.set_setting(key, val_str)
            print(f"Saved {len(settings)} settings.")
            return {"success": True}
        except Exception as e:
            print(f"Error saving settings: {e}")
            return {"success": False, "error": str(e)}

    def save_parameters(self, params):
        """Used by Onboarding to save initial config."""
        return self.save_settings(params)

    def exchange_oauth_code(self, code):
        """
        Handles the Rapnss OAuth code exchange entirely in Python.
        This avoids the `file://` CORS issue with `fetch()` calls from the desktop app.
        """
        print(f"[OAuth] Exchanging code for token in Python backend...")
        try:
            client_id = os.getenv("RAPNSS_CLIENT_ID", "client_e759717477b44e89b3aa983071baceb7")
            client_secret = os.getenv("RAPNSS_CLIENT_SECRET", "sec_9d3ba5dbe7ca4ef5b3345fa3480b46f2")
            redirect_uri = "http://127.0.0.1:5173/auth/callback"

            # Step 1: Exchange code for access token
            token_resp = requests.post("https://rapnss.in/api/oauth/token", json={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri
            }, timeout=15)
            token_data = token_resp.json()
            print(f"[OAuth] Token response: {token_resp.status_code} {token_data}")

            if not token_resp.ok or "access_token" not in token_data:
                return {"success": False, "error": "Token exchange failed", "details": token_data}

            access_token = token_data["access_token"]

            # Step 2: Fetch user profile
            user_resp = requests.get("https://rapnss.in/api/oauth/userinfo", headers={
                "Authorization": f"Bearer {access_token}"
            }, timeout=15)
            user_data = user_resp.json()
            print(f"[OAuth] User data: {user_resp.status_code} {user_data}")

            if not user_resp.ok:
                return {"success": False, "error": "Failed to get user profile", "details": user_data}

            # Step 2.5: Sync user profile to Horizon D1 Database
            try:
                sync_resp = requests.post("https://horizon-online.api-rapnss.workers.dev/api/auth/oauth-sync", json=user_data, timeout=10)
                if sync_resp.ok:
                    print(f"[OAuth] Synced user to D1 Database successfully.")
                else:
                    print(f"[OAuth] Failed to sync to D1 Database: {sync_resp.text}")
            except Exception as sync_e:
                print(f"[OAuth] Error syncing user to D1 Database: {sync_e}")

            # Step 3: Return user info to frontend
            email = user_data.get("email", f"{user_data.get('id', 'unknown')}@rapnss.oauth")
            name = user_data.get("name") or user_data.get("username") or email
            
            print(f"[OAuth] ✅ Logged in as: {name} ({email})")
            return {
                "success": True,
                "user": {
                    "id": user_data.get("id", ""),
                    "email": email,
                    "username": name
                }
            }
        except Exception as e:
            print(f"[OAuth] Error during exchange: {e}")
            return {"success": False, "error": str(e)}

    def emit_log(self, text, type='info'):
        """Send a log entry to the frontend LogViewer."""
        if window is None:
            return
        try:
            # Avoid backslashes in f-string expression for older python parser compatibility
            safe_text = str(text).replace("'", "\\'").replace("\n", " ")
            js_code = f"window.dispatchEvent(new CustomEvent('new-log', {{ detail: {{ text: '{safe_text}', type: '{type}' }} }}));"
            window.evaluate_js(js_code)
        except Exception as e:
            print(f"Log Error: {e}")
            pass

    def stop_agent(self, pane_id):
        print(f"[{pane_id}] 🛑 Stop requested for agent.")
        agent = self.agents.get(pane_id)
        if agent:
            # Try to set a stop flag if the agent supports it
            if hasattr(agent, 'stop_execution'):
                agent.stop_execution = True
            self.emit_log(f"Stop signal sent to agent {pane_id}", "error")
            return {"success": True}
        return {"success": False, "error": "Agent not found"}

    def run_threaded_agent(self, pane_id, prompt):
        print(f"[{pane_id}] Agent Prompt: {prompt}")
        agent = self._get_or_create_agent(pane_id)
        if not agent:
            return "Error: Could not initialize AI Worker."
        
        # Reset stop flag
        if hasattr(agent, 'stop_execution'):
            agent.stop_execution = False
            
        self.emit_log(f"Starting agent task: {prompt[:50]}...", "command")
        
        try:
            result = agent.run(prompt)
            if hasattr(agent, 'stop_execution') and agent.stop_execution:
                self.emit_log("Task interrupted by user.", "error")
                return "Task stopped."
            
            self.emit_log("Task completed successfully.", "info")
            return str(result)
        except Exception as e:
            print(f"[{pane_id}] Agent Execution Error: {e}")
            self.emit_log(f"Execution Error: {str(e)}", "error")
            return f"Error: {str(e)}"

    def create_payment(self, price, currency="INR"):
        print(f"Creating Payment: {price} {currency}")
        try:
            url = "https://api.nowpayments.io/v1/payment"
            payload = {
                "price_amount": price,
                "price_currency": currency.lower(),
                "pay_currency": "usdttrc20", # Default crypto, user can change on invoice page usually or use 'invoice' endpoint
                # 'invoice' endpoint is better for UI flow, let's try 'invoice' first if possible, or just payment 
                # Actually, 'v1/invoice' allows user to select crypto.
                "order_id": f"HD-{int(time.time())}",
                "order_description": "Horizon Desk Corporate Trial"
            }
            # Switch to invoice endpoint for better UX
            url = "https://api.nowpayments.io/v1/invoice"
            payload = {
                 "price_amount": price,
                 "price_currency": currency.lower(),
                 "order_id": f"HD-{int(time.time())}",
                 "order_description": "Horizon Desk Corporate Trial",
                 "success_url": "https://horizondesk.com/success",
                 "cancel_url": "https://horizondesk.com/cancel"
            }
            headers = {
                'x-api-key': 'X7QJS2G-2B34FJ2-PT4M6YT-RNRV5RE',
                'Content-Type': 'application/json'
            }
            response = requests.post(url, headers=headers, json=payload)
            print(f"Response: {response.text}")
            data = response.json()
            
            if 'invoice_url' in data:
                webbrowser.open(data['invoice_url'])
                return {"success": True, "url": data['invoice_url']}
            else:
                return {"success": False, "error": str(data)}
        except Exception as e:
            print(f"Error creating payment: {e}")
            return {"success": False, "error": str(e)}

# --- API for manual update check from Settings ---
    def get_app_version(self):
        """Returns the current application version from version.json."""
        try:
            version_file = resource_path('version.json')
            if os.path.exists(version_file):
                with open(version_file, 'r') as f:
                    return json.load(f).get("version", "0.2")
            return "0.2"
        except:
            return "0.2"

    def check_for_updates(self):
        print("[Updater API] Checking for updates manually...")
        try:
            # Read current version from version.json
            version_file = resource_path('version.json')
            current_version = "0.2"
            if os.path.exists(version_file):
                with open(version_file, 'r') as f:
                    current_version = json.load(f).get("version", "0.2")

            resp = requests.get("https://horizon-online.api-rapnss.workers.dev/versions.json", timeout=10)
            if resp.ok:
                data = resp.json()
                latest = data.get("latest", current_version)
                is_newer = False
                
                try:
                    c_parts = [int(x) for x in current_version.split('.')]
                    l_parts = [int(x) for x in latest.split('.')]
                    for c, l in zip(c_parts, l_parts):
                        if l > c:
                            is_newer = True
                            break
                        elif l < c:
                            break
                    if len(l_parts) > len(c_parts) and not is_newer:
                        is_newer = True
                except:
                    is_newer = latest != current_version
                
                return {
                    "success": True, 
                    "updateAvailable": is_newer,
                    "latest": latest,
                    "current": current_version,
                    "download_url": data.get("download_url", ""),
                    "release_notes": data.get("release_notes", "")
                }
            return {"success": False, "error": "HTTP Error"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def apply_update_now(self, *args):
        """Triggers a restart of the app. Accepts *args for backward compatibility with old builds."""
        try:
            print("[Updater API] Restarting app...")
            # If an old build passes a zip path here, we might want to log it
            if args:
                print(f"[Updater API] Note: Received unexpected arguments: {args}")
                
            python = sys.executable
            script = os.path.abspath(sys.argv[0])
            
            if window:
                window.destroy()
            
            if sys.platform == 'win32':
                subprocess.Popen([python, script] + sys.argv[1:])
                sys.exit(0)
            else:
                os.execl(python, python, script, *sys.argv[1:])
                
            return {"success": True}
        except Exception as e:
            print(f"Restart failed: {e}")
            return {"success": False, "error": str(e)}

    def download_update_stage(self, url):
        """Downloads update zip to project root while app is running."""
        try:
            print(f"[Updater API] Staging update from {url}...")
            # Save to project root instead of temp
            base_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.abspath(os.path.join(base_dir, '..'))
            
            filename = f"horizon_update_{int(time.time())}.zip"
            local_zip = os.path.join(project_root, filename)
            
            urllib.request.urlretrieve(url, local_zip)
            return {"success": True, "local_path": local_zip, "filename": filename}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def start_installation(self, local_zip_path, new_version):
        """Triggers the updater.py to extract and move files."""
        try:
            print(f"[Updater API] Starting installation for: {local_zip_path} (v{new_version})...")
            base_dir = os.path.dirname(os.path.abspath(__file__))
            install_dir = os.path.abspath(os.path.join(base_dir, '..'))
            updater_script = os.path.join(install_dir, "updater.py")
            
            if os.path.exists(updater_script):
                # Detach the updater process
                if sys.platform == 'win32':
                    DETACHED_PROCESS = 0x00000008
                    subprocess.Popen([sys.executable, updater_script, local_zip_path, install_dir, new_version], creationflags=DETACHED_PROCESS)
                else:
                    subprocess.Popen([sys.executable, updater_script, local_zip_path, install_dir, new_version], start_new_session=True)
                
                return {"success": True}
            return {"success": False, "error": "updater.py not found."}
        except Exception as e:
            return {"success": False, "error": str(e)}

# --- Local Server for OAuth Redirect ---
class OAuthCallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        # Strip any accidental whitespace/encoding that might be in the path
        clean_path = urllib.parse.unquote(parsed_path.path).strip()
        
        if clean_path == '/auth/callback':
            # Also handle potential spacing in the query string parsing
            # Sometimes ' ? code = val' becomes parsed weirdly. 
            # We'll just regex or safely get 'code' from standard qs, but if it has spaces in keys:
            query_str = urllib.parse.unquote(parsed_path.query)
            query_params = urllib.parse.parse_qs(query_str.replace(' ', ''))
            code = query_params.get('code', [None])[0]

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            if code:
                # Successfully received code. Send JS to close the browser popup
                # and trigger the pywebview inject.
                html = f"""
                <html><body>
                <h2 style="font-family: sans-serif; text-align: center; margin-top: 50px;">
                Authentication successful. You can close this window.
                </h2>
                <script>
                    // Close the popup window
                    setTimeout(() => window.close(), 1500);
                </script>
                </body></html>
                """
                self.wfile.write(html.encode())
                
                # Tell the GUI window to process the code
                if window:
                    print(f"Received OAuth code. Injecting into GUI...")
                    # We inject a JS call that the frontend expects
                    window.evaluate_js(f"if (window.handleOAuthCallback) window.handleOAuthCallback('{code}');")
            else:
                self.wfile.write(b"<html><body><h2>Error: No code received.</h2></body></html>")
        else:
            self.send_response(404)
            self.end_headers()

def start_oauth_server():
    server = HTTPServer(('127.0.0.1', 5173), OAuthCallbackHandler)
    print("Started local OAuth callback server on http://127.0.0.1:5173")
    server.serve_forever()

# Set up the window
def create_window():
    global window
    
    # We no longer launch main.py in a separate terminal.
    # The GUI has its own embedded Agent instance.
    print("Launching Horizon Desk v0.2 GUI...")

    # Fix Windows Taskbar Icon issue
    try:
        myappid = 'rapnss.horizondesk.app.0.2'
        windll = getattr(ctypes, 'windll', None)
        if windll:
            windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except (Exception, AttributeError):
        pass

    # Path to dist/index.html after build
    # For dev, one might use 'http://localhost:5173'
    # For prod, use local file
    
    entry_file = resource_path('sample-gui', 'dist', 'index.html')
    icon_path  = resource_path('sample-gui', 'public', 'logo.ico')

    url = f"file:///{entry_file.replace(os.sep, '/')}"
    if not os.path.exists(entry_file):
        print(f"Build not found at {entry_file}. Please run 'npm run build' first.")
        return

    api = HorizonApi()
    global window
    window = webview.create_window(
        'Horizon Desk', 
        url=url, 
        width=1200, 
        height=800, 
        min_size=(800, 600),
        frameless=True, # Enable custom title bar
        resizable=True,
        easy_drag=True, # Allow dragging from custom areas
        js_api=api
    )
    
    # Start the OAuth server in a background thread
    oauth_thread = threading.Thread(target=start_oauth_server, daemon=True)
    oauth_thread.start()
    
    # Start the loop — Switch debug=False for production
    if os.path.exists(icon_path):
        webview.start(debug=False, icon=icon_path, private_mode=False)
    else:
        webview.start(debug=False, private_mode=False)

if __name__ == '__main__':
    create_window()
