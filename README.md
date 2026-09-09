# SaaS English CEFR — Placement Grading API

`POST /grade` → CEFR A1-C2 dari 4 skills.

## Run
```
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```
Test: `python -m tests.test_cefr_grading` atau `python tests/test_cefr_grading.py` (no framework)

## API
`POST /grade` body: `{listening_items:[{skill,cefr_tag,is_correct}], reading_items:[...], writing_text:"...", speaking_transcript:"..."}`
Response: `overall_cefr, overall_score, skills{listening,reading,writing,speaking}, uneven_profile, equivalent{ielts,toefl_1_6}`

Prompts: `prompts/cefr_system.txt` + anchors `prompts/cefr_anchors.json`
Vault: `Documents/Obsidian Vault/Memory/AI CEFR Grading System.md`
