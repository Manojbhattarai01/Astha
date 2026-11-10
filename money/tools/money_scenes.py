# -*- coding: utf-8 -*-
"""Scene builders for the Nepali 'why people chase money' explainer (imported by gen_money.py)."""
import math
from gen import FONT_FACE, C, fmt, rr, label, pop, wobble, intro_js, scene_file  # noqa: F401

SKIN, HAIR = "#f1b48c", "#2b2233"
NOTE, NOTE2 = "#2f9e44", "#b2f2bb"
GOLD = "#ffd43b"


def txt(tid, x, y, s, size=40, color="#fff", anchor="middle"):
    return f'<text id="{tid}" x="{fmt(x)}" y="{fmt(y)}" text-anchor="{anchor}" font-family="Mukta" font-weight="800" font-size="{size}" fill="{color}">{s}</text>'


def note(nid, x, y, w=260, h=130, amount="१०००"):
    """A banknote centred on (x, y)."""
    return (
        f'<g id="{nid}"><rect x="{fmt(x - w / 2)}" y="{fmt(y - h / 2)}" width="{w}" height="{h}" rx="14" fill="{NOTE}"/>'
        f'<rect x="{fmt(x - w / 2 + 12)}" y="{fmt(y - h / 2 + 12)}" width="{w - 24}" height="{h - 24}" rx="10" fill="none" stroke="{NOTE2}" stroke-width="5"/>'
        f'<circle cx="{fmt(x - w * 0.22)}" cy="{y}" r="{fmt(h * 0.28)}" fill="{NOTE2}"/>'
        f'{txt(nid + "-t", x + w * 0.16, y + h * 0.16, "रु " + amount, int(h * 0.36), "#fff")}</g>'
    )


def guy(gid, cx, cy, s=1.0, money_eyes=False, shirt="#4dabf7"):
    """A cartoon guy; (cx, cy) = head centre. Legs #gid-l1/-l2 rotate at the hip, arms #gid-a1/-a2 at the shoulder."""
    hx, hy = cx, cy + 210 * s   # hip
    sx, sy = cx, cy + 95 * s    # shoulder
    leg = lambda i, c: f'<g id="{gid}-l{i}"><line x1="{fmt(hx)}" y1="{fmt(hy)}" x2="{fmt(hx)}" y2="{fmt(hy + 120 * s)}" stroke="{c}" stroke-width="{fmt(30 * s)}" stroke-linecap="round"/></g>'
    arm = lambda i: f'<g id="{gid}-a{i}"><line x1="{fmt(sx)}" y1="{fmt(sy)}" x2="{fmt(sx)}" y2="{fmt(sy + 100 * s)}" stroke="{SKIN}" stroke-width="{fmt(22 * s)}" stroke-linecap="round"/></g>'
    if money_eyes:
        eyes = (txt(gid + "-e1", cx - 22 * s, cy + 2 * s, "रु", int(34 * s), NOTE) + txt(gid + "-e2", cx + 26 * s, cy + 2 * s, "रु", int(34 * s), NOTE))
    else:
        eyes = f'<circle cx="{fmt(cx - 20 * s)}" cy="{fmt(cy - 6 * s)}" r="{fmt(7 * s)}" fill="#14213d"/><circle cx="{fmt(cx + 22 * s)}" cy="{fmt(cy - 6 * s)}" r="{fmt(7 * s)}" fill="#14213d"/>'
    mouth = f'<path id="{gid}-m" d="M{fmt(cx - 22 * s)} {fmt(cy + 24 * s)} Q{fmt(cx)} {fmt(cy + 46 * s)} {fmt(cx + 22 * s)} {fmt(cy + 24 * s)}" stroke="#14213d" stroke-width="{fmt(6 * s)}" fill="none" stroke-linecap="round"/>'
    return (
        f'<g id="{gid}">{leg(2, "#1c3d6e")}{arm(2)}'
        f'<rect x="{fmt(cx - 45 * s)}" y="{fmt(cy + 65 * s)}" width="{fmt(90 * s)}" height="{fmt(160 * s)}" rx="{fmt(36 * s)}" fill="{shirt}"/>'
        f'{leg(1, "#274c86")}'
        f'<circle cx="{fmt(cx)}" cy="{fmt(cy)}" r="{fmt(62 * s)}" fill="{SKIN}"/>'
        f'<path d="M{fmt(cx - 62 * s)} {fmt(cy - 10 * s)} Q{fmt(cx - 55 * s)} {fmt(cy - 72 * s)} {fmt(cx)} {fmt(cy - 64 * s)} Q{fmt(cx + 58 * s)} {fmt(cy - 70 * s)} {fmt(cx + 62 * s)} {fmt(cy - 10 * s)} Q{fmt(cx)} {fmt(cy - 40 * s)} {fmt(cx - 62 * s)} {fmt(cy - 10 * s)} Z" fill="{HAIR}"/>'
        f'{eyes}{mouth}{arm(1)}</g>'
    )


