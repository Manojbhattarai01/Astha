# -*- coding: utf-8 -*-
"""Generates the HyperFrames scenes for the Nepali left- vs right-handed explainer.

Timings come from tools/timing.json (tools/align.py + tools/snap.py on the voiceover);
without it, times are estimated from the script.
"""
import json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "video", "tools"))
from gen import FONT_FACE, C, fmt, rr, label, pop, wobble, intro_js, scene_file  # noqa: E402

OUT = os.path.join(HERE, "..")
W, H = 1080, 1920

CLAUSES = [
    (0, "दस जनामा एक जना मात्र देब्रे हात चलाउँछन्!"),
    (0, "तपाईं कुन हुनुहुन्छ?"),
    (0, "कोही दायाँ, कोही देब्रे किन हुन्छन्… आज रहस्य खुल्छ!"),
    (1, "सुरुमै एउटा अचम्मको कुरा —"),
    (1, "हाम्रो दिमागको बायाँ भागले शरीरको दायाँ भाग चलाउँछ, र दायाँ भागले देब्रे भाग।"),
    (1, "त्यसैले दायाँ हात चलाउनेको दिमागको बायाँ भाग, हात चलाउनमा बढी सक्रिय हुन्छ।"),
    (2, "अनि यो बानी जन्मपछि मात्र बन्ने होइन!"),
    (2, "आमाको पेटमै, धेरैजसो बच्चाले दायाँ बुढी औंला चुस्छन्…"),
    (2, "र पछि प्रायः दायाँ हात नै चलाउँछन्।"),
    (3, "त्यसो भए कारण के त?"),
    (3, "कुनै एउटा देब्रे जिन छैन।"),
    (3, "सयौं जिनको सानो-सानो असर, गर्भको विकास, र वातावरण —"),
    (3, "सबै मिलेर हात छानिन्छ।"),
    (4, "धेरैजसो मानिसमा, भाषा बुझ्ने काम दिमागको बायाँ भागले गर्छ।"),
    (4, "तर केही देब्रे हात चलाउनेहरूमा, यो काम दायाँ भाग वा दुवै भागमा बाँडिएको हुन सक्छ।"),
    (5, "खेलकुदमा देब्रेहरूलाई फाइदा हुन्छ!"),
    (5, "बक्सिङ, टेनिस वा क्रिकेटमा, विपक्षीलाई देब्रे खेलाडीसँग खेल्ने अभ्यास कम हुन्छ…"),
    (5, "त्यसैले उनीहरूको चाल अनुमान गर्न गाह्रो पर्छ।"),
    (6, "तर संसार दायाँ हातेहरूका लागि बनेको छ!"),
    (6, "कैँची, कापीको स्प्रिङ, कम्प्युटरको माउस…"),
    (6, "अनि लेख्दा, देब्रेहरूको हातमा मसी पोतिन्छ।"),
    (7, "र सबैभन्दा जरुरी कुरा —"),
    (7, "देब्रे हात चलाउनु गल्ती वा खराब बानी होइन।"),
    (7, "यो दिमागको प्राकृतिक बनावट हो।"),
    (7, "त्यसैले बच्चालाई जबरजस्ती दायाँ हात चलाउन नलगाउनुहोस्।"),
    (8, "तपाईं दायाँ कि देब्रे?"),
    (8, "कमेन्टमा लेख्नुहोस्, र देब्रे हात चलाउने साथीलाई ट्याग गर्नुहोस्!"),
]
KEYWORDS = ["देब्रे", "दायाँ", "दिमाग", "बायाँ", "जिन", "गर्भ", "भाषा", "फाइदा", "मसी", "प्राकृतिक", "जबरजस्ती", "कमेन्ट", "ट्याग", "रहस्य", "पेटमै"]
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


SKIN, SKIN2 = "#f1b48c", "#e39a6f"
LEFTC, RIGHTC = "#ff9f43", "#4dabf7"   # left side orange, right side blue


def txt(tid, x, y, s, size=40, color="#fff", anchor="middle"):
    return f'<text id="{tid}" x="{fmt(x)}" y="{fmt(y)}" text-anchor="{anchor}" font-family="Mukta" font-weight="800" font-size="{size}" fill="{color}">{s}</text>'


def hand(gid, cx, cy, s=1.0, left=False, color=SKIN, pen=False):
    """An open hand, palm facing viewer, fingers up. Left hands are mirrored (thumb on the right)."""
    flip = -1 if left else 1
    fingers = "".join(
        f'<rect x="{x}" y="{-150 - h}" width="34" height="{h + 40}" rx="17" fill="{color}"/>'
        for x, h in [(-62, 50), (-24, 75), (14, 68), (50, 40)]
    )
    thumb = f'<rect x="-104" y="-70" width="48" height="120" rx="24" fill="{color}" transform="rotate(-22 -80 40)"/>'
    palm = f'<rect x="-70" y="-120" width="156" height="170" rx="56" fill="{color}"/><rect x="-40" y="50" width="96" height="70" rx="20" fill="{color}"/>'
    lines = f'<path d="M-40 -40 Q10 -20 60 -50 M-30 0 Q15 15 55 -5" stroke="{SKIN2}" stroke-width="6" fill="none" stroke-linecap="round"/>'
    p = ""
    if pen:
        p = f'<g transform="rotate(30)"><rect x="-10" y="-260" width="20" height="230" rx="8" fill="{C["yellow"]}"/><path d="M-10 -30 L10 -30 L0 0 Z" fill="#14213d"/></g>'
    return f'<g id="{gid}"><g transform="translate({fmt(cx)} {fmt(cy)}) scale({fmt(s * flip)} {fmt(s)})">{p}{thumb}{fingers}{palm}{lines}</g></g>'


