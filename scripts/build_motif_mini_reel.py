#!/usr/bin/env python3
"""Assemble approved Motif assets into the event-driven mini Reel composition."""

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

PROJECT = ROOT / "videos/motif-mini-reel"
SPEC = json.loads((PROJECT / "scene-events.json").read_text())
MEDIA = json.loads((PROJECT / "audio-plan.json").read_text()) if (PROJECT / "audio-plan.json").exists() else {"tracks": []}
NIGHT = json.loads((ROOT / "scenes/scene-01/scene-01.json").read_text())
FACTORY = json.loads((ROOT / "scenes/scene-03/scene-03.json").read_text())


def fragment(source: str) -> str:
    svg = (ROOT / source).read_text()
    return svg.split("</defs>", 1)[-1].rsplit("</svg>", 1)[0].strip()


def piece(asset: dict, prefix: str) -> str:
    slug = asset["id"].removeprefix("scene-01-").removeprefix("scene-03-")
    x, y = asset["placement"].values()
    body = fragment(asset["source"])
    if prefix == "f" and slug == "clean-code-sheet":
        # Keep the approved SVG intact; the embedded check is a separate
        # animation layer and appears only after inspection succeeds.
        before, check = body.split('<circle cx="118" cy="87"', 1)
        body = before + '<g id="f-clean-check" class="motion-asset" opacity="0"><circle cx="118" cy="87"' + check + '</g>'
    return (f'<g transform="translate({x} {y})"><g id="{prefix}-{slug}" '
            f'data-source="{asset["source"]}" class="motion-asset" '
            f'data-layout-allow-overflow>{body}</g></g>')


def bot(name: str, base: str, face: str, overrides: dict) -> str:
    body, _ = assemble_pose(base, face, overrides)
    body = re.sub(r'id="([^"]+)"', lambda m: f'id="{name}-{m.group(1)}"', body)
    return f'<g id="{name}" class="bot-pose">{body}</g>'


def paper_sign(id_: str, y: int, title: str, size: int = 68) -> str:
    return f'''<g id="{id_}" class="paper-type" data-layout-allow-overflow>
      <path d="M123 {y+8} Q541 {y-1} 958 {y+8} L951 {y+113} Q549 {y+122} 127 {y+111} Z" fill="#202C32" opacity=".22" transform="translate(7 10)"/>
      <path d="M123 {y+8} Q541 {y-1} 958 {y+8} L951 {y+113} Q549 {y+122} 127 {y+111} Z" fill="#F4EBD8" stroke="#DCCDB3" stroke-width="5"/>
      <path d="M123 {y+8} Q541 {y-1} 958 {y+8} L951 {y+113} Q549 {y+122} 127 {y+111} Z" fill="url(#paperSpeckle)" opacity=".53"/>
      <text x="540" y="{y+80}" text-anchor="middle" fill="#202C32" font-family="Arial Rounded MT Bold, DejaVu Sans, Arial, sans-serif" font-size="{size}" font-weight="900" letter-spacing="1">{escape(title)}</text>
    </g>'''


def caption(id_: str, title: str, emphasis: str = "", color: str = "teal", y: int = 1660) -> str:
    width = min(790, max(330, 90 + len(title) * 29))
    left, right = 540 - width / 2, 540 + width / 2
    accent = {"teal": "#318E85", "coral": "#C66355"}.get(color, "#318E85")
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


night_assets = {a["id"].removeprefix("scene-01-"): a for a in NIGHT["assets"]}
factory_assets = {a["id"].removeprefix("scene-03-"): a for a in FACTORY["assets"]}

night_layers = {
    layer: "\n".join(piece(a, "d") for a in NIGHT["assets"] if a["layer"] == layer)
    for layer in ("background", "midground", "foreground", "ui")
}
factory_layers = {
    layer: "\n".join(piece(a, "f") for a in FACTORY["assets"] if a["layer"] == layer)
    for layer in ("background", "midground", "foreground", "character", "ui")
}
morning_layers = {
    layer: "\n".join(piece(a, "m") for a in NIGHT["assets"]
                     if a["layer"] == layer and
                     a["id"] not in {"scene-01-night-sky-moon", "scene-01-late-night-clock", "scene-01-document"})
    for layer in ("background", "midground", "foreground", "ui")
}
morning_sky = (f'<g transform="translate(132 398)"><g id="m-day-sky" class="motion-asset" '
               f'data-source="videos/motif-mini-reel/assets/day-sky-variation.svg">'
               f'{fragment("videos/motif-mini-reel/assets/day-sky-variation.svg")}</g></g>')
morning_report = fragment(night_assets["document"]["source"]).replace(">NOTES</text>", ">RESULTS</text>")

