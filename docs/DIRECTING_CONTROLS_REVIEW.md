# Directing-controls milestone review

## Result

Explicit focus decisions now reach the renderer through schema 1.1 `focus_target` and `framing`. Headline lifecycle is explicit, selection attaches to A or B, narration is reviewed for audience fit, and verification separates structured checks from encoded measurements. One fresh live-planned Reel completed with **zero corrections**, using the shared implementation fixed before its brief was chosen. Work stops here for review.

## Deliverables

| Artifact | Location |
|---|---|
| Complete Reel, 16.83 seconds | [final.mp4](../videos/productions/planned-evidence-selects-b/renders/final.mp4) |
| Mobile version | [mobile.mp4](../videos/productions/planned-evidence-selects-b/renders/mobile.mp4) |
| Preserved first encoded render | [first.mp4](../videos/productions/planned-evidence-selects-b/renders/first.mp4) |
| Exact fresh brief | [evidence-selects-b.json](../briefs/planning/evidence-selects-b.json) |
| Initial / accepted model plans | [initial](../videos/productions/planned-evidence-selects-b/initial-plan.json), [accepted](../videos/productions/planned-evidence-selects-b/production-plan.json) |
| Review / correction record | [planning-review.json](../videos/productions/planned-evidence-selects-b/planning-review.json) |
| Compiled renderer input | [scene-events.json](../videos/productions/planned-evidence-selects-b/scene-events.json) |
| Validated one-field focus comparison | [image](../validation/directing-controls/validated-focus-differential.png), [results](../validation/directing-controls/differential-results.json) |
| Diagnostic and A/B selection comparisons | [differential-mobile.png](../validation/directing-controls/differential-mobile.png) |
| Actual encoded frame samples | [contact sheet](../validation/directing-controls/fresh-encoded-contact-sheet.jpg) |
| Targeted regression output | [16 passing tests](../validation/directing-controls/regression-results.txt) |
| Source changes from packaged baseline | [implementation.patch](../validation/directing-controls/implementation.patch) |
| Operative fields and limits | [DIRECTING_CONTROLS.md](DIRECTING_CONTROLS.md) |

The initial and accepted plans are the same parsed model output, with different JSON formatting. Actual prompts/invocation records and the first compiled attempt remain in the run folder. They were not supplied as a manual shot list or script.

## Differential proof

The initial compiler-only test held saved assets, narration, timing and actions constant and changed A's `framing` from subject to detail. Exactly one camera event changed; the real diagnostic region grew from **608.1 to 784.5 delivery pixels**, a **29%** enlargement. A/B detail transforms and projected diagnostic bounds match exactly. This one-A variation is an isolated compiler test: it intentionally breaks the complete-plan comparison rule, which requires matching A/B framing.

A supplementary test uses two **fully validated** copies of the fresh accepted plan. Only the final `focus_target` changes: `answer-B.sheet` → `answer-B.connection`. Shot, framing, assets, narration and actions remain identical. Both complete plans pass deterministic review. The camera transform and painted frame change, while B's identity, pass evidence and selected stamp stay visible. These are controlled still-frame fixtures, not additional Reels or new live-model outputs.

Selecting A versus B also produces different attached stamp targets and different pixels, with unrelated rendering inputs constant. The earlier selection fixtures deliberately retain the old narration/labels and are only binding tests; their “human review” wording is not a new narrative claim. The fresh Reel provides the coherent B-selection story.

The decline regression clears PROPOSED at the decline beat's start, before proposal clearance. State actions cannot `keep` an earlier headline. The old calendar export is unchanged.

## Fresh supported production

Message: “Two candidate answers receive the same check. A fails and B passes. The assistant selects B based on that evidence.”

Generated narration:

> Two candidate answers face the same connection check. First, the assistant checks A; a missing link shows why it fails. Then it checks B; the complete route provides passing evidence. Based on both results, it chooses B, so the evidence drives the decision.

