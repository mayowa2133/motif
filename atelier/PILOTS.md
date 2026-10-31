# Atelier pilots: what was made, what was checked, what remains

Three original films made through the same entrypoint (`scripts/motif_atelier.py`)
and the same engine. Each film's source, concepts, direction, asset ledger,
review requests and responses (current and archived) are in
`atelier/projects/<slug>/`. Renders, voice takes and review frames are in the
ignored `atelier/runs/<slug>/`. Nothing here is approved or published: a person
must watch each film on a phone with sound.

| | A: why-popcorn-pops | B: runaway-shadow | C: the-keeper |
|---|---|---|---|
| kind | factual explanation, narrated (af_heart) | character comedy, silent | narrative reveal, sparse narration (bf_emma) |
| art and motion | risograph cutaway: overprinted inks, halftone, misregistration; diagrammatic morphs, slow-motion burst | flat bold cartoon; pose-driven puppet and projected cast shadows; squash, stretch, overlap | dark storm-at-sea look with soft gradients; parallax sea, additive light beam, rain, lightning; creature reveal |
| new characters | none (the kernels carry it) | Pim and its shadow twin | Ada, the calf, the mother |
| entrypoint | `run --brief atelier/examples/science-short.json` | `run --idea "A silent comedy about ..."` | `run --idea "A short fictional suspense story ..."` |
| length | 34.2 s | 29.6 s | 33.8 s |
| status | **BLOCKED:UNRESOLVED** | **REVIEW_REQUIRED** | **BLOCKED:UNRESOLVED** |

## B: Runaway Shadow (delivered for human review)

- **Made:** concepts (3 premises), direction, a new character puppet (Pim) and
  its shadow, drawn as real projections of Pim's pose through one light
  direction into a single flat layer, which is how the twin can melt into the
  tree's shade. A note-list pizzicato/marimba/celesta score and 60+ seeded sound
  cues are on the moment table. This is the action unavailable in Classic's
  catalogue: a shadow that detaches, hinges up into a standing twin, runs,
  hides and is pinned back.
- **Reused:** Atelier engine only (playback, audio mix, review, delivery checks);
  no Classic library pieces.
- **History:** proof (the escape) passed builder inspection. Approach
  `copycat-lure-v1` failed independent visual review three times (chase knot,
  a stomp that missed the shadow, the cap-net prop), so the budget blocked it.
  A recorded concept change (`stomp-lure-v2`) restructured the middle act
  around three missed stomps that plant the winning fourth. Independent
  story and visual reviews then passed with no critical issues.
- **Delivery checks (all PASS):** 1080x1920 and 360x640 H.264, 888 frames,
  AAC 48 kHz stereo, -14.22 LUFS, -1.78 dBTP, 0 clipped samples, 3 ms cue
  offset, delivered vs reviewed picture distance 0.47, byte-identical
  out-of-order re-seek, rights ledger.
- **Still needs a person:** comic timing in motion; whether the opening lag
  reads in the first seconds (reviewers could not see it in 0.5 s samples);
  how the sound feels (no one has listened). Reviewers' non-blocking notes:
  stomp 1 reads weakly as a dodge, and Pim's shadow falls toward the sun's
  side.

## A: Why Popcorn Pops (blocked; story and facts passed)

- **Made:** concepts, direction with an 8-claim ledger (Virot & Ponomarenko
  2015; Hoseney et al. 1983; Purdue/Hamaker 2020), each claim marked
  observation or inference, with excerpts and five dramatization notes. Built
  a risograph cutaway look, a sealed and a cracked kernel, steam pressure, the
  hull splitting into halves, the foam bloom, a starch leg, the jump, a replay
  that puts the pop on the steam, and a screen-space thermometer gauge.
- **Fact verification limits:** the session's network policy blocked the
  publisher, HAL, CIMMYT and Purdue hosts. Excerpts come from web-search
  summaries of the abstracts, not from reading full texts. The "135 psi"
  figure seen in secondary sources was left out because no accessible primary
  source confirmed it. The independent factual reviewer was under the same
  limits and said so.
