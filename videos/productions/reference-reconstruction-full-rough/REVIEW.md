# Full-reference reconstruction — moving rough

**Status: ready for rough review, not final art approval.**

Codex-assisted, reference-led production using Motif. The agent directed this bounded reconstruction from the supplied video and existing shot map. This does not demonstrate arbitrary-topic autonomous planning, and it is not a verified product announcement.

## Review files

- `renders/full-film-rough.mp4`: complete 1080 × 1920 moving assembly.
- `renders/mobile.mp4`: native 360 × 640 preview.
- `renders/comparison.mp4`: synchronized supplied reference left / Motif rough right, 1×, only reconstruction audio.
- `review/full-film-overview.jpg`: whole-film context sheet.
- `review/boundaries-and-stairs.jpg`: source / rough pairs at the approved passage boundaries and staircase transition.
- `SOURCE_CONTENT.md`: exact source attributions, pending portrait originals, and unverified claims.

All three movies contain **1262 frames at 30 fps: 42.066667 seconds**, using the existing 20-shot map and its source-frame boundaries. No picture retiming. The source’s longer audio tail is excluded.

## Locked passage

The approved **[436,600)** wash → terminal → scanner is reused from byte-identical copies of its full/native movies. Its source project and previous versions remain preserved. No new finishing pass, redraw, caption changes, choreography changes or sound remix were applied to that section.

The full-film export necessarily encodes its picture again; it is not a byte-identical concatenation. Verification compares all 164 inserted frames against the approved movies and checks both originals/copies by SHA-256. The prepared master copies the approved decoded audio samples at unity gain before the full-film AAC encode. It therefore does not claim that the complete film’s encoded AAC packets equal the old standalone passage.

## Remaining actions

| Section | Rough action / consequence |
| --- | --- |
| Gym | Canonical grips follow the rising/dropping bar. Attached instruction slips add burden while the needle moves into red. |
| Archive / answer | Notes land on the same labeled file; pencil reaches its checkbox before a check and duplicate sheet appear. |
| Race / skill introduction | Loaded car travels less distance, free car crosses first; gauge deteriorates. Three named, pending portrait cards introduce the audit document. |
| Classroom / shouting | Marker isolates the duplicate-check quote; held megaphone projects waves toward capitalized instructions. |
| Step scripts | Bot climbs to the independent upper platform. The same staircase collapses afterward; the bot remains supported, following the source’s end pose. |
| Permission | Lens follows proposed rows. The permission gate remains locked and the apply choice remains unanswered. |
| Evidence / research | Quoted developer post; findings attach to three named files before the source-reported 70 count; bot grip follows test lever before source result strip appears. |
| Cost / accuracy / takeaway | Exaggerated cost bars and creature reaction; three arrows enter and remain in the target before bullseye appears; guide fans and `AUDIT` types into an illustrative comment field. |

## Composition and finish assessment

The complete sequence now exposes rhythm, relative character scale, action occupancy and hard-cut handoffs in context. Headline and caption treatments remain editable, using the project-scoped `reference-expressive-v1`. Shapes, movement and before/after states carry the main meaning; fine text remains secondary at mobile size.

The approved central passage is the quality baseline. **New shots are intentionally simpler and less materially rich.** They do not yet match the source’s varied cut edges, layered dressing, debris or surface nuance. The gym, archive, skill introduction and evidence intro retain larger empty zones; the race uses simplified track dressing. This is staging evidence, not a claim that all 20 shots now match the finished section’s art quality.

The original portrait media and source post/article assets remain unresolved. Explicit portrait slots and attributed editable text prevent invented identities or fabricated screenshots. Dense source quotation cards cannot be fully read during their brief source-length shots; headline, file labels, count and physical action remain the immediate story cues.

New captions are phrase blocks fitted to shot windows, not final word-aligned captions. New voice cues are local Kokoro scratch performances; some are sped up to fit short source shots. Sparse reused effects support contacts. No music was added. The full rough measures approximately **−17.77 LUFS / −1.76 dBTP**; the approved section was kept at unity rather than changing its mix to normalize the whole scratch assembly. No subjective listening judgment is claimed.

## Engineering evidence and limits

- Current HyperFrames **0.8.99**, Motif event engine and primitives remain unchanged. Canonical mascot geometry and default style documents remain unchanged.
- New graphics are independent SVG groups plus 18 exported, shot-required prop pieces with metadata. Scene geometry, placement, captions and finite events are reconstructable from `build.py`, `scene-events.json`, `caption-events.json` and `reconstruction-timeline.json`. This is a bounded production, not a speculative global library.
- Strict check: `check-final-03.json`; no lint/runtime/layout/contrast errors or warnings. Automatic motion assertions are disabled; a passing check does not prove every contact or creative similarity.
- `verification.json` records frame counts, dimensions, all 19 adjacent-frame cut checks, inserted baseline frame correspondence, shared full/native/comparison AAC payload and original baseline hashes.
- Encoded picture was preserved during audio muxing. Both exports use hardware GPU / `drawelement` capture. Normal-speed comparison and native playback were observed; decoded overview and boundary frames were visually inspected. This is not a subjective full soundtrack review.
- Large local material files remain external composition dependencies. These HTML sources are not claimed to be a self-contained portable bundle. Review movies contain no font source package.
- Initial drafts, correction renders and pre-platform-fix assemblies remain preserved. Git HEAD remains `d2805cd8720c61811f3b4e5b47a10a581114cbff`; no commit, push or deletion.

## Rebuild

From repository root: run this project’s `build.py`; run `audio.py` only if refitting its frozen scratch narration. Render the root and `native-mobile` projects with the pinned CLI, then use `deliver.py` with the corresponding picture filenames. Audio is framework-owned in the editable composition; delivery uses the prepared master so all three review movies share one AAC payload.

## Review decision

The next decision is whether the **complete film’s pacing, focal scale, transitions and physical story beats** are right. Remaining surface work and final voice/caption timing wait for that review. Work stops here; no further polish, new framework, mass library, commit or push.
