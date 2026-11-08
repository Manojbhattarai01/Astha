# -*- coding: utf-8 -*-
"""Generates the HyperFrames scenes for the Nepali 'why do we yawn' explainer.

Timings come from tools/timing.json (made by tools/align.py from the voiceover);
without it, times are estimated from the script.
"""
import json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "video", "tools"))
from gen import FONT_FACE, C, fmt, rr, label, pop, wobble, intro_js, scene_file  # noqa: E402

OUT = os.path.join(HERE, "..")
W, H = 1080, 1920

CLAUSES = [
    (0, "एउटा चुनौती!"),
    (0, "यो भिडियो सकिनुअघि नै, तपाईंलाई बडुल्की आउनेछ… पक्का!"),
    (0, "र किन आउँछ, त्यो पनि आज थाहा पाउनुहुनेछ।"),
    (1, "बडुल्की सबैलाई आउँछ।"),
    (1, "आमाको पेटभित्रको बच्चाले पनि बडुल्की गर्छ।"),
    (1, "माछा, चरा, कुकुर, बिरालो —"),
    (1, "लगभग सबै जनावरलाई बडुल्की आउँछ।"),
    (2, "पहिले मानिसहरू सोच्थे, शरीरमा अक्सिजन कम भएर बडुल्की आउँछ।"),
    (2, "तर वैज्ञानिकहरूले परीक्षण गर्दा, बढी अक्सिजन दिँदा पनि बडुल्की उत्तिकै आयो।"),
    (2, "त्यो सिद्धान्त गलत साबित भयो।"),
    (3, "अहिलेको सबैभन्दा बलियो कारण — दिमागलाई चिसो पार्नु!"),
    (3, "बडुल्की गर्दा मुख ठूलो खुल्छ, चिसो हावा भित्र जान्छ,"),
    (3, "र बङ्गारा तन्किँदा टाउकोतिर रगतको बहाव बढ्छ।"),
    (4, "यसले दिमागलाई कम्प्युटरको फ्यान जस्तै ठण्डा पार्छ।"),
    (4, "त्यसैले थकित हुँदा, निद्रा लाग्दा वा बोर हुँदा, बढी बडुल्की आउँछ।"),
    (5, "एउटा प्रयोगमा, निधारमा चिसो पट्टी राख्दा,"),
    (5, "मानिसहरूलाई बडुल्की कम आयो!"),
    (6, "अब सबैभन्दा रोचक कुरा — बडुल्की सर्छ!"),
    (6, "अरूले बडुल्की गरेको देख्दा, सुन्दा,"),
    (6, "यहाँसम्म कि यसबारे पढ्दा मात्र पनि हामीलाई बडुल्की आउँछ।"),
    (7, "वैज्ञानिकहरूका अनुसार, यो हाम्रो दिमागको समानुभूतिसँग जोडिएको छ।"),
    (7, "त्यसैले अपरिचितको भन्दा, परिवार र साथीको बडुल्की छिटो सर्छ।"),
    (7, "तपाईंको कुकुरलाई पनि तपाईंको बडुल्की सर्न सक्छ!"),
    (8, "बडुल्की रोक्न चाहनुहुन्छ?"),
    (8, "नाकबाट गहिरो सास लिनुहोस्, वा निधारमा केही चिसो राख्नुहोस्।"),
    (9, "अब इमानदार भएर भन्नुहोस् —"),
    (9, "यो भिडियो हेर्दा तपाईंलाई कति पटक बडुल्की आयो?"),
    (9, "कमेन्टमा लेख्नुहोस्, र साथीलाई सेयर गरेर, उसलाई पनि बडुल्की सार्नुहोस्!"),
]
KEYWORDS = ["बडुल्की", "चुनौती", "अक्सिजन", "गलत", "दिमाग", "चिसो", "फ्यान", "सर्छ", "समानुभूति", "कुकुर", "नाक", "कमेन्ट", "सेयर", "पक्का", "रगत"]
NSCENES = 10


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


SKIN, SKIN2, HAIR = "#f1b48c", "#e39a6f", "#2b2233"
MOUTH, TONGUE = "#5a1f2b", "#e2566e"
COOL, HOT = "#5ad1ff", "#ff7a45"


