# Rig: launch-pad

A rocket lifts off its pad and its nose punches through a target ring. Launch, release, going live, hitting a goal.

**Origin:** original Motif design, authored SVG in `scripts/motif_rigs/library2.py`. Style inputs: `docs/STYLE_BIBLE.md` and `docs/style-reference-analysis.md` only; no reference frame traced or copied.

**Tags:** launch, release, ship, live, goal, speed, new, version

**States:** ready → flying

## Actions

- `lift`: ready → flying, 48 frames; contact `nose-ring` closes at frame 30 (distance 0, tested).

## Parameters

```json
{
  "label": "VERSION 1",
  "target": "LIVE"
}
```

**Bot slot:** x -250, y 0, scale 0.22: presses the launch button.

**Palettes:** renders in all 19 Motif palettes (berry, candy, citrus, cobalt, forest, lagoon, lilac, meadow, mint-coral, neon-ember, neon-teal, neon-violet, peach, plum-night, poppy, royal, sky, sunflower, sunrise); films rotate them per scene.

**Status:** draft proof; awaiting Mayowa approval (plan task 2.2).
