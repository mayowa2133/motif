#!/usr/bin/env python3
"""Assemble the approved Motif arena and canonical Bot into Demo 02."""

from __future__ import annotations

import json
import re
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_motif_bot import DEFS as BOT_DEFS, assemble_pose  # noqa: E402
from build_scene_01 import DEFS  # noqa: E402

PROJECT = ROOT / "videos/motif-arena-reel"
SPEC = json.loads((PROJECT / "story-revision-events.json").read_text())
MEDIA = json.loads((PROJECT / "audio-plan.json").read_text())
ARENA = json.loads((ROOT / "scenes/scene-02/scene-02.json").read_text())


def fragment(source: str) -> str:
    svg = (ROOT / source).read_text()
    return svg.split("</defs>", 1)[-1].rsplit("</svg>", 1)[0].strip()


def piece(asset: dict) -> str:
    slug = asset["id"].removeprefix("scene-02-")
    x, y = asset["placement"].values()
    body = fragment(asset["source"])
    if slug == "evaluation-board":
        # The approved board drawing stays intact. Its built-in arrow is a
        # separate reveal layer, so the winner is not indicated before checks.
        before, arrow = body.rsplit('<path d="M106 132', 1)
        body = before + '<g id="a-board-arrow" opacity="0"><path d="M106 132' + arrow + '</g>'
    return (f'<g transform="translate({x} {y})"><g id="a-{slug}" '
            f'data-source="{asset["source"]}" class="motion-asset" '
            f'data-layout-allow-overflow>{body}</g></g>')


def bot(name: str, base: str, face: str, overrides: dict) -> str:
    body, _ = assemble_pose(base, face, overrides)
    body = re.sub(r'id="([^"]+)"', lambda m: f'id="{name}-{m.group(1)}"', body)
    return f'<g id="{name}" class="bot-pose">{body}</g>'


def paper_sign(id_: str, title: str, size: int = 66) -> str:
    y = 72
    return f'''<g id="{id_}" class="paper-type" data-layout-allow-overflow>
      <path d="M123 {y+8} Q541 {y-1} 958 {y+8} L951 {y+113} Q549 {y+122} 127 {y+111} Z" fill="#202C32" opacity=".22" transform="translate(7 10)"/>
      <path d="M123 {y+8} Q541 {y-1} 958 {y+8} L951 {y+113} Q549 {y+122} 127 {y+111} Z" fill="#F4EBD8" stroke="#DCCDB3" stroke-width="5"/>
      <path d="M123 {y+8} Q541 {y-1} 958 {y+8} L951 {y+113} Q549 {y+122} 127 {y+111} Z" fill="url(#paperSpeckle)" opacity=".53"/>
      <text x="540" y="{y+80}" text-anchor="middle" fill="#202C32" font-family="Arial Rounded MT Bold, DejaVu Sans, Arial, sans-serif" font-size="{size}" font-weight="900" letter-spacing="1">{escape(title)}</text>
    </g>'''


def caption(id_: str, title: str, emphasis: str = "", color: str = "teal", y: int = 1660) -> str:
    width = min(790, max(330, 90 + len(title) * 29))
    left, right = 540 - width / 2, 540 + width / 2
    accent = {"teal": "#318E85", "coral": "#C66355", "blue": "#64869A"}.get(color, "#318E85")
    if emphasis and emphasis.lower() in title.lower():
        i = title.lower().index(emphasis.lower())
        label = (escape(title[:i]) + f'<tspan fill="{accent}">'
                 + escape(title[i:i + len(emphasis)]) + '</tspan>'
                 + escape(title[i + len(emphasis):]))
    else:
        label = escape(title)
    return f'''<g id="{id_}" class="paper-type caption-card" data-layout-allow-overflow>
      <path d="M{left+19:.1f} {y+6} Q540 {y-2} {right-10:.1f} {y+6} L{right-13:.1f} {y+107} Q540 {y+115} {left+6:.1f} {y+106} Z" fill="#202C32" opacity=".25" transform="translate(6 9)"/>
      <path d="M{left+19:.1f} {y+6} Q540 {y-2} {right-10:.1f} {y+6} L{right-13:.1f} {y+107} Q540 {y+115} {left+6:.1f} {y+106} Z" fill="#F4EBD8" stroke="#DCCDB3" stroke-width="4"/>
      <path d="M{left+19:.1f} {y+6} Q540 {y-2} {right-10:.1f} {y+6} L{right-13:.1f} {y+107} Q540 {y+115} {left+6:.1f} {y+106} Z" fill="url(#paperSpeckle)" opacity=".45"/>
      <text x="540" y="{y+77}" text-anchor="middle" fill="#202C32" font-family="Arial Rounded MT Bold, DejaVu Sans, Arial, sans-serif" font-size="58" font-weight="800">{label}</text>
    </g>'''


