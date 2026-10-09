# Rig: thermometer

A thermometer rises to a target mark, then stars pop. Hype, demand, heat, rating.

**Origin:** original Motif design, authored SVG in `scripts/motif_rigs/library.py`. Style inputs: `docs/STYLE_BIBLE.md` and `docs/style-reference-analysis.md` only; no reference frame traced or copied.

**Tags:** hype, heat, rating, demand, temperature, stars

**States:** cold → hot

## Actions

- `heat`: cold → hot, 54 frames; contact `mercury-target` closes at frame 34 (distance 0, tested).

## Parameters

```json
{
  "from": 15,
  "to": 90,
  "target": "VIRAL",
  "label": "HYPE",
  "stars": 3
}
```

**Bot slot:** x 220, y 0, scale 0.24: fans the bulb or reacts to the heat.

**Palettes:** renders in all 8 Motif palettes (berry, citrus, cobalt, lagoon, meadow, mint-coral, plum-night, sunrise); films rotate them per scene.

**Status:** draft proof; awaiting Mayowa approval (plan task 2.2).
