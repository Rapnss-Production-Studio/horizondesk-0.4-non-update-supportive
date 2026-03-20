
from core.tools import BaseTool
from core.capabilities import capability_manager

class AnalyzeDataTool(BaseTool):
    def __init__(self):
        super().__init__("AnalyzeData", "Analyzes CSV data using Pandas. Input: JSON 'filepath', 'query'.")

    def execute(self, filepath=None, query=None, payload=None):
        if payload:
            if isinstance(payload, dict):
                filepath = payload.get('filepath')
                query = payload.get('query')
            elif isinstance(payload, str):
                import json
                import re
                try:
                    # Find first { and last }
                    match = re.search(r"\{.*\}", payload, re.DOTALL)
                    if match:
                        data = json.loads(match.group(0))
                        filepath = data.get('filepath')
                        query = data.get('query')
                except: pass
        
        if not filepath: return "Error: Filepath required."
        
        layer = capability_manager.load_layer("DataLayer")
        if not layer: return "Error: DataLayer failed to load. Are libraries installed?"
        
        try:
            return layer.analyze_csv(filepath, query)
        except Exception as e:
            return f"Error analyzing data: {e}"

class CreateDocTool(BaseTool):
    def __init__(self):
        super().__init__("CreateDoc", "Creates a Word Document. Input: JSON 'filename', 'content'.")

    def execute(self, filename=None, content=None, payload=None):
        if payload:
            if isinstance(payload, dict):
                filename = payload.get('filename')
                content = payload.get('content')
            elif isinstance(payload, str):
                import json
                import re
                try:
                    match = re.search(r"\{.*\}", payload, re.DOTALL)
                    if match:
                        data = json.loads(match.group(0))
                        filename = data.get('filename')
                        content = data.get('content')
                except: pass
        
        if not filename or not content: return "Error: Filename and content required."
        
        layer = capability_manager.load_layer("DocLayer")
        if not layer: return "Error: DocLayer failed to load."
        
        try:
            return layer.create_word_doc(filename, content)
        except Exception as e:
            return f"Error creating doc: {e}"

class CreatePresentationTool(BaseTool):
    def __init__(self):
        super().__init__("CreatePresentation", "Creates a PowerPoint. Input: JSON 'filename', 'title', 'content_list'.")

    def execute(self, filename=None, title=None, content_list=None, payload=None):
        if payload:
            if isinstance(payload, dict):
                filename = payload.get('filename')
                title = payload.get('title')
                content_list = payload.get('content_list')
            elif isinstance(payload, str):
                import json
                import re
                try:
                    match = re.search(r"\{.*\}", payload, re.DOTALL)
                    if match:
                        data = json.loads(match.group(0))
                        filename = data.get('filename')
                        title = data.get('title')
                        content_list = data.get('content_list')
                except: pass
        
        if not filename: return "Error: Filename required."
        
        layer = capability_manager.load_layer("DocLayer")
        if not layer: return "Error: DocLayer failed to load."
        
        try:
            return layer.create_ppt(filename, title or "New Presentation", content_list)
        except Exception as e:
            return f"Error creating presentation: {e}"

class AskKnowledgeTool(BaseTool):
    def __init__(self):
        super().__init__("AskKnowledge", "Queries local knowledge base (RAG). Input: JSON 'query', 'folder_path'.")

    def execute(self, query=None, folder_path=None, payload=None):
        if payload:
            if isinstance(payload, dict):
                query = payload.get('query')
                folder_path = payload.get('folder_path')
            elif isinstance(payload, str):
                import json
                import re
                try:
                    match = re.search(r"\{.*\}", payload, re.DOTALL)
                    if match:
                        data = json.loads(match.group(0))
                        query = data.get('query')
                        folder_path = data.get('folder_path')
                except: pass
        
        if not query or not folder_path: return "Error: Query and folder_path required."
        
        layer = capability_manager.load_layer("KnowledgeLayer")
        if not layer: return "Error: KnowledgeLayer failed to load. Heavy AI libs missing?"
        
        try:
            # For demo, we assume index is created on fly. In prod, cache this.
            index = layer.index_folder(folder_path)
            return layer.query_index(index, query)
        except Exception as e:
            return f"Error querying knowledge: {e}"

class ScheduleMeetingTool(BaseTool):
    def __init__(self):
        super().__init__("ScheduleMeeting", "Creates a generic Google Meet link instantly. Input: None.")

    def execute(self, payload=None):
        # We use Playwright to automate the 'instant meeting' flow
        from tools.playwright_tool import PlaywrightManager
        import time
        import re
        
        manager = PlaywrightManager()
        page = manager.ensure_active()
        
        try:
            print("[ScheduleMeeting] Navigating to meet.google.com/new...")
            page.goto("https://meet.google.com/new", timeout=30000)
            
            # Wait for meeting to load. The URL usually redirects to meet.google.com/abc-defg-hij
            # We can just grab the URL after a few seconds or wait for a specific element
            page.wait_for_load_state("networkidle")
            time.sleep(3) # Safety buffer for redirects
            
            current_url = page.url
            if "meet.google.com" in current_url and "/new" not in current_url:
                return f"Meeting created successfully. Link: {current_url}"
            else:
                # Fallback: Try to scrape the 'copy link' box if URL didn't update (rare)
                # But usually /new redirects to the meeting room.
                return f"Meeting page loaded. Current URL: {current_url}"

        except Exception as e:
            return f"Error creating meeting: {e}"

class StoreMemoryTool(BaseTool):
    def __init__(self):
        super().__init__("StoreMemory", "Stores important facts, preferences, or knowledge in long-term memory. Input: JSON 'topic', 'content'.")

    def execute(self, topic=None, content=None, payload=None):
        if payload:
            if isinstance(payload, dict):
                topic = payload.get('topic')
                content = payload.get('content')
            elif isinstance(payload, str):
                import json
                import re
                try:
                    match = re.search(r"\{.*\}", payload, re.DOTALL)
                    if match:
                        data = json.loads(match.group(0))
                        topic = data.get('topic')
                        content = data.get('content')
                except:
                    pass

        if not topic or not content:
            return "Error: Topic and content are required."

        from core.memory import MemorySystem
        try:
            mem_sys = MemorySystem()
            return mem_sys.add_memory(topic, content)
        except Exception as e:
            return f"Error storing memory: {e}"

class SearchMemoryTool(BaseTool):
    def __init__(self):
        super().__init__("SearchMemory", "Searches long-term memory for specific past facts or context. Input: JSON 'query'.")

    def execute(self, query=None, payload=None):
        if payload:
            if isinstance(payload, dict):
                query = payload.get('query')
            elif isinstance(payload, str):
                query = payload # Basic fallback for single string input

        if not query:
            return "Error: Query is required."

        from core.memory import MemorySystem
        try:
            mem_sys = MemorySystem()
            return mem_sys.search_memory(query)
        except Exception as e:
            return f"Error searching memory: {e}"

class AddGoalTool(BaseTool):
    def __init__(self):
        super().__init__("AddGoal", "Adds a short or long-term goal for the user to track. Input: JSON 'goal_description'.")

    def execute(self, goal_description=None, payload=None):
        if payload:
            if isinstance(payload, dict):
                goal_description = payload.get('goal_description')
            elif isinstance(payload, str):
                goal_description = payload # Fallback

        if not goal_description:
            return "Error: Goal description is required."

        from core.memory import MemorySystem
        try:
            mem_sys = MemorySystem()
            return mem_sys.add_goal(goal_description)
        except Exception as e:
            return f"Error adding goal: {e}"
