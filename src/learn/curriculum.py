
import json, pathlib
from typing import List, Dict, Optional

CUR_PATH = pathlib.Path(__file__).resolve().parent.parent.parent / "data" / "curriculum_modules.json"
LESSON_PATH = pathlib.Path(__file__).resolve().parent.parent.parent / "data" / "lesson_bank.json"

def load_modules() -> List[Dict]:
    return json.loads(CUR_PATH.read_text(encoding="utf-8")) if CUR_PATH.exists() else []
def load_lessons() -> List[Dict]:
    return json.loads(LESSON_PATH.read_text(encoding="utf-8")) if LESSON_PATH.exists() else []

CEFR_ORDER = ["A1","A2","B1","B2","C1","C2"]
GRADE_GROUP = {"A1":"A","A2":"A","B1":"B","B2":"B","C1":"C","C2":"C","A":"A","B":"B","C":"C"}

def modules_for_grade(grade: str) -> List[Dict]:
    """grade = overall_cefr like B1 or group A/B/C"""
    g = GRADE_GROUP.get(grade.upper(), "A")
    mods = load_modules()
    if g=="A": return [m for m in mods if m["group"].startswith("A")]
    if g=="B": return [m for m in mods if "B -" in m["group"]]
    return [m for m in mods if "C -" in m["group"] or m["group"]=="All"]

def module_by_id(mid: str) -> Optional[Dict]:
    for m in load_modules():
        if m["id"]==mid: return m
    return None
def lessons_for_module(mid: str) -> List[Dict]:
    return [l for l in load_lessons() if l["module_id"]==mid]
def lesson_by_id(lid: str) -> Optional[Dict]:
    for l in load_lessons():
        if l["id"]==lid: return l
    return None
def system_prompt_for_lesson(lesson: Dict, learner_cefr: str="B1") -> str:
    pts=", ".join(lesson.get("points",[])[:2])
    vocab=", ".join(lesson.get("vocab",[])[:3])
    return f"""You are Mr Khoirul — friendly AI English tutor for Indonesian learners.
Module: {lesson['title']} ({lesson['cefr']}) — {lesson['objective']}
Learner grade: {learner_cefr} (from placement). Adapt language level accordingly.
Lesson focus: {pts}
Vocab: {vocab}
Style: Short, conversational, 1 question per turn. Correct gently via recast. Use Indonesian hint only for A1-A2.
Structure per turn:
  1. Warm example (1 sentence using target grammar)
  2. Ask learner to try (1 sentence)
  3. On answer: praise + recast if needed + next prompt
After 8-12 turns: suggest a 3-question quiz.
Never lecture >4 sentences. Never ask 2 questions at once.
"""
