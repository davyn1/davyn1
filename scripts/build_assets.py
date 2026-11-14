"""Build the retro RPG profile SVGs into ../assets.

Usage (from the repo root):  python scripts/build_assets.py

Every SVG is self-contained: pixel text is drawn as squares by pixfont.py
(GitHub can't load web fonts inside an <img>), animation is CSS keyframes
inside the SVG, and every animation is switched off for viewers who ask for
reduced motion. Each image is a framed dark "screen", so one file works on
both GitHub's light and dark themes.

Edit the data blocks below (CHARACTER, SKILLS, ACHIEVEMENTS, QUESTS) and rerun.
"""
import random
from pathlib import Path

from pixfont import glyph_paths, text_path, text_width

OUT = Path(__file__).resolve().parent.parent / "assets"

# ---- palette -------------------------------------------------------------
NAVY, NAVY_DEEP = "#0b1030", "#070a22"
GREEN, MAGENTA, CYAN, GOLD = "#3dff8a", "#ff3df2", "#2de2ff", "#ffd23d"
PALE, MUTED, DIM = "#d6dcff", "#8f99d9", "#39427a"

# ---- content ---------------------------------------------------------------
CHARACTER = [  # (label, value) rows on the character sheet
    ("CLASS", "SYSADMIN TECHNICIAN"),
    ("GUILD", "COUNTY OF SANTA CLARA"),
    ("ORIGIN", "UC IRVINE B.S. 2023"),
    ("LEVEL", "04"),
    ("BASE", "BAY AREA, CA"),
    ("WEAPON", "PYTHON"),
    ("QUEST", "AWS SOLUTIONS ARCH."),
]

SKILLS = [  # (group, colour, [(skill, level out of 10)])
    ("LANGUAGES", GREEN, [("PYTHON", 8), ("TYPESCRIPT", 5), ("SQL", 6)]),
    ("BACKEND", CYAN, [("FASTAPI", 8), ("SQLALCHEMY", 6), ("HTMX", 4)]),
    ("CLOUD", MAGENTA, [("AWS", 6), ("DOCKER", 6), ("FLY.IO", 5)]),
    ("TOOLS", GOLD, [("GIT", 7), ("LINUX", 6), ("PYTEST", 7), ("ACTIONS", 5)]),
]

ACHIEVEMENTS = [  # (lines, icon, unlocked, status)
    (["AWS", "CLOUD", "PRACTITIONER"], "trophy", True, "★ UNLOCKED"),
    (["GOOGLE", "CYBERSECURITY", "PROFESSIONAL"], "shield", True, "★ UNLOCKED"),
    (["AWS", "SOLUTIONS", "ARCHITECT"], "lock", False, "DEC 2026"),
]

QUESTS = [  # (file slug, number label, title, icon, status, status colour)
    ("trading-bot", "QUEST 01", "TRADING BOT", "bot", "★ CLEARED", GREEN),
    ("stock-analysis", "QUEST 02", "STOCK ANALYSIS", "chart", "★ CLEARED", GREEN),
    ("yums-map", "QUEST 03", "BAY AREA YUMS MAP", "pin", "★ LIVE", CYAN),
    ("flashcards", "QUEST 04", "KOREAN FLASHCARDS", "card", "★ LIVE", CYAN),
    ("morning-dashboard", "QUEST 05", "MORNING DASHBOARD", "sun", "PRIVATE", MUTED),
    ("side-quests", "SIDE", "SIDE QUESTS", "gear", "IN PROGRESS", MAGENTA),
]

# ---- 8x8 pixel icons -------------------------------------------------------
ICONS = {
    "trophy": ["01111110", "11111111", "11111111", "01111110", "00111100", "00011000", "00111100", "01111110"],
    "shield": ["11111111", "11111111", "11100111", "11000011", "11100111", "01111110", "00111100", "00011000"],
    "lock":   ["00111100", "01000010", "01000010", "11111111", "11100111", "11100111", "11111111", "11111111"],
    "bot":    ["00011000", "01111110", "11011011", "11111111", "10111101", "11111111", "01100110", "01100110"],
    "chart":  ["00000011", "00000111", "00001110", "10011100", "11111000", "01110000", "00100000", "11111111"],
    "pin":    ["00111100", "01111110", "11100111", "11100111", "01111110", "00111100", "00011000", "00011000"],
    "card":   ["11111100", "10000100", "10111111", "10100001", "11101101", "00100001", "00100001", "00111111"],
    "sun":    ["10011001", "01000010", "00111100", "10111101", "10111101", "00111100", "01000010", "10011001"],
    "gear":   ["00011000", "01111110", "01100110", "11000011", "11000011", "01100110", "01111110", "00011000"],
    "coin":   ["00111100", "01111110", "11100111", "11101111", "11101111", "11100111", "01111110", "00111100"],
}

