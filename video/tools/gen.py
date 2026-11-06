# -*- coding: utf-8 -*-
"""Generates the HyperFrames scenes for the Nepali tattoo explainer."""
import json, math, os, random, re

OUT = "/home/user/Astha/video"
W, H = 1080, 1920

# ---------- timing (seconds, from the voiceover's pauses) ----------
# scene boundaries (paragraph starts)
SCENES = [0.0, 7.0, 15.7, 22.55, 31.0, 41.9, 48.75, 57.9, 67.15, 72.85]
TOTAL = 81.6
DUR = [SCENES[i + 1] - SCENES[i] if i + 1 < len(SCENES) else TOTAL - SCENES[i] for i in range(len(SCENES))]

# clause (text, start, end)
CLAUSES = [
    ("रोकिनुहोस्!", 0.15, 1.15),
    ("तपाईंको ट्याटुभित्र अहिले पनि एउटा लडाइँ चलिरहेको छ…", 1.3, 4.98),
    ("र तपाईंलाई थाहै छैन!", 5.13, 6.86),
    ("ट्याटु मेसिनको सुई एक मिनेटमा हजारौं पटक माथि-तल गर्छ,", 7.1, 11.46),
    ("र हरेक पटक छालाभित्र मसीको सानो थोपा छाड्छ।", 11.66, 15.56),
    ("तर मसी छालाको माथिल्लो तहमा होइन…", 15.77, 18.66),
    ("करिब एक-दुई मिलिमिटर तल,", 18.9, 20.87),
    ("डर्मिस तहमा पुग्छ।", 21.03, 22.39),
    ("किन?", 22.58, 23.2),
    ("किनकि माथिल्लो तह हरेक केही हप्तामा झरेर नयाँ बन्छ।", 23.35, 27.47),
    ("मसी त्यहाँ भए,", 27.7, 28.8),
    ("ट्याटु एक महिनामै हराउँथ्यो।", 28.95, 30.76),
    ("सुईले घाउ बनाउनेबित्तिकै,", 31.03, 33.0),
    ("शरीरको इम्युन सिस्टम सक्रिय हुन्छ।", 33.15, 35.34),
    ("म्याक्रोफेज भन्ने सेतो रक्तकोषहरू दौडिएर आउँछन्,", 35.45, 39.12),
    ("र मसीलाई दुश्मन ठानेर निल्छन्।", 39.26, 41.66),
    ("तर मसीका कण धेरै ठूला हुन्छन्।", 41.93, 44.29),
    ("म्याक्रोफेजले पचाउनै सक्दैन…", 44.44, 46.53),
    ("र मसी उसैभित्र थुनिन्छ।", 46.66, 48.59),
    ("अनि अचम्मको कुरा —", 48.77, 50.2),
    ("जब त्यो कोष मर्छ,", 50.3, 51.7),
    ("नयाँ म्याक्रोफेज आएर त्यही मसी फेरि निल्छ।", 51.8, 55.32),
    ("यो चक्र जीवनभर चलिरहन्छ।", 55.5, 57.76),
    ("यसरी इम्युन सिस्टमले मसीलाई एकै ठाउँमा थुनेर राख्छ,", 57.94, 61.94),
    ("शरीरभरि फैलिन दिँदैन।", 62.05, 63.83),
    ("र त्यही थुनिएको मसी नै तपाईंको ट्याटु हो!", 63.96, 66.99),
    ("लेजरले यी कणलाई टुक्रा-टुक्रा पारेपछि मात्र,", 67.16, 70.4),
    ("शरीरले बिस्तारै सफा गर्न सक्छ।", 70.5, 72.69),
    ("अचम्म लाग्यो?", 72.89, 73.94),
    ("यो भिडियो ट्याटु भएको साथीलाई सेयर गर्नुहोस्,", 74.07, 77.09),
    ("र यस्तै रोचक विज्ञानका लागि फलो गर्नुहोस्!", 77.24, 80.54),
]

KEYWORDS = ["ट्याटु", "मसी", "डर्मिस", "म्याक्रोफेज", "इम्युन", "लेजर", "हजारौं", "सुई", "जीवनभर", "सेयर", "फलो", "लडाइँ", "रक्तकोष"]

FONT_FACE = """
@font-face{font-family:'Mukta';font-weight:500;src:url('assets/fonts/mukta-devanagari-500-normal.woff2') format('woff2');unicode-range:U+0900-097F,U+1CD0-1CF9,U+200C-200D,U+20A8,U+20B9,U+25CC,U+A830-A839,U+A8E0-A8FF;}
@font-face{font-family:'Mukta';font-weight:800;src:url('assets/fonts/mukta-devanagari-800-normal.woff2') format('woff2');unicode-range:U+0900-097F,U+1CD0-1CF9,U+200C-200D,U+20A8,U+20B9,U+25CC,U+A830-A839,U+A8E0-A8FF;}
@font-face{font-family:'Mukta';font-weight:500;src:url('assets/fonts/mukta-latin-500-normal.woff2') format('woff2');unicode-range:U+0000-00FF,U+2000-206F,U+2212;}
@font-face{font-family:'Mukta';font-weight:800;src:url('assets/fonts/mukta-latin-800-normal.woff2') format('woff2');unicode-range:U+0000-00FF,U+2000-206F,U+2212;}
"""

C = dict(
    ink="#3a1d9a", inkdark="#1d0c55", mac="#c8f7df", macedge="#3fcf93", nuc="#2a9d6f",
    epi="#f4c7a6", epiedge="#d99b78", derm="#e79b8c", dermline="#cf7f72", fat="#f7e3a3",
    yellow="#ffd23f", red="#ff4d6d", blue="#5ad1ff", steel="#3b4659", steel2="#7b879b", copper="#d08a3a",
)


def rr(seed):
    return random.Random(seed)


def fmt(x):
    return f"{x:.2f}".rstrip("0").rstrip(".")


# ---------- reusable SVG bits ----------
def macrophage(gid, cx, cy, r, ink=0, seed=1, eyes=False, inkid=None):
    """A macrophage: wobbly body, nucleus, optional ink inside."""
    R = rr(seed)
    bumps = "".join(
        f'<circle cx="{fmt(cx + r * 0.92 * math.cos(a))}" cy="{fmt(cy + r * 0.92 * math.sin(a))}" r="{fmt(r * R.uniform(0.22, 0.32))}" fill="{C["mac"]}" stroke="{C["macedge"]}" stroke-width="{fmt(max(2, r * 0.045))}"/>'
        for a in [R.uniform(0, 6.28) for _ in range(5)]
    )
    body = (
        f'<g class="body">{bumps}'
        f'<ellipse cx="{cx}" cy="{cy}" rx="{r}" ry="{fmt(r * 0.9)}" fill="{C["mac"]}" stroke="{C["macedge"]}" stroke-width="{fmt(max(3, r * 0.06))}"/>'
        f'<ellipse cx="{fmt(cx - r * 0.3)}" cy="{fmt(cy - r * 0.25)}" rx="{fmt(r * 0.32)}" ry="{fmt(r * 0.26)}" fill="{C["nuc"]}" opacity="0.55"/></g>'
    )
    dots = ""
    for i in range(ink):
        a = R.uniform(0, 6.28)
        d = R.uniform(0.1, 0.5) * r
        dots += f'<circle cx="{fmt(cx + r * 0.15 + d * math.cos(a))}" cy="{fmt(cy + r * 0.1 + d * math.sin(a))}" r="{fmt(r * R.uniform(0.09, 0.14))}" fill="{C["ink"]}" stroke="{C["inkdark"]}" stroke-width="2"/>'
    if dots:
        dots = f'<g{(" id=%s" % json.dumps(inkid)) if inkid else ""}>{dots}</g>'
    face = ""
    if eyes:
        face = (
            f'<circle cx="{fmt(cx + r * 0.05)}" cy="{fmt(cy - r * 0.15)}" r="{fmt(r * 0.1)}" fill="#14213d"/>'
            f'<circle cx="{fmt(cx + r * 0.4)}" cy="{fmt(cy - r * 0.15)}" r="{fmt(r * 0.1)}" fill="#14213d"/>'
            f'<path d="M{fmt(cx + r * 0.02)} {fmt(cy + r * 0.12)} Q{fmt(cx + r * 0.22)} {fmt(cy + r * 0.32)} {fmt(cx + r * 0.44)} {fmt(cy + r * 0.12)}" stroke="#14213d" stroke-width="{fmt(r * 0.06)}" fill="none" stroke-linecap="round"/>'
        )
    return f'<g id="{gid}">{body}{dots}{face}</g>'


