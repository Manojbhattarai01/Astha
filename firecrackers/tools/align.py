# Align script clauses to pauses in the voiceover and write tools/timing.json
import json, re, subprocess, sys
sys.path.insert(0, "/home/user/Astha/firecrackers/tools")
audio = "/home/user/Astha/firecrackers/assets/audio/voice-yash.mp3"
dur = float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",audio],capture_output=True,text=True).stdout)
out = subprocess.run(["ffmpeg","-i",audio,"-af","silencedetect=noise=-32dB:d=0.1","-f","null","-"],capture_output=True,text=True).stderr
ss = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", out)]
se = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", out)]
sil = list(zip(ss, se))
print("dur", dur); print("pauses", [(round(a,2),round(b,2)) for a,b in sil])
import importlib.util
spec = importlib.util.spec_from_file_location("g", "/home/user/Astha/firecrackers/tools/gen_fire.py")
src = open("/home/user/Astha/firecrackers/tools/gen_fire.py").read()
cl = eval(src[src.index("CLAUSES = [")+10:src.index("]\nKEYWORDS")+1])
lens = [len(re.sub(r"[\s।!?…,—:-]", "", t)) for _, t in cl]
tot = sum(lens); c = 0
speech_start = sil[0][1] if sil and sil[0][0] < 0.05 else 0.0
speech_end = sil[-1][0] if sil and sil[-1][1] > dur - 0.05 else dur
for (p, t), l in zip(cl, lens):
    c += l
    print(p, round(speech_start + c / tot * (speech_end - speech_start), 2), t)

# DP: each clause end snaps to a pause start (paragraph ends must) or is interpolated later.
P = [(a, b) for a, b in sil if a > 0.05]
n = len(cl); rate = (speech_end - speech_start) / tot
INF = 1e18
# state: (clause index i ending at pause j)
best = {}
def cost(t0, t1, chars):
    r = (t1 - t0) / chars
    return (r - rate) ** 2 * chars * 100
# dp[i][j] = min cost having clause i end at pause j, prev boundary chosen among pauses
import functools
ends_par = [i + 1 == n or cl[i + 1][0] != cl[i][0] for i in range(n)]
@functools.lru_cache(None)
def f(i, j):
    """min cost for clauses 0..i where clause i ends at pause j (start time of next = P[j][1])."""
    t1 = P[j][0]
    res = (INF, None)
    # clause i starts after some previous anchored boundary k (pause idx) with clauses k_cl+1..i in between (unanchored ones allowed if not paragraph end)
    for i0 in range(i, -1, -1):
        # clauses i0..i form a span between anchors
        if any(ends_par[q] for q in range(i0, i)):
            break
        chars = sum(lens[i0:i + 1])
        if i0 == 0:
            c = cost(speech_start, t1, chars)
            res = min(res, (c, (i0, None)))
        else:
            for k in range(j):
                pc, _ = f(i0 - 1, k)
                if pc >= INF: continue
                c = pc + cost(P[k][1], t1, chars)
                res = min(res, (c, (i0, k)))
    return res
j_last = len(P) - 1
c, _ = f(n - 1, j_last)
# backtrack
anch = {}
i, j = n - 1, j_last
while True:
    anch[i] = j
    c_, (i0, k) = f(i, j)
    if k is None: break
    i, j = i0 - 1, k
# build times: interpolate inside spans
times = []
prev_end_t = speech_start
keys = sorted(anch)
start_i = 0
for i in keys:
    j = anch[i]
    span = list(range(start_i, i + 1))
    t0 = prev_end_t; t1 = P[j][0]
    chars = sum(lens[q] for q in span); acc = 0
    for q in span:
        s = t0 + (t1 - t0) * acc / chars
        acc += lens[q]
        e = t0 + (t1 - t0) * acc / chars
        times.append([round(s + (0.05 if q != span[0] else 0), 2), round(e, 2)])
    prev_end_t = P[j][1]; start_i = i + 1
for (p, t), tm in zip(cl, times): print(p, tm, t)
json.dump({"clauses": times, "total": round(dur + 0.9, 2), "voice_duration": round(dur, 2)}, open("/home/user/Astha/firecrackers/tools/timing.json", "w"), indent=1)
