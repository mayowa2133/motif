# Message-to-production-plan milestone

Date: 2026-09-30. Two message-level briefs produced different scripts, visual actions, shot sequences and correct endings through the same shared command. This demonstrates limited planning within the calendar and arena capabilities. It does not establish arbitrary-topic autonomy or production reliability across all possible briefs.

## Execution boundary and inputs

`scripts/motif_direct.py` invokes a **live Codex CLI planning backend**, reviews its output, generates narration, compiles the plan into the existing event engine, then renders and finishes. These successful evaluations were not interactively authored scripts saved by the parent Codex session. The parent authored the shared contract, compiler, tests and review tooling; the command's model calls authored the evaluated plans and script content.

Configuration: Codex CLI 0.149.1, existing ChatGPT login, explicit `MOTIF_PLANNER_MODEL=gpt-5.6-sol`, low reasoning, ephemeral read-only sessions in an empty working directory, schema-constrained responses, no tools requested. Actual prompts, JSONL responses and invocation records are preserved in each output directory. The desktop's configured `gpt-6.1-sol` failed on this CLI account; the explicitly selected model came from its freshly fetched catalog. No credentials or subscriptions were added, and no saved-response fallback was used. New productions use HyperFrames **0.8.97**; frozen projects retain their existing pins.

Inputs provide only message, audience, intended duration/tolerance and output slug:

- [Brief A](../briefs/planning/calendar-declined.json): free hour → focus proposal → person declines → unchanged calendar. Requested 15 seconds ±3.
- [Brief B](../briefs/planning/arena-no-winner.json): two answers → same check → both fail → hand both to a person for review. Requested 17 seconds ±3.

The executable [workflow and supported scope](PRODUCTION_PLAN_WORKFLOW.md) describes commands, dependencies, the schema, registry and error boundaries. The earlier producer remains supported legacy template mode.

## Deliverables and expected versus actual

| Check | A — declined calendar proposal | B — no arena winner |
| --- | --- | --- |
| Complete MP4 | [final.mp4](../videos/productions/planned-calendar-declined/renders/final.mp4) | [final.mp4](../videos/productions/planned-arena-no-winner/renders/final.mp4) |
| Mobile playback | [360 × 640](../videos/productions/planned-calendar-declined/renders/mobile.mp4) | [360 × 640](../videos/productions/planned-arena-no-winner/renders/mobile.mp4) |
| Initial model plan | [initial-plan.json](../videos/productions/planned-calendar-declined/initial-plan.json) | [initial-plan.json](../videos/productions/planned-arena-no-winner/initial-plan.json) |
| Consumed plan | [production-plan.json](../videos/productions/planned-calendar-declined/production-plan.json) | [production-plan.json](../videos/productions/planned-arena-no-winner/production-plan.json) |
| Planning review | [review record](../videos/productions/planned-calendar-declined/planning-review.json) | [review record](../videos/productions/planned-arena-no-winner/planning-review.json) |
| Expected ending | Proposal removed; existing appointment retained; no booking | Both fail; no selected winner; both sheets received by a person |
| Actual ending | Matches | Matches |
| Duration / frames | 15.566667 s / 467 | 15.300000 s / 459 |
| Picture | 1080 × 1920, 30 fps | 1080 × 1920, 30 fps |
| Encoded loudness | −16.08 LUFS | −16.09 LUFS |
| Encoded true peak | −1.67 dBTP | −1.71 dBTP |
| First/final encoded picture | Identical within run | Identical within run |
| HyperFrames check | 0 errors/warnings, 36/36 text contrast checks pass | 0 errors/warnings, 18/18 text contrast checks pass |
| Final-run planning corrections | 0 | 1 |

Both initial storyboards are preserved. Accepted storyboards and production artifacts derive from the same consumed plan; there is no second fixed script. Raw initial JSON and formatted accepted JSON may have different byte hashes even when the parsed plan is unchanged.

### Different generated narration

**A:** “Assistant spots an open hour at four. It proposes focus time, placing a dashed card there. The person presses decline, removing the proposal while the existing meeting stays. The original calendar remains visibly unchanged.”

**B:** “Here are answers A and B. Checking A reveals a route gap before its cross appears. Checking B with the same stencil reveals its gap before the cross. Both answers failed the same check. No winner; both go to a person for review.”

A chooses calendar wide/detail framing with a dashed proposal and a human decline interaction. B chooses a two-sheet overview, matched A/B close shots, a both-failed overview, and a receiving-person handoff. Neither performs `calendar.commit` or `arena.select`. These are different action sequences and consequences, not label substitutions.

## Meaning, action order and mobile inspection

In A, the proposal entrance completes at **4.69 s**. The person's press starts at **6.86 s**, completes at **7.04 s**, and the coral cross starts at **7.09 s**. Proposal removal completes at **7.99 s**. The original TEAM card never moves, no solid FOCUS card is revealed, and CALENDAR UNCHANGED appears in the ending hold at **11.13 s**.

