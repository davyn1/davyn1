"""Generate the live GitHub stats and top-languages cards in the arcade style.

Usage: GITHUB_TOKEN=... python scripts/live_stats.py <github user> <out dir>

Runs daily in .github/workflows/profile-assets.yml and publishes to the
`output` branch. Uses only the standard library plus this folder's modules.
Counts public, non-fork repos owned by the user.
"""
import json
import os
import sys
import urllib.request
from pathlib import Path

from build_assets import CYAN, GOLD, GREEN, MAGENTA, MUTED, PALE, DIM, svg, text
from pixfont import text_width

QUERY = """
query($login: String!) {
  user(login: $login) {
    repositories(ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC, first: 100) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name } } }
      }
    }
    contributionsCollection {
      totalCommitContributions
      restrictedContributionsCount
      totalPullRequestContributions
      contributionCalendar { totalContributions }
    }
  }
}
"""


def fetch(login: str, token: str) -> dict:
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "profile-live-stats"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.load(resp)
    if payload.get("errors"):
        raise SystemExit(f"GraphQL error: {payload['errors']}")
    return payload["data"]["user"]


def stats_card(user: dict) -> str:
    W, H = 400, 220
    repos = user["repositories"]
    cc = user["contributionsCollection"]
    rows = [
        ("CONTRIBUTIONS", cc["contributionCalendar"]["totalContributions"]),
        ("COMMITS", cc["totalCommitContributions"] + cc["restrictedContributionsCount"]),
        ("PULL REQUESTS", cc["totalPullRequestContributions"]),
        ("PUBLIC REPOS", repos["totalCount"]),
        ("LANGUAGES", len(language_totals(user))),
    ]
    parts = [text("PLAYER STATS", 30, 30, 3, GREEN), text("PAST YEAR", W - 30, 34, 2, MUTED, anchor="end")]
    for i, (label, value) in enumerate(rows):
        y = 70 + i * 26
        parts.append(text(label, 30, y, 2, PALE))
        parts.append(f'<rect x="{30 + text_width(label, 2) + 8:g}" y="{y + 6}" '
                     f'width="{W - 60 - text_width(label, 2) - 16 - text_width(str(value), 2):g}" height="2" fill="{DIM}"/>')
        parts.append(text(str(value), W - 30, y, 2, GOLD, anchor="end"))
    label = "GitHub stats for the past year: " + ", ".join(f"{l.title()} {v}" for l, v in rows) + "."
    return svg(W, H, label, "\n  ".join(parts), inner=False)


# Markup and notebooks inflate byte counts without saying much about programming.
EXCLUDED_LANGUAGES = {"HTML", "CSS", "SCSS", "Jupyter Notebook"}


def language_totals(user: dict) -> dict[str, int]:
    totals: dict[str, int] = {}
    for repo in user["repositories"]["nodes"]:
        for edge in repo["languages"]["edges"]:
            name = edge["node"]["name"]
            if name not in EXCLUDED_LANGUAGES:
                totals[name] = totals.get(name, 0) + edge["size"]
    return totals


def langs_card(user: dict, top: int = 5) -> str:
    W, H = 400, 220
    totals = language_totals(user)
    grand = sum(totals.values()) or 1
    ranked = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)[:top]
    colours = [GREEN, CYAN, MAGENTA, GOLD, PALE]
    parts = [text("TOP LANGUAGES", 30, 30, 3, GREEN)]
    bar_x, bar_w = 186, W - 30 - 186 - 52
    for i, (name, size) in enumerate(ranked):
        y = 70 + i * 26
        pct = size / grand * 100
        shown = name.upper()[:12]
        parts.append(text(shown, 30, y, 2, PALE))
        parts.append(f'<rect x="{bar_x}" y="{y}" width="{bar_w}" height="14" fill="none" stroke="{DIM}" stroke-width="2"/>')
        parts.append(f'<rect class="seg" style="animation-delay:{0.2 + i * 0.15:.2f}s" x="{bar_x + 3}" y="{y + 3}" '
                     f'width="{max((bar_w - 6) * pct / 100, 2):.1f}" height="8" fill="{colours[i % len(colours)]}"/>')
        parts.append(text(f"{pct:.0f}%", W - 30, y, 2, GOLD, anchor="end"))
    css = """
    .seg { opacity: 0; animation: show 0s steps(1) forwards; }
    @keyframes show { to { opacity: 1; } }"""
    label = "Top languages by code size: " + ", ".join(f"{n} {s / grand * 100:.0f}%" for n, s in ranked) + "."
    return svg(W, H, label, "\n  ".join(parts), css, inner=False)


def main() -> None:
    login, out = sys.argv[1], Path(sys.argv[2])
    token = os.environ.get("GITHUB_TOKEN") or sys.exit("GITHUB_TOKEN is not set")
    user = fetch(login, token)
    out.mkdir(parents=True, exist_ok=True)
    (out / "github-stats.svg").write_text(stats_card(user), encoding="utf-8")
    (out / "top-langs.svg").write_text(langs_card(user), encoding="utf-8")
    print("wrote github-stats.svg and top-langs.svg to", out)


if __name__ == "__main__":
    main()
