from horizondesk import BaseTool, HorizonPlugin

class MyCustomTool(BaseTool):
    def __init__(self):
        super().__init__("LegacyCalculator", "Adds, subtracts, multiplies or divides two numbers. Input: JSON 'a', 'b', 'operation'.")

    def execute(self, a=None, b=None, operation=None, payload=None):
        if payload and isinstance(payload, dict):
            a = payload.get('a', a)
            b = payload.get('b', b)
            operation = payload.get('operation', operation)
        
        try:
            a, b = float(a), float(b)
            if operation == "add": return f"Result: {a + b}"
            if operation == "subtract": return f"Result: {a - b}"
            if operation == "multiply": return f"Result: {a * b}"
            if operation == "divide": return f"Result: {a / b}" if b != 0 else "Error: Division by zero"
            return "Error: Unknown operation"
        except Exception as e:
            return f"Error: {e}"

def register_tools(agent):
    plugin = HorizonPlugin("CalculatorPlugin")
    plugin.add_tool(MyCustomTool())
    plugin.register_all(agent)
