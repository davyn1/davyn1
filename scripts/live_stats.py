"""Generate the live "languages" card from GitHub's API, in the cloud card style.

Usage: GITHUB_TOKEN=... python scripts/live_stats.py <github user> <out dir>

Runs daily in .github/workflows/profile-assets.yml and publishes languages.svg
to the `output` branch. Standard library only (the static cards need Pillow,
this one doesn't). Counts code in public, non-fork repos the user owns.
"""
import json
import os
import sys
import urllib.request
from pathlib import Path

from cards import BODY, FAINT, INK, TRACK, card, label, t

QUERY = """
query($login: String!) {
  user(login: $login) {
    repositories(ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC, first: 100) {
      nodes { languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name color } } } }
    }
  }
}
"""

# Markup and notebooks inflate byte counts without saying much about programming.
EXCLUDED = {"HTML", "CSS", "SCSS", "Jupyter Notebook"}


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


def languages(user: dict, top: int = 5):
    sizes: dict[str, int] = {}
    colours: dict[str, str] = {}
    for repo in user["repositories"]["nodes"]:
        for edge in repo["languages"]["edges"]:
            name = edge["node"]["name"]
            if name in EXCLUDED:
                continue
            sizes[name] = sizes.get(name, 0) + edge["size"]
            colours[name] = edge["node"]["color"] or "#8b949e"
    total = sum(sizes.values()) or 1
    ranked = sorted(sizes.items(), key=lambda kv: kv[1], reverse=True)[:top]
    return [(name, size / total * 100, colours[name]) for name, size in ranked]


def languages_card(langs) -> str:
    W = 800
    row_h, y0 = 34, 82
    H = y0 + len(langs) * row_h + 18
    bar_x, bar_w = 230, 470
    parts = [label(36, 46, "LANGUAGES"),
             t(W - 36, 46, "by code in public repos · updated daily", 11.5, FAINT, 400, anchor="end")]
    for i, (name, pct, colour) in enumerate(langs):
        y = y0 + i * row_h
        parts.append(f'<rect x="36" y="{y - 12}" width="14" height="14" rx="3" fill="{colour}"/>')
        parts.append(t(60, y, name, 14, INK, 600))
        parts.append(f'<rect x="{bar_x}" y="{y - 10}" width="{bar_w}" height="10" rx="5" fill="{TRACK}"/>')
        parts.append(f'<rect class="grow" style="animation-delay:{0.1 + i * 0.12:.2f}s" x="{bar_x}" y="{y - 10}" '
                     f'width="{max(bar_w * pct / 100, 6):.1f}" height="10" rx="5" fill="{colour}"/>')
        parts.append(t(W - 36, y, f"{pct:.0f}%", 13, BODY, 600, anchor="end"))
    css = """
    .grow { transform-box: fill-box; transform-origin: left; animation: grow 1s cubic-bezier(.2, .8, .2, 1) both; }
    @keyframes grow { from { transform: scaleX(0); } }"""
    aria = "Languages by code in public repos: " + ", ".join(f"{n} {p:.0f}%" for n, p, _ in langs) + "."
    return card(W, H, aria, "\n  ".join(parts), css, clouds=[(560, H - 60, 1, .03, 90)])


def main() -> None:
    login, out = sys.argv[1], Path(sys.argv[2])
    token = os.environ.get("GITHUB_TOKEN") or sys.exit("GITHUB_TOKEN is not set")
    out.mkdir(parents=True, exist_ok=True)
    (out / "languages.svg").write_text(languages_card(languages(fetch(login, token))), encoding="utf-8")
    print("wrote languages.svg to", out)


if __name__ == "__main__":
    main()
