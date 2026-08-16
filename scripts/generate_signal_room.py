#!/usr/bin/env python3
"""Genera assets/signal-room.svg — dashboard radar SIGNAL ROOM con métricas reales de GitHub.
Usa solo la API REST pública (GITHUB_TOKEN opcional). Python >= 3.9, sin dependencias.
"""
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

USER = "rmMarioAlberto"
BASE = "https://api.github.com"

BG = "#050807"
PANEL = "#0B0F0E"
PRIMARY = "#39FF88"
AMBER = "#FFB454"
TEXT = "#E8F0EC"
MUTED = "#8A9490"


def api(path: str) -> dict | list:
    req = urllib.request.Request(f"{BASE}{path}", headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "signal-room",
        "X-GitHub-Api-Version": "2022-11-28",
    })
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as res:
        return json.load(res)


def main() -> int:
    try:
        user = api(f"/users/{USER}")
        repos = api(f"/users/{USER}/repos?per_page=100&sort=updated")
    except Exception as exc:
        print(f"ERROR: no se pudo consultar la API: {exc}", file=sys.stderr)
        return 1

    now = datetime.now(timezone.utc)
    stars = sum(r["stargazers_count"] for r in repos)
    lang_count: dict[str, int] = {}
    for r in repos:
        lang = r.get("language")
        if lang:
            lang_count[lang] = lang_count.get(lang, 0) + 1
    top_langs = ", ".join(k for k, _ in sorted(lang_count.items(), key=lambda kv: -kv[1])[:3]) or "—"
    active_30d = sum(1 for r in repos if r.get("pushed_at")
                     and (now - datetime.fromisoformat(r["pushed_at"].replace("Z", "+00:00"))).days <= 30)
    joined_year = user.get("created_at", "")[:4] or "—"
    followers = user.get("followers", 0)
    public_repos = user.get("public_repos", 0)
    generated = now.strftime("%Y-%m-%d %H:%M UTC")

    W, H = 800, 420
    CX, CY, R = 190, 205, 120

    def ring(r: int, opacity: str) -> str:
        return f'<circle cx="{CX}" cy="{CY}" r="{r}" fill="none" stroke="{PRIMARY}" stroke-opacity="{opacity}" stroke-width="1"/>'

    def metric(label: str, value: str, y: int) -> str:
        return (
            f'<text x="370" y="{y}" font-family="monospace" font-size="13" fill="{MUTED}">{label}</text>'
            f'<text x="770" y="{y}" text-anchor="end" font-family="monospace" font-size="13" font-weight="bold" fill="{PRIMARY}">{value}</text>'
        )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="JetBrains Mono, ui-monospace, monospace">
  <rect width="{W}" height="{H}" fill="{BG}"/>
  <rect x="14" y="14" width="{W - 28}" height="{H - 28}" fill="none" stroke="{PRIMARY}" stroke-opacity="0.25" rx="8"/>

  <text x="34" y="44" font-size="18" font-weight="bold" fill="{PRIMARY}">SIGNAL ROOM // TELEMETRY</text>
  <text x="{W - 34}" y="44" text-anchor="end" font-size="11" fill="{MUTED}">GITHUB://rmMarioAlberto</text>

  <!-- Radar -->
  <g>
    {ring(R, "0.45")}
    {ring(int(R * 0.75), "0.3")}
    {ring(int(R * 0.5), "0.2")}
    {ring(int(R * 0.25), "0.12")}
    <line x1="{CX - R}" y1="{CY}" x2="{CX + R}" y2="{CY}" stroke="{PRIMARY}" stroke-opacity="0.2"/>
    <line x1="{CX}" y1="{CY - R}" x2="{CX}" y2="{CY + R}" stroke="{PRIMARY}" stroke-opacity="0.2"/>
    <line x1="{CX - R}" y1="{CY - R}" x2="{CX + R}" y2="{CY + R}" stroke="{PRIMARY}" stroke-opacity="0.1"/>
    <line x1="{CX + R}" y1="{CY - R}" x2="{CX - R}" y2="{CY + R}" stroke="{PRIMARY}" stroke-opacity="0.1"/>
    <path d="M{CX},{CY} L{CX + R},{CY} A{R},{R} 0 0 1 {CX + R * 0.75},{CY + R * 0.66} Z" fill="{PRIMARY}" fill-opacity="0.18">
      <animateTransform attributeName="transform" type="rotate" from="0 {CX} {CY}" to="360 {CX} {CY}" dur="6s" repeatCount="indefinite"/>
    </path>
    <circle cx="{CX}" cy="{CY}" r="3.5" fill="{PRIMARY}">
      <animate attributeName="opacity" values="1;0.3;1" dur="1.6s" repeatCount="indefinite"/>
    </circle>
    <circle cx="{CX - 45}" cy="{CY - 55}" r="3" fill="{PRIMARY}">
      <animate attributeName="opacity" values="0.2;1;0.2" dur="2.4s" repeatCount="indefinite"/>
    </circle>
    <circle cx="{CX + 70}" cy="{CY + 40}" r="2.5" fill="{AMBER}">
      <animate attributeName="opacity" values="1;0.15;1" dur="3.1s" repeatCount="indefinite"/>
    </circle>
    <text x="{CX}" y="{CY + 90}" text-anchor="middle" font-size="11" fill="{MUTED}">SCANNING...</text>
  </g>

  <!-- Metrics -->
  <g>
    {metric("PUBLIC REPOS", str(public_repos), 120)}
    {metric("TOTAL STARS", str(stars), 150)}
    {metric("FOLLOWERS", str(followers), 180)}
    {metric("TOP LANGUAGES", top_langs[:32], 210)}
    {metric("ACTIVE IN 30D", str(active_30d), 240)}
    {metric("ACCOUNT SINCE", joined_year, 270)}
  </g>

  <!-- Status line -->
  <text x="34" y="340" font-size="13" fill="{MUTED}">[ OK ] BACKEND SERVICES</text>
  <text x="290" y="340" font-size="13" fill="{MUTED}">[ OK ] MQTT TELEMETRY</text>
  <text x="546" y="340" font-size="13" fill="{MUTED}">[ OK ] CI/CD</text>
  <text x="34" y="368" font-size="13" fill="{MUTED}">[ OK ] EDGE DEVICES</text>
  <text x="290" y="368" font-size="13" fill="{MUTED}">[ OK ] OBSERVABILITY</text>
  <text x="546" y="368" font-size="13" fill="{MUTED}">[ OK ] ISO 27001</text>
  <line x1="34" y1="386" x2="{W - 34}" y2="386" stroke="{PRIMARY}" stroke-opacity="0.25"/>
  <text x="34" y="406" font-size="11" fill="{MUTED}">GENERATED {generated}</text>
  <text x="{W - 34}" y="406" text-anchor="end" font-size="11" fill="{PRIMARY}">SIGNAL ROOM // END OF TRANSMISSION</text>
</svg>
"""
    os.makedirs("assets", exist_ok=True)
    with open("assets/signal-room.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"OK: assets/signal-room.svg generado ({len(svg)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
