#!/usr/bin/env python3
"""Build outputs from generate_full_dataset.py banks → JSON + SQL + Excel"""
import pathlib, json, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import generate_full_dataset as D

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DATA.mkdir(parents=True, exist_ok=True)

def write_json(path, obj):
    p = ROOT / path if not pathlib.Path(path).is_absolute() else pathlib.Path(path)
    # also handle relative like data/...
    if not p.is_absolute():
        p = ROOT / p
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {p} ({len(json.dumps(obj, ensure_ascii=False))} chars, {len(obj) if isinstance(obj,list) else 'dict'} records)")

# 1. Individual JSONs
write_json("data/listening_scripts.json", D.listening_bank)
write_json("data/reading_passages.json", D.reading_passages)
write_json("data/grammar_vocab_bank.json", D.grammar_vocab_bank)
write_json("data/writing_samples.json", D.writing_samples)
write_json("data/speaking_prompts.json", D.speaking_prompts)

# 2. Unified item_bank (for LLM RAG + adaptive engine)
item_bank = []
for e in D.listening_bank:
    for q in e["questions"]:
        item_bank.append({"id": f"{e['id']}-Q{item_bank.count(0)+1}", "skill":"listening","cefr":e["cefr"],"prompt": e["audio_script"][:200]+"... | Q: "+q["q"],"options":q.get("options"),"answer":q["answer"],"audio_script":e["audio_script"],"wpm":e["wpm"],"accent":e["accent"],"duration_s":e["duration_s"]})
# Listening items count
listening_qs = sum(len(e["questions"]) for e in D.listening_bank)
# For unified, redo properly:
item_bank=[]
for e in D.listening_bank:
    for qi, q in enumerate(e["questions"]):
        item_bank.append({"id": f"{e['id']}-Q{qi+1}","skill":"listening","cefr":e["cefr"],"type":q.get("type","MCQ"),"question":q["q"],"options":q.get("options"),"answer":q["answer"],"audio_script":e["audio_script"],"title":e["title"],"wpm":e["wpm"],"accent":e["accent"],"duration_s":e["duration_s"]})
for e in D.reading_passages:
    for qi, q in enumerate(e["questions"]):
        item_bank.append({"id": f"{e['id']}-Q{qi+1}","skill":"reading","cefr":e["cefr"],"type":"MCQ","question":q["q"],"options":q["options"],"answer":q["answer"],"passage":e["passage"],"title":e["title"],"word_count":e["word_count"]})
for e in D.grammar_vocab_bank:
    item_bank.append({"id": e["id"],"skill":"grammar_vocab","cefr":e["cefr"],"type":e["type"],"question":e["question"],"options":e["options"],"answer":e["answer"],"explanation":e["explanation"]})
for e in D.writing_samples:
    item_bank.append({"id": e["id"],"skill":"writing","cefr":e["cefr"],"prompt":e["prompt"],"text":e["text"],"word_count":e["word_count"],"rubric":e["rubric"],"note":e["note"]})
for e in D.speaking_prompts:
    item_bank.append({"id": e["id"],"skill":"speaking","cefr":e["cefr"],"task":e["task"],"prompt":e["prompt"],"expected":e["expected"],"duration_s":e["duration_s"],"rubric_hint":e.get("rubric_hint","")})

write_json("data/item_bank.json", item_bank)
print(f"Unified bank: {len(item_bank)} items (listening_qs={listening_qs}, reading_qs={sum(len(e['questions']) for e in D.reading_passages)}, grammar={len(D.grammar_vocab_bank)}, writing={len(D.writing_samples)}, speaking={len(D.speaking_prompts)})")

