# -*- coding: utf-8 -*-
"""Generates the HyperFrames scenes for the Nepali 'how firecrackers work' explainer.

Timings come from tools/timing.json (tools/align.py + tools/snap.py on the voiceover);
without it, times are estimated from the script.
"""
import json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "video", "tools"))
sys.path.insert(0, HERE)
from fire_scenes import SCENE_FNS  # noqa: E402
from gen import FONT_FACE, C, fmt, rr, label, pop, wobble, intro_js, scene_file  # noqa: E402

OUT = os.path.join(HERE, "..")
W, H = 1080, 1920

CLAUSES = [
    (0, "धुम!"),
    (0, "एउटा सानो कागजको पटाका… र यत्रो ठूलो आवाज!"),
    (0, "तर त्यो एक सेकेन्डभित्र, पटाकाभित्र के हुन्छ?"),
    (0, "आज खुल्छ रहस्य!"),
    (1, "पटाकाभित्र हुन्छ बारुद।"),
    (1, "यसमा दुई मुख्य कुरा हुन्छन् — इन्धन, अनि अक्सिजन दिने रसायन।"),
    (1, "अरू आगोलाई हावाबाट अक्सिजन चाहिन्छ, तर बारुदले आफ्नै अक्सिजन बोकेको हुन्छ।"),
    (2, "त्यसैले आगो छुनेबित्तिकै,"),
    (2, "यो सामान्य आगोभन्दा धेरै गुणा छिटो बल्छ,"),
    (2, "र एकैछिनमा धेरै तातो ग्यास बनाउँछ।"),
    (3, "अब त्यो ग्यास बाक्लो कागजभित्र थुनिएको हुन्छ।"),
    (3, "दबाब बढ्दै जान्छ…"),
    (3, "अनि कागज फुट्छ — धुम!"),
    (3, "त्यो फुटाइले हावामा तरङ्ग पठाउँछ, र त्यही हामी आवाजको रूपमा सुन्छौं।"),
    (4, "रंगीन आतिशबाजी झन् रोचक!"),
    (4, "रातो रंगका लागि स्ट्रोन्सियम, हरियोका लागि बेरियम, नीलोका लागि तामा।"),
    (4, "तातोले धातुका इलेक्ट्रोन माथि उफ्रन्छन्, र तल झर्दा आफ्नै रंगको उज्यालो छाड्छन्।"),
    (5, "अनि हवाई? न्युटनको नियम!"),
    (5, "तलतिर तातो ग्यास फाल्छ, र त्यसको उल्टो धक्काले रकेट माथि उड्छ।"),
    (6, "हजार वर्षअघि चीनमा बारुद पत्ता लागेको थियो —"),
    (6, "र अहिले यही विज्ञानले तिहार र दिवालीको रात झिलिमिली बनाउँछ।"),
    (7, "तर सावधान!"),
    (7, "कतिपय पटाकाको आवाज कान बिगार्न सक्ने हदसम्म चर्को हुन्छ।"),
    (7, "हातमा लिएर नपड्काउनुहोस्,"),
    (7, "नपड्केको पटाका फेरि नबाल्नुहोस्,"),
    (7, "र नजिकै पानीको बाल्टिन राख्नुहोस्।"),
    (8, "तपाईंलाई कुन पटाका मन पर्छ?"),
    (8, "कमेन्टमा लेख्नुहोस्, र यो भिडियो साथीलाई सेयर गर्नुहोस्!"),
    (8, "शुभ दीपावली!"),
]
KEYWORDS = ["धुम", "पटाका", "बारुद", "अक्सिजन", "इन्धन", "ग्यास", "दबाब", "तरङ्ग", "स्ट्रोन्सियम", "बेरियम", "तामा", "इलेक्ट्रोन", "न्युटन", "हवाई", "तिहार", "दिवाली", "सावधान", "पानी", "दीपावली", "कमेन्ट", "सेयर", "रहस्य"]
NSCENES = 9


def load_timing():
    p = os.path.join(HERE, "timing.json")
    if os.path.exists(p):
        t = json.load(open(p))
        return [tuple(x) for x in t["clauses"]], t["total"]
    out, t = [], 0.15
    for _, text in CLAUSES:
        d = 0.07 * len(text.replace(" ", ""))
        out.append((t, t + d))
        t += d + 0.25
    return out, t + 0.9


TIMES, TOTAL = load_timing()
SCENES = []
for p in range(NSCENES):
    first = next(i for i, (pp, _) in enumerate(CLAUSES) if pp == p)
    SCENES.append(0.0 if p == 0 else round(TIMES[first][0] - 0.12, 2))
DUR = [round((SCENES[i + 1] if i + 1 < NSCENES else TOTAL) - SCENES[i], 2) for i in range(NSCENES)]


def local(p):
    return [(TIMES[i][0] - SCENES[p], TIMES[i][1] - SCENES[p]) for i, (pp, _) in enumerate(CLAUSES) if pp == p]


