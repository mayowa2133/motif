# Motif local production workflow

This entry point connects a structured brief to a storyboard record, local narration, structured scene events, an encoded first render, audio finishing, and measured final-file gates. [The pre-change inspection](PRODUCTION_WORKFLOW_INSPECTION.md) records what was already shared. Demo 01–03 remain frozen.

## Run

From the repository root:

```bash
python3 scripts/motif_produce.py run --brief briefs/focus-hour-validation.json
```

The example [JSON brief](../briefs/focus-hour-validation.json) includes the required `message`, `audience`, `intended_duration_seconds`, `aspect_ratio`, `style`, and `voice`, plus a project `slug`, a supported `template`, and two short scene labels. Choose a **new slug** for a new run; the command refuses to overwrite existing output. It writes to `videos/productions/<slug>/`.

The local machine needs Python 3, Node/npm, FFmpeg/FFprobe, and the existing Kokoro ONNX runtime. Set `HYPERFRAMES_PYTHON` to the Python with `kokoro-onnx`; the command also recognizes the existing `~/.cache/motif-kokoro-venv/bin/python`. HyperFrames is pinned at `0.8.96` in the generated project.

## Stages and gates

1. Validate the structured brief and supported template.
2. Save `STORYBOARD_INITIAL.md` and `STORYBOARD_REVIEW.md` **before** narration, animation, or finished rendering. The deterministic review checks all five storyboard fields, evidence before result text, approval before booking, and an ending action. It does not replace creative judgment.
3. Generate local Kokoro `af_nova` narration, transcribe its words, and align caption handoffs to that take. The template's action timing scales with measured narration duration; permission-order, proposal-clearance, and result-headline gates inspect the structured event plan.
4. Assemble the scene from canonical SVGs and the reusable calendar template; run HyperFrames check; preserve `renders/first.mp4`.
5. Measure **encoded** first-render loudness and true peak. Try one gain on the combined mix. If a transient prevents reaching the target safely, apply combined-mix loudness processing with AAC headroom and measured calibration. Voice and SFX are never normalized separately.
6. Copy the video stream into `renders/final.mp4`, then verify approximately **−16 LUFS** (±0.8 LU), **≤−1.5 dBTP**, identical encoded video stream, identical duration, and the 12–18-second range. Failed checks raise an error and remain visible in `verification.json`. Make a 360 × 640 playback copy only after the gates pass.

The encoded audio result is a technical measurement. A person still needs to judge narration delivery, SFX balance, and the visual story. `audio-source-license-manifest.json` records the local voice source and reused cleared SFX; no music is added.

## Supported scope

The current scene template supports one **calendar open-slot proposal**: a fixed 3 PM existing card, a visibly provisional 4 PM FOCUS suggestion, a separate person's approval, then a booked solid card. The existing event label can vary within 2–6 uppercase letters; the proposed label remains `FOCUS` because the script and captions are fixed. The message is checked for an open hour, focus, and approval, then recorded; it is not interpreted by a general story model. The shared template and entry point prevent copying a new generator for each brief within this family. They do not select arbitrary metaphors or support other topics, times, aspect ratios, voices, or a general scene grammar. Such work still needs an authored template or bespoke scene code and review.

No new motion-engine action, mascot redesign, broad asset library, publishing surface, account system, or dashboard was added. The renderer, event engine, captions, Bot, approved environment pieces, calendar props, local Kokoro workflow, and cleared SFX are reused. The one new shared scene module, [`motif_calendar_template.py`](../scripts/motif_calendar_template.py), is a parameterized derivative of the frozen Demo 03 calendar assembly; Demo 03 itself was not changed.

The [first validation report](../videos/productions/focus-hour-validation/PRODUCTION_REPORT.md) describes the fresh brief, generated MP4, intervention history, and remaining limits. One successful run shows this **supported template** can be produced repeatably; it is not evidence of arbitrary-topic autonomy.
