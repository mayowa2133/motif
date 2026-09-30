# Mini Reel 01 — editorial cleanup review

Status: **approved as Motif Demo 01's visual and story baseline**. This is one bounded pass on the approved end-to-end Reel. The mascot, benchmark scenes, narration provider, event-driven motion system, and 9.55-second composition length remain in place. The approved export is frozen in [the baseline record](DEMO_01_BASELINE.md); the DONE-ticket contrast warnings are a separate [component issue](ISSUE_DONE_TICKET_CONTRAST.md).

## Deliverables

| Item | File |
| --- | --- |
| Revised 1080 × 1920 MP4 | [motif-mini-reel-01-editorial.mp4](../videos/motif-mini-reel/renders/motif-mini-reel-01-editorial.mp4) |
| 360 × 640 playback copy | [motif-mini-reel-01-editorial-mobile.mp4](../videos/motif-mini-reel/renders/motif-mini-reel-01-editorial-mobile.mp4) |
| Encoded frame contact sheet | [editorial-contact-sheet.png](../videos/motif-mini-reel/proof/editorial-contact-sheet.png) |
| Level-matched auditions | [af_nova](../videos/motif-mini-reel/assets/voice/audition-af-nova-matched.wav) · [bf_emma](../videos/motif-mini-reel/assets/voice/audition-bf-emma-matched.wav) |
| Audition measurements | [audition-level-match.json](../videos/motif-mini-reel/assets/voice/audition-level-match.json) |

## What changed

- The night desk establishes the hour, then the camera pushes at 0.90–1.30 s to make Bot and the active screens the focal objects during “an AI agent reviews your code.” It holds that framing until the paper transition. The bug close-up and visible rejection bin remain.
- Captions now use one reusable `CAPTION_REPLACE` action. Every incoming phrase clears the previous card at the same instant; the cards retain the same center and baseline. Longer phrase gaps clear the card at its end.
- At 7.72 s, within the spoken “in the morning” phrase (7.63–8.52 s), the factory cuts to the existing desk assembly. A composition-only daylight window insert, the approved checked-paper geometry labeled RESULTS, the existing DONE ticket, and canonical Bot create the payoff. The approved Scene 01 night artwork is unchanged. The former factory hold is replaced without extending the Reel.
- The original `af_nova` and `bf_emma` audition sources are preserved. Endpoint silence was trimmed and both listening copies were normalized to approximately −21 LUFS. `af_nova` remains the provisional narrator; the final Reel narration was not replaced.

## Encoded-result checks

- HyperFrames check passed with **zero lint, runtime, layout, or motion errors**. It reported two contrast warnings for the coral DONE-stamp text in the approved ticket, which appears in the night and morning shots.
- The encoded MP4 is H.264 at **1080 × 1920, 30 fps, 9.5667 s**, with AAC 48 kHz stereo audio. Measured final loudness is **−15.36 LUFS integrated**, with **−1.94 dBTP** true peak.
- Frames extracted from the encoded MP4 were inspected at **360 × 640**. The 1.05 s frame has “While you sleep”; the 1.17 s frame has only “an AI agent” on the same reading line. The bug close-up at 4.60 s, rejection at 5.40 s, approval at 7.30 s, and morning desk at 8.30 and 9.20 s are visible in the contact sheet. The morning report rests on the desk, with its title and checks readable at that size.
- The level-matched auditions measure **−21.00 LUFS** (`af_nova`, 2.99 s) and **−21.02 LUFS** (`bf_emma`, 2.75 s). Their true peaks are −4.77 and −3.66 dBTP respectively. These measurements support a fairer listening comparison; they do not establish which performance sounds better.

## Review limit

The exported video and waveform were checked technically and visually. Voice naturalness, effect balance, and overall engagement remain subjective listening judgments for a person. The clean caption handoff was checked on sampled encoded frames and is also enforced by the shared event action; this is not a claim that every viewer will prefer the editorial timing.

**Stop point:** No further scene, prop-library, mascot, provider, or music work is included in this pass.
