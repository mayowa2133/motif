# Rig: stacked-meter

Coloured blocks stack into a tower (optionally a rocket) with a live count. Growth, scale, momentum.

**Origin:** original Motif design, authored SVG in `scripts/motif_rigs/library.py`. Style inputs: `docs/STYLE_BIBLE.md` and `docs/style-reference-analysis.md` only; no reference frame traced or copied.

**Tags:** growth, scale, momentum, launch, increase, record

**States:** low → high

## Actions

- `build`: low → high, 50 frames; contact `top-block` closes at frame 38 (distance 0, tested).

## Parameters

```json
{
  "from": 2,
  "to": 9,
  "unit": "x",
  "label": "USERS",
  "rocket": true
}
```

**Bot slot:** x -230, y 0, scale 0.24: stacks the blocks.

**Palettes:** renders in all 8 Motif palettes (berry, citrus, cobalt, lagoon, meadow, mint-coral, plum-night, sunrise); films rotate them per scene.

**Status:** draft proof; awaiting Mayowa approval (plan task 2.2).
