from core.tools import BaseTool
from core.knowledge_base import KnowledgeBase
import os

kb = KnowledgeBase()

class LearnTool(BaseTool):
    def __init__(self):
        super().__init__("Learn", "Ingests text or a file into the Knowledge Base. Input: 'title', 'content' OR 'file_path'.")

    def execute(self, title=None, content=None, file_path=None, payload=None):
        if payload and isinstance(payload, dict):
            title = payload.get('title')
            content = payload.get('content')
            file_path = payload.get('file_path')
            
        # Handle file mode
        if file_path:
            valid_path = file_path.replace('"', '').strip()
            if os.path.exists(valid_path):
                try:
                    with open(valid_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    if not title:
                        title = os.path.basename(valid_path)
                except Exception as e:
                    return f"Error reading file: {e}"
            else:
                return f"File not found: {valid_path}"

        if not title or not content:
            return "Error: Title and Content (or valid file_path) required."

        return kb.learn_content(title, content)

class QueryKBTool(BaseTool):
    def __init__(self):
        super().__init__("QueryKnowledge", "Searches the Knowledge Base. Input: 'query'.")

    def execute(self, query=None, payload=None):
        q = query or (payload.get('query') if payload else None)
        if not q: return "Error: Query required."
        
        return kb.query(q)
