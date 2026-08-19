"""
generate_svgs.py - Generate animated SVGs for Dheepak's GitHub profile
Creates: github-contribution-animation.svg, terminal-card.svg, info-card.svg
"""
import random, os, html as _html
from urllib.request import urlopen, Request
from io import BytesIO

random.seed(42)

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
USERNAME = "dheepak6381-bit"
DISPLAY_NAME = "S. Dheepak"
ROLE = "Embedded Systems & Edge AI Engineer"

def xe(s): return _html.escape(str(s), quote=True)

# ═══════════════════════════════════════════════════════════════
# 1. github-contribution-animation.svg
# ═══════════════════════════════════════════════════════════════
COLORS = ["#161b22","#0e4429","#006d32","#26a641","#39d353"]
GLOW   = ["#21262d","#3dffa0","#57ffb0","#8dffcc","#c8ffe8"]

def pick_level():
    r = random.random()
    if r < 0.35: return 0
    if r < 0.55: return 1
    if r < 0.72: return 2
    if r < 0.87: return 3
    return 4

WEEKS, DAYS, SQ, GAP = 53, 7, 11, 3
STEP = SQ + GAP
GRAPH_X, GRAPH_Y = 34, 28
MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

def build_contrib():
    W, H = 850, 165
    lines = []
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
    lines.append('<defs>')
    lines.append(
        '<filter id="cellglow" x="-70%" y="-70%" width="240%" height="240%">'
        '<feGaussianBlur stdDeviation="2" result="blur"/>'
        '<feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>'
        '</filter>'
    )
    lines.append('</defs>')
    lines.append(f'<rect width="{W}" height="{H}" rx="16" fill="#0d1117" stroke="#30363d" stroke-width="1"/>')

    wpm = WEEKS / 12
    for i, m in enumerate(MONTHS):
        x = GRAPH_X + round(i * wpm) * STEP
        lines.append(f'<text x="{x}" y="18" fill="#8b949e" font-size="10" font-family="system-ui,sans-serif">{m}</text>')

    for i, lbl in enumerate(["Mon","","Wed","","Fri","",""]):
        if lbl:
            y = GRAPH_Y + i * STEP + SQ - 1
            lines.append(f'<text x="0" y="{y}" fill="#8b949e" font-size="9" font-family="system-ui,sans-serif">{lbl}</text>')

    anim_dur, pause = 4.5, 2.5
    total = anim_dur + pause
    SLANT = 0.6
    max_diag = (WEEKS - 1) + (DAYS - 1) * SLANT

    for col in range(WEEKS):
        for row in range(DAYS):
            lvl = pick_level()
            color, glow = COLORS[lvl], GLOW[lvl]
            x = GRAPH_X + col * STEP
            y = GRAPH_Y + row * STEP
            sq_id = f"s{col}_{row}"
            diag = col + row * SLANT
            t_rev = diag / max_diag * anim_dur
            t0 = t_rev / total
            t1 = min(t0 + 0.012, 0.97)
            t2 = min(t0 + 0.05, 0.99)
            fa = ' filter="url(#cellglow)"' if lvl >= 3 else ''
            lines.append(f'<rect id="{sq_id}" x="{x}" y="{y}" width="{SQ}" height="{SQ}" rx="2" fill="{color}" opacity="0"{fa}>')
            lines.append(f'<animate attributeName="opacity" values="0;0;1;1" keyTimes="0;{t0:.4f};{t1:.4f};1" dur="{total}s" repeatCount="indefinite"/>')
            if lvl > 0:
                lines.append(f'<animate attributeName="fill" values="{color};{color};{glow};{color}" keyTimes="0;{t0:.4f};{t1:.4f};{t2:.4f}" dur="{total}s" repeatCount="indefinite" calcMode="spline" keySplines="0 0 1 1;0 0 1 1;.4 0 .2 1"/>')
            lines.append('</rect>')

    lines.append('</svg>')
    path = os.path.join(OUT_DIR, "github-contribution-animation.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[OK] {path}")

