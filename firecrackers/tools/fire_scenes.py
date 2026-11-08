# -*- coding: utf-8 -*-
"""Scene builders for the Nepali 'how firecrackers work' explainer (imported by gen_fire.py)."""
import math
from gen import FONT_FACE, C, fmt, rr, label, pop, wobble, intro_js, scene_file  # noqa: F401

PAPER, PAPER2 = "#e63946", "#b5202d"
FUEL, OXY = "#2b2233", "#f1f3f5"
GAS = "#ffb703"
SR, BA, CU = "#ff4d6d", "#51cf66", "#4dabf7"


def txt(tid, x, y, s, size=40, color="#fff", anchor="middle"):
    return f'<text id="{tid}" x="{fmt(x)}" y="{fmt(y)}" text-anchor="{anchor}" font-family="Mukta" font-weight="800" font-size="{size}" fill="{color}">{s}</text>'


def burst(bid, cx, cy, r, color, n=14, seed=1):
    """Firework burst: rays + sparks around (cx, cy); animate scale from 0."""
    R = rr(seed)
    rays = ""
    for k in range(n):
        a = k / n * 6.283
        r1, r2 = r * 0.25, r * R.uniform(0.85, 1.0)
        rays += f'<line x1="{fmt(cx + r1 * math.cos(a))}" y1="{fmt(cy + r1 * math.sin(a))}" x2="{fmt(cx + r2 * math.cos(a))}" y2="{fmt(cy + r2 * math.sin(a))}" stroke="{color}" stroke-width="{fmt(max(4, r * 0.05))}" stroke-linecap="round"/>'
        rays += f'<circle cx="{fmt(cx + r2 * 1.08 * math.cos(a))}" cy="{fmt(cy + r2 * 1.08 * math.sin(a))}" r="{fmt(max(5, r * 0.05))}" fill="#fff"/>'
    return f'<g id="{bid}">{rays}<circle cx="{fmt(cx)}" cy="{fmt(cy)}" r="{fmt(r * 0.16)}" fill="#fff"/></g>'


def cracker(cid, x, y, w=120, h=300, fuse=True, angle=0):
    """Upright paper cracker with a fuse at the top; (x, y) = top-left."""
    stripes = "".join(f'<rect x="{x}" y="{y + k * h / 5}" width="{w}" height="{fmt(h / 10)}" fill="{PAPER2}"/>' for k in range(5))
    f = ""
    if fuse:
        f = f'<path d="M{x + w / 2} {y} q 20 -40 -10 -80" stroke="#c9a227" stroke-width="8" fill="none" stroke-linecap="round"/>'
    rot = f' transform="rotate({angle} {x + w / 2} {y + h / 2})"' if angle else ""
    return f'<g id="{cid}"{rot}><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{PAPER}"/>{stripes}<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="none" stroke="#7a1020" stroke-width="5"/>{f}</g>'


def spark(sid, x, y, s=1.0):
    return f'<g id="{sid}"><path d="M{x} {fmt(y - 34 * s)} L{fmt(x + 9 * s)} {fmt(y - 9 * s)} L{fmt(x + 34 * s)} {y} L{fmt(x + 9 * s)} {fmt(y + 9 * s)} L{x} {fmt(y + 34 * s)} L{fmt(x - 9 * s)} {fmt(y + 9 * s)} L{fmt(x - 34 * s)} {y} L{fmt(x - 9 * s)} {fmt(y - 9 * s)} Z" fill="{C["yellow"]}"/><circle cx="{x}" cy="{y}" r="{fmt(8 * s)}" fill="#fff"/></g>'


def flicker(sel, t0, t1, period=0.12):
    n = max(1, int((t1 - t0) / period) - 1)
    return f'    tl.fromTo("{sel}", {{scale:0.7, rotation:0, transformOrigin:"50% 50%"}}, {{scale:1.25, rotation:45, duration:{fmt(period)}, yoyo:true, repeat:{n}, ease:"sine.inOut"}}, {fmt(t0)});\n'


