# -*- coding: utf-8 -*-
"""Generates the HyperFrames scenes for the Nepali nail-biting explainer.

Timings come from tools/timing.json (made from the voiceover); without it,
times are estimated from the script so the scenes can be previewed early.
"""
import json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "video", "tools"))
from gen import FONT_FACE, C, fmt, rr, label, pop, wobble, intro_js, scene_file  # noqa: E402

OUT = os.path.join(HERE, "..")
W, H = 1080, 1920

# (paragraph, clause text)
CLAUSES = [
    (0, "रोकिनुहोस्!"),
    (0, "नङ टोक्दा,"),
    (0, "तपाईं आफ्नो हातको फोहोर सिधै मुखमा हाल्दै हुनुहुन्छ!"),
    (1, "नङमुनिको सानो खाडलमा,"),
    (1, "औंलाभन्दा धेरै कीटाणु लुकेर बसेका हुन्छन्।"),
    (2, "नङ टोक्दा ती कीटाणु मुखबाट पेटसम्म पुग्छन्,"),
    (2, "र पेटको संक्रमण निम्त्याउन सक्छन्।"),
    (3, "नङ वरिपरिको छाला चिरिँदा,"),
    (3, "ब्याक्टेरिया भित्र पस्छन्…"),
    (3, "र औंला सुन्निने, पाक्ने हुन्छ।"),
    (4, "दाँतलाई पनि असर गर्छ —"),
    (4, "दाँत खिइने, चर्किने,"),
    (4, "र बङ्गारा दुख्ने समस्या आउन सक्छ।"),
    (5, "तर हामी किन टोक्छौं?"),
    (5, "तनाव, चिन्ता वा बोर हुँदा,"),
    (5, "दिमागले यसलाई आराम पाउने बानी बनाउँछ।"),
    (5, "करिब चार जनामा एक जनाले नङ टोक्छन्।"),
    (6, "छुटाउने उपाय:"),
    (6, "नङ छोटो काट्नुहोस्,"),
    (6, "तितो नेल पोलिस लगाउनुहोस्,"),
    (6, "र हात व्यस्त राख्न स्ट्रेस बल चलाउनुहोस्।"),
    (7, "नङ टोक्ने साथीलाई ट्याग गर्नुहोस्,"),
    (7, "र यस्तै रोचक जानकारीका लागि फलो गर्नुहोस्!"),
]
KEYWORDS = ["नङ", "कीटाणु", "पेट", "ब्याक्टेरिया", "दाँत", "तनाव", "बानी", "तितो", "स्ट्रेस", "ट्याग", "फलो", "सुन्निने", "मुखमा", "फोहोर", "बङ्गारा"]
NSCENES = 8


def load_timing():
    p = os.path.join(HERE, "timing.json")
    if os.path.exists(p):
        t = json.load(open(p))
        return [tuple(x) for x in t["clauses"]], t["total"]
    # estimate: 0.075 s per letter, 0.25 s gaps
    out, t = [], 0.15
    for _, text in CLAUSES:
        d = 0.075 * len(text.replace(" ", ""))
        out.append((t, t + d))
        t += d + 0.25
    return out, t + 0.8


TIMES, TOTAL = load_timing()
SCENES = []
for p in range(NSCENES):
    first = next(i for i, (pp, _) in enumerate(CLAUSES) if pp == p)
    SCENES.append(0.0 if p == 0 else round(TIMES[first][0] - 0.12, 2))
DUR = [round((SCENES[i + 1] if i + 1 < NSCENES else TOTAL) - SCENES[i], 2) for i in range(NSCENES)]


def local(p):
    """Clause (start, end) times local to scene p."""
    return [(TIMES[i][0] - SCENES[p], TIMES[i][1] - SCENES[p]) for i, (pp, _) in enumerate(CLAUSES) if pp == p]


SKIN, SKIN2, NAIL, NAILTIP = "#f1b48c", "#e39a6f", "#ffd3dc", "#fff4f6"
GERM_G, GERM_P = "#7ee081", "#b07cff"


def germ(gid, cx, cy, r, color=GERM_G, seed=1, face=True):
    R = rr(seed)
    spikes = "".join(
        f'<circle cx="{fmt(cx + r * 1.02 * math.cos(a))}" cy="{fmt(cy + r * 1.02 * math.sin(a))}" r="{fmt(r * 0.24)}" fill="{color}"/>'
        for a in [k / 8 * 6.283 + R.uniform(-0.2, 0.2) for k in range(8)]
    )
    f = ""
    if face:
        f = (
            f'<circle cx="{fmt(cx - r * 0.32)}" cy="{fmt(cy - r * 0.12)}" r="{fmt(r * 0.24)}" fill="#fff"/>'
            f'<circle cx="{fmt(cx + r * 0.32)}" cy="{fmt(cy - r * 0.12)}" r="{fmt(r * 0.24)}" fill="#fff"/>'
            f'<circle cx="{fmt(cx - r * 0.28)}" cy="{fmt(cy - r * 0.08)}" r="{fmt(r * 0.11)}" fill="#14213d"/>'
            f'<circle cx="{fmt(cx + r * 0.36)}" cy="{fmt(cy - r * 0.08)}" r="{fmt(r * 0.11)}" fill="#14213d"/>'
            f'<path d="M{fmt(cx - r * 0.3)} {fmt(cy + r * 0.35)} Q{fmt(cx)} {fmt(cy + r * 0.6)} {fmt(cx + r * 0.3)} {fmt(cy + r * 0.35)}" stroke="#14213d" stroke-width="{fmt(max(2, r * 0.1))}" fill="none" stroke-linecap="round"/>'
        )
    return f'<g id="{gid}">{spikes}<circle cx="{fmt(cx)}" cy="{fmt(cy)}" r="{fmt(r)}" fill="{color}" stroke="rgba(0,0,0,.25)" stroke-width="{fmt(max(2, r * 0.08))}"/>{f}</g>'


