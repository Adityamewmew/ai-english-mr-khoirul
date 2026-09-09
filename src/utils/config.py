import os
from dotenv import load_dotenv
load_dotenv()
LLM_API_KEY=os.getenv("LLM_API_KEY","sk-dummy")
LLM_BASE_URL=os.getenv("LLM_BASE_URL","http://100.122.10.66:20128/v1")
LLM_MODEL=os.getenv("LLM_MODEL","gemini")
WEATHER_API_KEY=os.getenv("WEATHER_API_KEY","")
LOG_LEVEL=os.getenv("LOG_LEVEL","INFO")
