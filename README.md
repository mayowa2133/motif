# Motif visual system

Motif's initial style and mascot work lives here. The seven supplied videos define the visual style; the supplied robot defines the mascot identity.

- [Reference analysis](docs/style-reference-analysis.md)
- [Style bible](docs/STYLE_BIBLE.md) and [asset spec](docs/ASSET_SPEC.md)
- [Six mascot concepts](previews/mascot-concepts.png) and [concept review](docs/MASCOT_CONCEPT_REVIEW.md)
- [Selected mascot implementation](docs/MASCOT_IMPLEMENTATION.md)

Direction A is selected. The vector puppet is canonical v1. See its [implementation document](docs/MASCOT_IMPLEMENTATION.md) for component structure, previews, rebuild, composition and validation commands. The wider asset library remains deferred while motion is validated.

[Scene 01](docs/SCENE_01_REVIEW.md) is the approved quiet-workstation benchmark: one night developer desk with 17 independent SVG assets, a locked canonical mascot pose, metadata and mobile previews. Competition and inspection benchmarks are separate scene validations before any larger library build.

[Scene 02](docs/SCENE_02_REVIEW.md) tests an arena competition with 12 new modular SVGs. [Scene 03](docs/SCENE_03_REVIEW.md) tests code inspection with 14 new modular SVGs. Both are approved visual benchmarks. [The three-scene comparison](docs/BENCHMARK_WORLD_REVIEW.md) records the validated shared visual world. [Motion Benchmark 01](docs/MOTION_BENCHMARK_01_REVIEW.md) tests that world as a 6.4-second inspection sequence.

[Motif Demo 01](docs/DEMO_01_BASELINE.md) and [Demo 02](docs/DEMO_02_BASELINE.md) are frozen regression examples. Demo 02's [first cut](docs/DEMO_02_FIRST_CUT_REVIEW.md) remains the approved reuse benchmark; its [accepted story revision](docs/DEMO_02_STORY_REVISION_REVIEW.md) shows matched answer tests and a selected-answer handoff. The [style bible's storyboard gate](docs/STYLE_BIBLE.md#storyboard-gate-before-rendering) carries the directing lessons into future productions.

[Demo 03](docs/DEMO_03_BASELINE.md) is an accepted, audio-finished calendar-approval regression example. It tests whether a message-level brief can produce a clear first cut with a preserved initial storyboard, pre-render self-review, encoded first render, and one bounded visual correction. Its [production review](docs/DEMO_03_REVIEW.md) records the visual story and the audio-only finishing pass.

[The local production workflow](docs/PRODUCTION_WORKFLOW.md) connects a structured brief, storyboard gate, narration alignment, the existing scene-event engine, render, audio finishing, and encoded-file verification. Its [first limited-scope validation](videos/productions/focus-hour-validation/PRODUCTION_REPORT.md) produces an open-hour focus proposal from a new brief while leaving all three demos frozen.