# ---------- characters ----------
def yface(gid, cx, cy, r, skin=SKIN, hair=True, ears=None, extra=""):
    """A face that yawns: animate #{gid}-mouth scaleY (0.15 closed .. 1 wide open)."""
    e = ""
    if ears == "dog":
        e = f'<ellipse cx="{fmt(cx - r * 0.95)}" cy="{fmt(cy + r * 0.05)}" rx="{fmt(r * 0.32)}" ry="{fmt(r * 0.62)}" fill="#7a4a2a"/><ellipse cx="{fmt(cx + r * 0.95)}" cy="{fmt(cy + r * 0.05)}" rx="{fmt(r * 0.32)}" ry="{fmt(r * 0.62)}" fill="#7a4a2a"/>'
    elif ears == "cat":
        e = f'<path d="M{fmt(cx - r * 0.85)} {fmt(cy - r * 0.35)} L{fmt(cx - r * 0.7)} {fmt(cy - r * 1.2)} L{fmt(cx - r * 0.2)} {fmt(cy - r * 0.85)} Z" fill="{skin}"/><path d="M{fmt(cx + r * 0.85)} {fmt(cy - r * 0.35)} L{fmt(cx + r * 0.7)} {fmt(cy - r * 1.2)} L{fmt(cx + r * 0.2)} {fmt(cy - r * 0.85)} Z" fill="{skin}"/>'
    hr = ""
    if hair:
        hr = f'<path d="M{fmt(cx - r * 0.95)} {fmt(cy - r * 0.2)} Q{fmt(cx - r * 0.8)} {fmt(cy - r * 1.15)} {fmt(cx)} {fmt(cy - r * 1.02)} Q{fmt(cx + r * 0.85)} {fmt(cy - r * 1.1)} {fmt(cx + r * 0.95)} {fmt(cy - r * 0.2)} Q{fmt(cx)} {fmt(cy - r * 0.7)} {fmt(cx - r * 0.95)} {fmt(cy - r * 0.2)} Z" fill="{HAIR}"/>'
    sw = fmt(max(3, r * 0.07))
    eyes = (
        f'<g id="{gid}-eyes"><path d="M{fmt(cx - r * 0.55)} {fmt(cy - r * 0.15)} q {fmt(r * 0.2)} {fmt(r * 0.14)} {fmt(r * 0.4)} 0" stroke="#14213d" stroke-width="{sw}" fill="none" stroke-linecap="round"/>'
        f'<path d="M{fmt(cx + r * 0.15)} {fmt(cy - r * 0.15)} q {fmt(r * 0.2)} {fmt(r * 0.14)} {fmt(r * 0.4)} 0" stroke="#14213d" stroke-width="{sw}" fill="none" stroke-linecap="round"/></g>'
    )
    mouth = (
        f'<g id="{gid}-mouth"><ellipse cx="{fmt(cx)}" cy="{fmt(cy + r * 0.42)}" rx="{fmt(r * 0.3)}" ry="{fmt(r * 0.36)}" fill="{MOUTH}"/>'
        f'<ellipse cx="{fmt(cx)}" cy="{fmt(cy + r * 0.66)}" rx="{fmt(r * 0.18)}" ry="{fmt(r * 0.09)}" fill="{TONGUE}"/></g>'
    )
    blush = f'<circle cx="{fmt(cx - r * 0.62)}" cy="{fmt(cy + r * 0.15)}" r="{fmt(r * 0.12)}" fill="#ff8fa3" opacity="0.5"/><circle cx="{fmt(cx + r * 0.62)}" cy="{fmt(cy + r * 0.15)}" r="{fmt(r * 0.12)}" fill="#ff8fa3" opacity="0.5"/>'
    return f'<g id="{gid}">{e}<circle cx="{fmt(cx)}" cy="{fmt(cy)}" r="{fmt(r)}" fill="{skin}"/>{hr}{blush}{eyes}{mouth}{extra}</g>'


def yawn_js(gid, cx, cy, r, t, dur=1.6, hold=0.5, closed=0.15):
    """One yawn at local time t: mouth opens wide, head tilts back a little, closes."""
    org = f'"{fmt(cx)} {fmt(cy + r * 0.06)}"'
    return (
        f'    tl.to("#{gid}-mouth", {{scaleY:1, scaleX:1.08, duration:{fmt(dur * 0.45)}, ease:"sine.out", svgOrigin:{org}}}, {fmt(t)});\n'
        f'    tl.to("#{gid}-mouth", {{scaleY:{closed}, scaleX:1, duration:{fmt(dur * 0.35)}, ease:"sine.in", svgOrigin:{org}}}, {fmt(t + dur * 0.45 + hold)});\n'
        f'    tl.to("#{gid}", {{rotation:-6, duration:{fmt(dur * 0.45)}, ease:"sine.out", svgOrigin:"{fmt(cx)} {fmt(cy + r)}"}}, {fmt(t)});\n'
        f'    tl.to("#{gid}", {{rotation:0, duration:{fmt(dur * 0.35)}, ease:"sine.in", svgOrigin:"{fmt(cx)} {fmt(cy + r)}"}}, {fmt(t + dur * 0.45 + hold)});\n'
    )


def closed_js(gid, cx, cy, r, value=0.15):
    return f'    tl.set("#{gid}-mouth", {{scaleY:{value}, svgOrigin:"{fmt(cx)} {fmt(cy + r * 0.06)}"}}, 0);\n'


def zzz(zid, x, y, size=40):
    return f'<text id="{zid}" data-layout-ignore x="{x}" y="{y}" font-family="Mukta" font-weight="800" font-size="{size}" fill="{COOL}">Z<tspan font-size="{int(size * 0.75)}" dy="-{int(size * 0.5)}">z</tspan><tspan font-size="{int(size * 0.55)}" dy="-{int(size * 0.4)}">z</tspan></text>'


# ================= 1: hook / challenge =================
def y1(d, c):
    sid = "y1"
    cx, cy, r = 540, 380, 260
    face = yface("y1-f", cx, cy, r)
    watch = (
        f'<g id="y1-watch" transform="translate(880 120)"><circle r="78" fill="#fff"/><circle r="64" fill="#1b2156"/>'
        f'<rect x="-14" y="-108" width="28" height="26" rx="6" fill="#fff"/>'
        f'<g id="y1-hand"><line x1="0" y1="0" x2="0" y2="-50" stroke="{C["yellow"]}" stroke-width="9" stroke-linecap="round"/></g><circle r="9" fill="{C["yellow"]}"/></g>'
    )
    svg = face + zzz("y1-z", 800, 330, 64) + watch
    title = '<b>चुनौती!</b>'
    extra_css = "#y1-title{top:180px;font-size:120px;}"
    extra = (
        label("y1-sub", 540, 340, "भिडियो सकिनुअघि नै बडुल्की आउनेछ!", color="#14213d", bg=C["yellow"], size=46, anchor="center")
        + label("y1-why", 540, 1070, "किन आउँछ? आज थाहा पाउनुहोस्", color="#fff", bg=C["red"], size=44, anchor="center")
    )
    js = ""
    # frame 0: mouth already half open (thumbnail)
    js += f'    tl.set("#y1-f-mouth", {{scaleY:0.7, svgOrigin:"{cx} {fmt(cy + r * 0.06)}"}}, 0);\n'
    t = 0.2
    while t + 2.4 < d - 0.3:
        js += yawn_js("y1-f", cx, cy, r, t, 2.0, 0.4, 0.35)
        t += 2.6
    js += f'    tl.fromTo("#y1-hand", {{rotation:0, svgOrigin:"0 0"}}, {{rotation:360, duration:{fmt(d - 0.4)}, ease:"none"}}, 0);\n'
    js += f'    tl.fromTo("#y1-z", {{y:0, opacity:0.9}}, {{y:-60, opacity:0.2, duration:1.2, repeat:{int((d - 0.5) / 1.2) - 1}}}, 0.0);\n'
    js += f'    tl.fromTo("#y1-title", {{scale:1}}, {{scale:1.08, duration:0.22, yoyo:true, repeat:3, ease:"sine.inOut"}}, 0.05);\n'
    js += f'    tl.fromTo("#y1-sub", {{scale:1}}, {{scale:1.05, duration:0.3, yoyo:true, repeat:{int((d - 1) / 0.3) - 1}, ease:"sine.inOut"}}, 0.6);\n'
    js += pop("#y1-why", c[2][0])
    return scene_file(sid, d, title, svg, extra, js, extra_css)


