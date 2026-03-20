from horizondesk_sdk import BaseTool, HorizonPlugin

class MyCustomTool(BaseTool):
    def __init__(self):
        super().__init__("TestPluginTool", "Does something amazing. Input: 'data'.")

    def execute(self, data=None, payload=None):
        val = data or (payload.get('data') if isinstance(payload, dict) else payload)
        return f"[Plugin] Processed: {val}"

def register_tools(agent):
    plugin = HorizonPlugin("TestPlugin")
    plugin.add_tool(MyCustomTool())
    plugin.register_all(agent)