def person(pid, x, y, color, s=1.0):
    return f'<g id="{pid}"><circle cx="{fmt(x)}" cy="{fmt(y)}" r="{fmt(30 * s)}" fill="{color}"/><rect x="{fmt(x - 40 * s)}" y="{fmt(y + 38 * s)}" width="{fmt(80 * s)}" height="{fmt(80 * s)}" rx="{fmt(36 * s)}" fill="{color}"/></g>'


def brain_top(prefix, cx, cy, s=1.0, lcol=LEFTC, rcol=RIGHTC):
    """Brain seen from above: viewer's left = the person's left hemisphere."""
    L = f'<path id="{prefix}-L" d="M{fmt(cx - 10 * s)} {fmt(cy - 150 * s)} C {fmt(cx - 160 * s)} {fmt(cy - 160 * s)}, {fmt(cx - 200 * s)} {fmt(cy - 20 * s)}, {fmt(cx - 170 * s)} {fmt(cy + 80 * s)} C {fmt(cx - 140 * s)} {fmt(cy + 160 * s)}, {fmt(cx - 40 * s)} {fmt(cy + 160 * s)}, {fmt(cx - 10 * s)} {fmt(cy + 140 * s)} Z" fill="{lcol}" stroke="rgba(0,0,0,.25)" stroke-width="6"/>'
    R = f'<path id="{prefix}-R" d="M{fmt(cx + 10 * s)} {fmt(cy - 150 * s)} C {fmt(cx + 160 * s)} {fmt(cy - 160 * s)}, {fmt(cx + 200 * s)} {fmt(cy - 20 * s)}, {fmt(cx + 170 * s)} {fmt(cy + 80 * s)} C {fmt(cx + 140 * s)} {fmt(cy + 160 * s)}, {fmt(cx + 40 * s)} {fmt(cy + 160 * s)}, {fmt(cx + 10 * s)} {fmt(cy + 140 * s)} Z" fill="{rcol}" stroke="rgba(0,0,0,.25)" stroke-width="6"/>'
    sq = "".join(
        f'<path d="M{fmt(cx + k * 70 * s)} {fmt(cy + yy * s)} q {fmt(k * 40 * s)} {fmt(-25 * s)} {fmt(k * 80 * s)} 0" stroke="rgba(0,0,0,.22)" stroke-width="{fmt(6 * s)}" fill="none" stroke-linecap="round"/>'
        for k in (-1, 1) for yy in (-80, 0, 80)
    )
    return L + R + sq


# ================= 1: hook =================
def z1(d, c):
    sid = "z1"
    lh = hand("z1-lh", 300, 330, 1.05, left=True, color="#ffb37a")
    rh = hand("z1-rh", 780, 330, 1.05, left=False, color="#8cc8ff")
    vs = txt("z1-vs", 540, 300, "VS", 90, C["yellow"])
    people = "".join(person(f"z1-p{i}", 95 + i * 99, 600, LEFTC if i == 6 else "#55607a", 0.8) for i in range(10))
    svg = lh + rh + vs + people + txt("z1-ll", 300, 520, "देब्रे", 50, LEFTC) + txt("z1-rl", 780, 520, "दायाँ", 50, RIGHTC)
    title = '<b>दायाँ</b> कि <b>देब्रे?</b>'
    extra_css = "#z1-title{top:180px;font-size:118px;}"
    extra = (
        label("z1-chip", 540, 1075, "१० जनामा १ जना मात्र देब्रे!", color="#14213d", bg=C["yellow"], size=48, anchor="center")
    )
    js = ""
    js += f'    tl.fromTo("#z1-lh", {{rotation:0, svgOrigin:"300 380"}}, {{rotation:-10, duration:0.35, yoyo:true, repeat:{int((d - 0.6) / 0.35) - 1}, ease:"sine.inOut"}}, 0.05);\n'
    js += f'    tl.fromTo("#z1-rh", {{rotation:0, svgOrigin:"780 380"}}, {{rotation:10, duration:0.35, yoyo:true, repeat:{int((d - 0.6) / 0.35) - 1}, ease:"sine.inOut"}}, 0.05);\n'
    js += f'    tl.fromTo("#z1-vs", {{scale:1, transformOrigin:"50% 50%"}}, {{scale:1.2, duration:0.25, yoyo:true, repeat:{int((d - 0.6) / 0.25) - 1}, ease:"sine.inOut"}}, 0.1);\n'
    js += f'    tl.fromTo("#z1-p6", {{y:0}}, {{y:-22, duration:0.25, yoyo:true, repeat:{int((d - 0.8) / 0.25) - 1}}}, 0.3);\n'
    js += f'    tl.fromTo("#z1-chip", {{scale:1}}, {{scale:1.06, duration:0.3, yoyo:true, repeat:{int((d - 1) / 0.3) - 1}, transformOrigin:"50% 50%"}}, 0.4);\n'
    return scene_file(sid, d, title, svg, extra, js, extra_css)


