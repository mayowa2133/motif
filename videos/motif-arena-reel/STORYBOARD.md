---
mode: autonomous
message: "A comparison can expose weaknesses and select a stronger candidate, while a person still reviews the result."
aspect: "9:16"
---

# Motif Demo 02 — accepted story revision

Status: **rendered, accepted, frozen**. This storyboard records the completed cut and serves as an example of the [pre-render storyboard gate](../../docs/STYLE_BIBLE.md#storyboard-gate-before-rendering). The first-cut storyboard is archived in `versions/first-cut/STORYBOARD.md`.

| Beat | Subject and action | Visible before/after | Focal detail | Consequence |
| --- | --- | --- | --- | --- |
| 01 · Arena establish, 0–2.08 s | A, B, and C appear as answer tokens in the arena. | Empty stage → three candidates present. | Tokens and A/B/C board, in one brief wide view. | Move to A's answer for comparison. |
| 02 · A appears strong, 2.08–3.68 s | A's paper answer occupies its own close view. | Two tidy checked lines are visible; the link route is still untested. | Answer sheet, then the zone where the stencil will land. | The same connection test begins. |
| 03 · A's test, 3.68–4.98 s | The paper link stencil lands over A's sheet. | Unseen route → route with a center gap; the coral mark arrives after the gap. | The broken connection between the two endpoints. | A is not selected. |
| 04 · B's matched test, 4.98–6.67 s | The same stencil lands over B's sheet in matching framing. | Unseen route → continuous route between the same endpoints; the teal confirmation follows. | The completed connection, not the whole arena. | B proceeds to selection. |
| 05 · Selection and review, 6.67–10.20 s | B's selected sheet moves toward Motif Bot. Bot receives it and an inspection lens travels across it. | Sheet at the side → sheet at Bot's hand, under inspection. | Handoff, Bot's thinking face, and lens on the sheet. | Review before use; no claim of absolute best or rank for A/C. |

## Directing record

The cut presents the condition before its outcome mark, gives A and B comparable shots, and pairs “review” with an inspection action. The connection is illustrative, not a measured technical result. The accepted cut's [remaining limits](../../docs/DEMO_02_STORY_REVISION_REVIEW.md#verification-and-limits) are guidance for future storyboards, not changes to this one.

The approved Scene 02 arena and locked Bot are assembled by `scripts/build_motif_arena_reel_story_revision.py`. Three scene-specific props live in `assets/scenes/scene-02/story/`; timing is declared in `story-revision-events.json` and compiled by the unchanged Demo 01 event engine. The [Demo 02 baseline](../../docs/DEMO_02_BASELINE.md) records the frozen video and source hashes.