def rod(rid, cx, cy, ang, color=GERM_G):
    return f'<g id="{rid}"><rect x="{fmt(cx - 20)}" y="{fmt(cy - 8)}" width="40" height="16" rx="8" fill="{color}" stroke="#2f7a3a" stroke-width="3" transform="rotate({ang} {fmt(cx)} {fmt(cy)})"/></g>'


# ================= 1: hook =================
def n1(d, c):
    sid = "n1"
    face = (
        f'<g id="n1-face"><circle cx="400" cy="400" r="250" fill="{SKIN}"/>'
        f'<path d="M190 300 Q260 120 420 140 Q590 150 640 300" fill="#2b2233"/>'
        f'<ellipse cx="320" cy="370" rx="26" ry="32" fill="#14213d"/><ellipse cx="480" cy="370" rx="26" ry="32" fill="#14213d"/>'
        f'<circle cx="330" cy="360" r="8" fill="#fff"/><circle cx="490" cy="360" r="8" fill="#fff"/>'
        f'<path d="M280 315 L355 300 M445 300 L520 315" stroke="#14213d" stroke-width="12" stroke-linecap="round"/>'
        f'<ellipse id="n1-mouth" cx="430" cy="500" rx="62" ry="44" fill="#5a1f2b"/>'
        f'<ellipse cx="430" cy="530" rx="34" ry="12" fill="#e2566e"/></g>'
    )
    hand = (
        f'<g id="n1-hand">'
        f'<rect x="640" y="520" width="520" height="190" rx="95" fill="{SKIN2}" transform="rotate(28 640 610)"/>'
        f'<rect x="560" y="470" width="220" height="190" rx="70" fill="{SKIN}"/>'
        f'<rect x="420" y="478" width="200" height="62" rx="31" fill="{SKIN}"/>'
        f'<path d="M430 486 L478 486 Q490 509 478 532 L430 532 Q420 509 430 486 Z" fill="{NAIL}" stroke="#e7a3b2" stroke-width="3"/>'
        f'<rect x="560" y="545" width="200" height="40" rx="20" fill="{SKIN2}" opacity="0.5"/>'
        f'<rect x="560" y="595" width="200" height="40" rx="20" fill="{SKIN2}" opacity="0.5"/></g>'
    )
    germs = "".join(germ(f"n1-g{i}", 470, 509, 22, GERM_G if i % 2 else GERM_P, seed=10 + i) for i in range(5))
    big = germ("n1-big1", 840, 220, 70, GERM_P, seed=3) + germ("n1-big2", 940, 380, 52, GERM_G, seed=4)
    svg = face + hand + germs + big
    title = 'नङ <b>टोक्नुहुन्छ?</b>'
    extra_css = "#n1-title{top:190px;font-size:110px;}"
    extra = (
        label("n1-stop", 540, 330, "रोकिनुहोस्!", color="#fff", bg=C["red"], size=60, anchor="center")
        + label("n1-badge", 540, 1080, "हातको फोहोर सिधै मुखमा", color="#14213d", bg=C["yellow"], size=46, anchor="center")
    )
    js = ""
    js += f'    tl.fromTo("#n1-stop", {{scale:1, rotation:-4, transformOrigin:"50% 50%"}}, {{scale:1.12, rotation:4, duration:0.22, yoyo:true, repeat:{int((d - 0.6) / 0.22) - 1}, ease:"sine.inOut"}}, 0.0);\n'
    js += f'    tl.fromTo("#n1-hand", {{x:0}}, {{x:-22, duration:0.18, yoyo:true, repeat:{int((d - 0.6) / 0.18) - 1}, ease:"sine.inOut"}}, 0.2);\n'
    js += f'    tl.fromTo("#n1-mouth", {{scaleY:1, transformOrigin:"50% 50%"}}, {{scaleY:0.6, duration:0.18, yoyo:true, repeat:{int((d - 0.6) / 0.18) - 1}, ease:"sine.inOut"}}, 0.2);\n'
    # germs hop from the nail into the mouth, one after another
    for i in range(5):
        t = 0.3 + i * 0.55
        n = max(0, int((d - 0.6 - t) / 2.75))
        js += f'    tl.set("#n1-g{i}", {{x:0, y:0, scale:0.4, opacity:0, transformOrigin:"50% 50%"}}, 0);\n'
        js += f'    tl.to("#n1-g{i}", {{keyframes:[{{x:0, y:0, scale:0.4, opacity:0, duration:0.01}}, {{x:-20, y:-70, scale:1, opacity:1, duration:0.35, ease:"power2.out"}}, {{x:-40, y:-10, scale:0.5, duration:0.35, ease:"power2.in"}}, {{opacity:0, duration:0.05}}], repeat:{n}, repeatDelay:2.0}}, {fmt(t)});\n'
    js += wobble("#n1-big1", 0, d - 0.3, 0.08, 0.5)
    js += wobble("#n1-big2", 0.1, d - 0.3, 0.08, 0.45)
    js += pop("#n1-badge", c[2][0])
    return scene_file(sid, d, title, svg, extra, js, extra_css)


