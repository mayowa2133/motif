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
SPEC = json.loads((PROJECT / "scene-events.json").read_text())
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


layers = {layer: "\n".join(piece(a) for a in ARENA["assets"] if a["layer"] == layer)
          for layer in ("background", "midground", "character", "foreground", "ui")}
bot_poses = "".join([
    bot("a-bot-neutral", "standing", "thinking", {"head_tilt": 2}),
    bot("a-bot-point", "pointing", "determined",
        {"l": (225, 510, "open"), "r": (795, 508, "point"), "head_tilt": -4}),
    bot("a-bot-react", "presenting", "shocked", {"head_tilt": 5}),
    bot("a-bot-present", "presenting", "proud",
        {"l": (225, 510, "open"), "r": (795, 508, "open"), "head_tilt": -4}),
])
headlines = "".join([
    paper_sign("headline-intro", "THREE ANSWERS"),
    paper_sign("headline-check", "CHECK THE ANSWERS", 60),
    paper_sign("headline-selected", "B SELECTED"),
])
captions = "".join(caption(f"caption-{i}", c["text"], c.get("emphasis", ""), c.get("color", "teal"))
                   for i, c in enumerate(SPEC["captions"]))
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
  <title>Motif Demo 02 · Answer trials</title>
  <script src="assets/gsap.min.js"></script>
  <script src="assets/motion-primitives.js"></script>
  <script src="assets/motion-engine.js"></script>
  <style>
    * {{ box-sizing:border-box; }}
    html,body {{ margin:0; width:1080px; height:1920px; overflow:hidden; background:#B99173; }}
    #root,#scene {{ width:1080px; height:1920px; overflow:hidden; display:block; }}
    .motion-asset,.bot-pose,.paper-type {{ transform-box:fill-box; transform-origin:center; }}
    #arena-camera {{ transform-box:view-box; transform-origin:540px 1000px; }}
  </style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{SPEC['durationSec']}" data-width="1080" data-height="1920">
  <svg id="scene" class="clip" data-start="0" data-duration="{SPEC['durationSec']}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1920" aria-label="Three agent answers enter an arena; A fails a check, B performs better and is selected for review">
    <defs>{DEFS}{BOT_DEFS}</defs>
    <g id="arena-scene" data-layout-allow-overflow>
      <g id="arena-camera" data-layout-allow-overflow>
        {layers['background']}
        {layers['midground']}
        <g id="a-scan-A" class="motion-asset" opacity="0"><path d="M319 819 Q386 811 451 819 L451 880 Q388 888 319 880 Z" fill="#EBC46B" opacity=".55"/></g>
        <g id="a-scan-B" class="motion-asset" opacity="0"><path d="M494 819 Q559 811 625 819 L625 880 Q560 888 494 880 Z" fill="#A6E5D6" opacity=".62"/></g>
        <g transform="translate(15 1080) scale(.31)"><g id="a-bot-motion">{bot_poses}</g></g>
        {layers['character']}
        {layers['foreground']}
        {layers['ui']}
        <g id="a-mark-A" class="motion-asset" data-layout-allow-overflow><circle cx="420" cy="875" r="42" fill="#F4EBD8" stroke="#C66355" stroke-width="7"/><path d="M402 857 l36 36 M438 857 l-36 36" fill="none" stroke="#C66355" stroke-width="11" stroke-linecap="round"/></g>
        <g id="a-mark-B" class="motion-asset" data-layout-allow-overflow><circle cx="600" cy="875" r="42" fill="#F4EBD8" stroke="#318E85" stroke-width="7"/><path d="M580 874 l15 16 28 -33" fill="none" stroke="#318E85" stroke-width="11" stroke-linecap="round" stroke-linejoin="round"/></g>
        {paper_tag('a-promising-tag', 218, 949, 'PROMISING?', '#64869A', 290)}
        {paper_tag('a-flaw-tag', 257, 949, 'FLAW', '#C66355', 230)}
        {paper_tag('a-pass-tag', 625, 932, 'PASSES', '#318E85', 225)}
      </g>
    </g>
    {headlines}
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