# ================= 2: crossed wiring =================
def z2(d, c):
    sid = "z2"
    br = brain_top("z2", 540, 190, 0.9)
    tl_ = txt("z2-tl", 330, 60, "बायाँ भाग", 38, LEFTC)
    tr = txt("z2-tr", 750, 60, "दायाँ भाग", 38, RIGHTC)
    # body: viewer sees the person from behind, so their left is on the viewer's left
    body = f'<circle cx="540" cy="440" r="48" fill="{SKIN}"/><rect x="460" y="495" width="160" height="200" rx="60" fill="#3b4a7a"/>'
    lh = hand("z2-lh", 300, 640, 0.55, left=True)
    rh = hand("z2-rh", 780, 640, 0.55, left=False)
    arms = f'<path d="M470 540 Q380 560 320 610" stroke="#3b4a7a" stroke-width="40" fill="none" stroke-linecap="round"/><path d="M610 540 Q700 560 760 610" stroke="#3b4a7a" stroke-width="40" fill="none" stroke-linecap="round"/>'
    x1 = f'<path id="z2-x1" d="M430 240 C 520 380, 700 470, 780 600" stroke="{LEFTC}" stroke-width="12" fill="none" stroke-dasharray="22 14" stroke-linecap="round"/>'
    x2 = f'<path id="z2-x2" d="M650 240 C 560 380, 380 470, 300 600" stroke="{RIGHTC}" stroke-width="12" fill="none" stroke-dasharray="22 14" stroke-linecap="round"/>'
    glow = f'<circle id="z2-glow" cx="780" cy="620" r="110" fill="{LEFTC}" opacity="0"/>'
    svg = glow + arms + body + lh + rh + br + tl_ + tr + x1 + x2
    title = "दिमागको <b>उल्टो</b> तार"
    extra = label("z2-l", 540, 1080, "बायाँ दिमाग → दायाँ हात", color="#14213d", bg=LEFTC, size=46, anchor="center")
    js = intro_js(sid)
    t1 = c[1][0]
    js += f'    tl.fromTo("#z2-x1", {{opacity:0, attr:{{"stroke-dashoffset":200}}}}, {{opacity:1, attr:{{"stroke-dashoffset":0}}, duration:0.8}}, {fmt(t1 + 0.3)});\n'
    js += f'    tl.to("#z2-x1", {{attr:{{"stroke-dashoffset":-360}}, duration:{fmt(max(1, d - t1 - 1.4))}, ease:"none"}}, {fmt(t1 + 1.1)});\n'
    js += f'    tl.fromTo("#z2-x2", {{opacity:0, attr:{{"stroke-dashoffset":200}}}}, {{opacity:1, attr:{{"stroke-dashoffset":0}}, duration:0.8}}, {fmt(t1 + 2.6)});\n'
    js += f'    tl.to("#z2-x2", {{attr:{{"stroke-dashoffset":-360}}, duration:{fmt(max(1, d - t1 - 3.6))}, ease:"none"}}, {fmt(t1 + 3.4)});\n'
    js += f'    tl.fromTo("#z2-L", {{opacity:1}}, {{opacity:0.55, duration:0.3, yoyo:true, repeat:3}}, {fmt(t1 + 0.3)});\n'
    js += f'    tl.fromTo("#z2-R", {{opacity:1}}, {{opacity:0.55, duration:0.3, yoyo:true, repeat:3}}, {fmt(t1 + 2.6)});\n'
    t2 = c[2][0]
    js += f'    tl.to("#z2-glow", {{opacity:0.45, duration:0.4}}, {fmt(t2 + 0.3)});\n'
    js += f'    tl.to("#z2-glow", {{scale:1.15, transformOrigin:"50% 50%", duration:0.4, yoyo:true, repeat:{max(1, int((d - t2 - 1) / 0.4) - 1)}}}, {fmt(t2 + 0.7)});\n'
    js += f'    tl.to("#z2-x2", {{opacity:0.25, duration:0.3}}, {fmt(t2 + 0.2)});\n'
    js += pop("#z2-l", t2 + 0.2)
    return scene_file(sid, d, title, svg, extra, js)