def paper_tag(id_: str, x: int, y: int, title: str, ink: str, width: int = 230) -> str:
    return f'''<g id="{id_}" class="motion-asset" data-layout-allow-overflow>
      <path d="M{x+9} {y+7} Q{x+width//2} {y-1} {x+width-9} {y+7} L{x+width-5} {y+88} Q{x+width//2} {y+96} {x+6} {y+87} Z" fill="#202C32" opacity=".22" transform="translate(6 8)"/>
      <path d="M{x+9} {y+7} Q{x+width//2} {y-1} {x+width-9} {y+7} L{x+width-5} {y+88} Q{x+width//2} {y+96} {x+6} {y+87} Z" fill="#F4EBD8" stroke="#DCCDB3" stroke-width="4"/>
      <path d="M{x+9} {y+7} Q{x+width//2} {y-1} {x+width-9} {y+7} L{x+width-5} {y+88} Q{x+width//2} {y+96} {x+6} {y+87} Z" fill="url(#paperSpeckle)" opacity=".5"/>
      <text x="{x+width//2}" y="{y+65}" text-anchor="middle" fill="{ink}" font-family="Arial Rounded MT Bold, DejaVu Sans, Arial, sans-serif" font-size="37" font-weight="900">{escape(title)}</text>
    </g>'''


ANSWER_SHEET = "assets/scenes/scene-02/story/answer-sheet.svg"
STENCIL = "assets/scenes/scene-02/story/link-test-stencil.svg"
LENS = "assets/scenes/scene-02/story/inspection-lens.svg"
INCOMING_TICKET = "assets/scenes/scene-03/workflow/incoming-code-sheet.svg"
WALL = "assets/scenes/scene-02/environment/arena-wall.svg"
FLOOR = "assets/scenes/scene-02/environment/arena-floor.svg"
STAGE = "assets/scenes/scene-02/furniture/arena-stage.svg"


def close_shot(letter: str, complete: bool) -> str:
    key = letter.lower()
    ink = "#318E85" if complete else "#64869A"
    route = (
        '<path d="M352 965 H734" fill="none" stroke="#318E85" stroke-width="33" stroke-linecap="round"/>'
        '<path d="M490 965 H594" fill="none" stroke="#A6E5D6" stroke-width="14" stroke-linecap="round"/>'
        if complete else
        '<path d="M352 965 H474 M612 965 H734" fill="none" stroke="#64869A" stroke-width="33" stroke-linecap="round"/>'
        '<path d="M495 933 L595 933 L595 997 L495 997 Z" fill="none" stroke="#C66355" stroke-width="8" stroke-dasharray="13 12" stroke-linejoin="round"/>'
    )
    emphasis = (
        f'<g id="{key}-result" opacity="0"><circle cx="545" cy="965" r="76" fill="#A6E5D6" opacity=".22"/>'
        '<path d="M515 964 l21 22 42 -48" fill="none" stroke="#318E85" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/></g>'
        if complete else
        f'<g id="{key}-result" opacity="0"><circle cx="545" cy="965" r="77" fill="#C66355" opacity=".12" stroke="#C66355" stroke-width="8"/>'
        '<path d="M523 944 l44 44 M567 944 l-44 44" fill="none" stroke="#C66355" stroke-width="13" stroke-linecap="round"/></g>'
    )
    return f'''<g id="shot-{key}" class="shot" data-layout-allow-overflow>
      <g>{fragment(WALL)}</g><g transform="translate(0 1430)">{fragment(FLOOR)}</g>
      <g transform="translate(90 1380)">{fragment(STAGE)}</g>
      {paper_sign(f'{key}-title', f'ANSWER {letter}', 72)}
      <g transform="translate(160 390)">{fragment(ANSWER_SHEET)}</g>
      <g transform="translate(705 469) rotate(7) scale(.92)">{fragment(INCOMING_TICKET)}</g>
      <circle cx="261" cy="486" r="60" fill="{ink}" stroke="#725343" stroke-width="7"/>
      <text x="261" y="510" text-anchor="middle" fill="#F4EBD8" font-family="DejaVu Sans, Arial" font-size="70" font-weight="800">{letter}</text>
      <g fill="none" stroke="#318E85" stroke-width="14" stroke-linecap="round" stroke-linejoin="round">
        <path d="M762 575 l17 16 31 -38"/><path d="M762 635 l17 16 31 -38"/>
      </g>
      <g transform="translate(210 828)"><g id="{key}-stencil" class="motion-asset" data-layout-allow-overflow>{fragment(STENCIL)}</g></g>
      <g id="{key}-path" data-layout-allow-overflow opacity="0">
        <circle cx="303" cy="965" r="30" fill="#F4EBD8" stroke="{ink}" stroke-width="14"/>
        <circle cx="776" cy="965" r="30" fill="#F4EBD8" stroke="{ink}" stroke-width="14"/>
        {route}
      </g>
      {emphasis}
    </g>'''


