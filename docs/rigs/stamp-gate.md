# Rig: stamp-gate

A stamp lands on a document; the gate arm lifts (approved) or stays shut (rejected). Approval, policy, permission.

**Origin:** original Motif design, authored SVG in `scripts/motif_rigs/library.py`. Style inputs: `docs/STYLE_BIBLE.md` and `docs/style-reference-analysis.md` only; no reference frame traced or copied.

**Tags:** approval, policy, permission, review, regulation, reject

**States:** waiting → stamped

## Actions

- `stamp`: waiting → stamped, 42 frames; contact `stamp-document` closes at frame 20 (distance 0, tested).

## Parameters

```json
{
  "document": "NEW MODEL",
  "stamp": "APPROVED",
  "verdict": "approved"
}
```

**Bot slot:** x -60, y -640, scale 0.2: grips the stamp handle.

**Palettes:** renders in all 19 Motif palettes (berry, candy, citrus, cobalt, forest, lagoon, lilac, meadow, mint-coral, neon-ember, neon-teal, neon-violet, peach, plum-night, poppy, royal, sky, sunflower, sunrise); films rotate them per scene.

**Status:** draft proof; awaiting Mayowa approval (plan task 2.2).
