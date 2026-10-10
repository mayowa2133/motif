# Rig: light-render

A studio lamp shines on an object on a small stage; light rays bounce off it into a camera lens and each ray fills one tile of the camera screen until the rendered picture is complete. Ray tracing, rendering, real light, like a real camera, photo-real images.

**Origin:** original Motif design, authored SVG in `scripts/motif_rigs/library4.py`. Style inputs: `docs/STYLE_BIBLE.md` and `docs/style-reference-analysis.md` only; no reference frame traced or copied.

**Tags:** render, rendering, light, ray, rays, camera, photo, image, picture, realistic, 3d, engine, blender, cycles, graphics

**States:** idle → done

## Actions

- `trace`: idle → done, 72 frames; contact `ray-tile` closes at frame 54 (distance 0, tested).

## Parameters

```json
{
  "label": "CYCLES",
  "result": "REAL LIGHT",
  "subject": "teapot"
}
```

**Bot slot:** x 300, y 0, scale 0.24: stands by the camera and watches the picture fill in.

**Palettes:** renders in all 19 Motif palettes (berry, candy, citrus, cobalt, forest, lagoon, lilac, meadow, mint-coral, neon-ember, neon-teal, neon-violet, peach, plum-night, poppy, royal, sky, sunflower, sunrise); films rotate them per scene.

**Status:** draft proof; awaiting Mayowa approval (plan task 2.2).
