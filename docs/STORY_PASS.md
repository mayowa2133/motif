# The story pass

Motif's gates catch problems with the look: headlines, labels, sets, palettes,
the camera. The story pass catches problems with the story before any frame is
drawn, and the animatic shows the result in minutes instead of a full render.
It is required: `check` fails a brief without a `story` block, except the
briefs written before 2026-10-12 listed in `quality/story-pass-exempt.json`
(do not add to that list).

The ideas are adapted from three story-craft skills reviewed on 2026-10-12
(a writers'-room story engine, a film director's planning skill and a
narration skill). Motif keeps their story tests and drops what does not fit:
approval stops (Motif iterates on its own), AI video generation (Motif draws
from its library), and character backstory (too heavy for a 30 s explainer).

## Order

1. **Premises.** Before any beat, write at least three different premises in
   `story.premises`: each names one object, what it wants or what is wrong with
   it, the obstacle, and the picture at the end. Put the first idea that came
   to mind first, then push past it. Pick one in `story.chosen` and say why.
2. **Ending first.** Write `story.ending` (the final picture that keeps the
   hook's promise) and `hook.story.promise` before the middle. The opening
   plants details in `hook.story.sets_up` that the end pays off.
3. **Beats as changes.** For every beat write `story`:
   - `purpose`: complicate, demonstrate, reveal, escalate or resolve.
   - `link`: `but` or `therefore`. If only "and then" fits, the beat is a list
     item: cut it or rewrite it.
   - `before` / `after`: the object at the start and end of the beat. `after`
     must use words the viewer reads on screen (headline, payoff headline,
     machine labels or screen lines), so the field describes the film, not a
     wish.
   - `action`: the one physical action that makes the change.
   - `sets_up` / `pays_off`: short tokens for the set-up and pay-off ledger.
   - `line_job`: what the narration does that the picture cannot (context,
     anticipation, explain, land).
4. **Check.** `python scripts/motif_reel.py check --brief BRIEF --allow-draft`
   (or `python scripts/motif_story.py check BRIEF`).
5. **Animatic.** `python scripts/motif_reel.py animatic --brief BRIEF --out RUNS
   --tts-python PY --allow-draft` voices the brief, compiles it and writes
   `RUNS/<slug>/review/animatic.mp4` (two stills per shot on the real voice)
   and `review/storyboard.png` (each shot labelled with its link, purpose and
   after state). Watch it with the sound on: does the opening promise
   something, does every shot change something, does the end keep the promise?
   Fix the brief and repeat before you spend a render.
6. **Narration last.** With the timing known, revise the lines: vary sentence
   length (short, then long), keep each line to what the picture cannot say,
   and make the last beat a line people would repeat.

## Voice (the narration pass)

Adapted on 2026-10-15 from the "/human" writing skill (millee.md), which rests
on StoryScope (arXiv 2604.03136): AI and human stories were told apart at 93%
from structure alone. AI narrators state the moral (77% against 52% of human
ones), keep one tidy track, and escalate flatly (Claude's own fingerprint). For
a 30 s explainer that means:

1. **Never explain what it means.** No closing "that's why", "the real
   point", "it's that simple". The last change on screen is the point; the
   line says what happens, not what it proves. A line that calls back the
   hook's own picture ("no AI marks its own homework" after "graded its own
   code an A plus") is a payoff, not a moral: keep it.
2. **Every line holds a handle**: a number, a name, a command or a thing the
   viewer can picture ("git reflog", "ninety days", "no rate limit"), not a
   category ("better results", "the plan holds up").
3. **Start at the interesting moment** and backfill: the hook is the moment
   something goes wrong or surprising, not the topic.
4. **Escalate.** Each beat raises the stakes or the payoff of the one before
   (a bigger number, a worse failure, a second use). A run of equal-sized
   beats is a list.
5. **Say plain feelings plainly** when the host or viewer feels one ("that's
   scary", "it's gone"), in a few words, instead of describing the reaction.
6. **Surface last**, after the structure: no "it's not X, it's Y", no stock AI
   words (seamless, unlock, game-changer, magic, supercharge), no dashes, no
   fillers (actually, really, basically).

7. **Say it aloud.** The viewer hears each line once: no dropped verbs ("and
   Claude the code"), no file names the voice trips on (SKILL.md), no jargon
   the picture does not show. Do not rewrite a line that already works.

Blind test (2026-10-15): the rules rewrote 2 to 4 lines in each of three films
(Claudex, git reflog, second brain). A blind judge preferred the rewrite only
for second brain, where vague lines became pictures ("every page is a circle
and every link a line"). It preferred the originals of the other two, because
the rewrite dropped hook callbacks and added lines that are hard to say;
rules 1 and 7 now say so. Each gap was slight. The surface tells (rule 6) were
already almost absent from Motif briefs.

Subplots, digressions and unresolved endings, which the skill also asks for,
are fiction advice; a reel keeps one object and lands its ask. `check` gates
rule 1's common phrases and rule 6 (`scripts/motif_narration.py`) and warns on
rule 2.

## What `check` gates

- At least three different premises, and a chosen one.
- Every beat has a story block; before and after differ; the after state shares
  a word with what is on screen.
- At least one beat complicates (a `but` link or a complicate beat).
- The last beat reveals or resolves.
- A machine that comes back after another set must be the same object
  changing: the returning beat pays off something its earlier appearance set
  up. Otherwise it is a second metaphor on the same machine, which reads as a
  repeat. Briefs without a story block get this as a warning.
- Every token set up is paid off later; every pay-off was set up earlier; the
  last beat or CTA pays off something the hook set up.

Warnings (recorded, not failing): flat narration rhythm, three beats in a row
with the same purpose, `visual.hold` on a beat meant to demonstrate or resolve,
no line marked `land`.

## Example beat

```json
"story": {
  "purpose": "complicate", "link": "but",
  "before": "one key ring with one password key",
  "after": "the same key copied onto 9 locks",
  "action": "the host hangs the key on every door",
  "sets_up": ["copied-key"], "line_job": "anticipation"
}
```

## A/B result (2026-10-12)

One topic (passkeys), fixed length, look, mascot, voice and facts; each brief
written by a fresh agent (`quality/ab-story/`). Mayowa watched both blind on
the phone and picked the story-pass film: "it doesn't reuse metaphors; in film 2
I saw the lock twice". Film A (no story pass) used six machines, one per fact,
and brought the padlock back as a new idea; film B carried one password
(Sunny42) from the phone's saved passwords to the key that opens the bank lock,
then to the fingerprint and the wall of phones. B's animatic also caught three
headlines cut mid-phrase and a counter covering a screen before the render.
The returning-machine rule above came from this review.