# ================= 1: hook =================
def f1(d, c):
    sid = "f1"
    cr = cracker("f1-cr", 470, 420, 140, 320)
    sp = spark("f1-sp", 530, 335, 1.3)
    b = burst("f1-b1", 540, 330, 330, C["yellow"], 18, 3) + burst("f1-b2", 260, 160, 150, SR, 12, 4).replace('<g id="f1-b2">', '<g id="f1-b2" style="opacity:0">') + burst("f1-b3", 830, 180, 170, CU, 12, 5).replace('<g id="f1-b3">', '<g id="f1-b3" style="opacity:0">')
    svg = b + cr + sp
    title = '<b>धुम!</b>'
    extra_css = "#f1-title{top:170px;font-size:150px;}"
    extra = label("f1-chip", 540, 1080, "१ सेकेन्डभित्र के हुन्छ?", color="#14213d", bg=C["yellow"], size=50, anchor="center")
    js = ""
    js += f'    tl.set("#f1-b1", {{scale:0.9, opacity:1, transformOrigin:"50% 50%"}}, 0);\n'
    js += f'    tl.to("#f1-b1", {{scale:1.15, opacity:0, duration:0.9, ease:"power2.out"}}, 0.5);\n'
    js += flicker("#f1-sp", 0, d - 0.4)
    js += f'    tl.fromTo("#f1-title", {{scale:1}}, {{scale:1.15, duration:0.15, yoyo:true, repeat:3}}, 0.05);\n'
    t = 1.6
    k = 0
    while t + 1.2 < d - 0.3:
        sel = "#f1-b2" if k % 2 == 0 else "#f1-b3"
        js += f'    tl.to("{sel}", {{keyframes:[{{scale:0, opacity:1, duration:0.01}}, {{scale:1, duration:0.35, ease:"power3.out"}}, {{opacity:0, scale:1.15, duration:0.6}}]}}, {fmt(t)});\n'
        t += 1.1
        k += 1
    js += f'    tl.fromTo("#f1-cr", {{x:0}}, {{x:4, duration:0.05, yoyo:true, repeat:{int((d - 0.5) / 0.05) - 1}}}, 0.1);\n'
    js += f'    tl.fromTo("#f1-chip", {{scale:1}}, {{scale:1.06, duration:0.3, yoyo:true, repeat:{int((d - 1) / 0.3) - 1}, transformOrigin:"50% 50%"}}, 0.5);\n'
    return scene_file(sid, d, title, svg, extra, js, extra_css)


# ================= 2: inside the cracker =================
def f2(d, c):
    sid = "f2"
    R = rr(21)
    # cutaway tube, lying horizontally
    tube = f'<rect x="90" y="60" width="900" height="300" rx="40" fill="{PAPER}"/><rect x="120" y="90" width="840" height="240" rx="26" fill="#3b2f2f"/>'
    grains = ""
    for i in range(70):
        x, y = 150 + R.uniform(0, 780), 115 + R.uniform(0, 190)
        if i % 2:
            grains += f'<circle class="f2-fuel" cx="{fmt(x)}" cy="{fmt(y)}" r="{fmt(R.uniform(9, 14))}" fill="#14110f" stroke="#555" stroke-width="2"/>'
        else:
            grains += f'<rect class="f2-oxy" x="{fmt(x)}" y="{fmt(y)}" width="20" height="20" rx="4" fill="{OXY}" transform="rotate({int(R.uniform(0, 90))} {fmt(x + 10)} {fmt(y + 10)})"/>'
    legend = (
        f'<g id="f2-lf"><circle cx="190" cy="430" r="20" fill="#14110f" stroke="#888" stroke-width="3"/>{txt("f2-lft", 225, 445, "इन्धन", 44, "#fff", "start")}</g>'
        f'<g id="f2-lo"><rect x="520" y="410" width="40" height="40" rx="6" fill="{OXY}"/>{txt("f2-lot", 580, 445, "अक्सिजन दिने रसायन", 44, "#fff", "start")}</g>'
    )
    # compare: candle needs air vs powder carries its own
    cmp_ = (
        f'<g id="f2-cmp"><rect x="90" y="520" width="420" height="240" rx="30" fill="#1b2140"/><rect x="570" y="520" width="420" height="240" rx="30" fill="#1b2140"/>'
        f'<rect x="270" y="640" width="60" height="100" rx="10" fill="#f8f9fa"/><path d="M300 640 q -30 -50 0 -90 q 30 40 0 90 Z" fill="{GAS}"/>'
        + "".join(f'<text x="{x}" y="{y}" font-family="Mukta" font-weight="800" font-size="44" fill="{CU}">O<tspan font-size="30" dy="10">2</tspan></text>' for x, y in [(150, 600), (400, 590), (170, 700)])
        + f'{txt("f2-c1", 300, 795, "हावाबाट अक्सिजन", 36)}'
        + f'<rect x="700" y="600" width="160" height="110" rx="16" fill="#3b2f2f"/>'
        + "".join(f'<rect x="{720 + k * 40}" y="{620 + (k % 2) * 40}" width="22" height="22" rx="4" fill="{OXY}"/>' for k in range(4))
        + f'{txt("f2-c2", 780, 795, "आफ्नै अक्सिजन!", 36, C["yellow"])}</g>'
    )
    svg = tube + f'<g id="f2-grains">{grains}</g>' + legend + cmp_
    title = "भित्र हुन्छ <b>बारुद</b>"
    js = intro_js(sid)
    js += f'    tl.fromTo(".f2-fuel, .f2-oxy", {{opacity:0, scale:0, transformOrigin:"50% 50%"}}, {{opacity:1, scale:1, duration:0.2, stagger:0.015, ease:"back.out(2)"}}, 0.4);\n'
    t1 = c[1][0]
    js += pop("#f2-lf", t1 + 0.4)
    js += pop("#f2-lo", t1 + 1.2)
    js += f'    tl.to(".f2-oxy", {{scale:1.3, duration:0.2, yoyo:true, repeat:3, transformOrigin:"50% 50%"}}, {fmt(t1 + 1.3)});\n'
    t2 = c[2][0]
    js += pop("#f2-cmp", t2 + 0.2, 0.6)
    return scene_file(sid, d, title, svg, "", js)