# ================= 3: it starts in the womb =================
def z3(d, c):
    sid = "z3"
    womb = (
        f'<g id="z3-womb"><circle cx="300" cy="380" r="240" fill="#ffb3c1" opacity="0.45"/><circle cx="300" cy="380" r="240" fill="none" stroke="#ff8fa3" stroke-width="8"/>'
        f'<ellipse cx="320" cy="450" rx="120" ry="90" fill="{SKIN}"/>'
        f'<circle cx="260" cy="320" r="85" fill="{SKIN}"/>'
        f'<path d="M225 310 q 15 10 30 0 M275 310 q 15 10 30 0" stroke="#14213d" stroke-width="6" fill="none" stroke-linecap="round"/>'
        f'<g id="z3-thumb"><rect x="250" y="350" width="70" height="30" rx="15" fill="{SKIN2}"/><rect x="230" y="355" width="40" height="22" rx="11" fill="#f7c6a8"/></g>'
        f'<path d="M320 470 Q 330 400 300 370" stroke="{SKIN2}" stroke-width="30" fill="none" stroke-linecap="round"/></g>'
    )
    tag = f'<g id="z3-tag"><rect x="120" y="640" width="360" height="70" rx="35" fill="#1864ab"/>{txt("z3-tt", 300, 690, "दायाँ बुढी औंला", 40, "#ffffff")}</g>'
    arrow = f'<path id="z3-arrow" d="M560 380 L680 380" stroke="#fff" stroke-width="16" stroke-linecap="round"/><path id="z3-ah" d="M680 350 L730 380 L680 410 Z" fill="#fff"/>'
    kid = (
        f'<g id="z3-kid"><circle cx="880" cy="240" r="80" fill="{SKIN}"/><path d="M800 220 Q 820 140 880 150 Q 950 150 960 220" fill="#2b2233"/>'
        f'<rect x="800" y="320" width="160" height="200" rx="60" fill="#3b4a7a"/>'
        f'<rect x="760" y="560" width="250" height="140" rx="12" fill="#fff"/><path d="M790 600 h150 M790 630 h120 M790 660 h140" stroke="#adb5bd" stroke-width="6"/>'
        + hand("z3-kh", 960, 560, 0.35, left=False, pen=True)
        + "</g>"
    )
    svg = womb + tag + arrow + kid
    title = "<b>गर्भमै</b> सुरु हुन्छ"
    js = intro_js(sid)
    t1 = c[1][0]
    js += pop("#z3-tag", t1 + 0.5)
    js += f'    tl.fromTo("#z3-thumb", {{x:0}}, {{x:-8, duration:0.3, yoyo:true, repeat:{max(1, int((d - t1 - 0.8) / 0.3) - 1)}}}, {fmt(t1 + 0.6)});\n'
    t2 = c[2][0]
    js += f'    tl.fromTo("#z3-arrow, #z3-ah", {{opacity:0, x:-40}}, {{opacity:1, x:0, duration:0.4}}, {fmt(t2)});\n'
    js += pop("#z3-kid", t2 + 0.3)
    js += f'    tl.fromTo("#z3-kh", {{x:0, y:0}}, {{x:-40, y:10, duration:0.35, yoyo:true, repeat:{max(1, int((d - t2 - 1) / 0.35) - 1)}, ease:"sine.inOut"}}, {fmt(t2 + 0.7)});\n'
    js = js.replace('tl.fromTo("#z3-kh", {x:0, y:0}', 'tl.fromTo("#z3-kh", {x:0, y:0}')
    return scene_file(sid, d, title, svg, "", js)


