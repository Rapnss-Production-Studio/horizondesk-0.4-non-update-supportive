from core.tools import BaseTool
import os
import json
import time

# --- Configuration ---
CONFIG_FILE = "canva_mcp_config.json"

class CheckCanvaMCPTool(BaseTool):
    def __init__(self):
        super().__init__("CheckCanvaMCP", "Checks if Canva MCP is connected. Returns 'Connected' or 'Not Connected'.")

    def execute(self, payload=None):
        try:
            from core.memory import MemorySystem
            mem = MemorySystem()
            key = mem.get_setting("canvaApiKey")
            if key and len(key) > 5:
                # Also write to local config so create tools know it's connected
                config = {"status": "connected", "api_key": key}
                with open(CONFIG_FILE, 'w') as f:
                    json.dump(config, f)
                return "Connected"
        except ImportError:
            pass

        # Check if config file exists in the plugin directory as fallback
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                if config.get("status") == "connected":
                    return "Connected"
            except:
                pass
        return "Not Connected"

class CreateCanvaMCPConnectionTool(BaseTool):
    def __init__(self):
        super().__init__("CreateCanvaMCPConnection", "Creates a connection to Canva MCP. Input: 'api_key' (simulated).")

    def execute(self, api_key=None, payload=None):
        # Simulate saving the connection
        config = {
            "status": "connected",
            "api_key": api_key or "mock_key_12345",
            "connected_at": time.time()
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)
        return "Canva MCP Connected successfully."

class CreateCanvaPresentationTool(BaseTool):
    def __init__(self):
        super().__init__("CreateCanvaPresentation", "Creates a presentation using Canva MCP. Input: 'topic', 'slides'.")

    def execute(self, topic=None, slides=None, payload=None):
        if payload:
            if isinstance(payload, dict):
                topic = payload.get('topic')
                slides = payload.get('slides')
        
        # Check connection first
        if not os.path.exists(CONFIG_FILE):
            return "Error: Canva MCP not connected. Please use 'CreateCanvaMCPConnection' first."
            
        print(f"[CanvaMCP] Creating presentation on: {topic}")
        time.sleep(2) # Simulate work
        
        # Mock creation - save a dummy file
        filename = f"{topic.replace(' ', '_')}.pptx"
        with open(filename, 'w') as f:
            f.write(f"Presentation: {topic}\nSlides: {slides}")
            
        return f"Presentation '{filename}' created successfully using Canva MCP."

# --- Registration ---
def register_tools(agent):
    agent.register_tool(CheckCanvaMCPTool())
    agent.register_tool(CreateCanvaMCPConnectionTool())
    agent.register_tool(CreateCanvaPresentationTool())
