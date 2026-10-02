# Reference reconstruction 01 — review delivery

**Codex-assisted, reference-led production using Motif.** This is a reconstruction study of supplied footage; its depicted product claims have not been verified. This delivery covers only document wash → terminal → scanner.

## Deliverables

- [Normal-speed synchronized comparison](renders/comparison.mp4): reference left, Motif right, each 360 × 640; labeled 720 × 680 output. Reconstruction soundtrack only.
- [Reconstruction](renders/final.mp4): 1080 × 1920, 30 fps.
- [Native mobile reconstruction](renders/mobile.mp4): independently captured at 360 × 640, 30 fps; no downscaled full-size picture.
- [Matching keyframes](review/keyframe-comparison.jpg): six aligned pairs sampled from the actual encoded videos.
- [Full-reference shot map](../../../references/reconstruction/SHOT_MAP.md).
- [Source intervals and reconstruction timeline](reconstruction-timeline.json), [storyboard](STORYBOARD.md), [editable scene events](scene-events.json), and [caption events](caption-events.json).
- [Technical check](check-final.json), [encoded media/audio verification](verification.json), [comparison verification](comparison-verification.json), and [audio provenance](audio-source-license-manifest.json).

Source: `/Users/mayowaadesanya/Downloads/igexport-Dd15NcHvlNl.mp4`. Selected interval **[436,600)** at 30 fps: **14.533333–20.000000 seconds**, 164 frames / 5.466667 seconds. Wash uses 50 frames; terminal 38; scanner 76. Both comparison sides use these exact cuts without retiming. Source picture is 42.066667 seconds; its audio container extends slightly longer.

## Reuse and new work

The unchanged Motif event engine, motion primitives and GSAP files come from the approved workshop production. The existing finite event schema controls the picture and separate caption track. Canonical Bot geometry is imported from the existing Bot builder, with pose assembly and precomputed hand-following placement for this film. Canonical source assets, default style bible and frozen films were not rewritten.

The `reference-expressive-v1` preset is scoped to this project. It permits source-led framing, quicker physical actions, taped headline strips, coral serif caption chunks and sea-green / charcoal / tan scenes. It preserves editable content and the cream/teal Bot identity.

Necessary new original SVG masters with JSON metadata: wash portal, roller, document, removable instruction slip, Enter key, scanner gate, inspection lens and scanner page. Terminal content, foam, spray, scan band, highlights, alert lights and result counter remain separately controlled scene elements. Four seeded procedural surface tiles differentiate paper, wall, dark card and wood; no image generation was used and no extracted reference prop or character pixels enter the authored production assets.

This bounded compiler and choreography were authored by the agent. They are not output from a new autonomous planner run. Registry `code-terminal-run` supplied an inspected deterministic typing pattern; its layout is not mounted wholesale. Existing plant reuse was attempted, but the finished terminal lacks the source's readable plant/mug dressing, so that is not counted as successful visual reuse.

Fonts are bundled Inter 700, EB Garamond 700 and JetBrains Mono 400, embedded in editable HTML as font data. Inter is mapped to CSS weight 900; the mono face uses the authored IBM Plex Mono alias. The installed preset includes SIL Open Font License records. There are no loose font binary files or packaged dependency/authentication folders.

## Physical actions and review

| Question | Result and practical limit |
|---|---|
| Same idea understandable? | Attached instructions are scrubbed from a labeled document, a command is entered, and inspection produces three highlighted findings. |
| Contact and consequence? | Rollers overlap the entering document; slips peel from it. Bot lands on Enter, which depresses and releases. Page moves through a masked gate; the held lens searches and counter increments follow findings. The folder and open page are two editable representations of one logical document across a cut. |
| Focal scale? | Wash equipment, terminal and scanner occupy comparable middle-frame areas. The canonical Bot is secondary to the action. Terminal key and scan region remain readable at native mobile size. |
| Material family? | Muted scene colors, paper headlines, layered parts and serif caption tiles move toward the reference. Authored edges and surfaces remain cleaner and more geometric. Repeated texture tiles are visible, especially terminal and desk; source surfaces have more organic variation and localized wear. |
| Rhythm? | Exact source cut boundaries and overall duration. Individual entrances, scrub/debris paths and lens movement are approximations. Matching cuts does not establish identical internal choreography. |
| Captions? | Twelve content-sized phrase stages use local narration word timings; same predictable lower reading position. Wording and delivery differ from the source. The fast terminal voice segment especially warrants listening review. |
| Calmer or emptier? | Physical motion is present throughout each causal beat. Source debris is more varied, its terminal has more secondary dressing, and scanner alarm/detail animation is richer. These remain visible differences. |

Initial rough native video and synchronized rough comparison were preserved before polish. Two bounded visual repair passes corrected jump contact/scanner masking, then reduced excessive texture and added word-aligned captions. Prior event/source snapshots and preview sheets remain under `review/`; no third visual polish pass was undertaken. The final encoded comparison was opened in the browser and observed playing at rate 1, with both panels visible. Matching encoded keyframes support the contact and result review. This does not establish subjective audio quality or a perfect visual match.

## Audio and technical evidence

New local Kokoro `af_nova` narration uses segment speeds 1.25 / 1.5 / 1.15. Pop, soft click and short whoosh reuse the existing bundled SFX collection with its recorded Pixabay Content License attribution. The bundle lacks original item URLs; that provenance limitation is retained. No music is included because a suitable cleared matching bed was unavailable. No source voice, music or SFX is included in the reconstruction or comparison soundtrack.

Combined encoded mix finishing used the existing Motif preset: **−16.01 LUFS, −1.65 dBTP**, measured after AAC encoding. Full and mobile exports are each exactly 164 picture frames and 5.466667 seconds; picture stream hashes were preserved during audio finishing. Loudness is a technical gate; **subjective narration/SFX balance and listening quality remain unassessed**.

HyperFrames 0.8.99 strict check passes with zero lint/runtime/layout/contrast errors or warnings. Motion assertions were disabled, so no automated contact proof is claimed. The optional animation-map helper could not run because its optional producer/core packages were unavailable; no dependency bootstrap or upgrade was performed to obtain it.

Only the prior approval-record wording correction in `docs/CREATIVE_BENCHMARK_REUSE.md` changed an existing tracked file. The frozen workshop final retains SHA-256 `836db38ea0dcfbddfd5fb76b5489ff9f32de4def6bdcd6b3b14bb392c504b09d`. No commit or push was made for this production.

**Stop point reached: first section and comparison ready for review. The remainder of the reference is not produced.**