# ================= 2: everyone yawns =================
def y2(d, c):
    sid = "y2"
    cells = [(270, 150), (810, 150), (270, 420), (810, 420), (270, 670), (810, 670)]
    names = ["बच्चा", "मानिस", "माछा", "चरा", "कुकुर", "बिरालो"]
    parts = []
    # baby in the womb
    bx, by = cells[0]
    parts.append(f'<g id="y2-c0"><circle cx="{bx}" cy="{by}" r="110" fill="#ffb3c1" opacity="0.5"/><circle cx="{bx}" cy="{by}" r="110" fill="none" stroke="#ff8fa3" stroke-width="6"/>'
                 + yface("y2-a0", bx - 10, by - 10, 55, hair=False) + f'<ellipse cx="{bx + 35}" cy="{by + 55}" rx="45" ry="30" fill="{SKIN}"/></g>')
    parts.append(f'<g id="y2-c1">{yface("y2-a1", *cells[1], 100)}</g>')
    fx, fy = cells[2]
    parts.append(f'<g id="y2-c2"><path d="M{fx + 70} {fy} L{fx + 140} {fy - 55} L{fx + 140} {fy + 55} Z" fill="#ffa94d"/>'
                 f'<ellipse cx="{fx}" cy="{fy}" rx="110" ry="75" fill="#ffa94d"/>'
                 + f'<circle cx="{fx - 50}" cy="{fy - 20}" r="12" fill="#14213d"/>'
                 + f'<g id="y2-a2-mouth"><ellipse cx="{fx - 95}" cy="{fy + 15}" rx="22" ry="28" fill="{MOUTH}"/></g></g>')
    qx, qy = cells[3]
    parts.append(f'<g id="y2-c3"><circle cx="{qx}" cy="{qy}" r="95" fill="#74c0fc"/><circle cx="{qx - 30}" cy="{qy - 25}" r="12" fill="#14213d"/>'
                 f'<path d="M{qx + 50} {qy} L{qx + 140} {qy - 10} L{qx + 60} {qy - 35} Z" fill="#ffd43b"/>'
                 f'<g id="y2-a3-mouth"><path d="M{qx + 50} {qy + 5} L{qx + 140} {qy + 20} L{qx + 60} {qy + 35} Z" fill="#fab005"/></g></g>')
    parts.append(f'<g id="y2-c4">{yface("y2-a4", *cells[4], 90, skin="#c08552", hair=False, ears="dog")}</g>')
    parts.append(f'<g id="y2-c5">{yface("y2-a5", *cells[5], 90, skin="#ffc078", hair=False, ears="cat")}</g>')
    texts = "".join(f'<text id="y2-n{i}" x="{x}" y="{y + 125}" text-anchor="middle" font-family="Mukta" font-weight="800" font-size="40" fill="#fff">{n}</text>' for i, ((x, y), n) in enumerate(zip(cells, names)))
    svg = "".join(parts) + texts
    title = "<b>सबैलाई</b> बडुल्की आउँछ"
    js = intro_js(sid)
    radii = [55, 100, None, None, 90, 90]
    appear = [c[1][0] + 0.3, c[0][0] + 0.3, c[2][0] + 0.1, c[2][0] + 0.6, c[2][0] + 1.1, c[2][0] + 1.6]
    for i in range(6):
        js += pop(f"#y2-c{i}", appear[i], 0.3, 0.35)
        js += f'    tl.fromTo("#y2-n{i}", {{opacity:0}}, {{opacity:1, duration:0.2}}, {fmt(appear[i] + 0.1)});\n'
        x, y = cells[i]
        if radii[i]:
            cxx, cyy = (x - 10, y - 10) if i == 0 else (x, y)
            js += closed_js(f"y2-a{i}", cxx, cyy, radii[i])
            t = appear[i] + 0.4
            while t + 1.8 < d - 0.3:
                js += yawn_js(f"y2-a{i}", cxx, cyy, radii[i], t, 1.4, 0.3)
                t += 2.4 + (i % 3) * 0.3
        else:
            js += f'    tl.fromTo("#y2-a{i}-mouth", {{scale:0.3, transformOrigin:"50% 50%"}}, {{scale:1.3, duration:0.7, yoyo:true, repeat:{max(1, int((d - appear[i] - 0.8) / 0.7) - 1)}, ease:"sine.inOut"}}, {fmt(appear[i] + 0.3)});\n'
    js += pop("#y2-l", c[3][0])
    extra = label("y2-l", 540, 1090, "लगभग सबै जनावर", color="#14213d", bg=C["yellow"], size=46, anchor="center")
    return scene_file(sid, d, title, svg, extra, js)


