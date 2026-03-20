import os
import sys
import json
import argparse
import zipfile
import tempfile
from colorama import init, Fore

init(autoreset=True)

API_BASE = 'https://horizon-online.api-rapnss.workers.dev'
TIGRIS_UPLOADER = 'https://sufy-uploader.api-rapnss.workers.dev/tigris-upload'
CLI_CLIENT_ID = 'client_19149213c616458a813269c2b232bd7e'
OAUTH_REDIRECT_URI = 'http://localhost:9473/callback'


def main():
    parser = argparse.ArgumentParser(description="Horizon SDK CLI - Build, test, and publish plugins for Horizon Desk.")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # init command
    init_parser = subparsers.add_parser("init", help="Scaffold a new plugin")
    init_parser.add_argument("name", help="Name of the plugin")

    # run command (Workshop GUI)
    run_parser = subparsers.add_parser("run", help="Run a plugin workshop using its .raf file")
    run_parser.add_argument("file", help="Path to the horizon_plugin.raf file")
    run_parser.add_argument("--port", help="Port for the workshop bridge", default=4000)

    # test command (CLI mode)
    test_parser = subparsers.add_parser("test", help="Fast CLI test for the current plugin")
    test_parser.add_argument("--prompt", help="Prompt to test the agent with", default="List your tools")

    # login command
    subparsers.add_parser("login", help="Authenticate with your Rapnss account")

    # logout command
    subparsers.add_parser("logout", help="Remove stored credentials")

    # whoami command
    subparsers.add_parser("whoami", help="Display current authenticated user")

    # publish command
    publish_parser = subparsers.add_parser("publish", help="Publish the current plugin to the Horizon Store")
    publish_parser.add_argument("--name", help="Override plugin name")
    publish_parser.add_argument("--version", help="Override version string")
    publish_parser.add_argument("--category", help="Plugin category", default="general")
    publish_parser.add_argument("--description", help="Short description")

    # status command
    subparsers.add_parser("status", help="List your published plugins")

    args = parser.parse_args()

    if args.command == "init":
        handle_init(args.name)
    elif args.command == "run":
        handle_run(args.file)
    elif args.command == "test":
        handle_test(args.prompt)
    elif args.command == "login":
        handle_login()
    elif args.command == "logout":
        handle_logout()
    elif args.command == "whoami":
        handle_whoami()
    elif args.command == "publish":
        handle_publish(args)
    elif args.command == "status":
        handle_status()
    else:
        parser.print_help()


# ─────────────────────────────────────────────────────────────
# LOGIN / AUTH
# ─────────────────────────────────────────────────────────────

