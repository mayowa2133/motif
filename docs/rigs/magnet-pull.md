# Rig: magnet-pull

A giant magnet pulls small cards across the floor until they all stick to it. Attraction, pull, everyone flocking to one thing.

**Origin:** original Motif design, authored SVG in `scripts/motif_rigs/library2.py`. Style inputs: `docs/STYLE_BIBLE.md` and `docs/style-reference-analysis.md` only; no reference frame traced or copied.

**Tags:** attract, pull, popular, users, magnet, flock, draw

**States:** loose → stuck

## Actions

- `pull`: loose → stuck, 50 frames; contact `last-item-magnet` closes at frame 34 (distance 0, tested).

## Parameters

```json
{
  "count": 5,
  "item": "USERS",
  "label": "FREE"
}
```

**Bot slot:** x -200, y 0, scale 0.22: watches the cards fly past.

**Palettes:** renders in all 24 Motif palettes (berry, candy, citrus, cobalt, dusk-teal, forest, ink-navy, lagoon, lilac, mauve, meadow, mint-coral, mustard, neon-ember, neon-teal, neon-violet, peach, plum-night, poppy, royal, sky, slate, sunflower, sunrise); films rotate them per scene.

**Status:** draft proof; awaiting Mayowa approval (plan task 2.2).
