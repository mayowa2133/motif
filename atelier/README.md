# Motif Atelier

Motif Classic asks *what film can we make with the approved kit?* Atelier asks
*what is the strongest way to tell this story, and what artwork, performance or
animation code does it need?* It is an explicitly selected mode with its own
command, contracts, folders and reviews. Classic (`scripts/motif_reel.py`) is
unchanged. Agent rules: [AGENTS.md](AGENTS.md). What the three pilot films proved and what remains: [PILOTS.md](PILOTS.md).

## Commands

```bash
python scripts/motif_atelier.py run --idea "A silent comedy about a character trying to catch its runaway shadow" --slug runaway-shadow
python scripts/motif_atelier.py run --brief atelier/examples/science-short.json
python scripts/motif_atelier.py resume --project atelier/runs/runaway-shadow      # or atelier/projects/runaway-shadow
python scripts/motif_atelier.py status --project atelier/runs/runaway-shadow
python scripts/motif_atelier.py render --project ... [--stills 30,90] [--range a:b] [--size delivery]   # DIAGNOSTIC_ONLY
python scripts/motif_atelier.py ledger --project ... [--add-unrecorded --origin ... --author ... --rights ... --use ...]
python scripts/motif_atelier.py concept-change --project ... --to new-approach-id --reason "..."
python scripts/motif_atelier.py blocker --project ... --note "..."
python scripts/motif_atelier.py approve --project ... --by NAME --decision approved|rejected --note "..."   # a person only
```

Options on `run`/`resume`: `--worker handoff|codex` (who authors),
`--reviewer auto|codex|handoff` (auto uses the Codex CLI when it is installed and
signed in, otherwise writes a handoff), `--tts-python` (Python with kokoro-onnx;
default `.venv/bin/python`), `--workers` (parallel render segments). Exit codes:
0 `REVIEW_REQUIRED` or a human decision, 3 waiting for an author or reviewer,
2 blocked, 1 error.

## Layout

```
atelier/
  AGENTS.md README.md            the creative contract and this guide
  contracts/*.schema.json        brief, concepts, direction, film, asset-ledger, review
  engine/                        project state, contracts, playback, sound, review, orchestrator
  engine/runtime/                atelier.js + player.html: the only film/renderer contract
  examples/science-short.json    an example brief
  projects/<slug>/               authored and committed: brief, concepts, direction, source/, reviews/, manifest
  runs/<slug>/                   generated, ignored by Git: voice takes, mixes, proofs, roughs, deliveries, diagnostics
```

## The input contract

`mode: "atelier"` (explicit selection), `slug`, `idea`; optional `audience`,
`classification` (factual, fictional, mixed or unspecified), `intended_effect`,
`duration_s` (a starting point, not an invariant), `style`, `references`,
`constraints`, `locked_wording` (must be spoken verbatim) and `resources`
(concept count, repairs per approach up to 2, delivery renders, render minutes).
Shot plans and technical settings belong downstream.

## Stages and statuses

| stage | who | done when |
|---|---|---|
| intake | engine | the brief validates |
| concepts | author | N different premises, scored as hypotheses, one chosen with a rationale |
| direction | author | ending, opening promise, shot plan of visible change, style sheet, hardest shot, claim ledger if factual |
| proof | author + engine + inspector | the hardest shot renders at 360x640 and its inspection says PROCEED |
| source | author | film manifest, entry script and ledger validate; every planned shot is in the film |
| audio | engine | every narration take fits its slot (voice never sped up); stems, mix and captions written |
| rough | engine | a 360x640 preview with sound, frame count checked, evidence decoded from the encode |
| review | independent reviewers | story, visual (and factual) responses PASS for the current request |
| delivery | engine | 1080x1920 and 360x640 encodes clear every technical check |

`AWAITING_AUTHORING:<stage>` writes `handoff/<stage>.md`; `AWAITING_REVIEW:<role>`
writes `reviews/<role>-request.json` and `.md`; `BLOCKED:<reason>` names the gate.
The last automated status is `REVIEW_REQUIRED`. `approve` (a person) sets
`HUMAN_APPROVED` or `HUMAN_REJECTED` for the current delivery hash only.

