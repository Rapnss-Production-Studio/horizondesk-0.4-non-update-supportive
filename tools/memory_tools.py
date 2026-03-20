from core.tools import BaseTool
from core.memory import MemorySystem

# Global Memory Instance
memory_system = MemorySystem()

class RememberTool(BaseTool):
    def __init__(self):
        super().__init__("Remember", "Stores a fact in long-term memory. Input: 'key', 'value'. E.g. key='user_name', value='Aarav'")

    def execute(self, key=None, value=None, payload=None):
        k = key
        v = value
        
        if payload and isinstance(payload, dict):
            k = payload.get('key')
            v = payload.get('value')
            
        if not k or not v:
             return "Error: Key and Value required."
             
        return memory_system.add_memory(k, v)

class RecallTool(BaseTool):
    def __init__(self):
        super().__init__("Recall", "Retrieves information from memory. Input: 'query' (search term) or 'all' (list everything).")

    def execute(self, query=None, payload=None):
        q = query
        if payload and isinstance(payload, dict):
            q = payload.get('query')
        elif payload:
            q = payload
            
        if not q:
            return memory_system.get_all_memories()
            
        if str(q).lower() == 'all':
            return memory_system.get_all_memories()
            
        return memory_system.search_memory(str(q))