def handle_login():
    import webbrowser
    import http.server
    import urllib.parse
    import time
    from .credentials import save_credentials
    import requests

    print(Fore.CYAN + "╔══════════════════════════════════════╗")
    print(Fore.CYAN + "║    Horizon SDK — CLI Login           ║")
    print(Fore.CYAN + "╚══════════════════════════════════════╝")
    print()

    auth_code_holder = [None]

    class CallbackHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urllib.parse.urlparse(self.path)
            
            if parsed.path == '/login':
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                html = f"""
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <title>Horizon SDK Login</title>
                    <style>
                        body {{ font-family: system-ui, sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; background: #f8f9fa; margin: 0; }}
                        .box {{ text-align: center; padding: 48px; background: white; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); width: 400px; }}
                    </style>
                </head>
                <body>
                    <div class="box">
                        <h2 style="color:#1a73e8; margin-bottom: 24px;">Login to Horizon SDK</h2>
                        <script src="https://rapnss.in/api/auth/sdk.js"></script>
                        <div id="rapnss-login" style="display: flex; justify-content: center;"></div>
                        <script>
                            RapnssAuth.init({{
                                clientId: '{CLI_CLIENT_ID}',
                                redirectUri: '{OAUTH_REDIRECT_URI}',
                                containerId: 'rapnss-login',
                                onSuccess: function(data) {{
                                    window.location.href = '/callback?code=' + data.code;
                                }},
                                onError: function(err) {{
                                    console.error('Auth Error:', err);
                                    document.body.innerHTML = '<h2>Auth Error</h2><p>Check console for details.</p>';
                                }}
                            }});
                        </script>
                    </div>
                </body>
                </html>
                """
                self.wfile.write(html.encode('utf-8'))

            elif parsed.path == '/callback':
                params = urllib.parse.parse_qs(parsed.query)
                code = params.get('code', [None])[0]

                if code:
                    auth_code_holder[0] = code
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html')
                    self.end_headers()
                    html = '''
                    <html><body style="font-family:system-ui,sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;background:#f8f9fa;">
                    <div style="text-align:center;padding:48px;background:white;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,0.1);">
                    <h1 style="color:#1a73e8;margin-bottom:8px;">✓ Login Successful</h1>
                    <p style="color:#5f6368;">You can close this window and return to the terminal.</p>
                    </div></body></html>
                    '''
                    self.wfile.write(html.encode('utf-8'))
                else:
                    self.send_response(400)
                    self.send_header('Content-Type', 'text/html')
                    self.end_headers()
                    self.wfile.write(b"<h1>Login failed. No authorization code received.</h1>")
            else:
                self.send_response(404)
                self.end_headers()

        def log_message(self, format, *args):
            pass  # Suppress HTTP logs

    # Start local server
    server = http.server.HTTPServer(('localhost', 9473), CallbackHandler)
    server.timeout = 1  # 1 second timeout for unblocking the handle_request loop

    local_login_url = "http://localhost:9473/login"

    print(Fore.YELLOW + "Opening browser for authentication...")
    print(Fore.WHITE + f"If the browser doesn't open, visit: {local_login_url}")
    print()
    webbrowser.open(local_login_url)

    print(Fore.YELLOW + "Waiting for login callback (timeout: 120s)...")
    
    start_time = time.time()
    while not auth_code_holder[0] and (time.time() - start_time) < 120:
        server.handle_request()
        
    server.server_close()

    code = auth_code_holder[0]
    if not code:
        print(Fore.RED + "Login failed: no authorization code received or timed out.")
        return

    # Exchange code via backend
    print(Fore.YELLOW + "Exchanging token...")
    try:
        res = requests.post(f"{API_BASE}/api/dev/auth/token", json={
            'code': code,
            'redirectUri': OAUTH_REDIRECT_URI
        })
        data = res.json()

        if not data.get('success'):
            print(Fore.RED + f"Login failed: {data.get('error', 'Unknown error')}")
            return

        save_credentials({
            'token': data['token'],
            'user': data['user'],
            'developer': data['developer']
        })

        print()
        print(Fore.GREEN + "✓ Login successful!")
        print(Fore.WHITE + f"  Welcome, {data['user']['username']}!")
        print(Fore.WHITE + f"  Developer ID: {data['developer']['id']}")
        print(Fore.WHITE + f"  Free releases: {data['developer']['free_releases_left']}")
        print(Fore.WHITE + f"  Ad balance: ${data['developer']['ad_balance']:.2f}")
        print()

    except Exception as e:
        print(Fore.RED + f"Login error: {e}")


def handle_logout():
    from .credentials import clear_credentials
    clear_credentials()
    print(Fore.GREEN + "✓ Logged out. Credentials removed.")


def handle_whoami():
    from .credentials import load_credentials
    creds = load_credentials()
    if not creds:
        print(Fore.RED + "Not logged in. Run 'horizondesk-sdk login' first.")
        return

    user = creds.get('user', {})
    dev = creds.get('developer', {})
    print(Fore.CYAN + "╔══════════════════════════════════════╗")
    print(Fore.CYAN + "║    Current Authenticated User        ║")
    print(Fore.CYAN + "╚══════════════════════════════════════╝")
    print(Fore.WHITE + f"  Username:     {user.get('username', '—')}")
    print(Fore.WHITE + f"  Email:        {user.get('email', '—')}")
    print(Fore.WHITE + f"  User ID:      {user.get('id', '—')}")
    print(Fore.WHITE + f"  Developer ID: {dev.get('id', '—')}")
    print(Fore.WHITE + f"  Free releases: {dev.get('free_releases_left', 0)}")
    print(Fore.WHITE + f"  Ad balance:   ${dev.get('ad_balance', 0):.2f}")


# ─────────────────────────────────────────────────────────────
# PUBLISH
# ─────────────────────────────────────────────────────────────

