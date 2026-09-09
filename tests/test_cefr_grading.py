# runnable check — no framework, ponytail: ganti pytest when >50 tests
from app.grading import score_objective, aggregate, score_to_cefr
from app.models import ObjectiveItem

def assert_eq(a,b,msg=""):
    assert a==b, f"{msg} expected {b} got {a}"

# cut scores
assert_eq(score_to_cefr(0), "A1")
assert_eq(score_to_cefr(19), "A1")
assert_eq(score_to_cefr(20), "A2")
assert_eq(score_to_cefr(39), "A2")
assert_eq(score_to_cefr(40), "B1")
assert_eq(score_to_cefr(59), "B1")
assert_eq(score_to_cefr(60), "B2")
assert_eq(score_to_cefr(79), "B2")
assert_eq(score_to_cefr(80), "C1")
assert_eq(score_to_cefr(92), "C1")
assert_eq(score_to_cefr(93), "C2")
assert_eq(score_to_cefr(100), "C2")

# objective weighted: benar item C1 berbobot 3, salah A1 penalti kecil
items = [ObjectiveItem(skill="reading", cefr_tag="A1", is_correct=True), ObjectiveItem(skill="reading", cefr_tag="A1", is_correct=True), ObjectiveItem(skill="reading", cefr_tag="C1", is_correct=False)]
r = score_objective(items)
assert r["cefr"] in ("A2","B1","A1","B2"), r
assert 0 <= r["score_0_100"] <= 100

# all correct → 100 C2
items2 = [ObjectiveItem(skill="listening", cefr_tag="B2", is_correct=True) for _ in range(10)]
r2 = score_objective(items2)
assert_eq(r2["score_0_100"], 100)
assert_eq(r2["cefr"], "C2")

# all wrong → 0 A1
items3 = [ObjectiveItem(skill="listening", cefr_tag="A1", is_correct=False) for _ in range(5)]
r3 = score_objective(items3)
assert_eq(r3["score_0_100"], 0)
assert_eq(r3["cefr"], "A1")

# aggregate + uneven flag
skills = {"listening": {"cefr":"C1","score_0_100":85}, "reading": {"cefr":"C1","score_0_100":88}, "speaking": {"cefr":"A2","score_0_100":30}}
cefr, score, uneven = aggregate(skills)
assert uneven == True, "gap C1-A2 should be uneven"
assert 50 < score < 80

skills2 = {"listening": {"cefr":"B2","score_0_100":70}, "reading": {"cefr":"B2","score_0_100":72}}
cefr2, score2, uneven2 = aggregate(skills2)
assert uneven2 == False

# llm guard too_short — no API call
from app.llm import grade_text
d = grade_text("writing", "hi")
assert_eq(d["cefr"], "A1")
assert "too_short" in str(d["evidence"])

print("ALL ASSERTS PASSED")
