# Motif visual system — proposal v0.1

Status: **direction A selected; mascot canonical v1**. Derived from the seven supplied videos' style family and the supplied robot's identity. The A raster concept remains exploratory; the editable vector puppet is the canonical character.

## Core idea

Motif looks like a tiny animation workshop made of inked paper, soft card and reusable joints. Ideas become touchable machines, places and games. The mascot is a cream robot with teal signals and a dark expressive display, rebuilt as a flat cutout puppet. Every frame should communicate its claim on a phone before its decorative details are noticed.

## Palette

| Token | HEX | Role |
| --- | --- | --- |
| `paper` | `#F4EBD8` | Primary robot shell, cards, light labels |
| `paper-shadow` | `#DCCDB3` | Cut edge and underside |
| `ink` | `#202C32` | Face display, typography, outlines |
| `ink-soft` | `#4C5B60` | Secondary text and hardware |
| `teal` | `#56BFB1` | Identity accent, joints, active states |
| `teal-light` | `#A6E5D6` | Face glyphs and small highlights |
| `coral` | `#DF806B` | Human warmth, emphasis and alternate UI state |
| `marigold` | `#EBC46B` | Attention and reward |
| `slate-blue` | `#64869A` | Environment support |
| `deep-teal` | `#254D50` | Dark background option |
| `plum` | `#554565` | Alternate scene background |
| `mist` | `#CBD7D0` | Light background option |

Use warm paper plus ink and teal in every mascot scene. Choose one scene accent from coral, marigold, slate-blue or plum. Background colors can vary, while the robot's identity colors remain stable. White text is allowed on ink or deep-teal surfaces only when contrast is at least 4.5:1 for body text.

## Shape and proportion

- Use A's broad head, compact bell-like torso, short limbs and oversized little feet as the mascot's silhouette. Keep the head approximately 44–52% of total height. Do not add limb segments merely to make the character resemble a conventional humanoid rig.
- Keep two small asymmetric leaf/antenna shapes, a dark rounded display, two expressive eye marks, a simple mouth, round side modules and a visible `<>` chest glyph. These are identity anchors; exact joint construction can vary by concept.
- Build bodies from broad simple pieces: rounded rectangles, flattened ovals, gentle trapezoids and short cylinders represented in 2D. Avoid many nested armor seams.
- Primary prop silhouettes should read at 96 px high. A detail that disappears at that size is expendable unless it carries meaning.
- Use corner radii in a small family: 4–8% of minor dimension for cards, 12–18% for devices, and 24–35% for soft character pieces. Mix precise functional rectangles with imperfect paper curves.
- Default hands are cute teal mitten shapes. Use five interchangeable hand states only: `mitten`, `open` (wave), `grip`, `point` and `fist`. No detailed fingers or knuckles. Prop and costume connection points may exist in metadata without becoming visible mechanical hardware.
- Arms are flexible cutout strips that can rotate, curve or stretch. Legs are short graphic shapes; chunky feet carry more expression than knees or ankles. Hide rigging complexity from the drawing.

## Surface, edges and light

- Matte card and paper are the default materials. Add fine monochrome grain at low contrast; keep text fields quieter than broad backgrounds. Texture must not make an asset appear dirty.
- Stack 2–4 planar pieces where depth matters. Show a 2–5 px darker cut edge at a 1024 px character master scale rather than a rendered bevel.
- Use one contact shadow per lifted layer, offset down-right by roughly 0.5–1.5% of its width, blur 0.5–1% and opacity 12–20%. For a whole figure, use a wider grounded shadow at 10–16% opacity.
- Lighting is diffuse and even. Small printed highlights on display glyphs are allowed; bloom, lens flare, mirror reflections and glossy plastic are not.
- Use outlines only where adjacent shapes need separation. Typical outline: 1.5–2.5% of a small prop's width, ink or ink-soft. No uniform thick black border around every piece.
- Preserve crisp silhouette edges with slight controlled irregularity. Torn edges are reserved for ephemeral paper notes and FX, not the robot's primary shell.
- Give physical props subtle shape-level imperfections, not texture alone: a gently drifting cut edge, slight asymmetry or a small natural tilt. Vary grain by paper, dark card and wood surface; retain clean silhouettes and consistent down-right layer shadows. Keep the effect restrained enough that assets still align and read at phone size.

## Space and environment

- Default to front-on, orthographic staging. A shallow tabletop, wall, shelf, proscenium or floor plane creates location. Side or top faces may be hinted with a single flat shape; no vanishing-point rendering for core assets.
- Build scenes in separable background, midground, character/prop and foreground layers. Leave attachment and occlusion zones for motion.
- Each beat should have one main visual proposition. Secondary set dressing supports location, never competes with the metric, device or character action.
- Use a character as a scale and reaction cue. A large object can occupy most of the frame when it is the metaphor.
- Reusable environments should have quiet, texture-bearing fields and at most three strong location cues before story props are added.

## Props, UI and screenshots

- Design a prop around its silhouette and one distinguishing feature. Internal lines should serve interaction or meaning.
- UI containers are physical paper/device shells around a replaceable content rectangle. Specify the content mask and foreground bezel separately. Screens can carry precise user-supplied UI; surrounding illustration remains simplified.
- Product screenshots retain their real content. Do not redraw tiny UI as illegible decorative marks. If details cannot be read at delivery size, crop to the relevant area or replace them with a clearly labeled abstraction.
- If understanding UI words is necessary to understanding a scene, enlarge or isolate that UI until the words are readable at the target mobile viewing size. UI used only as environmental evidence may become unreadable texture, provided the scene's meaning still reads through silhouette, icons, state and context. Never rely on tiny UI copy for an essential claim.
- Prefer data as tangible elements: chart bars are stackable strips; progress is a fillable vessel; comparison is a shared scale; selection is a bracket, gate or spotlight.

