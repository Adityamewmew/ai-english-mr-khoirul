from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import pathlib as _pl
from fastapi.middleware.cors import CORSMiddleware
from .models import GradeRequest, GradeResponse, SkillResult, CEFR_META
from .grading import score_objective, aggregate
from .llm import grade_text
from .adaptive import select_stage1, select_stage2, estimate_ability, score_to_cefr, next_items_for_estimate

app = FastAPI(title="CEFR Grading API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/health")
def health(): return {"ok": True}

@app.get("/cefr/meta")
def meta(): return CEFR_META


AUDIO_DIR = _pl.Path(__file__).resolve().parent.parent / "data" / "audio"
# mount static audio (optional)
try:
    app.mount("/audio", StaticFiles(directory=str(AUDIO_DIR)), name="audio")
except Exception:
    pass

class Stage2Request(BaseModel):
    answers: List[dict]  # [{cefr_tag|cefr, is_correct}]
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
    import json
    p = _pl.Path(__file__).resolve().parent.parent / "data" / "speaking_prompts.json"
    if not p.exists():
        return []
    data = json.loads(p.read_text())
    if cefr:
        data = [d for d in data if d["cefr"] == cefr.upper()]
    return data[:n]

@app.get("/writing/samples")
def writing_samples(cefr: str = None, n: int = 6):
    import json
    p = _pl.Path(__file__).resolve().parent.parent / "data" / "writing_samples.json"
    if not p.exists():
        return []
    data = json.loads(p.read_text())
    if cefr:
        data = [d for d in data if d["cefr"] == cefr.upper()]
    return data[:n]

@app.get("/reading/passages")
def reading_passages(cefr: str = None, n: int = 4):
    import json
    p = _pl.Path(__file__).resolve().parent.parent / "data" / "reading_passages.json"
    if not p.exists():
        return []
    data = json.loads(p.read_text())
    if cefr:
        data = [d for d in data if d["cefr"] == cefr.upper()]
    return data[:n]


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
        # gabung transcript + pronunciation hint jika ada
        txt = req.speaking_transcript
        if req.speaking_pronunciation_hint:
            txt += f"\n[pronunciation_hint: {req.speaking_pronunciation_hint}]"
        d = grade_text("speaking", txt)
        skills["speaking"] = SkillResult(cefr=d["cefr"], score_0_100=d["score_0_100"], confidence=d["confidence"], detail={"criteria": d.get("criteria",{}), "evidence": d.get("evidence",[]), "feedback_en": d.get("feedback_en",""), "next_level_hint": d.get("next_level_hint","")})
        speaking_feedback = d.get("feedback_id","")
    else:
        speaking_feedback = ""

    if not skills:
        # no data → A1
        return GradeResponse(overall_cefr="A1", overall_score=0, skills={}, uneven_profile=False, equivalent=CEFR_META["A1"], feedback_id="Belum ada jawaban untuk dinilai.")

    overall_cefr, overall_score, uneven = aggregate(skills)
    equiv = CEFR_META[overall_cefr]

    # feedback ringkas
    weak = min(skills.items(), key=lambda x: x[1].score_0_100)[0] if len(skills)>1 else list(skills.keys())[0]
    feedback_id = writing_feedback or speaking_feedback or f"Level kamu {overall_cefr} ({equiv['label']}). Skill terlemah: {weak}. Fokus latihan {weak} untuk naik level."

    return GradeResponse(
        overall_cefr=overall_cefr,
        overall_score=overall_score,
        skills=skills,
        uneven_profile=uneven,
        equivalent=equiv,
        feedback_id=feedback_id
    )