def run_js(gid, cx, cy, s, t0, t1, period=0.32):
    """Running cycle: legs and arms swing in opposite phase."""
    n = max(1, int((t1 - t0) / (period / 2)) - 1)
    hip, sh = f'"{fmt(cx)} {fmt(cy + 210 * s)}"', f'"{fmt(cx)} {fmt(cy + 95 * s)}"'
    js = ""
    for part, org, a in [("l1", hip, 35), ("l2", hip, -35), ("a1", sh, -45), ("a2", sh, 45)]:
        js += f'    tl.fromTo("#{gid}-{part}", {{rotation:{-a}, svgOrigin:{org}}}, {{rotation:{a}, duration:{fmt(period / 2)}, yoyo:true, repeat:{n}, ease:"sine.inOut"}}, {fmt(t0)});\n'
    js += f'    tl.fromTo("#{gid}", {{y:0}}, {{y:-12, duration:{fmt(period / 4)}, yoyo:true, repeat:{n * 2 + 1}, ease:"sine.out"}}, {fmt(t0)});\n'
    return js


def treadmill(tid, x, y, w):
    return (
        f'<g id="{tid}"><rect x="{x}" y="{y}" width="{w}" height="46" rx="23" fill="#343a40"/>'
        f'<line id="{tid}-belt" x1="{x + 30}" y1="{y + 23}" x2="{x + w - 30}" y2="{y + 23}" stroke="#868e96" stroke-width="8" stroke-dasharray="30 26"/>'
        f'<rect x="{x + w - 40}" y="{y - 230}" width="26" height="250" rx="12" fill="#495057"/><rect x="{x + w - 120}" y="{y - 250}" width="130" height="40" rx="16" fill="#495057"/></g>'
    )


def check(cid, x, y, r=40):
    return f'<g id="{cid}" transform="translate({x} {y})"><circle r="{r}" fill="#22c55e"/><path d="M{-r * 0.45} 0 L{-r * 0.12} {r * 0.32} L{r * 0.5} {-r * 0.32}" stroke="#fff" stroke-width="{r * 0.22}" fill="none" stroke-linecap="round" stroke-linejoin="round"/></g>'


def cross(cid, x, y, r=40):
    return f'<g id="{cid}" transform="translate({x} {y})"><circle r="{r}" fill="{C["red"]}"/><path d="M{-r * 0.38} {-r * 0.38} L{r * 0.38} {r * 0.38} M{r * 0.38} {-r * 0.38} L{-r * 0.38} {r * 0.38}" stroke="#fff" stroke-width="{r * 0.22}" stroke-linecap="round"/></g>'


