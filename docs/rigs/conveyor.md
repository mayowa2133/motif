# Rig: conveyor

Labelled inputs ride a belt into a machine that outputs a result. Process, pipeline, automation.

**Origin:** original Motif design, authored SVG in `scripts/motif_rigs/library.py`. Style inputs: `docs/STYLE_BIBLE.md` and `docs/style-reference-analysis.md` only; no reference frame traced or copied.

**Tags:** process, pipeline, automation, workflow, factory, agent

**States:** idle → processed

## Actions

- `process`: idle → processed, 54 frames; contact `item-mouth` closes at frame 30 (distance 0, tested).

## Parameters

```json
{
  "items": [
    "EMAIL",
    "DOCS",
    "CHATS"
  ],
  "machine": "AGENT",
  "output": "REPORT"
}
```

**Bot slot:** x -200, y 0, scale 0.22: loads the belt.

**Palettes:** renders in all 8 Motif palettes (berry, citrus, cobalt, lagoon, meadow, mint-coral, plum-night, sunrise); films rotate them per scene.

**Status:** draft proof; awaiting Mayowa approval (plan task 2.2).
