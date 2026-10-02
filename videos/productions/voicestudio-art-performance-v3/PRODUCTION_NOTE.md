# VoiceStudio — art and performance v3

**REVIEW_REQUIRED.** Agent-authored art and choreography for the existing attributed reconstruction. This does not demonstrate autonomous original-video planning.

## Material changes

- Replaced the main monitor, vintage computer, microphone, and blue stool with four production-scoped paper illustrations. Original imagegen PNGs are retained. Editable UI, content masks, and foreground bezel geometry remain separate.
- Redrew paper edges, tape/layer treatments, laundry controls/drum, sleeping and startled cat, room details, workbench, book/pages, and keycap depth as vectors. Physical shells, wood, tiles, paper, and precise UI have different surface treatments.
- Enlarged the recording performance and active waveform. Added talking mouths, blink/gaze shifts, head/antenna response, acceptance anticipation, payment contraction, and cancellation relief using the canonical puppet.
- Reworked row and workflow landings, book-to-player page arrivals, and keyboard contact/release. Highlights follow landings; chapter rows follow arrivals; letters follow presses. Retained the pink sample token, prominent offline progress, and larger recognizable app tiles in the final burst.
- Used chosen shot layouts rather than continuous camera drift. The application reveal, menu, book/player, and keyboard have distinct focal arrangements.

## Provenance and editable sources

- `source/components.py` and `source/actions.py` contain the production-local drawings, integration masks, and performance recipes. Shared compile routing selects them only for this version.
- `assets/art-v3/provenance.json` records the actual imagegen sources/prompts and the unused microphone-cleanup attempt. The microphone haze is excluded by an authored SVG silhouette mask. No generated frame is presented as an editable rig.
- `assets/art-v3/metadata.json` describes each master and vector addition. WebP files are lossless presentation copies; original dimensions, alpha, and visible RGBA pixels were checked against the retained PNGs.
- `production-plan.json`, `scene-events.json`, and `speech-timing.json` preserve the editable timeline and semantics. The canonical mascot assets were not replaced.

The four bitmap masters are presented as HTML images inside SVG masks. Their background declarations use the pinned renderer’s existing image-decode preparation before capture. This replaces the intermittently missing SVG-image/instance exports without changing source pixels, timing, or the engine. Failed export attempts are retained.

Two bounded creative correction passes addressed key releases/supports and the speaking-face replacement. Subsequent changes repaired bitmap capture only; they did not reopen art direction.

## Inspection

Automated checks and visual judgment are separate. Both export sizes use the pinned 0.8.99 renderer. Strict runtime/layout/contrast checks do not assess craftsmanship; motion assertions are not enabled. Encoded material crops specifically check the prior missing-bitmap defect across every frame of the affected shot ranges. Nineteen decoded setup frames were inspected at 360 × 640. Browser playback of the actual encoded full film and caption-free native picture ran at 1× to completion, muted, with sampled playback observations. The final native captioned and caption-free pair also completed at 1×; the three matching old/new recording, menu, and keyboard clips completed at 1× without retiming. This is not subjective listening approval.

Final exports: 1080 × 1920 and native 360 × 640, each 986 frames / 32.866667 seconds. Combined encoded audio measures −16.01 LUFS integrated and −3.36 dBTP; both deliverables carry the same adjusted AAC. Full/native strict checks pass with no warnings. The material-presence checks pass in both sizes and the caption-free copy.

## Preservation and review limits

The 19 setups, 986 frames at 30 fps (32.866667 seconds), cut map, script, original narration, and speech anchors are retained. The reviewed v2 file hashes are recorded in `review/preserved-v2.json` and checked unchanged. Earlier productions and attempts remain available. No new TTS, music provider, commit, or push.

Remaining craft limits: the generated hero props have richer tonal modeling than some auxiliary vector interfaces; talking is designed rhythmic acting rather than phoneme synchronization; the original short shot budgets limit anticipation and recovery. Tiny UI text remains secondary to shape and action. Human visual approval and subjective listening are pending. Product, privacy, comparison, and licensing claims remain source-attributed reconstruction content, not verified advice.

The MP4s and comparison images/clips are the review deliverables. Source folders retain runtime dependencies and fonts for local editing; do not distribute those as an embedded-font source package.
