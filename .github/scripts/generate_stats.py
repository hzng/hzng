import os
import json
import urllib.request
import re

GH_TOKEN = os.environ.get("GH_TOKEN", "")
USERNAME = "hzng"

def fetch_json(url):
    req = urllib.request.Request(url)
    if GH_TOKEN:
        req.add_header("Authorization", f"Bearer {GH_TOKEN}")
    req.add_header("Accept", "application/vnd.github.v3+json")
    req.add_header("User-Agent", "Python-Script")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def main():
    os.makedirs("assets", exist_ok=True)
    
    # 1. Fetch user data
    user_data = fetch_json(f"https://api.github.com/users/{USERNAME}") or {}
    public_repos = user_data.get("public_repos", 0)
    followers = user_data.get("followers", 0)

    # 2. Fetch repos data
    repos_data = fetch_json(f"https://api.github.com/users/{USERNAME}/repos?per_page=100&type=owner") or []
    
    total_stars = 0
    total_forks = 0
    languages = {}

    for repo in repos_data:
        if repo.get("fork", False):
            continue
        total_stars += repo.get("stargazers_count", 0)
        total_forks += repo.get("forks_count", 0)
        
        lang_url = repo.get("languages_url")
        if lang_url:
            repo_langs = fetch_json(lang_url) or {}
            for lang, bytes_count in repo_langs.items():
                languages[lang] = languages.get(lang, 0) + bytes_count

    # Sort languages
    sorted_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:6]

    # Generate stats.svg
    stats_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="320" height="165" viewBox="0 0 320 165">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#1e1e2e"/>
      <stop offset="100%" style="stop-color:#16161e"/>
    </linearGradient>
    <linearGradient id="titleGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#f7b801"/>
      <stop offset="100%" style="stop-color:#ff6b00"/>
    </linearGradient>
  </defs>
  <rect width="320" height="165" fill="url(#bg)" rx="8"/>
  <rect x="4" y="4" width="312" height="157" fill="none" stroke="#2d2d3d" stroke-width="1" rx="6"/>
  
  <text x="160" y="30" text-anchor="middle" font-family="system-ui, sans-serif" font-size="16" font-weight="bold" fill="url(#titleGrad)">Hong Zhe's GitHub Stats</text>
  
  <g font-family="system-ui, sans-serif">
    <rect x="20" y="50" width="120" height="48" rx="6" fill="#1e1e2e" stroke="#2d2d3d"/>
    <text x="80" y="74" text-anchor="middle" font-size="20" font-weight="bold" fill="#f7b801">{public_repos}</text>
    <text x="80" y="90" text-anchor="middle" font-size="10" fill="#888">Public Repos</text>
    
    <rect x="180" y="50" width="120" height="48" rx="6" fill="#1e1e2e" stroke="#2d2d3d"/>
    <text x="240" y="74" text-anchor="middle" font-size="20" font-weight="bold" fill="#f7b801">{followers}</text>
    <text x="240" y="90" text-anchor="middle" font-size="10" fill="#888">Followers</text>
    
    <rect x="20" y="106" width="120" height="48" rx="6" fill="#1e1e2e" stroke="#2d2d3d"/>
    <text x="80" y="130" text-anchor="middle" font-size="20" font-weight="bold" fill="#f7b801">{total_stars}</text>
    <text x="80" y="146" text-anchor="middle" font-size="10" fill="#888">Total Stars</text>
    
    <rect x="180" y="106" width="120" height="48" rx="6" fill="#1e1e2e" stroke="#2d2d3d"/>
    <text x="240" y="130" text-anchor="middle" font-size="20" font-weight="bold" fill="#f7b801">{total_forks}</text>
    <text x="240" y="146" text-anchor="middle" font-size="10" fill="#888">Total Forks</text>
  </g>
</svg>'''

    with open("assets/stats.svg", "w", encoding="utf-8") as f:
        f.write(stats_svg)

    # Colors mapping
    color_map = {
        "Python": "#3776AB",
        "JavaScript": "#F7DF1E",
        "TypeScript": "#3178C6",
        "C": "#00599C",
        "C++": "#00599C",
        "C#": "#239120",
        "HTML": "#E34F26",
        "CSS": "#1572B6",
        "Vue": "#42b883",
        "Rust": "#dea584",
        "Go": "#00ADD8",
        "Java": "#ED8B00",
        "Shell": "#4EAA25"
    }

    total_bytes = sum(val for _, val in sorted_langs) or 1
    lang_bars = []
    y_pos = 46

    for lang, count in sorted_langs:
        pct = (count / total_bytes) * 100
        width = int((pct / 100) * 200)
        color = color_map.get(lang, "#888888")
        
        lang_bars.append(
            f'<text x="85" y="{y_pos + 12}" text-anchor="end" font-family="system-ui, sans-serif" font-size="11" fill="#ccc">{lang}</text>'
            f'<rect x="95" y="{y_pos}" width="{max(width, 4)}" height="14" rx="3" fill="{color}"/>'
            f'<text x="{95 + max(width, 4) + 8}" y="{y_pos + 12}" font-family="system-ui, sans-serif" font-size="10" fill="{color}">{pct:.1f}%</text>'
        )
        y_pos += 19

    top_langs_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="320" height="165" viewBox="0 0 320 165">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#1e1e2e"/>
      <stop offset="100%" style="stop-color:#16161e"/>
    </linearGradient>
    <linearGradient id="titleGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#f7b801"/>
      <stop offset="100%" style="stop-color:#ff6b00"/>
    </linearGradient>
  </defs>
  <rect width="320" height="165" fill="url(#bg)" rx="8"/>
  <rect x="4" y="4" width="312" height="157" fill="none" stroke="#2d2d3d" stroke-width="1" rx="6"/>
  
  <text x="160" y="30" text-anchor="middle" font-family="system-ui, sans-serif" font-size="16" font-weight="bold" fill="url(#titleGrad)">Most Used Languages</text>
  
  {"".join(lang_bars)}
</svg>'''

    with open("assets/top-langs.svg", "w", encoding="utf-8") as f:
        f.write(top_langs_svg)

    print("Successfully generated assets/stats.svg and assets/top-langs.svg")

if __name__ == "__main__":
    main()
