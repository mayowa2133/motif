# Rig: race-track

Two to four labelled racers; the leader reaches the finish line. Competition, benchmark, speed.

**Origin:** original Motif design, authored SVG in `scripts/motif_rigs/library.py`. Style inputs: `docs/STYLE_BIBLE.md` and `docs/style-reference-analysis.md` only; no reference frame traced or copied.

**Tags:** competition, benchmark, speed, ranking, versus

**States:** start → finish

## Actions

- `race`: start → finish, 60 frames; contact `finish-line` closes at frame 44 (distance 0, tested).

## Parameters

```json
{
  "labels": [
    "OPEN",
    "CLOSED",
    "LOCAL"
  ],
  "progress": [
    1.0,
    0.62,
    0.8
  ]
}
```

**Bot slot:** x -300, y 0, scale 0.2: waves the start flag beside the track.

**Palettes:** renders in all 19 Motif palettes (berry, candy, citrus, cobalt, forest, lagoon, lilac, meadow, mint-coral, neon-ember, neon-teal, neon-violet, peach, plum-night, poppy, royal, sky, sunflower, sunrise); films rotate them per scene.

**Status:** draft proof; awaiting Mayowa approval (plan task 2.2).
