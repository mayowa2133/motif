# Rig: bridge-span

Planks drop in one by one to bridge a gap between two cliffs; then a traveller crosses. Connecting people or systems, closing a gap.

**Origin:** original Motif design, authored SVG in `scripts/motif_rigs/library2.py`. Style inputs: `docs/STYLE_BIBLE.md` and `docs/style-reference-analysis.md` only; no reference frame traced or copied.

**Tags:** connect, bridge, gap, link, together, share, map, open, interoperate

**States:** gap → spanned

## Actions

- `span`: gap → spanned, 50 frames; contact `last-plank-cliff` closes at frame 34 (distance 0, tested).

## Parameters

```json
{
  "planks": 5,
  "left": "YOU",
  "right": "WORLD"
}
```

**Bot slot:** x -220, y 0, scale 0.2: stands on the near cliff.

**Palettes:** renders in all 24 Motif palettes (berry, candy, citrus, cobalt, dusk-teal, forest, ink-navy, lagoon, lilac, mauve, meadow, mint-coral, mustard, neon-ember, neon-teal, neon-violet, peach, plum-night, poppy, royal, sky, slate, sunflower, sunrise); films rotate them per scene.

**Status:** draft proof; awaiting Mayowa approval (plan task 2.2).