# ================= 3: it burns very fast =================
def f3(d, c):
    sid = "f3"
    tube = f'<rect x="90" y="140" width="900" height="260" rx="40" fill="{PAPER}"/><rect x="120" y="170" width="840" height="200" rx="26" fill="#3b2f2f"/>'
    front = f'<rect id="f3-front" x="120" y="170" width="840" height="200" rx="26" fill="{GAS}" opacity="0.9"/>'
    R = rr(31)
    bubbles = "".join(f'<circle id="f3-g{i}" cx="{fmt(150 + R.uniform(0, 780))}" cy="{fmt(190 + R.uniform(0, 160))}" r="{fmt(R.uniform(14, 26))}" fill="#fff3bf" opacity="0.85"/>' for i in range(24))
    match = spark("f3-sp", 110, 270, 1.4)
    speed = "".join(f'<line id="f3-s{i}" x1="{300 + i * 140}" y1="{470 + (i % 2) * 30}" x2="{400 + i * 140}" y2="{470 + (i % 2) * 30}" stroke="#fff" stroke-width="8" stroke-linecap="round" opacity="0"/>' for i in range(5))
    therm = (
        f'<g id="f3-th"><rect x="470" y="440" width="140" height="180" rx="20" fill="#1b2140"/>'
        f'<rect x="525" y="460" width="30" height="130" rx="15" fill="#fff"/><rect id="f3-merc" x="531" y="470" width="18" height="120" rx="9" fill="{C["red"]}"/><circle cx="540" cy="595" r="24" fill="{C["red"]}"/></g>'
    )
    svg = tube + front + bubbles + match + speed + therm
    title = "<b>बिजुली</b> जस्तो छिटो बल्छ"
    extra = label("f3-l", 540, 1080, "धेरै तातो ग्यास बन्छ", color="#14213d", bg=GAS, size=48, anchor="center")
    js = intro_js(sid)
    t0 = c[0][0] + 0.3
    js += flicker("#f3-sp", 0.2, t0 + 0.4)
    js += f'    tl.fromTo("#f3-front", {{scaleX:0, svgOrigin:"120 270"}}, {{scaleX:1, duration:0.6, ease:"power4.in"}}, {fmt(t0 + 0.3)});\n'
    for i in range(5):
        js += f'    tl.fromTo("#f3-s{i}", {{opacity:0, x:-60}}, {{opacity:1, x:60, duration:0.25, yoyo:true, repeat:1}}, {fmt(t0 + 0.3 + i * 0.08)});\n'
    for i in range(24):
        js += f'    tl.fromTo("#f3-g{i}", {{scale:0, transformOrigin:"50% 50%"}}, {{scale:1.4, duration:0.4, ease:"back.out(2)"}}, {fmt(t0 + 0.9 + (i % 12) * 0.08)});\n'
    js += f'    tl.fromTo("#f3-merc", {{scaleY:0.15, svgOrigin:"540 590"}}, {{scaleY:1, duration:0.8, ease:"power2.out"}}, {fmt(t0 + 0.9)});\n'
    js += pop("#f3-th", t0 + 0.7)
    js += pop("#f3-l", t0 + 1.4)
    js += f'    tl.to("#f3-front", {{opacity:0.6, duration:0.12, yoyo:true, repeat:{max(1, int((d - t0 - 1.6) / 0.12) - 1)}}}, {fmt(t0 + 1.0)});\n'
    return scene_file(sid, d, title, svg, extra, js)