def handle_publish(args):
    import requests
    from .credentials import load_credentials

    creds = load_credentials()
    if not creds:
        print(Fore.RED + "Not logged in. Run 'horizondesk-sdk login' first.")
        return

    # Check if we are in a plugin directory
    if not os.path.exists("horizon_plugin.raf"):
        print(Fore.RED + "Error: No 'horizon_plugin.raf' found in current directory.")
        print(Fore.YELLOW + "Run this command from inside a plugin directory.")
        return

    # Read metadata
    with open("horizon_plugin.raf", "r") as f:
        meta = json.load(f)

    plugin_name = args.name or meta.get("name", "Unnamed Plugin")
    plugin_version = args.version or meta.get("version", "1.0.0")
    description = args.description or meta.get("description", f"A plugin: {plugin_name}")
    category = args.category or meta.get("category", "general")
    dev_id = creds['developer']['id']

    print(Fore.CYAN + "╔══════════════════════════════════════╗")
    print(Fore.CYAN + "║    Horizon SDK — Publish Plugin      ║")
    print(Fore.CYAN + "╚══════════════════════════════════════╝")
    print()
    print(Fore.WHITE + f"  Name:        {plugin_name}")
    print(Fore.WHITE + f"  Version:     {plugin_version}")
    print(Fore.WHITE + f"  Category:    {category}")
    print(Fore.WHITE + f"  Description: {description}")
    print()

    # 1. Zip the plugin directory
    print(Fore.YELLOW + "📦 Packaging plugin...")
    zip_path = os.path.join(tempfile.gettempdir(), f"{plugin_name.replace(' ', '_')}.zip")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk('.'):
            # Skip common junk directories
            dirs[:] = [d for d in dirs if d not in ('__pycache__', '.git', 'node_modules', 'venv', '.venv')]
            for file in files:
                filepath = os.path.join(root, file)
                arcname = os.path.relpath(filepath, '.')
                zf.write(filepath, arcname)

    zip_size = os.path.getsize(zip_path)
    print(Fore.GREEN + f"   Bundle created: {zip_size / 1024:.1f} KB")

    # 2. Upload to Tigris
    print(Fore.YELLOW + "☁️  Uploading to Horizon Cloud...")
    try:
        with open(zip_path, 'rb') as f:
            files = {'file': (os.path.basename(zip_path), f)}
            data = {'filename': os.path.basename(zip_path)}
            upload_res = requests.post(TIGRIS_UPLOADER, files=files, data=data)

        if upload_res.status_code != 200:
            print(Fore.RED + f"Upload failed: {upload_res.text}")
            return

        tigris_url = upload_res.json().get('url')
        print(Fore.GREEN + f"   Upload complete!")
    except Exception as e:
        print(Fore.RED + f"Upload error: {e}")
        return
    finally:
        os.remove(zip_path)

    # 3. Create release via API
    print(Fore.YELLOW + "🚀 Creating release...")
    try:
        res = requests.post(f"{API_BASE}/api/dev/plugins", json={
            'developerId': dev_id,
            'name': plugin_name,
            'description': description,
            'version': plugin_version,
            'tigrisUrl': tigris_url,
            'category': category
        })
        result = res.json()

        if result.get('success'):
            print()
            print(Fore.GREEN + "═══════════════════════════════════════")
            print(Fore.GREEN + f"  ✓ Plugin '{plugin_name}' published!")
            print(Fore.GREEN + f"  Plugin ID: {result.get('pluginId')}")
            print(Fore.GREEN + "═══════════════════════════════════════")
        else:
            print(Fore.RED + f"Publish failed: {result.get('error', 'Unknown error')}")

    except Exception as e:
        print(Fore.RED + f"API error: {e}")


# ─────────────────────────────────────────────────────────────
# STATUS
# ─────────────────────────────────────────────────────────────

