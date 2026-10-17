# 3D experiment (DRAFT, not part of the pipeline)

Mayowa asked (2026-10-17) for an experiment: make 3D versions of Motif's existing
2D art. This folder does that with [three.js](https://threejs.org) without drawing
anything new. It reads the library's own SVG (Bot puppet, rooms, props, rigs) and
rebuilds it as lit 3D paper:

- every filled shape becomes an extruded card;
- every stroke becomes a round tube, so the Bot's arms, legs and antennae turn into real limbs;
- text becomes a printed decal on its card;
- shapes stack in draw order. Each shape rests on the shapes it overlaps, so a small
  piece sits on top of a big one instead of sinking into it;
- a set keeps its layers (room, back props, machine, host, front props) as separate
  planes. The room's floor folds down flat so everything stands on it. Each nearer layer
  is scaled down to cancel perspective, so the head-on view matches the 2D composition;
- 2D fake depth (drop-shadow and edge copies of a shape) is dropped, because real
  thickness and a real shadow-casting key light replace it. The paper grain is a
  procedural texture generated in `stage.js`.

There are two looks:

| mode | what it looks like |
|---|---|
| `card` | thin card stock with crisp edges: a paper diorama |
| `puffy` | thick, rounded, bevelled shapes: a soft vinyl or clay toy |

A rig's action (for example the hydraulic press stamping) plays in 3D. The layer is
rebuilt from the rig's own frame SVGs, so the contact and timing are the library's.

## Run it

```bash
cd experiments/three-d
npm install                                   # three 0.170.0, playwright-core 1.56.1
python3 export_scenes.py                      # writes scenes/*.json from the library
node render.mjs OUT --modes card,puffy --clip 4 --fps 24
```

For each scene, `OUT` gets `<scene>-2d.png` (the flat 2D original) and
`<scene>-<mode>-{front,left,right}.png`. With `--clip`, it also gets an orbit clip
`<scene>-<mode>-orbit.mp4`.

Rendering uses headless Chromium with SwiftShader WebGL. It needs no GPU and works in
the cloud container. A set takes a few seconds per still. During a clip, the frames
where the rig is acting take longer, because that layer is rebuilt every frame.

## What it is not (yet)

- It is not wired into `motif_reel.py`, the gates or the planner. Approved 2D reels
  are unchanged.
- The art stays front-facing paper. Past about ±30° you can see that the shapes are
  layered cutouts, not sculpted volumes. A true turnaround would need modelled parts.
- Gradients, clip paths and pattern fills are skipped. Lighting replaces the wall
  falloff and floor glow.
- No assets are added. `three` is an npm dependency of this folder only (MIT) and is
  not vendored into `assets/`.
