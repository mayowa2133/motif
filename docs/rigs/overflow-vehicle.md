# Rig: overflow-vehicle

A bus with fixed seats; extra riders pile on the roof. Demand exceeds capacity.

**Origin:** original Motif design, authored SVG in `scripts/motif_rigs/library.py`. Style inputs: `docs/STYLE_BIBLE.md` and `docs/style-reference-analysis.md` only; no reference frame traced or copied.

**Tags:** capacity, demand, limit, crowd, queue, scarcity

**States:** seated → overflow

## Actions

- `overflow`: seated → overflow, 45 frames; contact `roof` closes at frame 30 (distance 0, tested).

## Parameters

```json
{
  "seats": 6,
  "riders": 10,
  "label": "FREE TIER"
}
```

**Bot slot:** x 250, y 0, scale 0.22: driver waving from the door side.

**Palettes:** renders in all 8 Motif palettes (berry, citrus, cobalt, lagoon, meadow, mint-coral, plum-night, sunrise); films rotate them per scene.

**Status:** draft proof; awaiting Mayowa approval (plan task 2.2).
