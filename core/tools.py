from abc import ABC, abstractmethod

class BaseTool(ABC):
    def __init__(self, name, description):
        self.name = name
        self.description = description

    @abstractmethod
    def execute(self, **kwargs):
        pass

    def get_schema(self):
        """Returns the signature/schema of the tool for the LLM."""
        return f"{self.name}: {self.description}"
