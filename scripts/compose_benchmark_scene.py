#!/usr/bin/env python3
"""Reconstruct Scene 02 or 03 from its manifest and independent SVG assets."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from build_benchmark_scenes import BOT_DEFS, DEFS, ROOT, W, H, svg
from build_motif_bot import assemble_pose


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scene_id", choices=("scene-02", "scene-03"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    manifest_path = ROOT / "scenes" / args.scene_id / f"{args.scene_id}.json"
    manifest = json.loads(manifest_path.read_text())
    character = manifest["character"]
    pose = character["pose"]
    bot, _ = assemble_pose(pose["base"], pose["faceState"], pose["overrides"])
    place = character["placement"]
    bot_markup = (
        '<g id="canonical-motif-bot" '
        'data-source="assets/characters/motif-bot/canonical/v1/motif-bot-v1.json" '
        f'transform="translate({place["x"]} {place["y"]}) scale({place["scale"]})">'
        f'{bot}</g>'
    )
    parts = []
    for item in manifest["assets"]:
        source = ROOT / item["source"]
        if source.stem == character["insertBefore"]:
            parts.append(bot_markup)
        body = source.read_text().split("</defs>", 1)[1].rsplit("</svg>", 1)[0].strip()
        x,y = item["placement"]["x"],item["placement"]["y"]
        parts.append(
            f'<g id="{source.stem}" data-asset="{item["source"]}" '
            f'transform="translate({x} {y})">{body}</g>'
        )
    output = args.output or ROOT / manifest["render"]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(svg(W,H,"\n".join(parts),manifest["name"],DEFS+BOT_DEFS))
    print(output)


if __name__ == "__main__":
    main()
