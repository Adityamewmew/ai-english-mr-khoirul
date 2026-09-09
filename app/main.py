from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .models import GradeRequest, GradeResponse, SkillResult, CEFR_META
from .grading import score_objective, aggregate
from .llm import grade_text

app = FastAPI(title="CEFR Grading API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/health")
def health(): return {"ok": True}

@app.get("/cefr/meta")
def meta(): return CEFR_META

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