# 3. SQL seed
sql_path = DATA / "seed_training_data.sql"
lines = ["-- CEFR Full Training Dataset seed", "-- Generated "+__import__("datetime").date.today().isoformat(), ""]
# Ensure tables for training (create if not exists)
lines.append("""
CREATE TABLE IF NOT EXISTS training_passages (
  id TEXT PRIMARY KEY, cefr TEXT, title TEXT, passage TEXT, word_count INT
);
CREATE TABLE IF NOT EXISTS training_questions (
  id TEXT PRIMARY KEY, passage_id TEXT, skill TEXT, cefr TEXT, question TEXT, options JSONB, answer TEXT
);
CREATE TABLE IF NOT EXISTS training_listening (
  id TEXT PRIMARY KEY, cefr TEXT, title TEXT, audio_script TEXT, wpm INT, accent TEXT, duration_s INT
);
CREATE TABLE IF NOT EXISTS training_grammar (
  id TEXT PRIMARY KEY, cefr TEXT, type TEXT, question TEXT, options JSONB, answer TEXT, explanation TEXT
);
CREATE TABLE IF NOT EXISTS training_writing_samples (
  id TEXT PRIMARY KEY, cefr TEXT, prompt TEXT, text TEXT, word_count INT, rubric JSONB, note TEXT
);
CREATE TABLE IF NOT EXISTS training_speaking (
  id TEXT PRIMARY KEY, cefr TEXT, task TEXT, prompt TEXT, expected TEXT, duration_s INT
);
""")
def esc(s): return s.replace("'", "''")

for e in D.listening_bank:
    lines.append(f"INSERT INTO training_listening (id,cefr,title,audio_script,wpm,accent,duration_s) VALUES ('{esc(e['id'])}','{e['cefr']}','{esc(e['title'])}','{esc(e['audio_script'])}',{e['wpm']},'{esc(e['accent'])}',{e['duration_s']}) ON CONFLICT DO NOTHING;")
    for qi, q in enumerate(e["questions"]):
        qid = f"{e['id']}-Q{qi+1}"
        opts = json.dumps(q.get("options",[]), ensure_ascii=False).replace("'","''")
        lines.append(f"INSERT INTO training_questions (id,passage_id,skill,cefr,question,options,answer) VALUES ('{qid}','{e['id']}','listening','{e['cefr']}','{esc(q['q'])}','{opts}','{esc(str(q['answer']))}') ON CONFLICT DO NOTHING;")
for e in D.reading_passages:
    lines.append(f"INSERT INTO training_passages (id,cefr,title,passage,word_count) VALUES ('{esc(e['id'])}','{e['cefr']}','{esc(e['title'])}','{esc(e['passage'])}',{e['word_count']}) ON CONFLICT DO NOTHING;")
    for qi, q in enumerate(e["questions"]):
        qid = f"{e['id']}-Q{qi+1}"
        opts = json.dumps(q["options"], ensure_ascii=False).replace("'","''")
        lines.append(f"INSERT INTO training_questions (id,passage_id,skill,cefr,question,options,answer) VALUES ('{qid}','{e['id']}','reading','{e['cefr']}','{esc(q['q'])}','{opts}','{esc(q['answer'])}') ON CONFLICT DO NOTHING;")
for e in D.grammar_vocab_bank:
    opts = json.dumps(e["options"], ensure_ascii=False).replace("'","''")
    lines.append(f"INSERT INTO training_grammar (id,cefr,type,question,options,answer,explanation) VALUES ('{esc(e['id'])}','{e['cefr']}','{e['type']}','{esc(e['question'])}','{opts}','{esc(e['answer'])}','{esc(e['explanation'])}') ON CONFLICT DO NOTHING;")
for e in D.writing_samples:
    rub = json.dumps(e["rubric"], ensure_ascii=False).replace("'","''")
    lines.append(f"INSERT INTO training_writing_samples (id,cefr,prompt,text,word_count,rubric,note) VALUES ('{esc(e['id'])}','{e['cefr']}','{esc(e['prompt'])}','{esc(e['text'])}',{e['word_count']},'{rub}','{esc(e['note'])}') ON CONFLICT DO NOTHING;")
for e in D.speaking_prompts:
    lines.append(f"INSERT INTO training_speaking (id,cefr,task,prompt,expected,duration_s) VALUES ('{esc(e['id'])}','{e['cefr']}','{esc(e['task'])}','{esc(e['prompt'])}','{esc(e['expected'])}',{e['duration_s']}) ON CONFLICT DO NOTHING;")

