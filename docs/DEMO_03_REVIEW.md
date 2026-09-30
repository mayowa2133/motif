# Motif Demo 03 — calendar approval production review

Status: **visual story approved, audio finished, and frozen as a regression baseline on 2026-09-30**. Demo 01 and Demo 02 remain frozen. This 12.8-second 9:16 Reel is an illustrative workflow: an assistant notices overlapping commitments, suggests a free time, waits for human approval, and only then changes the schedule. It makes no product capability claim. See the [accepted baseline](DEMO_03_BASELINE.md).

## Deliverables

| Item | File |
| --- | --- |
| Complete 1080 × 1920 MP4 | [audio-finished Demo 03](../videos/motif-calendar-reel/renders/motif-demo-03-calendar-approval-audio-finished.mp4) |
| 360 × 640 playback copy | [audio-finished mobile MP4](../videos/motif-calendar-reel/renders/motif-demo-03-calendar-approval-audio-finished-mobile.mp4) |
| Encoded frames at mobile size | [final contact sheet](../videos/motif-calendar-reel/proof/final-contact-sheet.png) |
| Initial plan, unchanged after creation | [initial storyboard](../videos/motif-calendar-reel/STORYBOARD_INITIAL.md) |
| Planning self-review and revised plan | [pre-render review](../videos/motif-calendar-reel/PLANNING_REVIEW.md) · [production storyboard](../videos/motif-calendar-reel/STORYBOARD.md) |
| First encoded version | [first render](../videos/motif-calendar-reel/renders/motif-demo-03-first-render.mp4) · [first-render review](../videos/motif-calendar-reel/FIRST_RENDER_REVIEW.md) |
| One correction | [first-versus-corrected notes](../videos/motif-calendar-reel/CORRECTION_NOTES.md) |
| Audio-only finish after visual approval | [gain path and encoded measurements](../videos/motif-calendar-reel/AUDIO_FINISHING.md) |
| Editable production | [composition generator](../scripts/build_motif_calendar_reel.py) · [structured events](../videos/motif-calendar-reel/scene-events.json) · [audio plan](../videos/motif-calendar-reel/audio-plan.json) |
| Asset and audio provenance | [five SVG assets](../assets/scenes/demo-03/) · [audio source and license manifest](../videos/motif-calendar-reel/audio-source-license-manifest.json) |

## What was planned before rendering

The message-level brief gave no shot list. The initial storyboard chose a persistent paper calendar with two solid event cards, Motif Bot, a human fingertip, and a physical approval tab. Its internal review caught an incorrect implication: moving the real event toward 4 PM during the suggestion beat could suggest the schedule changed before permission. The saved revised storyboard made the proposed placement a separate pale dashed slip and kept the real solid card visibly at 3 PM until approval. The narration added “But the calendar stays put.” This was a planning change made before animation and the first finished render.

The planned visual evidence carries the story: two solid cards collide at 3 PM, a dashed possible placement appears in the vacant 4 PM row, the finger presses the tab while the conflict persists, and the real card moves only after that touch. The time labels and APPROVE label orient the viewer; captions reinforce the sequence rather than supplying its only explanation.

## What the encoded first render revealed

The first MP4 showed the full conflict → proposal → approval → actual change in its encoded frames at phone scale. The single defect selected for correction was the checkmark baked into the approval tab before the finger pressed it. The first render and matching source snapshot remain preserved. First MP4 SHA-256: `2ada16bf32af70a5f94948c3f1086b6809690a2ea353a931f52d3c395ce1480f`.

## What changed afterward

One bounded correction removed the prechecked symbol from the tab and revealed a separate check only after the press. The corrected encoded frames show an empty tab at 7.8–8.4 seconds, finger contact around 8.7 seconds, a check around 9.4 seconds, and then the solid FOCUS card moving to 4 PM. The final calendar shows separate CALL and FOCUS bookings. Corrected MP4 SHA-256: `01db54728fecc7c1c93775f0c82dd765da55f51a95c4c041ae48c9f1e3ad84c4`.

## Reuse and new work

| Category | Result |
| --- | --- |
| Existing assets and components reused | Locked canonical Motif Bot v1 poses, approved warm wall and floor/desk pieces, paper palette and shadow treatment, caption/sign component, GSAP event vocabulary and motion engine, HyperFrames renderer, local Kokoro `af_nova` narration workflow, and previously cleared SFX. |
| New modular assets | Five independent SVGs with JSON metadata: calendar board, appointment card template, proposal slip, approval tab, and human fingertip. |
| New reusable capabilities | None. The existing structured event system and action vocabulary were sufficient. |
| Bespoke scene code | [One isolated generator](../scripts/build_motif_calendar_reel.py) assembles the specific calendar, actor, camera, captions, audio clips, and event plan. It is scene code, not a new framework component. |

## Verification and limits

HyperFrames check passed with zero lint, runtime, layout, or motion findings and 45/45 text-contrast checks. The final encoded file is H.264/AAC, 1080 × 1920, 30 fps, 12.8 seconds; the mobile copy is 360 × 640 at the same duration. Encoded frame samples were visually inspected at the conflict, proposal, wait, press, card movement, and final schedule. A Whisper transcription of the encoded file detected the 33 spoken words in the expected order; this is an automated check, not a subjective listening judgment.

The initial encoded mix measured **−24.43 LUFS integrated and −9.87 dBTP**. After visual approval, a separately authorized audio-only pass applied +8.2 dB to the combined mix. The accepted encoded version measures **−16.24 LUFS integrated and −1.68 dBTP**. Its H.264 video stream and duration match the approved visual cut exactly. Narration clarity and SFX balance still need a person's listening judgment. The calendar is intentionally simple and the fingertip is symbolic; neither establishes that a real product can inspect or edit a calendar.

For future videos, avoid separately narrating several phrases that explain the same unchanged visual state, and size the final hold to the information the viewer needs to read. These are non-blocking timing lessons, not a request to reopen this accepted edit.

**Stop point:** Demo 03 is frozen. No Demo 04 or broad prop library work was started.