# ═══════════════════════════════════════════════════════════════
# 2. terminal-card.svg (ASCII art portrait from GitHub avatar)
# ═══════════════════════════════════════════════════════════════
def build_terminal():
    print("[..] Fetching GitHub avatar ...")
    try:
        req = Request(
            f"https://avatars.githubusercontent.com/{USERNAME}?size=400",
            headers={"User-Agent": "Mozilla/5.0"},
        )
        img_bytes = urlopen(req, timeout=20).read()
        print(f"[OK] Avatar fetched ({len(img_bytes):,} bytes)")
    except Exception as e:
        print(f"[WARN] Avatar fetch failed: {e}, generating placeholder")
        img_bytes = None

    try:
        from PIL import Image
    except ImportError:
        print("[WARN] Pillow not installed, skipping terminal card")
        return

    ASCII_CHARS = "  `.-':=+*csS%#@"
    ART_W, ART_H = 100, 53

    if img_bytes:
        img = Image.open(BytesIO(img_bytes)).convert("L")
        img = img.resize((ART_W, ART_H), Image.LANCZOS)
        pixels = list(img.getdata())
    else:
        pixels = [random.randint(0, 255) for _ in range(ART_W * ART_H)]

    rows = []
    for r in range(ART_H):
        row = ""
        for c in range(ART_W):
            px = pixels[r * ART_W + c]
            idx = int((255 - px) / 255 * (len(ASCII_CHARS) - 1))
            row += ASCII_CHARS[idx]
        rows.append(row)

    W1, ROW_H, ROW_Y0, FONT_SZ = 840, 15, 37, 12.9
    ROW_DUR = 0.11
    TEXT_W, TEXT_X = 800, 20
    FOOTER_LINE_Y = ROW_Y0 + ART_H * ROW_H
    FOOTER_TEXT_Y = FOOTER_LINE_Y + 19
    H1 = FOOTER_LINE_Y + 43

    rows_svg = ""
    for i, row in enumerate(rows):
        begin = i * ROW_DUR
        y_top = ROW_Y0 + i * ROW_H
        y_text = y_top + 11.1
        safe = xe(row)
        rows_svg += (
            f'<clipPath id="r{i}"><rect x="{TEXT_X}" y="{y_top:.1f}" height="{ROW_H}" width="0">'
            f'<animate attributeName="width" from="0" to="{TEXT_W}" begin="{begin:.3f}s" dur="{ROW_DUR}s" fill="freeze"/>'
            f'</rect></clipPath>\n'
            f'<g clip-path="url(#r{i})">'
            f'<text xml:space="preserve" x="{TEXT_X}" y="{y_text:.1f}" fill="#c9d1d9" font-size="{FONT_SZ}" '
            f'textLength="{TEXT_W}" lengthAdjust="spacing">{safe}</text></g>\n'
            f'<rect y="{y_top+1:.1f}" width="8" height="13" fill="#c9d1d9" opacity="0">'
            f'<animate attributeName="x" from="{TEXT_X}" to="{TEXT_X+TEXT_W}" begin="{begin:.3f}s" dur="{ROW_DUR}s" fill="freeze"/>'
            f'<set attributeName="opacity" to="0.85" begin="{begin:.3f}s"/>'
            f'<set attributeName="opacity" to="0" begin="{begin+ROW_DUR:.3f}s"/>'
            f'</rect>\n'
        )

    WHOAMI_TEXT = f"{USERNAME}@github:~$ whoami "
    CURSOR_X = TEXT_X + len(WHOAMI_TEXT) * 7.73

    svg1 = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W1}" height="{H1}" viewBox="0 0 {W1} {H1}">
