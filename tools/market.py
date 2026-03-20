from core.tools import BaseTool
import requests
import os

class AlphaVantageTool(BaseTool):
    def __init__(self):
        super().__init__("AlphaVantage", "Fetches real-time market data (stocks, commodities, forex) using Alpha Vantage API. Input: JSON with 'function' (e.g., 'GLOBAL_QUOTE', 'GOLD', 'SILVER', 'WTI', 'BRENT', 'NATURAL_GAS', 'COPPER', 'ALUMINUM', 'WHEAT', 'CORN', 'COTTON', 'SUGAR', 'COFFEE', 'ALL_COMMODITIES', 'CURRENCY_EXCHANGE_RATE') and 'symbol' (for stocks/forex).")
        self.api_key = os.getenv("ALPHA_VANTAGE_API_KEY", "6V28P6KCAG4N8TZZ")
        self.base_url = "https://www.alphavantage.co/query"

    def execute(self, function=None, symbol=None, from_currency=None, to_currency=None, payload=None):
        # Robust payload parsing
        if payload:
            if isinstance(payload, str):
                import json
                try:
                    p = json.loads(payload)
                    function = function or p.get('function')
                    symbol = symbol or p.get('symbol')
                    from_currency = from_currency or p.get('from_currency')
                    to_currency = to_currency or p.get('to_currency')
                except:
                    # If it's a simple string like "gold", try to be helpful
                    if function is None:
                        function = payload.upper()
        
        if not function:
            return "Error: 'function' parameter is required. Examples: 'GOLD', 'SILVER', 'GLOBAL_QUOTE', 'WTI'."

        # Normalize common names
        func_map = {
            "GOLD": "GOLD",
            "SILVER": "SILVER",
            "CRUDE OIL": "WTI",
            "OIL": "WTI",
            "BRENT OIL": "BRENT",
            "GAS": "NATURAL_GAS",
            "NATURAL GAS": "NATURAL_GAS"
        }
        function = func_map.get(function.upper(), function.upper())

        params = {
            "function": function,
            "apikey": self.api_key
        }

        # Context-specific parameters
        if function == "GLOBAL_QUOTE" and symbol:
            params["symbol"] = symbol
        elif function == "CURRENCY_EXCHANGE_RATE":
            params["from_currency"] = from_currency or symbol or "USD"
            params["to_currency"] = to_currency or "INR" # Default to INR for local context if possible
        elif function == "DIGITAL_CURRENCY_DAILY":
            params["symbol"] = symbol
            params["market"] = "USD"
        
        try:
            response = requests.get(self.base_url, params=params, timeout=15)
            data = response.json()
            
            if "Error Message" in data:
                return f"Alpha Vantage Error: {data['Error Message']}. Tip: For gold use function='GOLD'. For stocks use function='GLOBAL_QUOTE' with symbol."
            if "Note" in data:
                return f"Alpha Vantage Rate Limit: {data['Note']}"
            
            # Formatting output for the LLM
            import json
            return json.dumps(data, indent=2)
            
        except Exception as e:
            return f"Error connecting to Alpha Vantage: {str(e)}"

def get_market_data_instruction():
    return """
[MARKET DATA PRIORITY]
When the user asks for financial or economic data:
1. ALWAYS check AlphaVantage tool first. It supports:
   - Stocks: 'GLOBAL_QUOTE', 'TIME_SERIES_DAILY', 'TIME_SERIES_INTRADAY'
   - Commodities: 'GOLD', 'SILVER', 'WTI' (Oil), 'BRENT', 'NATURAL_GAS', 'COPPER', 'WHEAT', etc.
   - Forex/Exchange Rates: 'CURRENCY_EXCHANGE_RATE'
   - Crypto: 'DIGITAL_CURRENCY_DAILY'
   - Economic Indicators: 'REAL_GDP', 'CPI', 'INFLATION', 'UNEMPLOYMENT'
   - Technical Indicators: 'SMA', 'EMA', 'RSI', 'ADX'
   - News/Sentiment: 'NEWS_SENTIMENT'
2. For local rates (e.g., "Gold rate in India"), fetch the spot price using function='GOLD' and convert to INR using 'CURRENCY_EXCHANGE_RATE'.
3. Do NOT rely on training data or general web search for specific prices if AlphaVantage can provide them.
4. If a requested data type isn't listed, refer to https://mcp.alphavantage.co/ for all available functions.
"""