# ================= 4: pressure, burst, sound =================
def f4(d, c):
    sid = "f4"
    cr = f'<g id="f4-cr">{cracker("f4-crin", 430, 120, 220, 420, fuse=False)}<rect id="f4-glow" x="450" y="140" width="180" height="380" rx="12" fill="{GAS}" opacity="0"/></g>'
    gauge = (
        f'<g id="f4-gauge" transform="translate(860 230)"><circle r="110" fill="#fff"/><circle r="96" fill="#1b2140"/>'
        f'<path d="M-80 30 A 85 85 0 0 1 80 30" stroke="{C["red"]}" stroke-width="14" fill="none"/>'
        f'<g id="f4-needle"><line x1="0" y1="0" x2="0" y2="-80" stroke="#fff" stroke-width="10" stroke-linecap="round"/></g><circle r="12" fill="#fff"/>'
        f'{txt("f4-gt", 0, 160, "दबाब", 40)}</g>'
    )
    R = rr(41)
    frags = "".join(f'<rect id="f4-fr{i}" x="525" y="320" width="{int(R.uniform(26, 50))}" height="{int(R.uniform(16, 34))}" rx="5" fill="{PAPER if i % 2 else PAPER2}" opacity="0"/>' for i in range(16))
    rings = "".join(f'<circle id="f4-r{i}" cx="540" cy="330" r="80" fill="none" stroke="#fff" stroke-width="10" opacity="0"/>' for i in range(3))
    boom = txt("f4-boom", 540, 380, "धुम!", 170, C["yellow"])
    ear = (
        f'<g id="f4-ear" transform="translate(170 640)"><path d="M-20 -80 C 70 -110, 100 -10, 40 40 C 15 60, 30 100, -10 100" stroke="#f1b48c" stroke-width="26" fill="none" stroke-linecap="round"/>'
        f'<path d="M120 -40 q 30 40 0 80 M150 -70 q 50 70 0 140" stroke="#fff" stroke-width="8" fill="none" stroke-linecap="round"/></g>'
    )
    svg = cr + gauge + rings + frags + boom + ear
    title = "<b>दबाब</b> बढ्छ… अनि!"
    extra = label("f4-l", 540, 1080, "हावाको तरङ्ग = आवाज", color="#14213d", bg=C["yellow"], size=48, anchor="center")
    js = intro_js(sid)
    js += f'    tl.set("#f4-boom, #f4-ear", {{opacity:0}}, 0);\n'
    js += f'    tl.fromTo("#f4-needle", {{rotation:-70, svgOrigin:"0 0"}}, {{rotation:75, duration:{fmt(max(1, c[1][0] + 0.6))}, ease:"power2.in"}}, 0.3);\n'
    js += f'    tl.fromTo("#f4-cr", {{scaleX:1, svgOrigin:"540 330"}}, {{scaleX:1.12, duration:{fmt(max(1, c[1][0] + 0.6))}, ease:"power2.in"}}, 0.3);\n'
    js += f'    tl.to("#f4-glow", {{opacity:0.7, duration:{fmt(max(1, c[1][0] + 0.6))}}}, 0.3);\n'
    tb = c[2][1] - 0.45  # lands on "धुम!"
    js += f'    tl.to("#f4-cr", {{opacity:0, duration:0.05}}, {fmt(tb)});\n'
    for i in range(16):
        a = i / 16 * 6.283
        js += f'    tl.fromTo("#f4-fr{i}", {{opacity:1, x:0, y:0, rotation:0}}, {{x:{fmt(420 * math.cos(a))}, y:{fmt(380 * math.sin(a))}, rotation:{int(R.uniform(-300, 300))}, opacity:0, duration:1.1, ease:"power3.out"}}, {fmt(tb)});\n'
    for i in range(3):
        js += f'    tl.fromTo("#f4-r{i}", {{opacity:0.9, scale:0.3, transformOrigin:"50% 50%"}}, {{opacity:0, scale:5, duration:1.2, ease:"power2.out"}}, {fmt(tb + i * 0.25)});\n'
    js += f'    tl.fromTo("#f4-boom", {{opacity:0, scale:0.3, transformOrigin:"50% 50%"}}, {{opacity:1, scale:1, duration:0.25, ease:"back.out(3)"}}, {fmt(tb)});\n'
    js += f'    tl.to("#f4-boom", {{opacity:0, duration:0.3}}, {fmt(tb + 1.3)});\n'
    t3 = c[3][0]
    js += f'    tl.fromTo("#f4-ear", {{opacity:0, x:-60}}, {{opacity:1, x:0, duration:0.4}}, {fmt(t3)});\n'
    for i in range(3):
        js += f'    tl.fromTo("#f4-r{i}", {{opacity:0.8, scale:0.3}}, {{opacity:0, scale:4, duration:1.0, ease:"power1.out", immediateRender:false}}, {fmt(max(t3 + 0.3, tb + 1.3) + i * 0.3)});\n'
    js += pop("#f4-l", t3 + 0.2)
    return scene_file(sid, d, title, svg, extra, js)