# ================= 1: hook — running after money =================
def m1(d, c):
    sid = "m1"
    gx, gy, s = 420, 230, 1.0
    tm = treadmill("m1-tm", 160, 590, 720)
    g = guy("m1-g", gx, gy, s, money_eyes=True)
    rod = f'<path d="M{gx + 30} {gy + 90} L{gx + 330} {gy - 120}" stroke="#8d5524" stroke-width="12" stroke-linecap="round"/>'
    dangle = f'<g id="m1-dangle"><line x1="{gx + 330}" y1="{gy - 120}" x2="{gx + 330}" y2="{gy + 20}" stroke="#ced4da" stroke-width="4"/>{note("m1-note", gx + 330, gy + 80, 200, 100, "१ करोड")}</g>'
    sweat = "".join(f'<path id="m1-sw{i}" d="M{gx - 80 - i * 30} {gy - 30 + i * 20} q 12 22 0 32 q -12 -10 0 -32 Z" fill="#74c0fc"/>' for i in range(2))
    svg = tm + f'<g id="m1-rig">{g}{rod}{dangle}</g>' + sweat
    title = '<b>१ करोड</b> पाए?'
    extra_css = "#m1-title{top:180px;font-size:118px;}"
    extra = label("m1-chip", 540, 1080, "तर किन अझै दौड?", color="#14213d", bg=GOLD, size=54, anchor="center")
    js = ""
    js += run_js("m1-g", gx, gy, s, 0, d - 0.3)
    js += f'    tl.fromTo("#m1-tm-belt", {{attr:{{"stroke-dashoffset":0}}}}, {{attr:{{"stroke-dashoffset":560}}, duration:{fmt(d - 0.3)}, ease:"none"}}, 0);\n'
    js += f'    tl.fromTo("#m1-dangle", {{rotation:-10, svgOrigin:"{gx + 330} {gy - 120}"}}, {{rotation:10, duration:0.4, yoyo:true, repeat:{int((d - 0.5) / 0.4) - 1}, ease:"sine.inOut"}}, 0);\n'
    for i in range(2):
        js += f'    tl.fromTo("#m1-sw{i}", {{x:0, y:0, opacity:1}}, {{x:-50, y:30, opacity:0, duration:0.6, repeat:{int((d - 0.8) / 0.6) - 1}}}, {fmt(0.2 + i * 0.3)});\n'
    js += f'    tl.fromTo("#m1-title", {{scale:1}}, {{scale:1.08, duration:0.2, yoyo:true, repeat:3}}, 0.05);\n'
    js += pop("#m1-chip", c[1][0])
    return scene_file(sid, d, title, svg, extra, js, extra_css)


# ================= 2: money is just paper =================
def m2(d, c):
    sid = "m2"
    n = note("m2-note", 540, 170, 520, 250, "१०००")
    paper = (
        f'<g id="m2-paper"><path d="M300 60 L760 50 L790 160 L770 290 L320 300 L280 190 Z" fill="#e9ecef" stroke="#adb5bd" stroke-width="5"/>'
        f'<path d="M360 120 L450 180 M520 90 L600 200 M650 140 L700 250" stroke="#ced4da" stroke-width="5"/>{txt("m2-pt", 540, 200, "खाली कागज!", 60, "#495057")}</g>'
    )
    icons = (
        f'<g id="m2-i0" transform="translate(220 520)"><ellipse rx="90" ry="34" cy="30" fill="#fff"/><circle r="22" cx="-30" cy="0" fill="#ffd8a8"/><circle r="22" cx="10" cy="-8" fill="#ffd8a8"/><circle r="22" cx="40" cy="6" fill="#ffd8a8"/></g>'
        f'<g id="m2-i1" transform="translate(540 520)"><path d="M-90 0 L0 -80 L90 0 Z" fill="{C["red"]}"/><rect x="-70" y="0" width="140" height="100" fill="#fff"/><rect x="-18" y="40" width="36" height="60" fill="#8d5524"/></g>'
        f'<g id="m2-i2" transform="translate(860 520)"><path d="M0 -90 L80 -60 L80 10 Q80 70 0 100 Q-80 70 -80 10 L-80 -60 Z" fill="#4dabf7"/><path d="M-30 5 L-8 28 L32 -18" stroke="#fff" stroke-width="12" fill="none" stroke-linecap="round" stroke-linejoin="round"/></g>'
    )
    names = txt("m2-n0", 220, 670, "खाना", 44) + txt("m2-n1", 540, 670, "घर", 44) + txt("m2-n2", 860, 670, "सुरक्षा", 44)
    svg = n + paper + icons + names
    title = "पैसा = <b>कागजको टुक्रा?</b>"
    extra = label("m2-l", 540, 1080, "दिमागलाई: पैसा = ज्यानको सुरक्षा", color="#14213d", bg=GOLD, size=44, anchor="center")
    js = intro_js(sid)
    js += f'    tl.set("#m2-paper, #m2-i0, #m2-i1, #m2-i2, #m2-n0, #m2-n1, #m2-n2", {{opacity:0}}, 0);\n'
    tf = c[0][0] + 0.3
    js += f'    tl.to("#m2-note", {{scaleX:0, svgOrigin:"540 170", duration:0.25, ease:"power2.in"}}, {fmt(tf)});\n'
    js += f'    tl.fromTo("#m2-paper", {{opacity:1, scaleX:0, svgOrigin:"540 170"}}, {{scaleX:1, duration:0.25, ease:"power2.out"}}, {fmt(tf + 0.25)});\n'
    t1 = c[1][0]
    js += f'    tl.to("#m2-paper", {{opacity:0, duration:0.2}}, {fmt(t1)});\n'
    js += f'    tl.to("#m2-note", {{scaleX:1, svgOrigin:"540 170", duration:0.3, ease:"back.out(2)"}}, {fmt(t1 + 0.1)});\n'
    seg = max(0.4, (c[1][1] - c[1][0]) / 3)
    for k in range(3):
        js += f'    tl.fromTo("#m2-i{k}, #m2-n{k}", {{opacity:0, y:40}}, {{opacity:1, y:0, duration:0.35, ease:"back.out(2)"}}, {fmt(t1 + 0.3 + k * seg)});\n'
    js += pop("#m2-l", c[2][0])
    js += f'    tl.to("#m2-i2", {{scale:1.15, transformOrigin:"50% 50%", duration:0.3, yoyo:true, repeat:{max(1, int((d - c[2][0] - 0.8) / 0.3) - 1)}}}, {fmt(c[2][0] + 0.4)});\n'
    return scene_file(sid, d, title, svg, extra, js)


