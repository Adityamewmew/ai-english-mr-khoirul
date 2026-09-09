# AI English Mr Khoirul — Unified Agent + CEFR Grading

Struktur `ai-agent-project/` + fitur CEFR 4 skills A1-C2 (226 items, TTS 36 mp3).

## Run
```bash
pip install -r requirements.txt
cp .env.example .env  # isi LLM_API_KEY
python main.py          # -> http://localhost:8000
# atau
uvicorn src.api.routes:app --reload --port 8000
```
\n---\n# SaaS English CEFR — Placement Grading API

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