wide_assets = [a for a in ARENA["assets"] if a["id"] not in {
    "scene-02-podium", "scene-02-winner-seal", "scene-02-paper-confetti"
}]
wide_layers = {
    layer: "\n".join(piece(a) for a in wide_assets if a["layer"] == layer)
    for layer in ("background", "midground", "character", "foreground", "ui")
}
wide_bot = bot("wide-bot", "presenting", "proud",
               {"l": (225, 510, "open"), "r": (795, 508, "open"), "head_tilt": -4})
review_bot_present = bot("review-bot-present", "presenting", "proud",
                         {"l": (225, 510, "open"), "r": (795, 508, "open"), "head_tilt": -4})
review_bot_think = bot("review-bot-think", "presenting", "thinking",
                       {"l": (225, 510, "open"), "r": (795, 508, "open"), "head_tilt": 5})
captions = "".join(
    caption(f"caption-{i}", c["text"], c.get("emphasis", ""), c.get("color", "teal"))
    for i, c in enumerate(SPEC["captions"])
)
review_shot = f'''<g id="shot-review" class="shot" data-layout-allow-overflow>
  <g>{fragment(WALL)}</g><g transform="translate(0 1430)">{fragment(FLOOR)}</g>
  <g transform="translate(90 1410)">{fragment(STAGE)}</g>
  {paper_sign("review-title", "B SELECTED", 72)}
  <g transform="translate(30 700) scale(.62)"><g id="review-bot-motion">{review_bot_present}{review_bot_think}</g></g>
  <g id="selected-sheet" class="motion-asset" data-layout-allow-overflow>
    <g transform="translate(700 755) scale(.52)">{fragment(ANSWER_SHEET)}</g>
    <g transform="translate(788 829) scale(.48)">
      <circle cx="93" cy="137" r="42" fill="#F4EBD8" stroke="#318E85" stroke-width="12"/>
      <circle cx="566" cy="137" r="42" fill="#F4EBD8" stroke="#318E85" stroke-width="12"/>
      <path d="M140 137 H520" fill="none" stroke="#318E85" stroke-width="28" stroke-linecap="round"/>
    </g>
    <path d="M842 741 l52 14 -15 110 -24 -21 -33 16 Z" fill="#318E85" stroke="#276F69" stroke-width="5"/>
    <text x="826" y="815" fill="#202C32" font-family="DejaVu Sans, Arial" font-size="53" font-weight="900" text-anchor="middle">B</text>
  </g>
  <g transform="translate(652 1070) scale(.9)"><g id="review-lens" class="motion-asset" data-layout-allow-overflow>{fragment(LENS)}</g></g>
</g>'''
wide = f'''<g id="shot-wide" class="shot" data-layout-allow-overflow>
  {wide_layers['background']}{wide_layers['midground']}
  <g transform="translate(15 1080) scale(.31)">{wide_bot}</g>
  {wide_layers['character']}{wide_layers['foreground']}{wide_layers['ui']}
  {paper_sign("wide-title", "THREE ANSWERS", 66)}
</g>'''
spec_literal = json.dumps(SPEC, separators=(",", ":")).replace("</", "<\\/")
audio_markup = "\n".join(
    f'<audio id="audio-{escape(t["id"])}" src="{escape(t["file"])}" '
    f'data-start="{t["start"]}" data-duration="{t["duration"]}" '
    f'data-volume="{t["volume"]}" data-track-index="{t["lane"]}" '
    f'data-audio-group="{escape(t["group"])}"></audio>' for t in MEDIA["tracks"]
)
html = f'''<!doctype html>
<html lang="en" data-resolution="portrait">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=1080,height=1920" />
  <title>Motif Demo 02 · Matched answer test</title>
  <script src="assets/gsap.min.js"></script>
  <script src="assets/motion-primitives.js"></script>
  <script src="assets/motion-engine.js"></script>
  <style>
    * {{ box-sizing:border-box; }}
    html,body {{ margin:0; width:1080px; height:1920px; overflow:hidden; background:#B99173; }}
    #root,#scene {{ width:1080px; height:1920px; overflow:hidden; display:block; }}
    .motion-asset,.bot-pose,.paper-type {{ transform-box:fill-box; transform-origin:center; }}
  </style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{SPEC['durationSec']}" data-width="1080" data-height="1920">
  <svg id="scene" class="clip" data-start="0" data-duration="{SPEC['durationSec']}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1920" aria-label="Three answers enter an arena. The same paper connection test exposes a gap in A and a complete link in B; Motif Bot receives B for review.">
    <defs>{DEFS}{BOT_DEFS}</defs>
    {wide}
    {close_shot("A", False)}
    {close_shot("B", True)}
    {review_shot}
    {captions}
  </svg>
  {audio_markup}
</div>
<script id="motif-scene-events" type="application/json">{spec_literal}</script>
<script>
  window.__timelines = window.__timelines || {{}};
  window.MotifEventEngine.compile(JSON.parse(document.getElementById('motif-scene-events').textContent), 'main');
</script>
</body>
</html>
'''
(PROJECT / "index.html").write_text(html)
print(PROJECT / "index.html")
