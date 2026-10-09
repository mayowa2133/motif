# Rig: device-wall

Shelves of phones, browsers or laptops; a stamp lands the product mark on one screen and it spreads until every device shows it. Inside everything, everywhere, on every device.

**Origin:** original Motif design, authored SVG in `scripts/motif_rigs/library3.py`. Style inputs: `docs/STYLE_BIBLE.md` and `docs/style-reference-analysis.md` only; no reference frame traced or copied.

**Tags:** everywhere, inside, every, device, phone, browser, ubiquitous, installed, ships

**States:** dark → lit

## Actions

- `light-up`: dark → lit, 60 frames; contact `stamp-screen` closes at frame 22 (distance 0, tested).

## Parameters

```json
{
  "kind": "phone",
  "count": 6,
  "label": "EVERY DEVICE",
  "logo": null,
  "names": []
}
```

**Bot slot:** x 300, y 0, scale 0.24: points at the screens as they light.

**Palettes:** renders in all 19 Motif palettes (berry, candy, citrus, cobalt, forest, lagoon, lilac, meadow, mint-coral, neon-ember, neon-teal, neon-violet, peach, plum-night, poppy, royal, sky, sunflower, sunrise); films rotate them per scene.

**Status:** draft proof; awaiting Mayowa approval (plan task 2.2).
