# Motif — production planning evidence

Read-only review of the accepted **calendar-declined** and **arena-no-winner** runs. Begin with the original workflow and milestone review in `docs/`, then trace each run below. No new planning, rendering or creative edit was performed.

## Trace the two runs

| Step | Calendar | Arena |
|---|---|---|
| Exact input brief | `briefs/planning/calendar-declined.json` | `briefs/planning/arena-no-winner.json` |
| Run folder | `videos/productions/planned-calendar-declined/` | `videos/productions/planned-arena-no-winner/` |
| Initial model output | `initial-plan.json` | `initial-plan.json` |
| Correction | None; initial plan accepted | `corrected-plan.json`; rejected first review and successful second review preserved |
| Accepted model output | `production-plan.json` | `production-plan.json` |
| Correction/review summary | `planning-review.json` | `planning-review.json` |
| Renderer-consumed event plan | `scene-events.json` | `scene-events.json` |
| Actual renderer input | `index.html` (embedded event JSON verified equal to `scene-events.json`) | Same |

Each run also includes actual model prompts (`*-input.txt`), sanitized invocation records, deterministic/model reviews, initial/final storyboards, narration and measured word transcript, action/label/alignment records, backend/source hashes, run record and encoded verification. Calendar initial and final JSON represent the same parsed plan; byte formatting differs. Arena final JSON represents its recorded corrected model output. Initial arena review prompts retain the initial timings even though final event files were overwritten by the correction; a separate initial `scene-events.json` was not preserved.

## Decision origins

These classifications describe the existing implementation, not a general-purpose director.

| Decision | Origin | Evidence and boundaries |
|---|---|---|
| Narration wording | **Model-generated** | `beats[].narration` in initial/corrected plans. `motif_plan.narration()` deterministically concatenates it. Voice `af_nova`, speed 0.85 and synthesis settings are **fixed by a supported template** in `motif_direct.py`. |
| Outcome | **Model-generated**, checked/realized **deterministically** | Model chooses `expected_final`, ending and action results to express the human brief. `motif_plan.review_plan()` simulates finite state transitions and verifies agreement; compiler selects the supported visual action. No arbitrary outcome implementation is generated. |
| Meaningful action order | **Model-generated** | Ordered `beats[].actions` and narration cue phrases. Validator enforces prerequisites; compiler derives sorted timed events. Internal press/cross/fade, check/gap/cross and handoff choreography is **fixed by a supported template**. |
| Shot choices | **Model-generated** within a finite registry | Model supplies `beats[].shot`: two calendar choices/four arena choices. Exact positions, scale, perspective, scene geometry and calendar punch-in amount are **fixed by a supported template** in `calendar_world()`, `arena_world()` and `compile_plan()`; they are not model-generated layouts. |
| On-screen text | **Model-generated** plus **fixed by a supported template** | Captions, headlines and calendar TEAM/FOCUS labels come from the plan. TODAY/3 PM/4 PM rows, candidate A/B labels, marks and typography/card geometry are authored. Events replace/reveal labels **deterministically**; empty headlines persist under the existing template behavior. |
| Timing | **Deterministically derived** plus **fixed by a supported template** | Model narration and cue choices influence timing indirectly. `align()` uses measured speech word times; `compile_plan()` computes starts, label delays and end holds. Motion durations, offsets, easing, 30 fps and 1.2-second ending hold are authored constants; model does not generate arbitrary event timestamps or curves. |

## Source and provenance

- `scripts/motif_direct.py`: live CLI invocation, prompt assembly, bounded correction and run orchestration.
- `planning/PLANNER.md`: actual shared model contract.
- `schemas/production-plan.schema.json` and `schemas/planning-review.schema.json`: structured output contracts.
- `scripts/motif_plan.py`: capability registry and state/order validation.
- `scripts/motif_plan_compile.py`: finite world layouts, speech alignment and plan-to-event binding.
- `scripts/motif_plan_finish.py` and `scripts/motif_produce.py`: finishing adapter and imported shared helpers; legacy producer is separate template mode.
- `validation/production-plan/`: original shared hashes, development interventions, frozen-file hash baseline and existing saved-output results.
- `review/RUN_METADATA.json`: available model identifiers, timestamp observations, fallback/intervention records and consumption checks. **Exact invocation boundaries and server-resolved model identifiers were not recorded.** Filesystem times are labeled observations, not invented invocation times.
- `MANIFEST.json`: SHA-256 and byte count for every payload, original-source hashes and explicit transformations.

The 31-file source hash snapshots match across both runs and match current source bytes. Assets, dependencies and fonts referenced by those snapshots are intentionally not bundled. The implementation was uncommitted; current Git HEAD is only a packaging-time observation and is not the run's full source revision.

## Known issue and scope

See `review/KNOWN_ISSUES.md`: **PROPOSED persists from proposal clearance at 7.99 s until CALENDAR UNCHANGED at 11.13 s.** No fix was made. Existing pass reports remain unchanged; their label check does not establish that every persistent label stays current.

This is a small inspection bundle, not an executable production distribution. Exact original documents may link to omitted videos, sampled frames or development attempts. Already evaluated MP4s, audio, fonts, dependencies, raw session logs, credentials, environment/authentication files and the broader asset library are excluded. Only structured production/review outputs are included, never private reasoning. Preserved attempts remain in place. No commit or push was made.
