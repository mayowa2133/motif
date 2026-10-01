# Bounded brief variation review

Date: 2026-09-30. The accepted focus-hour export remains unchanged. This test audits the existing calendar entry point and exercises its real supported inputs.

## Finding

The producer changes the existing appointment label throughout the generated scene and storyboard. It packages an authored calendar story: it does not write narration or choose shots from the message. Times remain 3 PM and 4 PM; the proposal remains FOCUS; the outcome remains approval followed by booking. Those limitations are documented in the [field-by-field input contract](BRIEF_INPUT_CONTRACT.md).

Variation A changes CALL to SYNC. Variation B uses REVIEW, the longest permitted label length of six letters. Displayed times and longer narration are not configurable, so this review does not claim those variation capabilities passed.

## Expected versus actual

| Test brief | Expected | Actual |
| --- | --- | --- |
| [A: SYNC](../briefs/validation/variation-a-sync.json) | SYNC at 3 PM; open 4 PM; FOCUS proposed, approved, then booked | Rendered correctly. No visible or storyboard CALL. Fixed script/captions agree with the requested story without naming SYNC. |
| [B: REVIEW](../briefs/validation/variation-b-review.json) | Six-letter label remains readable; same supported outcome | Rendered correctly. REVIEW fits its card at mobile size; no label shortening, text removal, or per-run adjustment. |
| [Declined proposal](../briefs/validation/declined.json) | Refusal is unsupported; reject before production | Exit 2, `unsupported_outcome`; no project created. |
| [Unrelated plant topic](../briefs/validation/unrelated.json) | Reject calendar-only mismatch | Exit 2, `unsupported_topic`; no project created. |
| [9 AM / 10 AM](../briefs/validation/unsupported-times.json) | Explain fixed times | Exit 2, `unsupported_time`; no project created. |
| [PLANNING](../briefs/validation/long-label.json) | Explain label limit | Exit 2, `invalid_brief`: existing label must be 2–6 uppercase letters; no project created. |
| [Custom narration](../briefs/validation/custom-narration.json) | Reject unsupported input, rather than discard it | Exit 2, `unsupported_field`; no project created. This is a deliberately invalid fixture, not an added schema field. |

The negative tests invoked `run`, establishing that rejection happens before output creation, TTS, and rendering. [Recorded responses](../validation/brief-variation/negative-results.json) retain expected codes, actual messages, and output-existence checks.

## Finished outputs

| Measurement | A: SYNC | B: REVIEW |
| --- | ---: | ---: |
| Full export | [final.mp4](../videos/productions/brief-variation-a-sync/renders/final.mp4) | [final.mp4](../videos/productions/brief-variation-b-review/renders/final.mp4) |
| Mobile playback | [360 × 640](../videos/productions/brief-variation-a-sync/renders/mobile.mp4) | [360 × 640](../videos/productions/brief-variation-b-review/renders/mobile.mp4) |
| Duration | 13.366667 s | 13.366667 s |
| Picture | 1080 × 1920, 30 fps, 401 frames | 1080 × 1920, 30 fps, 401 frames |
| Encoded integrated loudness | −16.04 LUFS | −16.04 LUFS |
| Encoded true peak | −1.74 dBTP | −1.74 dBTP |
| First/final encoded video stream | Identical within run | Identical within run |
| HyperFrames check | Passed | Passed |

Both runs preserved their first exports. Combined-mix loudness processing with measured calibration reached the existing −16 LUFS target and −1.5 dBTP ceiling. A separate export inspection reran FFprobe, encoded FFmpeg loudness measurement, and first/final video-stream hashing. [Supported results](../validation/brief-variation/supported-results.json) record visible SVG text, transcript comparisons, caption starts, event timing, probes, audio measurements, and export hashes. The same generated voice hash and script hash in both runs confirm that label variation does not alter narration.

## Meaning, timing, and mobile inspection

The generated brief, scene data, card text, accessibility description, and storyboard agree on SYNC or REVIEW. Neither visible text nor storyboard retains CALL. Internal motion selectors such as `#call-card` retain their shared IDs; they are not displayed copy. FOCUS, 3 PM, and 4 PM remain because both supported briefs explicitly request those fixed template values.

