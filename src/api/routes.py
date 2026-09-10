from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import pathlib as _pl
import json

from src.api.schemas import ChatRequest, ChatResponse
from src.agent.agent import Agent
from src.api.cefr_schemas import GradeRequest, GradeResponse, SkillResult, CEFR_META
from src.utils.grading import score_objective, aggregate
from src.models.cefr_llm import grade_text
from src.agent.adaptive import select_stage1, select_stage2, estimate_ability, score_to_cefr, next_items_for_estimate

app = FastAPI(title="AI English Mr Khoirul - Unified API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ---- Generic Agent ----
_agent = Agent()

@app.get("/health")
def health(): return {"ok": True}

@app.get("/cefr/meta")
def cefr_meta(): return CEFR_META

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    return ChatResponse(reply=_agent.run(req.message), session_id=req.session_id)

@app.post("/reset")
def reset(): _agent.reset(); return {"ok": True}

# ---- Placement (Adaptive) ----
AUDIO_DIR = _pl.Path(__file__).resolve().parent.parent.parent / "data" / "audio"
try:
    app.mount("/audio", StaticFiles(directory=str(AUDIO_DIR)), name="audio")
except Exception:
    pass

class Stage2Request(BaseModel):
    answers: List[dict]
    exclude_ids: Optional[List[str]] = None
    n: int = 10

@app.get("/placement/stage1")
def placement_stage1(n: int = 10):
    return {"stage": 1, "n": n, "items": select_stage1(n=n)}

@app.post("/placement/stage2")
def placement_stage2(req: Stage2Request):
    est = estimate_ability(req.answers)
    nxt = select_stage2(est["cefr"], n=req.n, exclude_ids=set(req.exclude_ids or []))
    return {"stage": 2, "estimate": est, "items": nxt}

@app.get("/placement/next")
def placement_next(score: int, n: int = 10):
    cefr = score_to_cefr(score)
    items = next_items_for_estimate(score, n=n)
    return {"score": score, "cefr": cefr, "items": items}

@app.get("/listening/audio/{item_id}")
def listening_audio(item_id: str):
    fp = AUDIO_DIR / f"{item_id}.mp3"
    if not fp.exists():
        raise HTTPException(404, f"Audio {item_id} not found — run scripts/generate_tts.py")
    return FileResponse(str(fp), media_type="audio/mpeg", filename=f"{item_id}.mp3")

@app.get("/speaking/prompts")
def speaking_prompts(cefr: str = None, n: int = 6):
    p = _pl.Path(__file__).resolve().parent.parent.parent / "data" / "speaking_prompts.json"
    if not p.exists(): return []
    data = json.loads(p.read_text())
    if cefr: data = [d for d in data if d["cefr"] == cefr.upper()]
    return data[:n]

@app.get("/writing/samples")
def writing_samples(cefr: str = None, n: int = 6):
    p = _pl.Path(__file__).resolve().parent.parent.parent / "data" / "writing_samples.json"
    if not p.exists(): return []
    data = json.loads(p.read_text())
    if cefr: data = [d for d in data if d["cefr"] == cefr.upper()]
    return data[:n]

@app.get("/reading/passages")
def reading_passages(cefr: str = None, n: int = 4):
    p = _pl.Path(__file__).resolve().parent.parent.parent / "data" / "reading_passages.json"
    if not p.exists(): return []
    data = json.loads(p.read_text())
    if cefr: data = [d for d in data if d["cefr"] == cefr.upper()]
    return data[:n]


# ---- Learn: Curriculum & Tutor Chat ----
from src.learn.curriculum import load_modules, load_lessons, modules_for_grade, module_by_id, lessons_for_module, lesson_by_id, system_prompt_for_lesson
from src.models.llm_client import chat as llm_chat

@app.get("/learn/modules")
def learn_modules(grade: str = "B1"):
    mods = modules_for_grade(grade)
    return {"grade": grade.upper(), "count": len(mods), "modules": mods}

@app.get("/learn/modules/all")
def learn_modules_all():
    mods = load_modules()
    return {"count": len(mods), "modules": mods}

@app.get("/learn/lessons")
def learn_lessons(module_id: str = None):
    if module_id:
        return {"module_id": module_id, "lessons": lessons_for_module(module_id)}
    return {"count": len(load_lessons()), "lessons": load_lessons()}

@app.get("/learn/lesson/{lesson_id}")
def learn_lesson(lesson_id: str, learner_cefr: str = "B1"):
    lesson = lesson_by_id(lesson_id)
    if not lesson:
        raise HTTPException(404, f"Lesson {lesson_id} not found")
    mod = module_by_id(lesson["module_id"])
    return {"lesson": lesson, "module": mod, "system_prompt": system_prompt_for_lesson(lesson, learner_cefr)}

class LessonChatRequest(BaseModel):
    lesson_id: str
    learner_cefr: str = "B1"
    message: str
    history: List[dict] = []  # [{role, content}]

@app.post("/learn/lesson/chat")
def learn_lesson_chat(req: LessonChatRequest):
    lesson = lesson_by_id(req.lesson_id)
    if not lesson:
        raise HTTPException(404, f"Lesson {req.lesson_id} not found")
    sys_prompt = system_prompt_for_lesson(lesson, req.learner_cefr)
    msgs = [{"role":"system","content": sys_prompt}]
    for h in (req.history or [])[-10:]:
        if h.get("role") in ("user","assistant") and h.get("content"):
            msgs.append({"role": h["role"], "content": h["content"][:1200]})
    msgs.append({"role":"user","content": req.message[:1500]})
    try:
        reply = llm_chat(msgs, temperature=0.7, max_tokens=500)
        if not (reply or "").strip():
            raise ValueError("empty reply from LLM")
    except Exception as e:
        # fallback yang tetap ngajar, bukan stub kosong
        reply = f"Halo! Kita belajar {lesson['title']} ({lesson['cefr']}) — {lesson['objective']}. Contoh: I am a student. Kamu coba: perkenalkan diri pakai 'I am ...' dalam 1 kalimat. {lesson['exercise']}"
    return {"lesson_id": req.lesson_id, "reply": reply, "lesson": lesson}

@app.get("/learn/lesson/{lesson_id}/quiz")
def learn_lesson_quiz(lesson_id: str, n: int = 3):
    lesson = lesson_by_id(lesson_id)
    if not lesson:
        raise HTTPException(404, f"Lesson {lesson_id} not found")
    # quiz from grammar_vocab_bank filtered by lesson points
    import json as _js
    bank_path = _pl.Path(__file__).resolve().parent.parent.parent / "data" / "grammar_vocab_bank.json"
    bank = _js.loads(bank_path.read_text()) if bank_path.exists() else []
    # filter by cefr
    cand = [q for q in bank if q["cefr"]==lesson["cefr"]]
    if len(cand) < n: cand = bank
    import random as _rnd
    _rnd.seed(hash(lesson_id) % 997)
    quiz = _rnd.sample(cand, min(n, len(cand)))
    return {"lesson_id": lesson_id, "quiz": [{"id":q["id"],"question":q["question"],"options":q["options"],"answer":q["answer"]} for q in quiz]}



import tempfile, base64, asyncio
try:
    import edge_tts
    HAS_TTS = True
except Exception:
    HAS_TTS = False

async def _tts_bytes(text: str, voice: str = "en-US-AriaNeural", rate: str = "+0%") -> bytes:
    if not HAS_TTS:
        raise RuntimeError("edge-tts not installed")
    # edge_tts communicate
    comm = edge_tts.Communicate(text[:1200], voice, rate=rate)
    chunks = []
    async for chunk in comm.stream():
        if chunk["type"] == "audio":
            chunks.append(chunk["data"])
    return b"".join(chunks)

@app.get("/learn/tts/voices")
def tts_voices():
    return {
        "voices": [
            {"id":"en-US-AriaNeural","label":"Aria (US female, warm)","accent":"US"},
            {"id":"en-GB-SoniaNeural","label":"Sonia (UK female)","accent":"UK"},
            {"id":"en-AU-NatashaNeural","label":"Natasha (AU female)","accent":"AU"},
            {"id":"en-US-GuyNeural","label":"Guy (US male)","accent":"US"},
            {"id":"en-GB-RyanNeural","label":"Ryan (UK male)","accent":"UK"},
        ],
        "has_tts": HAS_TTS
    }

@app.post("/learn/lesson/tts")
async def learn_lesson_tts(payload: dict):
    text = (payload.get("text") or "")[:1200]
    voice = payload.get("voice") or "en-US-AriaNeural"
    rate = payload.get("rate") or "+0%"
    if not text.strip():
        raise HTTPException(400, "text required")
    if not HAS_TTS:
        raise HTTPException(503, "TTS not available (edge-tts missing)")
    try:
        data = await _tts_bytes(text, voice, rate)
    except Exception as e:
        raise HTTPException(500, f"TTS failed: {e}")
    from fastapi.responses import Response
    return Response(content=data, media_type="audio/mpeg", headers={"Content-Disposition": "inline; filename=tts.mp3"})

@app.post("/learn/lesson/chat-voice")
async def learn_lesson_chat_voice(payload: dict):
    """Chat + TTS in one call: returns reply + base64 audio"""
    lesson_id = payload.get("lesson_id")
    learner_cefr = payload.get("learner_cefr") or "B1"
    message = (payload.get("message") or "")[:1500]
    history = payload.get("history") or []
    voice = payload.get("voice") or "en-US-AriaNeural"
    rate = payload.get("rate") or "+0%"
    lesson = lesson_by_id(lesson_id)
    if not lesson:
        raise HTTPException(404, f"Lesson {lesson_id} not found")
    sys_prompt = system_prompt_for_lesson(lesson, learner_cefr)
    msgs = [{"role":"system","content": sys_prompt}]
    for h in history[-10:]:
        if h.get("role") in ("user","assistant") and h.get("content"):
            msgs.append({"role": h["role"], "content": h["content"][:1200]})
    msgs.append({"role":"user","content": message})
    try:
        reply = llm_chat(msgs, temperature=0.7, max_tokens=400)
        if not (reply or "").strip():
            raise ValueError("empty reply")
    except Exception as e:
        reply = f"Halo! Kita belajar {lesson['title']} ({lesson['cefr']}) — {lesson['objective']}. Contoh: I am a student. Kamu coba: perkenalkan diri pakai 'I am ...' dalam 1 kalimat. {lesson['exercise']}"
    audio_b64 = None
    if HAS_TTS:
        try:
            data = await _tts_bytes(reply, voice, rate)
            audio_b64 = base64.b64encode(data).decode()
        except Exception:
            pass
    return {"lesson_id": lesson_id, "reply": reply, "audio_b64": audio_b64, "lesson": lesson, "voice": voice}


# ---- CEFR Grading ----
@app.post("/grade", response_model=GradeResponse)
def grade(req: GradeRequest):
    skills: dict[str, SkillResult] = {}
    if req.listening_items:
        r = score_objective(req.listening_items)
        skills["listening"] = SkillResult(**r)
    if req.reading_items:
        r = score_objective(req.reading_items)
        skills["reading"] = SkillResult(**r)
    if req.writing_text is not None:
        d = grade_text("writing", req.writing_text)
        skills["writing"] = SkillResult(cefr=d["cefr"], score_0_100=d["score_0_100"], confidence=d["confidence"], detail={"criteria": d.get("criteria",{}), "evidence": d.get("evidence",[]), "feedback_en": d.get("feedback_en",""), "next_level_hint": d.get("next_level_hint","")})
        writing_feedback = d.get("feedback_id","")
    else:
        writing_feedback = ""
    if req.speaking_transcript is not None:
        txt = req.speaking_transcript
        if req.speaking_pronunciation_hint:
            txt += f"\n[pronunciation_hint: {req.speaking_pronunciation_hint}]"
        d = grade_text("speaking", txt)
        skills["speaking"] = SkillResult(cefr=d["cefr"], score_0_100=d["score_0_100"], confidence=d["confidence"], detail={"criteria": d.get("criteria",{}), "evidence": d.get("evidence",[]), "feedback_en": d.get("feedback_en",""), "next_level_hint": d.get("next_level_hint","")})
        speaking_feedback = d.get("feedback_id","")
    else:
        speaking_feedback = ""
    if not skills:
        return GradeResponse(overall_cefr="A1", overall_score=0, skills={}, uneven_profile=False, equivalent=CEFR_META["A1"], feedback_id="Belum ada jawaban untuk dinilai.")
    overall_cefr, overall_score, uneven = aggregate(skills)
    equiv = CEFR_META[overall_cefr]
    weak = min(skills.items(), key=lambda x: x[1].score_0_100)[0] if len(skills)>1 else list(skills.keys())[0]
    feedback_id = writing_feedback or speaking_feedback or f"Level kamu {overall_cefr} ({equiv['label']}). Skill terlemah: {weak}. Fokus latihan {weak} untuk naik level."
    return GradeResponse(overall_cefr=overall_cefr, overall_score=overall_score, skills=skills, uneven_profile=uneven, equivalent=equiv, feedback_id=feedback_id)