def ink_dot(did, cx, cy, r):
    return f'<circle id="{did}" cx="{fmt(cx)}" cy="{fmt(cy)}" r="{fmt(r)}" fill="{C["ink"]}" stroke="{C["inkdark"]}" stroke-width="3"/>'


def dermis_panel(pid, x, y, w, h, seed=3):
    """Pink dermis close-up with collagen fibres."""
    R = rr(seed)
    lines = ""
    for i in range(9):
        yy = y + 40 + i * (h - 80) / 8
        amp = R.uniform(8, 18)
        lines += f'<path d="M{x + 20} {fmt(yy)} q {fmt(w / 8)} {fmt(-amp)} {fmt(w / 4)} 0 t {fmt(w / 4)} 0 t {fmt(w / 4)} 0 t {fmt(w / 4 - 40)} 0" stroke="{C["dermline"]}" stroke-width="5" fill="none" opacity="0.45" stroke-linecap="round"/>'
    return (
        f'<g id="{pid}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="48" fill="{C["derm"]}"/>{lines}'
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="48" fill="none" stroke="#ffffff" stroke-opacity="0.25" stroke-width="4"/></g>'
    )


def skin_section(prefix, x, y, w, epi_h, derm_h, fat_h, seed=5):
    R = rr(seed)
    cells = ""
    cw, ch = 70, epi_h / 3
    for row in range(3):
        for col in range(int(w / cw) + 1):
            cx = x + col * cw + (cw / 2 if row % 2 else 0) - 20
            if cx > x + w - 30 or cx < x - 10:
                continue
            cells += f'<rect class="{prefix}-cell r{row}" x="{fmt(cx + 4)}" y="{fmt(y + row * ch + 4)}" width="{cw - 8}" height="{fmt(ch - 8)}" rx="14" fill="#f9d6bb" stroke="{C["epiedge"]}" stroke-width="2.5"/>'
    collagen = ""
    for i in range(6):
        yy = y + epi_h + 30 + i * (derm_h - 60) / 5
        collagen += f'<path d="M{x + 10} {fmt(yy)} q {fmt(w / 8)} -14 {fmt(w / 4)} 0 t {fmt(w / 4)} 0 t {fmt(w / 4)} 0 t {fmt(w / 4 - 20)} 0" stroke="{C["dermline"]}" stroke-width="5" fill="none" opacity="0.5"/>'
    fat = ""
    fy = y + epi_h + derm_h
    for i in range(int(w / 60)):
        fat += f'<circle cx="{fmt(x + 30 + i * 60 + R.uniform(-6, 6))}" cy="{fmt(fy + fat_h / 2 + R.uniform(-10, 10))}" r="{fmt(R.uniform(22, 30))}" fill="#fbeec3" stroke="#e2c46f" stroke-width="3"/>'
    vessel = f'<path d="M{x} {fmt(y + epi_h + derm_h * 0.78)} C {fmt(x + w * 0.3)} {fmt(y + epi_h + derm_h * 0.6)}, {fmt(x + w * 0.6)} {fmt(y + epi_h + derm_h * 0.95)}, {x + w} {fmt(y + epi_h + derm_h * 0.75)}" stroke="#c2263f" stroke-width="22" fill="none" stroke-linecap="round" opacity="0.8"/>'
    return (
        f'<g id="{prefix}-skin">'
        f'<rect id="{prefix}-fat" x="{x}" y="{fy}" width="{w}" height="{fat_h}" fill="{C["fat"]}"/>{fat}'
        f'<rect id="{prefix}-derm" x="{x}" y="{y + epi_h}" width="{w}" height="{derm_h}" fill="{C["derm"]}"/>{collagen}{vessel}'
        f'<rect id="{prefix}-epi" x="{x}" y="{y}" width="{w}" height="{epi_h}" fill="{C["epi"]}"/>'
        f'<g id="{prefix}-cells">{cells}</g>'
        f"</g>"
    )


def label(lid, x, y, text, color="#ffffff", bg="rgba(10,14,35,0.85)", size=40, anchor="left"):
    """HTML label chip placed in frame pixels. Centred chips span the width so no CSS transform is needed."""
    if anchor == "center":
        pos = f"left:0;right:0;top:{y}px;text-align:center"
    else:
        pos = f"left:{x}px;top:{y}px"
    return (
        f'<div id="{lid}" class="chipbox" style="{pos}">'
        f'<span class="chip" style="font-size:{size}px;color:{color};background:{bg}">{text}</span></div>'
    )


# ---------- scene shell ----------
SCENE_CSS = """
#root{position:absolute;inset:0;overflow:hidden;font-family:'Mukta',sans-serif;}
.wrap{position:absolute;inset:0;}
.title{position:absolute;left:60px;right:60px;top:200px;text-align:center;font-weight:800;font-size:68px;line-height:1.15;color:#fff;}
.title b{color:#ffd23f;font-weight:800;}
.title{text-shadow:0 4px 0 rgba(0,0,0,.55),0 0 28px rgba(0,0,0,.6);}
.stage{position:absolute;left:0;top:360px;width:1080px;height:780px;overflow:visible;}
.chipbox{position:absolute;}
.chip{display:inline-block;font-weight:800;padding:8px 28px 4px;border-radius:999px;white-space:nowrap;line-height:1.25;box-shadow:0 8px 30px rgba(0,0,0,.35);}
"""


def scene_file(sid, dur, title_html, svg, extra_html, js, extra_css="", stage_top=360, stage_h=780):
    return f"""<template>
  <style>
{FONT_FACE}
{SCENE_CSS}
#{sid}-stage{{top:{stage_top}px;height:{stage_h}px;}}
{extra_css}
  </style>
  <div id="root" data-composition-id="{sid}" data-width="{W}" data-height="{H}" data-layout-allow-overlap>
    <div id="{sid}-wrap" class="wrap">
      <div id="{sid}-title" class="title">{title_html}</div>
      <svg id="{sid}-stage" class="stage" viewBox="0 0 1080 {stage_h}" xmlns="http://www.w3.org/2000/svg" data-layout-allow-overflow>
{svg}
      </svg>
{extra_html}
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    const D = {fmt(dur)};
{js}
    tl.to("#{sid}-wrap", {{ opacity: 0, duration: 0.22, ease: "power2.in" }}, D - 0.26);
    window.__timelines["{sid}"] = tl;
  </script>
</template>
"""


def intro_js(sid, at0=False):
    if at0:
        return ""
    return (
        f'    tl.fromTo("#{sid}-title", {{opacity:0, y:-30}}, {{opacity:1, y:0, duration:0.35, ease:"back.out(2)"}}, 0.05);\n'
        f'    tl.fromTo("#{sid}-stage", {{opacity:0, scale:0.92, transformOrigin:"50% 50%"}}, {{opacity:1, scale:1, duration:0.4, ease:"power3.out"}}, 0.0);\n'
    )


def pop(sel, t, from_scale=0.4, dur=0.35):
    return f'    tl.fromTo("{sel}", {{opacity:0, scale:{from_scale}, transformOrigin:"50% 50%"}}, {{opacity:1, scale:1, duration:{dur}, ease:"back.out(2.2)"}}, {fmt(t)});\n'


def wobble(sel, t0, t1, amt=0.05, period=0.6):
    n = max(1, int((t1 - t0) / (period / 2)) - 1)
    return f'    tl.fromTo("{sel}", {{scaleX:1, scaleY:1, transformOrigin:"50% 50%"}}, {{scaleX:{1 + amt}, scaleY:{1 - amt}, duration:{fmt(period / 2)}, ease:"sine.inOut", yoyo:true, repeat:{n}}}, {fmt(t0)});\n'


