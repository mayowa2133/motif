# Rig: sprout-grow

A watering can drips onto a pot and a plant shoots up into bloom. Growth from small beginnings, community, nurturing, patience.

**Origin:** original Motif design, authored SVG in `scripts/motif_rigs/library2.py`. Style inputs: `docs/STYLE_BIBLE.md` and `docs/style-reference-analysis.md` only; no reference frame traced or copied.

**Tags:** growth, grow, community, nurture, small, start, bloom, volunteer, garden

**States:** seed → grown

## Actions

- `water`: seed → grown, 56 frames; contact `drop-soil` closes at frame 20 (distance 0, tested).

## Parameters

```json
{
  "leaves": 4,
  "label": "ONE IDEA",
  "bloom": "MILLIONS"
}
```

**Bot slot:** x 220, y 0, scale 0.22: waters the pot.

**Palettes:** renders in all 19 Motif palettes (berry, candy, citrus, cobalt, forest, lagoon, lilac, meadow, mint-coral, neon-ember, neon-teal, neon-violet, peach, plum-night, poppy, royal, sky, sunflower, sunrise); films rotate them per scene.

**Status:** draft proof; awaiting Mayowa approval (plan task 2.2).
