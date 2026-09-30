#!/usr/bin/env python3
"""Compile the approved Scene 03 assets and locked mascot poses into a seekable motion composition."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_motif_bot import DEFS as BOT_DEFS, assemble_pose  # noqa: E402
from build_scene_01 import DEFS  # noqa: E402

PROJECT = ROOT / "videos/code-inspection-motion"
MANIFEST = json.loads((ROOT / "scenes/scene-03/scene-03.json").read_text())


def fragment(path: Path) -> str:
    svg = path.read_text()
    return svg.split("</defs>", 1)[-1].rsplit("</svg>", 1)[0].strip()


def piece(asset: dict) -> str:
    slug = asset["id"].removeprefix("scene-03-")
    x, y = asset["placement"].values()
    body = fragment(ROOT / asset["source"])
    return (f'<g data-source="{asset["source"]}" transform="translate({x} {y})">'
            f'<g id="{slug}" class="motion-asset" data-layout-allow-overflow>{body}</g></g>')


def bot_state(name: str, base: str, face: str, overrides: dict | None = None) -> str:
    body, _ = assemble_pose(base, face, overrides)
    # Pose copies share geometry but need unique DOM IDs for direct head animation.
    body = re.sub(r'id="([^"]+)"', lambda m: f'id="{name}-{m.group(1)}"', body)
    return f'<g id="bot-{name}" class="bot-pose">{body}</g>'


assets = {a["id"].removeprefix("scene-03-"): a for a in MANIFEST["assets"]}
back = ["factory-wall", "factory-floor", "wall-pipes", "scan-sign", "quality-gauge",
        "scanner-frame", "scan-beam"]
front = ["conveyor-belt", "incoming-code-sheet", "clean-code-sheet", "caught-bug",
         "paper-grabber", "reject-bin", "pass-stamp"]
background = "\n".join(piece(assets[k]) for k in back)
foreground = "\n".join(piece(assets[k]) for k in front)
bot = "".join([
    bot_state("idle", "standing", "thinking", {"head_tilt": -4}),
    bot_state("point", "pointing", "determined", {"l": (278, 670, "mitten"), "r": (825, 523, "point"), "head_tilt": -3}),
    bot_state("react", "presenting", "shocked", {"head_tilt": 4}),
    bot_state("celebrate", "celebrating", "excited", {"head_tilt": -2}),
])

html = f'''<!doctype html>
<html lang="en" data-resolution="portrait">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=1080,height=1920" />
  <title>Motif Motion Benchmark 01 — Code Inspection</title>
  <script src="assets/gsap.min.js"></script>
  <script src="assets/motion-primitives.js"></script>
  <style>
    * {{ box-sizing: border-box; }}
    html, body {{ margin:0; width:1080px; height:1920px; overflow:hidden; background:#6D8890; }}
    #root, #scene {{ width:1080px; height:1920px; overflow:hidden; }}
    #scene {{ display:block; }}
    .motion-asset, .bot-pose {{ transform-box: fill-box; transform-origin: center; }}
    #world {{ transform-box: view-box; transform-origin: 690px 1090px; }}
  </style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="6.4" data-width="1080" data-height="1920">
    <svg id="scene" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1920" aria-label="Motif Bot inspects two code sheets; a bug is rejected and clean code passes">
      <defs>{DEFS}{BOT_DEFS}</defs>
      <g id="world" data-layout-allow-overflow>
        {background}
        <g id="belt-ticks" opacity=".45"><path d="M129 1268 H949" fill="none" stroke="#DCCDB3" stroke-width="6" stroke-linecap="round" stroke-dasharray="18 58"/></g>
        <g id="warning-flash" opacity="0"><path d="M442 892 Q548 867 669 894 L672 1223 Q556 1241 443 1226 Z" fill="#D87969" opacity=".29"/></g>
        {foreground}
        <g id="bot-placement" transform="translate(0 1100) scale(.35)"><g id="bot-motion">{bot}</g></g>
      </g>
    </svg>
</div>
<script>
  const tl = gsap.timeline({{ paused: true }});
  const M = window.MotifMotion;
  gsap.set('#incoming-code-sheet', {{ x: -520, y: 0, rotation: -5 }});
  gsap.set('#clean-code-sheet', {{ x: -1080, y: 0, rotation: -4 }});
  gsap.set('#caught-bug', {{ scale: 0, opacity: 0, rotation: -8 }});
  gsap.set('#pass-stamp', {{ opacity: 0, y: -190 }});
  gsap.set('#scan-beam', {{ opacity: 0, scaleY: .72 }});
  gsap.set('#paper-grabber', {{ y: -55 }});
  gsap.set('#bot-point, #bot-react, #bot-celebrate', {{ opacity: 0 }});
  tl.to('#belt-ticks path', {{ strokeDashoffset: -430, duration: 6.4, ease: 'none' }}, 0);

  // First sheet: arrive, settle under the machine, expose the literal bug.
  M.SLIDE(tl, '#incoming-code-sheet', .28, {{ fromX: -520, toX: 170, duration: 1.15, ease: 'power2.out' }});
  M.WOBBLE(tl, '#incoming-code-sheet', 1.23, {{ angle: 3, duration: .27 }});
  tl.set('#bot-idle', {{ opacity: 0 }}, .68);
  tl.set('#bot-point', {{ opacity: 1 }}, .68);
  M.BOUNCE(tl, '#bot-motion', .68, {{ height: 12, duration: .21 }});
  tl.to('#point-head', {{ rotation: -7, duration: .24, ease: 'power2.out' }}, .70);
  tl.to('#scan-beam', {{ opacity: .94, scaleY: 1, duration: .22, ease: 'power2.out' }}, 1.00);
  M.SQUASH(tl, '#scanner-frame', 1.04, {{ amount: .985, duration: .23 }});
  tl.to('#scan-beam', {{ opacity: .53, duration: .22, ease: 'power2.inOut' }}, 1.28);
  M.POP_IN(tl, '#caught-bug', 1.72, {{ duration: .34, overshoot: 1.19 }});
  M.WOBBLE(tl, '#caught-bug', 1.94, {{ angle: 11, duration: .36 }});
  tl.set('#bot-point', {{ opacity: 0 }}, 2.14);
  tl.set('#bot-react', {{ opacity: 1 }}, 2.14);
  M.STRETCH(tl, '#bot-motion', 2.14, {{ amount: 1.055, duration: .18 }});
  tl.to('#paper-grabber', {{ y: 8, duration: .26, ease: 'power2.in' }}, 2.24);
  tl.to('#warning-flash', {{ opacity: 1, duration: .09, ease: 'power2.out' }}, 2.42);
  tl.to('#warning-flash', {{ opacity: 0, duration: .14, ease: 'power2.in' }}, 2.51);
  M.SHAKE(tl, '#scanner-frame', 2.44, {{ distance: 8, duration: .29 }});
  M.SHAKE(tl, '#caught-bug', 2.45, {{ distance: 7, duration: .22 }});
  tl.to('#scan-beam', {{ opacity: 0, duration: .17 }}, 2.60);

  // The failed sheet and caught bug are physically tipped into the bin.
  M.SLIDE(tl, '#incoming-code-sheet', 2.64, {{ fromX: 170, toX: 430, duration: .24, ease: 'power2.in' }});
  M.DROP(tl, '#incoming-code-sheet', 2.87, {{ x: 430, y: 245, duration: .43, rotation: 16 }});
  M.DROP(tl, '#caught-bug', 2.77, {{ x: 286, y: 421, duration: .48, rotation: 27 }});
  M.SQUASH(tl, '#reject-bin', 3.14, {{ amount: .93, duration: .22 }});
  tl.to('#paper-grabber', {{ y: -55, duration: .25, ease: 'power2.out' }}, 2.98);
  tl.to('#incoming-code-sheet, #caught-bug', {{ opacity: 0, duration: .13 }}, 3.28);

  // Second sheet: a visibly clean pass, followed by a paper ticket impact.
  M.SLIDE(tl, '#clean-code-sheet', 3.23, {{ fromX: -1080, toX: -280, duration: .66, ease: 'power2.out' }});
  M.WOBBLE(tl, '#clean-code-sheet', 3.80, {{ angle: 2.5, duration: .24 }});
  tl.to('#scan-beam', {{ opacity: .85, scaleY: 1, duration: .18, ease: 'power2.out' }}, 3.68);
  tl.to('#scan-beam', {{ opacity: 0, duration: .18, ease: 'power2.in' }}, 4.05);
  M.STAMP(tl, '#pass-stamp', 4.08, {{ duration: .45, fromY: -190 }});
  M.SQUASH(tl, '#clean-code-sheet', 4.30, {{ amount: .94, duration: .18 }});
  M.SLIDE(tl, '#clean-code-sheet', 4.45, {{ fromX: -280, toX: 360, duration: .58, ease: 'power2.inOut' }});
  tl.set('#bot-react', {{ opacity: 0 }}, 4.76);
  tl.set('#bot-celebrate', {{ opacity: 1 }}, 4.76);
  M.BOUNCE(tl, '#bot-motion', 4.76, {{ height: 24, duration: .34 }});
  M.WOBBLE(tl, '#celebrate-head', 4.80, {{ angle: 5, duration: .38 }});
  M.CAMERA_PUSH(tl, '#world', 5.32, {{ scale: 1.065, duration: .68 }});
  tl.to('#pass-stamp', {{ rotation: -2, duration: .25, ease: 'power2.inOut' }}, 5.42);
  window.__timelines['main'] = tl;
  tl.seek(0);
</script>
</body>
</html>
'''

(PROJECT / "index.html").write_text(html)
print(PROJECT / "index.html")