In B, the same stencil and framing expose A's missing connection before its cross; A's check completes at **2.99 s**. The same process for B completes at **6.30 s**. “Same check” starts at **6.42 s**, and “Both failed” starts at **9.00 s**. Both marked sheets travel into the human hand from **12.12–13.12 s**, followed by “Human review” at **13.24 s**. No winner seal, successful route or selection event appears.

Manual inspection used decoded encoded-mobile frames: [calendar story samples](../validation/production-plan/planned-calendar-declined-mobile.jpg), [arena story samples](../validation/production-plan/planned-arena-no-winner-mobile.jpg), and [closer action evidence](../validation/production-plan/action-evidence.jpg). Labels and captions fit at 360 × 640. The decline is attributable to the human finger, the gap is visible before each failure mark, and both marked sheets remain identifiable in the receiving hand. The gap reveal before its overlaid cross is brief, approximately 0.29 seconds after the route settles; the detail samples preserve that evidence for review. This is sampled-frame inspection, not a subjective full-playback or listening judgment.

Actual speech alignment drives beat starts, captions and action cues. Exact ASR merges retain measured token intervals with their coarser precision recorded. Unmatched anchors or timing conflicts stop production; they are not silently retimed from a demo. Both exports fit their input duration ranges. Encoded finishing used a combined-mix gain for A and combined-mix loudness processing for B; both preserve the project target and peak ceiling. Subjective narration/SFX balance remains unassessed.

## Reviews, shared implementation and interventions

In the successful A run, the initial generated plan passed deterministic and live model reviews without correction. In B, review rejected an early “same check” claim and a described arrival not supported by its recorded action. The command's single bounded correction changed the opening to already aligned sheets, retained matched failure tests, added a both-failed hold, and preserved the human handoff. A second live review passed. That corrected model response is preserved; no plan was hand-edited.

The [shared-source snapshot](../validation/production-plan/shared-source-before-runs.json) and both `source-hashes.json` files are identical across the successful runs. The [independent saved-output results](../validation/production-plan/results.json) verify different narration, consumed wording, completed evidence before headlines, expected simulated states, actual encoded levels and duration, first/final video-stream equality, and unchanged shared source. All **363** frozen/legacy files checked against the [before snapshot](../validation/production-plan/frozen-before.json) are unchanged, including the canonical mascot, three demos, accepted focus-hour production and legacy producer.

Development exposed shared defects before the final evaluated pair. The [development fix record](../validation/production-plan/development-fixes.json) preserves the full history:

1. Protected macOS font flags made `copy2` fail; copy font bytes without system metadata.
2. The desktop model setting was unsupported by CLI authentication; add an explicit recorded integration model override.
3. Input paraphrasing and overly long scripts needed clearer planner constraints; measured duration remains the final acceptance gate.
4. Missing pose audit entries and early labels needed complete timing records and headline scheduling after physical evidence. Restore explicit timeline-registry initialization; measure SFX slots and mark intentional SVG overflow.
5. Add the missing `json` import in the finishing adapter.
6. Recover exact merged ASR word groups without inventing within-token timings.

The final evaluated pair was planned and rendered afresh after the last shared fix, using the complete updated implementation. Earlier attempts are separate and preserved, including one calendar export that had passed before the final aligner update. No preserved development-attempt folder was deleted.

Ten regression test methods pass. They cover legacy rejection behavior, booking without approval, a failed candidate becoming a winner, unsupported actions/assets, message/final-state disagreement, plan content reaching the composition, and measured ASR merge boundaries. Development layout fixtures were used for technical checks and are distinct from evaluated outputs. Those fixtures were not additional finished demos.

Manual work: implemented the shared planning contract/compiler/adapter; wrote the message briefs and development tests; selected the available backend configuration; diagnosed and fixed shared defects; invoked both commands; inspected mobile samples; wrote the reports. **No successful-run script, plan, event, caption, audio or picture was manually edited.** No commit or push was made.

## Remaining limits

The command depends on the signed-in Codex CLI and its account usage/model availability. This is a local integration, not a hosted product backend. The two successful evaluations are not evidence that every future model plan will pass within one correction.

Only the finite calendar/arena registry is supported. Calendar times remain illustrative fixed rows; full schedules and the no-opening branch are unavailable. Arena tests illustrate route checking; they do not evaluate real answer quality. Approved/booked and pass/selection actions have state tests but were not additional completed video evaluations here. Text-fit limits and 4–6 beat constraints are narrow; unsupported actions, missing assets, meaning review failures and duration conflicts stop the run.

Deterministic checks establish explicit state/order consistency, not natural-language truth. Model review can miss semantic or staging problems. ASR can produce coarse or unmatched anchors, and creative/mobile inspection plus subjective audio review remain human responsibilities.

The milestone is complete. Work stops here.