## Type and on-screen language

- **Headline:** short sentence or claim, bold rounded grotesk/sans, sentence case or selective uppercase. Place on Motif's own folded card or sign system, not the references' exact taped strip. Max two lines, 28–42 characters per line at 1080 × 1920 when practical.
- **Caption:** phrase chunks on small matte paper lozenges or cards, with stable baseline and restrained pop/slide. Keep 1–5 words visible at once. Use a high-contrast sans rather than imitating the references' serif word tiles.
- **CTA:** a large physical button, card, lever or selectable slot tied to the scene. The call to action is an interaction, not a generic floating pill.
- Type must be editable text in the video system. Rasterized text is for user-provided screenshots only.

## Motion and FX

- Motif motion has weight: quick travel followed by a short settle. Use a single clear action per beat, then hold long enough to read it. Avoid continuous idle motion across every layer.
- Faces blink or swap simple glyph states; head, antennae, arms, hand states and feet can move independently. Use the minimum visual pieces needed to read the action. An arm may stretch across a table, a grip may grow for a large prop, a leg may bend unnaturally, and feet may separate slightly during a jump.
- Favor clear silhouettes and pose swaps over anatomically correct motion. A gesture should read instantly even when the mascot is very small.
- Favor reveal, slide, stack, stamp, hinge, spring, peel and physically motivated handoffs. Use camera moves sparingly; move scene objects first.
- FX are sparse paper confetti, drawn sparks, cutout dust or flat speed marks. Reserve them for a state change.

## Storyboard gate before rendering

For every major beat, record these five answers in the existing storyboard before animation begins. A beat that only names a caption, reaction pose, or camera move is incomplete.

| Question | What the storyboard must show |
| --- | --- |
| Subject | The specific object or character whose state matters. |
| Action | What physically happens to or through that subject. |
| Visible before/after | The condition a viewer can compare without narration, followed by the changed condition or outcome. |
| Focal detail | The smallest feature that explains the result, and how the shot makes it legible at 360 × 640. |
| Consequence | What the outcome causes next in the world. |

- A result label reinforces visible evidence. It cannot be the first or only evidence of success, failure, selection, or completion. Show the condition, give the viewer a moment to recognize it, then confirm it.
- Frame the diagnostic detail rather than merely enlarging its container. A large document is insufficient if the relevant gap, mark, line, code region, or chart change stays small.
- Keep a meaningful relationship to the world during a close view: a character submits or receives the prop, a mechanism acts on it, or the tested piece visibly returns to the scene. Close views can simplify scenery while retaining an interaction.
- Match an ending instruction with an action. If narration says to review, show inspection or handoff; a celebration alone does not communicate review.
- Check the sequence without captions and at mobile size before rendering. If the outcome only reads through words, revise the storyboard first.

**Rejected storyboard, using the existing arena, answer sheets, stencil, Bot, and lens:** “Show A’s sheet; pop a FLAW label over it. Show B’s sheet; pop a PASSES label. Cut to Bot with a SELECTED banner and lens. The physical link remains too small or unseen.” The labels announce a comparison but the viewer cannot see what changed.

**Improved storyboard with those same assets:** “A’s answer sheet enters the close view with two tidy checked lines. The link stencil lands; the shot favors the route and reveals its center gap before a coral failure mark. B’s sheet receives the same stencil in the same framing; its route connects both ends before a teal confirmation mark. The selected B sheet moves into Bot’s hand, where the lens inspects it.” The route explains the outcome and the handoff explains the next step. For a future production, let the stencil or character physically act on the route when the available assets and timing permit it; this accepted Demo 02 remains the regression reference, not a new edit request.

## 9:16 layout and readability

- Design at 1080 × 1920; test at 360 × 640. Keep essential words and faces in the central 900 × 1540 px unless a delivery platform's measured safe area is narrower.
- Reserve the top ~12% for app chrome uncertainty and the bottom ~18% for caption/CTA and platform controls; validate final platform-specific placement rather than treating these as universal masks.
- Main subject should remain recognizable at 180 px high; mascot identity should survive at 96 px high; face expression at 64 px head width.
- Minimum planned live type at delivery: 52 px for primary headline, 44 px for captions, 34 px for short labels; verify with real font, case and contrast.
- Do not put critical text over busy texture. Break long claims into multiple beats.

## Consistency gates and forbidden traits

Every new asset must use the palette roles, matte surfaces, shallow perspective, clear silhouette and standardized shadow logic. Mascot assets must retain the cream shell, teal details, dark display, two ear/antenna cues and chest code mark. Compare new work against a canonical contact sheet once a direction is approved.

Reject: photoreal or glossy 3D rendering; chrome, glass or neon bloom; elaborate armor seams; visible elbow/knee machinery; five-finger hands; realistic gait or joint behavior; thin pale lines that vanish on mobile; stock vector gradients; generic emoji expressions; deep perspective; unreadable fake UI; noisy texture under text; an orange square mascot like the source guide; exact recreations of source headlines, captions, characters or compositions.
