import httpx
from src.utils.config import WEATHER_API_KEY
def get_weather(city: str) -> str:
    if not WEATHER_API_KEY: return f"[weather stub] {city}: 28°C, partly cloudy (set WEATHER_API_KEY for live data)"
    # ponytail: call openweathermap
    return f"[weather] {city} — live call not yet wired"