The speech discusses the idea and consequence; it does not narrate crosses appearing, dashed graphics or renderer operations. The connection remains an illustrative metaphor, not a real answer-quality evaluator.

The model chooses paired establishment, matched A/B connection detail, and B-sheet subject framing for selection. The compiler computes their transforms and executes the existing finite choreography. A completes failure at **5.64 s**, then A FAILS starts at **5.76 s**. B completes passing at **8.70 s**, then B PASSES starts at **8.82 s**. B's attached selection completes at **12.81 s**, then B SELECTED starts at **12.93 s**. Earlier headlines clear at the new beat boundaries.

The live plan/data reviewer passed, including audience narration, with no correction. Encoded 360×640 samples show A's gap and B's complete route before their confirmation marks; B's attached stamp remains readable through the ending. The initial same-check caption establishes the intended procedure; matching physical checks subsequently demonstrate it. The presentation remains a calm explainer, not evidence that Motif reaches the references' entertainment ceiling.

## Verification provenance

| Kind | Recorded evidence |
|---|---|
| Pre-render data | State/order validator and live model data review pass; caption starts match measured speech anchors; event times sorted. [pre-render-checks.json](../videos/productions/planned-evidence-selects-b/pre-render-checks.json) |
| Framework check | 0 lint/runtime/layout errors or warnings; 9/9 visible text contrast checks pass. No motion sidecar assertions were enabled. [check.log](../videos/productions/planned-evidence-selects-b/check.log) |
| Encoded measurement | 1080×1920, 30 fps, 505 frames, 16.833333 s; **−16.44 LUFS**, **−1.79 dBTP**. Within the preserved loudness tolerance/peak ceiling; first/final video stream and duration match. [verification.json](../videos/productions/planned-evidence-selects-b/verification.json) |
| Sampled painted frames | Agent inspected decoded final-MP4 samples and real differential snapshots. [fresh-run-results.json](../validation/directing-controls/fresh-run-results.json) |
| Human playback / subjective listening | **Not assessed.** Plan/data review and sampled agent inspection do not replace these. |

The finishing adapter references the earlier pre-render result by path/hash. It no longer writes literal `plan_and_event_order=True` or `speech_aligned_captions=True` as post-encode checks. The generic keyframes diagnostic could not enumerate Motif's JSON-generated SVG tweens; its canvas-only ghost fallback was inapplicable. Those diagnostic logs are preserved; no successful keyframes-tool result is claimed.

## Provenance, interventions and limits

Explicit requested backend: `gpt-5.6-sol`, Codex CLI 0.149.1, existing ChatGPT login, low reasoning. Two successful live calls: planner and data reviewer. Start/end timestamps are now captured around the calls. A separately resolved server model identifier is still unavailable; no saved response or model fallback was used in this run. See [fresh-run-results.json](../validation/directing-controls/fresh-run-results.json).

Shared implementation work included the typed registry/camera fitter, attached stamps, label lifecycle, narration contract/reviewer and reporting changes. A development snapshot exposed a clipped Bot; before selecting the fresh brief, the shared arena builder moved the complete canonical Bot outside the work-prop camera into an authored supporting foreground slot. No evaluated script, shot list, plan, event, caption, audio or picture was hand-edited. The initial encoded render is preserved.

New projects use HyperFrames **0.8.98**, upgraded from 0.8.97 after a fixture passed its full check. Frozen projects keep their pins. The fresh run matches all **32** hashes in the implementation snapshot taken before choosing its brief. All **596** preserved baseline files match, including stored assets, canonical mascot, frozen demos, previous accepted productions and the legacy producer. [Preservation results](../validation/directing-controls/preservation-results.json).

There are still two supported worlds, six containers, finite focus targets and authored choreography. Bounds are registered for that geometry, not arbitrary visual understanding. No new complete calendar-focus production was evaluated here; its headline defect has a structural regression. No new assets, mass library, framework replacement, dashboard, arbitrary code, commit or push were produced. The implementation remains an uncommitted working tree with explicit source hashes.