# ================= 4: no single gene =================
def z4(d, c):
    sid = "z4"
    one = (
        f'<g id="z4-one"><rect x="380" y="40" width="320" height="110" rx="55" fill="#fff"/>{txt("z4-ot", 540, 112, "\'देब्रे जिन\'", 52, "#14213d")}'
        f'<path id="z4-x" d="M400 50 L680 140 M680 50 L400 140" stroke="{C["red"]}" stroke-width="16" stroke-linecap="round"/></g>'
    )
    # DNA helix
    pts = ""
    for k in range(9):
        y = 230 + k * 32
        ox = 60 * math.sin(k * 0.8)
        pts += f'<line x1="{fmt(200 - ox)}" y1="{y}" x2="{fmt(200 + ox)}" y2="{y}" stroke="#ffffff" stroke-width="6" opacity="0.7"/><circle cx="{fmt(200 - ox)}" cy="{y}" r="10" fill="{RIGHTC}"/><circle cx="{fmt(200 + ox)}" cy="{y}" r="10" fill="{LEFTC}"/>'
    dna = f'<g id="z4-dna">{pts}</g>{txt("z4-dt", 200, 560, "सयौं जिन", 40)}'
    womb = f'<g id="z4-womb"><circle cx="540" cy="360" r="110" fill="#ffb3c1" opacity="0.5"/><circle cx="540" cy="360" r="110" fill="none" stroke="#ff8fa3" stroke-width="6"/><circle cx="520" cy="340" r="40" fill="{SKIN}"/><ellipse cx="555" cy="395" rx="50" ry="35" fill="{SKIN}"/></g>{txt("z4-wt", 540, 560, "गर्भको विकास", 40)}'
    env = (
        f'<g id="z4-env"><path d="M800 400 L880 330 L960 400 Z" fill="{C["red"]}"/><rect x="815" y="400" width="130" height="100" fill="#fff"/><rect x="865" y="440" width="34" height="60" fill="#8d5524"/>'
        f'<circle cx="970" cy="300" r="45" fill="{C["yellow"]}"/><rect x="760" y="430" width="18" height="70" fill="#8d5524"/><circle cx="769" cy="410" r="40" fill="#40c057"/></g>{txt("z4-et", 880, 560, "वातावरण", 40)}'
    )
    sum_ = f'<g id="z4-sum"><path d="M200 600 Q540 700 880 600" stroke="{C["yellow"]}" stroke-width="10" fill="none" stroke-dasharray="18 12"/>' + hand("z4-h", 540, 740, 0.35, left=False, color="#ffd23f") + "</g>"
    svg = one + dna + womb + env + sum_
    title = "कारण <b>एउटा होइन</b>"
    extra = label("z4-l", 540, 1090, "सबै मिलेर हात छानिन्छ", color="#14213d", bg=C["yellow"], size=46, anchor="center")
    js = intro_js(sid)
    js += f'    tl.set("#z4-x", {{opacity:0}}, 0);\n'
    t1 = c[1][0]
    js += pop("#z4-one", max(0.3, t1 - 0.3))
    js += f'    tl.fromTo("#z4-x", {{opacity:0, scale:1.6, transformOrigin:"50% 50%"}}, {{opacity:1, scale:1, duration:0.3, ease:"power4.in"}}, {fmt(t1 + 0.8)});\n'
    t2 = c[2][0]
    for k, (g, tt) in enumerate([("#z4-dna", "#z4-dt"), ("#z4-womb", "#z4-wt"), ("#z4-env", "#z4-et")]):
        tk = t2 + k * (c[2][1] - c[2][0]) / 3
        js += pop(g, tk)
        js += f'    tl.fromTo("{tt}", {{opacity:0}}, {{opacity:1, duration:0.2}}, {fmt(tk + 0.1)});\n'
    js += f'    tl.fromTo("#z4-dna", {{y:0}}, {{y:-12, duration:0.5, yoyo:true, repeat:{max(1, int((d - t2 - 1) / 0.5) - 1)}}}, {fmt(t2 + 0.5)});\n'
    t3 = c[3][0]
    js += pop("#z4-sum", t3 - 0.6)
    js += pop("#z4-l", t3 - 0.6)
    return scene_file(sid, d, title, svg, extra, js)


# ================= 5: language side =================
def z5(d, c):
    sid = "z5"
    a = brain_top("z5a", 280, 330, 0.75, lcol=LEFTC, rcol="#55607a")
    b = brain_top("z5b", 800, 330, 0.75, lcol=LEFTC, rcol=LEFTC)

    def bubble(bid, x, y):
        return f'<g id="{bid}"><rect x="{x - 45}" y="{y - 32}" width="90" height="64" rx="20" fill="#fff"/><path d="M{x - 20} {y + 30} l -10 26 l 30 -26 Z" fill="#fff"/><circle cx="{x - 22}" cy="{y}" r="8" fill="#14213d"/><circle cx="{x}" cy="{y}" r="8" fill="#14213d"/><circle cx="{x + 22}" cy="{y}" r="8" fill="#14213d"/></g>'
    bubbles = bubble("z5-s1", 215, 300) + bubble("z5-s2", 735, 300) + bubble("z5-s3", 865, 300)
    texts = txt("z5-at", 280, 520, "धेरैजसो मानिस", 40) + txt("z5-bt", 800, 520, "केही देब्रेहरू", 40, LEFTC)
    divider = f'<line x1="540" y1="120" x2="540" y2="560" stroke="#fff" stroke-width="4" stroke-dasharray="12 12" opacity="0.5"/>'
    svg = a + b + bubbles + texts + divider
    title = "<b>भाषा</b> दिमागको कुन भागमा?"
    extra = label("z5-l", 540, 1080, "दायाँ वा दुवै भागमा बाँडिन सक्छ", color="#14213d", bg=LEFTC, size=44, anchor="center")
    js = intro_js(sid)
    js += f'    tl.set("#z5b-L, #z5b-R, #z5-s2, #z5-s3, #z5-bt", {{opacity:0}}, 0);\n'
    js += pop("#z5-s1", c[0][0] + 0.8)
    js += f'    tl.fromTo("#z5-s1", {{y:0}}, {{y:-10, duration:0.3, yoyo:true, repeat:{max(1, int((d - 1.5) / 0.3) - 1)}}}, {fmt(c[0][0] + 1.2)});\n'
    t2 = c[1][0]
    js += f'    tl.to("#z5b-L, #z5b-R, #z5-bt", {{opacity:1, duration:0.4}}, {fmt(t2 + 0.2)});\n'
    js += f'    tl.to("#z5-s2", {{opacity:1, duration:0.3}}, {fmt(t2 + 1.2)});\n'
    js += f'    tl.to("#z5-s3", {{opacity:1, duration:0.3}}, {fmt(t2 + 1.8)});\n'
    js += pop("#z5-l", t2 + 1.5)
    return scene_file(sid, d, title, svg, extra, js)