night_bot = "".join([
    bot("d-bot-point", "pointing", "determined",
        {"l": (390, 669, "mitten"), "r": (824, 535, "point"), "head_tilt": -4}),
    bot("d-bot-thinking", "standing", "thinking", {"head_tilt": 3}),
])
factory_bot = "".join([
    bot("f-bot-idle", "standing", "thinking", {"head_tilt": -4}),
    bot("f-bot-point", "pointing", "determined",
        {"l": (278, 670, "mitten"), "r": (825, 523, "point"), "head_tilt": -3}),
    bot("f-bot-react", "presenting", "shocked", {"head_tilt": 4}),
    bot("f-bot-celebrate", "celebrating", "excited", {"head_tilt": -2}),
])
morning_bot = bot("m-bot-present", "pointing", "excited",
                  {"l": (390, 669, "mitten"), "r": (824, 535, "point"), "head_tilt": -4})

headlines = "".join([
    paper_sign("headline-night", 72, "WHILE YOU SLEEP", 66),
    paper_sign("headline-bug", 72, "CODE INSPECTION", 66),
    paper_sign("headline-pass", 72, "CHECKS PASSED", 66),
    paper_sign("headline-morning", 72, "READY BY MORNING", 62),
])
captions = "".join(caption(f"caption-{i}", item["text"], item.get("emphasis", ""), item.get("color", "teal"))
                   for i, item in enumerate(SPEC["captions"]))

spec_literal = json.dumps(SPEC, separators=(",", ":")).replace("</", "<\\/")
duration = SPEC["durationSec"]
audio_markup = "\n".join(
    f'<audio id="audio-{escape(track["id"])}" src="{escape(track["file"])}" '
    f'data-start="{track["start"]}" data-duration="{track["duration"]}" '
    f'data-volume="{track["volume"]}" data-track-index="{track["lane"]}" '
    f'data-audio-group="{escape(track["group"])}"></audio>'
    for track in MEDIA["tracks"]
)
html = f'''<!doctype html>
<html lang="en" data-resolution="portrait">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=1080,height=1920" />
  <title>Motif · AI agents inspect code</title>
  <script src="assets/gsap.min.js"></script>
  <script src="assets/motion-primitives.js"></script>
  <script src="assets/motion-engine.js"></script>
  <style>
    * {{ box-sizing:border-box; }}
    html,body {{ margin:0; width:1080px; height:1920px; overflow:hidden; background:#62546A; }}
    #root,#scene {{ width:1080px; height:1920px; overflow:hidden; display:block; }}
    .motion-asset,.bot-pose,.paper-type {{ transform-box:fill-box; transform-origin:center; }}
    #d-camera,#f-camera,#m-camera {{ transform-box:view-box; transform-origin:540px 1000px; }}
    #d-paper-cover {{ transform-box:fill-box; transform-origin:center; }}
  </style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{duration}" data-width="1080" data-height="1920">
  <svg id="scene" class="clip" data-start="0" data-duration="{duration}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1920" aria-label="Motif Bot works through the night, catches a bug, then presents results at a daylight desk">
    <defs>{DEFS}{BOT_DEFS}</defs>
    <g id="d-scene" data-layout-allow-overflow>
      <g id="d-camera" data-layout-allow-overflow>
        {night_layers['background']}
        {night_layers['midground']}
        <g transform="translate(264 854) scale(.43)"><g id="d-bot-motion">{night_bot}</g></g>
        {night_layers['foreground']}
        {night_layers['ui']}
        <g id="d-screen-glow" opacity="0"><path d="M651 916 Q803 910 905 925 L899 1010 Q780 1030 660 1015 Z" fill="#A6E5D6" opacity=".19"/></g>
      </g>
    </g>
    <g id="m-scene" data-layout-allow-overflow>
      <g id="m-camera" data-layout-allow-overflow>
        {morning_layers['background']}
        {morning_sky}
        {morning_layers['midground']}
        <g transform="translate(264 854) scale(.43)"><g id="m-bot-motion">{morning_bot}</g></g>
        {morning_layers['foreground']}
        <g transform="translate(510 1090) scale(1.8)"><g id="m-report" class="motion-asset" data-source="assets/scenes/scene-01/desk-props/document.svg">{morning_report}</g></g>
        {morning_layers['ui']}
      </g>
    </g>
    <g id="f-scene" data-layout-allow-overflow>
      <g id="f-camera" data-layout-allow-overflow>
        {factory_layers['background']}
        {factory_layers['midground']}
        <g id="f-belt-ticks" opacity=".5"><path d="M129 1268 H949" fill="none" stroke="#DCCDB3" stroke-width="6" stroke-linecap="round" stroke-dasharray="18 58"/></g>
        <g id="f-warning" opacity="0"><path d="M430 850 Q548 839 680 858 L681 1240 Q552 1258 432 1237 Z" fill="#DF806B" opacity=".33"/></g>
        {factory_layers['foreground']}
        {factory_layers['character']}
        <g transform="translate(0 1100) scale(.35)"><g id="f-bot-motion">{factory_bot}</g></g>
        {factory_layers['ui']}
        <g id="f-pass-check" opacity="0"><circle cx="970" cy="1000" r="52" fill="#318E85" stroke="#F4EBD8" stroke-width="9"/><path d="M944 1002 l19 18 33 -40" fill="none" stroke="#F4EBD8" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/></g>
      </g>
    </g>
    <g id="d-paper-cover" opacity="0" transform="translate(426 1161)" data-layout-allow-overflow>{fragment(night_assets['document']['source'])}</g>
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
