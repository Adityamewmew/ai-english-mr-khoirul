import httpx
def search(query: str, limit: int = 5) -> str:
    # ponytail: swap to tavily/brave when key available
    return f"[search stub] results for: {query} (limit {limit}) — integrate API key in .env"
