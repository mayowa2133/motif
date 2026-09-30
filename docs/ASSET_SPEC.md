# Motif asset specification — proposal v0.1

Status: **direction A selected; mascot canonical v1**. Applies to future production assets. The phase 2 PNGs remain exploratory; the editable vector puppet is canonical.

## Units and deliverables

- Author a character master in a 1024 × 1024 coordinate space, transparent, with a documented art box and 5% transparent padding. Retain editable SVG layers for canonical parts. Use PNG/WebP only for restrained surface textures or presentation previews.
- Props use a 512 × 512 master unless a wide/tall family requires 768 × 512 or 512 × 768. A nominal 256 px prop should appear at a consistent physical scale relative to a nominal 512 px mascot.
- Raster preview: sRGB PNG, transparent where the asset is standalone. Environment previews may have full backgrounds. Do not premultiply alpha in delivered PNGs.
- Naming: lowercase kebab case, category prefix where ambiguity exists, view/state suffix, and semantic version for revised canonical art. Example: `motif-bot-front-neutral-v1.svg`.
- Concept files live under `assets/characters/motif-bot/concepts/` with `status: review`. Approval is a later explicit promotion step.

## Minimal cutout puppet contract

- Each independently controlled visual group has a stable `id`, local art box and the few anchors it actually uses, in normalized `[0,1]` coordinates. Draw order is explicit.
- The canonical puppet has ten primary control groups: `head`, `body`, `leftArm`, `leftHand`, `rightArm`, `rightHand`, `leftLeg`, `leftFoot`, `rightLeg`, `rightFoot`. Head subcomponents include the shell, face panel, replaceable face state and antennae. The chest code mark stays grouped with the body.
- Each arm is one flexible cutout shape with a swappable simple hand attached. Internal curve controls or invisible segments are allowed for animation, but do not draw exposed upper-arm/forearm joints. Five hand states are `mitten`, `open`, `grip`, `point`, `fist`.
- Each leg is a simple shape with a separately controlled chunky foot; no visible knees, ankles or articulated armor.
- Mirroring is permitted only for parts with no side-specific identity feature. Left/right in metadata refer to the character's anatomical side.
- Poses are parameter definitions over the shared components: head/body transforms, arm endpoints, hand and face selection, and foot placement. Rendered pose images are validation proofs, not canonical components. Stretch, scale and whole-shape swaps are valid. A pose must maintain a clear silhouette and avoid exposed gaps unless a deliberate jump/fall cheat calls for separation. Accessories bind to named anchors, not hard-coded frame pixels.
- Masks for displays or UI screens are separate from outer frames. A screenshot replacement must not alter the container art.

## Required metadata schema

Store sidecar JSON next to the eventual source asset. Required keys:

```json
{
  "id": "motif-bot-front-neutral",
  "name": "Motif Bot front neutral",
  "category": "character",
  "subcategory": "mascot",
  "concepts": ["assistant", "coding", "friendly"],
  "keywords": ["robot", "cream", "teal"],
  "style": "motif-default-v1",
  "orientation": "front",
  "dimensions": {"width": 1024, "height": 1024, "unit": "px"},
  "artBox": {"x": 52, "y": 52, "width": 920, "height": 920},
  "anchors": {"neck": {"x": 0.5, "y": 0.46}},
  "compatibleCharacters": ["motif-bot"],
  "supportedActions": ["stand", "wave"],
  "sourceType": "vector",
  "source": {"file": "motif-bot-front-neutral-v1.svg", "reference": "user-supplied robot identity"},
  "version": 1,
  "status": "review",
  "preview": "motif-bot-front-neutral-v1.png",
  "license": "project-original"
}
```

`status` is one of `generated`, `review`, `canonical`. `sourceType` is one of `generated`, `vector`, `manual`, `derived`. `source.file` is project relative. IDs are immutable after canonical promotion; revisions increment version. Metadata for raster generated concepts must also record their generation prompt, source references and a statement that inferred riggability has not yet been implemented.

Concept sidecars also use `directionSelection: selected|not-selected`. This records the chosen design direction independently of art maturity: concept A is selected, while its current PNG remains `status: review`.

## Anchor vocabulary

Character core: `neck`, `headAccessory`, `faceAccessory`, `leftShoulder`, `rightShoulder`, `leftHand`, `rightHand`, `torsoAccessory`, `backAccessory`, `leftHip`, `rightHip`, `leftFoot`, `rightFoot`, `groundContact`. `leftHand` and `rightHand` identify the swap/grip locations. Optional internal arm curve controls are animation parameters, not visible elbow anchors. Prop families may add `grip`, `screenContent`, `hinge`, `surface` and `socket`. Coordinates are relative to each asset art box, with origin at its top-left.

## Validation and QA

1. File opens, dimensions match metadata, alpha is real where required, art does not clip, and unreferenced external resources are absent.
2. Render at master size and at 96 px mascot / 64 px prop. Check silhouette, face and meaning.
3. Compare palette and material to `STYLE_BIBLE.md`; reject strong gradients, plastic highlights and excess detail.
4. For puppet assets, test point, grip, push, wave, run and jump using simple rotations, curves or pose swaps. Inspect the action at phone size; avoid visible mechanical seams and require no realistic gait.
5. For UI, replace the content layer with a contrasting test image and verify masking, bezel and shadows independently.
6. Review a contact sheet in context. Mark approved assets `canonical` only after human selection; preserve earlier versions.

## Current phase boundary

Direction A is selected. The six phase 2 outputs remain **concept art**. The minimal vector puppet described in [MASCOT_REFINEMENT_BRIEF.md](MASCOT_REFINEMENT_BRIEF.md) is canonical v1; see [MASCOT_IMPLEMENTATION.md](MASCOT_IMPLEMENTATION.md). The wider prop, environment, UI and FX library remains outside this mascot task.
