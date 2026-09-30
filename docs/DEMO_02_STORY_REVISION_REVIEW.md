# Motif Demo 02 — story revision review

Status: **accepted and frozen as Motif's completed second prototype on 2026-09-30**. The first cut remains the approved reuse benchmark. This revision shows evaluation through visible action. It is an illustrative comparison, not a claim about measured answer quality. The frozen media and event hashes are recorded in [the Demo 02 baseline](DEMO_02_BASELINE.md).

## Deliverables

| Item | File |
| --- | --- |
| Full 1080 × 1920 Reel | [story revision MP4](../videos/motif-arena-reel/renders/motif-demo-02-arena-story-revision.mp4) |
| 360 × 640 playback copy | [mobile MP4](../videos/motif-arena-reel/renders/motif-demo-02-arena-story-revision-mobile.mp4) |
| Frames from the final encoded Reel | [mobile contact sheet](../videos/motif-arena-reel/proof/story-revision-contact-sheet.png) |
| Editable composition | [generator](../scripts/build_motif_arena_reel_story_revision.py) · [scene events](../videos/motif-arena-reel/story-revision-events.json) · [audio plan](../videos/motif-arena-reel/audio-plan.json) |

## Visual story check

- **Visible test:** A and B each receive the same large two-ended paper stencil. A initially has a neat answer sheet with two checked lines. When the stencil lands, its route stops at an exposed center gap. B receives the matching stencil and its route connects the same endpoints. The red gap and continuous teal path carry the result; small text is secondary.
- **Readable shot:** The wide arena lasts 2.08 seconds. A then fills the frame from 2.08 to 4.98 seconds, followed by a matching B close view until 6.67 seconds. At 360 × 640, both paper routes and outcomes are visible in the encoded frames. The crowd and arch leave these close views.
- **Final review action:** The B sheet carries a selection ribbon, moves from the side into Motif Bot's open hand, and receives a moving inspection lens as the Bot changes to a thinking expression. The final frame says “B SELECTED” rather than making an absolute “BEST” claim. No podium or ranking of A and C appears.

## System fit and scope

The approved arena, locked canonical Motif Bot, paper palette, edge treatment, shadow direction, caption component, GSAP motion vocabulary, `af_nova` narration, and existing SFX remain. The two close views reuse the same answer sheet and stencil geometry, plus the existing Scene 03 incoming code ticket. Three new modular SVG props have individual metadata: [answer sheet](../assets/scenes/scene-02/story/answer-sheet.json), [link test stencil](../assets/scenes/scene-02/story/link-test-stencil.json), and [inspection lens](../assets/scenes/scene-02/story/inspection-lens.json). No new motion engine action, mascot design, environment, or broad prop set was created. The prior cut's source was preserved in [versions/first-cut](../videos/motif-arena-reel/versions/first-cut/).

## Verification and limits

HyperFrames check passed with zero lint, runtime, layout, motion, or contrast findings; 27/27 text checks passed. The final file is H.264/AAC, 1080 × 1920, 30 fps, 10.20 seconds; the phone copy is 360 × 640 at the same duration. Encoded audio measures about −16.2 LUFS integrated and −3.0 dBTP. Final encoded frames were inspected at the arena establish, both tests, selection, handoff, and ending.

The connection test is a deliberate visual metaphor. It demonstrates one missing condition in A and a present condition in B; it does not explain the content of the answers or evaluate C. Subjective narration and SFX balance still need a person's listening judgment.

The accepted cut also leaves four directing limits for future work: the test is diagrammatic rather than a fully physical interaction; the relevant route could occupy more of each close view; the paper close views lose some connection to the arena; and the lens reads more like an overlay than a tool held by Bot. These observations inform the [pre-render storyboard gate](STYLE_BIBLE.md#storyboard-gate-before-rendering) and do not reopen Demo 02.

**Stop point:** Demo 02 is frozen. No further visual refinement, variant, or prop library work is started.
