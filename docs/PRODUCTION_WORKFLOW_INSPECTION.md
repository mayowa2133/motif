# Motif production workflow inspection

Inspected before implementing the local entry point on 2026-09-30. Demo 01, Demo 02, and Demo 03 are accepted and frozen; this work does not edit their source or output.

| Stage | Already shared | Still per-demo or manual |
| --- | --- | --- |
| Story | `docs/STYLE_BIBLE.md` storyboard gate defines subject, action, visible before/after, focal detail, consequence, evidence before labels, and ending action. | Initial storyboard and review are written separately for each demo. |
| Art | Locked canonical Motif Bot generator, reusable SVGs and metadata, paper palette, approved environments. | Each demo generator places and labels the parts for its own story. |
| Motion | `motion-engine.js` and `motion-primitives.js` accept structured event JSON; GSAP and caption components are reused. | Event plans, camera timing, and specific actor actions are demo data. |
| Voice and audio | Local Kokoro `af_nova`, a cleared SFX set, HyperFrames audio tracks, FFmpeg. | TTS, placement, and source/master choice were manual. Demo 03's raw voice left its first encoded mix at −24.43 LUFS. |
| Render and proof | Pinned HyperFrames CLI, check, render, mobile frame inspection. | The project directory, export command, encoded loudness/peak measurement, and video-integrity check were run by hand. |

The local workflow will first support one **calendar proposal** family using the existing calendar scene grammar: an existing event, a visibly distinct proposed slot, human approval, then a booked or moved solid card. The first validation uses the **open-slot booking** variant. This is a deliberately limited template, not an arbitrary-topic director. A new brief changes project data and copy; it does not get a copied scene generator. Other motifs still require authored staging and may need bespoke scene code, which must be recorded rather than described as shared capability.