# ================= 2: under the nail =================
def n2(d, c):
    sid = "n2"
    finger = (
        f'<rect x="-40" y="120" width="820" height="200" rx="100" fill="{SKIN}"/>'
        f'<rect x="-40" y="260" width="800" height="40" rx="20" fill="{SKIN2}" opacity="0.5"/>'
        f'<path d="M420 96 L780 96 Q880 100 900 150 L900 170 Q860 150 780 150 L420 150 Z" fill="{NAIL}" stroke="#e7a3b2" stroke-width="4"/>'
        f'<path d="M780 96 Q880 100 900 150 L900 170 Q860 150 780 150 Z" fill="{NAILTIP}"/>'
        f'<path id="n2-gap" d="M760 150 Q850 152 900 170 L880 220 Q820 200 760 230 Z" fill="#3b2a30"/>'
    )
    tiny = ""
    R = rr(22)
    for i in range(6):
        tiny += germ(f"n2-t{i}", 800 + R.uniform(-20, 70), 185 + R.uniform(-10, 15), 9, GERM_G if i % 2 else GERM_P, seed=30 + i, face=False)
    bubble = (
        f'<line id="n2-lead" x1="830" y1="210" x2="620" y2="400" stroke="#fff" stroke-width="6" stroke-dasharray="14 10"/>'
        f'<g id="n2-bub"><circle cx="540" cy="560" r="210" fill="#2a1a2e" stroke="#fff" stroke-width="10"/></g>'
    )
    many = ""
    for i in range(18):
        a = R.uniform(0, 6.28)
        rr_ = R.uniform(20, 160)
        many += germ(f"n2-m{i}", 540 + rr_ * math.cos(a), 560 + rr_ * math.sin(a) * 0.95, R.uniform(18, 30), GERM_G if i % 3 else GERM_P, seed=50 + i)
    svg = finger + tiny + bubble + f'<g id="n2-many">{many}</g>'
    title = "नङमुनि <b>लुकेका</b> कीटाणु"
    extra = label("n2-l", 540, 1060, "औंलाभन्दा धेरै फोहोर", color="#fff", bg=C["red"], size=48, anchor="center")
    js = intro_js(sid)
    js += f'    tl.fromTo("#n2-gap", {{opacity:0.4}}, {{opacity:1, duration:0.25, yoyo:true, repeat:3}}, {fmt(c[0][0] + 0.2)});\n'
    js += f'    tl.fromTo("#n2-lead", {{opacity:0}}, {{opacity:1, duration:0.3}}, {fmt(c[0][0] + 0.8)});\n'
    js += pop("#n2-bub", c[0][0] + 1.0, 0.2, 0.45)
    for i in range(18):
        js += pop(f"#n2-m{i}", c[1][0] + i * (max(0.5, c[1][1] - c[1][0] - 0.5) / 18), 0.1, 0.3)
        per = 0.2 + (i % 4) * 0.04
        js += f'    tl.to("#n2-m{i}", {{scaleX:1.1, scaleY:0.9, duration:{fmt(per)}, yoyo:true, repeat:{max(1, int((d - 0.6 - c[1][0] - 0.4) / per) - 1)}, ease:"sine.inOut"}}, {fmt(c[1][0] + 0.4 + i * 0.05 + 0.3)});\n'
    js += pop("#n2-l", c[1][0] + 1.0)
    return scene_file(sid, d, title, svg, extra, js)


