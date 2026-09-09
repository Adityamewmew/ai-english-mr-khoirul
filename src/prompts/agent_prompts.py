AGENT_INSTRUCTION = """You have tools: search, calculator, weather. Call them via JSON: {"tool":"search","args":{"query":"..."}}. After tool result, synthesize final answer."""
FORMAT_PROMPT = """Respond as JSON when calling a tool, plain text for final answer."""
