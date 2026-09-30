---
mode: autonomous
message: "A comparison can expose weaknesses and select a stronger candidate, while a person still reviews the result."
aspect: "9:16"
---

# Motif Demo 02 — arena first cut

## Frame 01 — candidates enter
status: rendered
src: `index.html#arena-scene`
rules: spring-pop-entrance, nudge-curve

Brief arena establishing shot. The three existing answer tokens become visible before any ranking. The board introduces A, B, and C. Narration: “Three agents propose answers.”

## Frame 02 — A looks promising
status: rendered
src: `index.html#arena-scene`
rules: spring-pop-entrance, press-release-spring

A becomes the large focal subject. A provisional paper prompt highlights it, with no winner seal or podium yet. Narration: “Answer A looks strong.”

## Frame 03 — evaluation finds a flaw
status: rendered
src: `index.html#arena-scene`
rules: svg-path-draw, press-release-spring

The board and A occupy the frame. A scanning line runs first; only then does a large coral X appear and A droops. Narration: “Then a check finds a flaw.”

## Frame 04 — B passes
status: rendered
src: `index.html#arena-scene`
rules: svg-path-draw, spring-pop-entrance

The evaluation shifts to B. A green check appears before any ranking. B rises into focus while the narrator says it performs better.

## Frame 05 — selected, then review
status: rendered
src: `index.html#arena-scene`
rules: spring-pop-entrance

The existing podium, winner seal, and sparse static paper-confetti asset reveal B as the selected candidate. Canonical Bot presents the result. A final caption asks the viewer to review it, qualifying the illustrative workflow. Hold just long enough for the choice to read.

## Implementation note

The approved Scene 02 assets and locked Bot are assembled by `scripts/build_motif_arena_reel.py`. Normal animation is declared in `scene-events.json` and compiled by the unchanged Demo 01 event engine. The board's baked winner arrow is treated as an internal reveal layer; A/B marks and three short paper tags are composition-only overlays. No new library asset or engine action was added.
