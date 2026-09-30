#!/usr/bin/env python3
"""Assemble Demo 03 from Motif's locked Bot, approved world pieces, and calendar props."""

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

PROJECT = ROOT / "videos/motif-calendar-reel"
SPEC = json.loads((PROJECT / "scene-events.json").read_text())
MEDIA = json.loads((PROJECT / "audio-plan.json").read_text())


def fragment(source: str) -> str:
    raw = (ROOT / source).read_text()
    body = raw.split("</defs>", 1)[-1]
    body = re.sub(r"^\s*<svg[^>]*>\s*(?:<title>.*?</title>\s*)?", "", body, flags=re.S)
    return body.rsplit("</svg>", 1)[0].strip()


def bot(name: str, base: str, face: str, overrides: dict) -> str:
    body, _ = assemble_pose(base, face, overrides)
    body = re.sub(r'id="([^"]+)"', lambda match: f'id="{name}-{match.group(1)}"', body)
    return f'<g id="{name}" class="bot-pose">{body}</g>'


def sign(id_: str, title: str, size: int = 57) -> str:
    label = escape(title)
    return f'''<g id="{id_}" class="paper-type" data-layout-allow-overflow>
      <path d="M104 83 Q539 70 977 83 L971 201 Q540 211 109 198 Z" transform="translate(8 11)" fill="#202C32" opacity=".22"/>
      <path d="M104 83 Q539 70 977 83 L971 201 Q540 211 109 198 Z" fill="#F4EBD8" stroke="#DCCDB3" stroke-width="5"/>
      <path d="M104 83 Q539 70 977 83 L971 201 Q540 211 109 198 Z" fill="url(#paperSpeckle)" opacity=".52"/>
      <text x="540" y="165" text-anchor="middle" fill="#202C32" font-family="Arial Rounded MT Bold, DejaVu Sans, Arial, sans-serif" font-size="{size}" font-weight="900" letter-spacing=".7">{label}</text>
    </g>'''


def caption(id_: str, title: str, emphasis: str = "", color: str = "teal", y: int = 1660) -> str:
    width = min(825, max(350, 100 + len(title) * 29))
    left, right = 540 - width / 2, 540 + width / 2
    accent = {"teal": "#318E85", "coral": "#C66355", "blue": "#64869A"}.get(color, "#318E85")
    if emphasis and emphasis.lower() in title.lower():
        at = title.lower().index(emphasis.lower())
        label = escape(title[:at]) + f'<tspan fill="{accent}">' + escape(title[at:at+len(emphasis)]) + '</tspan>' + escape(title[at+len(emphasis):])
    else:
        label = escape(title)
    return f'''<g id="{id_}" class="paper-type caption-card" data-layout-allow-overflow>
      <path d="M{left+19:.1f} {y+6} Q540 {y-2} {right-10:.1f} {y+6} L{right-13:.1f} {y+107} Q540 {y+115} {left+6:.1f} {y+106} Z" fill="#202C32" opacity=".25" transform="translate(6 9)"/>
      <path d="M{left+19:.1f} {y+6} Q540 {y-2} {right-10:.1f} {y+6} L{right-13:.1f} {y+107} Q540 {y+115} {left+6:.1f} {y+106} Z" fill="#F4EBD8" stroke="#DCCDB3" stroke-width="4"/>
      <path d="M{left+19:.1f} {y+6} Q540 {y-2} {right-10:.1f} {y+6} L{right-13:.1f} {y+107} Q540 {y+115} {left+6:.1f} {y+106} Z" fill="url(#paperSpeckle)" opacity=".45"/>
      <text x="540" y="{y+77}" text-anchor="middle" fill="#202C32" font-family="Arial Rounded MT Bold, DejaVu Sans, Arial, sans-serif" font-size="58" font-weight="800">{label}</text>
    </g>'''


def appointment(id_: str, x: int, y: int, title: str, color: str) -> str:
    body = fragment("assets/scenes/demo-03/appointment-card.svg")
    return f'''<g transform="translate({x} {y}) scale(.85)"><g id="{id_}" class="motion-asset" data-layout-allow-overflow>
      {body}
      <path d="M21 15 Q35 13 50 13 L48 151 Q30 153 14 151 Z" fill="{color}" opacity=".95"/>
      <text x="74" y="88" fill="#202C32" font-family="Arial Rounded MT Bold, DejaVu Sans, Arial, sans-serif" font-size="54" font-weight="900">{escape(title)}</text>
    </g></g>'''


bot_poses = "".join([
    bot("bot-neutral", "standing", "neutral", {"head_tilt": 2}),
    bot("bot-notice", "pointing", "confused", {"l": (245, 590, "open"), "r": (850, 450, "point"), "head_tilt": -5}),
    bot("bot-wait", "presenting", "thinking", {"l": (230, 525, "open"), "r": (790, 525, "open"), "head_tilt": 3}),
    bot("bot-happy", "presenting", "happy", {"l": (225, 510, "open"), "r": (795, 508, "open"), "head_tilt": -4}),
])

