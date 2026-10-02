# VoiceStudio — fidelity refinement v2

Status: **REVIEW_REQUIRED**. The prior film remains preserved in `../voicestudio-text-directed-film/`.

## Delivered

- `renders/moving-preview.mp4`: 1080 × 1920, **986 frames / 30 fps / 32.866667 seconds**.
- `renders/mobile.mp4`: independently rendered 360 × 640, same frames and adjusted AAC soundtrack.
- `renders/19-shot-contact-sheet.jpg`: nineteen setups decoded from the delivered full-size MP4.

## Changes

The same nineteen setups, cut boundaries, headlines, script and recurring objects remain. This pass strengthens their correspondence and presentation through the existing Motif director, finite UI bindings, event engine and pinned HyperFrames 0.8.99. The locked canonical Bot geometry, default bible and accepted films were preserved.

**Semantic timing:** ten natural narration clauses were regenerated locally with Kokoro af_nova at closely related cadences (1.328–1.357). Saved takes, quiet edge trims, placement and per-clause DTW measurements are retained. Speech was neither stretched nor truncated; captions follow these new measured words.

| Spoken/caption anchor | Onset | Relevant picture |
| --- | ---: | --- |
| VoiceStudio | 11.27s | Name reveal |
| short clip | 12.40s | Recording |
| audiobook | 18.07s | Chapter players |
| types out | 18.70s | Dictation |
| paying | 27.07s | Cancellation |
| runs | 28.30s | Offline processing |

**Prominence:** the opening's largest pink bar at 1.5s measures **75px** in the actual native export, compared with 37px in the previous film. FREE, pricing checks/rejection and the central offline fill are stronger. The ending retains three larger recognizable waveform tiles plus supporting satellites with different paths and lifetimes; VOICE stays clear.

**Finish and acting:** shared paper cuts have stable variation and shallow undersides; locations use different quiet wall/wood treatments. The basement has a worn thick-rim computer, vents and plain base. Existing mascot expressions/poses supply talking, strain, relief, hop compression and follow-through. Cat startle, sample collapse/transfer and three causal page-to-chapter arrivals are clearer. Larger coral serif letterforms remain stable on independently angled cards.

## Verification and limits

Full and native runtime/layout/contrast checks pass with zero findings. Motion assertions were **disabled**. Ten existing Python regression tests and the frame-sequence seek tests passed. Encoded setup frames and denser interaction sequences were inspected at phone scale; the native movie reached its end at normal speed with no media error. Playback inspection was muted: **subjective listening remains pending**.

The full supplied script is preserved in narration input and captions. DTW is approximate: 98% lexical coverage, three estimated filler-word entrances, and documented compound/numeral spelling normalization. The finished mix measures **−16.01 LUFS / −3.36 dBTP**. Product and numerical claims remain unverified reconstruction content. This is a directed finite study, not evidence of arbitrary-topic autonomous production. No commit, push or publication.

## Reproduce

From the repository, render the saved project without replanning or revoicing:

```sh
python3 scripts/motif_direct.py script-preview --project videos/productions/voicestudio-text-directed-film-fidelity-v2 --render
```

Stop here for review.