<defs><style>@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&amp;display=swap');
text, tspan {{ font-family:'Fira Code',monospace; }}</style></defs>
<rect width="{W1}" height="{H1}" rx="12" fill="#0d1117" stroke="#30363d" stroke-width="1"/>
<circle cx="16" cy="14" r="6" fill="#ff5f57"/><circle cx="34" cy="14" r="6" fill="#febc2e"/><circle cx="52" cy="14" r="6" fill="#28c840"/>
<text x="80" y="18" fill="#8b949e" font-size="12">{xe(USERNAME)}@github: ~$ ./portrait.sh</text>
{rows_svg}
<line x1="0" y1="{FOOTER_LINE_Y}" x2="{W1}" y2="{FOOTER_LINE_Y}" stroke="#30363d"/>
<text x="{TEXT_X}" y="{FOOTER_TEXT_Y}" fill="#8b949e" font-size="13">{xe(WHOAMI_TEXT)}</text>
<text x="{CURSOR_X}" y="{FOOTER_TEXT_Y}" fill="#58a6ff" font-size="13" font-weight="700">{xe(DISPLAY_NAME)}</text>
<rect x="{CURSOR_X + len(DISPLAY_NAME)*7.8}" y="{FOOTER_TEXT_Y - 11}" width="9" height="15" fill="#c9d1d9">
<animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></rect>
</svg>'''

    path = os.path.join(OUT_DIR, "terminal-card.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg1)
    print(f"[OK] {path}")

# ═══════════════════════════════════════════════════════════════
# 3. info-card.svg (neofetch-style info panel)
# ═══════════════════════════════════════════════════════════════
def build_info():
    W2, H2 = 500, 460
    info_rows = [
        ("", f"\\033[1;36m{USERNAME}\\033[0m@\\033[1;36mgithub\\033[0m", True),
        ("", "─" * 35, False),
        ("🎓", "B.Tech ECE • Kalasalingam (9.02)", False),
        ("💡", "Indian Patent Holder (PyroSentinel)", False),
        ("📝", "IEEE Published Author", False),
        ("🏆", "PR Lead @ ACM SIGBED", False),
        ("", "", False),
        ("", "── Stack ──────────────────", False),
        ("⚙️", "STM32 · ESP32 · Embedded C · C++", False),
        ("🧠", "Python · OpenCV · Edge AI", False),
        ("🌐", "LoRa Mesh · Fog Computing · IoT", False),
        ("🔧", "MATLAB · KiCad · Proteus", False),
        ("", "", False),
        ("", "── Highlights ─────────────", False),
        ("🏅", "EduAIThon · ELECTROTHON · Nanochip", False),
        ("🎯", "AICTE IIC – YUKTI Shortlisted", False),
        ("🔬", "8+ Hardware & IoT Projects", False),
    ]

    ROW_H, Y0, X_ICON, X_TEXT = 22, 40, 20, 48
    FONT_SZ = 13

    rows_svg = ""
    for i, (icon, text, is_header) in enumerate(info_rows):
        y = Y0 + i * ROW_H
        delay = 0.08 * i

        # Parse terminal color codes for header
        if is_header:
            text_render = f'<tspan fill="#58a6ff" font-weight="700">{xe(USERNAME)}</tspan><tspan fill="#8b949e">@</tspan><tspan fill="#58a6ff" font-weight="700">github</tspan>'
        else:
            text_render = xe(text)

        fill = "#58a6ff" if "──" in text else "#c9d1d9"
        fw = ' font-weight="700"' if is_header or "──" in text else ""

        rows_svg += f'''<g opacity="0" transform="translate(0, 12)">
<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" dur="0.4s" fill="freeze"/>
<animateTransform attributeName="transform" type="translate" from="0 12" to="0 0" begin="{delay:.2f}s" dur="0.4s" fill="freeze"/>
'''
        if icon:
            rows_svg += f'<text x="{X_ICON}" y="{y}" font-size="{FONT_SZ}">{icon}</text>\n'
        if is_header:
            rows_svg += f'<text x="{X_TEXT}" y="{y}" font-size="{FONT_SZ}">{text_render}</text>\n'
        else:
            rows_svg += f'<text x="{X_TEXT if icon else X_ICON}" y="{y}" fill="{fill}" font-size="{FONT_SZ}"{fw}>{text_render}</text>\n'
        rows_svg += '</g>\n'

    svg2 = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W2}" height="{H2}" viewBox="0 0 {W2} {H2}">
<defs><style>@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&amp;display=swap');
text, tspan {{ font-family:'Fira Code',monospace; }}</style></defs>
<rect width="{W2}" height="{H2}" rx="12" fill="#0d1117" stroke="#30363d" stroke-width="1"/>
<circle cx="16" cy="14" r="6" fill="#ff5f57"/><circle cx="34" cy="14" r="6" fill="#febc2e"/><circle cx="52" cy="14" r="6" fill="#28c840"/>
<text x="80" y="18" fill="#8b949e" font-size="12">{xe(USERNAME)}@github: ~$ neofetch</text>
{rows_svg}
</svg>'''

    path = os.path.join(OUT_DIR, "info-card.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg2)
    print(f"[OK] {path}")

# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    build_contrib()
    build_terminal()
    build_info()
    print("\n[DONE] All SVGs generated.")
