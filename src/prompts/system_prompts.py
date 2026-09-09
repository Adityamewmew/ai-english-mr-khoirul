SYSTEM_PROMPT = """You are a helpful AI agent. Think step-by-step, use tools when needed, and answer concisely."""
CEFR_SYSTEM = open("prompts/cefr_system.txt").read() if __import__("pathlib").Path("prompts/cefr_system.txt").exists() else SYSTEM_PROMPT