sql_path.write_text("\n".join(lines), encoding="utf-8")
print(f"Wrote {sql_path} ({len(lines)} lines)")

# 4. Excel
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

wb = Workbook()
font_title = Font(name="Arial", size=14, bold=True, color="1E293B")
font_sub = Font(name="Arial", size=9, italic=True, color="64748B")
font_hdr = Font(name="Arial", size=9, bold=True, color="FFFFFF")
fill_navy = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
fill_blue = PatternFill(start_color="2563EB", end_color="2563EB", fill_type="solid")
fill_teal = PatternFill(start_color="0D9488", end_color="0D9488", fill_type="solid")
fill_purple = PatternFill(start_color="6D28D9", end_color="6D28D9", fill_type="solid")
fill_slate = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
fill_zebra = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
thin = Side(style="thin", color="CBD5E1")
border = Border(left=thin,right=thin,top=thin,bottom=thin)
ac = Alignment(horizontal="center", vertical="center", wrap_text=True)
al = Alignment(horizontal="left", vertical="center", wrap_text=True)

def style_header(ws, row, cols, fill):
    for c in range(1, cols+1):
        cell = ws.cell(row=row, column=c)
        cell.font = font_hdr
        cell.fill = fill
        cell.alignment = ac
        cell.border = border

def auto_width(ws, widths):
    for i,w in enumerate(widths, start=1):
        from openpyxl.utils import get_column_letter
        ws.column_dimensions[get_column_letter(i)].width = w

# Sheet 1 Overview
ws = wb.active
ws.title = "Overview"
ws.merge_cells("A1:F1"); ws["A1"]="CEFR FULL TRAINING DATASET — AI English SaaS (Mr Khoirul)"; ws["A1"].font=font_title
ws.merge_cells("A2:F2"); ws["A2"]=f"Listening 36 scripts ({listening_qs} Qs) + Reading 24 passages (54 Qs) + Grammar/Vocab 60 + Writing 36 + Speaking 36 = {len(item_bank)} training entities | Generated {__import__('datetime').date.today().isoformat()}"; ws["A2"].font=font_sub
ws["A4"]="Sheet"; ws["B4"]="Records"; ws["C4"]="CEFR Coverage"; ws["D4"]="Use"; ws["E4"]="TTS / Notes"
style_header(ws,4,5,fill_navy)
overview = [
 ["Listening Scripts","36 scripts / 48 Qs","6 per level A1-C2","Audio Script + MCQ, accent & wpm tagged","TTS: wpm 95-178, duration 20-130s, British/American/Australian"],
 ["Reading Passages","24 passages / 54 Qs","4 per level","Passage 130-712w + MCQ","A1 130-145w → C2 ~700w, headline verified word_count"],
 ["Grammar/Vocab","60 items","10 per level","MCQ grammar & vocab","A1 present simple → C2 idioms/specious/notwithstanding"],
 ["Writing Samples","36 samples","6 per level","Prompt + sample text + rubric 0-5","Word count 17-208w, rubric Content/Communicative/Organisation/Language"],
 ["Speaking Prompts","36 prompts","6 per level","Task + prompt + expected + duration","30-100s, rubric hint per level"],
 ["Item Bank (unified)","252 entities","All","JSON for RAG + adaptive engine","data/item_bank.json"],
]
for i, row in enumerate(overview, start=5):
    for j, v in enumerate(row, start=1):
        c=ws.cell(row=i, column=j, value=v); c.alignment=al; c.border=border; c.font=Font(name="Arial", size=9)
        if i%2==0: c.fill=fill_zebra
auto_width(ws,[22,22,18,32,48]); ws.sheet_properties.pageSetUpPr.fitToPage=True

