# Motif mini Reel benchmark

This 9.55 second, 1080 × 1920, 30 fps composition tests one complete Motif short-form story. It reuses the approved Scene 01 night desk, the approved Scene 03 inspection factory, and the locked canonical Motif Bot v1. The factory returns for the clean pass rather than introducing a third environment.

## Build

From the repository root:

```bash
python3 scripts/build_motif_mini_reel.py
cd videos/motif-mini-reel
npm run check
npm run render
```

`scene-events.json` is the executable motion plan. `assets/motion-engine.js` validates selectors and times, maps actions to `assets/motion-primitives.js`, and registers the resulting paused GSAP timeline with HyperFrames. `index.html` calls the compiler once; it contains no scene-specific animation calls. For supported actions, changing the JSON and rebuilding is enough to change motion.

`audio-plan.json` lists each local sound cue and the narration clip with its placement and mix level. It contains no music bed: no cleared track was found, and standard MusicGen weights were excluded. The builder makes root-level HyperFrames audio elements from that file. Each visual fragment is loaded from the approved source SVG and assembled at its manifest placement. Mascot poses come from `scripts/build_motif_bot.py` without changing canonical geometry.

## Event shape

```json
{
  "time": 5.3,
  "target": "#f-caught-bug",
  "action": "POP_IN",
  "params": { "duration": 0.34, "overshoot": 1.3 }
}
```

Supported actions: `POP_IN`, `POP_OUT`, `SLIDE`, `DROP`, `STAMP`, `BOUNCE`, `WOBBLE`, `SHAKE`, `SQUASH`, `STRETCH`, `CAMERA_PUSH`, `CAMERA_PULL`, `SET`, `TWEEN`, `FROM_TO`, `PULSE`, `POSE_SWAP`, and `SCENE_CUT`. The first twelve are reusable Motif primitives; the remaining actions are general timeline operations and state changes. All actions are deterministic and seekable.

## Provenance

- Scene assets: `scenes/scene-01/scene-01.json` and `scenes/scene-03/scene-03.json`.
- Mascot: `assets/characters/motif-bot/canonical/v1/motif-bot-v1.json` and its generator.
- SFX: locally bundled Pixabay effects; see `assets/sfx/CREDITS.md`.
- Narration: Kokoro-82M v1.0, `af_nova`, 0.85 speed, with two audition samples and a replaceable file track. Source and hashes are in `audio-source-license-manifest.json`.

This benchmark makes no new prop library or new environment. Headlines, captions, scanner warning, belt motion marks, and the check accent are composition overlays rather than library assets.