Both runs have the same event timing:

| Visible event or spoken anchor | Seconds |
| --- | ---: |
| Finger press completes | 8.066 |
| Approval check begins | 8.181 |
| Finger withdrawal completes | 8.653 |
| Spoken “Only then” / caption handoff | 8.690 |
| Dashed proposal fade completes | 9.713 |
| Solid FOCUS booking begins | 9.818 |
| Solid booking entrance completes | 10.395 |
| BLOCK BOOKED headline begins | 10.510 |

All eight caption handoffs match the measured word anchors, and the normalized transcript matches the fixed 34-word script. Captions are concise paraphrases, not verbatim subtitles. The final caption remains as an ending hold. The target duration field of 14 seconds is an intention within the supported range; it is not an exact length setting.

Manual visual inspection used decoded frames from each encoded mobile copy: [story samples](../validation/brief-variation/mobile-story-frames.jpg) and [approval samples](../validation/brief-variation/approval-detail.jpg). SYNC and REVIEW remain readable at 360 × 640, fit within the cards, and persist in the original slot. The proposed slip is distinguishable from the later solid card. Sampled approval frames show an unchecked tab before the check and the booked card before the result headline. Headlines and captions fit within the frame. This is sampled-frame inspection, not a subjective review of full playback or audio balance. Subjective listening remains unassessed.

## Shared fixes and reuse evidence

The [before-fix findings](../validation/brief-variation/before-fix-findings.json) recorded three defects during contract inspection:

1. The original keyword validator accepted the declined-proposal fixture and would produce BLOCK BOOKED. Added explicit unsupported-outcome rejection and calendar-topic validation.
2. Two storyboard references retained CALL after the label changed. Both now use `existing_title`.
3. Unknown input fields were ignored. They now receive `unsupported_field`; explicit unsupported clock times receive `unsupported_time`.

A `validate` action now returns a concise supported-template description without producing a project. Invalid `run` and `validate` requests return a JSON rejection with exit code 2. No new configurable fields were introduced.

These shared producer fixes were completed before either supported run. Both commands then used the same producer SHA-256:

```text
8962655b2d07ed654fff7c17845d1389ac8edd09811e65a5680cdc093b200ff7
```

The [source snapshot](../validation/brief-variation/shared-source-hashes.json) covers 16 producer/template/runtime/source-asset files. The [reuse and frozen-file check](../validation/brief-variation/source-reuse-and-frozen-check.json) found no shared-source changes between runs and no changes in 362 frozen files across the canonical mascot, three demos, and accepted focus-hour production.

Commands:

```bash
python3 scripts/motif_produce.py run --brief briefs/validation/variation-a-sync.json
python3 scripts/motif_produce.py run --brief briefs/validation/variation-b-review.json
python3 -m unittest discover -s tests -v
python3 validation/brief-variation/verify_outputs.py
```

Four regression test methods pass, including the five rejected fixtures, unknown scene fields, the fixed proposed-label restriction, and stale-storyboard checks. The [independent saved-output inspector](../validation/brief-variation/verify_outputs.py) passes for both exports. Its initial XML parsing attempt needed normalization of an HTML boolean attribute in the inspector; neither production source nor output was changed for that correction.

Manual interventions: authored the test briefs; audited and fixed the shared producer once; ran both commands; inspected sampled mobile frames; wrote this report and evidence. No per-run source, script, caption, event, audio, or picture edits. Development-attempt folders remain intact. This validation has not been committed or pushed.

## Remaining limits

Message checks are conservative keyword rules. They reject the tested unsupported meanings, but cannot guarantee semantic agreement for arbitrary prose, unusual clock notation, mixed topics, or every refusal paraphrase. The structured fields and authored calendar template remain the real contract. Broader semantic understanding is not established by these tests.

Times, proposal type, outcome, narration, caption wording, headline wording, voice, and layout are fixed. Labels accept letters only and at most six characters. Six-character REVIEW was tested; all possible six-letter strings were not. Exact duration, custom narration, and arbitrary-topic production remain unsupported. Creative review and subjective audio listening remain manual steps.

The bounded validation is complete. No new environment, prop library, dashboard, or additional template was built.
