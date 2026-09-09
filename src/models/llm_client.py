from openai import OpenAI
from src.utils.config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL
def client(): return OpenAI(base_url=LLM_BASE_URL, api_key=LLM_API_KEY, timeout=20, max_retries=1)
def chat(messages, temperature=0.7, max_tokens=800):
    c=client()
    r=c.chat.completions.create(model=LLM_MODEL, messages=messages, temperature=temperature, max_tokens=max_tokens)
    return r.choices[0].message.content