# ================= 3: oxygen myth =================
def y3(d, c):
    sid = "y3"
    tank = (
        f'<g id="y3-tank"><rect x="80" y="200" width="170" height="420" rx="60" fill="#1864ab"/><rect x="130" y="150" width="70" height="60" rx="12" fill="#adb5bd"/>'
        f'<text x="165" y="440" text-anchor="middle" font-family="Mukta" font-weight="800" font-size="90" fill="#fff">O<tspan font-size="54" dy="20">2</tspan></text></g>'
    )
    R = rr(33)
    bubbles = "".join(f'<circle id="y3-b{i}" cx="230" cy="{fmt(220 + R.uniform(-10, 10))}" r="{fmt(R.uniform(12, 22))}" fill="none" stroke="{COOL}" stroke-width="5"/>' for i in range(8))
    fx, fy, fr = 720, 380, 210
    face = yface("y3-f", fx, fy, fr)
    stamp = f'<g id="y3-x" transform="translate(540 380)"><rect x="-230" y="-80" width="460" height="160" rx="24" fill="none" stroke="{C["red"]}" stroke-width="16"/><text x="0" y="40" text-anchor="middle" font-family="Mukta" font-weight="800" font-size="120" fill="{C["red"]}">गलत!</text></g>'
    svg = tank + bubbles + face + stamp
    title = "पुरानो सोच: <b>अक्सिजन</b> कम?"
    extra = label("y3-l", 540, 1090, "बढी अक्सिजनमा पनि बडुल्की उत्तिकै", color="#fff", bg="#1c7ed6", size=42, anchor="center")
    js = intro_js(sid)
    js += closed_js("y3-f", fx, fy, fr)
    js += f'    tl.set("#y3-x", {{opacity:0}}, 0);\n'
    t_test = c[1][0]
    for i in range(8):
        js += f'    tl.fromTo("#y3-b{i}", {{x:0, y:0, opacity:0}}, {{x:{fmt(R.uniform(300, 380))}, y:{fmt(R.uniform(80, 200))}, opacity:1, duration:1.4, ease:"sine.out", repeat:{max(0, int((d - t_test - 1.6) / 1.4) - 1)}}}, {fmt(t_test + i * 0.18)});\n'
    t = 0.6
    while t + 1.8 < d - 0.3:
        js += yawn_js("y3-f", fx, fy, fr, t, 1.5, 0.3)
        t += 2.5
    js += pop("#y3-l", t_test + 1.0)
    t_x = c[2][0]
    js += f'    tl.fromTo("#y3-x", {{scale:2.5, opacity:0, rotation:-12, transformOrigin:"50% 50%"}}, {{scale:1, opacity:1, rotation:-8, duration:0.3, ease:"power4.in"}}, {fmt(t_x + 0.4)});\n'
    return scene_file(sid, d, title, svg, extra, js)


# ================= 4: brain cooling =================
def y4(d, c):
    sid = "y4"
    head = (
        f'<path d="M330 700 L330 560 Q230 520 240 420 Q180 400 210 360 L250 330 Q220 120 470 80 Q760 50 820 300 Q860 520 700 620 L700 700 Z" fill="{SKIN}"/>'
        f'<path id="y4-jaw" d="M250 420 Q300 470 400 470" stroke="{SKIN2}" stroke-width="14" fill="none" stroke-linecap="round"/>'
    )
    brain = (
        f'<path id="y4-brain" d="M400 150 C 470 100, 640 100, 720 170 C 790 230, 780 340, 700 370 C 640 400, 520 400, 450 370 C 370 340, 340 220, 400 150 Z" fill="#f7a8c4" stroke="#c75b8a" stroke-width="8"/>'
        f'<path id="y4-hot" d="M400 150 C 470 100, 640 100, 720 170 C 790 230, 780 340, 700 370 C 640 400, 520 400, 450 370 C 370 340, 340 220, 400 150 Z" fill="{HOT}" opacity="0.6"/>'
        f'<path id="y4-cool" d="M400 150 C 470 100, 640 100, 720 170 C 790 230, 780 340, 700 370 C 640 400, 520 400, 450 370 C 370 340, 340 220, 400 150 Z" fill="{COOL}" opacity="0"/>'
        f'<path d="M480 180 Q520 220 490 260 M600 170 Q640 210 610 250 M540 300 Q580 330 640 310" stroke="#c75b8a" stroke-width="7" fill="none" stroke-linecap="round"/>'
    )
    mouth = f'<g id="y4-mouth"><ellipse cx="225" cy="440" rx="40" ry="55" fill="{MOUTH}"/></g>'
    arrows = "".join(
        f'<g id="y4-a{i}"><path d="M{20} {400 + i * 40} L150 {420 + i * 15}" stroke="{COOL}" stroke-width="12" stroke-linecap="round"/><path d="M150 {420 + i * 15} l -26 -16 l 4 30 Z" fill="{COOL}"/></g>'
        for i in range(3)
    )
    blood = "".join(f'<circle id="y4-r{i}" cx="{330 + (i % 3) * 30}" cy="560" r="12" fill="#e03131"/>' for i in range(9))
    therm = (
        f'<g id="y4-therm"><rect x="930" y="120" width="60" height="420" rx="30" fill="#fff"/><circle cx="960" cy="560" r="55" fill="#fff"/>'
        f'<rect id="y4-merc" x="944" y="160" width="32" height="390" rx="16" fill="{C["red"]}"/><circle cx="960" cy="560" r="40" fill="{C["red"]}"/></g>'
    )
    svg = head + brain + mouth + arrows + blood + therm
    title = "कारण: <b>दिमागलाई चिसो</b> पार्नु"
    extra = (
        label("y4-l1", 540, 1090, "चिसो हावा भित्र", color="#14213d", bg=COOL, size=46, anchor="center")
        + label("y4-l2", 540, 1090, "रगतको बहाव बढ्छ", color="#fff", bg="#e03131", size=46, anchor="center")
    )
    js = intro_js(sid)
    js += f'    tl.set("#y4-mouth", {{scaleY:0.2, svgOrigin:"225 410"}}, 0);\n'
    t_air = c[1][0]
    js += f'    tl.to("#y4-mouth", {{scaleY:1, duration:0.8, ease:"sine.out", svgOrigin:"225 410"}}, {fmt(t_air)});\n'
    for i in range(3):
        js += f'    tl.fromTo("#y4-a{i}", {{opacity:0, x:-80}}, {{opacity:1, x:40, duration:0.6, ease:"power1.out", repeat:{max(1, int((d - t_air - 1.0) / 0.6) - 1)}}}, {fmt(t_air + 0.3 + i * 0.15)});\n'
    js += pop("#y4-l1", t_air + 0.2)
    t_bl = c[2][0]
    js += f'    tl.to("#y4-l1", {{opacity:0, duration:0.15}}, {fmt(t_bl - 0.15)});\n'
    js += pop("#y4-l2", t_bl)
    js += f'    tl.fromTo("#y4-jaw", {{opacity:0.4}}, {{opacity:1, duration:0.3, yoyo:true, repeat:3}}, {fmt(t_bl)});\n'
    for i in range(9):
        js += f'    tl.fromTo("#y4-r{i}", {{x:0, y:0, opacity:0}}, {{keyframes:[{{opacity:1, duration:0.1}}, {{x:{120 + (i % 3) * 40}, y:-330, duration:1.1, ease:"sine.inOut"}}, {{opacity:0, duration:0.1}}], repeat:{max(0, int((d - t_bl - 1.6) / 1.3))}}}, {fmt(t_bl + 0.2 + i * 0.12)});\n'
    js += f'    tl.to("#y4-hot", {{opacity:0, duration:{fmt(max(1, d - t_air - 1))}, ease:"sine.inOut"}}, {fmt(t_air + 0.4)});\n'
    js += f'    tl.to("#y4-cool", {{opacity:0.45, duration:{fmt(max(1, d - t_air - 1))}, ease:"sine.inOut"}}, {fmt(t_air + 0.4)});\n'
    js += f'    tl.fromTo("#y4-merc", {{scaleY:1, svgOrigin:"960 550"}}, {{scaleY:0.35, duration:{fmt(max(1, d - t_air - 1))}, ease:"sine.inOut"}}, {fmt(t_air + 0.4)});\n'
    # the keyframes tween above used fromTo; switch to set + to for validity
    js = js.replace('tl.fromTo("#y4-r', 'tl.FROMTO_R("#y4-r')
    lines = []
    for ln in js.split("\n"):
        if "FROMTO_R" in ln:
            sel = ln.split('"')[1]
            lines.append(f'    tl.set("{sel}", {{x:0, y:0, opacity:0}}, 0);')
            ln = ln.replace("tl.FROMTO_R(", "tl.to(").replace("{x:0, y:0, opacity:0}, ", "")
        lines.append(ln)
    js = "\n".join(lines)
    return scene_file(sid, d, title, svg, extra, js)