# ================= SCENE 1: hook =================
def s1(d):
    sid = "s1"
    # arm with tattoo + magnifier showing the battle
    R = rr(11)
    heart = "M0 -40 C 0 -80, -70 -80, -70 -30 C -70 10, -20 40, 0 70 C 20 40, 70 10, 70 -30 C 70 -80, 0 -80, 0 -40 Z"
    arm = (
        f'<g id="s1-arm"><g transform="rotate(-14 540 520)">'
        f'<rect x="-80" y="400" width="1240" height="300" rx="150" fill="#e8b18c"/>'
        f'<rect x="-80" y="400" width="1240" height="90" rx="45" fill="#f2c5a3" opacity="0.7"/>'
        f'<g transform="translate(330 555) scale(1.25)"><path d="{heart}" fill="none" stroke="{C["inkdark"]}" stroke-width="14"/>'
        f'<path d="M-90 0 L-130 0 M90 0 L130 0" stroke="{C["inkdark"]}" stroke-width="10" stroke-linecap="round"/></g>'
        f"</g></g>"
    )
    lens_cx, lens_cy, lens_r = 700, 330, 250
    inner = ""
    for i in range(10):
        inner += ink_dot(f"s1-ink{i}", lens_cx + R.uniform(-150, 150), lens_cy + R.uniform(-150, 150), R.uniform(10, 16))
    macs = (
        macrophage("s1-m0", lens_cx - 110, lens_cy - 60, 70, ink=4, seed=1)
        + macrophage("s1-m1", lens_cx + 100, lens_cy + 80, 80, ink=5, seed=2)
        + macrophage("s1-m2", lens_cx + 60, lens_cy - 140, 50, ink=2, seed=3)
    )
    sparks = ""
    for i, (sx, sy) in enumerate([(lens_cx - 20, lens_cy + 10), (lens_cx - 170, lens_cy + 120), (lens_cx + 170, lens_cy - 40)]):
        sparks += f'<g id="s1-spark{i}" transform="translate({sx} {sy})"><path d="M0 -34 L8 -8 L34 0 L8 8 L0 34 L-8 8 L-34 0 L-8 -8 Z" fill="{C["yellow"]}"/></g>'
    lens = (
        f'<defs><clipPath id="s1-clip"><circle cx="{lens_cx}" cy="{lens_cy}" r="{lens_r}"/></clipPath></defs>'
        f'<g id="s1-lens">'
        f'<line x1="{lens_cx - 175}" y1="{lens_cy + 175}" x2="{lens_cx - 330}" y2="{lens_cy + 330}" stroke="#2b3245" stroke-width="56" stroke-linecap="round"/>'
        f'<g clip-path="url(#s1-clip)">{dermis_panel("s1-derm", lens_cx - lens_r, lens_cy - lens_r, 2 * lens_r, 2 * lens_r)}{inner}{macs}{sparks}</g>'
        f'<circle cx="{lens_cx}" cy="{lens_cy}" r="{lens_r}" fill="none" stroke="#e8edf5" stroke-width="26"/>'
        f'<circle cx="{lens_cx}" cy="{lens_cy}" r="{lens_r - 13}" fill="none" stroke="#9aa6bb" stroke-width="6"/>'
        f'<path d="M{lens_cx - 170} {lens_cy - 120} A {lens_r - 40} {lens_r - 40} 0 0 1 {lens_cx - 60} {lens_cy - 200}" stroke="#ffffff" stroke-width="14" fill="none" opacity="0.5" stroke-linecap="round"/>'
        f"</g>"
    )
    svg = arm + lens
    title = 'तपाईंको <b>ट्याटुभित्र</b><br/>चलिरहेको छ <b>लडाइँ!</b>'
    extra_css = "#s1-title{top:190px;font-size:96px;line-height:1.12;} #s1-stop{position:absolute;left:0;right:0;top:118px;text-align:center;}"
    extra = label("s1-badge", 540, 1095, "शरीर vs मसी", color="#14213d", bg=C["yellow"], size=48, anchor="center")
    js = ""
    js += wobble("#s1-m0 .body", 0, d - 0.3, 0.07, 0.7)
    js += wobble("#s1-m1 .body", 0.1, d - 0.3, 0.06, 0.8)
    js += wobble("#s1-m2 .body", 0.05, d - 0.3, 0.08, 0.6)
    for i in range(3):
        js += f'    tl.fromTo("#s1-spark{i}", {{scale:0.3, rotation:0, opacity:1, transformOrigin:"50% 50%"}}, {{scale:1.2, rotation:90, opacity:0.2, duration:0.4, ease:"power2.out", yoyo:true, repeat:{int((d - 0.6) / 0.4) - 1}}}, {fmt(0.15 * i)});\n'
    # ink being pulled toward the cells
    for i in range(10):
        tx = (lens_cx - 110) if i % 2 == 0 else (lens_cx + 100)
        ty = (lens_cy - 60) if i % 2 == 0 else (lens_cy + 80)
        js += f'    tl.to("#s1-ink{i}", {{x:"+={fmt((tx - lens_cx) * 0.25)}", y:"+={fmt((ty - lens_cy) * 0.25)}", duration:{fmt(d - 1)}, ease:"sine.inOut"}}, 0.3);\n'
    js += f'    tl.fromTo("#s1-lens", {{scale:1, transformOrigin:"700px 330px"}}, {{scale:1.06, duration:0.5, ease:"sine.inOut", yoyo:true, repeat:{int((d - 1) / 0.5) - 1}}}, 0.4);\n'
    js += f'    tl.fromTo("#s1-title", {{scale:1}}, {{scale:1.05, duration:0.18, ease:"power2.out", yoyo:true, repeat:1}}, 0.12);\n'
    js += f'    tl.fromTo("#s1-badge", {{scale:1}}, {{scale:1.1, duration:0.25, ease:"sine.inOut", yoyo:true, repeat:{int((d - 1.5) / 0.25) - 1}}}, 1.2);\n'
    return scene_file(sid, d, title, svg, extra, js, extra_css)


