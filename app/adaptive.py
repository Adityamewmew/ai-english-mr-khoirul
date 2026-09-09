"""Adaptive placement CAT-lite — 3-stage, 226 item bank, no IRT dep.
Stage 1: 10 mixed A1-B1 → estimate
Stage 2: branch 10 items near estimate
Stage 3: confirm + speaking/writing (LLM) — outside this module
Uses weighted scoring + ability estimate mapped to CEFR.
"""
import json, pathlib, random
from typing import List, Dict, Any

BANK_PATH = pathlib.Path(__file__).resolve().parent.parent / "data" / "item_bank.json"
_LISTENING_SCRIPTS = pathlib.Path(__file__).resolve().parent.parent / "data" / "listening_scripts.json"

CEFR_ORDER = ["A1","A2","B1","B2","C1","C2"]
CEFR_TO_IDX = {v:i for i,v in enumerate(CEFR_ORDER)}
WEIGHT = {"A1":1.0,"A2":1.0,"B1":1.5,"B2":2.0,"C1":3.0,"C2":3.0}

def _load_bank() -> List[Dict]:
    if not BANK_PATH.exists():
        return []
    return json.loads(BANK_PATH.read_text(encoding="utf-8"))
BANK = _load_bank()
# index by cefr+skill for quick
BY_CEFR_SKILL: Dict[str, List[Dict]] = {}
for it in BANK:
    key = f"{it.get('cefr')}:{it.get('skill')}"
    BY_CEFR_SKILL.setdefault(key, []).append(it)
# also by skill
BY_SKILL: Dict[str, List[Dict]] = {}
for it in BANK:
    BY_SKILL.setdefault(it.get("skill"), []).append(it)

def score_to_cefr(s: float) -> str:
    if s < 20: return "A1"
    if s < 40: return "A2"
    if s < 60: return "B1"
    if s < 80: return "B2"
    if s < 93: return "C1"
    return "C2"

def estimate_ability(items: List[Dict]) -> Dict[str, Any]:
    """items: list of {cefr_tag, is_correct} or {cefr, is_correct}"""
    if not items:
        return {"score": 50, "cefr": "B1", "confidence": 0.5}
    total_w = sum(WEIGHT.get(it.get("cefr_tag") or it.get("cefr") or "B1", 1.5) for it in items)
    correct_w = sum(WEIGHT.get(it.get("cefr_tag") or it.get("cefr") or "B1", 1.5) for it in items if it.get("is_correct"))
    raw = (correct_w / total_w * 100) if total_w else 50
    # confidence grows with n
    n = len(items)
    conf = 0.55 if n < 5 else 0.70 if n < 10 else 0.80 if n < 20 else 0.88
    # adjust if all correct/incorrect on hard items — push estimate
    score = int(round(raw))
    return {"score": score, "cefr": score_to_cefr(score), "confidence": conf, "n": n, "raw": round(raw,1)}

def select_stage1(n: int = 10) -> List[Dict]:
    """Stage 1: balanced A1-B1 mix (4 grammar A1-A2, 3 listening A1-A2, 3 reading A1-B1)"""
    bank = _load_bank()
    # filter objective only for stage1
    pool = [it for it in bank if it.get("skill") in ("grammar_vocab","listening","reading")]
    # prefer A1-B1
    a1b1 = [it for it in pool if it.get("cefr") in ("A1","A2","B1")]
    # sample balanced
    random.seed(42)
    # ensure mix
    g = [it for it in a1b1 if it.get("skill")=="grammar_vocab"]
    lst = [it for it in a1b1 if it.get("skill")=="listening"]
    rd = [it for it in a1b1 if it.get("skill")=="reading"]
    sel=[]
    sel += random.sample(g, min(4, len(g)))
    sel += random.sample(lst, min(3, len(lst)))
    sel += random.sample(rd, min(3, len(rd)))
    # fill remaining if needed
    if len(sel) < n:
        extra = [it for it in a1b1 if it not in sel]
        sel += random.sample(extra, min(n - len(sel), len(extra)))
    # strip heavy fields for API (keep id, skill, cefr, question, options)
    return [{"id": it["id"], "skill": it["skill"], "cefr": it["cefr"], "question": it.get("question") or it.get("prompt") or "", "options": it.get("options"), "passage": it.get("passage","")[:300] if it.get("passage") else "", "audio_hint": bool(it.get("audio_script"))} for it in sel[:n]]

def select_stage2(current_cefr: str, n: int = 10, exclude_ids: set = None) -> List[Dict]:
    """Stage 2: branch near current estimate"""
    exclude_ids = exclude_ids or set()
    bank = _load_bank()
    pool = [it for it in bank if it.get("skill") in ("grammar_vocab","listening","reading") and it["id"] not in exclude_ids]
    idx = CEFR_TO_IDX.get(current_cefr, 2)
    # target cefrs: if A1/A2 -> stay A1-A2+B1; if B1 -> B1-B2; if B2 -> B2-C1; if C1/C2 -> B2-C2
    if idx <= 1:
        target = ["A1","A2","B1"]
    elif idx == 2:
        target = ["B1","B2"]
    elif idx == 3:
        target = ["B2","C1"]
    else:
        target = ["B2","C1","C2"]
    cand = [it for it in pool if it.get("cefr") in target]
    if len(cand) < n:
        cand = pool
    random.seed(hash(current_cefr) % 997)
    sel = random.sample(cand, min(n, len(cand)))
    return [{"id": it["id"], "skill": it["skill"], "cefr": it["cefr"], "question": it.get("question") or it.get("prompt") or "", "options": it.get("options"), "passage": it.get("passage","")[:300] if it.get("passage") else "", "audio_hint": bool(it.get("audio_script"))} for it in sel]

def next_items_for_estimate(score: int, n: int = 10, exclude_ids: set = None) -> List[Dict]:
    cefr = score_to_cefr(score)
    return select_stage2(cefr, n=n, exclude_ids=exclude_ids)