# ================= 5: colours =================
def f5(d, c):
    sid = "f5"
    bursts = burst("f5-b0", 230, 170, 170, SR, 14, 51) + burst("f5-b1", 540, 120, 170, BA, 14, 52) + burst("f5-b2", 850, 170, 170, CU, 14, 53)
    labels = (
        txt("f5-l0", 230, 400, "स्ट्रोन्सियम", 40, SR) + txt("f5-l1", 540, 350, "बेरियम", 40, BA) + txt("f5-l2", 850, 400, "तामा", 40, CU)
    )
    # atom: nucleus + two orbits, electron jumps out and back, emits a wave
    atom = (
        f'<g id="f5-atom"><circle cx="400" cy="620" r="38" fill="{C["red"]}"/><circle cx="400" cy="620" r="95" fill="none" stroke="#fff" stroke-width="4" opacity="0.6"/>'
        f'<circle cx="400" cy="620" r="150" fill="none" stroke="#fff" stroke-width="4" stroke-dasharray="10 10" opacity="0.6"/>'
        f'<circle id="f5-e" cx="495" cy="620" r="18" fill="{CU}"/></g>'
        f'<path id="f5-wave" d="M580 620 q 25 -40 50 0 t 50 0 t 50 0 t 50 0 t 50 0" stroke="{BA}" stroke-width="10" fill="none" stroke-linecap="round" opacity="0"/>'
        f'{txt("f5-at", 400, 520 - 40, "तातो → इलेक्ट्रोन उफ्रन्छ", 36, "#fff")}'
    )
    svg = bursts + labels + atom
    title = "<b>रंग</b> कहाँबाट आउँछ?"
    extra = label("f5-l", 540, 1080, "हरेक धातुको आफ्नै रंग", color="#14213d", bg=C["yellow"], size=46, anchor="center")
    js = intro_js(sid)
    js += f'    tl.set("#f5-b0, #f5-b1, #f5-b2, #f5-l0, #f5-l1, #f5-l2, #f5-atom, #f5-at", {{opacity:0}}, 0);\n'
    t1 = c[1][0]
    seg = (c[1][1] - c[1][0]) / 3
    for k in range(3):
        tk = t1 + k * seg
        js += f'    tl.fromTo("#f5-b{k}", {{opacity:1, scale:0, transformOrigin:"50% 50%"}}, {{scale:1, duration:0.4, ease:"power3.out"}}, {fmt(tk)});\n'
        js += f'    tl.to("#f5-b{k}", {{scale:1.06, duration:0.5, yoyo:true, repeat:{max(1, int((d - tk - 0.8) / 0.5) - 1)}, transformOrigin:"50% 50%"}}, {fmt(tk + 0.4)});\n'
        js += f'    tl.to("#f5-l{k}", {{opacity:1, duration:0.2}}, {fmt(tk + 0.2)});\n'
    t2 = c[2][0]
    js += f'    tl.to("#f5-atom, #f5-at", {{opacity:1, duration:0.3}}, {fmt(t2)});\n'
    for rep in range(3):
        tr = t2 + 0.6 + rep * 1.4
        if tr + 1.2 < d - 0.3:
            js += f'    tl.to("#f5-e", {{attr:{{cx:550}}, duration:0.3, ease:"power2.out"}}, {fmt(tr)});\n'
            js += f'    tl.to("#f5-e", {{attr:{{cx:495}}, duration:0.3, ease:"power2.in"}}, {fmt(tr + 0.5)});\n'
            js += f'    tl.fromTo("#f5-wave", {{opacity:1, x:-40}}, {{opacity:0, x:120, duration:0.6, immediateRender:false}}, {fmt(tr + 0.8)});\n'
    js += pop("#f5-l", t2 + 0.5)
    return scene_file(sid, d, title, svg, extra, js)