# ================= 6: sports advantage =================
def z6(d, c):
    sid = "z6"
    # two boxers facing each other
    me = (
        f'<g id="z6-me"><circle cx="300" cy="240" r="70" fill="{SKIN}"/><rect x="230" y="320" width="140" height="220" rx="60" fill="{LEFTC}"/>'
        f'<g id="z6-jab"><path d="M330 380 L470 360" stroke="{LEFTC}" stroke-width="40" stroke-linecap="round"/><circle cx="490" cy="358" r="42" fill="{C["red"]}"/></g>'
        f'<path d="M270 380 L360 430" stroke="{LEFTC}" stroke-width="40" stroke-linecap="round"/><circle cx="375" cy="440" r="38" fill="{C["red"]}"/></g>'
        f'{txt("z6-mt", 300, 620, "देब्रे खेलाडी", 40, LEFTC)}'
    )
    them = (
        f'<g id="z6-them"><circle cx="790" cy="240" r="70" fill="#c68642"/><rect x="720" y="320" width="140" height="220" rx="60" fill="{RIGHTC}"/>'
        f'<path d="M760 380 L680 410" stroke="{RIGHTC}" stroke-width="40" stroke-linecap="round"/><circle cx="665" cy="415" r="38" fill="#1c7ed6"/>'
        f'<path d="M820 400 L740 450" stroke="{RIGHTC}" stroke-width="40" stroke-linecap="round"/><circle cx="725" cy="460" r="38" fill="#1c7ed6"/></g>'
        f'{txt("z6-tt", 790, 620, "विपक्षी", 40, RIGHTC)}'
    )
    qs = "".join(txt(f"z6-q{i}", x, y, "?", 90, C["yellow"]) for i, (x, y) in enumerate([(700, 140), (880, 110), (950, 210)]))
    icons = (
        f'<g id="z6-ic"><circle cx="440" cy="90" r="34" fill="none" stroke="#fff" stroke-width="8"/><path d="M465 115 L500 150" stroke="#fff" stroke-width="10" stroke-linecap="round"/>'
        f'<circle cx="560" cy="100" r="30" fill="{C["red"]}"/><path d="M534 82 Q560 100 586 82 M534 118 Q560 100 586 118" stroke="#fff" stroke-width="4" fill="none"/>'
        f'<rect x="650" y="40" width="22" height="120" rx="9" fill="#e9c46a" transform="rotate(25 661 100)"/></g>'
    )
    svg = me + them + qs + icons
    title = "खेलमा <b>देब्रेलाई फाइदा</b>"
    extra = label("z6-l", 540, 1080, "चाल अनुमान गर्न गाह्रो!", color="#14213d", bg=C["yellow"], size=46, anchor="center")
    js = intro_js(sid)
    js += f'    tl.fromTo("#z6-jab", {{x:0}}, {{x:60, duration:0.18, yoyo:true, repeat:{int((d - 1) / 0.18) - 1}, ease:"power2.out"}}, 0.5);\n'
    js += f'    tl.fromTo("#z6-them", {{rotation:0, svgOrigin:"790 540"}}, {{rotation:5, duration:0.36, yoyo:true, repeat:{int((d - 1) / 0.36) - 1}, ease:"sine.inOut"}}, 0.5);\n'
    js += pop("#z6-ic", c[1][0] + 0.3)
    t3 = c[2][0]
    for i in range(3):
        js += pop(f"#z6-q{i}", t3 + i * 0.2)
    js += pop("#z6-l", t3 + 0.3)
    return scene_file(sid, d, title, svg, extra, js)


