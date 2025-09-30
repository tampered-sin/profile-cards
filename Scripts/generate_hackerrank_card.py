#!/usr/bin/env python3
"""
Generate a modern HackerRank stats SVG card with icons for 'tenkunga911'.
"""

import os
import re
from datetime import datetime
from textwrap import dedent

import requests
from bs4 import BeautifulSoup

OUT_DIR = "assets"
OUT_FILE = os.path.join(OUT_DIR, "hackerrank_card.svg")
USERNAME = "tenkunga911"

HEADERS = {
    "User-Agent": "github-actions-hackerrank-card/1.0 (+https://github.com)"
}

def fetch_profile_json(username):
    url = f"https://www.hackerrank.com/rest/hackers/{username}/profile"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None

def parse_profile_html(username):
    url = f"https://www.hackerrank.com/{username}"
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    stats = {
        "username": username,
        "problems_solved": "—",
        "rank": "—",
        "badges": "—",
        "profile_url": url
    }

    text = soup.get_text(separator="\n")

    m = re.search(r"(Problems\s*Solved|Solved)\s*[:\-\n]?\s*([0-9,]+)", text, re.IGNORECASE)
    if m:
        stats["problems_solved"] = m.group(2).replace(",", "")

    m = re.search(r"Badges\s*[:\-\n]?\s*([0-9,]+)", text, re.IGNORECASE)
    if m:
        stats["badges"] = m.group(1).replace(",", "")

    m = re.search(r"(Rank|Global Rank)\s*(?:#)?\s*([0-9,]+)", text, re.IGNORECASE)
    if m:
        stats["rank"] = m.group(2).replace(",", "")

    if stats["problems_solved"] == "—":
        candidates = re.findall(r"([0-9,]{1,10})\s*\n\s*(Problems|Solved|Submissions)", text, re.IGNORECASE)
        if candidates:
            stats["problems_solved"] = candidates[0][0].replace(",", "")

    return stats

def build_svg(stats):
    user = stats["username"]
    solved = stats["problems_solved"]
    rank = stats["rank"]
    badges = stats["badges"]
    profile_url = stats["profile_url"]
    generated_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    # Inline SVG icons
    check_icon = """<text x="12" y="14" font-size="14">✅</text>"""
    trophy_icon = """<text x="12" y="14" font-size="14">🏆</text>"""
    medal_icon = """<text x="12" y="14" font-size="14">🎖️</text>"""

    svg = dedent(f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="540" height="160" viewBox="0 0 540 160" role="img" aria-labelledby="title">
      <title>HackerRank stats for {user}</title>
      <rect rx="15" width="100%" height="100%" fill="#0e6a4a"/>
      <g transform="translate(20,20)" fill="#ffffff" font-family="Segoe UI, Roboto, Helvetica, sans-serif">

        <!-- Username -->
        <text x="0" y="0" font-size="22" font-weight="700">{user}</text>
        <a href="{profile_url}" target="_blank" rel="noopener noreferrer">
          <text x="0" y="30" font-size="12" opacity="0.9">View HackerRank profile</text>
        </a>

        <!-- Stats cards -->
        <g transform="translate(0,50)">
          <!-- Problems Solved -->
          <rect x="0" y="0" width="160" height="70" rx="12" fill="#1b8e5f" opacity="0.85"/>
          {check_icon}
          <text x="32" y="24" font-size="12" fill="#ffffff" font-weight="500">Problems Solved</text>
          <text x="32" y="52" font-size="24" font-weight="700">{solved}</text>

          <!-- Global Rank -->
          <g transform="translate(190,0)">
            <rect x="0" y="0" width="160" height="70" rx="12" fill="#1b8e5f" opacity="0.85"/>
            {trophy_icon}
            <text x="32" y="24" font-size="12" fill="#ffffff" font-weight="500">Global Rank</text>
            <text x="32" y="52" font-size="24" font-weight="700">{rank}</text>
          </g>

          <!-- Badges -->
          <g transform="translate(380,0)">
            <rect x="0" y="0" width="160" height="70" rx="12" fill="#1b8e5f" opacity="0.85"/>
            {medal_icon}
            <text x="32" y="24" font-size="12" fill="#ffffff" font-weight="500">Badges</text>
            <text x="32" y="52" font-size="24" font-weight="700">{badges}</text>
          </g>
        </g>

        <!-- Footer timestamp -->
        <text x="0" y="145" font-size="10" fill="#ffffff" opacity="0.7">Updated: {generated_time}</text>
      </g>
    </svg>
    """)
    return svg

def main():
    stats = fetch_profile_json(USERNAME)
    if not stats or not stats.get("problems_solved"):
        stats = parse_profile_html(USERNAME)

    if not os.path.exists(OUT_DIR):
        os.makedirs(OUT_DIR, exist_ok=True)

    svg = build_svg(stats)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write(svg)

    print(f"Wrote HackerRank stats card with icons to {OUT_FILE}")

if __name__ == "__main__":
    main()
