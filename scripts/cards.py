"""Build the cloud-themed profile cards into ../assets.

Usage (from the repo root):  python scripts/cards.py      (needs Pillow for thumbnails)

Each card is a self-contained SVG: dark panel, sky-to-sunset gradient border,
slow drifting clouds. GitHub shows README SVGs through <img>, so screenshots
are embedded as data URIs and links live in the README around each card.
Edit PROFILE, PROJECTS and CERTS below and rerun.
"""
import base64
import io
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"

# ---- theme -----------------------------------------------------------------
BG, BG_SOFT, TRACK = "#0b1020", "#121933", "#1c2445"
INK, BODY, FAINT = "#f1f5ff", "#a9b4d6", "#6b77a3"
SKY, VIOLET, BLUSH = "#38bdf8", "#a78bfa", "#f9a8d4"
GREEN = "#4ade80"
SANS = "'Segoe UI', -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace"

# A soft cloud silhouette, 100 x 44 units, drawn at any scale with transform.
CLOUD = ("M18 44 C6 44 0 37 0 29 C0 21 7 15 15 16 C17 7 25 1 35 1 C45 1 52 7 55 15 "
         "C59 10 66 8 72 10 C80 12 85 19 85 26 C93 26 100 32 100 37 C100 41 97 44 92 44 Z")

# ---- content ---------------------------------------------------------------
PROFILE = {
    "label": "CLOUD PROFILE",
    "name": "Davy Nguyen",
    "tagline": ["Systems Administrator · Software Engineer in the making",
                "Building fun projects and learning as I go."],
    "meta": "Bay Area · County of Santa Clara · UC Irvine ’23",
    "now": "Now: building an AI agent harness  ·  Next: a RAG project with evals",
}

PROJECTS = [  # slug, label, name, description lines, language, colour, badge, thumbnail
    ("yums-map", "PROJECT 01", "Bay Area Yums Map",
     ["Saved Instagram food reels,", "turned into a shared map."],
     "Python", "#3572A5", "Live demo", ("yums-map.png", (300, 40, 740, 320))),
    ("stock-analysis", "PROJECT 02", "Stock Analysis",
     ["28 indicators computed in code,", "explained by an LLM at 3 levels."],
     "Python", "#3572A5", "FastAPI + React", ("stock-analysis-dark.png", (266, 368, 706, 648))),
    ("trading-bot", "PROJECT 03", "Trading Bot",
     ["Multi-strategy Alpaca bot with", "ATR-based stops and risk limits."],
     "Python", "#3572A5", "Paper trading", ("trading-bot-dark.png", (470, 400, 910, 680))),
    ("flashcards", "PROJECT 04", "Korean Flashcards",
     ["Offline-first PWA with spaced", "repetition and device sync."],
     "TypeScript", "#3178c6", "Live app", None),
]

CERTS = [  # name lines, issuer, earned, status
    (["Cloud Practitioner"], "AWS Certified", True, "Earned"),
    (["Cybersecurity Professional"], "Google Certificate", True, "Earned"),
    (["Solutions Architect – Associate"], "AWS Certified", False, "In progress · Dec 2026"),
]


# ---- shared pieces -----------------------------------------------------------
def t(x, y, s, size, fill, weight=400, family=SANS, anchor="start", spacing=None, cls=None):
    extra = f' letter-spacing="{spacing}"' if spacing else ""
    extra += f' text-anchor="{anchor}"' if anchor != "start" else ""
    extra += f' class="{cls}"' if cls else ""
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}"{extra}>{escape(s)}</text>')


def label(x, y, s):
    return t(x, y, s, 11, SKY, 700, MONO, spacing="2.5")


REDUCED = "@media (prefers-reduced-motion: reduce) { * { animation: none !important; } }"


def card(w, h, aria, body, css="", clouds=()):
    """Dark rounded card with an animated gradient border and optional drifting clouds.

    clouds: (x, y, scale, opacity, seconds) tuples; each drifts left to right and loops.
    """
    drift = []
    for i, (x, y, sc, op, secs) in enumerate(clouds):
        drift.append(f'<g class="drift" style="animation-duration:{secs}s;animation-delay:-{secs * (i + 1) / 3:.1f}s">'
                     f'<path d="{CLOUD}" transform="translate({x} {y}) scale({sc})" fill="#ffffff" opacity="{op}"/></g>')
    drift_css = f"""
    .drift {{ animation: drift linear infinite; }}
    @keyframes drift {{ from {{ transform: translateX(-{w // 3}px); }} to {{ transform: translateX({w // 3}px); }} }}""" if clouds else ""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(aria)}">
  <title>{escape(aria)}</title>
  <style>{css}{drift_css}
    .edge {{ animation: hue 9s ease-in-out infinite alternate; }}
    @keyframes hue {{ from {{ stop-color: {SKY}; }} to {{ stop-color: {BLUSH}; }} }}
    {REDUCED}
  </style>
  <defs>
    <linearGradient id="border" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{SKY}" class="edge"/>
      <stop offset=".5" stop-color="{VIOLET}"/>
      <stop offset="1" stop-color="{BLUSH}"/>
    </linearGradient>
    <clipPath id="panel"><rect x="2" y="2" width="{w - 4}" height="{h - 4}" rx="16"/></clipPath>
  </defs>
  <rect x="2" y="2" width="{w - 4}" height="{h - 4}" rx="16" fill="{BG}"/>
  <g clip-path="url(#panel)">{"".join(drift)}</g>
  <rect x="2" y="2" width="{w - 4}" height="{h - 4}" rx="16" fill="none" stroke="url(#border)" stroke-width="2.5"/>
  {body}