# ================= 3: dopamine & salary text =================
def m3(d, c):
    sid = "m3"
    brain = (
        f'<g id="m3-brain"><path d="M380 120 C 420 40, 640 40, 690 110 C 760 150, 760 260, 690 290 C 640 330, 440 330, 390 290 C 310 260, 310 160, 380 120 Z" fill="#f7a8c4" stroke="#c75b8a" stroke-width="8"/>'
        f'<path d="M540 60 L540 315 M440 140 Q480 170 450 210 M640 140 Q600 170 630 210" stroke="#c75b8a" stroke-width="7" fill="none" stroke-linecap="round"/></g>'
    )
    R = rr(31)
    dots = "".join(f'<circle id="m3-d{i}" cx="540" cy="190" r="{fmt(R.uniform(10, 18))}" fill="{GOLD}" stroke="#f08c00" stroke-width="3"/>' for i in range(14))
    dlabel = txt("m3-dl", 540, 380, "डोपामिन!", 56, GOLD)
    phone = (
        f'<g id="m3-phone"><rect x="140" y="430" width="260" height="360" rx="34" fill="#212529"/><rect x="156" y="460" width="228" height="300" rx="16" fill="#e7f5ff"/>'
        f'<g id="m3-msg"><rect x="166" y="500" width="208" height="120" rx="14" fill="#fff" stroke="{NOTE}" stroke-width="4"/>{txt("m3-m1", 270, 548, "तलब जम्मा भयो", 28, "#14213d")}{txt("m3-m2", 270, 595, "रु ५०,०००", 40, NOTE)}</g></g>'
    )
    g = guy("m3-g", 760, 520, 0.95, money_eyes=True, shirt="#ff922b")
    svg = brain + dots + dlabel + phone + g
    title = "<b>दिमाग</b>को खेल"
    extra = label("m3-l", 540, 1090, "मन फुरुक्क!", color="#14213d", bg=GOLD, size=54, anchor="center")
    js = intro_js(sid)
    js += f'    tl.set("#m3-dl, #m3-phone, #m3-g", {{opacity:0}}, 0);\n'
    t0 = c[0][0] + 0.8
    for i in range(14):
        a = i / 14 * 6.283
        js += f'    tl.fromTo("#m3-d{i}", {{x:0, y:0, opacity:0, scale:0.3, transformOrigin:"50% 50%"}}, {{x:{fmt(230 * math.cos(a))}, y:{fmt(150 * math.sin(a))}, opacity:1, scale:1, duration:0.7, ease:"power3.out"}}, {fmt(t0)});\n'
    js += f'    tl.to("#m3-dl", {{opacity:1, duration:0.2}}, {fmt(t0 + 0.2)});\n'
    js += f'    tl.to("#m3-brain", {{scale:1.06, transformOrigin:"50% 50%", duration:0.25, yoyo:true, repeat:{max(1, int((d - t0 - 0.6) / 0.25) - 1)}}}, {fmt(t0 + 0.3)});\n'
    t1 = c[1][0]
    js += f'    tl.fromTo("#m3-phone", {{opacity:0, y:80}}, {{opacity:1, y:0, duration:0.35, ease:"back.out(2)"}}, {fmt(t1)});\n'
    js += f'    tl.fromTo("#m3-msg", {{scale:0, svgOrigin:"270 560"}}, {{scale:1, duration:0.35, ease:"back.out(3)"}}, {fmt(t1 + 0.4)});\n'
    js += f'    tl.to("#m3-g", {{opacity:1, duration:0.2}}, {fmt(t1 + 0.6)});\n'
    js += f'    tl.fromTo("#m3-g", {{y:0}}, {{y:-60, duration:0.22, yoyo:true, repeat:{max(1, int((d - t1 - 1.0) / 0.22) - 1)}, ease:"power2.out"}}, {fmt(t1 + 0.7)});\n'
    js += pop("#m3-l", t1 + 0.9)
    return scene_file(sid, d, title, svg, extra, js)