# ================= 5: like a computer fan =================
def y5(d, c):
    sid = "y5"
    brain = (
        f'<path d="M330 150 C 400 80, 680 80, 750 150 C 830 220, 820 370, 720 400 C 640 430, 440 430, 360 400 C 260 370, 250 220, 330 150 Z" fill="#f7a8c4" stroke="#c75b8a" stroke-width="8"/>'
        f'<path d="M540 110 L540 410 M420 180 Q460 220 430 270 M660 180 Q620 220 650 270" stroke="#c75b8a" stroke-width="7" fill="none" stroke-linecap="round"/>'
    )
    fan = (
        f'<g transform="translate(540 260)"><circle r="150" fill="#1b2156" opacity="0.75"/><circle r="150" fill="none" stroke="#cfd6e3" stroke-width="10"/>'
        f'<g id="y5-blades">' + "".join(f'<path transform="rotate({a})" d="M0 0 C 40 -40, 100 -60, 120 -20 C 80 -10, 40 0, 0 0 Z" fill="{COOL}"/>' for a in (0, 72, 144, 216, 288)) + "</g>"
        f'<circle r="22" fill="#cfd6e3"/></g>'
    )
    wind = "".join(f'<path id="y5-w{i}" d="M{720 + i * 10} {200 + i * 60} q 60 -20 120 0 t 120 0" stroke="{COOL}" stroke-width="8" fill="none" stroke-linecap="round" opacity="0.8"/>' for i in range(3))
    icons = (
        f'<g id="y5-i0" transform="translate(200 640)"><rect x="-80" y="-40" width="150" height="80" rx="14" fill="none" stroke="#fff" stroke-width="8"/><rect x="72" y="-16" width="14" height="32" rx="4" fill="#fff"/><rect x="-68" y="-28" width="34" height="56" rx="6" fill="{C["red"]}"/></g>'
        f'<g id="y5-i1" transform="translate(540 640)"><path d="M20 -60 A 60 60 0 1 0 60 30 A 48 48 0 1 1 20 -60 Z" fill="{C["yellow"]}"/>{zzz("y5-zz", 40, -20, 40)}</g>'
        f'<g id="y5-i2" transform="translate(880 640)"><circle r="62" fill="#fff"/><line x1="0" y1="0" x2="0" y2="-40" stroke="#14213d" stroke-width="8" stroke-linecap="round"/><line x1="0" y1="0" x2="30" y2="10" stroke="#14213d" stroke-width="8" stroke-linecap="round"/></g>'
    )
    labels = "".join(f'<text id="y5-t{i}" x="{x}" y="760" text-anchor="middle" font-family="Mukta" font-weight="800" font-size="40" fill="#fff">{t}</text>' for i, (x, t) in enumerate([(200, "थकित"), (540, "निद्रा"), (880, "बोर")]))
    svg = brain + fan + wind + icons + labels
    title = "दिमागको <b>फ्यान</b> जस्तै"
    js = intro_js(sid)
    js += f'    tl.fromTo("#y5-blades", {{rotation:0, svgOrigin:"0 0"}}, {{rotation:{int(360 * (d / 0.5))}, duration:{fmt(d - 0.3)}, ease:"none"}}, 0.2);\n'
    for i in range(3):
        js += f'    tl.fromTo("#y5-w{i}", {{opacity:0, x:-40}}, {{opacity:0.9, x:40, duration:0.7, repeat:{max(1, int((d - 1) / 0.7) - 1)}, ease:"sine.inOut"}}, {fmt(0.4 + i * 0.2)});\n'
    t2 = c[1][0]
    for i, dt in enumerate([0.6, 1.4, 2.4]):
        js += pop(f"#y5-i{i}", t2 + dt)
        js += f'    tl.fromTo("#y5-t{i}", {{opacity:0}}, {{opacity:1, duration:0.2}}, {fmt(t2 + dt + 0.1)});\n'
    return scene_file(sid, d, title, svg, "", js)