# ================= SCENE 2: the machine =================
def s2(d):
    sid = "s2"
    tipx, tipy = 540, 600
    # machine drawn around the needle tip (540, 600)
    mach = (
        f'<g id="s2-mach">'
        f'<g id="s2-frame">'
        f'<path d="M380 60 L380 330 Q380 360 410 360 L560 360" stroke="{C["steel"]}" stroke-width="44" fill="none" stroke-linejoin="round"/>'
        f'<rect x="420" y="160" width="70" height="170" rx="14" fill="{C["copper"]}"/>'
        f'<rect x="510" y="160" width="70" height="170" rx="14" fill="{C["copper"]}"/>'
        + "".join(f'<line x1="420" y1="{y}" x2="490" y2="{y}" stroke="#a5652a" stroke-width="5"/><line x1="510" y1="{y}" x2="580" y2="{y}" stroke="#a5652a" stroke-width="5"/>' for y in range(180, 330, 22))
        + f'<rect x="440" y="140" width="30" height="24" fill="#5c677a"/><rect x="530" y="140" width="30" height="24" fill="#5c677a"/>'
        f'<rect x="510" y="360" width="70" height="210" rx="18" fill="{C["steel2"]}"/>'
        + "".join(f'<line x1="512" y1="{y}" x2="578" y2="{y}" stroke="#5b667a" stroke-width="6"/>' for y in range(390, 560, 18))
        + f'<path d="M520 570 L560 570 L546 598 L534 598 Z" fill="#c9d1de"/>'
        f'<path d="M380 60 Q300 40 250 -10" stroke="#222a39" stroke-width="16" fill="none"/>'
        f"</g>"
        f'<g id="s2-arm">'
        f'<rect x="400" y="110" width="200" height="26" rx="10" fill="#9aa6bb"/>'
        f'<line x1="545" y1="120" x2="{tipx}" y2="{tipy}" stroke="#eef2f7" stroke-width="7" stroke-linecap="round"/>'
        f'<circle cx="545" cy="122" r="12" fill="#eef2f7"/>'
        f"</g>"
        f'<g id="s2-glow"><circle cx="455" cy="245" r="70" fill="{C["blue"]}" opacity="0.25"/><circle cx="545" cy="245" r="70" fill="{C["blue"]}" opacity="0.25"/></g>'
        f"</g>"
    )
    # skin block under the tip
    skin = (
        f'<rect x="100" y="{tipy - 20}" width="880" height="54" rx="10" fill="{C["epi"]}"/>'
        f'<rect x="100" y="{tipy + 34}" width="880" height="150" fill="{C["derm"]}"/>'
        f'<rect x="100" y="{tipy + 184}" width="880" height="10" fill="{C["fat"]}"/>'
    )
    dots = ""
    xs = list(range(330, 760, 26))
    for i, x in enumerate(xs):
        dots += ink_dot(f"s2-d{i}", x, tipy + 70 + (i % 3) * 8, 11)
    svg = skin + f'<g id="s2-dots">{dots}</g>' + mach
    title = "<b>ट्याटु मेसिन</b> कसरी चल्छ?"
    extra = (
        label("s2-chip1", 540, 300, "१ मिनेटमा हजारौं पटक", color="#14213d", bg=C["yellow"], size=46, anchor="center")
        + label("s2-l1", 860, 470, "सुई", size=40, anchor="left")
        + label("s2-l2", 860, 1000, "मसीको थोपा", size=38, anchor="left")
    )
    extra_css = "#s2-l1{left:820px;} #s2-l2{left:770px;top:880px;}"
    js = intro_js(sid)
    # machine glides left->right while needle hammers
    t0, t1 = 0.6, d - 0.6
    js += f'    tl.fromTo("#s2-mach", {{x:-210}}, {{x:220, duration:{fmt(t1 - t0)}, ease:"none"}}, {fmt(t0)});\n'
    js += f'    tl.fromTo("#s2-arm", {{y:0}}, {{y:26, duration:0.05, ease:"sine.inOut", yoyo:true, repeat:{int((t1 - t0) / 0.05) - 1}}}, {fmt(t0)});\n'
    js += f'    tl.fromTo("#s2-glow", {{opacity:0.2}}, {{opacity:1, duration:0.1, yoyo:true, repeat:{int((t1 - t0) / 0.1) - 1}}}, {fmt(t0)});\n'
    for i, x in enumerate(xs):
        # tip x at time t: 540 - 210 + 430*(t-t0)/(t1-t0)
        frac = (x - 330) / 430
        t = t0 + frac * (t1 - t0)
        js += f'    tl.fromTo("#s2-d{i}", {{opacity:0, scale:0, transformOrigin:"50% 50%"}}, {{opacity:1, scale:1, duration:0.18, ease:"back.out(3)"}}, {fmt(t)});\n'
    js += pop("#s2-chip1", 1.6)
    js += f'    tl.fromTo("#s2-l1", {{opacity:0, x:30}}, {{opacity:1, x:0, duration:0.3}}, 1.0);\n'
    js += f'    tl.fromTo("#s2-l2", {{opacity:0, x:30}}, {{opacity:1, x:0, duration:0.3}}, {fmt(11.66 - SCENES[1] + 1.4)});\n'
    return scene_file(sid, d, title, svg, extra, js, extra_css)


# ================= SCENE 3: depth =================
def s3(d):
    sid = "s3"
    x, y, w = 140, 80, 700
    sec = skin_section("s3", x, y, w, 150, 340, 140)
    needle = (
        f'<g id="s3-needle"><rect x="476" y="-420" width="48" height="380" rx="12" fill="{C["steel2"]}"/>'
        f'<path d="M490 -40 L510 -40 L500 0 Z" fill="#c9d1de"/>'
        f'<line x1="500" y1="-60" x2="500" y2="330" stroke="#eef2f7" stroke-width="10" stroke-linecap="round"/></g>'
    )
    R = rr(31)
    ink = "".join(ink_dot(f"s3-i{i}", 500 + R.uniform(-60, 60), 330 + R.uniform(-35, 35), R.uniform(10, 15)) for i in range(9))
    ghost = f'<g id="s3-ghost">{ink_dot("s3-g0", 300, 150, 13)}{ink_dot("s3-g1", 330, 175, 10)}<path d="M270 120 L360 205 M360 120 L270 205" stroke="{C["red"]}" stroke-width="12" stroke-linecap="round"/></g>'
    ruler = (
        f'<g id="s3-ruler"><line x1="105" y1="{y}" x2="105" y2="330" stroke="{C["yellow"]}" stroke-width="8"/>'
        f'<line x1="85" y1="{y}" x2="125" y2="{y}" stroke="{C["yellow"]}" stroke-width="8"/>'
        f'<line x1="85" y1="330" x2="125" y2="330" stroke="{C["yellow"]}" stroke-width="8"/></g>'
    )
    hi = f'<rect id="s3-hi" x="{x - 6}" y="{y + 150}" width="{w + 12}" height="340" fill="none" stroke="{C["yellow"]}" stroke-width="10" rx="8"/>'
    svg = sec + ghost + f'<g id="s3-ink">{ink}</g>' + needle + ruler + hi
    title = "मसी कति <b>गहिरो</b> जान्छ?"
    stage_top = 360
    extra = (
        label("s3-lepi", 860, stage_top + y + 50, "एपिडर्मिस", size=36)
        + label("s3-lderm", 860, stage_top + y + 290, "डर्मिस", color="#14213d", bg=C["yellow"], size=44)
        + label("s3-lfat", 860, stage_top + y + 540, "बोसो तह", size=36)
        + label("s3-lmm", 30, stage_top + 160, "१–२ mm", color="#14213d", bg=C["yellow"], size=40)
    )
    extra_css = "#s3-lepi,#s3-lderm,#s3-lfat{left:850px;} #s3-lmm{left:14px;}"
    js = intro_js(sid)
    js += f'    tl.fromTo("#s3-lepi", {{opacity:0, x:30}}, {{opacity:1, x:0, duration:0.3}}, 0.4);\n'
    js += f'    tl.fromTo("#s3-lfat", {{opacity:0, x:30}}, {{opacity:1, x:0, duration:0.3}}, 0.6);\n'
    js += pop("#s3-ghost", 1.2)
    js += f'    tl.to("#s3-ghost", {{opacity:0.0, duration:0.3}}, 2.7);\n'
    js += f'    tl.fromTo("#s3-needle", {{y:-260, opacity:1}}, {{y:0, duration:0.45, ease:"power3.in"}}, 3.0);\n'
    js += f'    tl.fromTo("#s3-ink circle", {{opacity:0, scale:0, transformOrigin:"50% 50%"}}, {{opacity:1, scale:1, duration:0.25, stagger:0.05, ease:"back.out(3)"}}, 3.4);\n'
    js += f'    tl.to("#s3-needle", {{y:-520, opacity:0, duration:0.5, ease:"power2.in"}}, 4.0);\n'
    js += f'    tl.fromTo("#s3-ruler", {{opacity:0, scaleY:0, transformOrigin:"50% 0%"}}, {{opacity:1, scaleY:1, duration:0.4, ease:"power2.out"}}, 3.2);\n'
    js += pop("#s3-lmm", 3.5)
    js += f'    tl.fromTo("#s3-hi", {{opacity:0}}, {{opacity:1, duration:0.2, yoyo:true, repeat:3}}, {fmt(21.03 - SCENES[2])});\n'
    js += pop("#s3-lderm", 21.03 - SCENES[2])
    return scene_file(sid, d, title, svg, extra, js, extra_css)