# ================= 4: happiness fades — the treadmill =================
def m4(d, c):
    sid = "m4"
    axes = f'<line x1="120" y1="420" x2="980" y2="420" stroke="#adb5bd" stroke-width="6"/><line x1="120" y1="80" x2="120" y2="420" stroke="#adb5bd" stroke-width="6"/>' + txt("m4-ay", 120, 60, "खुसी", 40, GOLD) + txt("m4-ax", 940, 470, "दिन", 38, "#adb5bd")
    line_ = f'<path id="m4-line" d="M130 330 L300 330 L340 110 C 420 120, 520 300, 640 325 C 760 335, 880 330, 970 330" stroke="{GOLD}" stroke-width="12" fill="none" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="1400" stroke-dashoffset="1400"/>'
    phone = f'<g id="m4-ph"><rect x="310" y="20" width="60" height="100" rx="12" fill="#212529"/><rect x="318" y="30" width="44" height="78" rx="6" fill="#74c0fc"/>{txt("m4-pt", 440, 70, "नयाँ मोबाइल!", 34, "#fff", "start")}</g>'
    tm = treadmill("m4-tm", 250, 740, 600)
    g = guy("m4-g", 520, 450, 0.85)
    svg = axes + line_ + phone + f'<g id="m4-run">{tm}{g}</g>'
    title = "खुसी <b>टिक्दैन</b>"
    extra = label("m4-l", 540, 1100, "जति दौडे पनि उही ठाउँ!", color="#14213d", bg=GOLD, size=46, anchor="center")
    js = intro_js(sid)
    js += f'    tl.set("#m4-ph, #m4-run", {{opacity:0}}, 0);\n'
    t1 = c[1][0]
    js += f'    tl.to("#m4-line", {{attr:{{"stroke-dashoffset":0}}, duration:{fmt(max(1.2, c[1][1] - c[1][0]))}, ease:"none"}}, {fmt(t1)});\n'
    js += pop("#m4-ph", t1 + 0.4)
    t2 = c[2][0]
    js += f'    tl.to("#m4-run", {{opacity:1, duration:0.3}}, {fmt(t2 - 0.1)});\n'
    js += run_js("m4-g", 520, 450, 0.85, t2, d - 0.3, 0.28)
    js += f'    tl.fromTo("#m4-tm-belt", {{attr:{{"stroke-dashoffset":0}}}}, {{attr:{{"stroke-dashoffset":400}}, duration:{fmt(max(0.5, d - t2 - 0.3))}, ease:"none"}}, {fmt(t2)});\n'
    js += pop("#m4-l", t2 + 0.2)
    return scene_file(sid, d, title, svg, extra, js)


