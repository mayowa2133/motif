# Scene 01 review — An AI agent works while you sleep

Status: **approved benchmark scene** for quiet workstation, night desk and software productivity compositions. The modular architecture, 17 independent source assets, five layer exports, metadata and deterministic composition are preserved. Motif Bot's canonical v1 geometry, face system and scale were not changed. Scene 01's art is locked; future work will test different environments without redesigning it.

## Review outputs

| Output | File |
| --- | --- |
| Clean 1080 × 1920 scene | [scene-full.png](../previews/scene-01/scene-full.png) |
| Before / after comparison | [before-after.png](../previews/scene-01/before-after.png) |
| Baseline scene snapshot | [scene-before.png](../previews/scene-01/scene-before.png) |
| 360 × 640 mobile simulation | [mobile-preview.png](../previews/scene-01/mobile-preview.png) |
| Reusable asset contact sheet | [contact-sheet.png](../previews/scene-01/contact-sheet.png) |
| Exploded asset view | [exploded-view.png](../previews/scene-01/exploded-view.png) |
| Layer diagram | [layer-diagram.png](../previews/scene-01/layer-diagram.png) |
| Editable scene and manifest | [scene SVG](../scenes/scene-01/scene-01-night-work.svg) · [scene-01.json](../scenes/scene-01/scene-01.json) |

The new [source assets](../assets/scenes/scene-01/) retain individual transparent SVGs and JSON sidecars: four environment pieces, two furniture pieces, four computing pieces, five desk props and two UI pieces. The locked mascot is a separate eighteenth source. Background, midground, character, foreground and UI also have independent [layer SVGs](../scenes/scene-01/).

## What changed in the refinement

| Change to reusable source assets | Why |
| --- | --- |
| Physical cards and device shells now have slight deterministic edge drift, less even corners, stronger cut-stock edges and down-right contact shadows. Grain varies across paper, dark card and wood. | Reduces the mathematically clean SVG feel while retaining a crisp silhouette and predictable alignment. |
| The wall gained a very faint paper panel seam; the floor gained irregular cut lines and restrained wood fibers. The window, desk, laptop, monitor, keyboard and clock received small shape or layer irregularities. | Makes the room feel assembled from material pieces rather than flat colors with one uniform texture. No asset is distressed or dirty. |
| The completed-task notification became a taped paper ticket with a prominent coral **DONE** stamp and a small paper tail toward the monitor. The progress panel gained a cut-paper border, tape tabs and separate task strips. | Turns completed software work into a physical object in the room, while preserving the original night-work story and replaceable UI architecture. |
| The workstation, mascot, desk props and UI moved upward **64 px** together. The moonlit window, clock, headline-safe area and caption-safe area stayed in place. | Improves vertical balance without filling the upper wall or changing the mascot's relative size. Desk legs still meet the floor. |
| [STYLE_BIBLE.md](STYLE_BIBLE.md) now distinguishes essential UI text from environmental UI texture at target mobile size. | Prevents future scenes from relying on tiny dashboard copy for their core meaning. |

All visual changes above are in [build_scene_01.py](../scripts/build_scene_01.py) and its exported independent SVGs. The scene was not painted over or flattened. The baseline render is preserved so the comparison can be judged directly.

## Story and mobile test

The moon and the 02:14 clock establish night. The laptop remains active; the monitor still shows work running while its first two steps are complete. The stamped **DONE** ticket makes the completed result visible as a paper object beside the still-active system. Motif Bot points toward the monitor with a determined face. This continues to communicate “the AI is working late at night” without a headline, caption or narration.

At **360 × 640**, the window/moon, bot, workstation, active-status shapes and large DONE stamp remain legible. “Plan / Code / Verify,” small laptop code lines, task number and notes are environmental evidence; they are not required to understand the scene. Any future edit that makes their exact wording essential must enlarge or isolate that UI.

## Evaluation against the validation criteria

| Criterion | Assessment |
| --- | --- |
| Seven reference videos | **Closer.** The revised cut edges, varied material textures and stamped task ticket strengthen the handmade object logic seen across the references. Their animated paper collisions and camera timing remain outside this static scene test. |
| Motif Bot consistency | **Pass.** The bot still uses the locked canonical v1 drawing functions and pose parameters. Its colors, geometry and relative scale are unchanged. |
| Tactile quality | **Improved.** Material separation is visible on the desk and UI props, while broad silhouettes remain clean. The wall remains deliberately quiet for future animated headline treatment. |
| Asset modularity | **Pass.** All 17 new assets remain independent. Monitor shell, progress panel, stamped ticket, window frame and night sky can each be swapped independently. |
| Composition | **Improved.** Moving the workstation up reduces the low visual center of gravity. Top and bottom text-safe areas remain empty. |
| Mobile readability | **Pass for the story.** Essential meaning comes from moon, clock, active monitor, completed stamp and character action. Tiny UI copy is supplemental texture. |
| Visual storytelling | **Improved.** The completed task is now a physical ticket above the active computer rather than a generic floating notification. |
| Style mismatches | The monitor screen still has relatively precise UI, which suits a replaceable content inset. The surrounding paper bezel, task strips and stamped ticket keep it in the same visual world. |
| Too detailed / too empty | **Balanced.** The workstation carries several small props, but their shapes remain simple. The upper wall and lower floor retain breathing room for motion and text. |

The remaining risk is **motion fit**: this static validation cannot prove the timing, impact and settle of the ticket, paper layers or UI transitions beside the reference videos. The scene is nevertheless approved as the static quality benchmark for this scene family.

## Reconstruction check

```bash
python3 scripts/build_scene_01.py
python3 scripts/compose_scene_01.py --output /tmp/motif-scene-01-reconstructed.svg
```

The first command regenerates the 17 assets, sidecars, scene and review previews. The second rebuilds the scene from the exported SVG pieces, manifest and locked mascot pose. Final QA compares the two renders pixel for pixel. Scene 01 assets are now `canonical` as part of the approved benchmark; the mascot remains `canonical`.