# ================= 3: into the stomach =================
def n3(d, c):
    sid = "n3"
    body = (
        f'<circle cx="540" cy="110" r="95" fill="{SKIN}"/>'
        f'<ellipse id="n3-mouth" cx="540" cy="150" rx="30" ry="16" fill="#5a1f2b"/>'
        f'<rect x="505" y="195" width="70" height="80" fill="{SKIN}"/>'
        f'<rect x="300" y="250" width="480" height="520" rx="150" fill="#3b4a7a"/>'
        f'<path d="M540 160 L540 430" stroke="#f19aa8" stroke-width="40" stroke-linecap="round"/>'
        f'<path d="M540 160 L540 430" stroke="#ffc2cc" stroke-width="16" stroke-linecap="round"/>'
        f'<g id="n3-stomach"><path d="M520 420 C 620 400, 700 470, 680 560 C 660 650, 520 660, 470 610 C 440 580, 500 560, 520 520 Z" fill="#f19aa8" stroke="#c75b6c" stroke-width="8"/></g>'
        f'<path id="n3-red" d="M520 420 C 620 400, 700 470, 680 560 C 660 650, 520 660, 470 610 C 440 580, 500 560, 520 520 Z" fill="{C["red"]}" opacity="0"/>'
    )
    pains = "".join(
        f'<path id="n3-p{i}" d="M{x} {y} l 22 -18 l -10 22 l 26 -10" stroke="{C["yellow"]}" stroke-width="8" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
        for i, (x, y) in enumerate([(700, 470), (420, 520), (690, 610), (420, 620)])
    )
    germs = "".join(germ(f"n3-g{i}", 540, 140, 22, GERM_G if i % 2 else GERM_P, seed=70 + i) for i in range(5))
    hand = f'<g id="n3-hand"><rect x="560" y="120" width="160" height="44" rx="22" fill="{SKIN}"/><rect x="680" y="100" width="150" height="120" rx="45" fill="{SKIN}"/></g>'
    svg = body + germs + hand + pains
    title = "मुखबाट सिधै <b>पेटसम्म</b>"
    extra = label("n3-l", 540, 1060, "पेटको संक्रमण", color="#fff", bg=C["red"], size=50, anchor="center")
    js = intro_js(sid)
    js += f'    tl.fromTo("#n3-hand", {{x:0}}, {{x:-14, duration:0.18, yoyo:true, repeat:7}}, 0.3);\n'
    for i in range(5):
        t = 0.6 + i * 0.45
        js += f'    tl.set("#n3-g{i}", {{y:0, x:0, opacity:0, scale:0.5, transformOrigin:"50% 50%"}}, 0);\n'
        js += f'    tl.to("#n3-g{i}", {{keyframes:[{{opacity:1, scale:1, duration:0.15}}, {{y:290, duration:1.3, ease:"power1.in"}}, {{y:{390 + (i % 3) * 30}, x:{(i - 2) * 35}, duration:0.4, ease:"power2.out"}}]}}, {fmt(t)});\n'
        js += wobble(f"#n3-g{i}", t + 1.9, d - 0.3, 0.12, 0.35)
    t_bad = c[1][0]
    js += f'    tl.to("#n3-red", {{opacity:0.55, duration:0.5}}, {fmt(t_bad)});\n'
    js += f'    tl.fromTo("#n3-stomach, #n3-red", {{x:0}}, {{x:8, duration:0.06, yoyo:true, repeat:{int((d - t_bad - 0.6) / 0.06) - 1}}}, {fmt(t_bad + 0.2)});\n'
    for i in range(4):
        js += f'    tl.fromTo("#n3-p{i}", {{opacity:0, scale:0.3, transformOrigin:"50% 50%"}}, {{opacity:1, scale:1.2, duration:0.25, yoyo:true, repeat:{int((d - t_bad - 0.6) / 0.25) - 1}}}, {fmt(t_bad + 0.2 + i * 0.1)});\n'
    js += pop("#n3-l", t_bad + 0.1)
    return scene_file(sid, d, title, svg, extra, js)


# ================= 4: infected finger (paronychia) =================
def n4(d, c):
    sid = "n4"
    finger = (
        f'<rect x="330" y="60" width="420" height="760" rx="210" fill="{SKIN}"/>'
        f'<ellipse id="n4-swell" cx="540" cy="300" rx="235" ry="250" fill="{C["red"]}" opacity="0"/>'
        f'<path d="M420 180 Q420 110 540 110 Q660 110 660 180 L660 420 Q540 450 420 420 Z" fill="{NAIL}" stroke="#e7a3b2" stroke-width="6"/>'
        f'<path d="M430 170 Q440 120 540 120 Q640 120 650 170 Q540 150 430 170 Z" fill="{NAILTIP}"/>'
        f'<path d="M420 420 Q540 450 660 420" stroke="{SKIN2}" stroke-width="16" fill="none"/>'
        f'<path id="n4-tear" d="M660 400 L690 380 L672 360 L700 340 L680 318 L706 300" stroke="#b3122e" stroke-width="10" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
        f'<circle id="n4-pus" cx="690" cy="430" r="30" fill="#ffe27a" stroke="#d9b23a" stroke-width="5"/>'
    )
    rods = "".join(rod(f"n4-r{i}", 960 + (i % 3) * 30, 200 + i * 55, (i * 37) % 180) for i in range(7))
    svg = finger + rods
    title = "छाला चिरियो… <b>संक्रमण!</b>"
    extra = (
        label("n4-l1", 540, 1060, "ब्याक्टेरिया भित्र पस्छन्", color="#14213d", bg=GERM_G, size=46, anchor="center")
        + label("n4-l2", 540, 1060, "औंला सुन्निने, पाक्ने", color="#fff", bg=C["red"], size=50, anchor="center")
    )
    js = intro_js(sid)
    js += f'    tl.fromTo("#n4-tear", {{opacity:0, scale:0.2, transformOrigin:"0% 100%"}}, {{opacity:1, scale:1, duration:0.4, ease:"power3.out"}}, {fmt(c[0][0] + 0.5)});\n'
    t_in = c[1][0]
    for i in range(7):
        js += f'    tl.fromTo("#n4-r{i}", {{x:0, y:0, rotation:0, transformOrigin:"50% 50%"}}, {{x:{-270 - (i % 3) * 30 + 10}, y:{fmt(350 - (200 + i * 55))}, rotation:{180 + i * 20}, duration:1.2, ease:"power2.in"}}, {fmt(t_in - 0.6 + i * 0.12)});\n'
        js += f'    tl.to("#n4-r{i}", {{opacity:0, scale:0.3, duration:0.25}}, {fmt(t_in + 0.6 + i * 0.12)});\n'
    js += pop("#n4-l1", t_in)
    t_sw = c[2][0]
    js += f'    tl.to("#n4-l1", {{opacity:0, duration:0.15}}, {fmt(t_sw - 0.15)});\n'
    js += f'    tl.fromTo("#n4-swell", {{opacity:0, scale:0.8, transformOrigin:"50% 50%"}}, {{opacity:0.45, scale:1.08, duration:0.8, ease:"power2.out"}}, {fmt(t_sw)});\n'
    js += f'    tl.to("#n4-swell", {{opacity:0.3, scale:1.02, duration:0.4, yoyo:true, repeat:{max(1, int((d - t_sw - 1.2) / 0.4) - 1)}, ease:"sine.inOut"}}, {fmt(t_sw + 0.8)});\n'
    js += pop("#n4-pus", t_sw + 0.6)
    js += pop("#n4-l2", t_sw + 0.1)
    return scene_file(sid, d, title, svg, extra, js).replace('<circle id="n4-pus"', '<circle id="n4-pus" opacity="0"')