# ================= 6: rocket =================
def f6(d, c):
    sid = "f6"
    rocket = (
        f'<g id="f6-rk"><path d="M540 160 L600 260 L600 470 L480 470 L480 260 Z" fill="{PAPER}"/><path d="M540 160 L600 260 L480 260 Z" fill="{C["yellow"]}"/>'
        f'<rect x="533" y="470" width="14" height="300" fill="#c9a227"/>'
        + "".join(f'<path id="f6-fl{i}" d="M{500 + i * 20} 470 q 10 {60 + i * 10} 0 {110 + (i % 2) * 30}" stroke="{GAS}" stroke-width="18" fill="none" stroke-linecap="round"/>' for i in range(4))
        + "</g>"
    )
    up = f'<g id="f6-up"><path d="M820 420 L820 200" stroke="{CU}" stroke-width="22" stroke-linecap="round"/><path d="M780 230 L820 170 L860 230 Z" fill="{CU}"/>{txt("f6-ut", 820, 470, "धक्का", 44, CU)}</g>'
    down = f'<g id="f6-down"><path d="M260 300 L260 520" stroke="{GAS}" stroke-width="22" stroke-linecap="round"/><path d="M220 490 L260 550 L300 490 Z" fill="{GAS}"/>{txt("f6-dt", 260, 260, "ग्यास", 44, GAS)}</g>'
    svg = down + up + rocket
    title = "<b>हवाई</b> कसरी उड्छ?"
    extra = label("f6-l", 540, 1080, "न्युटनको तेस्रो नियम", color="#14213d", bg=CU, size=48, anchor="center")
    js = intro_js(sid)
    js += f'    tl.set("#f6-up, #f6-down", {{opacity:0}}, 0);\n'
    for i in range(4):
        js += f'    tl.fromTo("#f6-fl{i}", {{scaleY:0.6, opacity:0.8, svgOrigin:"540 470"}}, {{scaleY:1.2, opacity:1, duration:0.08, yoyo:true, repeat:{int((d - 0.6) / 0.08) - 1}}}, {fmt(0.2 + i * 0.02)});\n'
    t1 = c[1][0]
    js += f'    tl.to("#f6-down", {{opacity:1, duration:0.3}}, {fmt(t1)});\n'
    js += f'    tl.to("#f6-up", {{opacity:1, duration:0.3}}, {fmt(t1 + 0.9)});\n'
    js += f'    tl.fromTo("#f6-rk", {{y:0}}, {{y:-320, duration:{fmt(max(1, d - t1 - 1.6))}, ease:"power2.in"}}, {fmt(t1 + 1.0)});\n'
    js += pop("#f6-l", c[0][0] + 0.6)
    return scene_file(sid, d, title, svg, extra, js)


