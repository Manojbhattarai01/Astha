# Build tools/timing.json from ElevenLabs Scribe word timestamps (tools/words.json).
# Usage: python3 tools/words_timing.py <gen module file>
import json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(sys.argv[1]).read()
cl = eval(src[src.index("CLAUSES = [") + 10:src.index("]\nKEYWORDS") + 1])
raw = json.load(open(os.path.join(HERE, "words.json")))
words = raw["words"] if isinstance(raw, dict) and "words" in raw else raw
toks = [w for w in words if w.get("type", "word") == "word" and not re.fullmatch(r"\[.*\]", w["text"].strip()) and w["text"].strip() not in ("—", "-", "")]
out_cl, out_w, k = [], [], 0
for _, text in cl:
    sw = [w for w in text.split() if w not in ("—", "-")]
    ws = []
    for w in sw:
        t = toks[k]
        if re.sub(r"[^ऀ-ॿ]", "", t["text"]) != re.sub(r"[^ऀ-ॿ]", "", w):
            print("mismatch", k, repr(w), repr(t["text"]))
        ws.append([w, round(t["start"], 3), round(t["end"], 3)])
        k += 1
    out_w.append(ws)
    out_cl.append([ws[0][1], ws[-1][2]])
print("script words", k, "transcript words", len(toks))
audio = [f for f in os.listdir(os.path.join(HERE, "..", "assets", "audio")) if f.endswith(".mp3")][0]
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", os.path.join(HERE, "..", "assets", "audio", audio)], capture_output=True, text=True).stdout)
json.dump({"clauses": out_cl, "words": out_w, "total": round(dur + 0.9, 2), "voice_duration": round(dur, 2)}, open(os.path.join(HERE, "timing.json"), "w"), ensure_ascii=False, indent=1)
for (p, t), c in zip(cl, out_cl):
    print(p, c, t[:30])