# ================= 5: teeth =================
def n5(d, c):
    sid = "n5"
    mouth = f'<rect x="120" y="140" width="840" height="560" rx="260" fill="#5a1f2b"/><ellipse cx="540" cy="620" rx="300" ry="60" fill="#e2566e"/>'
    upper = "".join(f'<rect x="{200 + i * 115}" y="160" width="105" height="170" rx="30" fill="#fbfbf5" stroke="#d8d4c4" stroke-width="4"/>' for i in range(6))
    lower = "".join(f'<rect x="{200 + i * 115}" y="500" width="105" height="160" rx="30" fill="#fbfbf5" stroke="#d8d4c4" stroke-width="4"/>' for i in range(6))
    nail = f'<g id="n5-nail"><rect x="560" y="360" width="520" height="130" rx="65" fill="{SKIN}"/><path d="M500 372 L640 372 L640 478 L500 478 Q470 425 500 372 Z" fill="{NAIL}" stroke="#e7a3b2" stroke-width="4"/></g>'
    crack = f'<path id="n5-crack" d="M440 330 L462 280 L445 250 L470 205" stroke="#5b5b5b" stroke-width="7" fill="none" stroke-linecap="round" stroke-dasharray="160" stroke-dashoffset="160"/>'
    chip = f'<path id="n5-chip" d="M455 300 L500 300 L500 330 L470 330 Z" fill="#fbfbf5" stroke="#d8d4c4" stroke-width="3" opacity="0"/>'
    bolts = "".join(
        f'<path id="n5-b{i}" d="M{x} 380 l -30 50 h 30 l -30 60" stroke="{C["yellow"]}" stroke-width="12" fill="none" stroke-linecap="round" stroke-linejoin="round" opacity="0"/>'
        for i, x in enumerate([90, 1010])
    )
    svg = mouth + f'<g id="n5-lower">{lower}</g>' + nail + f'<g id="n5-upper">{upper}{crack}</g>' + chip + bolts
    title = "<b>दाँतलाई</b> पनि नोक्सान"
    extra = (
        label("n5-l1", 540, 1060, "दाँत खिइने, चर्किने", color="#14213d", bg=C["yellow"], size=48, anchor="center")
        + label("n5-l2", 540, 1060, "बङ्गारा दुख्ने", color="#fff", bg=C["red"], size=50, anchor="center")
    )
    js = intro_js(sid)
    js += f'    tl.fromTo("#n5-upper", {{y:0}}, {{y:40, duration:0.2, yoyo:true, repeat:{int((d - 0.8) / 0.2) - 1}, ease:"power2.in"}}, 0.4);\n'
    js += f'    tl.fromTo("#n5-lower", {{y:0}}, {{y:-30, duration:0.2, yoyo:true, repeat:{int((d - 0.8) / 0.2) - 1}, ease:"power2.in"}}, 0.4);\n'
    t1 = c[1][0]
    js += f'    tl.to("#n5-crack", {{attr:{{"stroke-dashoffset":0}}, duration:0.5, ease:"power2.out"}}, {fmt(t1 + 0.3)});\n'
    js += f'    tl.fromTo("#n5-chip", {{opacity:1, y:0, rotation:0, transformOrigin:"50% 50%"}}, {{y:360, rotation:160, opacity:0, duration:1.2, ease:"power2.in"}}, {fmt(t1 + 0.9)});\n'
    js += pop("#n5-l1", t1)
    t2 = c[2][0]
    js += f'    tl.to("#n5-l1", {{opacity:0, duration:0.15}}, {fmt(t2 - 0.15)});\n'
    js += pop("#n5-l2", t2 + 0.1)
    for i in range(2):
        js += f'    tl.fromTo("#n5-b{i}", {{opacity:0, scale:0.4, transformOrigin:"50% 50%"}}, {{opacity:1, scale:1.15, duration:0.2, yoyo:true, repeat:{max(1, int((d - t2 - 0.6) / 0.2) - 1)}}}, {fmt(t2 + i * 0.1)});\n'
    return scene_file(sid, d, title, svg, extra, js)