# ================= 7: history & Tihar lights =================
def f7(d, c):
    sid = "f7"
    scroll = (
        f'<g id="f7-scroll"><rect x="280" y="40" width="520" height="250" rx="20" fill="#f4e3c1"/><rect x="250" y="30" width="40" height="270" rx="20" fill="#c08552"/><rect x="790" y="30" width="40" height="270" rx="20" fill="#c08552"/>'
        f'{txt("f7-yr", 540, 150, "१००० वर्षअघि", 64, "#7a1020")}{txt("f7-cn", 540, 230, "चीनमा बारुद", 52, "#14213d")}</g>'
    )
    diyos = ""
    for i in range(6):
        x = 120 + i * 168
        diyos += (
            f'<g id="f7-d{i}"><path d="M{x - 55} 640 Q{x} 720 {x + 55} 640 Z" fill="#d9480f"/><path d="M{x - 55} 640 L{x + 55} 640" stroke="#ffa94d" stroke-width="8"/>'
            f'<path id="f7-fl{i}" d="M{x} 630 q -22 -40 0 -80 q 22 40 0 80 Z" fill="{GAS}"/></g>'
        )
    sky = burst("f7-b0", 250, 420, 110, SR, 12, 71) + burst("f7-b1", 830, 420, 110, BA, 12, 72) + burst("f7-b2", 540, 400, 130, C["yellow"], 14, 73)
    svg = scroll + sky + diyos
    title = "<b>हजार वर्ष</b> पुरानो विज्ञान"
    extra = label("f7-l", 540, 1080, "तिहार र दिवालीको झिलिमिली", color="#14213d", bg=C["yellow"], size=46, anchor="center")
    js = intro_js(sid)
    js += f'    tl.set("#f7-b0, #f7-b1, #f7-b2", {{opacity:0}}, 0);\n'
    js += pop("#f7-scroll", 0.3, 0.6)
    t2 = c[1][0]
    for i in range(6):
        js += pop(f"#f7-d{i}", t2 + i * 0.15)
        js += f'    tl.fromTo("#f7-fl{i}", {{scaleY:0.85, svgOrigin:"{120 + i * 168} 630"}}, {{scaleY:1.15, duration:0.15, yoyo:true, repeat:{max(1, int((d - t2 - 1) / 0.15) - 1)}}}, {fmt(t2 + 0.3 + i * 0.05)});\n'
    for k in range(3):
        tk = t2 + 0.8 + k * 0.5
        js += f'    tl.fromTo("#f7-b{k}", {{opacity:1, scale:0, transformOrigin:"50% 50%"}}, {{scale:1, duration:0.4, ease:"power3.out"}}, {fmt(tk)});\n'
    js += pop("#f7-l", t2 + 0.4)
    return scene_file(sid, d, title, svg, extra, js)


# ================= 8: safety =================
def f8(d, c):
    sid = "f8"
    rows = [40, 280, 520]

    def card(cid, y, icon, text, ok):
        mark = (f'<g transform="translate(930 {y + 100})"><circle r="44" fill="#22c55e"/><path d="M-20 2 L-6 16 L22 -14" stroke="#fff" stroke-width="10" fill="none" stroke-linecap="round" stroke-linejoin="round"/></g>' if ok
                else f'<g transform="translate(930 {y + 100})"><circle r="44" fill="{C["red"]}"/><path d="M-16 -16 L16 16 M16 -16 L-16 16" stroke="#fff" stroke-width="10" stroke-linecap="round"/></g>')
        return f'<g id="{cid}"><rect x="40" y="{y}" width="1000" height="200" rx="36" fill="#1b2140"/>{icon}{txt(cid + "-t", 270, y + 118, text, 46, "#fff", "start")}{mark}</g>'
    hand_icon = f'<g><rect x="100" y="{rows[0] + 60}" width="110" height="90" rx="30" fill="#f1b48c"/>{cracker("f8-c1", 150, rows[0] + 30, 34, 90, fuse=True)}</g>'
    dud_icon = f'<g>{cracker("f8-c2", 130, rows[1] + 70, 60, 110, fuse=False)}<path d="M160 {rows[1] + 70} q 10 -20 -5 -40" stroke="#555" stroke-width="7" fill="none"/></g>'
    bucket = f'<g><path d="M100 {rows[2] + 60} L220 {rows[2] + 60} L200 {rows[2] + 170} L120 {rows[2] + 170} Z" fill="#4dabf7"/><rect x="95" y="{rows[2] + 50}" width="130" height="20" rx="8" fill="#1c7ed6"/><path d="M110 {rows[2] + 50} Q160 {rows[2] - 10} 210 {rows[2] + 50}" stroke="#adb5bd" stroke-width="6" fill="none"/></g>'
    cards = (
        card("f8-k1", rows[0], hand_icon, "हातमा लिएर नपड्काउनुहोस्", False)
        + card("f8-k2", rows[1], dud_icon, "नपड्केको फेरि नबाल्नुहोस्", False)
        + card("f8-k3", rows[2], bucket, "पानीको बाल्टिन नजिकै", True)
    )
    svg = cards
    title = "<b>सावधान!</b>"
    extra_css = "#f8-title{font-size:96px;}"
    extra = label("f8-l", 540, 1104, "चर्को आवाजले कान बिगार्न सक्छ", color="#fff", bg=C["red"], size=42, anchor="center")
    js = intro_js(sid)
    js += f'    tl.fromTo("#f8-title", {{scale:1}}, {{scale:1.1, duration:0.2, yoyo:true, repeat:3, transformOrigin:"50% 50%"}}, 0.4);\n'
    js += pop("#f8-l", c[1][0])
    for k, ck in enumerate(c[2:5]):
        js += f'    tl.fromTo("#f8-k{k + 1}", {{opacity:0, x:-140}}, {{opacity:1, x:0, duration:0.4, ease:"power3.out"}}, {fmt(ck[0])});\n'
    return scene_file(sid, d, title, svg, extra, js, extra_css)


