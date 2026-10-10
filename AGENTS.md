# Making a Motif reel (for any AI agent: Codex, Claude, others)

Motif turns a JSON brief into a narrated 2D paper-style short-form reel. A reel is
**data only**: you write a brief, the pipeline draws everything from the approved
library and gates the result. Never write per-film code, never hand-draw a frame,
never copy a reference reel's characters, metaphors or layouts.

## The loop in five commands

```bash
python scripts/motif_reel.py catalog > /tmp/catalog.json     # 1. what a brief may name
# 2. write quality/<dir>/<slug>.json (see "Writing the brief")
python scripts/motif_reel.py check --brief BRIEF --allow-draft # 3. fast: script, plan, sound-off, lessons
python scripts/motif_reel.py run --brief BRIEF --out RUNS \
    --tts-python <python with kokoro-onnx> --allow-draft --render  # 4. voice, compile, gate, render
python scripts/motif_improve.py retro RUNS/<slug> [--feedback "what the reviewer said"]  # 5. learn
```

Repeat 3 until it prints `PASS` before you spend a render (a 45 s reel takes
about 50 minutes on 4 cores). After any reviewer feedback, follow
[docs/IMPROVEMENT_LOOP.md](docs/IMPROVEMENT_LOOP.md) so the next film is better.

The run stops at `REVIEW_REQUIRED`: a human (Mayowa) watches it on a phone. Every
stage result is in `RUNS/<slug>/reel-record.json`; the render is under
`RUNS/<slug>-finished/`.

## Writing the brief

Schema: `schemas/reel-brief.schema.json`. Examples:
`quality/benchmark-briefs/` (short, 20-32 s) and
`quality/adaptation-briefs/adapt-second-brain.json` (long, 43 s, the current
quality bar). Copy the closest one and change it.

1. **Story first.** Pick one object that changes through the film (the
   second-brain reel's vault: a leaky brain, then a RAW crate, then a WIKI board
   that fills, answers and gets checked). Each beat is one change to it.
   Objects and consequences stay connected; a pretty metaphor that does not
   demonstrate the claim is a failure.
2. **Facts.** Every claim beat cites a fact with an http(s) `source_url`.
   Write narration in plain speech, about 3.7 words per second.
3. **Format.** `"format": "short"` (default, 20-32 s, 4-6 beats) or `"long"`
   (30-62 s, 4-10 beats).
4. **Visual hints.** Author them; the fallback planner reads generic. Per beat:
   `visual.rig` + `params` (labels use the claim's own nouns), `room`,
   `palette`, optional `insert`, `costume`, `brand`, `hold`. The hook can have
   its own machine via `hook.visual`.
5. **Relation.** Each claim beat names a `relation` its machine can show
   (`catalog` lists `relations` and which machines show each).
6. **Palettes.** One name, or `"object/room"` (e.g. `"lagoon/berry"`): the
   first colours the machine, the second the walls and floor. A machine that
   appears in several beats keeps its object palette; vary only the room.
7. **Brand.** If the film is about a product, set `brand.slug` (and
   `visual.brand` on beats about a second product). The mark must exist in
   `assets/brands/brands.json`; to add one, vendor the CC0 Simple Icons SVG and
   record it with `scripts/motif_provenance.py`.
8. **Look.** Optionally name a `look` (`paper-craft`, `neon-arcade`,
   `primary-pop`, `candy-pastel`, `great-outdoors`); otherwise the planner picks
   one not used by recent films. Films must not look alike.
9. **Headlines.** Short, uppercase, a new one at least every 3 s; consecutive
   headlines never start with the same word.
10. **CTA.** `cta.keyword` must be said in `cta.narration`.

The full rule list is `brief_rules` in `catalog` (from `quality/lessons.json`).
`check` enforces the measurable ones.

## Mascots

The host is chosen per film with `"mascot"`:

| id | who | suits |
|---|---|---|
| `bot` | Motif Bot, cream paper robot (CANONICAL, default) | anything |
| `kit` | cut-paper fox with a white-tipped tail (DRAFT) | discovery, research, how-to |
| `memo` | sticky note with a spiral-pad body (DRAFT) | notes, productivity, knowledge |
| `lumo` | light bulb in a teal suit (DRAFT) | ideas, tips, inventions |

Every mascot shares Bot's skeleton, so all 16 poses, expressions, costumes,
walk cycles and crowds work for each. Pick the mascot whose character fits the
topic, and vary it across films. DRAFT mascots need `--allow-draft` until
Mayowa approves them. To add a mascot, add a `Mascot` entry to
`scripts/motif_mascots.py` (head, body and hands drawn on the 1024-unit
canvas), run `tests/test_mascots.py`, and leave it DRAFT.

## When the library is missing something

`run` and `check` write `library-requests.json` instead of guessing. Do not
work around a missing machine by misusing another one. Build the piece in the
library (a rig in `scripts/motif_rigs/`, a room or prop, an insert), with a
test that its contact closes and its labels print, and mark it DRAFT. See
`docs/rigs/` for every machine's modes and params
(`python -m motif_rigs docs` regenerates them).

## Rules for agents

- Work on your own branch; never commit renders, reference videos or
  downloaded reels (`videos/`, `review-bundles/` stay untracked).
- References are a style guide only. All assets are Motif's own; every asset
  must trace to `assets/PROVENANCE.json` (the gate checks it).
- Run `python -m pytest -q tests` before you push.
- Run `python scripts/motif_improve.py regress` after changing a rule, the
  planner or the library; every repo brief must still pass.