# 12x16 generic pixel adventurer for the character sheet (not a likeness).
SPRITE = [
    "....hhhh....",
    "...hhhhhh...",
    "..hhhhhhhh..",
    "..hssssssh..",
    "..ssksskss..",
    "..ssssssss..",
    "...ssmmss...",
    "....ssss....",
    "..gggggggg..",
    ".gggggggggg.",
    "sggggggggggs",
    "sggggggggggs",
    "..gggggggg..",
    "..bbb..bbb..",
    "..bbb..bbb..",
    "..kkk..kkk..",
]
SPRITE_COLOURS = {"h": "#3a2a5c", "s": "#f2c9a0", "k": "#070a22", "m": "#c0566e",
                  "g": GREEN, "b": "#2d3a8c"}


# ---- helpers ---------------------------------------------------------------
def bitmap_path(rows, x, y, s, on="1"):
    d = []
    for r, row in enumerate(rows):
        c = 0
        while c < len(row):
            if row[c] == on:
                start = c
                while c < len(row) and row[c] == on:
                    c += 1
                d.append(f"M{x + start * s:g} {y + r * s:g}h{(c - start) * s:g}v{s:g}h{-(c - start) * s:g}z")
            else:
                c += 1
    return "".join(d)


def icon(name, x, y, s, fill, cls=""):
    klass = f' class="{cls}"' if cls else ""
    return f'<path{klass} fill="{fill}" d="{bitmap_path(ICONS[name], x, y, s)}"/>'


def text(t, x, y, s, fill, cls="", anchor="start"):
    if anchor == "middle":
        x = x - text_width(t, s) / 2
    elif anchor == "end":
        x = x - text_width(t, s)
    klass = f' class="{cls}"' if cls else ""
    return f'<path{klass} fill="{fill}" d="{text_path(t, round(x), y, s)}"/>'


# Reduced motion: stop every animation and show the end state. Only the classes
# that start hidden (typed letters, revealed rows, bar segments) are forced visible.
REDUCED = ("@media (prefers-reduced-motion: reduce) { * { animation: none !important; } "
           ".t, .sub, .start, .row, .seg, .coin { opacity: 1 !important; } }")


def svg(w, h, label, body, css="", accent=GREEN, inner=True):
    """Wrap `body` in the shared arcade frame: navy screen, neon border, notched corners, scanlines."""
    inner_rect = (f'<rect x="20" y="20" width="{w - 40}" height="{h - 40}" fill="none" stroke="{DIM}" stroke-width="2"/>'
                  if inner else "")
    corners = "".join(f'<rect x="{x}" y="{y}" width="10" height="10"/>' for x in (8, w - 18) for y in (8, h - 18))
    dots = "".join(f'<rect x="{x}" y="{y}" width="4" height="4"/>' for x in (16, w - 20) for y in (16, h - 20))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{label}">
  <title>{label}</title>
  <style>
    {css}
    {REDUCED}
  </style>
  <defs>
    <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="2" fill="#ffffff" opacity=".035"/></pattern>
  </defs>
  <rect width="{w}" height="{h}" fill="{NAVY_DEEP}"/>
  <rect x="10" y="10" width="{w - 20}" height="{h - 20}" fill="{NAVY}" stroke="{accent}" stroke-width="4"/>
  {inner_rect}
  <g fill="{NAVY_DEEP}">{corners}</g>
  <g fill="{accent}">{dots}</g>
  {body}
  <rect x="12" y="12" width="{w - 24}" height="{h - 24}" fill="url(#scan)"/>
