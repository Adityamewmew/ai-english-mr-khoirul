import json, pathlib
from openai import OpenAI
from src.utils.cefr_config import LLM_BASE_URL, LLM_API_KEY, LLM_MODEL, CEFR_SYSTEM_PATH

SYSTEM = pathlib.Path(CEFR_SYSTEM_PATH).read_text() if pathlib.Path(CEFR_SYSTEM_PATH).exists() else pathlib.Path("prompts/cefr_system.txt").read_text() if pathlib.Path("prompts/cefr_system.txt").exists() else "You are CEFR grader."

def _client():
    return OpenAI(base_url=LLM_BASE_URL, api_key=LLM_API_KEY, timeout=6.0, max_retries=0)

def grade_text(skill: str, text: str) -> dict:
    # guard too_short
    if not text or len(text.split()) < 20:
        return {"cefr":"A1","score_0_100":5,"confidence":0.6,"criteria":{},"evidence":["too_short"],"feedback_id":"Jawaban terlalu pendek untuk dinilai. Coba tulis minimal 20 kata.","feedback_en":"Too short to grade.","next_level_hint":"Tulis kalimat lengkap dengan subjek + kata kerja."}
    client = _client()
    prompt = SYSTEM.replace("{skill}", skill) + f"\n\nSkill: {skill}\nUser input:\n{text[:6000]}\n\nReturn JSON only."
    try:
        resp = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role":"system","content":"You output JSON only."},{"role":"user","content":prompt}],
            temperature=0.2,
            max_tokens=800,
        )
        raw = resp.choices[0].message.content.strip()
        # extract json
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"): raw = raw[4:]
        data = json.loads(raw)
        # validate
        assert data.get("cefr") in ("A1","A2","B1","B2","C1","C2")
        data["score_0_100"] = int(max(0,min(100, int(data.get("score_0_100",50)))))
        data["confidence"] = float(max(0,min(1, float(data.get("confidence",0.7)))))
        return data
    except Exception as e:
        # fallback heuristic — ponytail: upgrade when LLM stable
        return {"cefr":"B1","score_0_100":50,"confidence":0.4,"criteria":{},"evidence":[f"llm_fallback: {e}"[:80]],"feedback_id":"Penilaian otomatis fallback. Cek koneksi LLM.","feedback_en":"Fallback grading.","next_level_hint":"Gunakan connector although/however untuk naik ke B2."}
