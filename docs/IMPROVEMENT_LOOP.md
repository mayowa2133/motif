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