# ================= 9: CTA =================
def f9(d, c):
    sid = "f9"
    diyo = f'<g id="f9-diyo"><path d="M400 330 Q540 450 680 330 Z" fill="#d9480f"/><path d="M400 330 L680 330" stroke="#ffa94d" stroke-width="12"/><path id="f9-fl" d="M540 315 q -40 -70 0 -150 q 40 80 0 150 Z" fill="{GAS}"/></g>'
    sky = burst("f9-b0", 200, 140, 120, SR, 12, 91) + burst("f9-b1", 880, 140, 120, CU, 12, 92)
    bub = (
        f'<g id="f9-bub"><rect x="160" y="470" width="760" height="140" rx="40" fill="#fff"/><path d="M260 600 l -40 60 l 100 -60 Z" fill="#fff"/>'
        f'{txt("f9-bt", 540, 560, "कुन पटाका मन पर्छ?", 58, "#14213d")}</g>'
    )
    share = (
        f'<g id="f9-share" transform="translate(540 720)"><rect x="-330" y="-56" width="660" height="112" rx="56" fill="{C["red"]}"/>'
        f'{txt("f9-st", 0, 18, "साथीलाई सेयर गर्नुहोस्", 50)}</g>'
    )
    svg = sky + diyo + bub + share
    title = "शुभ <b>दीपावली!</b>"
    extra_css = "#f9-title{font-size:104px;}"
    js = intro_js(sid)
    js += f'    tl.fromTo("#f9-fl", {{scaleY:0.85, svgOrigin:"540 315"}}, {{scaleY:1.15, duration:0.15, yoyo:true, repeat:{int((d - 0.6) / 0.15) - 1}}}, 0.2);\n'
    js += f'    tl.set("#f9-b0, #f9-b1", {{opacity:0}}, 0);\n'
    t = 0.5
    k = 0
    while t + 1.2 < d - 0.3:
        js += f'    tl.to("#f9-b{k % 2}", {{keyframes:[{{opacity:1, scale:0, duration:0.01, transformOrigin:"50% 50%"}}, {{scale:1, duration:0.35, ease:"power3.out"}}, {{opacity:0, scale:1.1, duration:0.6}}]}}, {fmt(t)});\n'
        t += 1.0
        k += 1
    js += pop("#f9-bub", c[0][0] + 0.2)
    js += pop("#f9-share", c[1][0] + 0.8)
    js += f'    tl.to("#f9-share", {{scale:1.06, duration:0.3, yoyo:true, repeat:{max(1, int((d - c[1][0] - 1.6) / 0.3) - 1)}, transformOrigin:"50% 50%"}}, {fmt(c[1][0] + 1.3)});\n'
    return scene_file(sid, d, title, svg, "", js, extra_css)


SCENE_FNS = [f1, f2, f3, f4, f5, f6, f7, f8, f9]
