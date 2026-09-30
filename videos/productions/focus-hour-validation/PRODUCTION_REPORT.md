# Workflow validation 01 — open hour for focus

Status: **complete for human review**. This is a new brief within the approved calendar visual family, not Demo 04 and not a change to the frozen Demo 01–03 baselines. The illustrative story is: a 3 PM CALL exists, 4 PM is open, the assistant suggests a FOCUS block as a dashed proposal, a person approves, and only then a solid FOCUS block is booked.

## Deliverables

| Item | File |
| --- | --- |
| Full 1080 × 1920 finished MP4 | [final.mp4](renders/final.mp4) |
| 360 × 640 playback copy | [mobile.mp4](renders/mobile.mp4) |
| Preserved first encoded render | [first.mp4](renders/first.mp4) |
| Encoded frames sampled at phone size | [final mobile contact sheet](proof/final-mobile-contact-sheet.png) |
| Input, initial storyboard, and pre-render review | [brief](brief.json) · [initial storyboard](STORYBOARD_INITIAL.md) · [review](STORYBOARD_REVIEW.md) |
| Editable data and assembly | [scene data](scene-data.json) · [event plan](scene-events.json) · [audio plan](audio-plan.json) · [calendar template](../../../scripts/motif_calendar_template.py) |
| Encoded checks and provenance | [verification.json](verification.json) · [audio source and license manifest](audio-source-license-manifest.json) |

## What the one-command run did

The command `python3 scripts/motif_produce.py run --brief briefs/focus-hour-validation.json` saved the initial storyboard and deterministic review before narration or rendering. It generated a new `af_nova` take, used its word transcription for caption handoffs, assembled the existing calendar pieces, passed HyperFrames checks, preserved the first MP4, finished the combined soundtrack, and wrote final verification. The successful run required no edit after its first render. The video is illustrative and asserts no product calendar capability.

The first encoded mix measured **−24.14 LUFS and −3.99 dBTP**. Simple gain could not reach the project target within the peak ceiling because of a transient. The encoded final mix measures **−16.04 LUFS and −1.74 dBTP** after combined-mix loudness processing. Both full files are **13.366667 seconds** and share the same encoded H.264 stream hash. The final has **401 frames**. The full video SHA-256 is `0db612d0d196002b642691fcea4b4e54625dec32751377989e97668eaea9d329`.

HyperFrames check found zero lint, runtime, layout, or motion issues, and **42/42** text contrast checks passed. The sampled mobile frames show an empty 4 PM row, a dashed proposed FOCUS slip, a person's press, a visible approval check before the “Only then” caption, and a solid FOCUS card replacing the proposal. The “BLOCK BOOKED” headline follows the visible solid card. These are visual and automated observations; no subjective listening approval was made.

## Reuse and intervention record

The locked Motif Bot, Scene 01 floor and desk, approved warm wall, Demo 03 calendar SVG props, shared caption/sign treatment, GSAP motion engine, structured events, HyperFrames renderer, Kokoro voice, and cleared SFX were reused. **No new SVG asset or motion-engine action** was needed. The new reusable code is the local [`motif_produce.py`](../../../scripts/motif_produce.py) entry point and one parameterized calendar scene template. Template-specific script, fixed 3/4 PM staging, and event transformations remain authored code; they are disclosed rather than presented as a general director.

During workflow development, an initial storyboard gate rejected wording that did not explicitly call the proposed slip dashed. The first development render exposed a premature “BLOCK BOOKED” headline and overlapping proposal/solid text; event-order checks and timing were tightened. The first loudness check rejected a quiet mix with a high transient. A later encoded check caught AAC true-peak overshoot and a short loudness-filter tail; the finisher now leaves headroom and trims that tail. Word alignment then exposed that “Only then” arrived before the approval mark was clearly visible; the press and hand withdrawal were moved earlier. These were **pipeline and template interventions before the successful one-command validation run**. The final run preserves its own first render and final render.

## Limits

This validates one constrained calendar proposal template, not arbitrary-topic autonomy. A different metaphor or environment still requires authored staging and likely bespoke scene code. The script and visual beats come from the template; the message-level brief chooses the supported scenario and labels. The timing gate uses a fixed script and its 34-word alignment, so script changes require updating the template. Visual appeal and narration/SFX quality require human judgment. The successful final file is a workflow proof, not an accepted fourth regression baseline.
