# OmniAgent v3.0 Plugin API Documentation

Welcome to the OmniAgent Plugin Ecosystem! This guide will show you how to build custom plugins to extend the capabilities of the Horizon Desk AI, swap inference engines, or script complex automation flows.

## How Plugins Work

OmniAgent loads plugins dynamically on startup from the `plugins/` directory. Each plugin must define Python classes inheriting from `BaseTool` and register them via a `register_tools` function.

### Core Anatomy of a Plugin

Create a directory (e.g., `plugins/MyPlugin/`) and inside it, create a `main.py` file:

```python
from core.tools import BaseTool
import json
import time

class MyCustomTool(BaseTool):
    def __init__(self):
        # 1. Name: How the LLM calls the tool. Must be alphanumeric (no spaces).
        # 2. Description: Tells the LLM *when* and *how* to use this tool, and what arguments it expects in JSON.
        super().__init__("MyCustomTool", "Does a specific task. Input MUST be valid JSON: {'message': 'Hello'}")

    def execute(self, payload=None, **kwargs):
        """
        The execution logic. The LLM will pass arguments either via kwargs (if parsed) 
        or raw string payload. Always handle both gracefully.
        """
        try:
            # Handle parsed JSON kwargs
            if kwargs and 'message' in kwargs:
                msg = kwargs['message']
            # Fallback to payload dict/string
            elif isinstance(payload, dict):
                msg = payload.get('message', 'Default')
            elif isinstance(payload, str):
                data = json.loads(payload)
                msg = data.get('message', 'Default')
            else:
                msg = "No message provided."
                
            print(f"[MyPlugin] executing with: {msg}")
            time.sleep(1) # Simulate work
            
            # The return string becomes the "Observation" for the LLM
            return f"Success! Executed task with message: {msg}"
            
        except Exception as e:
            return f"Error executing tool: {e}"

# Registration hook called by HorizonApi
def register_tools(agent):
    agent.register_tool(MyCustomTool())
```

---

## Cookbook: Common Architectures

### 1. Swapping AI Inference (Local LLM Plugin)

By default, OmniAgent uses the Cloudflare AI Gateway (e.g., Gemini 2.0 Flash). You can create a "System Overrider" plugin to hijack the `generate_text` method in the core agent if you want to use Local LLMs via LM Studio or Ollama.

```python
# plugins/LocalInferenceProvider/main.py
from core.tools import BaseTool
import requests
import json

class RouteToLocalLLMTool(BaseTool):
    def __init__(self):
        super().__init__("RouteToLocalLLM", "Sends a prompt to a local Ollama instance instead of cloud.")

    def execute(self, prompt=None, payload=None):
        if not prompt and isinstance(payload, dict):
            prompt = payload.get('prompt')

        url = "http://127.0.0.1:11434/api/generate"
        data = {
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
        
        response = requests.post(url, json=data)
        if response.status_code == 200:
            return f"Local LLM Response: {response.json().get('response')}"
        return "Error connecting to local LLM."

def register_tools(agent):
    agent.register_tool(RouteToLocalLLMTool())
```

### 2. Schedulers & Background Tasks

Plugins can spawn background daemon threads to execute autonomous tasks even when the user isn't typing in the Horizon GUI chat.

```python
# plugins/BackgroundCron/main.py
from core.tools import BaseTool
import threading
import time

class BackgroundTaskTool(BaseTool):
    def __init__(self):
        super().__init__("StartBackgroundTask", "Schedules a task. Input: {'minutes': 5}")

    def execute(self, payload=None, **kwargs):
        minutes = kwargs.get('minutes', 5)
        
        def run_later():
            print(f"[Cron] Waiting {minutes} minutes...")
            time.sleep(minutes * 60)
            print("[Cron] Executing delayed autonomous action!")
            # Note: Do not write to GUI state directly from here, push to a log file
            # or use the memory database to queue an alert.
            
        thread = threading.Thread(target=run_later, daemon=True)
        thread.start()
        
        return f"Successfully scheduled task to run in {minutes} minutes."

def register_tools(agent):
    agent.register_tool(BackgroundTaskTool())
```

### 3. PC-Phone Connectivity Bridge

To trigger actions on the user's mobile device, you can write a plugin that communicates with a local websocket server or push notification service.

```python
# plugins/PhoneBridge/main.py
from core.tools import BaseTool
import requests

class SendToPhoneTool(BaseTool):
    def __init__(self):
        super().__init__("SendToPhone", "Pushes an alert or link to the user's Rapnss mobile app.")

    def execute(self, message=None, link=None, **kwargs):
        msg = message or kwargs.get('message', 'Default Notification')
        # Here you would call your backend endpoint that triggers FCM/APNS to the device token
        url = "https://your-backend.com/api/notify"
        
        try:
            res = requests.post(url, json={"body": msg, "action_link": link})
            return f"Push notification requested: {res.status_code}"
        except Exception as e:
            return f"Network error: {e}"

def register_tools(agent):
    agent.register_tool(SendToPhoneTool())
```

## Security Best Practices
- **Never hardcode secrets**: Use the `MemorySystem().get_setting('my_api_key')` API to read credentials safely from the GUI configuration, rather than keeping plaintext keys in the python files. 
- **Graceful Failures**: If a user does not have a dependency installed, handle the `ImportError` gracefully at the top of the file and do not crash the `register_tools` loading sequence.