world = f'''<g id="world-camera" data-layout-allow-overflow>
  <g id="warm-wall">{fragment('assets/scenes/scene-02/environment/arena-wall.svg')}</g>
  <g transform="translate(0 1430)">{fragment('assets/scenes/scene-01/environment/floor.svg')}</g>
  <g transform="translate(70 1390)">{fragment('assets/scenes/scene-01/furniture/desk.svg')}</g>
  <g transform="translate(120 315)">{fragment('assets/scenes/demo-03/calendar-board.svg')}</g>
  {appointment('call-card', 380, 625, 'CALL', '#318E85')}
  {appointment('focus-card', 590, 665, 'FOCUS', '#C66355')}
  <g id="overlap-bracket" class="motion-asset" data-layout-allow-overflow>
    <path d="M488 599 h-34 q-11 0 -11 12 v192 q0 12 11 12 h34 M913 599 h31 q11 0 11 12 v192 q0 12 -11 12 h-31" fill="none" stroke="#C66355" stroke-width="15" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M698 835 l15 18 15 -18" fill="none" stroke="#C66355" stroke-width="12" stroke-linecap="round"/>
  </g>
  <g id="proposal-route" data-layout-allow-overflow>
    <path d="M918 775 C997 815 989 907 920 997" fill="none" stroke="#318E85" stroke-width="12" stroke-linecap="round" stroke-dasharray="20 18"/>
    <path d="M895 989 l24 21 19 -27" fill="none" stroke="#318E85" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>
  </g>
  <g transform="translate(590 975) scale(.85)"><g id="proposal-slip" class="motion-asset" data-layout-allow-overflow>
    {fragment('assets/scenes/demo-03/proposal-slip.svg')}
    <text x="74" y="89" fill="#318E85" opacity=".8" font-family="Arial Rounded MT Bold, DejaVu Sans, Arial, sans-serif" font-size="52" font-weight="900">FOCUS</text>
  </g></g>
  <g transform="translate(120 1135) scale(.38)"><g id="bot-motion">{bot_poses}</g></g>
  <g transform="translate(613 1238)"><g id="approval-tab" class="motion-asset" data-layout-allow-overflow>{fragment('assets/scenes/demo-03/approval-tab.svg')}</g></g>
  <g id="approval-glow" class="motion-asset" data-layout-allow-overflow><circle cx="785" cy="1324" r="138" fill="#A6E5D6" opacity=".26" stroke="#318E85" stroke-width="10"/></g>
  <g transform="translate(690 1160)"><g id="human-finger" class="motion-asset" data-layout-allow-overflow>{fragment('assets/scenes/demo-03/human-fingertip.svg')}</g></g>
</g>'''
headlines = "".join([
    sign("headline-intro", "TWO PLANS. ONE TIME.", 58),
    sign("headline-propose", "A TIME TO TRY", 66),
    sign("headline-wait", "YOUR APPROVAL", 66),
    sign("headline-done", "THEN IT MOVES", 66),
])
captions = "".join(caption(f"caption-{i}", item["text"], item.get("emphasis", ""), item.get("color", "teal")) for i, item in enumerate(SPEC["captions"]))
spec_literal = json.dumps(SPEC, separators=(",", ":")).replace("</", "<\\/")
audio_markup = "\n".join(
    f'<audio id="audio-{escape(t["id"])}" src="{escape(t["file"])}" data-start="{t["start"]}" data-duration="{t["duration"]}" data-volume="{t["volume"]}" data-track-index="{t["lane"]}" data-audio-group="{escape(t["group"])}"></audio>'
    for t in MEDIA["tracks"]
)

html = f'''<!doctype html>
<html lang="en" data-resolution="portrait">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=1080,height=1920" />
  <title>Motif Demo 03 · Permission before the calendar moves</title>
  <script src="assets/gsap.min.js"></script>
  <script src="assets/motion-primitives.js"></script>
  <script src="assets/motion-engine.js"></script>
  <style>
    * {{ box-sizing:border-box; }}
    html,body {{ margin:0; width:1080px; height:1920px; overflow:hidden; background:#B99476; }}
    #root,#scene {{ width:1080px; height:1920px; overflow:hidden; display:block; }}
    .motion-asset,.bot-pose,.paper-type {{ transform-box:fill-box; transform-origin:center; }}
    #world-camera {{ transform-box:view-box; transform-origin:540px 900px; }}
  </style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{SPEC['durationSec']}" data-width="1080" data-height="1920">
  <svg id="scene" class="clip" data-start="0" data-duration="{SPEC['durationSec']}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1920" aria-label="Two commitments collide in a calendar. An assistant proposes a different time, waits for a person to approve, then moves the appointment.">
    <defs>{DEFS}{BOT_DEFS}</defs>
    {world}
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
