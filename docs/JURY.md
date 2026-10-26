# The jury pass

The scorecard measures what a number can catch (cut rate, motion, loudness,
product share, host size). Story, finish by eye and host acting stay with a
reviewer, and until now each grade was written from scratch, so grades of two
cuts were hard to compare. The jury pass gives every reviewer the same pack,
the same anchors and the same output, and it must be someone who did not make
the film.

Adapted from the review rubric of the MIT-licensed
[mg-styles-15](https://github.com/Vincentwei1021/mg-styles-15) repo
(reviewed 2026-10-26), whose films went make, independent review, revise,
twice. Its style prompts, 16:9 10 s spec and award-level framing are not
taken; Motif keeps its own references as the bar.

## Run it

```bash
python scripts/motif_jury.py pack RUNS/<slug>            # after run --render
python scripts/motif_jury.py pack path/to/film.mp4 --out DIR   # any video
```

It writes `RUNS/<slug>/review/jury/`:

- `contact-sheet.png`: a frame every 0.5 s with timecodes.
- `strip-move-*.png`: 8 frames, 2 apart, around the two fastest in-shot moves
  (cuts are excluded), to judge spacing, overlap and follow-through.
- `strip-payoff-*.png`: the same around every payoff contact (from the run's
  audio plan).
- `still-*.png`: full-resolution frames at the start, every payoff, every
  sixth of the runtime and the end, to judge type, edges and texture at 100 %.
- `pack.json`: spec numbers (size, fps, duration, LUFS, true peak, black
  spans, longest frozen span, cuts, motion) and where the payoffs land as a
  share of the runtime (a strong short usually lands its biggest payoff at
  60 % to 75 %).
- `jury-prompt.md`: the jury brief, with the film's beats and story promise.

## Grade it

Open a fresh agent session (or ask a person) that did not make the film, give
it the folder and `jury-prompt.md`. It scores six dimensions (story and
concept, motion craft, design and type, finish, sound and sync, technical) on
fixed anchors (6 = template level, 8 = the reference reels), lists critical
issues and 5 to 10 fixes with timecodes phrased as brief changes, and writes
`jury.json` next to the prompt.

Then, in the session that made the film: apply every critical issue and the
high-impact fixes, re-render, and pack again. Two rounds is the usual budget.
A fix that would apply to every film goes through the improvement loop
(`docs/IMPROVEMENT_LOOP.md`) as a lesson, not into one brief.

Mayowa's phone rating stays the final bar; the jury is there so the film he
watches has already been through two honest rounds.
