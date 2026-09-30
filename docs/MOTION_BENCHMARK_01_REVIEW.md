# Motion Benchmark 01 — Code Inspection

Status: **rendered for review**. This is the first motion test of the approved Motif world. It animates the existing Scene 03 SVG pieces and poses generated from the locked Motif Bot v1 geometry. The Scene 02/03 master SVGs, raster previews, mascot generator, and canonical mascot manifest were hash checked before and after the approval metadata update; their artwork is unchanged.

## Deliverables

| Output | File |
| --- | --- |
| Final 1080 × 1920, 30 fps, 6.4 s MP4 | [motion-benchmark-01.mp4](../videos/code-inspection-motion/renders/motion-benchmark-01.mp4) |
| 360 × 640, 12 fps GIF preview | [motion-benchmark-01-preview.gif](../videos/code-inspection-motion/renders/motion-benchmark-01-preview.gif) |
| Five representative frames from the MP4 | [five-beat-contact-sheet.png](../videos/code-inspection-motion/proof/five-beat-contact-sheet.png) |
| 0.4-second sequence scan | [sequence-check.png](../videos/code-inspection-motion/proof/sequence-check.png) |
| Individual proof frames | [beginning](../videos/code-inspection-motion/proof/beginning.png) · [bug reveal](../videos/code-inspection-motion/proof/bug-reveal.png) · [rejection](../videos/code-inspection-motion/proof/rejection.png) · [PASS](../videos/code-inspection-motion/proof/pass.png) · [ending](../videos/code-inspection-motion/proof/ending.png) |
| Native mobile-scale PASS frame | [mobile-pass.png](../videos/code-inspection-motion/proof/mobile-pass.png) |
| Structured event timeline | [scene-events.json](../videos/code-inspection-motion/scene-events.json) |
| Reusable primitives | [motion-primitives.js](../videos/code-inspection-motion/assets/motion-primitives.js) |
| Seekable composition | [index.html](../videos/code-inspection-motion/index.html) and [generator](../scripts/build_motion_benchmark_01.py) |

## Timeline

| Time | Story event | Physical cue |
| --- | --- | --- |
| 0.00–0.28 | Empty inspection line runs | Belt ticks move at a steady rate. |
| 0.28–1.43 | First code sheet enters | Paper slides in, tilts, and settles at the scanner. Bot notices and points at 0.68. |
| 1.00–2.14 | Scanner activates; bug appears | Teal beam extends, machine compresses slightly, coral bug pops and wobbles. |
| 2.14–3.41 | Failure and rejection | Bot changes to a shocked face and open hands, grabber descends, coral warning flashes, scanner shakes, then sheet and bug fall into the bin. Bin compresses on impact. |
| 3.23–4.53 | Clean code is checked | Second sheet arrives, beam scans, physical PASS ticket stamps down with impact and rebound. |
| 4.45–6.40 | Approved result | Clean sheet exits, Bot celebrates, and the camera pushes 6.5% toward the PASS state before holding. |

The main visual actions occur roughly every 0.2–0.7 seconds. The longer tail is a deliberate readable result hold. Small text on the sheets is texture; bug, reject bin, checkmark, PASS ticket, and Bot reaction carry the meaning.

## Motion system

`scene-events.json` separates target, time, action, preset, and story purpose. `motion-primitives.js` implements `POP_IN`, `POP_OUT`, `SLIDE`, `DROP`, `STAMP`, `BOUNCE`, `WOBBLE`, `SHAKE`, `SQUASH`, `STRETCH`, `CAMERA_PUSH`, and `CAMERA_PULL` against a paused GSAP timeline. This benchmark instantiates the motions that serve this story; `POP_OUT` and `CAMERA_PULL` are available for later scenes and are not forced into this shot. Bot changes use four states from `assemble_pose`, including the existing canonical face and hand definitions. Its head angle, body bounce/stretch, face, and hand state change at the narrative beats. No character shape was redrawn.

The sole new drawn element is a low-opacity coral warning flash inside the scanner, an animation-specific derivative. Belt ticks are simple strokes tied to the existing conveyor. All other visible props and environment forms come from Scene 03. The camera affects one `#world` wrapper and only moves near the ending.

## Review

| Criterion | Assessment |
| --- | --- |
| Pacing | The sequence has a clear setup, reveal, reject, second try, and payoff. The first sheet arrival is the longest motion, letting viewers orient; the reject section is quicker and more playful. The final hold is long enough to read on a phone. |
| Physicality | Paper settles with a slight wobble, the machine compresses and shakes, the bug overshoots, failed work drops, the bin reacts, and the PASS ticket lands with a squash and rebound. These are contact-driven motions rather than uniform layer translations. |
| Visual clarity | At 360 × 640, the central arch, coral bug, bin X, green checkmark, PASS ticket, and Bot expression remain distinct. The five frames from the encoded MP4 preserve the intended order. Tiny code lines remain decorative. |
| Character motion | The same puppet moves from thinking to pointing, shocked, then excited. The head and body add small accents. The discrete pose swaps are readable at this scale, though a future animation rig could interpolate arm paths for closer shots. |
| Motion consistency | Easing, brief overshoots, restrained angular wobble, and contact squash follow one tactile paper language. The camera moves once and the world remains spatially stable. |
| Seven-reference fit | The sequence uses their key motion philosophy: frequent purposeful events, tangible software metaphors, fast paper-object beats, and a clear payoff. It is quieter than the reference videos because this pass has no headline, sound accents, or inter-scene transition. |
| Generic-animation risk | The slide entrance and exit are the plainest moves; the bug capture, bin impact, and physical PASS landing prevent the piece from reading as a generic UI presentation. A future sound pass would strengthen these contact moments. |
| Primitive reuse | Twelve named actions share parameterized timing and easing functions; the structured event file makes scene direction inspectable. The event JSON is a planning representation, while the composition currently instantiates it in authored GSAP calls rather than a fully generic event interpreter. |

The test supports the motion-system hypothesis for one inspection metaphor. It does not yet validate captions, narration sync, sound design, transitions between scenes, or arena-style spectacle. The large headline and caption safe areas look intentionally quiet in this no-copy benchmark, but should be assessed with actual text in a later product test.

## Reproduction and verification

```bash
python3 scripts/build_motion_benchmark_01.py
cd videos/code-inspection-motion
npx hyperframes check --at 0,1.9,3.2,4.35,6.2
npx hyperframes render --quality delivery --fps 30 --output renders/motion-benchmark-01.mp4
ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate,nb_frames,duration -of json renders/motion-benchmark-01.mp4
```

HyperFrames `check` passed with zero lint, runtime, layout, motion-assertion, and contrast findings. `ffprobe` confirmed H.264, 1080 × 1920, 30 fps, 192 frames, and 6.400 seconds. The proof images were extracted from the final MP4. Rendering is time-seeked with a paused GSAP timeline, local JS, no render-time network media, no live clock, and no unseeded randomness.

**Stop point:** Motion Benchmark 01 is ready for user review. No further scene, library, or product work is included.