</svg>
'''


# ---- 1. banner -------------------------------------------------------------
def banner():
    W, H = 800, 280
    NAME, NAME_S, NAME_Y = "DAVY NGUYEN", 8, 84
    TYPE_START, TYPE_STEP = 0.3, 0.11
    typed_end = TYPE_START + len(NAME) * TYPE_STEP
    bands = ((44, 65), (84, 144), (170, 198), (228, 249))

    rng = random.Random(3)
    stars = []
    for _ in range(34):
        x, y = rng.randrange(24, W - 28, 4), rng.randrange(22, H - 26, 4)
        if any(a - 6 <= y <= b + 6 for a, b in bands):
            continue
        size = 4 if rng.random() < 0.25 else 2
        stars.append(f'<rect class="tw" x="{x}" y="{y}" width="{size}" height="{size}" fill="#6b78d6" '
                     f'style="animation-delay:{rng.uniform(0, 3):.2f}s"/>')

    def name_layer(fill, cls=None, dx=0, dy=0):
        x = round((W - text_width(NAME, NAME_S)) / 2) + dx
        parts = [f'<path class="t" style="animation-delay:{TYPE_START + i * TYPE_STEP:.2f}s" d="{d}"/>'
                 for i, _, d in glyph_paths(NAME, x, NAME_Y + dy, NAME_S)]
        klass = f' class="{cls}"' if cls else ""
        return f'<g{klass} fill="{fill}">' + "".join(parts) + "</g>"

    t0 = typed_end + 1
    css = f"""
    .t {{ opacity: 0; animation: show 0s steps(1) forwards; }}
    .sub {{ opacity: 0; animation: show 0s steps(1) {typed_end + 0.2:.2f}s forwards; }}
    .start {{ opacity: 0; animation: blink 1.1s steps(1) {typed_end + 0.6:.2f}s infinite; }}
    .tw {{ animation: twinkle 3s steps(1) infinite; }}
    .gm {{ opacity: 0; animation: glitch-m 5s steps(1) {t0:.2f}s infinite; }}
    .gc {{ opacity: 0; animation: glitch-c 5s steps(1) {t0:.2f}s infinite; }}
    .main {{ animation: jitter 5s steps(1) {t0:.2f}s infinite; }}
    @keyframes show {{ to {{ opacity: 1; }} }}
    @keyframes blink {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0; }} }}
    @keyframes twinkle {{ 0% {{ opacity: 1; }} 70% {{ opacity: .35; }} 85% {{ opacity: 1; }} }}
    @keyframes glitch-m {{ 0% {{ opacity: 0; }} 90% {{ opacity: .85; transform: translate(-6px, 0); }}
      92% {{ opacity: .85; transform: translate(5px, 2px); }} 94% {{ opacity: 0; }} }}
    @keyframes glitch-c {{ 0% {{ opacity: 0; }} 90% {{ opacity: .85; transform: translate(6px, -2px); }}
      92% {{ opacity: .85; transform: translate(-4px, 0); }} 94% {{ opacity: 0; }} }}
    @keyframes jitter {{ 0% {{ transform: none; }} 90% {{ transform: translate(2px, 0); }}
      92% {{ transform: translate(-2px, 0); }} 94% {{ transform: none; }} }}"""
    body = f'''<defs><filter id="glow" x="-10%" y="-30%" width="120%" height="160%">
    <feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter></defs>
  <g>{"".join(stars)}</g>
  {text("PLAYER 1", W / 2, 44, 3, MAGENTA, anchor="middle")}
  {name_layer(MAGENTA, "gm")}
  {name_layer(CYAN, "gc")}
  <g class="main">{name_layer("#8a1f86", dx=4, dy=4)}<g filter="url(#glow)">{name_layer(GREEN)}</g></g>
  {text("SYSADMIN · SOFTWARE ENGINEER", W / 2, 170, 4, PALE, "sub", "middle")}
  {text("▶ PRESS START", W / 2, 228, 3, PALE, "start", "middle")}'''
    return svg(W, H, "Player 1: Davy Nguyen, Systems Administrator and Software Engineer. Press start.", body, css)


# ---- 2. character sheet ----------------------------------------------------
def character():
    W, H = 800, 290
    s = 8
    sx, sy = 52, 58
    sprite = []
    for key, colour in SPRITE_COLOURS.items():
        sprite.append(f'<path fill="{colour}" d="{bitmap_path(SPRITE, sx, sy, s, key)}"/>')
    rows = []
    for i, (label, value) in enumerate(CHARACTER):
        y = 44 + i * 31
        rows.append(f'<g class="row" style="animation-delay:{0.15 + i * 0.12:.2f}s">'
                    f'{text(label, 214, y, 3, MAGENTA)}{text(value, 358, y, 3, PALE)}</g>')
    css = """
    .row { opacity: 0; animation: show 0s steps(1) forwards; }
    .bob { animation: bob 1.2s steps(1) infinite; }
    .cur { animation: blink 1s steps(1) infinite; }
    @keyframes show { to { opacity: 1; } }
    @keyframes bob { 0% { transform: translateY(0); } 50% { transform: translateY(-4px); } }
    @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0; } }"""
    body = f'''<rect x="36" y="40" width="128" height="176" fill="{NAVY_DEEP}" stroke="{DIM}" stroke-width="2"/>
  <g class="bob">{"".join(sprite)}</g>
  <rect x="44" y="196" width="112" height="10" fill="{DIM}"/>
  {text("P1", 100, 232, 3, GREEN, anchor="middle")}
  {text("▶", 68, 232, 3, GREEN, "cur", "middle")}
  <rect x="190" y="40" width="2" height="{H - 80}" fill="{DIM}"/>
  {"".join(rows)}'''
    label = ("Character sheet. Class: Systems Administrator Technician. Guild: County of Santa Clara. "
             "Origin: UC Irvine, B.S. 2023. Level 4. Base: Bay Area, CA. Weapon: Python. "
             "Current quest: AWS Solutions Architect Associate.")
    return svg(W, H, label, body, css)


# ---- 3. skill stats --------------------------------------------------------
def stats():
    W = 800
    col_x = (36, 412)
    seg_w, seg_gap, seg_h = 14, 3, 18
    blocks, label_parts = [], []
    row_y0 = 40
    tallest = max(len(g[2]) for g in SKILLS)
    group_h = 34 + tallest * 32
    delay = 0.2
    for gi, (group, colour, skills) in enumerate(SKILLS):
        gx = col_x[gi % 2]
        gy = row_y0 + (gi // 2) * (group_h + 18)
        blocks.append(text(group, gx, gy, 3, colour))
        for si, (skill, level) in enumerate(skills):
            y = gy + 34 + si * 32
            blocks.append(text(skill, gx, y, 3, PALE))
            bx = gx + 190
            for k in range(10):
                x = bx + k * (seg_w + seg_gap)
                if k < level:
                    blocks.append(f'<rect class="seg" style="animation-delay:{delay + k * 0.05:.2f}s" '
                                  f'x="{x}" y="{y + 1}" width="{seg_w}" height="{seg_h}" fill="{colour}"/>')
                else:
                    blocks.append(f'<rect x="{x + 1}" y="{y + 2}" width="{seg_w - 2}" height="{seg_h - 2}" '
                                  f'fill="none" stroke="{DIM}" stroke-width="2"/>')
            label_parts.append(f"{skill.title()} {level} of 10")
            delay += 0.08
    H = row_y0 + 2 * group_h + 18 + 22
    css = """
    .seg { opacity: 0; animation: show 0s steps(1) forwards; }
    @keyframes show { to { opacity: 1; } }"""
    label = "Skill stats out of 10. " + ", ".join(label_parts) + "."
    return svg(W, H, label, "\n  ".join(blocks), css)


# ---- 4. achievements -------------------------------------------------------
def achievements():
    W, H = 800, 272
    box_w, gap = 240, 12
    x0 = (W - (3 * box_w + 2 * gap)) / 2
    parts = []
    for i, (lines, ico, unlocked, status) in enumerate(ACHIEVEMENTS):
        bx = x0 + i * (box_w + gap)
        cx = bx + box_w / 2
        border = GREEN if unlocked else DIM
        dash = "" if unlocked else ' stroke-dasharray="8 6"'
        parts.append(f'<rect x="{bx:g}" y="30" width="{box_w}" height="{H - 60}" fill="{NAVY_DEEP}" '
                     f'stroke="{border}" stroke-width="2"{dash}/>')
        parts.append(icon(ico, cx - 24, 44, 6, GOLD if unlocked else DIM, "shine" if unlocked else ""))
        for li, line in enumerate(lines):
            parts.append(text(line, cx, 106 + li * 28, 3, PALE if unlocked else MUTED, anchor="middle"))
        if unlocked:
            parts.append(text(status, cx, 202, 3, GREEN, anchor="middle"))
        else:
            # target date plus a charging bar
            parts.append(text(status, cx, 196, 2, MAGENTA, "blink", "middle"))
            parts.append(f'<rect x="{cx - 70:g}" y="218" width="140" height="10" fill="none" stroke="{MAGENTA}" stroke-width="2"/>')
            parts.append(f'<rect class="charge" x="{cx - 67:g}" y="221" width="134" height="4" fill="{MAGENTA}"/>')
    css = """
    .shine { animation: shine 2.4s steps(1) infinite; }
    .charge { transform-box: fill-box; transform-origin: left; animation: charge 2.4s steps(8) infinite; }
    .blink { animation: blink 1.2s steps(1) infinite; }
    @keyframes shine { 0% { opacity: 1; } 85% { opacity: .55; } 92% { opacity: 1; } }
    @keyframes charge { from { transform: scaleX(0); } to { transform: scaleX(1); } }
    @keyframes blink { 0% { opacity: 1; } 50% { opacity: .2; } }"""
    label = ("Achievements. Unlocked: AWS Certified Cloud Practitioner; Google Cybersecurity Professional Certificate. "
             "Locked, in progress: AWS Solutions Architect Associate, expected December 2026.")
    return svg(W, H, label, "\n  ".join(parts), css, inner=False)


# ---- 5. quest card headers -------------------------------------------------
def quest(num, title, ico, status, colour):
    W, H = 400, 80
    body = f'''{icon(ico, 26, 20, 5, GOLD, "bob")}
  {text(num, 80, 22, 2, MAGENTA)}
  {text(status, W - 26, 22, 2, colour, anchor="end")}
  {text(title, 80, 42, 3, PALE)}'''
    css = """
    .bob { animation: bob 1.4s steps(1) infinite; }
    @keyframes bob { 0% { transform: translateY(0); } 50% { transform: translateY(-3px); } }"""
    label = f"{num.title()}: {title.title()} ({status.replace('★', '').strip().lower()})"
    return svg(W, H, label, body, css, inner=False)


# ---- 7. footer -------------------------------------------------------------
def footer():
    W, H = 800, 200
    digits = "9876543210"
    big = 7
    cont_x = round((W - text_width("CONTINUE? 9", big)) / 2)  # title + space + one digit, centred
    digit_x = cont_x + 10 * 6 * big
    coin_w, coin_gap = 40, 16
    coin_x = round((W - (coin_w + coin_gap + text_width("INSERT COIN BELOW", 3))) / 2)
    frames = []
    for i, d in enumerate(digits):
        frames.append(f'<path class="n" style="animation-delay:{i}s" fill="{GREEN}" '
                      f'd="{text_path(d, digit_x, 46, big)}"/>')
    css = """
    .n { opacity: 0; animation: tick 10s steps(1) infinite; }
    .coin { animation: blink 1s steps(1) infinite; }
    .spin { animation: spin 1.2s steps(1) infinite; }
    @keyframes tick { 0% { opacity: 1; } 10% { opacity: 0; } }
    @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0; } }
    @keyframes spin { 0% { transform: scaleX(1); } 25% { transform: scaleX(.5); } 50% { transform: scaleX(.15); } 75% { transform: scaleX(.5); } }
    @media (prefers-reduced-motion: reduce) { .n { opacity: 0 !important; } .n:last-child { opacity: 1 !important; } }"""
    body = f'''{text("CONTINUE?", cont_x, 46, big, MAGENTA)}
  <g>{"".join(frames)}</g>
  <g class="spin" style="transform-box: fill-box; transform-origin: center">{icon("coin", coin_x, 118, 5, GOLD)}</g>
  {text("INSERT COIN BELOW", coin_x + coin_w + coin_gap, 128, 3, PALE, "coin")}
  {text("LINKS ▼", W / 2, 164, 2, MUTED, anchor="middle")}'''
    # with reduced motion, only the last digit ("0") shows: .n:last-child in the group above
    return svg(W, H, "Continue? Insert coin: contact links are below.", body, css)


def main():
    OUT.mkdir(exist_ok=True)
    files = {
        "banner.svg": banner(),
        "character.svg": character(),
        "stats.svg": stats(),
        "achievements.svg": achievements(),
        "footer.svg": footer(),
    }
    for slug, num, title, ico, status, colour in QUESTS:
        files[f"quest-{slug}.svg"] = quest(num, title, ico, status, colour)
    for name, content in files.items():
        (OUT / name).write_text(content, encoding="utf-8")
        print(f"{name:32} {len(content.encode()):>6} bytes")


if __name__ == "__main__":
    main()