# ================= SCENE 4: why top layer can't hold ink =================
def s4(d):
    sid = "s4"
    x, y, w = 90, 120, 900
    sec = skin_section("s4", x, y, w, 210, 300, 110, seed=8)
    R = rr(41)
    top_ink = "".join(ink_dot(f"s4-t{i}", 230 + R.uniform(-60, 60), 230 + R.uniform(-40, 40), 12) for i in range(6))
    deep_ink = "".join(ink_dot(f"s4-b{i}", 760 + R.uniform(-70, 70), 470 + R.uniform(-45, 45), 13) for i in range(8))
    flakes = ""
    for i in range(10):
        fx = x + 40 + i * 88
        flakes += f'<rect id="s4-f{i}" x="{fx}" y="{y - 10}" width="64" height="26" rx="12" fill="#f9d6bb" stroke="{C["epiedge"]}" stroke-width="3"/>'
    divider = f'<line x1="540" y1="{y - 40}" x2="540" y2="{y + 640}" stroke="#ffffff" stroke-width="4" stroke-dasharray="14 14" opacity="0.6"/>'
    check = f'<g id="s4-ok" transform="translate(890 330)"><circle r="48" fill="#22c55e"/><path d="M-22 2 L-6 18 L24 -16" stroke="#fff" stroke-width="12" fill="none" stroke-linecap="round" stroke-linejoin="round"/></g>'
    cross = f'<g id="s4-no" transform="translate(110 330)"><circle r="48" fill="{C["red"]}"/><path d="M-18 -18 L18 18 M18 -18 L-18 18" stroke="#fff" stroke-width="12" stroke-linecap="round"/></g>'
    svg = sec + f'<g id="s4-top">{top_ink}</g><g id="s4-deep">{deep_ink}</g>' + flakes + divider + check + cross
    title = "माथिल्लो तह <b>फेरिइरहन्छ</b>"
    st = 360
    extra = (
        label("s4-cal", 540, st - 10, "हरेक केही हप्तामा नयाँ छाला", color="#14213d", bg=C["yellow"], size=42, anchor="center")
        + label("s4-lt", 270, st + 700, "१ महिनामै गायब!", color="#fff", bg=C["red"], size=40, anchor="center")
        + label("s4-lb", 810, st + 700, "स्थायी ट्याटु", color="#fff", bg="#16a34a", size=40, anchor="center")
    )
    extra_css = "#s4-cal{top:330px;}"
    js = intro_js(sid)
    # flakes peel off the top continuously
    for i in range(10):
        t = 0.6 + (i * 0.37) % 2.2
        js += f'    tl.fromTo("#s4-f{i}", {{y:0, opacity:1, rotation:0, transformOrigin:"50% 50%"}}, {{y:-150, x:{fmt(R.uniform(-40, 40))}, rotation:{fmt(R.uniform(-60, 60))}, opacity:0, duration:2.2, ease:"power1.out", repeat:{int((d - 1.2 - t) / 2.2)}}}, {fmt(t)});\n'
    # cells drift upward slowly (renewal)
    js += f'    tl.fromTo("#s4-cells", {{y:0}}, {{y:-30, duration:{fmt(d - 0.8)}, ease:"none"}}, 0.3);\n'
    js += pop("#s4-cal", 1.2)
    # top ink rides up and leaves
    tgone = 28.95 - SCENES[3]
    js += f'    tl.fromTo("#s4-top circle", {{y:0}}, {{y:-60, duration:{fmt(tgone - 0.5)}, ease:"none"}}, 0.5);\n'
    js += f'    tl.to("#s4-top circle", {{y:-220, opacity:0, duration:0.9, stagger:0.08, ease:"power2.in"}}, {fmt(tgone)});\n'
    js += pop("#s4-no", tgone + 0.3)
    js += pop("#s4-lt", tgone + 0.5)
    js += pop("#s4-ok", 27.7 - SCENES[3])
    js += pop("#s4-lb", 27.7 - SCENES[3] + 0.2)
    js += f'    tl.fromTo("#s4-deep circle", {{scale:1, transformOrigin:"50% 50%"}}, {{scale:1.25, duration:0.25, yoyo:true, repeat:1, stagger:0.04}}, {fmt(27.7 - SCENES[3])});\n'
    return scene_file(sid, d, title, svg, extra, js, extra_css)


# ================= SCENE 5: immune response =================
def s5(d):
    sid = "s5"
    px, py, pw, ph = 60, 20, 960, 740
    panel = dermis_panel("s5-panel", px, py, pw, ph, seed=9)
    wound = (
        f'<g id="s5-wound" transform="translate(540 90)">'
        f'<path d="M0 -50 L14 -14 L52 -18 L22 8 L36 46 L0 24 L-36 46 L-22 8 L-52 -18 L-14 -14 Z" fill="{C["red"]}"/></g>'
        + "".join(f'<circle id="s5-ring{i}" cx="540" cy="90" r="60" fill="none" stroke="{C["red"]}" stroke-width="8"/>' for i in range(3))
    )
    clusters = [(330, 330), (720, 300), (420, 560), (690, 560)]
    R = rr(51)
    ink = ""
    for c, (cx, cy) in enumerate(clusters):
        for j in range(4):
            ink += ink_dot(f"s5-i{c}{j}", cx + R.uniform(-40, 40), cy + R.uniform(-35, 35), R.uniform(11, 16))
    alerts = "".join(
        f'<g id="s5-a{c}" transform="translate({cx} {cy - 80})"><circle r="26" fill="{C["red"]}"/><text x="0" y="13" text-anchor="middle" font-size="40" font-weight="800" fill="#fff" font-family="Mukta">!</text></g>'
        for c, (cx, cy) in enumerate(clusters)
    )
    starts = [(-120, 330), (1200, 260), (-120, 600), (1200, 640)]
    macs = "".join(macrophage(f"s5-m{c}", cx, cy, 78, seed=60 + c) for c, (cx, cy) in enumerate(clusters))
    svg = panel + wound + f'<g id="s5-ink">{ink}</g>' + alerts + macs
    title = "<b>इम्युन सिस्टम</b> सक्रिय!"
    extra = label("s5-lm", 540, 1140 - 60, "म्याक्रोफेज = सेतो रक्तकोष", color="#14213d", bg=C["mac"], size=44, anchor="center")
    extra_css = "#s5-lm{top:1060px;}"
    js = intro_js(sid)
    js += f'    tl.fromTo("#s5-wound", {{scale:0, transformOrigin:"50% 50%"}}, {{scale:1, duration:0.3, ease:"back.out(3)"}}, 0.3);\n'
    for i in range(3):
        js += f'    tl.fromTo("#s5-ring{i}", {{scale:0.4, opacity:0.9, transformOrigin:"50% 50%"}}, {{scale:5, opacity:0, duration:1.4, ease:"power1.out", repeat:2}}, {fmt(0.6 + i * 0.45)});\n'
    tm = 35.45 - SCENES[4]  # macrophage named
    t_eat = 39.6 - SCENES[4]
    for c, (cx, cy) in enumerate(clusters):
        sx, sy = starts[c]
        js += f'    tl.fromTo("#s5-m{c}", {{x:{sx - cx}, y:{sy - cy}}}, {{x:0, y:0, duration:{fmt(t_eat - tm - 0.4)}, ease:"power2.inOut"}}, {fmt(tm + c * 0.15)});\n'
        js += wobble(f"#s5-m{c} .body", tm, d - 0.4, 0.07, 0.5)
        js += pop(f"#s5-a{c}", t_eat - 0.9 + c * 0.1)
        js += f'    tl.to("#s5-a{c}", {{opacity:0, duration:0.2}}, {fmt(t_eat + 0.6)});\n'
        for j in range(4):
            js += f'    tl.to("#s5-i{c}{j}", {{x:{fmt(-0)}, scale:0.7, transformOrigin:"50% 50%", duration:0.6, ease:"power2.in"}}, {fmt(t_eat + j * 0.12)});\n'
    # ink pulled into the cell centre
    js += f'    tl.to("#s5-ink circle", {{opacity:0.95, duration:0.1}}, {fmt(t_eat)});\n'
    js += pop("#s5-lm", tm + 0.3)
    # move ink into macrophages: put macrophage bodies above? draw ink pulled toward centre
    js_pull = ""
    for c, (cx, cy) in enumerate(clusters):
        js_pull += f'    tl.to("#s5-ink circle[id^=\\"s5-i{c}\\"]", {{attr:{{cx:{cx + 10}, cy:{cy + 5}}}, duration:0.7, stagger:0.06, ease:"power2.in"}}, {fmt(t_eat)});\n'
    js += js_pull
    # bring ink to front so it shows inside the cells
    return scene_file(sid, d, title, svg.replace(f'<g id="s5-ink">{ink}</g>', "").replace(macs, macs + f'<g id="s5-ink">{ink}</g>'), extra, js, extra_css)


