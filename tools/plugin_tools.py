from core.tools import BaseTool

class ListPluginsTool(BaseTool):
    def __init__(self, plugin_manager):
        super().__init__("ListPlugins", "Lists all installed Horizon plugins and their descriptions.")
        self.plugin_manager = plugin_manager

    def execute(self, payload=None):
        return self.plugin_manager.get_plugin_info()
