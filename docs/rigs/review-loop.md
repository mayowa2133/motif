# Rig: review-loop

Two workstations, each under its maker's badge, that check each other's work: one PLAN sheet and one block-tower build carried across beats. Modes: solo (one desk plans, builds and gives itself a gold A+ while bugs crawl out), plan (the left desk writes the steps and throws the sheet across), audit (a red pen strikes rows and objection tabs slap on), loop (the sheet goes back and forth, objections peel off as the ROUND counter rises, a HOLDS UP stamp lands), swap (the role tags drop off and new ones slap on), build (blocks named after the steps stack into a tower; the other desk's magnifier finds a bug and a fixed block drops in), ship (both badges fire a seal onto the tower). Code review, second opinions, audits, pair work, two AI models, checks and balances.

**Origin:** original Motif design, authored SVG in `scripts/motif_rigs/library7.py`. Style inputs: `docs/STYLE_BIBLE.md` and `docs/style-reference-analysis.md` only; no reference frame traced or copied.

**Tags:** review, audit, plan, check, checks, second, opinion, pair, two, models, feedback, homework, grade, judge, critic, swap, roles, build, bug, bugs, loop, rounds

**States:** idle → done

## Actions

- `run`: idle → done, 66 frames; contact `loop-contact` closes at frame 46 (distance 0, tested).

## Parameters

```json
{
  "mode": "plan",
  "steps": [
    "SCHEMA",
    "LOGIN",
    "API",
    "TESTS"
  ],
  "left": "WRITER",
  "right": "CHECKER",
  "left_logo": null,
  "right_logo": null,
  "roles": [
    "PLANS",
    "AUDITS"
  ],
  "new_roles": [
    "AUDITS",
    "BUILDS"
  ],
  "gaps": [
    "NO TESTS",
    "AUTH?"
  ],
  "rounds": 3,
  "stamp": "HOLDS UP",
  "bug": 2,
  "bug_label": "BUG",
  "banner": null,
  "solo": "1 MODEL",
  "solo_logo": null,
  "solo_roles": [
    "PLANS",
    "BUILDS",
    "GRADES"
  ],
  "grade": "A+",
  "bugs": 3
}
```

**Bot slot:** x -340, y 0, scale 0.22: carries the sheet between desks, points at objections and cheers the stamp.

**Palettes:** renders in all 24 Motif palettes (berry, candy, citrus, cobalt, dusk-teal, forest, ink-navy, lagoon, lilac, mauve, meadow, mint-coral, mustard, neon-ember, neon-teal, neon-violet, peach, plum-night, poppy, royal, sky, slate, sunflower, sunrise); films rotate them per scene.

**Status:** draft proof; awaiting Mayowa approval (plan task 2.2).
