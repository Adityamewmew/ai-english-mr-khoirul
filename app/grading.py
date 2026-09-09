from typing import List
from .models import ObjectiveItem, WEIGHT, score_to_cefr, CEFR_META, CEFR_TO_IDX

def score_objective(items: List[ObjectiveItem]) -> dict:
    if not items:
        return {"cefr":"A1","score_0_100":0,"confidence":0.0,"detail":{"total":0,"correct":0}}
    total_w = sum(WEIGHT[i.cefr_tag] for i in items)
    correct_w = sum(WEIGHT[i.cefr_tag] for i in items if i.is_correct)
    raw = (correct_w / total_w * 100) if total_w else 0
    # time penalty ringan: ponytail
    score = int(round(raw))
    cefr = score_to_cefr(score)
    confidence = 0.6 if len(items) < 10 else 0.85 if len(items) >= 20 else 0.75
    return {
        "cefr": cefr,
        "score_0_100": score,
        "confidence": confidence,
        "detail": {"total": len(items), "correct": sum(1 for i in items if i.is_correct), "weighted_correct": round(correct_w,2), "weighted_total": round(total_w,2), "raw": round(raw,1)}
    }

def aggregate(skills: dict) -> tuple:
    if not skills: return "A1", 0, False
    def _score(v): return v.score_0_100 if hasattr(v, "score_0_100") else v["score_0_100"]
    def _cefr(v): return v.cefr if hasattr(v, "cefr") else v["cefr"]
    scores = [_score(v) for v in skills.values()]
    overall = int(round(sum(scores)/len(scores)))
    cefr = score_to_cefr(overall)
    idx = [CEFR_TO_IDX[_cefr(v)] for v in skills.values()]
    uneven = (max(idx) - min(idx) > 1) if len(idx)>1 else False
    return cefr, overall, uneven
