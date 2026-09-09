import json, re
def safe_json_loads(s: str):
    try: return json.loads(s)
    except Exception: return {}
def extract_json(text: str):
    m=re.search(r"\{.*\}", text, re.S)
    return safe_json_loads(m.group(0)) if m else {}
def truncate(text: str, n=4000):
    return text[:n] + "…[truncated]" if len(text)>n else text