# ================= 7: a right-handed world =================
def z7(d, c):
    sid = "z7"
    sc = (
        f'<g id="z7-sc"><circle cx="150" cy="200" r="40" fill="none" stroke="{RIGHTC}" stroke-width="14"/><circle cx="150" cy="300" r="40" fill="none" stroke="{RIGHTC}" stroke-width="14"/>'
        f'<path d="M185 215 L330 290 M185 285 L330 210" stroke="#cfd6e3" stroke-width="16" stroke-linecap="round"/></g>'
    )
    book = (
        f'<g id="z7-book"><rect x="420" y="140" width="220" height="220" rx="14" fill="#fff"/>'
        + "".join(f'<circle cx="430" cy="{165 + k * 26}" r="10" fill="none" stroke="#868e96" stroke-width="6"/>' for k in range(8))
        + f'<path d="M460 200 h150 M460 240 h150 M460 280 h120" stroke="#adb5bd" stroke-width="6"/></g>'
    )
    mouse = (
        f'<g id="z7-mouse"><rect x="780" y="150" width="150" height="220" rx="75" fill="#e9ecef"/><line x1="855" y1="150" x2="855" y2="240" stroke="#868e96" stroke-width="5"/>'
        f'<path d="M780 240 Q820 230 855 240" stroke="#868e96" stroke-width="5" fill="none"/><path d="M855 150 Q 870 100 900 80" stroke="#868e96" stroke-width="6" fill="none"/></g>'
    )
    paper = f'<rect x="80" y="470" width="920" height="270" rx="20" fill="#fff"/>'
    line_ = f'<path id="z7-line" d="M140 600 Q 200 560 260 600 T 380 600 T 500 600 T 620 600" stroke="#1c3faa" stroke-width="10" fill="none" stroke-linecap="round" stroke-dasharray="560" stroke-dashoffset="560"/>'
    smear = f'<path id="z7-smear" d="M150 640 Q 300 660 520 640" stroke="#1c3faa" stroke-width="40" fill="none" stroke-linecap="round" opacity="0" />'
    wh = hand("z7-wh", 160, 600, 0.45, left=True, pen=True)
    svg = sc + book + mouse + paper + line_ + smear + wh
    title = "संसार <b>दायाँ हातेहरूको</b>"
    extra = label("z7-l", 540, 1080, "हातमा मसी पोतिन्छ!", color="#fff", bg="#1c3faa", size=46, anchor="center")
    js = intro_js(sid)
    js += f'    tl.set("#z7-sc, #z7-book, #z7-mouse", {{opacity:0}}, 0);\n'
    t1 = c[1][0]
    for k, g in enumerate(["#z7-sc", "#z7-book", "#z7-mouse"]):
        js += pop(g, t1 + k * (c[1][1] - c[1][0]) / 3)
    t2 = c[2][0]
    js += f'    tl.to("#z7-line", {{attr:{{"stroke-dashoffset":0}}, duration:{fmt(max(1, c[2][1] - c[2][0]))}, ease:"none"}}, {fmt(t2)});\n'
    js += f'    tl.to("#z7-wh", {{x:470, duration:{fmt(max(1, c[2][1] - c[2][0]))}, ease:"none"}}, {fmt(t2)});\n'
    js += f'    tl.to("#z7-smear", {{opacity:0.35, duration:{fmt(max(1, c[2][1] - c[2][0]))}}}, {fmt(t2 + 0.3)});\n'
    js += pop("#z7-l", t2 + 0.6)
    return scene_file(sid, d, title, svg, extra, js)


# ================= 8: not a fault =================
def z8(d, c):
    sid = "z8"
    kid = (
        f'<circle cx="420" cy="200" r="90" fill="{SKIN}"/><path d="M335 180 Q 350 90 420 100 Q 500 95 510 180" fill="#2b2233"/>'
        f'<path d="M385 215 q 12 10 24 0 M435 215 q 12 10 24 0" stroke="#14213d" stroke-width="6" fill="none" stroke-linecap="round"/>'
        f'<path id="z8-mouth" d="M395 250 Q 420 270 445 250" stroke="#14213d" stroke-width="6" fill="none" stroke-linecap="round"/>'
        f'<rect x="330" y="290" width="180" height="230" rx="60" fill="{LEFTC}"/>'
        f'<rect x="180" y="500" width="720" height="40" rx="12" fill="#8d5524"/><rect x="250" y="440" width="300" height="70" rx="8" fill="#fff"/>'
        + hand("z8-kh", 320, 470, 0.35, left=True, pen=True)
    )
    grab = f'<g id="z8-grab">{hand("z8-big", 760, 300, 0.75, left=False, color="#c68642")}<path d="M680 380 L380 470" stroke="#c68642" stroke-width="22" stroke-dasharray="20 14" opacity="0.6"/></g>'
    no = f'<g id="z8-no" transform="translate(700 330)"><circle r="150" fill="none" stroke="{C["red"]}" stroke-width="22"/><path d="M-105 105 L105 -105" stroke="{C["red"]}" stroke-width="22"/></g>'
    ok = f'<g id="z8-ok" transform="translate(740 300)"><circle r="56" fill="#22c55e"/><path d="M-26 2 L-8 20 L28 -18" stroke="#fff" stroke-width="12" fill="none" stroke-linecap="round" stroke-linejoin="round"/></g>'
    svg = kid + grab + no + ok
    title = "देब्रे हुनु <b>गल्ती होइन</b>"
    extra = (
        label("z8-l1", 540, 1080, "दिमागको प्राकृतिक बनावट", color="#14213d", bg="#8ce99a", size=46, anchor="center")
        + label("z8-l2", 540, 1080, "जबरजस्ती नगर्नुहोस्!", color="#fff", bg=C["red"], size=50, anchor="center")
    )
    js = intro_js(sid)
    js += f'    tl.set("#z8-no, #z8-ok", {{opacity:0}}, 0);\n'
    js += f'    tl.fromTo("#z8-kh", {{x:0}}, {{x:30, duration:0.4, yoyo:true, repeat:{int((d - 1) / 0.4) - 1}, ease:"sine.inOut"}}, 0.5);\n'
    js += f'    tl.fromTo("#z8-grab", {{x:200, opacity:0}}, {{x:0, opacity:1, duration:0.6, ease:"power2.out"}}, {fmt(c[1][0])});\n'
    js += pop("#z8-no", c[1][0] + 1.4)
    t3 = c[2][0]
    js += f'    tl.to("#z8-grab", {{x:300, opacity:0, duration:0.5}}, {fmt(t3)});\n'
    js += f'    tl.to("#z8-no", {{opacity:0, duration:0.3}}, {fmt(t3)});\n'
    js += pop("#z8-ok", t3 + 0.3)
    js += pop("#z8-l1", t3 + 0.2)
    t4 = c[3][0]
    js += f'    tl.to("#z8-l1", {{opacity:0, duration:0.15}}, {fmt(t4 - 0.15)});\n'
    js += pop("#z8-l2", t4)
    js += f'    tl.fromTo("#z8-ok", {{scale:1}}, {{scale:1.15, duration:0.3, yoyo:true, repeat:{max(1, int((d - t4 - 1) / 0.3) - 1)}, transformOrigin:"50% 50%"}}, {fmt(t4 + 0.4)});\n'
    js = js.replace('tl.fromTo("#z8-ok", {scale:1}, {scale:1.15', 'tl.to("#z8-ok", {scale:1.15').replace('{scale:1.15, duration:0.3, yoyo:true', '{scale:1.15, duration:0.3, yoyo:true')
    return scene_file(sid, d, title, svg, extra, js)