## Quality policy

Judged against the film's own genre and intention, never against Classic's
look. A silent cartoon is not failed for having no narration, a one-location gag
for having no room changes, or a new character for not looking like Bot.

| gate | what passes | evidence |
|---|---|---|
| story (independent) | opening promise, progression, payoff, cause before effect, normal-speed clarity, picture and sound telling one story | ordered frames, dense strips, phone frames, timed narration |
| visual (independent) | focal hierarchy, identity and continuity, composition, readable action, motion and performance, style coherence, phone readability, no defects | same |
| factual (independent, factual or mixed films) | claims match sources, narration maps to the ledger, dramatization labelled | ledger, narration, frames, web search |
| technical (measured) | 1080x1920 and 360x640 H.264 yuv420p, exact frame count, AAC 48 kHz stereo, A/V duration, -14 LUFS +/- 1, true peak <= -1 dBTP, zero clipped samples, cue sync, soft captions when narrated, delivered picture matches the reviewed preview, deterministic re-seek, rights ledger | the delivered files |
| human | watching on a phone with sound, rights and facts confirmed | `approve` |

There are no averages. Any FAIL, any NOT_ASSESSED on a dimension frames can
establish, any undeclared NOT_APPLICABLE or any critical issue blocks. Two
dimensions need moving playback (`clarity_normal_speed`, and listening). When the
reviewer only had frames, their NOT_ASSESSED is **deferred to the person's phone
viewing**: it is shown in the status, never counted as a PASS, and a FAIL there
still blocks. Measurements are not listening approval.

## Reviews and freshness

A request binds hashes of the brief, concepts, direction, source tree, audio
master, the preview encode and a fingerprint of its decoded frames. A response
answers exactly that request; any upstream change makes it stale and it is
archived under `reviews/history/`. The one exception: if only paths or container
bytes changed (same brief, concepts, direction, source and audio, and every shared
sampled frame within the same-picture tolerance: thumbnail distance mean <= 1.0,
max <= 24), the verdict carries over and the carry is logged. Failed reviews
are counted against the approach before any request is replaced. Two repair
rounds per approach; the third failure stops further renders on it.

Backends: `codex` reuses Classic's read-only, data-only `codex exec` call with
the evidence images; `handoff` writes the request and waits for a separate
reviewer (a person or another model session) to write the response. The
builder may inspect a proof (recorded as builder self-inspection) but cannot
pass story, visual or factual gates.

## Playback and its boundary

`render(ctx, env)` is called per frame in any order by a headless Chromium
page served only the project's `source/` and the runtime; every non-local
request is aborted and fails the render, `Math.random`, clocks and timers are
disabled, and each frame has a timeout. Frames are rendered in independent
seekable segments and concatenated. Python never imports project files. This is
browser isolation plus request interception, not an operating-system sandbox.
Source is linted before it runs (no fetch, eval, remote URLs, timers, storage);
the lint is a convenience, not the boundary.

Rebuilds reproduce frame counts and timing exactly and pictures within a
declared tolerance (thumbnail distance), not byte-identical encodes.

## Sound

Narration: one take per line with the approved Kokoro voices through the same
pinned HyperFrames TTS as Classic, cached by content so a resume never
regenerates an unchanged take. Timing is measured per line; nothing claims
word-level alignment, and a line that must land on an action is split at that
action. Sound design: seeded recipes named in `film.json` on the picture's moment
table. Music: an optional note list rendered by small synth instruments. Mix:
music ducked under voice, measured gain into a look-ahead limiter until the
integrated level converges on -14 LUFS, AAC at 256 kbps (192 kbps overshot sharp
transients by about 3.8 dB in testing).

## Production metadata

`production-metadata.json` (written at delivery): concept, hook (opening image),
style, classification, duration, approach and revision hashes. No uploading,
scheduling or analytics.