# ================= SCENE 6: too big to digest =================
def s6(d):
    sid = "s6"
    cx, cy, r = 540, 380, 290
    big = macrophage("s6-m", cx, cy, r, seed=70)
    R = rr(71)
    pos = [(cx + 40, cy - 40), (cx + 130, cy + 60), (cx - 30, cy + 110), (cx + 150, cy - 120), (cx - 60, cy - 10)]
    inks = "".join(ink_dot(f"s6-i{i}", px, py, 34) for i, (px, py) in enumerate(pos))
    enz = ""
    for i in range(10):
        a = i / 10 * 6.28
        enz += f'<circle id="s6-e{i}" cx="{fmt(cx + 0.78 * r * math.cos(a))}" cy="{fmt(cy + 0.7 * r * math.sin(a))}" r="11" fill="{C["yellow"]}"/>'
    xmark = f'<g id="s6-x" transform="translate({cx} {cy})"><path d="M-170 -170 L170 170 M170 -170 L-170 170" stroke="{C["red"]}" stroke-width="40" stroke-linecap="round" opacity="0.9"/></g>'
    lock = (
        f'<g transform="translate({cx + 60} {cy + 10})"><g id="s6-lock">'
        f'<path d="M-46 -20 L-46 -62 A46 46 0 0 1 46 -62 L46 -20" stroke="#e8edf5" stroke-width="20" fill="none"/>'
        f'<rect x="-72" y="-24" width="144" height="118" rx="20" fill="{C["yellow"]}"/>'
        f'<circle cx="0" cy="26" r="16" fill="#14213d"/><rect x="-7" y="30" width="14" height="36" rx="6" fill="#14213d"/></g></g>'
    )
    svg = big + f'<g id="s6-ink">{inks}</g>' + enz + xmark + lock
    title = "मसीका कण <b>धेरै ठूला</b>"
    extra = (
        label("s6-l1", 540, 1070, "पचाउनै सक्दैन!", color="#fff", bg=C["red"], size=50, anchor="center")
        + label("s6-l2", 540, 1070, "मसी भित्रै थुनिन्छ", color="#14213d", bg=C["yellow"], size=50, anchor="center")
    )
    js = intro_js(sid)
    js += wobble("#s6-m .body", 0, d - 0.3, 0.04, 0.8)
    js += f'    tl.fromTo("#s6-ink circle", {{scale:0, transformOrigin:"50% 50%"}}, {{scale:1, duration:0.4, stagger:0.08, ease:"back.out(2.5)"}}, 0.3);\n'
    # enzymes attack and bounce back
    for i in range(10):
        tx, ty = pos[i % 5]
        a = i / 10 * 6.28
        ex, ey = cx + 0.78 * r * math.cos(a), cy + 0.7 * r * math.sin(a)
        js += f'    tl.fromTo("#s6-e{i}", {{x:0, y:0}}, {{x:{fmt((tx - ex) * 0.8)}, y:{fmt((ty - ey) * 0.8)}, duration:0.45, ease:"power2.in", yoyo:true, repeat:3}}, {fmt(0.9 + i * 0.06)});\n'
    js += f'    tl.fromTo("#s6-ink circle", {{x:0}}, {{x:6, duration:0.06, yoyo:true, repeat:11}}, 1.35);\n'
    t_no = 44.44 - SCENES[5]
    t_lock = 46.7 - SCENES[5]
    js += f'    tl.fromTo("#s6-x", {{scale:2.4, opacity:0, transformOrigin:"50% 50%"}}, {{scale:1, opacity:1, duration:0.3, ease:"power4.in"}}, {fmt(t_no + 0.6)});\n'
    js += pop("#s6-l1", t_no + 0.4)
    js += f'    tl.to("#s6-x", {{opacity:0, duration:0.25}}, {fmt(t_lock - 0.2)});\n'
    js += f'    tl.to("#s6-l1", {{opacity:0, duration:0.15}}, {fmt(t_lock - 0.2)});\n'
    js += f'    tl.fromTo("#s6-lock", {{y:-300, opacity:0}}, {{y:0, opacity:1, duration:0.45, ease:"bounce.out"}}, {fmt(t_lock)});\n'
    js += pop("#s6-l2", t_lock + 0.2)
    return scene_file(sid, d, title, svg, extra, js)


# ================= SCENE 7: the cycle =================
def s7(d):
    sid = "s7"
    cx, cy = 540, 400
    a = macrophage("s7-a", cx, cy, 170, seed=80)
    b = macrophage("s7-b", cx, cy, 170, seed=81)
    R = rr(82)
    ink = "".join(ink_dot(f"s7-i{i}", cx + 30 + R.uniform(-70, 70), cy + 20 + R.uniform(-60, 60), 22) for i in range(6))
    frags = "".join(
        f'<circle id="s7-f{i}" cx="{cx}" cy="{cy}" r="{fmt(R.uniform(14, 26))}" fill="#9fb1a8" stroke="#6f8279" stroke-width="3"/>' for i in range(12)
    )
    ring = (
        f'<g id="s7-ring"><circle cx="{cx}" cy="{cy}" r="300" fill="none" stroke="{C["yellow"]}" stroke-width="14" stroke-dasharray="380 90" stroke-linecap="round"/>'
        + "".join(
            f'<path transform="rotate({ang} {cx} {cy})" d="M{cx + 300} {cy - 40} l -26 34 l 52 0 Z" fill="{C["yellow"]}"/>' for ang in (0, 120, 240)
        )
        + "</g>"
    )
    rip = f'<text id="s7-rip" x="{cx}" y="{cy - 210}" text-anchor="middle" font-family="Mukta" font-weight="800" font-size="56" fill="#cbd5e1">कोष मर्यो</text>'
    svg = ring + f'<g id="s7-dead">{a}</g>' + frags + b + f'<g id="s7-ink">{ink}</g>' + rip
    title = "मर्छ… अनि <b>फेरि निलिन्छ</b>"
    extra = label("s7-l", 540, 1070, "यो चक्र जीवनभर", color="#14213d", bg=C["yellow"], size=50, anchor="center")
    js = intro_js(sid)
    js += wobble("#s7-a .body", 0, 2.0, 0.05, 0.6)
    t_die = 50.6 - SCENES[6]
    js += f'    tl.to("#s7-a", {{opacity:0.0, scale:1.15, transformOrigin:"50% 50%", duration:0.35, ease:"power2.in"}}, {fmt(t_die)});\n'
    for i in range(12):
        ang = i / 12 * 6.28
        js += f'    tl.fromTo("#s7-f{i}", {{opacity:0, x:0, y:0}}, {{opacity:1, x:{fmt(260 * math.cos(ang))}, y:{fmt(240 * math.sin(ang))}, duration:0.8, ease:"power3.out"}}, {fmt(t_die + 0.1)});\n'
        js += f'    tl.to("#s7-f{i}", {{opacity:0, duration:0.5}}, {fmt(t_die + 0.9)});\n'
    js += pop("#s7-rip", t_die + 0.1)
    js += f'    tl.to("#s7-rip", {{opacity:0, duration:0.3}}, {fmt(t_die + 1.4)});\n'
    js += f'    tl.fromTo("#s7-ink circle", {{x:0, y:0}}, {{x:"random(-40,40)", y:"random(-30,30)", duration:1.2, ease:"sine.inOut"}}, {fmt(t_die + 0.1)});\n'
    t_new = 51.8 - SCENES[6]
    js += f'    tl.fromTo("#s7-b", {{x:900, opacity:1}}, {{x:0, duration:1.6, ease:"power3.out"}}, {fmt(t_new + 0.3)});\n'
    js += f'    tl.set("#s7-b", {{x:900}}, 0);\n'
    js += f'    tl.to("#s7-ink circle", {{x:0, y:0, duration:0.6, ease:"power2.in"}}, {fmt(t_new + 2.2)});\n'
    js += wobble("#s7-b .body", t_new + 1.9, d - 0.3, 0.05, 0.6)
    t_cyc = 55.5 - SCENES[6]
    js += f'    tl.fromTo("#s7-ring", {{opacity:0, rotation:-90, transformOrigin:"540px 400px"}}, {{opacity:1, rotation:0, duration:0.6, ease:"power3.out"}}, {fmt(t_cyc - 0.2)});\n'
    js += f'    tl.to("#s7-ring", {{rotation:200, duration:{fmt(d - t_cyc - 0.4)}, ease:"none"}}, {fmt(t_cyc + 0.4)});\n'
    js += pop("#s7-l", t_cyc)
    return scene_file(sid, d, title, svg, extra, js).replace('x:"random(-40,40)", y:"random(-30,30)"', 'x:30, y:-20')


