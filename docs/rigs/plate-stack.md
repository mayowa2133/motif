# Rig: plate-stack

Plates pile onto a buffet counter. Workload, backlog or consumption growing.

**Origin:** original Motif design, authored SVG in `scripts/motif_rigs/library.py`. Style inputs: `docs/STYLE_BIBLE.md` and `docs/style-reference-analysis.md` only; no reference frame traced or copied.

**Tags:** backlog, growth, usage, workload, pile, consumption

**States:** short → tall

## Actions

- `stack`: short → tall, 54 frames; contact `top-plate` closes at frame 40 (distance 0, tested).

## Parameters

```json
{
  "count_from": 3,
  "count_to": 12,
  "label": "TOKENS USED"
}
```

**Bot slot:** x -270, y 0, scale 0.24: carries the next plate.

**Palettes:** renders in all 19 Motif palettes (berry, candy, citrus, cobalt, forest, lagoon, lilac, meadow, mint-coral, neon-ember, neon-teal, neon-violet, peach, plum-night, poppy, royal, sky, sunflower, sunrise); films rotate them per scene.

**Status:** draft proof; awaiting Mayowa approval (plan task 2.2).
