# The improvement loop

Every reel Motif makes should leave the next one better. A problem a reviewer
finds once becomes a rule, and where possible a check, so no later film (made
by any agent) repeats it.

```
brief -> check -> run -> review -> retro -> lesson (+ check) or library work -> regress -> next brief
```

## 1. Retro after every run

```bash
python scripts/motif_improve.py retro RUNS/<slug> --feedback "headline sat too long on the answer beat" --reviewer Mayowa
```

Writes `RUNS/<slug>/retro.md` (stages, what the lesson checks caught, library
requests, feedback) and appends one line to `quality/run-log.jsonl`. Run it
again with `--feedback` when the phone review comes in.

## 2. Turn each new symptom into a lesson

```bash
python scripts/motif_improve.py lesson --source "Mayowa, second-brain cut 2" \
    --symptom "two headlines starting ANSWERS read as one 4.3 s headline" \
    --rule "Consecutive headlines never open with the same word" --check headline-openers
```

Lessons live in `quality/lessons.json`. Each has a `level`:

- `gate`: a check in `scripts/motif_lessons.py` (`CHECKS`) that fails the run.
- `warn`: the check runs and is recorded in the retro, but does not fail.
- `brief`: a rule for brief authors, shown in `catalog`'s `brief_rules`, until it
  can be measured.

When a rule can be measured on the compiled project (plan, set layouts, SVG
labels), write the check: a function `(project, plan, layouts) -> findings`
added to `CHECKS`, plus a test that reproduces the original failure. Prefer
fixing the cause in the planner or set solver too (L011 is both a check and a
solver rule).

## 3. Grow the library from what films asked for

```bash
python scripts/motif_improve.py backlog
```

Ranks `quality/library-backlog.json`: machines, rooms, inserts and costumes
that briefs requested but the library lacks, and lessons that keep firing.
Build the top items as DRAFT library entries with tests.

## 4. Regress before the next film

```bash
python scripts/motif_improve.py regress
```

Re-checks every brief in `quality/benchmark-briefs/` and
`quality/adaptation-briefs/` against the current rules, so a new rule is
proven on old films and a library change breaks nothing.

## History

| lesson | came from | enforced by |
|---|---|---|
| L001-L008 | rounds 1-8 of the reference-quality work (2026-10-09/10) | looks + variety, semantics, provenance, finish, pacing, sound-off |
| L009 shared-object palette | Codex's v11 critique (Python lock pink then teal) | check, gate |
| L010 headline openers | second-brain cut 2 (headline held 4.3 s) | check, gate |
| L011 label occlusion | second-brain cut 2 (crate covered PAGES 7) | solver rule + check, gate |
| L012 label legibility | second-brain cut 2 (21 px page titles) | check, warn |
| L013 clipped tags | second-brain cut 3 retro | vault forget mode redrawn; brief rule |
| L014 set variety | cut 3 vs references (one room for 28 s) | check, gate |
| L015 headline length | cut 3 vs references (two-line vague cards) | check, warn; strip headline in paper-craft |
| L016 product on screen | cut 3 vs references (product shown once) | check, warn; app-screen files/note/graph/chat views |
| L017 host in front | cut 3 vs references (host half hidden behind the machine) | solver rule + check, gate |
| L018 paper rooms | cut 3 vs references (flat vector, bright walls) | paper-craft look: crumpled material, dusk room palettes, darker grade |
| L019 runtime | cut 3 vs references (43.6 s vs 20-30 s) | brief rule |
| L020 sticker clear | second-brain cut 4 (logo stickers covered screen text) | sticker placement + check, gate |
| L021 whole headlines | second-brain cut 5 (CTA read BUILD IT ONCE USE) | planner cuts at clause or connector; check, gate |
| L022 wall variety | second-brain cut 5 (5 of 12 sets striped) | per-beat wallpapers in papered rooms; check, gate |
| L023 host acts | second-brain cut 5 (Memo watched in 9 of 12 frames) | host carries a note and throws it in at contact; brief rule |
| L024 full screens | second-brain cut 5 (terminal read "> cd sec") | app screens start 40% typed; chat answers after send; brief rule |
| L025 label collision | second-brain cut 6 stills (CLAUDE IS IN over the last line) | result stickers below text; check, warn |
| L026 motion events | cut 6 vs references (0.6 picture changes/s vs 0.7-1.9) | snap framings per shot + stronger contact kick; motion stage gate |
