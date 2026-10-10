# Rig: knowledge-vault

A second-brain machine that keeps its identity across beats: a RAW crate, a WIKI pinboard of linked pages, a gantry claw and a paper brain that fills as pages are added. Modes: forget (items fall through a leaky brain and fade), setup (folder labels slap on), collect (items arc into the crate), compile (the claw pins linked wiki pages), ask (cited answer card), save (the answer becomes a page), check (a lens finds an outdated page, the claw swaps it). Notes, wikis, knowledge bases, research, memory, second brains, personal knowledge management.

**Origin:** original Motif design, authored SVG in `scripts/motif_rigs/library6.py`. Style inputs: `docs/STYLE_BIBLE.md` and `docs/style-reference-analysis.md` only; no reference frame traced or copied.

**Tags:** knowledge, notes, wiki, brain, second, memory, research, library, obsidian, vault, folder, sources, organize, answer, question, cite, citations, smarter, remember, forget

**States:** idle → done

## Actions

- `run`: idle → done, 66 frames; contact `vault-contact` closes at frame 46 (distance 0, tested).

## Parameters

```json
{
  "mode": "collect",
  "items": [
    "ARTICLE",
    "BOOK",
    "PODCAST",
    "MEETING"
  ],
  "pages": [
    "IDEA",
    "PEOPLE",
    "PROJECTS",
    "HABITS",
    "TOOLS",
    "READING",
    "GOALS",
    "NOTES"
  ],
  "pages_from": 0,
  "pages_to": 0,
  "count": 10,
  "label": "SAVED",
  "question": "WHAT AM I MISSING?",
  "answer": "ANSWER",
  "cite": [
    0,
    2,
    3
  ],
  "flag": 1,
  "flag_label": "OUTDATED",
  "stamp": "CHECKED",
  "raw_label": "RAW",
  "wiki_label": "WIKI",
  "logo": null
}
```

**Bot slot:** x -330, y 0, scale 0.22: feeds the crate, watches the claw and cheers as the brain fills.

**Palettes:** renders in all 19 Motif palettes (berry, candy, citrus, cobalt, forest, lagoon, lilac, meadow, mint-coral, neon-ember, neon-teal, neon-violet, peach, plum-night, poppy, royal, sky, sunflower, sunrise); films rotate them per scene.

**Status:** draft proof; awaiting Mayowa approval (plan task 2.2).
