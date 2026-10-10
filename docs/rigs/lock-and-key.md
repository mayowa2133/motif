# Rig: lock-and-key

A big key slides into a giant padlock, turns, and the shackle springs open. Unlocking, access, free, open, security.

**Origin:** original Motif design, authored SVG in `scripts/motif_rigs/library2.py`. Style inputs: `docs/STYLE_BIBLE.md` and `docs/style-reference-analysis.md` only; no reference frame traced or copied.

**Tags:** unlock, access, open, free, security, key, lock, padlock, secure

**States:** locked → open

## Actions

- `unlock`: locked → open, 50 frames; contact `key-slot` closes at frame 26 (distance 0, tested).

## Parameters

```json
{
  "label": "LOCKED",
  "key": "FREE"
}
```

**Bot slot:** x 230, y 0, scale 0.22: cheers as the lock opens.

**Palettes:** renders in all 19 Motif palettes (berry, candy, citrus, cobalt, forest, lagoon, lilac, meadow, mint-coral, neon-ember, neon-teal, neon-violet, peach, plum-night, poppy, royal, sky, sunflower, sunrise); films rotate them per scene.

**Status:** draft proof; awaiting Mayowa approval (plan task 2.2).