# ================= 9: CTA =================
def z9(d, c):
    sid = "z9"
    lb = (
        f'<g id="z9-lb" transform="translate(300 260)"><rect x="-220" y="-110" width="440" height="220" rx="50" fill="{LEFTC}"/>'
        f'<path d="M-150 0 l 50 -40 v 25 h 60 v 30 h -60 v 25 Z" fill="#14213d"/>{txt("z9-lt", 50, 22, "देब्रे", 72, "#14213d")}</g>'
    )
    rb = (
        f'<g id="z9-rb" transform="translate(780 260)"><rect x="-220" y="-110" width="440" height="220" rx="50" fill="{RIGHTC}"/>'
        f'{txt("z9-rt", -50, 22, "दायाँ", 72, "#14213d")}<path d="M150 0 l -50 -40 v 25 h -60 v 30 h 60 v 25 Z" fill="#14213d"/></g>'
    )
    bub = (
        f'<g id="z9-bub"><rect x="160" y="450" width="760" height="150" rx="40" fill="#fff"/><path d="M260 590 l -40 60 l 100 -60 Z" fill="#fff"/>'
        f'{txt("z9-bt", 540, 545, "कमेन्टमा लेख्नुहोस्!", 60, "#14213d")}</g>'
    )
    tag = f'<g id="z9-tag" transform="translate(540 720)"><rect x="-330" y="-56" width="660" height="112" rx="56" fill="{C["red"]}"/>{txt("z9-tg", 0, 18, "@ देब्रे साथीलाई ट्याग", 50)}</g>'
    svg = lb + rb + bub + tag
    title = "तपाईं <b>कुन?</b>"
    extra_css = "#z9-title{font-size:110px;}"
    js = intro_js(sid)
    js += pop("#z9-lb", 0.3)
    js += pop("#z9-rb", 0.5)
    js += f'    tl.to("#z9-lb", {{scale:1.07, transformOrigin:"50% 50%", duration:0.3, yoyo:true, repeat:{int((d - 1.2) / 0.3) - 1}}}, 0.9);\n'
    js += f'    tl.to("#z9-rb", {{scale:1.07, transformOrigin:"50% 50%", duration:0.3, yoyo:true, repeat:{int((d - 1.5) / 0.3) - 1}}}, 1.2);\n'
    js += pop("#z9-bub", c[1][0])
    js += pop("#z9-tag", c[1][0] + (c[1][1] - c[1][0]) * 0.45)
    return scene_file(sid, d, title, svg, "", js, extra_css)


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
        f'      <div id="z{i + 1}" data-composition-id="z{i + 1}" data-composition-src="compositions/z{i + 1}.html" data-start="{fmt(s)}" data-duration="{fmt(dd)}" data-track-index="1" data-track-kind="graphics" data-width="{W}" data-height="{H}"></div>\n'
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
      html, body {{ margin: 0; width: {W}px; height: {H}px; overflow: hidden; background: #101327; font-family: 'Mukta', sans-serif; }}
      #bg {{ position: absolute; inset: 0; background: radial-gradient(circle at 14% 20%, rgba(255,159,67,.3) 0 7px, transparent 8px), radial-gradient(circle at 86% 30%, rgba(77,171,247,.3) 0 9px, transparent 10px), radial-gradient(circle at 76% 82%, rgba(77,171,247,.22) 0 8px, transparent 9px), radial-gradient(circle at 20% 74%, rgba(255,159,67,.22) 0 10px, transparent 11px), linear-gradient(90deg, rgba(255,159,67,.10) 0%, rgba(0,0,0,0) 50%, rgba(77,171,247,.10) 100%), radial-gradient(120% 70% at 50% 35%, #26304f 0%, #141a33 55%, #080b1c 100%); }}
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
    fns = [z1, z2, z3, z4, z5, z6, z7, z8, z9]
    for i, fn in enumerate(fns):
        with open(f"{OUT}/compositions/z{i + 1}.html", "w") as f:
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