# ================= captions + index =================
def caption_groups():
    groups = []
    for (_, text), (s, e) in zip(CLAUSES, TIMES):
        words = text.split()
        chunks, cur = [], []
        for w_ in words:
            trial = cur + [w_]
            if cur and (len(trial) > 4 or len(" ".join(trial)) > 22):
                chunks.append(cur)
                cur = [w_]
            else:
                cur = trial
        if cur:
            chunks.append(cur)
        total = sum(len(" ".join(ch)) for ch in chunks)
        t = s
        for ch in chunks:
            gd = (e - s) * len(" ".join(ch)) / total
            groups.append((ch, t, t + gd))
            t += gd
    return groups


def captions():
    groups = caption_groups()
    html, js = "", ""
    for gi, (words, s, e) in enumerate(groups):
        spans = " ".join(f'<span class="w{" hot" if any(k in w_ for k in KEYWORDS) else ""}">{w_}</span>' for w_ in words)
        html += f'      <div id="cg{gi}" class="cg"><div class="cg-in">{spans}</div></div>\n'
        end = e + 0.12
        if gi + 1 < len(groups):
            end = min(end, groups[gi + 1][1] - 0.001)
        js += f'    tl.fromTo("#cg{gi} .cg-in", {{opacity:0, y:24, scale:0.9}}, {{opacity:1, y:0, scale:1, duration:0.16, ease:"back.out(2.5)"}}, {fmt(max(0.05, s))});\n'
        js += f'    tl.set("#cg{gi} .cg-in", {{opacity:0}}, {fmt(end)});\n'
    return f"""<template>
  <style>
{FONT_FACE}
#root{{position:absolute;inset:0;font-family:'Mukta',sans-serif;}}
.cg{{position:absolute;left:0;right:0;top:1170px;text-align:center;overflow:visible;}}
.cg-in{{display:inline-block;opacity:0;font-weight:800;font-size:66px;line-height:1.25;color:#fff;padding:10px 30px 4px;border-radius:24px;background:rgba(6,8,20,0.62);max-width:900px;}}
.w.hot{{color:#ffd23f;}}
  </style>
  <div id="root" data-composition-id="captions" data-width="{W}" data-height="{H}" data-layout-allow-overlap>
{html}  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{js}    window.__timelines["captions"] = tl;
  </script>
</template>
"""


def index(voice_dur):
    hosts = "".join(
        f'      <div id="f{i + 1}" data-composition-id="f{i + 1}" data-composition-src="compositions/f{i + 1}.html" data-start="{fmt(s)}" data-duration="{fmt(dd)}" data-track-index="1" data-track-kind="graphics" data-width="{W}" data-height="{H}"></div>\n'
        for i, (s, dd) in enumerate(zip(SCENES, DUR))
    )
    audio = ""
    if voice_dur:
        audio = f'      <audio id="voice" class="clip" src="assets/audio/voice-yash.mp3" data-start="0" data-duration="{fmt(voice_dur)}" data-track-index="3" data-volume="1"></audio>\n'
    return f"""<!doctype html>
<html lang="ne">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="vendor/gsap.min.js"></script>
    <style>
{FONT_FACE}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: {W}px; height: {H}px; overflow: hidden; background: #08051a; font-family: 'Mukta', sans-serif; }}
      #bg {{ position: absolute; inset: 0; background: radial-gradient(circle at 12% 18%, #fff 0 2px, transparent 3px), radial-gradient(circle at 30% 8%, #fff 0 2px, transparent 3px), radial-gradient(circle at 72% 14%, #fff 0 2px, transparent 3px), radial-gradient(circle at 90% 26%, #fff 0 2px, transparent 3px), radial-gradient(circle at 55% 30%, rgba(255,255,255,.7) 0 2px, transparent 3px), radial-gradient(circle at 8% 60%, rgba(255,183,3,.25) 0 9px, transparent 10px), radial-gradient(circle at 92% 70%, rgba(255,77,109,.25) 0 10px, transparent 11px), radial-gradient(120% 70% at 50% 30%, #2a1450 0%, #120a2e 55%, #05030f 100%); }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{fmt(TOTAL)}" data-width="{W}" data-height="{H}" data-fps="30">
      <div id="bg" class="clip" data-start="0" data-duration="{fmt(TOTAL)}" data-track-index="0" data-layout-ignore></div>
{hosts}      <div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="{fmt(TOTAL)}" data-track-index="2" data-track-kind="captions" data-width="{W}" data-height="{H}"></div>
{audio}    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
"""


if __name__ == "__main__":
    fns = SCENE_FNS
    for i, fn in enumerate(fns):
        with open(f"{OUT}/compositions/f{i + 1}.html", "w") as f:
            f.write(fn(DUR[i], local(i)))
    with open(f"{OUT}/compositions/captions.html", "w") as f:
        f.write(captions())
    vd = None
    tp = os.path.join(HERE, "timing.json")
    if os.path.exists(tp):
        vd = json.load(open(tp)).get("voice_duration")
    with open(f"{OUT}/index.html", "w") as f:
        f.write(index(vd))
    print("ok total", round(TOTAL, 2), "scenes", DUR)