- **History:** three rounds. The reviewers caught real problems each time:
  - kernels drawn outside the bowl;
  - an unledgered "100 °C" readout and an unlabelled boiling simplification;
  - a crack sound on a beat meant to be silent;
  - steam vanishing at the burst;
  - a leg that read as a stand.
  
  Round 3: story PASS, factual PASS, visual FAIL (the leg still reads as a
  stand rather than a push; the flake passes behind the gauge at the apex).
  The budget blocked further repairs; a blocker is recorded with the two
  smallest next steps.
- **Viewable:** the reviewed rough (360x640, with sound) in
  `atelier/runs/why-popcorn-pops/rough/`. It is not a delivery.

## C: The Keeper (blocked at the last beat; story passed)

- **Made:** concepts, direction, and new characters: Ada (an elderly keeper in
  an oilskin with round glasses), the whale calf (eye, tear, crying mouth,
  spout) and the mother (a tail and a spout). There is a lighthouse with a
  hand-cranked lamp, a shutter lever and an additive beam that sweeps, finds,
  dims, flares, steers and lays a path home. Also a parallax storm sea, rain,
  lightning and a dawn re-light. Narration is seven measured lines (bf_emma,
  speed 0.92), with a storm sound bed, whale calls and a sparse pad and
  celesta score.
- **History:**
  - **Round 1:** reviewers caught the calf swimming tail-first and an invisible
    dawn payoff.
  - **Round 2:** story PASS; visual flagged the threat as a disc with a
    sparkle, the decision acted as panic, and a crank that faded with the
    lamp.
  - **Round 3:** story PASS (all six dimensions); visual 7 of 8 PASS, with one
    critical issue. The two dawn spouts still don't read at phone size
    (grey-blue puffs at about 1.75:1 against the peach sky).
  
  The budget blocked a fourth attempt. The blocker names the smallest fix:
  push in on the whales and draw white spouts with a dark rim.
- **Disclosed:** the round-3 rough was rendered by a runtime build that had
  a per-frame line-style leak (fixed before B's delivery). A re-render will
  differ by a few pixels. The story reviewer noted that the creature
  silhouette the round-2 visual reviewer asked for now reveals "what it is"
  early. That is a real tension between the two critiques, left for a person
  to weigh.
- **Viewable:** the reviewed rough in `atelier/runs/the-keeper/rough/`. It is
  not a delivery.

## Engine findings the pilots forced

These were all found by rendering and reviewing real films, not by design:

- Per-frame timeouts did not exist (`page.evaluate` waits forever). They now use
  Chromium's own termination.
- An unbalanced `restore()` in film code leaked the camera transform. The
  runtime now fails such frames.
- Removing the per-frame `save()/restore()` leaked line styles between frames.
  The deterministic-seek gate caught it before delivery.
- A caption track trimmed the picture through `-shortest`.
- AAC at 192 kbps overshot sharp synthetic transients by about 3.8 dB.
- Failed reviews could escape the repair count when a request changed, or be
  charged to the wrong approach.
- A Classic-era assumption, that the story gate needs normal-speed clarity
  from frames, was resolved as "deferred to the person, never PASS".

## Comparison with accepted internal work

Compared with VoiceStudio v6 (Classic's accepted visual benchmark), from 16
still frames and measured loudness only:

- **Loudness:** v6 masters at -16.0 LUFS / -3.4 dBTP over 32.9 s, and the pilots
  at -14 LUFS (Classic's later reel mixer also targets about -14).
- **Structure:** v6 tells its story through headline cards, labelled product
  screens and a recurring mascot. The pilots use no headlines (A has three
  readouts), and each builds its own world and characters.
- **Not compared:** craft parity was not claimed. No external creator references
  were inspected, and no audience data exists.

## Review effort and resources

- **Independent reviews:** 23 separate model sessions, each in a fresh context
  and given only the request and the decoded evidence. They are the same model
  family as the builder, a limit disclosed in every response. There were no
  human reviews; the builder did self-inspection for proofs only.
- **Render time:** A 3.7, B 3.0, C 2.1 render-minutes, all within the 60-minute
  budgets. Wall-clock time was dominated by the reviews (each round took 6 to
  26 minutes).