def handle_status():
    import requests
    from .credentials import load_credentials

    creds = load_credentials()
    if not creds:
        print(Fore.RED + "Not logged in. Run 'horizondesk-sdk login' first.")
        return

    user_id = creds['user']['id']
    print(Fore.YELLOW + "Fetching your plugins...")

    try:
        res = requests.get(f"{API_BASE}/api/dev/dashboard?userId={user_id}")
        data = res.json()

        if not data.get('success'):
            print(Fore.RED + f"Error: {data.get('error', 'Unknown error')}")
            return

        plugins = data.get('plugins', [])
        dev = data.get('developer', {})

        print()
        print(Fore.CYAN + "╔══════════════════════════════════════╗")
        print(Fore.CYAN + "║    Your Published Plugins            ║")
        print(Fore.CYAN + "╚══════════════════════════════════════╝")
        print(Fore.WHITE + f"  Free releases left: {dev.get('free_releases_left', 0)}")
        print(Fore.WHITE + f"  Ad balance: ${dev.get('ad_balance', 0):.2f}")
        print()

        if not plugins:
            print(Fore.YELLOW + "  No plugins published yet.")
            print(Fore.YELLOW + "  Run 'horizondesk-sdk publish' from a plugin directory to get started.")
        else:
            # Table header
            print(f"  {'Name':<25} {'Version':<10} {'Category':<15} {'Status':<12}")
            print(f"  {'─'*25} {'─'*10} {'─'*15} {'─'*12}")
            for p in plugins:
                status_color = Fore.GREEN if p.get('status') == 'published' else Fore.YELLOW
                print(f"  {p.get('name', '—'):<25} v{p.get('version', '?'):<9} {p.get('category', '—'):<15} {status_color}{p.get('status', '—')}")

        print()

    except Exception as e:
        print(Fore.RED + f"Error: {e}")


# ─────────────────────────────────────────────────────────────
# INIT
# ─────────────────────────────────────────────────────────────

def handle_init(plugin_name):
    print(Fore.CYAN + f"Scaffolding plugin: {plugin_name}...")
    
    # Create directory
    if os.path.exists(plugin_name):
        print(Fore.RED + f"Error: Directory '{plugin_name}' already exists.")
        return

    os.makedirs(plugin_name)
    
    # Create horizon_plugin.raf (Metadata)
    raf_data = {
        "name": plugin_name,
        "version": "1.0.0",
        "developer": os.environ.get("USERNAME", "Developer"),
        "description": f"A specialized plugin for {plugin_name}",
        "entry_point": "main.py",
        "category": "general"
    }
    
    with open(os.path.join(plugin_name, "horizon_plugin.raf"), "w") as f:
        json.dump(raf_data, f, indent=4)

    # Create main.py (Template)
    main_template = f"""from horizondesk_sdk import BaseTool, HorizonPlugin

class MyCustomTool(BaseTool):
    def __init__(self):
        super().__init__("{plugin_name}Tool", "Does something amazing. Input: 'data'.")

    def execute(self, data=None, payload=None):
        val = data or (payload.get('data') if isinstance(payload, dict) else payload)
        return f"[Plugin] Processed: {{val}}"

def register_tools(agent):
    plugin = HorizonPlugin("{plugin_name}")
    plugin.add_tool(MyCustomTool())
    plugin.register_all(agent)
"""
    with open(os.path.join(plugin_name, "main.py"), "w") as f:
        f.write(main_template)

    print(Fore.GREEN + f"Success! Plugin '{plugin_name}' created. Run 'cd {plugin_name}' to start.")


# ─────────────────────────────────────────────────────────────
# TEST
# ─────────────────────────────────────────────────────────────