# Helper to add sheet
def add_sheet(name, headers, rows, fill, widths):
    w = wb.create_sheet(name)
    w.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(headers))
    w.cell(row=1, column=1, value=name).font = Font(name="Arial", size=12, bold=True, color="1E293B")
    for j,h in enumerate(headers, start=1):
        c=w.cell(row=2, column=j, value=h)
        c.font=font_hdr; c.fill=fill; c.alignment=ac; c.border=border
    for i, row in enumerate(rows, start=3):
        for j, v in enumerate(row, start=1):
            c=w.cell(row=i, column=j, value=v); c.alignment=al; c.border=border; c.font=Font(name="Arial", size=8)
            if i%2==1: c.fill=fill_zebra
            # wrap for long text
            if isinstance(v,str) and len(v)>80: c.alignment=Alignment(wrap_text=True, vertical="center")
    auto_width(w,widths)
    w.freeze_panes="A3"; w.auto_filter.ref=f"A2:{chr(64+len(headers))}2"
    w.sheet_properties.pageSetUpPr.fitToPage=True
    return w

# Listening
rows=[]
for e in D.listening_bank:
    for q in e["questions"]:
        rows.append([e["id"], e["cefr"], e["title"], e["accent"], e["wpm"], e["duration_s"], q["q"], " | ".join(q["options"]), q["answer"], e["audio_script"][:220]])
add_sheet("Listening", ["ID","CEFR","Title","Accent","WPM","Dur(s)","Question","Options","Answer","Audio Script (preview)"], rows, fill_blue, [12,7,22,18,7,7,32,32,12,44])

# Reading
rows=[[e["id"], e["cefr"], e["title"], e["word_count"], e["passage"][:300]+"…", " | ".join([q["q"]+" → "+q["answer"] for q in e["questions"]])] for e in D.reading_passages]
add_sheet("Reading", ["ID","CEFR","Title","Words","Passage (preview 300)","Questions → Answers"], rows, fill_teal, [12,7,22,8,50,50])

# Grammar
rows=[[e["id"], e["cefr"], e["type"], e["question"], " | ".join(e["options"]), e["answer"], e["explanation"]] for e in D.grammar_vocab_bank]
add_sheet("GrammarVocab", ["ID","CEFR","Type","Question","Options","Answer","Explanation"], rows, fill_purple, [12,7,10,40,28,14,30])

# Writing
rows=[[e["id"], e["cefr"], e["prompt"], e["text"][:260]+"…", e["word_count"], str(e["rubric"]), e["note"]] for e in D.writing_samples]
add_sheet("Writing", ["ID","CEFR","Prompt","Sample Text (preview)","Words","Rubric","Note"], rows, fill_navy, [12,7,30,46,7,22,34])

# Speaking
rows=[[e["id"], e["cefr"], e["task"], e["prompt"], e["expected"][:180]+"…", e["duration_s"], e.get("rubric_hint","")] for e in D.speaking_prompts]
add_sheet("Speaking", ["ID","CEFR","Task","Prompt","Expected (preview)","Dur(s)","Rubric Hint"], rows, fill_blue, [12,7,20,36,38,7,30])

# Conversions sheet
add_sheet("Conversions", ["CEFR","IELTS","TOEFL 1-6 (2026)","TOEFL 0-120 (legacy)","Score 0-100"], [["A1","<4.0","1.0","0-30","0-19"],["A2","4.0-5.0","2.0","31-45","20-39"],["B1","5.0-6.0","3.0-3.5","42-71","40-59"],["B2","6.5-7.5","4.0-5.0","72-94","60-79"],["C1","8.0-8.5","5.5","95-106","80-92"],["C2","9.0","6.0","107-120","93-100"]], fill_teal, [10,12,16,18,12])

# ItemBank sheet (summary)
rows=[[e["id"], e.get("skill","-"), e.get("cefr","-"), (e.get("question") or e.get("prompt") or e.get("task") or "")[:80], str(e.get("answer") or e.get("text","")[:40])] for e in item_bank[:250]]
add_sheet("ItemBank_252", ["ID","Skill","CEFR","Question/Prompt (80)","Answer/Text preview"], rows, fill_purple, [18,14,7,44,30])

out_xlsx = ROOT / "CEFR_Full_Training_Dataset.xlsx"
wb.save(out_xlsx)
print(f"Wrote {out_xlsx} ({out_xlsx.stat().st_size/1024:.0f} KB, {len(wb.sheetnames)} sheets: {wb.sheetnames})")
