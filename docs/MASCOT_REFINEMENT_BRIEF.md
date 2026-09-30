# Motif Bot A — minimal puppet refinement brief

Decision: **A, Paper puppet, is the selected visual direction.** Preserve its cute cutout-symbol quality. The current generated PNG is a reference for the redraw, not a template to trace pixel for pixel and not a canonical rig.

Implementation: the canonical v1 vector package is described in [MASCOT_IMPLEMENTATION.md](MASCOT_IMPLEMENTATION.md). This brief records the original direction; the implementation document records the final component contract.

## Refinement prompt

> Redraw Motif Bot A as an original, editable 2D cut-paper mascot in the visual family of the seven supplied videos. Preserve the broad cream head, dark friendly face display, small teal leaf antennae and side discs, compact bell torso, `<>` chest mark, simple flexible arms, barely-there legs and chunky little feet. Design the minimum number of independently controllable pieces needed to communicate actions. Arms may be single flexible paper strips with interchangeable simple hands. Legs remain short graphic shapes; feet carry direction and weight. Prioritize charm and instant phone-size readability over physical or anatomical accuracy. Keep the matte fibrous surface, shallow layering and restrained contact shadows. Do not add detailed fingers, visible elbow or knee joints, segmented armor, glossy 3D lighting or a sophisticated humanoid silhouette.

## Visual groups

```text
head
  shell, face panel, face state (eyes + mouth), antennae
body (including chest mark)
left arm  → left hand
right arm → right hand
left leg  → left foot
right leg → right foot
```

The final puppet has ten control groups and face subcomponents. Hand and expression states are swaps. Feet have separate controls without a permanent visual seam. Hidden arm curve controls can bend a single drawn strip without creating a visible elbow.

## Hand library

1. `mitten`: default soft teal mitten/blob.
2. `open`: friendly wave silhouette readable at small size.
3. `grip`: a C-shaped hold with a declared `grip` anchor; scale it for large props.
4. `point`: one simple directional extension.
5. `fist`: compact closed blob for pushing or determination.

Each hand is a whole-shape swap. No finger animation. Mirror only when the shape and palm mark remain correct.

## Permitted cheats

- Stretch or curve an arm to reach across a table.
- Enlarge a grip hand to hold a large prop.
- Bend a leg silhouette beyond plausible anatomy to show speed.
- Offset or briefly detach a foot during a jump or fall if the pose reads better.
- Replace a whole pose drawing when a single flexible shape cannot show the action cleanly.

Use the cheat that makes the action clearest at delivery size. Maintain the cream/teal/dark identity and paper surface in every state.

## Acceptance checks completed for canonical v1

- A neutral pose reads as the same mascot at 96 px high and retains its oversized feet.
- Point, grip, push, type, celebrate and inspect can be communicated using simple hand swaps and arm curves. A walk/run can use minimal alternating leg poses; no natural knee cycle is required.
- No visible elbows, knees, knuckles or extra armor seams appear just to accommodate controls.
- The five hands attach cleanly on both sides; prop grip anchor is stable.
- Face state swaps preserve the dark display and remain legible on a 64 px head.
- All source groups, aliases and anchors are editable and named according to [ASSET_SPEC.md](ASSET_SPEC.md).