# ================= 5: the neighbour effect =================
def m5(d, c):
    sid = "m5"

    def option(oid, x, you, nb, you_h, nb_h, letter):
        base = 520
        return (
            f'<g id="{oid}"><rect x="{x}" y="40" width="440" height="560" rx="36" fill="#1b2140"/>{txt(oid + "-L", x + 220, 110, letter, 60, GOLD)}'
            f'<rect x="{x + 70}" y="{base - you_h}" width="120" height="{you_h}" rx="14" fill="#4dabf7"/>{txt(oid + "-yv", x + 130, base - you_h - 16, you, 36)}'
            f'<rect x="{x + 250}" y="{base - nb_h}" width="120" height="{nb_h}" rx="14" fill="#ff922b"/>{txt(oid + "-nv", x + 310, base - nb_h - 16, nb, 36)}'
            f'{txt(oid + "-yl", x + 130, 570, "तपाईं", 36, "#4dabf7")}{txt(oid + "-nl", x + 310, 570, "छिमेकी", 36, "#ff922b")}</g>'
        )
    a = option("m5-a", 60, "५० हजार", "२५ हजार", 160, 80, "A")
    b = option("m5-b", 580, "१ लाख", "२ लाख", 160, 320, "B")
    chk = check("m5-ok", 280, 680, 46)
    svg = a + b + chk
    title = "<b>छिमेकी</b> इफेक्ट"
    extra = (
        label("m5-l1", 540, 1080, "झन्डै आधाले A रोजे!", color="#14213d", bg=GOLD, size=48, anchor="center")
        + label("m5-l2", 540, 1080, "छिमेकीभन्दा बढी भए पुग्यो!", color="#fff", bg=C["red"], size=46, anchor="center")
    )
    js = intro_js(sid)
    js += f'    tl.set("#m5-ok", {{opacity:0}}, 0);\n'
    js += pop("#m5-a", c[0][0] + 0.2)
    js += pop("#m5-b", c[0][0] + 0.5)
    t1 = c[1][0]
    js += pop("#m5-ok", t1 + 0.8)
    js += f'    tl.to("#m5-a", {{scale:1.05, transformOrigin:"50% 50%", duration:0.3, yoyo:true, repeat:3}}, {fmt(t1 + 0.9)});\n'
    js += pop("#m5-l1", t1 + 0.3)
    t2 = c[2][0]
    js += f'    tl.to("#m5-l1", {{opacity:0, duration:0.15}}, {fmt(t2 - 0.15)});\n'
    js += pop("#m5-l2", t2)
    return scene_file(sid, d, title, svg, extra, js)


