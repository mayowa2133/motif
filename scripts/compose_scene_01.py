#!/usr/bin/env python3
"""Reconstruct Scene 01 from its asset SVGs, manifest and locked mascot geometry."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from build_scene_01 import BOT_DEFS, DEFS, ROOT, W, H, mascot_group, svg


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest", type=Path, default=ROOT / "scenes/scene-01/scene-01.json"
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text())
    output = args.output or ROOT / manifest["render"]
    pieces = []
    for asset in manifest["assets"]:
        if asset["id"] == "scene-01-desk":
            pieces.append(mascot_group())
        source = ROOT / asset["source"]
        exported = source.read_text()
        body = exported.split("</defs>", 1)[1].rsplit("</svg>", 1)[0].strip()
        x, y = asset["placement"]["x"], asset["placement"]["y"]
        slug = source.stem
        pieces.append(
            f'<g id="{slug}" data-asset="{asset["source"]}" '
            f'transform="translate({x} {y})">{body}</g>'
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        svg(W, H, "\n".join(pieces), manifest["name"], DEFS + BOT_DEFS)
    )
    print(output)


if __name__ == "__main__":
    main()
