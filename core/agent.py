import re
import json
from colorama import Fore, Style
from .llm import LLMProvider

class Agent:
    def __init__(self):
        self.llm = LLMProvider()
        self.tools = {} # Map tool_name -> tool_instance
        self.history = []
        self.max_steps = 200 # Increased for Gmail Agent / Long Tasks (was 25)
        self.input_manager = None # Will be injected by main.py
        
        # Persistent Memory System to avoid repeated connection overhead/leaks
        from core.memory import MemorySystem
        self.memory_system = MemorySystem()
        
        # Real-time Hooks for SDK Workshop
        self._thought_callback = None
        self._action_callback = None
        self._observation_callback = None

    def register_tool(self, tool):
        self.tools[tool.name] = tool

    def _build_system_prompt(self):
        import os
        import platform
        import datetime
        
        cwd = os.getcwd()
        os_info = platform.system() + " " + platform.release()
        user = os.getenv('USERNAME') or os.getenv('USER') or 'User'
        home = os.path.expanduser("~")
        
        # Current Time for Scheduling/monitoring
        now = datetime.datetime.now()
        time_str = now.strftime("%Y-%m-%d %I:%M %p") # e.g. 2026-01-27 08:30 PM
        
        # OmniAgent Data Directory
        data_dir = os.path.join(os.environ.get('USERPROFILE', home), "AppData", "Local", "Omniagent")
        
        # Memory Context
        memory_context = self.memory_system.get_all_memories()
        
        # Load GUI Settings
        agent_name = self.memory_system.get_setting("agentName", "Horizon Agent")
        
        # Skill Context
        from tools.skills import skill_manager
        persona_context = skill_manager.get_system_prompt_addition()

        # Screen Resolution for Vision Context
        import pyautogui
        try:
            screen_width, screen_height = pyautogui.size()
            resolution = f"{screen_width}x{screen_height}"
        except:
            resolution = "Unknown"
        
        # Market, Search & Reddit Instructions
        market_instructions = ""
        search_instructions = ""
        reddit_instructions = ""
        try:
            from tools.market import get_market_data_instruction
            market_instructions = get_market_data_instruction()
            from tools.web import get_search_instruction
            search_instructions = get_search_instruction()
            from tools.reddit import get_reddit_instruction
            reddit_instructions = get_reddit_instruction()
        except ImportError:
            pass

        persona_context = f"{persona_context}\n{market_instructions}\n{search_instructions}\n{reddit_instructions}"

        # Team Context for Horizon Online
        team_context = ""
        import builtins
        if hasattr(builtins, 'horizon_team_code'):
            team_code = getattr(builtins, 'horizon_team_code', None)
            is_leader = getattr(builtins, 'horizon_is_leader', False)
            task_mode = getattr(builtins, 'horizon_task_mode', 'manual')
            team_members = getattr(builtins, 'horizon_team_members', [])
            
            if team_code:
                team_context = f"""
[HORIZON ONLINE TEAM]
You are part of Team {team_code}.
Your Role: {'TEAM LEADER' if is_leader else 'TEAM MEMBER'}
Task Mode: {task_mode.upper()}
"""
                if is_leader and team_members:
                    team_context += "Team Members:\n"
                    for m in team_members:
                        team_context += f"  - {m['role']} (ID: {m['id']})\n"
                    team_context += """
LEADER INSTRUCTIONS:
When given a project task, you MUST:
1. Analyze the task and create ONE subtask per team member based on their role
2. Use HorizonAssignTask tool ONCE per member with JSON: {"member_id": "<actual_member_id>", "description": "<detailed task>", "type": "code"}
3. IMPORTANT: After assigning tasks to ALL members, you MUST say "Final Answer: Tasks have been assigned to team members!" and STOP.
4. DO NOT keep assigning more tasks after the first round - assign ONCE per member then STOP.
"""
        installed_apps_context = ""
        if 'LaunchApp' in self.tools:
            app_tool = self.tools['LaunchApp']
            if hasattr(app_tool, 'apps_map'):
                if not app_tool.apps_map:
                    app_tool._cache_apps()
                app_names = list(app_tool.apps_map.keys())
                if app_names:
                    app_list = ", ".join(app_names[:150])
                    if len(app_names) > 150:
                        app_list += f", and {len(app_names) - 150} more..."
                    installed_apps_context = f"\n[Installed Applications (Can be opened via LaunchApp)]\n{app_list}\n"

        tool_descriptions = "\n".join([t.get_schema() for t in self.tools.values()])
        prompt = f"""You are **{agent_name}**, powered by the **Horizon Stack**.
System Context:
- OS: {os_info}
- Current User: {user}
- Current Time: {time_str}
- Home Directory: {home}
- OmniAgent Data Dir: {data_dir}
- Current Working Directory: {cwd}

[HORIZON PLUGINS]
{getattr(self, 'plugin_info', 'No plugins loaded.')}

[Long Term Memory]
{memory_context}

{persona_context}

{market_instructions}

{team_context}
{installed_apps_context}

### 🧠 GLOBAL CAPABILITY LAYERS (The Horizon Stack)
You are equipped with specialized layers to handle complex tasks:
1.  **Reasoning Layer** (LangChain): For complex logic and multi-step reasoning.
2.  **Knowledge Layer** (LlamaIndex + FAISS): For reading documents, indexing folders, and RAG.
3.  **Data Layer** (Pandas + NumPy): For analyzing CSVs, Excel, and extensive data crunching.
4.  **Doc Layer** (Docx + PPTX): For creating professional Word reports and PowerPoint presentations.
5.  **Vision Layer** (ResNet-50 + OpenCV): For seeing the screen and finding objects.
6.  **Automation Layer** (Playwright + Prefect): For browsing the web and scheduling tasks.

### 🛠️ TOOL USAGE PROTOCOLS
1.  **Data Analysis**: Use `AnalyzeDataTool` for CSV/Excel files. DO NOT try to read them manually.
2.  **Document Creation**: Use `CreateDocTool` or `CreatePresentationTool`.
3.  **Knowledge**: Use `AskKnowledge` to query large folders of documents.
4.  **Web Navigation**: Use `Browser*` tools (Playwright) exclusively.
5.  **Long-Term Memory**: 
    - Use `StoreMemory` to remember facts about the user (e.g. "I am busy on Tuesdays", "I like dark mode").
    - Use `SearchMemory` if you need past context not currently visible in the prompt.
    - Use `AddGoal` to track long-term tasks requested by the user.

{tool_descriptions}

### ⚠️ CRITICAL RULES (MUST FOLLOW)
1. **TERMINATION PROTOCOL**: 
   - To finish a task, you MUST use the phrase `Final Answer:` followed by your result.
   - **`Final Answer` is NOT a tool.** Do NOT say `Action: Final Answer`.
   - **`Inform` is NOT a tool.** Do NOT say `Action: Inform`.
   - If you have the answer, just say `Final Answer: <your answer>` and STOP.

2. Do NOT repeat the "Question" in your output. Start directly with "Thought".
2. Use the variables from 'System Context' (e.g., Home Directory) for file paths.
3. **Chit-Chat Protocol**: If the user says "Hi", "Hello", "Who are you", or asks a general question, DO NOT use `Type` or `LaunchApp`.
   - **CORRECT**: 
     Thought: User is greeting me.
     Final Answer: Hello! I am Omniagent v3.0. How can I help you?
   - **INCORRECT**:
     Action: LaunchApp ... (Wrong!)

4. **Web Navigation Protocol (PLAYWRIGHT)**:
   - **Preferred**: Use `Browser*` tools for all web tasks. They are faster and more reliable than `LaunchApp` + `Type`.
   - **Launch**: `BrowserOpen` (opens persistent browser).
   - **Navigate**: `BrowserNavigate` "https://google.com".
   - **Interact**: 
     - `BrowserType` (selector="input[name='q']", text="query")
     - `BrowserClick` (selector="button.submit")
     - `BrowserScroll` (direction="down")
   - **Scrape**: `BrowserScrape` (type="text")
   - **Screenshot**: `BrowserScreenshot`
   - **Fallback**: NONE. Do NOT use `LaunchApp` for the browser. `BrowserOpen` handles the persistent profile.
     - **INCORRECT**: `LaunchApp` "chrome" (This opens a guest profile! STOP!)
     
5. **Vision Protocol ("Ask for Screenshot")**:
   - You have `LocateObject` (Grid Search) and `AnalyzeImage` (Full Screen).
   - **Rule**: DO NOT take a screenshot unless:
     a) The user explicitly asks ("take a screenshot", "verify with vision").
     b) You are in "Interactive Navigation" mode and need to find a button to click.
   - **Grid Search**: Use `LocateObject` to find coordinates of generic objects (e.g. "submit button").

5. **Error Handling Protocol**:
   - If an Observation is "Error...", **DO NOT** say "Final Answer". You must try to fix it or ask the user.
   - Example observation: "Error typing: PyAutoGUI fail-safe..." -> Thought: I moved the mouse too fast. I should try again carefully.

6. **Typing Protocol**:
   - ONLY use the `Type` tool if the user explicitly asks you to write code, email, or text *into an application*.
   - NEVER use `Type` to communicate with the user. Use "Final Answer" for that.

7. **JSON Formatting Rules**:
   - **NO MATH**: Do not use expressions like `0.5 * 1920`. Calculate the value yourself! (e.g., `960`).
   - **Integers Only**: For coordinates, use integers.
   - **Strict JSON**: Ensure valid JSON syntax.

8. **Communication Protocol**:
   - **Before sending emails or scheduling meetings**:
     - Check if the user specified a platform (Gmail vs Outlook).
     - If NOT specified, **ASK**: "Which email platform should I use? (Gmail or Outlook)"
   
   - **Gmail Protocol (Example Flow)**:
     - **Step 1 (Open)**:
       Thought: I need to open Gmail with the draft.
       Action: BrowserOpen
       Action Input: {{"url": "https://mail.google.com/mail/?view=cm&fs=1&to=<EMAIL>&su=<SUBJECT>&body=<BODY>"}}
     - **Step 2 (Wait)**:
       Action: Wait
       Action Input: {{"seconds": 10}}
     - **Step 3 (Send)**:
       Action: PressKey
       Action Input: {{"key": "ctrl+enter"}}
     - **Step 4 (Finish)**:
       Final Answer: Email sent.
     - **Auth Check**: If redirected to login, STOP and ask user to login manually.
   
   - **Interactive Login Protocol (CRITICAL)**:
     - If the user says "Let me log in", "I want to login", or "Open browser":
     - 0. **PRE-CHECK**: Warn the user: "Please close all existing Chrome windows first, or I cannot access your main profile."
     - 1. **Open Browser**: Use `BrowserOpen` with url="https://accounts.google.com"
     - 2. **STOP**: Do NOT type email. Do NOT type password. Do NOT click.
     - 3. **Wait**: Use `Wait` with seconds=5 to ensure it loads.
     - 4. **Final Answer**: "Browser is open with your MAIN profile. Please log in manually. Tell me when you are done."
     - **NEVER** try to automate the login page unless explicitly given credentials in the prompt.

   - **Canva MCP Protocol (Presentation/Post)**:
     - **Rule**: ALWAYS check connection before creating content.
     - **Step 1 (Check)**:
       Action: CheckCanvaMCP
     - **Step 2 (Branch)**:
       - **If "Not Connected"**:
         - Thought: Canva MCP is not connected. I need to set it up.
         - Action: BrowserOpen with {{"url": "https://www.canva.com/"}} (Simulate setup).
         - Action: CreateCanvaMCPConnection with {{"api_key": "simulated_key"}}
         - Action: CreateCanvaPresentation with {{"topic": "<TOPIC>", "slides": ["Slide 1", "Slide 2"]}}
       - **If "Connected"**:
         - Thought: Canva MCP is connected. I can create the presentation directly.
         - Action: CreateCanvaPresentation with {{"topic": "<TOPIC>", "slides": ["Slide 1", "Slide 2"]}}

9. **Task Completion Protocol (CRITICAL)**:
   - **NO REPORTING TOOLS**: Do NOT use `Type`, `Inform`, `Report`, or `Final Answer` as tools.
   - **JUST SAY IT**: To finish, output "Final Answer:" followed by your report.
   - **Final Answer is NOT a tool**. It is a special ending keyword.
   - **CORRECT**:
     Observation: File created.
     Thought: The task is done.
     Final Answer: I have created the file successfully.
   - **INCORRECT**:
     Action: Use the 'Final Answer' tool... (WRONG!)
     Action: Inform the user... (WRONG!)
   - **CORRECT**: After saving a file:
     Thought: The file has been saved successfully.
     Final Answer: I have created the file "states_and_capitals.html" on your Desktop. You can open it in Chrome and print to PDF.
   - **INCORRECT**: Just stopping without a Final Answer after completing actions.

10. **Local File vs Web URL Protocol**:
    - For **web URLs** (e.g., `https://google.com`): Use `OpenBrowserUrl` directly.
    - For **local files** (e.g., `C:/Users/.../file.html`): Use `OpenBrowserUrl` - it will handle the conversion to `file://` format automatically.
    - Do NOT manually construct `file:///` URLs with `%20` or URI encoding - the tool handles this.

11. **Code Creation Protocol (CRITICAL)**:
    - When asked to create a Python script, program, or any code file:
      1. **ALWAYS use `WriteFile`** to create the file directly. Do NOT launch an IDE.
      2. **NEVER use `Type`** to type code into an editor - this is unreliable and slow.
      3. Use escaped newlines (\\n) in the content for multi-line code.
      4. After writing, inform user of the file path and how to run it.
    - **CORRECT**: `WriteFile` with path and full code content.
    - **INCORRECT**: `LaunchApp` to open an IDE, then `Type` to write code.

12. **App Launch Error Handling**:
    - After `LaunchApp`, carefully check the Observation.
    - If Observation contains "cannot find" or "not found", the app is NOT installed.
    - Do NOT proceed as if the app launched successfully.
    - **CORRECT**: "The application 'pycharm' is not installed. Would you like me to try a different approach?"
    - **INCORRECT**: Continuing to `Type` into a non-existent window.

13. **Path Handling with Spaces (CRITICAL)**:
    - Windows paths often contain spaces (e.g., "Aarav Kushwaha" in the username).
    - When using `RunCommand`, ALWAYS wrap paths in double quotes.
    - **CORRECT**: `mkdir "C:/Users/Aarav Kushwaha/Desktop/game"`
    - **INCORRECT**: `mkdir C:/Users/Aarav Kushwaha/Desktop/game` (breaks at space!)
    - For WriteFile, use the `Home Directory` variable from System Context: `{home}/Desktop/myfile.py`

14. **Folder vs File Creation (CRITICAL)**:
    - **To create a FOLDER**: Use `RunCommand` with `mkdir "path/to/folder"`
    - **To create a FILE**: Use `WriteFile` with path and content
    - `WriteFile` creates FILES, not folders! Do NOT use it to make directories.
    - **CORRECT folder creation**: RunCommand with command: mkdir "C:/Users/Username/Desktop/Game"
    - **INCORRECT**: `WriteFile` with an empty content to "create a folder"

15. **ANTI-HALLUCINATION RULES (STRICT)**:
    - **NO TASK IDs**: Do NOT invent "Task IDs", do NOT create "task_id.txt" files, do NOT create folders to track tasks unless the user EXPLICITLY asks.
    - **NO LOOPING**: If an action fails twice, STOP and ask the user. Do not loop infinitely.
    - **BROWSER AUTOMATION vs VIEWING**: 
      - If asked to simply "open a link" or "show me a page" in the default browser, use `OpenBrowserUrl`. This is fast and uses the user's default browser profile without locking it.
      - If asked to **manage, automate, read, or interact** with websites (e.g., Instagram, Facebook, LinkedIn, Media, Presentations), you MUST use Playwright tools (`BrowserOpen`, `BrowserClick`, `BrowserType`, `BrowserNavigate`). You have the power to fully automate these tasks!
    
    - **WRITING vs TYPING (CRITICAL)**:
      - **WriteFile**: Use ONLY for creating background files, scripts, or data (e.g., "Create a python script", "Save these results to a txt file").
      - **Type**: Use ONLY for interacting with active UI applications like Notepad, Word, or Browser inputs (e.g., "Open notepad and write...", "Type 'Hello' into the browser").
      - **RULE**: If you just used `LaunchApp`, you should almost ALWAYS use `Type` or `Keyboard` next to interact with it. Do NOT use `WriteFile` to write into an app you just opened.

16. **Video Editing Protocol (VideoEditorTool)**:
    - You can now edit video files programmatically using `VideoEditorTool`.
    - **Available Tasks**:
      - `cut`: Cut a clip from start/end seconds. Input: `{{"task":"cut","input_paths":["C:/path/video.mp4"],"output_path":"C:/path/output.mp4","start_time":0,"end_time":30}}`
      - `concatenate`: Stitch multiple videos together. Input: `{{"task":"concatenate","input_paths":["C:/vid1.mp4","C:/vid2.mp4"],"output_path":"C:/merged.mp4"}}`
      - `add_text`: Overlay text over a video. Input: `{{"task":"add_text","input_paths":["C:/vid.mp4"],"output_path":"C:/with_text.mp4","text":"Intro Title","fontsize":60,"color":"white"}}`
    - **Rules**:
      - ALWAYS verify the input path exists by using `ListDirectory` or asking the user first.
      - ALWAYS use full absolute paths (e.g. `C:/Users/Aarav Kushwaha/Videos/raw.mp4`).
      - Output file should be in the same folder as input unless user specifies otherwise.
      - After success, report the output file path clearly so the user can find it.

Use the following format:

Thought: you should always think about what to do
Action: the action to take, should be one of [{', '.join(self.tools.keys())}]
Action Input: the input to the action (json format preferred needed)
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!
"""
        return prompt

    def run(self, user_input):
        print(Fore.GREEN + f"Agent assigned task: {user_input}")
        self.history.append(f"Question: {user_input}")
        
        step_count = 0
        while step_count < self.max_steps:
            system_prompt = self._build_system_prompt()
            
            # --- TOKEN MANAGEMENT (Sliding Window) ---
            # Keep only the last 3-5 turns of history + the original question
            # This prevents the context from exploding > 3k tokens.
            context_window = self.history[-6:] if len(self.history) > 6 else self.history[:]
            if len(self.history) > 3:
                # Always include the original question at the start if truncated
                if not context_window[0].startswith("Question:"):
                     context_window.insert(0, f"Question: {user_input}")
            
            full_prompt = "\n".join(context_window) + "\n"

            # UPDATE OVERLAY STATUS
            if hasattr(self, 'input_manager') and self.input_manager:
                 self.input_manager.update_status("Thinking...", "Analyzing context...")
            
            # Call LLM
            response = self.llm.generate_text(full_prompt, system_prompt=system_prompt)
            if not response:
                return "Error: LLM failed to respond."
            
            original_response = response # Save for checking Final Answer later
            
            # Sanitize response: Remove "Question: ..." if the LLM hallucinated it
            response = re.sub(r"^Question:.*$", "", response, flags=re.MULTILINE).strip()
            
            print(Fore.MAGENTA + f"\n[LLM Response]:\n{response}\n")
            
            # Parse Response
            # The LLM sometimes hallucinates the entire flow (Action -> Observation -> Final Answer) in one go
            # if the Cloudflare worker 'stop' parameter fails.
            # We MUST check for an Action first. If an Action exists, we execute it and ignore any
            # hallucinated observation or final answer that comes after it.
            
            action_match = re.search(r"Action:\s*(.*?)\n", response)
            
            if action_match:
                action = action_match.group(1).strip()
                
                # Get everything after the *first* "Action Input:"
                parts = response.split("Action Input:")
                if len(parts) > 1:
                    raw_input = parts[1].strip()
                    
                    # STRICT TRUNCATION:
                    # Cut off any hallucinated content after the action input
                    action_input_str = raw_input
                    for terminator in ["Observation:", "Action:", "Thought:", "Final Answer:"]:
                        if terminator in action_input_str:
                            action_input_str = action_input_str.split(terminator)[0].strip()

                    # Reconstruct the clean step for display/logging
                    step_thought = response.split("Action:")[0].strip()
                    response = f"{step_thought}\nAction: {action}\nAction Input: {action_input_str}"
                    
                    print(Fore.YELLOW + f"Attempting Action: {action}")
                    
                    # WORKSHOP HOOK
                    if self._thought_callback: self._thought_callback(step_thought)
                    if self._action_callback: self._action_callback(action, action_input_str)

                    # UPDATE OVERLAY STATUS
                    if hasattr(self, 'input_manager') and self.input_manager:
                         self.input_manager.update_status(f"Executing: {action}", "Processing...")
                
                print(Fore.YELLOW + f"Attempting Action: {action} with Input: {action_input_str}")
                
                # INTERCEPT HALLUCINATIONS
                if action.lower() in ["final answer", "inform", "report"]:
                    print(Fore.GREEN + "Intercepted hallucinated tool call. Terminating.")
                    # self.history.append(response) # MOVED BELOW
                    # If it's a dict, get the text/message
                    if "{" in action_input_str:
                        try:
                            data = json.loads(action_input_str)
                            result_text = data.get("text") or data.get("message") or action_input_str
                        except:
                            result_text = action_input_str
                    else:
                        result_text = action_input_str
                    
                    self.history.append(f"{step_thought}\nFinal Answer: {result_text}")
                    return result_text

                if action not in self.tools:
                    observation = f"Error: Tool '{action}' not found. Please try to answer without using this tool if possible, or use a different tool."
                else:
                    try:
                        # Try to parse input as JSON, otherwise pass as string
                        # This works for simple string inputs too if quotes are handled, but specific tools might need robust parsing
                        # Parse Input first
                        action_input = None
                        try:
                            # Try to parse as valid JSON first
                            if "{" in action_input_str:
                                try:
                                    # Strip comments (formatted as # comment or // comment) before parsing
                                    # Regex to remove # or // at end of lines or lines starting with them
                                    clean_json = re.sub(r"//.*|#.*", "", action_input_str)
                                    action_input = json.loads(clean_json)
                                except json.JSONDecodeError:
                                    # Fallback 1: Fix Windows paths (single backslash to double)
                                    clean_json = re.sub(r"//.*|#.*", "", action_input_str)
                                    fixed_json = clean_json.replace("\\", "\\\\")
                                    try:
                                        action_input = json.loads(fixed_json)
                                    except json.JSONDecodeError:
                                        # Fallback 2: Handle literal newlines/tabs in content
                                        # Escape control characters INSIDE string values
                                        import codecs
                                        escaped_json = clean_json.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
                                        try:
                                            action_input = json.loads(escaped_json)
                                        except json.JSONDecodeError:
                                            # Final fallback: pass as raw string to tool
                                            action_input = action_input_str
                            else:
                                action_input = action_input_str # Keep as string if not JSON
                        except Exception as e:
                            # If all parsing fails, treat as raw string (though this might break tools needing dicts)
                            action_input = action_input_str
                            print(Fore.RED + f"[Debugger] JSON Parsing failed, using raw string: {e}")

                        try:
                            # Execute Tool (Temporarily unlocking if manager exists)
                            if hasattr(self, 'input_manager') and self.input_manager and action in ['MouseClick', 'Type', 'PressKey', 'LaunchApp']:
                                # Prepare payload for tools that expect 'payload' or specific keys
                                if isinstance(action_input, dict):
                                    observation = self.input_manager.temporarily_unlock_for_action(self.tools[action].execute, **action_input)
                                else:
                                    observation = self.input_manager.temporarily_unlock_for_action(self.tools[action].execute, payload=action_input)
                            else:
                                # Normal execution
                                if isinstance(action_input, dict):
                                    observation = self.tools[action].execute(**action_input)
                                else:
                                    observation = self.tools[action].execute(payload=action_input)
                                    
                        except Exception as e:
                             observation = f"Error executing tool: {e}"
                    except Exception as e:
                        observation = f"Error: {e}"

                # WORKSHOP HOOK
                if self._observation_callback: self._observation_callback(observation)
                # Truncate observation if too long to save tokens
                obs_to_save = observation
                if isinstance(observation, str) and len(observation) > 2000:
                    obs_to_save = observation[:2000] + "\n... [TRUNCATED FOR CONTEXT WINDOW] ..."
                    print(Fore.YELLOW + f"[LLM] Observation truncated from {len(observation)} to 2000 chars.")

                # Append to history
                step_str = f"{response}\nObservation: {obs_to_save}\n"
                self.history.append(step_str)
                
                # Check for "Final Answer" in the ORIGINAL hallucinatory response
                # If the LLM already thought it was done, we should respect that 
                # AFTER performing the action it requested.
                if "Final Answer:" in original_response:
                    final_answer = original_response.split("Final Answer:")[-1].strip()
                    print(Fore.GREEN + f"Final Answer detected in same turn as Action. Terminating.")
                    
                    # Log the final state
                    self.history.append(f"Thought: Task completed after action.\nFinal Answer: {final_answer}")
                    
                    if hasattr(self, 'input_manager') and self.input_manager:
                         self.input_manager.update_status("Task Completed", "Done.")
                    return final_answer
                     
            else:
                # If no action found, check for Final Answer
                if "Final Answer:" in response:
                    final_answer = response.split("Final Answer:")[-1].strip()
                    self.history.append(response)
                    
                    # UPDATE OVERLAY STATUS
                    if hasattr(self, 'input_manager') and self.input_manager:
                         self.input_manager.update_status("Task Completed", "Waiting for input...")
                         
                    return final_answer
                    
                # If no action and no final answer, usually the LLM is just chatting or failed format.
                print(Fore.RED + "Agent did not output an action. Ending turn.")
                self.history.append(response)
                return response
            
            step_count += 1
        
        return "Max steps reached."
