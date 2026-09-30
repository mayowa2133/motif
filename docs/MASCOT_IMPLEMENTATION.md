# Motif Bot A — canonical vector puppet v1

Status: **canonical v1**. The approved A character design is locked. This pass refined the side and back views and paper material, then verified that the original front silhouette, cream/teal identity and small-size readability remain intact. The six earlier raster concepts retain `review` status.

## Component structure

The editable [front master](../assets/characters/motif-bot/canonical/v1/motif-bot-front-neutral-v1.svg) uses a 1024 × 1024 transparent canvas. Its ten independently controlled groups are:

```text
HEAD                 BODY
LEFT_ARM             RIGHT_ARM
LEFT_HAND            RIGHT_HAND
LEFT_LEG             RIGHT_LEG
LEFT_FOOT            RIGHT_FOOT
```

The head contains a shell, dark face panel, swappable face state and two antennae. The chest code mark is part of the body. Arms remain single flexible strips; legs and chunky feet have separate controls without visible knee or ankle machinery. Registered SVG parts and JSON sidecars are in [the canonical package](../assets/characters/motif-bot/canonical/v1/). [The manifest](../assets/characters/motif-bot/canonical/v1/motif-bot-v1.json) records the art box, palette, draw order, groups, anchors, hand and face states, and turnaround views.

Five whole-shape hand states are `mitten` (default), `open` (wave), `grip`, `point` and `fist`. Twelve face states swap inside the display. There are no articulated fingers.

## Poses are parameters

[Sixteen pose presets](../assets/characters/motif-bot/canonical/v1/pose-presets.json) define body and head rotation, arm endpoints, hand selection, foot placement and face state. These are composition recipes, not sixteen canonical character illustrations. Their rendered SVGs live only in [preview proofs](../previews/motif-bot-a-v1/proofs/) to validate range of action. Demo props in those proofs are disposable scene examples, not character components.

`scripts/build_motif_bot.py` is the source for canonical geometry and metadata. `scripts/compose_motif_bot.py` builds a particular pose from the shared components and parameters. Both use the Python standard library. The PNG preview script uses Pillow and CairoSVG from `scripts/requirements-preview.txt`.

```bash
python3 scripts/build_motif_bot.py
python3 scripts/render_motif_bot_previews.py
python3 scripts/validate_motif_bot.py
```

To compose a custom variant without adding another canonical pose file:

```bash
python3 scripts/compose_motif_bot.py --pose pointing --expression happy \
  --right-hand grip --right-end 800,520 --output /tmp/motif-custom.svg
```

Parts remain registered in the master canvas for exact overlay. The manifest records normalized anchors and convenient `anchorPixels`; pose endpoints are expressed in master-canvas pixels. The puppet has deliberate cutout motion, not a physical 3D skeleton.

## Final previews

- [Turnaround: front, three-quarter, side and back](../previews/mascot-turnaround.png)
- [96 / 144 / 288 px readability comparison](../previews/mascot-small-size.png)
- [Six representative actions: standing, running, pointing, holding, typing and falling](../previews/mascot-representative-poses.png)
- [All sixteen pose proofs](../previews/mascot-poses.png)
- [Face expressions](../previews/mascot-expressions.png)
- [Transparent front raster](../previews/motif-bot-front-neutral-v1.png)

The side heads retain more depth, and the back uses straight vent slots and a tiny port instead of curved marks. Slight irregular grain and soft contact shadows give the original shapes more paper tactility. Preview sheets use a muted green field so the cream shell can be judged; the standalone art is transparent.

This release stops at the mascot. Props, costumes, environments and the wider library are future scene work.
