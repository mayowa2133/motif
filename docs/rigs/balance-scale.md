# Rig: balance-scale

Two labelled pans; the heavier side tips down onto its stop. Trade-off, comparison, value.

**Origin:** original Motif design, authored SVG in `scripts/motif_rigs/library.py`. Style inputs: `docs/STYLE_BIBLE.md` and `docs/style-reference-analysis.md` only; no reference frame traced or copied.

**Tags:** tradeoff, comparison, value, weigh, versus, balance

**States:** level → tipped

## Actions

- `tip`: level → tipped, 45 frames; contact `pan-stop` closes at frame 30 (distance 0, tested).

## Parameters

```json
{
  "left_label": "COST",
  "right_label": "VALUE",
  "left_weight": 2,
  "right_weight": 6
}
```

**Bot slot:** x -290, y 0, scale 0.22: adds the last weight.

**Palettes:** renders in all 8 Motif palettes (berry, citrus, cobalt, lagoon, meadow, mint-coral, plum-night, sunrise); films rotate them per scene.

**Status:** draft proof; awaiting Mayowa approval (plan task 2.2).