# ================= 6: why we do it =================
def n6(d, c):
    sid = "n6"
    brain = (
        f'<g id="n6-brain"><path d="M440 60 C 380 60, 350 110, 370 150 C 330 170, 340 240, 400 250 C 420 290, 500 290, 540 260 C 580 290, 660 290, 680 250 C 740 240, 750 170, 710 150 C 730 110, 700 60, 640 60 C 610 30, 560 40, 540 60 C 520 40, 470 30, 440 60 Z" fill="#f7a8c4" stroke="#c75b8a" stroke-width="8"/>'
        f'<path d="M540 60 L540 260 M420 120 Q460 140 440 180 M660 120 Q620 140 640 180 M410 210 Q450 200 470 230 M670 210 Q630 200 610 230" stroke="#c75b8a" stroke-width="7" fill="none" stroke-linecap="round"/></g>'
    )
    gx, gy, gr = 300, 520, 160
    gauge = (
        f'<g id="n6-gauge"><path d="M{gx - gr} {gy} A {gr} {gr} 0 0 1 {gx - gr * 0.5} {fmt(gy - gr * 0.866)}" stroke="#22c55e" stroke-width="34" fill="none"/>'
        f'<path d="M{gx - gr * 0.5} {fmt(gy - gr * 0.866)} A {gr} {gr} 0 0 1 {gx + gr * 0.5} {fmt(gy - gr * 0.866)}" stroke="{C["yellow"]}" stroke-width="34" fill="none"/>'
        f'<path d="M{gx + gr * 0.5} {fmt(gy - gr * 0.866)} A {gr} {gr} 0 0 1 {gx + gr} {gy}" stroke="{C["red"]}" stroke-width="34" fill="none"/>'
        f'<g id="n6-needle"><line x1="{gx}" y1="{gy}" x2="{gx}" y2="{gy - gr + 30}" stroke="#fff" stroke-width="12" stroke-linecap="round"/></g>'
        f'<circle cx="{gx}" cy="{gy}" r="20" fill="#fff"/>'
        f'<text x="{gx}" y="{gy + 70}" text-anchor="middle" font-family="Mukta" font-weight="800" font-size="44" fill="#fff">तनाव</text></g>'
    )
    lx, ly = 790, 430
    loop = (
        f'<g id="n6-loop"><circle cx="{lx}" cy="{ly}" r="140" fill="none" stroke="{C["blue"]}" stroke-width="16" stroke-dasharray="250 40" stroke-linecap="round"/>'
        + "".join(f'<path transform="rotate({a} {lx} {ly})" d="M{lx + 140} {ly - 30} l -24 30 l 48 0 Z" fill="{C["blue"]}"/>' for a in (0, 120, 240))
        + "</g>"
        + f'<text id="n6-habit" x="{lx}" y="{ly + 18}" text-anchor="middle" font-family="Mukta" font-weight="800" font-size="56" fill="#fff">बानी</text>'
    )
    people = ""
    for i in range(4):
        px = 240 + i * 200
        col = C["yellow"] if i == 2 else "#55607a"
        people += f'<g id="n6-p{i}"><circle cx="{px}" cy="660" r="34" fill="{col}"/><rect x="{px - 46}" y="700" width="92" height="80" rx="40" fill="{col}"/></g>'
    svg = brain + gauge + loop + people
    title = "हामी किन <b>टोक्छौं?</b>"
    extra = label("n6-l", 540, 1155 - 95, "चार जनामा एक जना", color="#14213d", bg=C["yellow"], size=46, anchor="center")
    js = intro_js(sid)
    js += wobble("#n6-brain", 0.3, d - 0.3, 0.03, 0.8)
    t_st = c[1][0]
    js += f'    tl.fromTo("#n6-gauge", {{opacity:0, scale:0.6, transformOrigin:"300px 520px"}}, {{opacity:1, scale:1, duration:0.35, ease:"back.out(2)"}}, {fmt(t_st)});\n'
    js += f'    tl.fromTo("#n6-needle", {{rotation:-80, svgOrigin:"300 520"}}, {{rotation:70, duration:1.0, ease:"power2.out"}}, {fmt(t_st + 0.2)});\n'
    js += f'    tl.to("#n6-needle", {{rotation:62, duration:0.08, yoyo:true, repeat:5}}, {fmt(t_st + 1.2)});\n'
    t_h = c[2][0]
    js += f'    tl.to("#n6-needle", {{rotation:-60, duration:0.7, ease:"power2.inOut"}}, {fmt(t_h + 0.6)});\n'
    js += f'    tl.fromTo("#n6-loop", {{opacity:0, rotation:-120, svgOrigin:"790 430"}}, {{opacity:1, rotation:0, duration:0.6, ease:"power3.out"}}, {fmt(t_h + 0.8)});\n'
    js += pop("#n6-habit", t_h + 1.0)
    js += f'    tl.to("#n6-loop", {{rotation:180, duration:{fmt(max(0.5, d - t_h - 1.8))}, ease:"none"}}, {fmt(t_h + 1.4)});\n'
    t_p = c[3][0]
    for i in range(4):
        js += pop(f"#n6-p{i}", t_p + i * 0.12)
    js += f'    tl.fromTo("#n6-p2", {{y:0}}, {{y:-24, duration:0.25, yoyo:true, repeat:{max(1, int((d - t_p - 1.2) / 0.25) - 1)}}}, {fmt(t_p + 0.7)});\n'
    js += pop("#n6-l", t_p + 0.4)
    return scene_file(sid, d, title, svg, extra, js)


