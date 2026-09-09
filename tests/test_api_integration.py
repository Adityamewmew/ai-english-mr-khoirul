from fastapi.testclient import TestClient
from app.main import app
import json

c = TestClient(app)
print("health:", c.get("/health").json())
print("meta keys:", list(c.get("/cefr/meta").json().keys())[:3])

# B2 writing + B2 speaking anchors → expect B2 overall, unless LLM unavailable -> fallback B1 still weighted OK
payload = {
  "listening_items": [
    {"skill":"listening","cefr_tag":"A1","is_correct": True},
    {"skill":"listening","cefr_tag":"A1","is_correct": True},
    {"skill":"listening","cefr_tag":"B1","is_correct": False}
  ],
  "reading_items": [
    {"skill":"reading","cefr_tag":"B2","is_correct": True},
    {"skill":"reading","cefr_tag":"B2","is_correct": True}
  ],
  "writing_text": "Although many people argue that online learning is less effective, I believe it offers significant advantages. However students need self-discipline to succeed. It is claimed that face-to-face interaction cannot be replaced, but recent studies have shown that well-designed blended courses can achieve similar outcomes. Therefore universities should adopt a blended approach and provide examples from real experience.",
  "speaking_transcript": "I think working from home has both advantages and disadvantages. On the one hand you can save time, however you may feel isolated because you dont interact with colleagues directly. In my experience a hybrid model works best and I prefer it because it gives flexibility while keeping social contact which is important for mental health and productivity."
}
r = c.post("/grade", json=payload)
print("status:", r.status_code)
print(json.dumps(r.json(), indent=2, ensure_ascii=False))

# test uneven profile
payload2 = {
  "listening_items": [{"skill":"listening","cefr_tag":"C1","is_correct": True}]*10,
  "speaking_transcript": "Hello my name Adit. I like football. I play every day."
}
r2 = c.post("/grade", json=payload2)
print("\n--- uneven test ---")
print(json.dumps(r2.json(), indent=2, ensure_ascii=False))
assert r2.json()["uneven_profile"] == True, "should flag uneven"
print("INTEGRATION OK")
