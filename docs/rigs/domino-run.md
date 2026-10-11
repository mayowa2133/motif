# Rig: domino-run

A row of dominoes topples in turn until the last one rings a bell. Chain reaction, adoption spreading, one thing leads to the next.

**Origin:** original Motif design, authored SVG in `scripts/motif_rigs/library2.py`. Style inputs: `docs/STYLE_BIBLE.md` and `docs/style-reference-analysis.md` only; no reference frame traced or copied.

**Tags:** chain, spread, adoption, reaction, network, effect, everyone

**States:** standing → fallen

## Actions

- `topple`: standing → fallen, 54 frames; contact `last-domino-bell` closes at frame 36 (distance 0, tested).

## Parameters

```json
{
  "count": 7,
  "label": "ONE CHANGE",
  "target": "EVERYONE"
}
```

**Bot slot:** x -240, y 0, scale 0.22: taps the first domino.

**Palettes:** renders in all 24 Motif palettes (berry, candy, citrus, cobalt, dusk-teal, forest, ink-navy, lagoon, lilac, mauve, meadow, mint-coral, mustard, neon-ember, neon-teal, neon-violet, peach, plum-night, poppy, royal, sky, slate, sunflower, sunrise); films rotate them per scene.

**Status:** draft proof; awaiting Mayowa approval (plan task 2.2).