# ================= 6: losing hurts more =================
def m6(d, c):
    sid = "m6"
    stand = f'<path d="M540 150 L540 640 M420 660 L660 660" stroke="#adb5bd" stroke-width="18" stroke-linecap="round"/><path d="M500 640 L580 640 L540 600 Z" fill="#adb5bd"/>'

    def pan(pid, x, label_txt, face_sad, color):
        mouth = (f'<path d="M{x - 26} 470 Q{x} 448 {x + 26} 470" stroke="#14213d" stroke-width="7" fill="none" stroke-linecap="round"/>' if face_sad
                 else f'<path d="M{x - 26} 458 Q{x} 482 {x + 26} 458" stroke="#14213d" stroke-width="7" fill="none" stroke-linecap="round"/>')
        tear = f'<path d="M{x - 30} 440 q 8 18 0 26 q -8 -8 0 -26 Z" fill="#74c0fc"/>' if face_sad else ""
        return (
            f'<g id="{pid}"><line x1="{x - 110}" y1="300" x2="{x}" y2="160" stroke="#868e96" stroke-width="5"/><line x1="{x + 110}" y1="300" x2="{x}" y2="160" stroke="#868e96" stroke-width="5"/>'
            f'<path d="M{x - 130} 300 Q{x} 380 {x + 130} 300 Z" fill="{color}"/>'
            f'<circle cx="{x}" cy="450" r="60" fill="{GOLD}"/><circle cx="{x - 20}" cy="435" r="7" fill="#14213d"/><circle cx="{x + 20}" cy="435" r="7" fill="#14213d"/>{mouth}{tear}'
            f'{txt(pid + "-t", x, 560, label_txt, 38)}</g>'
        )
    beam = f'<g id="m6-beam"><line x1="230" y1="160" x2="850" y2="160" stroke="#dee2e6" stroke-width="16" stroke-linecap="round"/><circle cx="540" cy="160" r="20" fill="#dee2e6"/></g>'
    left = pan("m6-pl", 230, "रु १०० हरायो", True, "#e03131")
    right = pan("m6-pr", 850, "रु १०० भेटियो", False, "#2f9e44")
    badge = f'<g id="m6-x2"><circle cx="540" cy="70" r="62" fill="{C["red"]}"/>{txt("m6-x2t", 540, 92, "२x", 60)}</g>'
    svg = stand + beam + left + right + badge
    title = "गुमाउँदा <b>दोब्बर</b> दुख्छ"
    js = intro_js(sid)
    js += f'    tl.set("#m6-pl, #m6-pr, #m6-x2", {{opacity:0}}, 0);\n'
    js += f'    tl.to("#m6-pl", {{opacity:1, duration:0.3}}, {fmt(c[0][0] + 0.2)});\n'
    t1 = c[1][0]
    js += f'    tl.to("#m6-pr", {{opacity:1, duration:0.3}}, {fmt(t1 + 0.1)});\n'
    tilt = t1 + 0.6
    # left side goes down (loss weighs more)
    js += f'    tl.to("#m6-beam", {{rotation:-14, svgOrigin:"540 160", duration:0.7, ease:"bounce.out"}}, {fmt(tilt)});\n'
    js += f'    tl.to("#m6-pl", {{y:150, duration:0.7, ease:"bounce.out"}}, {fmt(tilt)});\n'
    js += f'    tl.to("#m6-pr", {{y:-150, duration:0.7, ease:"bounce.out"}}, {fmt(tilt)});\n'
    js += pop("#m6-x2", tilt + 0.5)
    return scene_file(sid, d, title, svg, "", js)


