# Rig: app-screen

The product in use: a monitor, laptop or phone showing a Motif-drawn terminal, app window or browser page; the brief's lines type in, the cursor presses run and the result pops. Demos, commands, settings, checkboxes, downloads.

**Origin:** original Motif design, authored SVG in `scripts/motif_rigs/library3.py`. Style inputs: `docs/STYLE_BIBLE.md` and `docs/style-reference-analysis.md` only; no reference frame traced or copied.

**Tags:** demo, screen, app, terminal, command, install, download, checkbox, setting, browser, website, click

**States:** idle → done

## Actions

- `run`: idle → done, 60 frames; contact `cursor-press` closes at frame 30 (distance 0, tested).

## Parameters

```json
{
  "device": "monitor",
  "ui": "terminal",
  "title": "Terminal",
  "lines": [
    "run the thing"
  ],
  "result": "DONE",
  "button": null,
  "logo": null
}
```

**Bot slot:** x 300, y 0, scale 0.24: watches the screen and reacts to the result.

**Palettes:** renders in all 19 Motif palettes (berry, candy, citrus, cobalt, forest, lagoon, lilac, meadow, mint-coral, neon-ember, neon-teal, neon-violet, peach, plum-night, poppy, royal, sky, sunflower, sunrise); films rotate them per scene.

**Status:** draft proof; awaiting Mayowa approval (plan task 2.2).
