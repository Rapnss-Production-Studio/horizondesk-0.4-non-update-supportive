from core.tools import BaseTool
from core.corporation.spy import date_spy

class AnalyzeCompetitorTool(BaseTool):
    def __init__(self):
        super().__init__("AnalyzeCompetitor", "Scans a rival URL. Input: 'url'.")

    def execute(self, url=None, payload=None):
        u = url or (payload.get('url') if payload else None)
        if not u: return "URL required."
        return date_spy.analyze_target(u)
