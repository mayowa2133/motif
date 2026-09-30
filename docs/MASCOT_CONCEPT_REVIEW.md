# Motif Bot — six concept review

Status: **direction A selected in user feedback; current art remains review**. Compare all six in [the contact sheet](../previews/mascot-concepts.png). Each full-size transparent PNG and JSON sidecar is under `assets/characters/motif-bot/concepts/`. These are generated single images, not an implemented puppet.

## Evaluation scale

Scores are 1–5, where 5 is strongest. `Video fit` means fit with the seven clips' broad handmade 2D style, not similarity to any particular source character. Scores reflect inspection at full size and in the contact sheet; they are design judgments rather than measured tests.

| Criterion | A Paper puppet | B Editorial mascot | C Soft chibi | D Hinged puppet | E Refined guide | F Balanced bot |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Robot identity | 4 | 5 | 4 | 4 | 4 | 5 |
| Video style fit | **5** | 3 | **5** | 4 | 4 | 3 |
| Charm | 5 | 4 | **5** | 4 | 3 | 4 |
| Cuteness | 4 | 4 | **5** | 3 | 3 | 4 |
| Silhouette clarity | **5** | 4 | **5** | 4 | 4 | 4 |
| Mobile readability | **5** | 4 | **5** | 4 | 4 | 4 |
| Modularity potential | 4 | 3 | 3 | **5** | 4 | 4 |
| Animation potential | 4 | 3 | 4 | **5** | 4 | 4 |
| Costume potential | 4 | 3 | 2 | **5** | **5** | 4 |
| Prop handling potential | 4 | 4 | 2 | **5** | **5** | 5 |
| Originality | **5** | 3 | 4 | 4 | 4 | 3 |
| Brand potential | **5** | 4 | 4 | 3 | 4 | 4 |

## Direction notes

### A — Paper puppet

The broad paper head, bell torso and simple arms translate the robot most convincingly into the clips' flat, tactile visual family. The code mark, side discs and two leaves preserve identity without copied armor. It reads quickly at small size and has an original silhouette. Its tiny legs and oversized feet are strengths to preserve. Interchangeable simple hands will let it interact with props without increasing anatomical detail.

### B — Editorial mascot

Strong identity and tidy, appealing finish. The recognizable robot proportions and leg armor also make it feel closer to a matte redraw of the supplied 3D model. It carries more tiny seams than needed; this will be harder to animate and less native to the reference videos. The chest glyph became `</>` rather than the supplied paired chevrons. The background is transparent in the delivered PNG despite the image tool's preview showing the RGB data beneath alpha.

### C — Soft chibi

The cutest option, with the clearest head and facial read. Its broad paper shapes strongly fit the reference style. Tiny torso and hands limit costumes, holding tools and nuanced body acting; a whole video could overuse the huge face. Good source for expression proportion and cheek treatment even if it is not selected.

### D — Hinged puppet

Best example of how extra articulation can change the character's personality. Exposed pivots, long limbs and high antennae make it more mechanical and less cozy than A or C; it has too many small fasteners for Motif's chosen mascot. Internal controls may borrow its range of motion, but its visible joint system should not transfer to A.

### E — Refined guide

Slim, calm and costume friendly, with a readable display and code badge. It is less distinctive at phone size because its narrow body and long legs resemble a general robot guide. The small face and more structured limbs reduce the childlike charm of the supplied clips. It is a credible premium variant if Motif later needs a more reserved sub-brand character.

### F — Balanced bot

The most immediately familiar to the supplied robot and the most capable of grasping an object. Its brows add expressive range. It retains too much armored limb segmentation and rendered depth for the primary 2D cutout world, so the balance tilts toward identity at the expense of the requested style priority. It is a useful check that the chosen direction has not lost the original robot, but not the best canonical base.

## Recommendation

**A, Paper puppet, is the selected direction.** It obeys the user's style-over-rendering priority while retaining the robot's cream/teal/dark display, two leaves, side modules and `<>` chest identity. Keep its simple head, torso, arms, legs and chunky feet. Add five interchangeable simple hand states and hidden curve/rotation controls where needed. This selects a direction, not a fully realized canonical asset.

An editable canonical v1 vector puppet now implements those requirements with simple face and hand swaps, 96 px checks, parameterized actions and a turnaround. See [MASCOT_IMPLEMENTATION.md](MASCOT_IMPLEMENTATION.md) for the final package. All six exploratory concept images retain `review` status.

## Generation and QA notes

- Concepts were generated with the built-in image generation tool from original prompts; the robot was treated as identity, and sampled video frames supplied broad material/style cues. Prompts and input roles are recorded in [MASCOT_GENERATION_PROMPTS.md](MASCOT_GENERATION_PROMPTS.md).
- All six PNGs are RGBA and preserve alpha. The comparison sheet composites them over one neutral paper field so silhouettes can be compared fairly.
- These images are exploratory raster concepts. They do not yet meet the vector, attachment-point or pose requirements of later phases. The JSON sidecars explicitly record `riggable: false` and `status: review`.
- No props, environments, costumes, UI containers or other library categories were created.
