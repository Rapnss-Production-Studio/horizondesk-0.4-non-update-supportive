from core.tools import BaseTool
from core.corporation.lobbyist import lobbyist
from core.corporation.brand import brand
from core.corporation.rnd import rnd

class CheckRateLimitTool(BaseTool):
    def __init__(self):
        super().__init__("CheckRateLimit", "Checks API quota. Input: 'host'.")
    def execute(self, host=None, payload=None):
        h = host or (payload.get('host') if payload else "unknown")
        return lobbyist.negotiate_quota(h)

class GenerateAdTool(BaseTool):
    def __init__(self):
        super().__init__("GenerateAd", "Writes ad copy. Input: 'product'.")
    def execute(self, product=None, payload=None):
        p = product or (payload.get('product') if payload else "Horizon")
        return brand.generate_ad_copy(p)

class RunBenchmarkTool(BaseTool):
    def __init__(self):
        super().__init__("RunBenchmark", "Compares code. Input: 'code_a', 'code_b'.")
    def execute(self, code_a=None, code_b=None, payload=None):
        a = code_a or (payload.get('code_a') if payload else "pass")
        b = code_b or (payload.get('code_b') if payload else "pass")
        return rnd.ab_test(a, b)