# ================= SCENE 8: zoom out to the tattoo =================
def s8(d):
    sid = "s8"
    # heart made of ink-filled cells on an arm
    pts = []
    for k in range(64):
        t = k / 64 * 2 * math.pi
        hx = 16 * math.sin(t) ** 3
        hy = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((540 + hx * 15, 400 + hy * 15))
    # fill a few inner rows too
    inner = []
    for s in (0.75, 0.5):
        for k in range(0, 64, 2):
            t = k / 64 * 2 * math.pi
            hx = 16 * math.sin(t) ** 3
            hy = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
            inner.append((540 + hx * 15 * s, 400 + hy * 15 * s + 15 * (1 - s)))
    cells = "".join(
        f'<g><circle cx="{fmt(x)}" cy="{fmt(y)}" r="13" fill="{C["mac"]}" stroke="{C["macedge"]}" stroke-width="2"/><circle cx="{fmt(x + 2)}" cy="{fmt(y + 2)}" r="7" fill="{C["ink"]}"/></g>'
        for (x, y) in pts + inner
    )
    arm = (
        f'<rect x="-200" y="120" width="1480" height="560" rx="280" fill="#e8b18c"/>'
        f'<rect x="-200" y="120" width="1480" height="150" rx="75" fill="#f2c5a3" opacity="0.6"/>'
    )
    shield = f'<path id="s8-shield" d="M540 120 C 760 120, 860 220, 860 380 C 860 560, 700 660, 540 720 C 380 660, 220 560, 220 380 C 220 220, 320 120, 540 120 Z" fill="none" stroke="{C["blue"]}" stroke-width="10" stroke-dasharray="26 18"/>'
    blocked = "".join(
        f'<g id="s8-b{i}" transform="translate({bx} {by})"><path d="M0 0 L{dx} {dy}" stroke="{C["red"]}" stroke-width="10" stroke-linecap="round"/><path d="M{dx * 0.4 - 16} {dy * 0.4 - 16} l32 32 m0 -32 l-32 32" stroke="#fff" stroke-width="8" stroke-linecap="round"/></g>'
        for i, (bx, by, dx, dy) in enumerate([(870, 300, 110, -40), (210, 300, -110, -40), (790, 620, 100, 70), (290, 620, -100, 70)])
    )
    svg = (f'<defs><clipPath id="s8-clip"><rect x="40" y="0" width="1000" height="780" rx="48"/></clipPath></defs>'
           f'<rect x="40" y="0" width="1000" height="780" rx="48" fill="#111737"/>'
           f'<g clip-path="url(#s8-clip)"><g id="s8-world">{arm}<g id="s8-heart">{cells}</g></g></g>' + shield + blocked)
    title = "इम्युन सिस्टमले <b>थुनेर</b> राख्छ"
    extra = label("s8-l", 540, 1070, "थुनिएको मसी = तपाईंको ट्याटु", color="#14213d", bg=C["yellow"], size=48, anchor="center")
    js = intro_js(sid)
    js += f'    tl.fromTo("#s8-world", {{scale:6, transformOrigin:"{fmt(pts[8][0])}px {fmt(pts[8][1])}px"}}, {{scale:1, duration:3.2, ease:"power2.inOut"}}, 0.1);\n'
    t_shield = 62.05 - SCENES[7]
    js += f'    tl.fromTo("#s8-shield", {{opacity:0, scale:0.8, transformOrigin:"540px 420px"}}, {{opacity:1, scale:1, duration:0.5, ease:"back.out(2)"}}, {fmt(t_shield - 0.6)});\n'
    for i in range(4):
        js += pop(f"#s8-b{i}", t_shield + i * 0.12)
        js += f'    tl.to("#s8-b{i}", {{opacity:0, duration:0.3}}, {fmt(63.9 - SCENES[7] + 0.2)});\n'
    js += f'    tl.fromTo("#s8-heart", {{scale:1, transformOrigin:"540px 400px"}}, {{scale:1.08, duration:0.3, yoyo:true, repeat:5, ease:"sine.inOut"}}, {fmt(64.5 - SCENES[7])});\n'
    js += pop("#s8-l", 64.0 - SCENES[7])
    js += f'    tl.to("#s8-title", {{opacity:0, duration:0.2}}, {fmt(63.9 - SCENES[7])});\n'
    js += f'    tl.fromTo("#s8-title2", {{opacity:0, y:-20}}, {{opacity:1, y:0, duration:0.3}}, {fmt(64.0 - SCENES[7])});\n'
    extra += '<div id="s8-title2" class="title" style="opacity:0">यही हो तपाईंको <b>ट्याटु!</b></div>'
    return scene_file(sid, d, title, svg, extra, js)


# ================= SCENE 9: laser =================
def s9(d):
    sid = "s9"
    panel = dermis_panel("s9-panel", 60, 120, 960, 640, seed=91)
    device = (
        f'<g id="s9-dev"><rect x="430" y="-40" width="220" height="110" rx="24" fill="#2b3245"/>'
        f'<rect x="505" y="70" width="70" height="40" rx="8" fill="#5c677a"/><circle cx="470" cy="15" r="12" fill="{C["red"]}"/></g>'
    )
    beam = f'<rect id="s9-beam" x="522" y="110" width="36" height="330" fill="{C["red"]}" opacity="0.85"/><rect id="s9-core" x="533" y="110" width="14" height="330" fill="#fff"/>'
    flash = f'<circle id="s9-flash" cx="540" cy="450" r="140" fill="#fff"/>'
    R = rr(92)
    bigs = [(470, 430), (600, 420), (540, 510), (430, 520), (650, 520)]
    big = "".join(ink_dot(f"s9-b{i}", x, y, 36) for i, (x, y) in enumerate(bigs))
    tiny = ""
    for i in range(40):
        bx, by = bigs[i % 5]
        tiny += f'<circle id="s9-t{i}" cx="{fmt(bx + R.uniform(-25, 25))}" cy="{fmt(by + R.uniform(-25, 25))}" r="{fmt(R.uniform(4, 8))}" fill="{C["ink"]}"/>'
    lymph = f'<path id="s9-lymph" d="M1000 560 C 880 600, 840 700, 720 740" stroke="#7dd3a8" stroke-width="40" fill="none" stroke-linecap="round" opacity="0.8"/>'
    svg = panel + lymph + f'<g id="s9-big">{big}</g><g id="s9-tiny">{tiny}</g>' + beam + flash + device
    title = "<b>लेजरले</b> कसरी मेटाउँछ?"
    extra = (
        label("s9-l1", 540, 1070, "टुक्रा-टुक्रा!", color="#fff", bg=C["red"], size=50, anchor="center")
        + label("s9-l2", 540, 1070, "शरीरले बिस्तारै सफा गर्छ", color="#14213d", bg=C["mac"], size=46, anchor="center")
    )
    js = intro_js(sid)
    js += f'    tl.set("#s9-tiny circle", {{opacity:0}}, 0);\n'
    js += f'    tl.set("#s9-flash", {{opacity:0}}, 0);\n'
    js += f'    tl.fromTo("#s9-beam, #s9-core", {{scaleY:0, transformOrigin:"50% 0%"}}, {{scaleY:1, duration:0.2, ease:"power4.in"}}, 0.6);\n'
    js += f'    tl.fromTo("#s9-beam", {{opacity:0.85}}, {{opacity:0.4, duration:0.07, yoyo:true, repeat:15}}, 0.8);\n'
    js += f'    tl.fromTo("#s9-flash", {{opacity:0, scale:0.3, transformOrigin:"50% 50%"}}, {{opacity:0.9, scale:1.4, duration:0.15, ease:"power2.out"}}, 1.6);\n'
    js += f'    tl.to("#s9-flash", {{opacity:0, duration:0.4}}, 1.75);\n'
    js += f'    tl.to("#s9-big circle", {{opacity:0, scale:0.5, transformOrigin:"50% 50%", duration:0.15}}, 1.65);\n'
    js += f'    tl.set("#s9-tiny circle", {{opacity:1}}, 1.65);\n'
    for i in range(40):
        a = R.uniform(0, 6.28)
        js += f'    tl.fromTo("#s9-t{i}", {{x:0, y:0}}, {{x:{fmt(math.cos(a) * R.uniform(60, 140))}, y:{fmt(math.sin(a) * R.uniform(60, 140))}, duration:0.6, ease:"power3.out"}}, 1.65);\n'
        js += f'    tl.to("#s9-t{i}", {{x:{fmt(R.uniform(330, 470))}, y:{fmt(R.uniform(200, 330))}, opacity:0, duration:2.0, ease:"power1.in"}}, {fmt(2.8 + (i % 10) * 0.08)});\n'
    js += f'    tl.to("#s9-beam, #s9-core", {{opacity:0, duration:0.2}}, 2.1);\n'
    js += pop("#s9-l1", 1.7)
    js += f'    tl.to("#s9-l1", {{opacity:0, duration:0.15}}, {fmt(70.4 - SCENES[8])});\n'
    js += pop("#s9-l2", 70.5 - SCENES[8])
    return scene_file(sid, d, title, svg, extra, js)


