# Current calendar producer input contract

Audit of the real schema in `scripts/motif_produce.py`. This producer packages a fixed open-hour → proposed FOCUS → human approval → booking story. Its configurable scene content is the existing appointment label. A different message does not author a different script or set of shots.

| Existing field | Actual control |
| --- | --- |
| `slug` | Output directory under `videos/productions/`; existing directories are preserved. |
| `message` | Checked against the supported calendar scenario, then copied into the brief and initial storyboard. Does not generate narration. Decline/cancellation and explicit unsupported times are rejected. These checks are conservative keyword rules, not a general semantic parser. |
| `audience` | Recorded in the storyboard; no change to voice, wording, staging, or shots. |
| `intended_duration_seconds` | Must be 12–18. It does not set an exact export duration: actual voice duration plus 1.45 seconds, with a 12-second floor, controls the timeline. Encoded output must remain within 12–18 seconds. |
| `aspect_ratio` | Only `9:16` is accepted; output is 1080 × 1920. |
| `style` | Only `motif-v1` is accepted; locked assets and paper treatment remain fixed. |
| `voice` | Only `af_nova` is accepted; local Kokoro speed is fixed at 0.85. |
| `template` | Only `calendar-open-slot` is accepted. The renderer's internal conflict branch is not exposed by this entry point. |
| `scene_data.existing_title` | 2–6 uppercase letters. Controls the solid existing card, accessibility description, and storyboard references. The fixed narration and captions do not name this event. |
| `scene_data.proposed_title` | Must be `FOCUS`. It is a required constant, not a configurable appointment type. |

No other fields are supported. Unknown top-level or `scene_data` fields now produce `unsupported_field`; custom narration, times, or outcomes cannot be silently discarded.

The calendar asset fixes TODAY, 3 PM, and 4 PM. The fixed 34-word narration, caption phrases, headlines, approved outcome, prop positions, and five action beats are authored template decisions. Word alignment controls caption handoffs; voice duration scales the action timeline. Event gates enforce press → check → hand withdrawal → spoken “Only then,” followed by the booked card and then the booking headline. Encoded audio retains the −16 LUFS target (±0.8 LU) and −1.5 dBTP ceiling.

Use `python3 scripts/motif_produce.py validate --brief <brief.json>` to inspect acceptance without creating a project. Invalid `run` and `validate` requests return a JSON rejection and exit code 2 before TTS or rendering. Refusal is currently unsupported; the workflow rejects it rather than generating an unchanged-calendar branch.

The bounded [variation review](BRIEF_VARIATION_REVIEW.md) records which fields were exercised and which capabilities remain unavailable. Visual and listening approval remain manual.
