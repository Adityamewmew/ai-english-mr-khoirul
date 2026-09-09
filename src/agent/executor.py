from src.tools.search import search
from src.tools.calculator import calculate
from src.tools.weather import get_weather
TOOLS={"search":search, "calculator":calculate, "weather":get_weather}
def execute(tool: str, args: dict):
    fn=TOOLS.get(tool)
    if not fn: return f"unknown tool: {tool}"
    try: return fn(**args)
    except Exception as e: return f"tool error {tool}: {e}"
