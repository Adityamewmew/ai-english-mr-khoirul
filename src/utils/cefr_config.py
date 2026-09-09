import os
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://100.122.10.66:20128/v1")
LLM_API_KEY = os.getenv("LLM_API_KEY") or os.getenv("HERMES_CUSTOM_100_122_10_66_20128_API_KEY") or "sk-dummy"
LLM_MODEL = os.getenv("LLM_MODEL", "gemini")
CEFR_SYSTEM_PATH = os.getenv("CEFR_SYSTEM_PATH", "prompts/cefr_system.txt")
