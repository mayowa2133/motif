# Motif Demo 02 — arena Reel

The accepted, frozen 10.2-second story revision shows the same physical connection test applied to A and B, then Motif Bot receiving the selected B sheet for review. The [first cut](../../docs/DEMO_02_FIRST_CUT_REVIEW.md) remains an approved reuse benchmark; its source files are preserved in `versions/first-cut/`. The [Demo 02 baseline](../../docs/DEMO_02_BASELINE.md) records the accepted media and event hashes for future regression checks.

## Build the story revision

From the repository root:

```bash
python3 scripts/build_motif_arena_reel_story_revision.py
cd videos/motif-arena-reel
npm run check
npm run render -- -o renders/motif-demo-02-arena-story-revision.mp4 --skill=general-video -q delivery
```

`story-revision-events.json` is the editable shot and motion plan. `audio-plan.json` places the existing local Kokoro `af_nova` narration and reused SFX. The generator assembles approved arena SVGs, the locked Motif Bot generator, and three new modular story props with metadata under `assets/scenes/scene-02/story/`. The shared GSAP motion engine and caption component are unchanged.

See the [story revision review](../../docs/DEMO_02_STORY_REVISION_REVIEW.md) for the final MP4, mobile proof, visible test, and review action.
