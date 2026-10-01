# Known editorial issue — calendar headline

Status: recorded for later review; the existing export and implementation are unchanged.

After `calendar.decline` clears the proposal at **7.99 s**, **PROPOSED** remains visible until **CALENDAR UNCHANGED** starts at **11.13 s**. For approximately **3.14 s**, the headline describes an earlier state while the calendar itself correctly remains unchanged.

Evidence: `videos/productions/planned-calendar-declined/action-trace.json`, `label-timing.json`, `production-plan.json`, `scene-events.json`, and the embedded events in `index.html`.

Origin: the model-generated decline beat has an empty headline. In `scripts/motif_plan_compile.py`, previous headlines are cleared only when a later beat supplies a nonempty headline. Thus the proposed headline persists across the empty-headline beat.

Review limitation: the recorded reviews and `results.json` check that new headlines follow physical evidence; they did not catch a headline that becomes stale after a subsequent state change. Their pass records are preserved as recorded and do not imply that intermediate labels always describe the current state.

Reusable review criterion: when story state changes, inspect accompanying headline and caption state as well as the objects. This is a recorded lesson, not an implemented change.
