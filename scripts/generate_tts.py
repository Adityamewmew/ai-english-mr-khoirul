#!/usr/bin/env python3
"""Generate MP3 for all listening scripts via edge-tts (Microsoft free).
Rate mapped from wpm: 150wpm = 0%, others scaled.
Voice mapped from accent field.
"""
import json, pathlib, subprocess, sys, re

DATA = pathlib.Path("data/listening_scripts.json")
OUT = pathlib.Path("data/audio")
OUT.mkdir(parents=True, exist_ok=True)

ACCENT_VOICE = {
    "British (slow)": "en-GB-LibbyNeural",
    "British": "en-GB-SoniaNeural",
    "British academic": "en-GB-ThomasNeural",
    "British (fast, idiomatic)": "en-GB-RyanNeural",
    "American (slow)": "en-US-EmmaMultilingualNeural",
    "American": "en-US-AriaNeural",
    "American academic": "en-US-GuyNeural",
    "Australian": "en-AU-NatashaNeural",
    "Neutral": "en-US-EmmaMultilingualNeural",
    "Mixed (British/American, fast, idiomatic)": "en-GB-SoniaNeural",
    "Mixed": "en-US-AriaNeural",
    "Mixed (British/American, fast, idiomatic)": "en-GB-SoniaNeural",
}
# fallback voices cycle
FALLBACK = {
    "en-GB": ["en-GB-SoniaNeural","en-GB-RyanNeural","en-GB-LibbyNeural","en-GB-ThomasNeural","en-GB-MaisieNeural"],
    "en-US": ["en-US-AriaNeural","en-US-GuyNeural","en-US-EmmaMultilingualNeural","en-US-AndrewNeural"],
    "en-AU": ["en-AU-NatashaNeural","en-AU-WilliamMultilingualNeural"],
}

def wpm_to_rate(wpm: int) -> str:
    # 150 = 0%
    pct = int(round((wpm - 150) / 150 * 100))
    # clamp edge-tts usually -50% to +50% (actually +- 100% allowed but keep)
    pct = max(-40, min(35, pct))
    return f"{pct:+d}%"

def voice_for(accent: str, idx: int) -> str:
    if accent in ACCENT_VOICE:
        return ACCENT_VOICE[accent]
    # heuristic
    if "British" in accent: return FALLBACK["en-GB"][idx % len(FALLBACK["en-GB"])]
    if "Australian" in accent or "AU" in accent: return FALLBACK["en-AU"][idx % len(FALLBACK["en-AU"])]
    return FALLBACK["en-US"][idx % len(FALLBACK["en-US"])]

def sanitize_for_tts(script: str) -> str:
    # edge-tts: strip speaker labels, keep natural pause via comma
    # "Receptionist: Hello." -> "Hello."
    lines=[]
    for line in script.split("\n"):
        if ":" in line:
            # keep after colon
            txt = line.split(":",1)[1].strip()
        else:
            txt=line.strip()
        if txt:
            lines.append(txt)
    text=" ".join(lines)
    # remove brackets that TTS misreads?
    return text

items=json.loads(DATA.read_text(encoding="utf-8"))
manifest={}
for i,e in enumerate(items):
    vid=e["id"]
    accent=e["accent"]
    wpm=e["wpm"]
    voice=voice_for(accent,i)
    rate=wpm_to_rate(wpm)
    text=sanitize_for_tts(e["audio_script"])
    out_file=OUT / f"{vid}.mp3"
    # skip if exists and non-empty
    if out_file.exists() and out_file.stat().st_size>5000:
        print(f"SKIP {vid} exists {out_file.stat().st_size}B")
        manifest[vid]={"file":str(out_file),"voice":voice,"rate":rate,"wpm":wpm,"accent":accent,"title":e["title"],"duration_s":e["duration_s"],"text_preview":text[:120]}
        continue
    cmd=["edge-tts","--voice",voice,f"--rate={rate}","--text",text,"--write-media",str(out_file)]
    print(f"GEN {vid} voice={voice} rate={rate} wpm={wpm} accent={accent} -> {out_file.name}")
    try:
        r=subprocess.run(cmd, capture_output=True, text=True, timeout=45)
        if r.returncode!=0:
            print(f"  ERR {vid}: {r.stderr[:500]}")
        else:
            sz=out_file.stat().st_size if out_file.exists() else 0
            print(f"  OK {sz}B")
            manifest[vid]={"file":str(out_file),"voice":voice,"rate":rate,"wpm":wpm,"accent":accent,"title":e["title"],"duration_s":e["duration_s"],"text_preview":text[:120]}
    except subprocess.TimeoutExpired:
        print(f"  TIMEOUT {vid}")
    except Exception as ex:
        print(f"  EXC {vid}: {ex}")

# write manifest
manifest_path=OUT / "manifest.json"
manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"\nManifest {manifest_path} {len(manifest)} entries")
# summary
total_sz=sum((OUT/f"{k}.mp3").stat().st_size for k in manifest if (OUT/f"{k}.mp3").exists())
print(f"Total audio size: {total_sz/1024:.0f} KB across {len([p for p in OUT.glob('*.mp3')])} files")
