# ponytail: plug text-embedding-3-small / local bge when needed
from src.utils.config import LLM_BASE_URL, LLM_API_KEY
def embed(texts: list[str]) -> list[list[float]]:
    # placeholder — returns zero vectors to keep offline
    dim=1536
    return [[0.0]*dim for _ in texts]
def cosine(a,b): return 0.0
