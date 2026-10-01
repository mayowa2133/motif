# Message-driven production plans

The new entry point is `scripts/motif_direct.py`. The earlier `motif_produce.py` remains supported legacy calendar-template mode, with its existing contract intact.

## Execution boundary

The command calls the installed, authenticated Codex CLI to generate a JSON production plan and review it. It then validates finite state transitions, generates a new local Kokoro narration take, aligns the actual words, compiles allowed actions into the existing Motif event JSON, renders through HyperFrames, and finishes the encoded combined mix.

This is a live model integration, not a saved example response or keyword-to-story lookup. The new evaluation briefs supply message, audience, desired duration, tolerance and output slug. They do not supply scripts or shots. Initial plans, actual model prompts/responses, review records, accepted plans, storyboard, action trace and output measurements are saved in each production directory.

The backend uses `codex exec --output-schema` and an ephemeral read-only session in an empty working directory. Its prompt provides the brief, planning contract and capability registry; it requests no tools. The caller rejects tool-use responses. The video runtime only receives compiled, allowlisted data. It does not execute code written by the model. This CLI invocation pattern is documented in [OpenAI's non-interactive mode guide](https://learn.chatgpt.com/docs/non-interactive-mode).

No new provider account or API credential was added. This machine's Codex CLI is signed in with ChatGPT. Its desktop model setting `gpt-6.1-sol` was rejected by the CLI backend during development. The evaluated workflow explicitly sets `MOTIF_PLANNER_MODEL=gpt-5.6-sol`, which appeared in the CLI's freshly fetched available-model catalog. This choice is recorded per run; there is no silent model or saved-plan fallback. Planning consumes usage on the signed-in account.

## Run

From the repository root:

```bash
MOTIF_PLANNER_MODEL=gpt-5.6-sol python3 scripts/motif_direct.py run --brief briefs/planning/calendar-declined.json
MOTIF_PLANNER_MODEL=gpt-5.6-sol python3 scripts/motif_direct.py run --brief briefs/planning/arena-no-winner.json
```

Existing output directories cannot be overwritten; use a fresh slug to rerun. To inspect scope or validate a saved plan without model calls or rendering:

```bash
python3 scripts/motif_direct.py capabilities
python3 scripts/motif_direct.py validate --brief <brief.json> --plan <production-plan.json>
```

The default model comes from existing Codex configuration; `MOTIF_PLANNER_MODEL` explicitly overrides it for this integration without modifying global settings. Authentication failure, backend failure, unsupported assets/actions, rejected review or duration conflict stops production with a specific error. Failed attempts remain separate and preserved.

Requirements: Python 3.11+, `jsonschema` (declared in `scripts/requirements-planning.txt`), the signed-in Codex CLI, Node/npm, FFmpeg/FFprobe, the existing Kokoro environment, and the local Arial Bold font already used by approved compositions. `HYPERFRAMES_PYTHON` can select the installed Kokoro Python; otherwise the existing cache environment is used. HyperFrames is pinned to 0.8.97 for new productions; frozen demos retain their original pins. An embedded local font keeps new exports repeatable on this machine; font redistribution rights must be resolved before shipping the font in a hosted product.

## Brief and plan contracts

A message brief contains exactly:

| Field | Meaning |
| --- | --- |
| `slug` | Fresh output identity under `videos/productions/` |
| `message` | Meaning and outcome the planner must preserve |
| `audience` | Guides the planner's language and explanation choices |
| `intended_duration_seconds` | Planning constraint, 12–25 seconds |
| `duration_tolerance_seconds` | Explicit permitted deviation, >0 and ≤3 seconds |

The [production-plan JSON Schema](../schemas/production-plan.schema.json) rejects extra fields. A plan contains the original message/audience, claims, illustrative assumptions, selected world and registered assets, missing asset requests, expected final state, ending action, and 4–6 beats. Each beat includes subject/action/before-and-after/focal-detail/consequence, generated narration, caption/headline, chosen framing, and semantic actions with exact spoken cues and prerequisite facts.

Narration is concatenated from beat sentences. The storyboard, visible wording, caption cards, framing and structured events all derive from that same plan. There is no separate fixed script or demonstration timeline. The new command performs no message-keyword dispatch; the model chooses a supported world and sequence. Structured plan validation checks explicit state and capability requirements, while model review assesses broader brief fidelity.

## Supported filmmaking capabilities

The canonical Bot geometry, palette and paper texture are unchanged. The available worlds reuse approved parts:

| World | Reused bindings | Plan-controlled actions and framing |
| --- | --- | --- |
| Calendar | Board, appointment, dashed proposal, decision tab, human fingertip, Bot, desk, wall/floor | Propose; person's approve or decline press; commit after approval. Wide/detail framing, labels, wording, script and outcome follow the plan. |
| Arena | Arch, crowd, stage, two answer sheets, identical link stencil, human fingertip, Bot, wall/floor | Check A or B with fail/pass route geometry; select only a passing answer; hand both tested sheets to a person. Pair, matched A/B close views, and receiving-person shot. |

Small reusable extensions: a coral cross decision on the existing control, parameterized pass/fail route and result layers on answer sheets, and a receiving-person staging binding using the existing human asset. No new mascot, environment or speculative prop library was generated. Camera cuts and motion use the existing `FROM_TO`, `TWEEN`, `SET`, `SCENE_CUT` and `CAPTION_REPLACE` engine actions.

The calendar still has two illustrative rows at 3 PM and 4 PM; arbitrary times, full schedules or the no-opening branch are not implemented. The arena's link test is an illustrative metaphor, not a real answer evaluator. Two candidates are supported; additional actors, arbitrary actions and unresolved asset requests are capability errors. Plans can request approved/booked or pass/selection actions, but those branches have state tests rather than completed video evaluation in this milestone. The two evaluated productions exercise decline/unchanged and both-fail/human-handoff.

## Review and timing

A deterministic pre-render review simulates state changes. It requires a visible proposal before a human decision, approval before committing a booking, a passing result before winner selection, both answers tested before handoff, and a simulated final state equal to the plan's expected final state. Unsupported actions and shot/world mismatches cannot silently disappear.

The initial plan and initial storyboard are preserved. One planning correction is permitted if schema/state checks, actual speech timing or model review find issues. After one correction, failure stops the run. Before rendering, a separate live model call reviews the brief against the plan and actual action timings. This is evidence of review, not a semantic guarantee.

Actual transcript matches determine beat starts, caption handoffs and action cues. Matching coverage must be at least 90%; unmatched beat/action anchors cause an error. Exact concatenated ASR groups (such as “a cross” transcribed as “across”) share their measured token interval; these coarser boundaries are recorded, never interpolated into invented word timings. Each meaningful choreography must finish before the next beat; the measured export must fit the explicit intended-duration range. The suggested word budget guides planning, while measured speech duration controls acceptance. The command revises the plan or reports conflict, rather than stretching a previous demonstration timeline or accelerating speech. Captions are short paraphrases; the last card remains during the ending hold. Headlines in action beats appear only after the physical choreography completes.

The encoded finishing stage preserves the −16 LUFS target (±0.8 LU), ≤−1.5 dBTP ceiling, first/final encoded video-stream identity, matching duration, and mobile playback export. Picture is 1080 × 1920 at 30 fps. Automated checks do not replace sampled-frame inspection or subjective listening.

See [the milestone review](PRODUCTION_PLAN_MILESTONE_REVIEW.md) for actual evaluation results, corrections, shared hashes and manual steps.
