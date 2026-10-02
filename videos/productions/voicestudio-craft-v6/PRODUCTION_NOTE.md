# VoiceStudio v6 — final targeted craft pass

**REVIEW_REQUIRED.** v5 is the accepted baseline. v6 awaits visual approval; no further version is planned in this task.

## Seven selected moments

| Shot | Source frames | Change |
| --- | --- | --- |
| 02 Repository | 76–137 | Pressed ledge yields; count ticket reacts; distant tab responds weakly and later. Continuous same-size stars become two timed paper-star bursts with one large accent, two medium pieces and smaller support. |
| 03 Payment | 138–206 | Bot compresses with inward hands, lowered/angled head and independently drooping antennae as receipts arrive. One longer receipt hangs below the board into the foreground; receipt stacks settle locally. |
| 05 Basement | 248–327 | At completion, Bot throws its existing hands outward, the cat stretches and jumps higher, and its laundry basket rocks one frame later. Bot's feet remain on the original stool; washer, monitor and stool masters are unchanged. |
| 09 Menu | 455–506 | ASR landing is heavy, Diarisation landing lighter. Contacted rows yield; the nearest row responds less and later. Asymmetric Bot recovery and antenna lag distinguish the two landings. |
| 12 Transcript | 600–650 | Final speaker strip is longer, overlaps the previous stack unevenly and has a turned paper end. Earlier strips flutter briefly and the output lip yields slightly; speaker assignments and delivery frames are unchanged. |
| 16 Cancellation | 790–838 | Bot opens out of the burdened posture: lifted head, relaxed outward hands and springing antennae. Stopped receipts react and settle. The same longer receipt preserves the pricing callback. |
| 19 Keyboard | 937–985 | Tucked anticipation, compressed contact and open rebound use the existing Bot parts. Five VOICE contacts remain on frames 965/967/969/971/973. The app-tile payoff has one dominant tile, two medium tiles and smaller support; nearby clipboard follows weakly after two frames. |

Reaction envelopes are local, damped and limited to 18 frames, with distance and story relevance reducing their strength. There is no whole-scene shake or added global texture. The two depth cues are the hanging receipt and the extended/folded speaker strip; no new prop masters were generated.

## Review files

- [Complete v6](renders/moving-preview.mp4)
- [Native 360 × 640](renders/mobile.mp4)
- [Seven same-time native before/after pairs](renders/selected-before-after.png) — captions omitted in this sheet; headline preserved. Each individual picture is 360 × 640.
- [Billing and relief](renders/comparisons/billing-and-relief.mp4) — two matched source excerpts, separated by a cut.
- [Basement completion](renders/comparisons/basement-completion.mp4)
- [Keyboard contact/rebound](renders/comparisons/keyboard-contact-rebound.mp4)

Comparison clips are muted and play at the original 30 fps / 1× speed. Full and native films retain the original finished audio.

## Preservation and limits

All 19 shots, boundaries, 986 frames, script, narration, captions, UI state transitions and engine remain fixed. Twelve unselected shot compositions are copied byte for byte from v5. Existing raster masters and canonical Bot paths are reused. v5 and earlier productions remain intact. No dependency upgrade, new music, commit or push.

Full-size strict checks passed. Selected native checks found no runtime or layout errors; they retain ten existing contrast warnings on small `Paid` and `Speaker` labels. A matched v5 check produced the same ten warnings and ratios. These secondary labels were kept with the accepted baseline; icons, large copy and captions carry the main story.

One bounded correction pass addressed receipt pivoting, bilateral antenna movement and the visibility of startle/rebound hands outside the head silhouette. The selected native frames were reviewed before the full render; final playback and encoded-media results are recorded in `review/encoded-final.json` and `review/playback.json`.

The film still uses cleaner lettering, more regular UI rows and a narrower range of expressive deformation than the references. Rapid menu and keyboard beats remain brief at the locked cut timing. Small labels remain secondary to shape, pose and action. This is an incremental craft pass, not a claim of reference-level parity or automatic original-film direction. Narration claims and subjective listening approval were not reassessed.