# ================= 6: cold pack experiment =================
def y6(d, c):
    sid = "y6"
    fx, fy, fr = 300, 330, 190
    pack = (
        f'<g id="y6-pack"><rect x="{fx - 150}" y="{fy - 240}" width="300" height="90" rx="40" fill="{COOL}"/>'
        + "".join(f'<path d="M{fx - 110 + k * 60} {fy - 215} l 0 40 M{fx - 130 + k * 60} {fy - 195} l 40 0" stroke="#fff" stroke-width="6" stroke-linecap="round"/>' for k in range(4))
        + "</g>"
    )
    face = yface("y6-f", fx, fy, fr)
    chart = (
        f'<line x1="600" y1="620" x2="1010" y2="620" stroke="#fff" stroke-width="6"/>'
        f'<rect id="y6-bar1" x="630" y="220" width="150" height="400" rx="16" fill="{C["red"]}"/>'
        f'<rect id="y6-bar2" x="830" y="470" width="150" height="150" rx="16" fill="{COOL}"/>'
        f'<text x="705" y="680" text-anchor="middle" font-family="Mukta" font-weight="800" font-size="36" fill="#fff">बिना</text>'
        f'<text x="905" y="680" text-anchor="middle" font-family="Mukta" font-weight="800" font-size="36" fill="#fff">चिसो पट्टी</text>'
        f'<text x="800" y="180" text-anchor="middle" font-family="Mukta" font-weight="800" font-size="40" fill="{C["yellow"]}">बडुल्की</text>'
    )
    svg = face + pack + chart
    title = "<b>प्रयोग:</b> निधारमा चिसो"
    extra = label("y6-l", 540, 1090, "बडुल्की कम आयो!", color="#14213d", bg=C["yellow"], size=50, anchor="center")
    js = intro_js(sid)
    js += closed_js("y6-f", fx, fy, fr)
    js += f'    tl.fromTo("#y6-pack", {{y:-300, opacity:0}}, {{y:0, opacity:1, duration:0.6, ease:"bounce.out"}}, {fmt(c[0][0] + 1.0)});\n'
    js += f'    tl.fromTo("#y6-bar1", {{scaleY:0, svgOrigin:"705 620"}}, {{scaleY:1, duration:0.7, ease:"power2.out"}}, {fmt(c[0][0] + 0.4)});\n'
    js += f'    tl.fromTo("#y6-bar2", {{scaleY:0, svgOrigin:"905 620"}}, {{scaleY:1, duration:0.7, ease:"power2.out"}}, {fmt(c[1][0] + 0.1)});\n'
    js += pop("#y6-l", c[1][0] + 0.3)
    js += yawn_js("y6-f", fx, fy, fr, 0.3, 1.2, 0.2)
    return scene_file(sid, d, title, svg, extra, js)


# ================= 7: contagious chain =================
def y7(d, c):
    sid = "y7"
    xs = [150, 400, 650, 900]
    skins = [SKIN, "#c68642", "#ffdbac", "#8d5524"]
    faces = "".join(yface(f"y7-f{i}", x, 520, 110, skin=skins[i]) for i, x in enumerate(xs))
    eye = f'<g id="y7-eye" transform="translate(260 180)"><path d="M-90 0 Q0 -70 90 0 Q0 70 -90 0 Z" fill="#fff"/><circle r="32" fill="#1c7ed6"/><circle r="14" fill="#14213d"/></g>'
    ear = f'<g id="y7-ear" transform="translate(540 180)"><path d="M-30 -70 C 50 -90, 80 -10, 30 30 C 10 50, 20 80, -10 80" stroke="#fff" stroke-width="18" fill="none" stroke-linecap="round"/><path d="M60 -40 q 30 30 0 60 M85 -60 q 50 50 0 100" stroke="{COOL}" stroke-width="8" fill="none" stroke-linecap="round"/></g>'
    book = f'<g id="y7-book" transform="translate(820 180)"><path d="M0 -50 Q-60 -70 -110 -50 L-110 60 Q-60 40 0 60 Z" fill="#fff"/><path d="M0 -50 Q60 -70 110 -50 L110 60 Q60 40 0 60 Z" fill="#e9ecef"/><path d="M-90 -20 h70 M-90 5 h70 M20 -20 h70 M20 5 h70" stroke="#adb5bd" stroke-width="6"/></g>'
    words = "".join(f'<text id="y7-w{i}" x="{x}" y="{300}" text-anchor="middle" font-family="Mukta" font-weight="800" font-size="40" fill="#fff">{t}</text>' for i, (x, t) in enumerate([(260, "देख्दा"), (540, "सुन्दा"), (820, "पढ्दा")]))
    arrows = "".join(f'<path id="y7-ar{i}" d="M{xs[i] + 70} 400 q 55 -60 110 0" stroke="{C["yellow"]}" stroke-width="8" fill="none" stroke-linecap="round" stroke-dasharray="8 12"/>' for i in range(3))
    svg = eye + ear + book + words + arrows + faces
    title = "बडुल्की <b>सर्छ!</b>"
    js = intro_js(sid)
    js += '    tl.set("#y7-ar0, #y7-ar1, #y7-ar2", {opacity:0}, 0);\n'
    for i, x in enumerate(xs):
        js += closed_js(f"y7-f{i}", x, 520, 110)
    t0 = c[0][0] + 0.4
    for rep in range(2):
        base = t0 + rep * 4.6
        for i, x in enumerate(xs):
            t = base + i * 0.9
            if t + 1.6 < d - 0.3:
                js += yawn_js(f"y7-f{i}", x, 520, 110, t, 1.3, 0.25)
            if i < 3 and t + 0.5 < d - 0.3:
                js += f'    tl.to("#y7-ar{i}", {{opacity:1, duration:0.2, yoyo:true, repeat:1}}, {fmt(t + 0.5)});\n'
    for i, (sel, tt) in enumerate([("#y7-eye", c[1][0] + 0.2), ("#y7-ear", c[1][0] + 1.0), ("#y7-book", c[2][0] + 0.8)]):
        js += pop(sel, tt)
        js += f'    tl.fromTo("#y7-w{i}", {{opacity:0}}, {{opacity:1, duration:0.2}}, {fmt(tt + 0.1)});\n'
    return scene_file(sid, d, title, svg, "", js)


