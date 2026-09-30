# Scene 03 review — The system scans your code and catches bugs

Status: **approved visual benchmark**. This is one 1080 × 1920 inspection and quality-control benchmark. Motif Bot uses its locked canonical v1 drawing and a parameterized pointing pose; no character geometry was altered.

## Outputs

| Output | File |
| --- | --- |
| Full scene | [scene-full.png](../previews/scene-03/scene-full.png) |
| Exploded asset view | [exploded-view.png](../previews/scene-03/exploded-view.png) |
| Individual asset contact sheet | [contact-sheet.png](../previews/scene-03/contact-sheet.png) |
| Layer diagram | [layer-diagram.png](../previews/scene-03/layer-diagram.png) |
| 360 × 640 mobile preview | [mobile-preview.png](../previews/scene-03/mobile-preview.png) |
| Editable scene | [scene-03.svg](../scenes/scene-03/scene-03.svg) |
| Reconstruction manifest | [scene-03.json](../scenes/scene-03/scene-03.json) |

There are **14 new independent SVGs with JSON sidecars** in [the Scene 03 asset directory](../assets/scenes/scene-03/). The factory wall and floor, conduit set, scan sign, quality dial, scanning gate, beam, conveyor, incoming and checked code tickets, bug, grabber, reject bin and pass card are separate pieces. Five transparent layer SVGs sit beside the scene master.

## What the scene communicates

An incoming code ticket reaches a paper scanning gate on a conveyor. A coral bug is caught within the scan beam by a small grabber. A checked code ticket with a large teal check emerges on the right, while an X-marked reject bin below provides a destination for defects. Motif Bot points at the process. The bug/check contrast and left-to-right material flow carry the story; the small code strokes are environmental detail.

## Evaluation

| Criterion | Assessment |
| --- | --- |
| Seven-video visual family | **Promising.** A technical process becomes a tangible machine with entry, inspection, rejection and approved output. This follows the reference family’s physical metaphor approach without copying a specific machine or frame. |
| Scene 01 / Motif consistency | **Pass.** The cool slate scene retains cream card shells, teal success marks, restrained coral warnings, soft material grain, shallow perspective and the unmodified canonical mascot. |
| Tactile quality | **Good.** Pipe sleeves, taped signs, scanner casing, individual tickets, belt rollers and the reject bin have separate cut-paper edges and contact shadows. The beam remains soft so it does not become a glossy effect. |
| Modularity | **Pass.** Scanner, beam, grabber, bug, tickets, conveyor, bin and signs can be replaced or animated independently. The render is reconstructed from those SVGs and the manifest. |
| Composition | **Pass.** Conduits and sign establish the factory above; the gate and caught bug occupy the center; the conveyor spans the action; the mascot is a small guide at the lower left. Text-safe areas remain empty. |
| Mobile readability | **Pass for the story.** The scanner arch, coral bug, outgoing check, X bin and bot read at 360 × 640. The words “SCAN” and “PASS” reinforce the meaning, but their exact reading is not required. |
| Process clarity | **Good.** Input, caught defect and checked output are distinguishable. A moving conveyor and grabber would make temporal order even clearer in an eventual animated beat. |
| Style mismatch / limits | The conduit set is more geometric than the paper desk and arena crowd, but its cream sleeves and shallow construction keep it within the same system. Static art cannot validate process timing or scan motion. |

This scene follows [the mobile UI rule](STYLE_BIBLE.md): `<>` code strokes are a code cue, while the bug and large check communicate the essential result.

## Rebuild

```bash
python3 scripts/build_benchmark_scenes.py
python3 scripts/compose_benchmark_scene.py scene-03 --output /tmp/motif-scene-03.svg
```

The second command recomposes from the exported SVGs, manifest and locked mascot pose. Final QA found the reconstructed scene pixel identical to the generated master. The user approved Scene 03 as the inspection visual benchmark. Motion Benchmark 01 animates this scene without changing its asset drawings.
