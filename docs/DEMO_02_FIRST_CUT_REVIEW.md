# Motif Demo 02 — arena first-cut review

Status: **approved as a reuse benchmark**. The 10.2-second Reel uses the approved Scene 02 arena to test whether Motif can tell a different story with the same system. It is an illustrative answer-comparison workflow: A looks promising, a check finds a flaw, B passes its check and is selected, and the narration asks the viewer to review the result before using it. No correctness guarantee is implied. A [bounded story revision](DEMO_02_STORY_REVISION_REVIEW.md) adds visible answer tests and a physical review handoff.

## Deliverables

| Item | File |
| --- | --- |
| Complete 1080 × 1920 MP4 | [motif-demo-02-arena-first-cut.mp4](../videos/motif-arena-reel/renders/motif-demo-02-arena-first-cut.mp4) |
| 360 × 640 playback copy | [mobile MP4](../videos/motif-arena-reel/renders/motif-demo-02-arena-first-cut-mobile.mp4) |
| Frames extracted from final encoded MP4 | [mobile contact sheet](../videos/motif-arena-reel/proof/first-cut-contact-sheet.png) |
| Editable timing and source | [scene events](../videos/motif-arena-reel/scene-events.json) · [generator](../scripts/build_motif_arena_reel.py) · [audio plan](../videos/motif-arena-reel/audio-plan.json) |
| Post-render correction record | [manual-corrections.json](../videos/motif-arena-reel/proof/manual-corrections.json) |

## Repeatability accounting

| Category | What this cut used |
| --- | --- |
| Existing assets and components | All **12** approved Scene 02 SVG assets; canonical Bot v1 with four generator poses; Demo 01's paper headline/caption design and exclusive caption replacement; the same GSAP, motion engine and primitive files (byte-identical copies); `af_nova` through the same local Kokoro model; **7** previously cleared SFX files. |
| New assets or reusable capabilities | **No new library asset or engine action.** Five composition-only paper graphics were drawn: A's X, B's check, and PROMISING, FLAW, and PASSES tags. The new narration, event plan and audio plan are specific to this Reel. |
| Bespoke scene code | `scripts/build_motif_arena_reel.py` assembles the manifest, defines four canonical Bot poses, isolates the existing board's baked winner arrow for a delayed reveal, and lays out the five paper graphics. Normal animation remains in structured `scene-events.json`; no scene-specific GSAP calls were added. |
| Manual work after first render | **One correction pass:** the PROMISING card was hidden before FLAW appears, and B's rise was delayed to the podium reveal. The first encoded render was replaced; the changes are recorded in `proof/manual-corrections.json`. Before that render, validation also caught two short audio slots and paper marks covering board letters; those were fixed before export. |

## Timing and readability

- The brief wide arena introduction gives way to an A-focused view at 2.08 s. A's check runs at 3.68 s; the FLAW tag and X arrive around the spoken “flaw” at 4.40–4.84 s.
- The view shifts to B at 4.98 s. Its own check begins at 5.29 s, and the green mark lands as the narrator says “better,” before any ranking appears.
- The podium and delayed board arrow begin at 6.67–6.70 s, matching “selected” (6.67–7.46 s). The winner seal follows at 7.03 s. The final review caption starts at 7.54 s and remains readable through the ending.
- Final encoded frames were inspected at 360 × 640 at the introduction, A focus, both evaluations, the result reveal, and the ending. The board letters remain visible beside the X and check. B remains grounded until the podium rises. The last frame still shows B selected while the caption says “before using it.”

## Technical verification and limits

HyperFrames check passed with **zero lint, runtime, layout, motion, or contrast findings**; all 59 sampled text checks passed. The encoded file is H.264, **1080 × 1920 at 30 fps for 10.20 s**, with AAC 48 kHz stereo audio. Final audio measured **−16.25 LUFS integrated** and **−3.00 dBTP** true peak. The phone-size copy is 360 × 640 and the same duration.

Whisper small.en recovered the sentence from the encoded mix with 26 word tokens. It merged “B performs” into one token and rendered “looks” as “look,” so this is evidence of approximate intelligibility and timing, not an exact transcript or a subjective listening verdict. `af_nova` remains provisional; voice character, effect balance and overall engagement need a person's listening judgment. The [audio manifest](../videos/motif-arena-reel/audio-source-license-manifest.json) records the local model and reused SFX sources and their provenance limit.

This cut required a new scene generator and a small post-render timing correction, so it is evidence of repeatability with controlled assembly and review. It is not evidence that arbitrary prompts can yet be turned into equally good Reels without direction.

**Stop point:** The first cut remains the approved reuse benchmark. Its [single story revision](DEMO_02_STORY_REVISION_REVIEW.md) is delivered separately for review.
