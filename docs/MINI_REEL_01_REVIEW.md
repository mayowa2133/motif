# Mini Reel 01 — narration-led review

The approved prototype has a later bounded editorial revision. See [Mini Reel 01 editorial cleanup review](MINI_REEL_01_EDITORIAL_REVIEW.md) for the current MP4, mobile preview, and matched voice auditions. This page records the first complete render.

Status: **finished for review**. This 9.57-second 9:16 Reel uses the approved Scene 01 desk, approved Scene 03 factory, and locked Motif Bot v1. It adds no environment or prop library. The final is narration plus SFX; no music was included because the repository contained no existing track with verified rights for the intended use.

## Deliverables

| Item | File |
| --- | --- |
| Final 1080 × 1920 MP4 | [motif-mini-reel-01.mp4](../videos/motif-mini-reel/renders/motif-mini-reel-01.mp4) |
| 360 × 640 MP4 with the same sound | [mobile preview](../videos/motif-mini-reel/renders/motif-mini-reel-01-mobile.mp4) |
| Mobile bug and approval frames | [bug](../videos/motif-mini-reel/proof/mobile-bug.png) · [approval](../videos/motif-mini-reel/proof/mobile-approval.png) |
| Encoded MP4 contact sheet | [encoded-contact-sheet.png](../videos/motif-mini-reel/proof/encoded-contact-sheet.png) |
| Narration master and auditions | [master WAV](../videos/motif-mini-reel/assets/voice/narration-master.wav) · [af_nova](../videos/motif-mini-reel/assets/voice/audition-af-nova.wav) · [bf_emma](../videos/motif-mini-reel/assets/voice/audition-bf-emma.wav) |
| Script and word data | [script](../videos/motif-mini-reel/assets/voice/narration.txt) · [word timings](../videos/motif-mini-reel/assets/voice/transcript.json) · [alignment review](../videos/motif-mini-reel/assets/voice/word-timing-review.json) |
| System sources | [scene events](../videos/motif-mini-reel/scene-events.json) · [engine](../videos/motif-mini-reel/assets/motion-engine.js) · [audio plan](../videos/motif-mini-reel/audio-plan.json) · [source/license manifest](../videos/motif-mini-reel/audio-source-license-manifest.json) |

## Direction and story

The night desk hands off via an enlarging paper note at 3.04 s. The code sheet enters while the narration says “reviews your code.” A camera push makes the coral bug the largest idea at “potential bugs,” then the view widens for the rejection bin. The second sheet enters during “runs tests.” Its green check is hidden in the incoming asset layer and appears only after the PASS ticket lands. The headline then changes to **CHECKS PASSED**; the approved sheet exits and Bot celebrates while the results remain visible. Tiny code text stays decorative. The narration is illustrative of an AI-agent workflow and does not claim that Motif itself performs code review or guarantees bug-free output.

The bottom captions are individual paper cutouts sized to their 1–3 word content. One meaningful word per chunk takes a restrained teal or coral accent. The headline names the beat rather than repeating each caption. The transition, bug close-up, and factory return preserve the successful parts of the visual proof without redrawing approved art.

## What was verified

- HyperFrames check passed: no lint, runtime, or motion errors. One contrast warning remains in the approved Scene 01 DONE-ticket art, and one informational text overlap occurs during the intentional enlarging-note transition.
- The final encoded file was probed as H.264, 1080 × 1920, 30 fps, 9.5667 s, with AAC 48 kHz stereo audio. Frames extracted from that MP4 were inspected at 360 × 640, both for the bug and the approval result.
- The final audio measured **−15.36 LUFS integrated** and **−1.94 dB true peak**, with no measured clipping. HyperFrames transcribed the encoded MP4 with Whisper small.en and recovered the exact 25 spoken words in order. This is an objective intelligibility check, not a substitute for a human listening review.
- The raw final narration was aligned with Whisper small.en DTW. The transcription text matches the script exactly. The alignment is estimated; short boundaries for “AI,” “It,” “and,” and “in” are flagged in `word-timing-review.json`. The caption cards use phrase boundaries, so they do not depend on those individual word boundaries being exact.
- The engine compiles `scene-events.json` into one seekable timeline. The [timing-edit record](../videos/motif-mini-reel/proof/json-timing-edit.json) and [before/after at 6.0 s](../videos/motif-mini-reel/proof/json-timing-before-after.png) show the second scanner moving into the spoken “runs tests” beat after JSON-only timing edits. No matching hardcoded GSAP calls were added to the composition.

## Audio provenance and limits

The provisional narrator is Kokoro-82M v1.0, `af_nova` at 0.85 speed, through `kokoro-onnx` 0.6.1. The model card identifies its weights as Apache-2.0 licensed: [Kokoro model card](https://huggingface.co/hexgrad/Kokoro-82M). The two audition WAVs use the same passage. Whisper recovered all nine words from both; `af_nova` was selected provisionally because its 3.1-second sample gave the sentence more room than `bf_emma` at 2.67 seconds. This is a pacing choice, not a subjective claim that one voice sounds better. The files let a person compare the voices before locking a brand narrator. The narration remains a replaceable media file in `audio-plan.json`.

The SFX come from the bundled local set, whose [credits](../videos/motif-mini-reel/assets/sfx/CREDITS.md) attribute it to Pixabay. [Pixabay's licence summary](https://pixabay.com/service/license-summary/) allows adapted use, subject to its restrictions. The bundle does not retain original item URLs; that provenance limit is recorded in the manifest. Standard MusicGen weights were not used; the [released model card](https://huggingface.co/facebook/musicgen-small) lists CC-BY-NC 4.0 for its weights. No music-inclusive version was made.

## Remaining human review

Listen to the final encoded MP4 on a phone or speakers, then compare the two audition samples. The agent environment could inspect waveform levels and transcription, but could not perform a subjective listening pass. Check whether the scanner SFX feels too electronic, whether the selected voice suits Motif, and whether the short final hold gives enough reading time. These are creative judgments rather than automated pass/fail findings.

**Stop point:** This completed Reel is ready for approval. No further scene, mascot, prop-library, or product work follows from this delivery.
