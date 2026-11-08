# Snap clause boundaries inside paragraphs to nearby pauses in the voiceover.
import json, re, subprocess, sys
proj = sys.argv[1]
t = json.load(open(f"{proj}/tools/timing.json"))
out = subprocess.run(["ffmpeg", "-i", f"{proj}/assets/audio/voice-yash.mp3", "-af", "silencedetect=noise=-32dB:d=0.1", "-f", "null", "-"], capture_output=True, text=True).stderr
sil = list(zip([float(x) for x in re.findall(r"silence_start: ([0-9.]+)", out)], [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", out)]))
c = t["clauses"]
for i in range(len(c) - 1):
    e, nxt = c[i][1], c[i + 1][0]
    if nxt - e > 0.2:
        continue
    near = [p for p in sil if abs(p[0] - e) < 0.7]
    if near:
        p = min(near, key=lambda p: abs(p[0] - e))
        if p[0] > c[i][0] + 0.4 and p[1] < c[i + 1][1] - 0.4:
            c[i][1], c[i + 1][0] = round(p[0], 2), round(p[1], 2)
json.dump(t, open(f"{proj}/tools/timing.json", "w"), indent=1)
print("snapped")