# ================= 7: how to stop =================
def n7(d, c):
    sid = "n7"
    rows = [60, 300, 540]
    # row 1: scissors trimming a nail
    r1 = (
        f'<g id="n7-r1"><rect x="40" y="{rows[0]}" width="1000" height="200" rx="40" fill="#151b3d"/>'
        f'<rect x="90" y="{rows[0] + 80}" width="200" height="70" rx="35" fill="{SKIN}"/>'
        f'<path d="M90 {rows[0] + 80} L180 {rows[0] + 80} L180 {rows[0] + 112} L90 {rows[0] + 112} Q78 {rows[0] + 96} 90 {rows[0] + 80} Z" fill="{NAIL}"/>'
        f'<g id="n7-sc"><g id="n7-b1"><line x1="80" y1="{rows[0] + 96}" x2="300" y2="{rows[0] + 40}" stroke="#cfd6e3" stroke-width="12" stroke-linecap="round"/><circle cx="320" cy="{rows[0] + 34}" r="22" fill="none" stroke="{C["red"]}" stroke-width="10"/></g>'
        f'<g id="n7-b2"><line x1="80" y1="{rows[0] + 96}" x2="300" y2="{rows[0] + 152}" stroke="#cfd6e3" stroke-width="12" stroke-linecap="round"/><circle cx="320" cy="{rows[0] + 158}" r="22" fill="none" stroke="{C["red"]}" stroke-width="10"/></g></g>'
        f'<text x="400" y="{rows[0] + 118}" font-family="Mukta" font-weight="800" font-size="58" fill="#fff">नङ छोटो काट्नुहोस्</text></g>'
    )
    # row 2: bitter polish with a yuck face
    r2 = (
        f'<g id="n7-r2"><rect x="40" y="{rows[1]}" width="1000" height="200" rx="40" fill="#151b3d"/>'
        f'<rect x="130" y="{rows[1] + 40}" width="44" height="50" rx="8" fill="#2b2233"/>'
        f'<rect x="100" y="{rows[1] + 86}" width="104" height="100" rx="24" fill="{C["red"]}"/>'
        f'<rect x="112" y="{rows[1] + 100}" width="26" height="60" rx="10" fill="#ffffff" opacity="0.35"/>'
        f'<g id="n7-yuck"><circle cx="300" cy="{rows[1] + 100}" r="56" fill="{C["yellow"]}"/>'
        f'<path d="M272 {rows[1] + 86} l14 8 l-14 8 M328 {rows[1] + 86} l-14 8 l14 8" stroke="#14213d" stroke-width="6" fill="none" stroke-linecap="round"/>'
        f'<path d="M276 {rows[1] + 124} Q300 {rows[1] + 112} 324 {rows[1] + 124}" stroke="#14213d" stroke-width="6" fill="none"/>'
        f'<path d="M296 {rows[1] + 124} q8 26 18 0" fill="#e2566e"/></g>'
        f'<text x="400" y="{rows[1] + 118}" font-family="Mukta" font-weight="800" font-size="58" fill="#fff">तितो नेल पोलिस</text></g>'
    )
    # row 3: stress ball
    r3 = (
        f'<g id="n7-r3"><rect x="40" y="{rows[2]}" width="1000" height="200" rx="40" fill="#151b3d"/>'
        f'<g id="n7-ball"><circle cx="200" cy="{rows[2] + 100}" r="70" fill="{C["blue"]}"/><path d="M150 {rows[2] + 80} Q200 {rows[2] + 50} 250 {rows[2] + 80}" stroke="#ffffff" stroke-width="8" fill="none" opacity="0.5"/></g>'
        f'<text x="400" y="{rows[2] + 118}" font-family="Mukta" font-weight="800" font-size="58" fill="#fff">स्ट्रेस बल चलाउनुहोस्</text></g>'
    )
    svg = r1 + r2 + r3
    title = "छुटाउने <b>३ उपाय</b>"
    js = intro_js(sid)
    for k, row in enumerate(["#n7-r1", "#n7-r2", "#n7-r3"]):
        js += f'    tl.fromTo("{row}", {{opacity:0, x:-120}}, {{opacity:1, x:0, duration:0.4, ease:"power3.out"}}, {fmt(c[k + 1][0])});\n'
    t1 = c[1][0]
    js += f'    tl.fromTo("#n7-b1", {{rotation:0, svgOrigin:"80 {rows[0] + 96}"}}, {{rotation:10, duration:0.18, yoyo:true, repeat:7}}, {fmt(t1 + 0.4)});\n'
    js += f'    tl.fromTo("#n7-b2", {{rotation:0, svgOrigin:"80 {rows[0] + 96}"}}, {{rotation:-10, duration:0.18, yoyo:true, repeat:7}}, {fmt(t1 + 0.4)});\n'
    t2 = c[2][0]
    js += f'    tl.fromTo("#n7-yuck", {{rotation:0, svgOrigin:"300 {rows[1] + 100}"}}, {{rotation:12, duration:0.12, yoyo:true, repeat:9}}, {fmt(t2 + 0.5)});\n'
    t3 = c[3][0]
    js += f'    tl.fromTo("#n7-ball", {{scaleX:1, scaleY:1, svgOrigin:"200 {rows[2] + 100}"}}, {{scaleX:1.25, scaleY:0.75, duration:0.3, yoyo:true, repeat:{max(1, int((d - t3 - 0.9) / 0.3) - 1)}, ease:"sine.inOut"}}, {fmt(t3 + 0.4)});\n'
    return scene_file(sid, d, title, svg, "", js)