# ================= 7: what money can't buy =================
def m7(d, c):
    sid = "m7"

    def tag(tid, x, y, text, ok):
        mark = check(tid + "-m", x + 330, y + 60, 34) if ok else cross(tid + "-m", x + 330, y + 60, 34)
        stamp = "" if ok else f'<g id="{tid}-s"><rect x="{x + 40}" y="{y + 30}" width="250" height="64" rx="10" fill="none" stroke="{C["red"]}" stroke-width="6" transform="rotate(-8 {x + 165} {y + 62})"/>{txt(tid + "-st", x + 165, y + 76, "बिक्रीमा छैन", 34, C["red"])}</g>'
        return (
            f'<g id="{tid}"><path d="M{x} {y} L{x + 380} {y} L{x + 420} {y + 60} L{x + 380} {y + 120} L{x} {y + 120} Z" fill="#fff"/><circle cx="{x + 392}" cy="{y + 60}" r="10" fill="#1b2140"/>'
            f'{txt(tid + "-t", x + 165, y + 76, text, 46, "#14213d")}{mark}{stamp}</g>'
        )
    tags = (
        tag("m7-t0", 330, 20, "चिन्ता कम", True)
        + tag("m7-t1", 330, 190, "साथी", False)
        + tag("m7-t2", 330, 360, "परिवार", False)
        + tag("m7-t3", 330, 530, "मीठो निद्रा", False)
    )
    cart = f'<g id="m7-cart"><path d="M60 140 L110 140 L160 380 L290 380" stroke="#dee2e6" stroke-width="12" fill="none" stroke-linecap="round" stroke-linejoin="round"/><path d="M120 190 L300 190 L280 320 L150 320 Z" fill="#495057"/><circle cx="180" cy="420" r="22" fill="#dee2e6"/><circle cx="270" cy="420" r="22" fill="#dee2e6"/>{note("m7-n", 210, 160, 150, 70, "५००")}</g>'
    svg = cart + tags
    title = "पैसाले के <b>किन्न सक्दैन</b>?"
    js = intro_js(sid)
    js += f'    tl.set("#m7-t1-s, #m7-t2-s, #m7-t3-s", {{opacity:0}}, 0);\n'
    js += pop("#m7-t0", c[0][0] + 0.2)
    t1 = c[1][0]
    seg = max(0.4, (c[1][1] - c[1][0]) / 3.5)
    for k in range(1, 4):
        js += pop(f"#m7-t{k}", t1 + (k - 1) * seg)
        js += f'    tl.fromTo("#m7-t{k}-s", {{opacity:0, scale:2.2, transformOrigin:"50% 50%"}}, {{opacity:1, scale:1, duration:0.25, ease:"power4.in"}}, {fmt(t1 + (k - 1) * seg + 0.35)});\n'
    js += f'    tl.fromTo("#m7-cart", {{x:0}}, {{x:14, duration:0.25, yoyo:true, repeat:{int((d - 0.8) / 0.25) - 1}}}, 0.4);\n'
    return scene_file(sid, d, title, svg, "", js)


# ================= 8: CTA =================
def m8(d, c):
    sid = "m8"
    case = (
        f'<g id="m8-case"><rect x="340" y="150" width="400" height="260" rx="26" fill="#5c3d2e"/><rect x="480" y="110" width="120" height="50" rx="16" fill="none" stroke="#5c3d2e" stroke-width="16"/>'
        f'<rect x="340" y="250" width="400" height="20" fill="#3e2a1f"/>{txt("m8-ct", 540, 360, "१ करोड", 60, GOLD)}</g>'
    )
    R = rr(81)
    flying = "".join(note(f"m8-n{i}", 540, 200, 120, 60, "") for i in range(8))
    bub = (
        f'<g id="m8-bub"><rect x="160" y="470" width="760" height="140" rx="40" fill="#fff"/><path d="M260 600 l -40 60 l 100 -60 Z" fill="#fff"/>'
        f'{txt("m8-bt", 540, 560, "पहिले के किन्ने?", 62, "#14213d")}</g>'
    )
    tag = f'<g id="m8-tag" transform="translate(540 730)"><rect x="-340" y="-56" width="680" height="112" rx="56" fill="{C["red"]}"/>{txt("m8-tg", 0, 18, "@ कन्जुस साथीलाई ट्याग", 48)}</g>'
    svg = flying + case + bub + tag
    title = "<b>कमेन्ट</b> गर्नुहोस्!"
    extra_css = "#m8-title{font-size:100px;}"
    js = intro_js(sid)
    for i in range(8):
        a = -2.6 + i * 0.75
        js += f'    tl.fromTo("#m8-n{i}", {{x:0, y:0, rotation:0, opacity:0}}, {{x:{fmt(420 * math.cos(a))}, y:{fmt(-120 + 160 * math.sin(a))}, rotation:{int(R.uniform(-90, 90))}, opacity:1, duration:1.0, ease:"power3.out"}}, {fmt(0.4 + i * 0.08)});\n'
    js += pop("#m8-bub", c[0][0] + 0.2)
    js += pop("#m8-tag", c[1][0] + 0.6)
    js += f'    tl.to("#m8-tag", {{scale:1.06, duration:0.3, yoyo:true, repeat:{max(1, int((d - c[1][0] - 1.4) / 0.3) - 1)}, transformOrigin:"50% 50%"}}, {fmt(c[1][0] + 1.1)});\n'
    return scene_file(sid, d, title, svg, "", js, extra_css)


SCENE_FNS = [m1, m2, m3, m4, m5, m6, m7, m8]