# ================= SCENE 10: CTA =================
def s10(d):
    sid = "s10"
    mascot = macrophage("s10-m", 540, 200, 140, ink=4, seed=100, eyes=True)
    share = (
        f'<g id="s10-share" transform="translate(540 440)"><rect x="-330" y="-62" width="660" height="124" rx="62" fill="#ffffff"/>'
        f'<g transform="translate(-250 0)"><circle cx="-18" cy="0" r="14" fill="#14213d"/><circle cx="22" cy="-26" r="14" fill="#14213d"/><circle cx="22" cy="26" r="14" fill="#14213d"/>'
        f'<path d="M-18 0 L22 -26 M-18 0 L22 26" stroke="#14213d" stroke-width="7"/></g>'
        f'<text x="30" y="18" text-anchor="middle" font-family="Mukta" font-weight="800" font-size="52" fill="#14213d">सेयर गर्नुहोस्</text></g>'
    )
    follow = (
        f'<g id="s10-follow" transform="translate(540 600)"><rect x="-330" y="-62" width="660" height="124" rx="62" fill="{C["red"]}"/>'
        f'<path d="M-260 0 h44 M-238 -22 v44" stroke="#fff" stroke-width="12" stroke-linecap="round"/>'
        f'<text x="30" y="18" text-anchor="middle" font-family="Mukta" font-weight="800" font-size="52" fill="#fff">फलो गर्नुहोस्</text></g>'
    )
    hand = f'<g transform="translate(800 640)"><g id="s10-tap"><circle r="34" fill="#ffffff" opacity="0.9"/><circle r="56" fill="none" stroke="#fff" stroke-width="6" opacity="0.6"/></g></g>'
    svg = mascot + share + follow + hand
    title = "<b>अचम्म</b> लाग्यो?"
    extra_css = "#s10-title{font-size:104px;top:190px;}"
    extra = label("s10-tag", 540, 1060, "ट्याटु भएको साथीलाई ट्याग गर्नुहोस्", color="#14213d", bg=C["yellow"], size=40, anchor="center")
    js = intro_js(sid)
    js += f'    tl.fromTo("#s10-m", {{y:0}}, {{y:-30, duration:0.35, ease:"sine.inOut", yoyo:true, repeat:{int((d - 0.8) / 0.35) - 1}}}, 0.3);\n'
    js += wobble("#s10-m .body", 0.2, d - 0.3, 0.05, 0.5)
    js += pop("#s10-share", 1.3)
    js += pop("#s10-tag", 2.0)
    js += f'    tl.to("#s10-share", {{scale:1.06, duration:0.25, yoyo:true, repeat:5, transformOrigin:"50% 50%"}}, 2.6);\n'
    t_f = 77.3 - SCENES[9]
    js += pop("#s10-follow", t_f)
    js += f'    tl.fromTo("#s10-tap", {{opacity:0, x:120, y:120}}, {{opacity:1, x:0, y:0, duration:0.5, ease:"power3.out"}}, {fmt(t_f + 1.6)});\n'
    js += f'    tl.to("#s10-follow", {{scale:0.92, duration:0.12, yoyo:true, repeat:1, transformOrigin:"50% 50%"}}, {fmt(t_f + 2.1)});\n'
    js += f'    tl.to("#s10-follow", {{scale:1.06, duration:0.3, yoyo:true, repeat:{int((d - t_f - 3.0) / 0.3) - 1}, transformOrigin:"50% 50%"}}, {fmt(t_f + 2.5)});\n'
    return scene_file(sid, d, title, svg, extra, js, extra_css)


# ================= captions =================
def caption_groups():
    groups = []
    for text, s, e in CLAUSES:
        words = text.split()
        # chunk into groups of <= 4 words and <= 20 letters
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
        total = sum(len(" ".join(c)) for c in chunks)
        t = s
        for c in chunks:
            frac = len(" ".join(c)) / total
            gd = (e - s) * frac
            groups.append((c, t, t + gd))
            t += gd
    return groups


def captions(total):
    groups = caption_groups()
    html, js = "", ""
    for gi, (words, s, e) in enumerate(groups):
        spans = ""
        for w_ in words:
            hot = any(k in w_ for k in KEYWORDS)
            spans += f'<span class="w{" hot" if hot else ""}">{w_}</span> '
        html += f'      <div id="cg{gi}" class="cg"><div class="cg-in">{spans.strip()}</div></div>\n'
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


def index(total):
    hosts = ""
    for i, (s, dd) in enumerate(zip(SCENES, DUR)):
        sid = f"s{i + 1}"
        hosts += f'      <div id="{sid}" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html" data-start="{fmt(s)}" data-duration="{fmt(dd)}" data-track-index="1" data-track-kind="graphics" data-width="{W}" data-height="{H}"></div>\n'
    return f"""<!doctype html>
<html lang="ne">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="vendor/gsap.min.js"></script>
    <style>
{FONT_FACE}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: {W}px; height: {H}px; overflow: hidden; background: #070a1a; font-family: 'Mukta', sans-serif; }}
      #bg {{ position: absolute; inset: 0; background: radial-gradient(circle at 15% 20%, rgba(124,108,255,.35) 0 6px, transparent 7px), radial-gradient(circle at 85% 30%, rgba(124,108,255,.3) 0 9px, transparent 10px), radial-gradient(circle at 75% 80%, rgba(90,209,255,.25) 0 7px, transparent 8px), radial-gradient(circle at 20% 75%, rgba(90,209,255,.25) 0 10px, transparent 11px), radial-gradient(120% 70% at 50% 35%, #1b2156 0%, #0b0f2a 55%, #050714 100%); }}
      #bg-motes {{ position: absolute; inset: 0; }}
      .mote {{ position: absolute; border-radius: 50%; background: #7c6cff; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{fmt(total)}" data-width="{W}" data-height="{H}" data-fps="30">
      <div id="bg" class="clip" data-start="0" data-duration="{fmt(total)}" data-track-index="0" data-layout-ignore></div>
{hosts}      <div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="{fmt(total)}" data-track-index="2" data-track-kind="captions" data-width="{W}" data-height="{H}"></div>
      <audio id="voice" class="clip" src="assets/audio/voice-sarita.mp3" data-start="0" data-duration="80.77" data-track-index="3" data-volume="1"></audio>
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""


if __name__ == "__main__":
    os.makedirs(f"{OUT}/compositions", exist_ok=True)
    fns = [s1, s2, s3, s4, s5, s6, s7, s8, s9, s10]
    for i, fn in enumerate(fns):
        with open(f"{OUT}/compositions/s{i + 1}.html", "w") as f:
            f.write(fn(DUR[i]))
    with open(f"{OUT}/compositions/captions.html", "w") as f:
        f.write(captions(TOTAL))
    with open(f"{OUT}/index.html", "w") as f:
        f.write(index(TOTAL))
    print("ok", [round(x, 2) for x in DUR])
