# Scene 02 review — Multiple agents compete and the strongest answer wins

Status: **approved visual benchmark**. This is one 1080 × 1920 competition benchmark, not a new mascot or a general prop-library release. Motif Bot uses its locked canonical v1 drawing and a parameterized presenting pose.

## Outputs

| Output | File |
| --- | --- |
| Full scene | [scene-full.png](../previews/scene-02/scene-full.png) |
| Exploded asset view | [exploded-view.png](../previews/scene-02/exploded-view.png) |
| Individual asset contact sheet | [contact-sheet.png](../previews/scene-02/contact-sheet.png) |
| Layer diagram | [layer-diagram.png](../previews/scene-02/layer-diagram.png) |
| 360 × 640 mobile preview | [mobile-preview.png](../previews/scene-02/mobile-preview.png) |
| Editable scene | [scene-02.svg](../scenes/scene-02/scene-02.svg) |
| Reconstruction manifest | [scene-02.json](../scenes/scene-02/scene-02.json) |

There are **12 new independent SVGs with JSON sidecars** in [the Scene 02 asset directory](../assets/scenes/scene-02/). They comprise a backdrop, floor, crowd tiers, arena arch, answer evaluation board, stage, three contestant tokens, podium, best-answer seal and sparse confetti. Five transparent layer SVGs sit beside the scene master.

## What the scene communicates

Three simple agent tokens enter one arena. A three-answer board points toward the center. The teal agent occupies the highest first-place podium, with a large check seal and a few paper confetti pieces; the blue and coral agents stand on lower positions. Motif Bot is a small presenter beside the result. The selection can be understood from placement, height, color and checkmark before reading “ANSWER TRIALS” or “BEST.”

## Evaluation

| Criterion | Assessment |
| --- | --- |
| Seven-video visual family | **Promising.** The arena uses shallow paper architecture, crowd rhythm, physical ranking and a small guide character. It borrows the reference grammar without recreating a source frame, headline strip or character. |
| Scene 01 / Motif consistency | **Pass.** Cream cut edges, fibrous grain, matte colors, down-right shadows, teal success signals and the unmodified canonical mascot connect the warm arena to the night desk. |
| Tactile quality | **Good.** Arch, tier rails, stage, podium and seal read as overlapping card stock. The crowd is deliberately simplified into repeated cutout shapes. |
| Modularity | **Pass.** Crowd, arch, stage, answer board, each contestant, podium and seal can be moved or swapped independently. The render is reconstructed from their SVGs and manifest. |
| Composition | **Pass.** The arch and tiers establish a venue; the central podium is the focal mass. The mascot remains a secondary scale cue. Top headline and bottom caption zones stay empty. |
| Mobile readability | **Pass for the story.** Three competitors, a raised winner, large check seal and celebrating guide survive at 360 × 640. Individual audience figures and board copy become texture. |
| Crowding without chaos | **Pass.** The audience is visually dense but low contrast. Three large contestants and one winner seal remain the only high-priority shapes. |
| Style mismatch / limits | The contestant tokens are new simple agents rather than variants of Motif Bot, so they should be reviewed for brand fit. This static result frame does not prove racing, elimination or winner-reveal motion. |

The exact wording on the board is supplemental. The first-place platform and check seal carry the essential claim in line with [the mobile UI rule](STYLE_BIBLE.md).

## Rebuild

```bash
python3 scripts/build_benchmark_scenes.py
python3 scripts/compose_benchmark_scene.py scene-02 --output /tmp/motif-scene-02.svg
```

The second command recomposes from the exported SVGs, manifest and locked mascot pose. Final QA found the reconstructed scene pixel identical to the generated master. The user approved Scene 02 as a visual benchmark; arena energy remains a motion question rather than a still-scene redesign task.
