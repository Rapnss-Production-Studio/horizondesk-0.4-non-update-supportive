import os
import sys
import dotenv
from colorama import init, Fore, Style

# Load environment variables
dotenv.load_dotenv()

# Initialize colorama
init(autoreset=True)

# Session file path
SESSION_FILE = os.path.join(os.path.dirname(__file__), ".horizon_session.json")

def save_horizon_session(data):
    """Save team session to file."""
    import json
    try:
        with open(SESSION_FILE, 'w') as f:
            json.dump(data, f)
    except:
        pass

def load_horizon_session():
    """Load team session from file."""
    import json
    try:
        if os.path.exists(SESSION_FILE):
            with open(SESSION_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return None

def clear_horizon_session():
    """Clear saved session."""
    try:
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)
    except:
        pass

def get_initialized_agent(input_manager=None):
    """
    Centralized function to create and configure an OmniAgent instance.
    This ensures both the CLI (main.py) and GUI (main_gui.py) use the exact same tool loadout.
    """
    from core.agent import Agent
    from core.input_manager import InputManager

    # Import Tools
    from tools.filesystem import ListDirectoryTool, ReadFileTool, WriteFileTool
    from tools.desktop import LaunchAppTool, MouseClickTool, TakeScreenshotTool, KeyboardTool, PressKeyTool, WaitTool
    from tools.system import RunCommandTool
    from tools.web import SearchWebTool, OpenBrowserUrlTool, GoogleSearchTool, WebSearchMCPTool
    from tools.mcp_tools import BraveSearchTool, FirecrawlScrapeTool
    from tools.reddit import RedditTool
    
    # Initialize Core
    if input_manager is None:
        input_manager = InputManager()
    
    agent = Agent()
    agent.input_manager = input_manager
    
    # Base OS & General Tools
    agent.register_tool(ListDirectoryTool())
    agent.register_tool(ReadFileTool())
    agent.register_tool(WriteFileTool())
    agent.register_tool(LaunchAppTool())
    agent.register_tool(WaitTool())
    agent.register_tool(MouseClickTool())
    agent.register_tool(KeyboardTool())
    agent.register_tool(PressKeyTool())
    agent.register_tool(TakeScreenshotTool())
    agent.register_tool(SearchWebTool())
    agent.register_tool(GoogleSearchTool())
    agent.register_tool(WebSearchMCPTool())
    agent.register_tool(RedditTool())
    agent.register_tool(OpenBrowserUrlTool())
    agent.register_tool(BraveSearchTool())
    agent.register_tool(FirecrawlScrapeTool())
    agent.register_tool(RunCommandTool())
    
    # Playwright Web Tools
    from tools.playwright_tool import (
        BrowserOpenTool, BrowserNavigateTool, BrowserClickTool, 
        BrowserTypeTool, BrowserScrollTool, BrowserScreenshotTool, BrowserScrapeTool
    )
    agent.register_tool(BrowserOpenTool())
    agent.register_tool(BrowserNavigateTool())
    agent.register_tool(BrowserClickTool())
    agent.register_tool(BrowserTypeTool())
    agent.register_tool(BrowserScrollTool())
    agent.register_tool(BrowserScreenshotTool())
    agent.register_tool(BrowserScrapeTool())
    
    # Vision Tools
    try:
        from tools.vision import AnalyzeImageTool, LocateObjectTool
        agent.register_tool(AnalyzeImageTool(agent))
        agent.register_tool(LocateObjectTool(agent))
    except ImportError:
        pass
        
    # Advanced Tools
    from tools.advanced_tools import AnalyzeDataTool, CreateDocTool, CreatePresentationTool, AskKnowledgeTool, ScheduleMeetingTool, StoreMemoryTool, SearchMemoryTool, AddGoalTool
    agent.register_tool(AnalyzeDataTool())
    agent.register_tool(CreateDocTool())
    agent.register_tool(CreatePresentationTool())
    agent.register_tool(AskKnowledgeTool())
    agent.register_tool(ScheduleMeetingTool())
    agent.register_tool(StoreMemoryTool())
    agent.register_tool(SearchMemoryTool())
    agent.register_tool(AddGoalTool())

    # Video & Telegram (Fixes the ModuleNotFoundError missing tools)
    from tools.video_tools import VideoEditorTool
    agent.register_tool(VideoEditorTool())

    from tools.telegram_tool import TelegramSendMessageTool, TelegramGetUpdatesTool, TelegramGetChatIdTool
    agent.register_tool(TelegramSendMessageTool())
    agent.register_tool(TelegramGetUpdatesTool())
    agent.register_tool(TelegramGetChatIdTool())

    # Plugin Tools
    from tools.plugin_tools import ListPluginsTool

    # Market Data
    from tools.market import AlphaVantageTool
    agent.register_tool(AlphaVantageTool())

    # Plugin Manager
    try:
        from core.plugin_manager import PluginManager
        plugin_manager = PluginManager(agent)
        plugin_manager.load_plugins()
        # Store in globals for interactive @ commands
        globals()['plugin_manager'] = plugin_manager
        
        agent.register_tool(ListPluginsTool(plugin_manager))
        agent.plugin_info = plugin_manager.get_plugin_info()
        print(f"Loaded {len(plugin_manager.plugins)} plugins for the Agent.")
    except Exception as e:
        print(f"Plugin Manager not loaded or encountered error: {e}")
        
    return agent

