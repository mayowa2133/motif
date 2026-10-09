# Rig: hydraulic-press

A press plate comes down on a labelled block and flattens it. Pressure, cost cuts, compression.

**Origin:** original Motif design, authored SVG in `scripts/motif_rigs/library.py`. Style inputs: `docs/STYLE_BIBLE.md` and `docs/style-reference-analysis.md` only; no reference frame traced or copied.

**Tags:** pressure, compression, cost, squeeze, cut, price

**States:** open → crushed

## Actions

- `press`: open → crushed, 48 frames; contact `plate-object` closes at frame 24 (distance 0, tested).

## Parameters

```json
{
  "object": "PRICE",
  "force": "COMPETITION"
}
```

**Bot slot:** x 300, y 0, scale 0.22: pulls the lever.

**Palettes:** renders in all 19 Motif palettes (berry, candy, citrus, cobalt, forest, lagoon, lilac, meadow, mint-coral, neon-ember, neon-teal, neon-violet, peach, plum-night, poppy, royal, sky, sunflower, sunrise); films rotate them per scene.

**Status:** draft proof; awaiting Mayowa approval (plan task 2.2).