# ================= 8: empathy network =================
def y8(d, c):
    sid = "y8"
    me = yface("y8-me", 540, 330, 120)
    fam = yface("y8-fam", 210, 170, 85, skin="#ffdbac")
    fr_ = yface("y8-fr", 870, 170, 85, skin="#c68642")
    st = yface("y8-st", 210, 560, 80, skin="#9aa6bb", hair=False)
    dog = yface("y8-dog", 870, 560, 80, skin="#c08552", hair=False, ears="dog")
    links = (
        f'<path id="y8-l1" d="M290 200 L430 290" stroke="{C["red"]}" stroke-width="16" stroke-linecap="round"/>'
        f'<path id="y8-l2" d="M790 200 L650 290" stroke="{C["red"]}" stroke-width="16" stroke-linecap="round"/>'
        f'<path id="y8-l3" d="M285 530 L430 400" stroke="#9aa6bb" stroke-width="6" stroke-dasharray="10 14" stroke-linecap="round"/>'
        f'<path id="y8-l4" d="M795 530 L650 400" stroke="{C["yellow"]}" stroke-width="12" stroke-linecap="round"/>'
    )
    hearts = "".join(
        f'<path id="y8-h{i}" transform="translate({x} {y}) scale(1.4)" d="M0 -6 C 0 -16, -16 -16, -16 -4 C -16 6, -4 12, 0 18 C 4 12, 16 6, 16 -4 C 16 -16, 0 -16, 0 -6 Z" fill="{C["red"]}"/>'
        for i, (x, y) in enumerate([(360, 235), (720, 235)])
    )
    names = "".join(f'<text id="y8-n{i}" x="{x}" y="{y}" text-anchor="middle" font-family="Mukta" font-weight="800" font-size="38" fill="#fff">{t}</text>'
                    for i, (x, y, t) in enumerate([(210, 290, "परिवार"), (870, 290, "साथी"), (210, 680, "अपरिचित"), (870, 680, "कुकुर")]))
    svg = links + hearts + me + fam + fr_ + st + dog + names
    title = "<b>समानुभूति</b>सँग जोडिएको"
    extra = (
        label("y8-c1", 540, 1090, "आफ्नाको बडुल्की छिटो सर्छ", color="#fff", bg=C["red"], size=44, anchor="center")
        + label("y8-c2", 540, 1090, "कुकुरलाई पनि सर्छ!", color="#14213d", bg=C["yellow"], size=48, anchor="center")
    )
    js = intro_js(sid)
    for g, x, y, r in [("y8-me", 540, 330, 120), ("y8-fam", 210, 170, 85), ("y8-fr", 870, 170, 85), ("y8-st", 210, 560, 80), ("y8-dog", 870, 560, 80)]:
        js += closed_js(g, x, y, r)
    js += f'    tl.set("#y8-dog, #y8-n3, #y8-l4", {{opacity:0}}, 0);\n'
    js += pop("#y8-me", 0.3)
    js += f'    tl.to("#y8-me", {{scale:1.04, transformOrigin:"50% 50%", duration:0.6, yoyo:true, repeat:{int((d - 1) / 0.6) - 1}}}, 0.8);\n'
    t1 = c[1][0]
    js += yawn_js("y8-me", 540, 330, 120, t1 + 0.1, 1.4, 0.3)
    for sel in ["#y8-l1", "#y8-l2", "#y8-h0", "#y8-h1", "#y8-n0", "#y8-n1"]:
        js += pop(sel, t1 + 0.3)
    js += yawn_js("y8-fam", 210, 170, 85, t1 + 0.6, 1.3, 0.3)
    js += yawn_js("y8-fr", 870, 170, 85, t1 + 0.7, 1.3, 0.3)
    js += f'    tl.fromTo("#y8-l3, #y8-n2", {{opacity:0}}, {{opacity:1, duration:0.3}}, {fmt(t1 + 0.9)});\n'
    js += yawn_js("y8-st", 210, 560, 80, t1 + 2.6, 1.3, 0.2)
    js += pop("#y8-c1", t1 + 0.4)
    t2 = c[2][0]
    js += f'    tl.to("#y8-c1", {{opacity:0, duration:0.15}}, {fmt(t2 - 0.15)});\n'
    js += f'    tl.to("#y8-dog, #y8-n3, #y8-l4", {{opacity:1, duration:0.3}}, {fmt(t2)});\n'
    js += yawn_js("y8-me", 540, 330, 120, t2 + 0.3, 1.3, 0.2)
    js += yawn_js("y8-dog", 870, 560, 80, t2 + 0.9, 1.3, 0.3)
    js += pop("#y8-c2", t2 + 0.2)
    return scene_file(sid, d, title, svg, extra, js)


