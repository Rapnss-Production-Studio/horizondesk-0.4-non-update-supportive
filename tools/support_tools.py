from core.tools import BaseTool
from core.corporation.support import support

class ConsultKnowledgeBaseTool(BaseTool):
    def __init__(self):
        super().__init__("ConsultKB", "Searches the support database. Input: 'query'.")

    def execute(self, query=None, payload=None):
        q = query or (payload.get('query') if payload else None)
        if not q: return "Query required."
        return support.query_kb(q)