</svg>
'''


def thumbnail(src, box, size=(264, 168)):
    """Crop a screenshot, shrink it, and return it as a JPEG data URI."""
    from PIL import Image  # only needed when building the static cards

    img = Image.open(OUT / src).convert("RGB").crop(box).resize(size, Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=82, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


# ---- cards -------------------------------------------------------------------
def header():
    W, H = 800, 236
    p = PROFILE
    cx, cy, r = 676, 112, 62
    body = f'''{label(36, 46, p["label"])}
  {t(36, 92, p["name"], 36, INK, 700)}
  {t(36, 124, p["tagline"][0], 16, INK, 600)}
  {t(36, 146, p["tagline"][1], 15, BODY)}
  {t(36, 180, p["meta"], 12.5, FAINT, 400, MONO)}
  <circle cx="36" cy="203" r="3.5" fill="{GREEN}" class="pulse"/>
  {t(48, 207, p["now"], 12.5, BODY, 400, MONO)}
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#1e3a8a"/><stop offset=".6" stop-color="#6d28d9"/><stop offset="1" stop-color="#db2777"/>
    </linearGradient>
    <clipPath id="avatar"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath>
  </defs>
  <circle cx="{cx}" cy="{cy}" r="{r + 5}" fill="none" stroke="url(#border)" stroke-width="3"/>
  <circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#sky)"/>
  <g clip-path="url(#avatar)">{server_cloud(cx, cy)}</g>'''
    css = """
    .bob { animation: bob 5s ease-in-out infinite; }
    .pulse { animation: pulse 2s ease-in-out infinite; }
    .uplink { animation: uplink 1.2s linear infinite; }
    .led { animation: led 2.4s steps(1) infinite; }
    @keyframes bob { 0%, 100% { transform: translate(0, 0); } 50% { transform: translate(3px, -2px); } }
    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: .3; } }
    @keyframes uplink { to { stroke-dashoffset: 12; } }
    @keyframes led { 0% { opacity: 1; } 80% { opacity: .25; } 90% { opacity: 1; } }"""
    aria = (f'{p["name"]}. {p["tagline"][0]}. {p["tagline"][1]} {p["meta"].replace("’", "20")}. '
            f'{p["now"].replace("  ·  ", ". ")}.')
    return card(W, H, aria, body, css, clouds=[(120, 150, 1.6, .035, 70), (420, 20, 1.1, .03, 90), (300, 190, .8, .03, 60)])


def server_cloud(cx, cy):
    """Avatar art: a small server rack sending data up to a cloud (sysadmin → cloud).

    Drawn around (0, 0) and placed at (cx, cy). Status lights blink out of step,
    the dashed uplink flows upward, and the cloud drifts gently.
    """
    units = []
    for i, y in enumerate((-5, 15, 35)):
        units.append(f'<rect x="-30" y="{y}" width="60" height="16" rx="3" fill="{BG}" stroke="{SKY}" stroke-width="1.5"/>'
                     f'<line x1="-2" y1="{y + 8}" x2="22" y2="{y + 8}" stroke="{SKY}" stroke-width="1.5" opacity=".7"/>')
        for j, colour in enumerate((GREEN, BLUSH if i == 1 else GREEN)):
            units.append(f'<circle class="led" style="animation-delay:{(i * 2 + j) * 0.37:.2f}s" '
                         f'cx="{-21 + j * 8}" cy="{y + 8}" r="2.5" fill="{colour}"/>')
    return f'''<g transform="translate({cx} {cy + 1}) scale(.97)">
      <g class="bob"><path d="{CLOUD}" transform="translate(-36 -53) scale(.72)" fill="#ffffff"/></g>
      <line class="uplink" x1="0" y1="-8" x2="0" y2="-20" stroke="#ffffff" stroke-width="2" stroke-dasharray="3 3"/>
      {"".join(units)}
    </g>'''


def flashcard_art(x, y, w, h):
    """Small drawn stand-in for the flashcard app (its live site is behind a sign-in)."""
    return f'''<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="#05071a"/>
  <rect x="{x + 30}" y="{y + 14}" width="{w - 50}" height="{h - 40}" rx="6" fill="#2a2470" transform="rotate(-6 {x + w / 2} {y + h / 2})"/>
  <rect x="{x + 22}" y="{y + 12}" width="{w - 44}" height="{h - 38}" rx="6" fill="#141a3a" stroke="#6366f1" stroke-width="1.5"/>
  <text x="{x + w / 2}" y="{y + 50}" text-anchor="middle" font-family="'Malgun Gothic', 'Apple SD Gothic Neo', 'Noto Sans KR', sans-serif" font-size="22" font-weight="700" fill="#818cf8">한국어</text>
  {"".join(f'<rect x="{x + 16 + i * 26}" y="{y + h - 20}" width="22" height="10" rx="3" fill="{c}"/>' for i, c in enumerate(("#ef4444", "#f59e0b", "#22c55e", "#38bdf8")))}'''


def project(slug, num, name, lines, lang, colour, badge, thumb):
    W, H = 400, 200
    tx, ty, tw, th = 254, 58, 124, 80
    if thumb:
        src, box = thumb
        art = (f'<clipPath id="thumb"><rect x="{tx}" y="{ty}" width="{tw}" height="{th}" rx="8"/></clipPath>'
               f'<image href="{thumbnail(src, box)}" x="{tx}" y="{ty}" width="{tw}" height="{th}" '
               f'preserveAspectRatio="xMidYMid slice" clip-path="url(#thumb)"/>')
    else:
        art = flashcard_art(tx, ty, tw, th)
    body = f'''{label(26, 40, num)}
  {t(26, 80, name, 19, INK, 700)}
  {t(26, 106, lines[0], 13, BODY)}
  {t(26, 124, lines[1], 13, BODY)}
  {art}
  <rect x="{tx}" y="{ty}" width="{tw}" height="{th}" rx="8" fill="none" stroke="{TRACK}" stroke-width="1.5"/>
  <rect x="26" y="158" width="10" height="10" rx="2" fill="{colour}"/>
  {t(42, 167, lang, 12, BODY, 600)}
  <rect x="{W - 26 - 9 * len(badge) - 18}" y="152" width="{9 * len(badge) + 18}" height="22" rx="11" fill="{BG_SOFT}" stroke="{TRACK}"/>
  {t(W - 26 - (9 * len(badge) + 18) / 2, 167, badge, 11.5, SKY, 600, anchor="middle")}'''
    aria = f"{num.title()}: {name}. {' '.join(lines)} {lang}. {badge}."
    return card(W, H, aria, body, clouds=[(40, 150, .9, .03, 80)])


def certifications():
    W, H = 800, 168
    col_w = (W - 72) / 3
    parts = [label(36, 46, "CERTIFICATIONS")]
    for i, (lines, issuer, earned, status) in enumerate(CERTS):
        x = 36 + i * col_w
        if earned:
            parts.append(f'<circle cx="{x + 12}" cy="{88}" r="12" fill="{GREEN}" opacity=".15"/>'
                         f'<path d="M{x + 6} 88 l4 4 l8 -8" fill="none" stroke="{GREEN}" stroke-width="2.4" '
                         f'stroke-linecap="round" stroke-linejoin="round"/>')
        else:
            parts.append(f'<circle cx="{x + 12}" cy="88" r="11" fill="none" stroke="{VIOLET}" stroke-width="2.4" '
                         f'stroke-dasharray="4 3" class="spin" style="transform-origin:{x + 12}px 88px"/>')
        parts.append(t(x + 34, 84, issuer, 11.5, FAINT, 600, MONO))
        parts.append(t(x + 34, 104, lines[0], 14.5 if len(lines[0]) < 28 else 13, INK, 700))
        parts.append(t(x + 34, 130, status, 12, GREEN if earned else VIOLET, 600))
    css = """
    .spin { animation: spin 6s linear infinite; }
    @keyframes spin { to { transform: rotate(360deg); } }"""
    aria = "Certifications. " + "; ".join(f"{issuer} {' '.join(l)}: {s}" for l, issuer, _, s in CERTS) + "."
    return card(W, H, aria, "\n  ".join(parts), css, clouds=[(500, 110, 1.2, .03, 85)])


def main():
    files = {"header.svg": header(), "certifications.svg": certifications()}
    for p in PROJECTS:
        files[f"project-{p[0]}.svg"] = project(*p)
    for name, content in files.items():
        (OUT / name).write_text(content, encoding="utf-8")
        print(f"{name:28} {len(content.encode()):>7} bytes")


if __name__ == "__main__":
    main()