# ================= 9: how to stop =================
def y9(d, c):
    sid = "y9"
    r1 = (
        f'<g id="y9-r1"><rect x="40" y="60" width="1000" height="300" rx="40" fill="#151b3d"/>'
        f'<path d="M200 110 Q170 220 140 260 Q170 300 230 290 Q250 310 270 290 Q320 300 330 260 Q300 220 270 110 Z" fill="{SKIN}"/>'
        f'<ellipse cx="200" cy="285" rx="16" ry="10" fill="{SKIN2}"/><ellipse cx="275" cy="285" rx="16" ry="10" fill="{SKIN2}"/>'
        + "".join(f'<path id="y9-a{i}" d="M{150 + i * 120} 340 q 0 -40 40 -40" stroke="{COOL}" stroke-width="10" fill="none" stroke-linecap="round"/>' for i in range(2))
        + f'<text x="400" y="200" font-family="Mukta" font-weight="800" font-size="56" fill="#fff">नाकबाट गहिरो सास</text></g>'
    )
    r2 = (
        f'<g id="y9-r2"><rect x="40" y="420" width="1000" height="300" rx="40" fill="#151b3d"/>'
        + yface("y9-f", 230, 600, 100)
        + f'<g id="y9-pack"><rect x="150" y="470" width="160" height="56" rx="26" fill="{COOL}"/><path d="M180 485 v26 M230 485 v26 M280 485 v26" stroke="#fff" stroke-width="6"/></g>'
        + f'<text x="400" y="590" font-family="Mukta" font-weight="800" font-size="56" fill="#fff">निधारमा केही चिसो</text></g>'
    )
    svg = r1 + r2
    title = "बडुल्की <b>रोक्ने</b> उपाय"
    js = intro_js(sid)
    js += closed_js("y9-f", 230, 600, 100)
    t = c[1][0]
    js += f'    tl.fromTo("#y9-r1", {{opacity:0, x:-120}}, {{opacity:1, x:0, duration:0.4, ease:"power3.out"}}, {fmt(t)});\n'
    js += f'    tl.fromTo("#y9-a0, #y9-a1", {{y:30, opacity:0}}, {{y:-30, opacity:1, duration:0.8, repeat:{max(1, int((d - t - 1) / 0.8) - 1)}, ease:"sine.in"}}, {fmt(t + 0.4)});\n'
    t2 = t + (c[1][1] - c[1][0]) * 0.5
    js += f'    tl.fromTo("#y9-r2", {{opacity:0, x:-120}}, {{opacity:1, x:0, duration:0.4, ease:"power3.out"}}, {fmt(t2)});\n'
    js += f'    tl.fromTo("#y9-pack", {{y:-120, opacity:0}}, {{y:0, opacity:1, duration:0.5, ease:"bounce.out"}}, {fmt(t2 + 0.4)});\n'
    return scene_file(sid, d, title, svg, "", js)


# ================= 10: CTA =================
def y10(d, c):
    sid = "y10"
    face = yface("y10-f", 540, 200, 140)
    bubble = (
        f'<g id="y10-bub"><rect x="200" y="380" width="680" height="170" rx="40" fill="#fff"/><path d="M300 540 l -40 70 l 100 -60 Z" fill="#fff"/>'
        f'<text x="540" y="455" text-anchor="middle" font-family="Mukta" font-weight="800" font-size="50" fill="#14213d">कति पटक बडुल्की आयो?</text>'
        + "".join(f'<text id="y10-n{i}" x="540" y="525" text-anchor="middle" font-family="Mukta" font-weight="800" font-size="56" fill="{C["red"]}">{n}</text>' for i, n in enumerate(["१ पटक", "२ पटक", "३ पटक!"]))
        + "</g>"
    )
    share = (
        f'<g id="y10-share" transform="translate(540 635)"><rect x="-330" y="-62" width="660" height="124" rx="62" fill="{C["red"]}"/>'
        f'<g transform="translate(-250 0)"><circle cx="-18" cy="0" r="14" fill="#fff"/><circle cx="22" cy="-26" r="14" fill="#fff"/><circle cx="22" cy="26" r="14" fill="#fff"/><path d="M-18 0 L22 -26 M-18 0 L22 26" stroke="#fff" stroke-width="7"/></g>'
        f'<text x="30" y="18" text-anchor="middle" font-family="Mukta" font-weight="800" font-size="52" fill="#fff">साथीलाई सेयर गर्नुहोस्</text></g>'
    )
    svg = face + zzz("y10-z", 720, 120, 56) + bubble + share
    title = "<b>इमानदार</b> भएर भन्नुहोस्"
    js = intro_js(sid)
    js += closed_js("y10-f", 540, 200, 140)
    t = 0.4
    while t + 2 < d - 0.3:
        js += yawn_js("y10-f", 540, 200, 140, t, 1.6, 0.3)
        t += 2.8
    js += f'    tl.fromTo("#y10-z", {{y:0, opacity:0.9}}, {{y:-50, opacity:0.2, duration:1.2, repeat:{int((d - 0.6) / 1.2) - 1}}}, 0.1);\n'
    tq = c[1][0]
    js += pop("#y10-bub", tq)
    for i in range(3):
        js += f'    tl.set("#y10-n{i}", {{opacity:0}}, 0);\n'
        js += f'    tl.set("#y10-n{i}", {{opacity:1}}, {fmt(tq + 0.8 + i * 0.7)});\n'
        if i < 2:
            js += f'    tl.set("#y10-n{i}", {{opacity:0}}, {fmt(tq + 0.8 + (i + 1) * 0.7)});\n'
    ts = c[2][0]
    js += pop("#y10-share", ts + 0.5)
    js += f'    tl.to("#y10-share", {{scale:1.06, duration:0.3, yoyo:true, repeat:{max(1, int((d - ts - 1.2) / 0.3) - 1)}, transformOrigin:"50% 50%"}}, {fmt(ts + 1.0)});\n'
    extra = label("y10-c", 540, 1098, "कमेन्टमा लेख्नुहोस्", color="#14213d", bg=C["yellow"], size=48, anchor="center")
    js += pop("#y10-c", ts)
    return scene_file(sid, d, title, svg, extra, js)


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
        f'      <div id="y{i + 1}" data-composition-id="y{i + 1}" data-composition-src="compositions/y{i + 1}.html" data-start="{fmt(s)}" data-duration="{fmt(dd)}" data-track-index="1" data-track-kind="graphics" data-width="{W}" data-height="{H}"></div>\n'
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
      html, body {{ margin: 0; width: {W}px; height: {H}px; overflow: hidden; background: #0b1530; font-family: 'Mukta', sans-serif; }}
      #bg {{ position: absolute; inset: 0; background: radial-gradient(circle at 14% 20%, rgba(90,209,255,.28) 0 7px, transparent 8px), radial-gradient(circle at 86% 30%, rgba(255,210,63,.25) 0 9px, transparent 10px), radial-gradient(circle at 76% 82%, rgba(90,209,255,.22) 0 8px, transparent 9px), radial-gradient(circle at 20% 74%, rgba(255,210,63,.2) 0 10px, transparent 11px), radial-gradient(120% 70% at 50% 35%, #1d3a7a 0%, #0f1d45 55%, #060c22 100%); }}
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
    fns = [y1, y2, y3, y4, y5, y6, y7, y8, y9, y10]
    for i, fn in enumerate(fns):
        with open(f"{OUT}/compositions/y{i + 1}.html", "w") as f:
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
