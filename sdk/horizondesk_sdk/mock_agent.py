import json
from .base import BaseTool

class MockAgent:
    """
    A lightweight, standalone agent for testing Horizon Desk plugins.
    Simulates the OmniAgent interface without external dependencies.
    """
    def __init__(self):
        self.tools = {}
        self._thought_callback = None
        self._action_callback = None
        self._observation_callback = None

    def register_tool(self, tool: BaseTool):
        """Registers a tool with the mock agent."""
        self.tools[tool.name] = tool
        print(f"[MockAgent] Tool Registered: {tool.name}")

    def run(self, prompt):
        """
        Simulates running a prompt. 
        In mock mode, we just list available tools if the prompt is 'list'.
        Otherwise, we try to match the prompt to a tool name for simple execution.
        """
        if self._thought_callback:
            self._thought_callback("MockAgent is processing your request...")

        prompt_lower = prompt.lower()
        
        if "list" in prompt_lower or "tools" in prompt_lower:
            tool_list = "\n".join([f"- {name}: {t.description}" for name, t in self.tools.items()])
            return f"I have the following tools available:\n{tool_list}"

        # Try to find a tool name in the prompt
        for name, tool in self.tools.items():
            if name.lower() in prompt_lower:
                if self._action_callback:
                    self._action_callback(name, {"data": prompt})
                
                try:
                    result = tool.execute(data=prompt)
                    if self._observation_callback:
                        self._observation_callback(result)
                    return f"Executed tool '{name}'. Result: {result}"
                except Exception as e:
                    return f"Error executing tool '{name}': {str(e)}"

        return f"MockAgent received: '{prompt}'. No specific tool matched. Available tools: {', '.join(self.tools.keys())}"