def handle_test(prompt):
    print(Fore.CYAN + "Starting isolated plugin test...")
    
    # 1. Verify we are in a plugin directory
    if not os.path.exists("horizon_plugin.raf") or not os.path.exists("main.py"):
        print(Fore.RED + "Error: This command must be run inside a plugin directory (containing horizon_plugin.raf and main.py).")
        return

    # 2. Boot a minimal agent
    try:
        # Load environment variables
        import dotenv
        # Try to find .env in current or parent dirs
        dotenv_path = dotenv.find_dotenv()
        if not dotenv_path:
            # Fallback: look in project root if we can find it
            project_root = os.path.dirname(os.path.dirname(os.getcwd()))
            dotenv_path = os.path.join(project_root, ".env")
        
        if os.path.exists(dotenv_path):
            dotenv.load_dotenv(dotenv_path)
            print(Fore.YELLOW + f"Loaded environment from {dotenv_path}")
        else:
            print(Fore.RED + "Warning: .env not found. Agent may fail if it needs API keys.")

        try:
            from core.agent import Agent
            from core.input_manager import InputManager
            agent = Agent()
            agent.input_manager = InputManager() 
            print(Fore.YELLOW + "Using local Horizon Desk core for testing.")
        except ImportError:
            from horizonsdk import MockAgent
            agent = MockAgent()
            print(Fore.YELLOW + "Horizon Desk core not found. Using MockAgent for testing.")
        
        # Load the current plugin
        import importlib.util
        spec = importlib.util.spec_from_file_location("test_plugin", "main.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        if hasattr(module, "register_tools"):
            module.register_tools(agent)
            print(Fore.GREEN + "Plugin loaded successfully.")
        else:
            print(Fore.RED + "Error: main.py missing 'register_tools(agent)' function.")
            return

        # 3. Run a test prompt
        print(Fore.YELLOW + f"Testing Prompt: \"{prompt}\"")
        result = agent.run(prompt)
        print(Fore.WHITE + "--- Agent Response ---")
        print(result)
        print(Fore.WHITE + "----------------------")

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(Fore.RED + f"Error during test: {e}")


# ─────────────────────────────────────────────────────────────
# RUN (Workshop GUI)
# ─────────────────────────────────────────────────────────────

class WorkshopApi:
    def __init__(self, agent, window=None):
        self.agent = agent
        self.window = window

    def run_agent_prompt(self, pane_id, prompt):
        # We wrap the agent.run to capture hooks
        def on_thought(t): 
            if self.window: self.window.evaluate_js(f"window.pushThought({json.dumps(t)})")
        def on_action(a, i): 
            if self.window: self.window.evaluate_js(f"window.pushAction({json.dumps(a)}, {json.dumps(i)})")
        def on_obs(o): 
            if self.window: self.window.evaluate_js(f"window.pushObservation({json.dumps(str(o))})")

        # Basic hook injection (requires agent.py support or monkeypatch)
        self.agent._thought_callback = on_thought
        self.agent._action_callback = on_action
        self.agent._observation_callback = on_obs

        try:
            return self.agent.run(prompt)
        except Exception as e:
            return f"Error: {e}"

def handle_run(raf_path):
    import webview
    import threading
    
    # 1. Verify file
    if not os.path.exists(raf_path):
        # Check if they just gave the name and it's in a folder
        alt_path = os.path.join(raf_path.replace(".raf", ""), "horizon_plugin.raf")
        if os.path.exists(alt_path):
            raf_path = alt_path
        else:
            print(Fore.RED + f"Error: Could not find plugin file at {raf_path}")
            return

    plugin_dir = os.path.dirname(os.path.abspath(raf_path))
    os.chdir(plugin_dir)

    print(Fore.CYAN + f"Launching Horizon Workshop for {os.path.basename(raf_path)}...")
    
    try:
        # Load metadata
        with open("horizon_plugin.raf", "r") as f:
            meta = json.load(f)

        # 2. Setup Agent
        # Try to find project root by looking for main.py upward
        current = plugin_dir
        project_root = None
        for _ in range(5):
            if os.path.exists(os.path.join(current, "main.py")) and os.path.exists(os.path.join(current, "core")):
                project_root = current
                break
            current = os.path.dirname(current)
        
        if not project_root:
            print(Fore.RED + "Error: Could not locate Horizon Desk core files. Ensure you are running from within the Horizon project.")
            return

        try:
            sys.path.append(project_root)
            from core.agent import Agent
            agent = Agent()
            print(Fore.YELLOW + "Using local Horizon Desk core for workshop.")
        except ImportError:
            from horizonsdk import MockAgent
            agent = MockAgent()
            print(Fore.YELLOW + "Horizon Desk core not found. Using MockAgent for workshop.")

        # Load plugin
        import importlib.util
        spec = importlib.util.spec_from_file_location("plugin", "main.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.register_tools(agent)

        # 3. Launch GUI
        # The workshop folder is inside the package
        import horizonsdk
        html_path = os.path.join(os.path.dirname(horizonsdk.__file__), "workshop", "index.html")
        url = f"file:///{html_path.replace(os.sep, '/')}"
        
        api = WorkshopApi(agent)
        window = webview.create_window(
            f"Horizon Workshop - {meta.get('name')}",
            url=url,
            js_api=api,
            width=1400, height=850,
            background_color='#0f172a'
        )
        api.window = window

        def set_label():
            import time
            time.sleep(1.5)
            window.evaluate_js(f"window.updatePluginLabel('{meta.get('name')}')")
            window.evaluate_js(f"window.updatePluginMeta({json.dumps(meta)})")

        threading.Thread(target=set_label, daemon=True).start()
        webview.start(debug=True)

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(Fore.RED + f"Workshop Error: {e}")


if __name__ == "__main__":
    main()
