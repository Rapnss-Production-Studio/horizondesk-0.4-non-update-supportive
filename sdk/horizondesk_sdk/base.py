from abc import ABC, abstractmethod

class BaseTool(ABC):
    """
    Base class for all Horizon Desk tools.
    Developers must inherit from this and implement 'execute'.
    """
    def __init__(self, name, description):
        self.name = name
        self.description = description

    @abstractmethod
    def execute(self, **kwargs):
        """
        The logic of the tool. 
        Args passed are typically based on the tool's description provided to the LLM.
        """
        pass

    def get_schema(self):
        """Returns the signature/schema of the tool for the LLM."""
        return f"{self.name}: {self.description}"

class HorizonPlugin(ABC):
    """
    Base class for Horizon Desk plugins.
    Handles the registration of multiple tools into the OmniAgent.
    """
    def __init__(self, name, version="1.0.0", developer="Unknown"):
        self.name = name
        self.version = version
        self.developer = developer
        self.tools = []

    def add_tool(self, tool: BaseTool):
        """Adds a tool instance to the plugin."""
        if not isinstance(tool, BaseTool):
            raise TypeError("Tool must be an instance of BaseTool")
        self.tools.append(tool)

    def register_all(self, agent):
        """Registers all plugin tools with the OmniAgent."""
        for tool in self.tools:
            agent.register_tool(tool)