# --- GUI Agent Runner ---
# A per-pane agent cache owned by main.py so main_gui.py stays a pure GUI shell.
_gui_agents = {}

def run_agent_prompt(pane_id: str, prompt: str, input_manager=None) -> str:
    """
    Called by main_gui.py whenever the user sends a prompt in a workspace pane.
    main_gui.py should NOT manage agent creation or tool registration —
    that is entirely this function's responsibility.
    """
    global _gui_agents

    if pane_id not in _gui_agents:
        print(f"[GUI Agent] Initializing agent for pane '{pane_id}'...")
        try:
            agent = get_initialized_agent(input_manager)
            _gui_agents[pane_id] = agent
            print(f"[GUI Agent] Agent '{pane_id}' ready.")
        except Exception as e:
            import traceback
            traceback.print_exc()
            return f"Error: Could not initialize AI Worker — {e}"

    agent = _gui_agents[pane_id]
    try:
        result = agent.run(prompt)
        return str(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error: {e}"

def main():
    print(Fore.CYAN + "--------------------------------------------------------")
    
    gateway_url = os.getenv("CLOUDFLARE_AI_GATEWAY_URL")
    if not gateway_url:
        print(Fore.RED + "Error: CLOUDFLARE_AI_GATEWAY_URL not found in .env file.")
        print(Fore.YELLOW + "Set it to your deployed horizon-updater worker URL, e.g.:")
        print(Fore.WHITE + "  CLOUDFLARE_AI_GATEWAY_URL=https://horizon-updater.<your-subdomain>.workers.dev")
        return

    # Load previous session if exists
    import builtins
    session = load_horizon_session()
    if session:
        print(Fore.GREEN + f"\n[Session Restored] Team {session.get('team_code')}")
        print(Fore.WHITE + f"  Role: {session.get('role')}")
        print(Fore.WHITE + f"  Is Leader: {session.get('is_leader')}")
        
        # Restore globals and builtins
        globals()['horizon_team_code'] = session.get('team_code')
        globals()['horizon_is_leader'] = session.get('is_leader', False)
        globals()['horizon_member_id'] = session.get('member_id')
        globals()['horizon_my_role'] = session.get('role')
        globals()['horizon_task_mode'] = session.get('task_mode', 'manual')
        globals()['horizon_team_folder'] = session.get('team_folder')
        globals()['horizon_team_members'] = session.get('team_members', [])
        
        builtins.horizon_team_code = session.get('team_code')
        builtins.horizon_is_leader = session.get('is_leader', False)
        builtins.horizon_member_id = session.get('member_id')
        builtins.horizon_my_role = session.get('role')
        builtins.horizon_task_mode = session.get('task_mode', 'manual')
        builtins.horizon_team_members = session.get('team_members', [])
        
        # Also set client state
        from core.horizon_online import get_client
        client = get_client()
        client.team_code = session.get('team_code')
        client.member_id = session.get('member_id')
        client.is_leader = session.get('is_leader', False)
        
        if session.get('is_leader'):
            print(Fore.MAGENTA + "\nLeader commands: @refresh-team, @team-status, @sync-results")
        else:
            print(Fore.MAGENTA + "\nMember commands: @auto-work, @manual-work, @my-tasks")
        print(Fore.YELLOW + "Use @leave-team to leave current team.\n")

    print(Fore.GREEN + "System initialized. Ready for tasks.")
    print(Fore.YELLOW + "Type 'exit' or 'quit' to stop.")

    while True:
        try:
            user_input = input(Fore.BLUE + "\nOmniAgent> " + Style.RESET_ALL)
            if user_input.lower() in ['exit', 'quit']:
                print(Fore.CYAN + "Shutting down...")
                break
            
            if not user_input.strip():
                continue
            
            # @leave-team command
            if user_input.strip().lower() == "@leave-team":
                clear_horizon_session()
                # Clear globals
                for key in ['horizon_team_code', 'horizon_is_leader', 'horizon_member_id', 
                           'horizon_my_role', 'horizon_task_mode', 'horizon_team_folder', 'horizon_team_members']:
                    if key in globals():
                        del globals()[key]
                print(Fore.GREEN + "Left team. Session cleared.")
                continue
            
            # @horizon-online command handler
            if user_input.strip().lower() == "@horizon-online":
                print(Fore.CYAN + "\n=== Horizon Online - Team Collaboration ===")
                print(Fore.WHITE + "1. Create Team (become leader)")
                print(Fore.WHITE + "2. Join Team (enter 6-digit code)")
                choice = input(Fore.BLUE + "\nSelect option (1/2): " + Style.RESET_ALL)
                
                if choice == "1":
                    role = input(Fore.BLUE + "Enter your role (e.g., Backend Developer): " + Style.RESET_ALL)
                    
                    # Task mode selection
                    print(Fore.CYAN + "\n--- Task Distribution Mode ---")
                    print(Fore.WHITE + "1. Manual Mode - Members receive tasks, complete with AI, use @send-team to submit")
                    print(Fore.WHITE + "2. Auto Mode - AI automatically executes tasks and sends results")
                    task_mode = input(Fore.BLUE + "Select mode (1/2): " + Style.RESET_ALL)
                    
                    from core.horizon_online import get_client
                    client = get_client()
                    result = client.create_team(role)
                    if result.get("success"):
                        # Store session state
                        team_folder = os.path.expanduser(f"~/Desktop/HorizonTeam_{result['team_code']}")
                        os.makedirs(team_folder, exist_ok=True)
                        
                        # Set global session variables
                        globals()['horizon_team_code'] = result['team_code']
                        globals()['horizon_is_leader'] = True
                        globals()['horizon_task_mode'] = 'manual' if task_mode == '1' else 'auto'
                        globals()['horizon_team_folder'] = team_folder
                        globals()['horizon_team_members'] = []
                        
                        # Store in builtins for agent access
                        import builtins
                        builtins.horizon_team_code = result['team_code']
                        builtins.horizon_is_leader = True
                        builtins.horizon_task_mode = 'manual' if task_mode == '1' else 'auto'
                        builtins.horizon_team_members = []
                        
                        # Save session to file
                        save_horizon_session({
                            'team_code': result['team_code'],
                            'is_leader': True,
                            'role': role,
                            'task_mode': 'manual' if task_mode == '1' else 'auto',
                            'team_folder': team_folder,
                            'team_members': []
                        })
                        
                        print(Fore.GREEN + f"\n{result['message']}")
                        print(Fore.YELLOW + f"Share this code with your team: {result['team_code']}")
                        print(Fore.CYAN + f"Team folder: {team_folder}")
                        print(Fore.WHITE + f"Task Mode: {'Manual' if task_mode == '1' else 'Automatic'}")
                        print(Fore.MAGENTA + "\nWorkflow:")
                        print(Fore.WHITE + "  1. Share team code with members")
                        print(Fore.WHITE + "  2. Wait for them to join")
                        print(Fore.WHITE + "  3. Run @refresh-team to load member IDs")
                        print(Fore.WHITE + "  4. Ask AI to assign tasks!")
                        print(Fore.MAGENTA + "\nLeader Commands:")
                        print(Fore.WHITE + "  @refresh-team - REQUIRED: Load members before assigning")
                        print(Fore.WHITE + "  @team-status  - View team and task status")
                        print(Fore.WHITE + "  @sync-results - Pull all results to your folder")
                    else:
                        print(Fore.RED + f"Error: {result.get('error')}")
                        
                elif choice == "2":
                    code = input(Fore.BLUE + "Enter 6-digit team code: " + Style.RESET_ALL)
                    role = input(Fore.BLUE + "Enter your role (e.g., Frontend Developer): " + Style.RESET_ALL)
                    from core.horizon_online import get_client
                    import builtins
                    client = get_client()
                    result = client.join_team(code, role)
                    if result.get("success"):
                        # Store session state
                        globals()['horizon_team_code'] = code
                        globals()['horizon_is_leader'] = False
                        globals()['horizon_member_id'] = result['member_id']
                        globals()['horizon_my_role'] = role
                        
                        # Store in builtins for agent access
                        builtins.horizon_team_code = code
                        builtins.horizon_is_leader = False
                        builtins.horizon_member_id = result['member_id']
                        builtins.horizon_my_role = role
                        
                        # Save session to file
                        save_horizon_session({
                            'team_code': code,
                            'is_leader': False,
                            'member_id': result['member_id'],
                            'role': role
                        })
                        
                        print(Fore.GREEN + f"\n{result['message']}")
                        print(Fore.MAGENTA + "\nMember Commands:")
                        print(Fore.WHITE + "  @auto-work   - AI auto-executes tasks immediately")
                        print(Fore.WHITE + "  @manual-work - Get notified, review & give instructions")
                        print(Fore.WHITE + "  @my-tasks    - View tasks assigned to you")
                        print(Fore.WHITE + "  @team-status - View team status")
                    else:
                        print(Fore.RED + f"Error: {result.get('error')}")
                continue
            
            # @auto-work command (member enters auto-execute mode)
            if user_input.strip().lower() == "@auto-work":
                import builtins
                
                # Check if member - from globals or builtins
                member_id = globals().get('horizon_member_id') or getattr(builtins, 'horizon_member_id', None)
                team_code = globals().get('horizon_team_code') or getattr(builtins, 'horizon_team_code', None)
                
                if not member_id:
                    print(Fore.RED + "You are not a team member. Join a team first.")
                    continue
                
                print(Fore.CYAN + "\n=== AUTO-WORK MODE ===")
                print(Fore.YELLOW + "Initializing AI agent...")
                
                # Initialize agent if not exists
                from core.agent import Agent
                from core.horizon_online import get_client
                import time
                
                if 'agent' not in globals() or globals().get('agent') is None:
                    globals()['agent'] = Agent()
                    # Register essential tools
                    from tools.file_system import ReadFileTool, WriteFileTool, ListDirectoryTool
                    from tools.code_tools import RunPythonTool
                    from tools.system_tools import RunCommandTool
                    globals()['agent'].register_tool(ReadFileTool())
                    globals()['agent'].register_tool(WriteFileTool())
                    globals()['agent'].register_tool(ListDirectoryTool())
                    globals()['agent'].register_tool(RunPythonTool())
                    globals()['agent'].register_tool(RunCommandTool())
                
                print(Fore.GREEN + "AI agent ready!")
                print(Fore.WHITE + f"Member ID: {member_id[:20]}...")
                print(Fore.WHITE + f"Team Code: {team_code}")
                print(Fore.WHITE + "Polling every 10 seconds... (Press Ctrl+C to exit)\n")
                
                client = get_client()
                # ALWAYS set member_id and team_code from session
                client.member_id = member_id
                client.team_code = team_code
                client.is_leader = False
                
                processed_tasks = set()  # Track processed task IDs
                
                try:
                    while True:
                        # Poll for new tasks
                        print(Fore.WHITE + ".", end="", flush=True)
                        tasks = client.get_my_tasks()
                        for task in tasks:
                            if task['id'] not in processed_tasks:
                                processed_tasks.add(task['id'])
                                print(Fore.GREEN + f"\n{'='*50}")
                                print(Fore.GREEN + f"[NEW TASK RECEIVED]")
                                print(Fore.WHITE + f"  Task ID: {task['id']}")
                                print(Fore.CYAN + f"  Description: {task['description']}")
                                print(Fore.YELLOW + f"  Type: {task['type']}")
                                print(Fore.MAGENTA + "\nAI is working on this task...\n")
                                
                                # Execute task with agent
                                if 'agent' in dir() or 'agent' in globals():
                                    agent_instance = globals().get('agent')
                                    if agent_instance:
                                        result = agent_instance.run(task['description'])
                                        
                                        # Submit result
                                        client.submit_result(task['id'], {
                                            "filename": f"output_{task['id']}.txt",
                                            "content": str(result)
                                        })
                                        print(Fore.GREEN + f"\n[DONE] Task completed and submitted to leader!")
                                    else:
                                        print(Fore.RED + "Agent not initialized. Run a query first.")
                                else:
                                    print(Fore.RED + "Agent not initialized. Run a query first to init agent.")
                        
                        print(Fore.WHITE + ".", end="", flush=True)  # Progress indicator
                        time.sleep(10)  # Poll every 10 seconds
                except KeyboardInterrupt:
                    print(Fore.CYAN + "\n\nExited auto-work mode.")
                continue
            
            # @manual-work command (member enters manual mode with notifications)
            if user_input.strip().lower() == "@manual-work":
                import builtins
                
                # Check if member - from globals or builtins
                member_id = globals().get('horizon_member_id') or getattr(builtins, 'horizon_member_id', None)
                team_code = globals().get('horizon_team_code') or getattr(builtins, 'horizon_team_code', None)
                
                if not member_id:
                    print(Fore.RED + "You are not a team member. Join a team first.")
                    continue
                
                print(Fore.CYAN + "\n=== MANUAL-WORK MODE ===")
                print(Fore.YELLOW + "Initializing AI agent...")
                
                # Initialize agent if not exists
                from core.agent import Agent
                from core.horizon_online import get_client
                import time
                
                if 'agent' not in globals() or globals().get('agent') is None:
                    globals()['agent'] = Agent()
                    # Register essential tools
                    from tools.filesystem import ReadFileTool, WriteFileTool, ListDirectoryTool
                    from tools.code_tools import RunPythonTool
                    from tools.system_tools import RunCommandTool
                    from tools.web import SearchWebTool, OpenBrowserUrlTool
                    
                    globals()['agent'].register_tool(ReadFileTool())
                    globals()['agent'].register_tool(WriteFileTool())
                    globals()['agent'].register_tool(ListDirectoryTool())
                    globals()['agent'].register_tool(RunPythonTool())
                    globals()['agent'].register_tool(RunCommandTool())
                    globals()['agent'].register_tool(SearchWebTool())
                    globals()['agent'].register_tool(OpenBrowserUrlTool())
                
                print(Fore.GREEN + "AI agent ready!")
                print(Fore.WHITE + f"Member ID: {member_id[:20]}...")
                print(Fore.WHITE + f"Team Code: {team_code}")
                print(Fore.WHITE + "You will be notified of tasks and can give instructions.")
                print(Fore.WHITE + "Polling every 10 seconds... (Press Ctrl+C to exit)\n")
                
                client = get_client()
                # ALWAYS set member_id and team_code from session
                client.member_id = member_id
                client.team_code = team_code
                client.is_leader = False
                
                processed_tasks = set()
                
                try:
                    while True:
                        tasks = client.get_my_tasks()
                        for task in tasks:
                            if task['id'] not in processed_tasks:
                                # Show notification
                                print(Fore.GREEN + f"\n{'='*50}")
                                print(Fore.GREEN + f"[NEW TASK NOTIFICATION]")
                                print(Fore.WHITE + f"  Task ID: {task['id']}")
                                print(Fore.CYAN + f"  Description: {task['description']}")
                                print(Fore.YELLOW + f"  Type: {task['type']}")
                                print(Fore.GREEN + f"{'='*50}")
                                
                                # Ask user to accept
                                accept = input(Fore.BLUE + "\nAccept this task? (y/n): " + Style.RESET_ALL)
                                if accept.lower() == 'y':
                                    processed_tasks.add(task['id'])
                                    
                                    # Get user instructions
                                    print(Fore.CYAN + "\nGive additional instructions to AI (or press Enter to use task as-is):")
                                    instructions = input(Fore.BLUE + "Instructions: " + Style.RESET_ALL)
                                    
                                    full_task = task['description']
                                    if instructions.strip():
                                        full_task = f"{task['description']}\n\nAdditional instructions: {instructions}"
                                    
                                    print(Fore.MAGENTA + "\nAI is working on this task...\n")
                                    
                                    # Execute with agent
                                    if 'agent' in globals() and globals().get('agent'):
                                        result = globals()['agent'].run(full_task)
                                        
                                        # Submit result
                                        client.submit_result(task['id'], {
                                            "filename": f"output_{task['id']}.txt",
                                            "content": str(result)
                                        })
                                        print(Fore.GREEN + f"\n[DONE] Task completed and submitted!")
                                    else:
                                        print(Fore.RED + "Agent not initialized. Run a query first.")
                                else:
                                    print(Fore.YELLOW + "Task skipped. You can accept it later.")
                        
                        time.sleep(10)  # Poll every 10 seconds
                except KeyboardInterrupt:
                    print(Fore.CYAN + "\n\nExited manual-work mode.")
                continue
            
            # @team-status command
            if user_input.strip().lower() == "@team-status":
                if 'horizon_team_code' not in globals():
                    print(Fore.RED + "Not in a team. Use @horizon-online first.")
                    continue
                from core.horizon_online import get_client
                import builtins
                client = get_client()
                status = client.get_team_status()
                print(Fore.CYAN + f"\n=== Team {globals()['horizon_team_code']} Status ===")
                print(Fore.WHITE + f"Leader: {status.get('leader', {}).get('role', 'Unknown')}")
                members = status.get('members', [])
                # Update builtins for agent access
                builtins.horizon_team_members = members
                globals()['horizon_team_members'] = members
                print(Fore.WHITE + f"Members ({len(members)}):")
                for m in members:
                    print(Fore.GREEN + f"  - {m['role']} ({m['id'][:15]}...)")
                tasks = status.get('tasks', [])
                print(Fore.WHITE + f"Tasks ({len(tasks)}):")
                for t in tasks:
                    status_color = Fore.YELLOW if t['status'] == 'pending' else Fore.GREEN
                    print(status_color + f"  [{t['status']}] {t['description'][:50]}...")
                continue
            
            # @refresh-team command (refresh member list for AI)
            if user_input.strip().lower() == "@refresh-team":
                if not globals().get('horizon_is_leader', False):
                    print(Fore.RED + "Only team leader can refresh team.")
                    continue
                from core.horizon_online import get_client
                import builtins
                client = get_client()
                # Ensure client has correct state
                client.team_code = globals().get('horizon_team_code')
                client.is_leader = True
                
                status = client.get_team_status()
                members = status.get('members', [])
                builtins.horizon_team_members = members
                globals()['horizon_team_members'] = members
                print(Fore.GREEN + f"Team refreshed! {len(members)} member(s) loaded.")
                for m in members:
                    print(Fore.WHITE + f"  - {m['role']} (ID: {m['id']})")
                if members:
                    print(Fore.CYAN + "\nYour AI now knows all team members!")
                    print(Fore.WHITE + "Now you can ask: 'Assign frontend task to create landing page'")
                else:
                    print(Fore.YELLOW + "\nNo members yet. Wait for them to join, then run @refresh-team again.")
                continue
            
            # @my-tasks command (members)
            if user_input.strip().lower() == "@my-tasks":
                if 'horizon_member_id' not in globals():
                    print(Fore.RED + "You are not a team member. Use @horizon-online to join.")
                    continue
                from core.horizon_online import get_client
                client = get_client()
                tasks = client.get_my_tasks()
                if not tasks:
                    print(Fore.YELLOW + "No pending tasks assigned to you.")
                else:
                    print(Fore.CYAN + f"\n=== Your Pending Tasks ===")
                    for t in tasks:
                        print(Fore.WHITE + f"  Task ID: {t['id']}")
                        print(Fore.GREEN + f"  Description: {t['description']}")
                        print(Fore.YELLOW + f"  Type: {t['type']}")
                        print()
                continue
            
            # @send-team command (submit work)
            if user_input.strip().lower() == "@send-team":
                if 'horizon_team_code' not in globals():
                    print(Fore.RED + "Not in a team. Use @horizon-online first.")
                    continue
                    
                task_id = input(Fore.BLUE + "Enter Task ID to submit: " + Style.RESET_ALL)
                filename = input(Fore.BLUE + "Enter filename for your work: " + Style.RESET_ALL)
                print(Fore.YELLOW + "Enter your work content (type END on a new line to finish):")
                lines = []
                while True:
                    line = input()
                    if line.strip() == "END":
                        break
                    lines.append(line)
                content = "\n".join(lines)
                
                from core.horizon_online import get_client
                client = get_client()
                result = client.submit_result(task_id, {"filename": filename, "content": content})
                if result.get("success"):
                    print(Fore.GREEN + "Work submitted successfully to team leader!")
                else:
                    print(Fore.RED + f"Error: {result.get('error')}")
                continue
            
            # @sync-results command (leader pulls results)
            if user_input.strip().lower() == "@sync-results":
                if not globals().get('horizon_is_leader', False):
                    print(Fore.RED + "Only team leader can sync results.")
                    continue
                from core.horizon_online import get_client
                client = get_client()
                folder = globals().get('horizon_team_folder', os.path.expanduser("~/Desktop/HorizonTeamResults"))
                result = client.sync_results_to_folder(folder)
                if result.get("success"):
                    print(Fore.GREEN + f"Synced {result['total']} files to {folder}")
                    for f in result.get('synced_files', []):
                        print(Fore.WHITE + f"  - {f}")
                else:
                    print(Fore.RED + f"Error: {result.get('error')}")
                continue
            
            # @list-plugins command
            if user_input.strip().lower() == "@list-plugins":
                pm = globals().get('plugin_manager')
                if pm:
                    print(Fore.CYAN + "\n=== Loaded Plugins ===")
                    if not pm.plugins:
                        print(Fore.YELLOW + "No plugins loaded.")
                    for name, meta in pm.plugins.items():
                        print(Fore.GREEN + f"- {name} (v{meta.get('version', '?')}) by {meta.get('developer', 'Unknown')}")
                        print(Fore.WHITE + f"  {meta.get('description', '')}")
                else:
                    print(Fore.RED + "Plugin Manager not initialized.")
                continue

            # @assign-task command (leader assigns task interactively)
            if user_input.strip().lower() == "@assign-task":
                if not globals().get('horizon_is_leader', False):
                    print(Fore.RED + "Only team leader can assign tasks.")
                    continue
                
                from core.horizon_online import get_client
                client = get_client()
                status = client.get_team_status()
                members = status.get('members', [])
                
                if not members:
                    print(Fore.YELLOW + "No members in team yet. Share your team code first.")
                    continue
                
                print(Fore.CYAN + "\n=== Assign Task ===")
                print(Fore.WHITE + "Select a team member:")
                for i, m in enumerate(members, 1):
                    print(Fore.GREEN + f"  {i}. {m['role']} ({m['id'][:20]}...)")
                
                member_choice = input(Fore.BLUE + f"Select member (1-{len(members)}): " + Style.RESET_ALL)
                try:
                    member_idx = int(member_choice) - 1
                    if 0 <= member_idx < len(members):
                        selected_member = members[member_idx]
                    else:
                        print(Fore.RED + "Invalid selection.")
                        continue
                except:
                    print(Fore.RED + "Invalid input.")
                    continue
                
                description = input(Fore.BLUE + "Task description: " + Style.RESET_ALL)
                task_type = input(Fore.BLUE + "Task type (code/design/research): " + Style.RESET_ALL) or "code"
                
                result = client.assign_task(selected_member['id'], description, task_type)
                if result.get("success"):
                    print(Fore.GREEN + f"\nTask assigned successfully!")
                    print(Fore.WHITE + f"  Task ID: {result.get('taskId')}")
                    print(Fore.WHITE + f"  Assigned to: {selected_member['role']}")
                    print(Fore.WHITE + f"  Description: {description}")
                    
                    task_mode = globals().get('horizon_task_mode', 'manual')
                    if task_mode == 'auto':
                        print(Fore.YELLOW + "\n[AUTO MODE] Task will be executed automatically by the member's AI.")
                else:
                    print(Fore.RED + f"Error: {result.get('error')}")
                continue


            
            # Agent Execution
            # print(Fore.MAGENTA + f"Thinking about: {user_input}...")
            
            # Initialize Agent ONCE if not already done
            if 'agent' not in locals() and 'agent' not in globals():
                 from core.input_manager import InputManager
                 input_manager = InputManager()
                 agent = get_initialized_agent(input_manager)

                 # Make agent persistent
                 globals()['agent'] = agent
                 globals()['input_manager'] = input_manager

            # Retrieve persistent instances
            agent = globals()['agent']
            input_manager = globals()['input_manager']

            # Start Blocking
            print(Fore.YELLOW + "Taking control... (Use Ctrl+Z to force stop)")
            input_manager.start_blocking()
            
            try:
                result = agent.run(user_input)
                print(Fore.GREEN + f"\nFINAL RESULT: {result}\n")
            finally:
                input_manager.stop_blocking()

        except KeyboardInterrupt:
            print(Fore.CYAN + "\nInterrupted. Exiting...")
            try: input_manager.stop_blocking()
            except: pass
            break

        except Exception as e:
            print(Fore.RED + f"An error occurred: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