# ================= 8: CTA =================
def n8(d, c):
    sid = "n8"
    g = germ("n8-g", 540, 190, 120, GERM_G, seed=99)
    sweat = f'<path id="n8-sw" d="M700 120 q 16 30 0 44 q -16 -14 0 -44 Z" fill="{C["blue"]}"/>'
    tag = (
        f'<g id="n8-tag" transform="translate(540 440)"><rect x="-330" y="-62" width="660" height="124" rx="62" fill="#ffffff"/>'
        f'<text x="-250" y="20" text-anchor="middle" font-family="Mukta" font-weight="800" font-size="70" fill="#14213d">@</text>'
        f'<text x="30" y="18" text-anchor="middle" font-family="Mukta" font-weight="800" font-size="52" fill="#14213d">ट्याग गर्नुहोस्</text></g>'
    )
    follow = (
        f'<g id="n8-follow" transform="translate(540 600)"><rect x="-330" y="-62" width="660" height="124" rx="62" fill="{C["red"]}"/>'
        f'<path d="M-260 0 h44 M-238 -22 v44" stroke="#fff" stroke-width="12" stroke-linecap="round"/>'
        f'<text x="30" y="18" text-anchor="middle" font-family="Mukta" font-weight="800" font-size="52" fill="#fff">फलो गर्नुहोस्</text></g>'
    )
    svg = g + sweat + tag + follow
    title = "नङ टोक्ने <b>साथी</b> छ?"
    extra_css = "#n8-title{font-size:96px;}"
    extra = label("n8-bye", 540, 1060, "बाइ बाइ कीटाणु!", color="#14213d", bg=GERM_G, size=46, anchor="center")
    js = intro_js(sid)
    js += f'    tl.fromTo("#n8-g", {{x:0, rotation:0, svgOrigin:"540 190"}}, {{x:30, rotation:8, duration:0.15, yoyo:true, repeat:{int((d - 0.8) / 0.15) - 1}}}, 0.3);\n'
    js += f'    tl.fromTo("#n8-sw", {{y:0, opacity:1}}, {{y:60, opacity:0, duration:0.7, repeat:{int((d - 1) / 0.7) - 1}}}, 0.4);\n'
    js += pop("#n8-tag", c[0][0] + 0.3)
    js += f'    tl.to("#n8-tag", {{scale:1.06, duration:0.25, yoyo:true, repeat:5, transformOrigin:"50% 50%"}}, {fmt(c[0][0] + 0.8)});\n'
    js += pop("#n8-follow", c[1][0] + 0.2)
    js += f'    tl.to("#n8-follow", {{scale:1.06, duration:0.3, yoyo:true, repeat:{max(1, int((d - c[1][0] - 1.0) / 0.3) - 1)}, transformOrigin:"50% 50%"}}, {fmt(c[1][0] + 0.7)});\n'
    js += pop("#n8-bye", 0.9)
    return scene_file(sid, d, title, svg, extra, js, extra_css)


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
.cg{{position:absolute;left:0;right:0;top:1165px;text-align:center;overflow:visible;}}
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
        f'      <div id="n{i + 1}" data-composition-id="n{i + 1}" data-composition-src="compositions/n{i + 1}.html" data-start="{fmt(s)}" data-duration="{fmt(dd)}" data-track-index="1" data-track-kind="graphics" data-width="{W}" data-height="{H}"></div>\n'
        for i, (s, dd) in enumerate(zip(SCENES, DUR))
    )
    audio = ""
    if voice_dur:
        audio = f'      <audio id="voice" class="clip" src="assets/audio/voice-sarita.mp3" data-start="0" data-duration="{fmt(voice_dur)}" data-track-index="3" data-volume="1"></audio>\n'
    return f"""<!doctype html>
<html lang="ne">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="vendor/gsap.min.js"></script>
    <style>
{FONT_FACE}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: {W}px; height: {H}px; overflow: hidden; background: #0c0a1f; font-family: 'Mukta', sans-serif; }}
      #bg {{ position: absolute; inset: 0; background: radial-gradient(circle at 12% 22%, rgba(126,224,129,.28) 0 7px, transparent 8px), radial-gradient(circle at 88% 28%, rgba(176,124,255,.3) 0 9px, transparent 10px), radial-gradient(circle at 78% 82%, rgba(126,224,129,.22) 0 8px, transparent 9px), radial-gradient(circle at 18% 72%, rgba(176,124,255,.25) 0 10px, transparent 11px), radial-gradient(120% 70% at 50% 35%, #2a1d5c 0%, #110d2e 55%, #07051a 100%); }}
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
    fns = [n1, n2, n3, n4, n5, n6, n7, n8]
    for i, fn in enumerate(fns):
        with open(f"{OUT}/compositions/n{i + 1}.html", "w") as f:
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
