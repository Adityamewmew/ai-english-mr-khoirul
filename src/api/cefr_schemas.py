from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any

CEFR = Literal["A1","A2","B1","B2","C1","C2"]
Skill = Literal["listening","reading","speaking","writing"]

CEFR_ORDER = ["A1","A2","B1","B2","C1","C2"]
CEFR_TO_IDX = {v:i for i,v in enumerate(CEFR_ORDER)}
WEIGHT = {"A1":1.0,"A2":1.0,"B1":1.5,"B2":2.0,"C1":3.0,"C2":3.0}

# TOEFL 1-6 & IELTS mapping for display
CEFR_META = {
    "A1": {"label":"Beginner","group":"Basic User","ielts":"<4.0","toefl_1_6":"1.0","score_range":"0-19"},
    "A2": {"label":"Elementary","group":"Basic User","ielts":"4.0-5.0","toefl_1_6":"2.0","score_range":"20-39"},
    "B1": {"label":"Intermediate","group":"Independent","ielts":"5.0-6.0","toefl_1_6":"3.0-3.5","score_range":"40-59"},
    "B2": {"label":"Upper-Intermediate","group":"Independent","ielts":"6.5-7.5","toefl_1_6":"4.0-5.0","score_range":"60-79"},
    "C1": {"label":"Advanced","group":"Proficient","ielts":"8.0-8.5","toefl_1_6":"5.5","score_range":"80-92"},
    "C2": {"label":"Mastery","group":"Proficient","ielts":"9.0","toefl_1_6":"6.0","score_range":"93-100"},
}

def score_to_cefr(s: float) -> str:
    if s < 20: return "A1"
    if s < 40: return "A2"
    if s < 60: return "B1"
    if s < 80: return "B2"
    if s < 93: return "C1"
    return "C2"

class ObjectiveItem(BaseModel):
    skill: Literal["listening","reading"]
    cefr_tag: CEFR
    is_correct: bool
    time_spent_s: Optional[int] = None

class GradeRequest(BaseModel):
    user_id: Optional[str] = None
    listening_items: List[ObjectiveItem] = Field(default_factory=list)
    reading_items: List[ObjectiveItem] = Field(default_factory=list)
    writing_text: Optional[str] = None  # task 2 essay, task1 merged
    speaking_transcript: Optional[str] = None
    speaking_pronunciation_hint: Optional[Dict[str, Any]] = None

class SkillResult(BaseModel):
    cefr: CEFR
    score_0_100: int
    confidence: float = 0.8
    detail: Dict[str, Any] = Field(default_factory=dict)

class GradeResponse(BaseModel):
    overall_cefr: CEFR
    overall_score: int
    skills: Dict[str, SkillResult]
    uneven_profile: bool = False
    equivalent: Dict[str, str] = Field(default_factory=dict)
    feedback_id: str = ""
