# Full-film reference reconstruction — accepted baseline

Status: **accepted and frozen on 2026-10-01** as Motif’s first completed full-length reference-reconstruction study. The accepted cut has 20 shots, 1,262 frames at 30 fps, and a duration of 42.066667 seconds. This is reference-led, agent-assisted production.

## Frozen delivery

- [Full film, 1080 × 1920](../videos/productions/reference-reconstruction-full-fine-cut/renders/full-film-fine-cut.mp4)
- [Native mobile, 360 × 640](../videos/productions/reference-reconstruction-full-fine-cut/renders/mobile.mp4)
- [Labeled reference comparison](../videos/productions/reference-reconstruction-full-fine-cut/renders/comparison.mp4)
- [Production change note and prior verification](../videos/productions/reference-reconstruction-full-fine-cut/CHANGE_NOTE.md)
- [Source attribution and unavailable originals](../videos/productions/reference-reconstruction-full-fine-cut/SOURCE_CONTENT.md)

SHA-256 identifiers for the accepted files:

| File | SHA-256 |
| --- | --- |
| Full film | `9a2173ec722600c9defab34a0d6863a7ef4555da6e2339ee8e7e42b37cddd43c` |
| Native mobile | `053797b16e3c3bb9c323505955123f6eafb4bd6fb46dcf41e4e4c90597afd1dd` |
| Comparison | `b0fc98eb4d4d4c9fbfeeba722e104deb783f175e97030429c57c6b12464161cc` |

## Resolved issues

The accepted review finds the following repairs present in the inspected output:

- The gym pointer remains visible and moves as the instruction burden increases.
- A platform supports the lifting Bot while its hands follow the bar.
- Cost bars share a baseline and show the internally consistent 100 → 91 relationship; the bracket emphasizes the nine-percent difference.
- Archive notes overlap and accumulate instead of forming a tidy grid.
- Megaphone activity precedes progressive “YOU MUST,” “ALWAYS RUN,” and “THE TESTS!!” reveals.
- Portrait placeholders are replaced by finished, portrait-free credits and explicitly retyped, attributed excerpts.

Successful interactions also remain intact: the burdened race, the Bot reaching an independent platform before the stairs clear, the unanswered apply-permission decision, findings attaching to files before the counter, and arrows embedding in the target.

## Retained limitations

- Artwork remains cleaner and simpler than the reference, with less distinctive object detail and less varied staging in several shots.
- Physical expression is more restrained, including the opening weight struggle.
- Original source media remain unavailable and depicted product claims are unverified. Internally correct chart proportions do not establish the source claim.
- Subjective narration and SFX listening quality is not established by loudness, timing, or peak measurements.
- This study does not establish arbitrary-topic autonomous production, visual equivalence to the reference, or a fact-checked product explainer ready to publish as news.

Future art direction may improve individual objects, physical reactions, and composition. More global grain or random motion is not the remedy, and these observations do not reopen this accepted cut.

## Evidence boundaries

The supplied independent acceptance review inspected decoded samples covering all 20 shots, examined repairs, and compared all 164 pictures in `[436,600)` with the earlier uploaded rough. It found very close visual continuity and acceptable joins. It independently measured the full MP4 at 1080 × 1920, 30 fps, 1,262 frames, 42.066667 seconds, **−16.53 LUFS / −1.75 dBTP**.

That review did not rerun repository tests, make subjective listening judgments, inspect the separately linked native-mobile export, or independently verify original asset hashes, the standalone approved master, or unity-gain audio insertion. The production note records the earlier agent checks separately; its findings are not attributed to the independent reviewer.

This documentation closeout checked existing delivery and preservation hashes. It did not rerender, rerun runtime tests, or perform new playback or listening review.

## Preservation and reuse

Preserve these existing production directories, including their source, renders, inputs, and earlier attempts:

- `videos/productions/reference-reconstruction-full-fine-cut/` — accepted delivery and retained finishing candidates.
- `videos/productions/reference-reconstruction-full-rough/` — original 20-shot rough and its build/audio evidence.
- `videos/productions/reference-reconstruction-01-finishing/` — approved standalone middle passage and finishing attempts.
- `videos/productions/reference-reconstruction-01/` — earlier reconstruction work.
- `references/` — existing source-study material; retain the original reference MP4 at `/Users/mayowaadesanya/Downloads/igexport-Dd15NcHvlNl.mp4`.

The approved middle passage `[436,600)` is closed to further editing. Its standalone full MP4 SHA-256 is `6b80a5d2a4efae9a5db40dc5efe66a0cf3924a0408502656e82fb5b445fb0c96`; its native-mobile SHA-256 is `c24268a97f4077fb0f61a7a2a6357070478c0ca3f58a6a682b33280c0f5103f5`.

Keep the existing `reference-expressive-v1` preset, editable SVG assets, repaired fixed-pivot components, and authored interactions available in the fine-cut production’s `style-preset.json`, `assets/`, `build.py`, and `scene-events.json`. They use the existing renderer and event system. Their availability does not make every shot a mandatory template or add arbitrary-topic planning support.

No broad polish pass, framework, speculative library, new audit bundle, commit, push, or further production is part of this closeout. Stop at this accepted baseline.
