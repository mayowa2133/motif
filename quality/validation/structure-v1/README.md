# Structural grammar validation

Implementation scope: planning and pre-render gates inside motif-gold-v1, retaining Quality System v1.1. No new production, render, audio, artwork or canonical promotion. Stop for review.

## Deliverables

| Requested output | Location |
|---|---|
| Canonical grammar | [MOTIF_STRUCTURAL_GRAMMAR.md](../../../docs/MOTIF_STRUCTURAL_GRAMMAR.md) |
| Film structure schema | [film-structure.schema.json](../../../schemas/film-structure.schema.json) |
| Setup contract | [setup-contract.schema.json](../../../schemas/setup-contract.schema.json), embedded in the film contract and existing plan schemas |
| Ordinary planner integration | [motif_direct.py](../../../scripts/motif_direct.py), [motif_script.py](../../../scripts/motif_script.py), shared [planning context and critic](../../../scripts/motif_structure.py) |
| Independent macro critic | [prompt](../../structure-critic/PROMPT.md), [schema](../../../schemas/structure-critic.schema.json) |
| Moving hierarchy rules | [visual prompt](../../visual-critic/PROMPT.md), [mapping into existing gates](../../rubric/hierarchy.json) |
| Planning fixtures/results | [clean fixtures](fixtures-clean/), [results.json](results.json), [live log](live-validation-clean.log) |
| Negative rowhouse registration | [rowhouse.json](../../negative/rowhouse.json) |
| Existing quality regressions | [results](existing-quality-regressions.json), [Python log](regression-tests.txt), [Node log](frame-sequence-tests.txt) |
| Frozen preservation | [results.json](results.json), [rowhouse byte baseline](rowhouse-preservation.json) |

## Results

- All ten clean live planning expectations passed: six rejection cases and four valid controls.
- 72 Python regressions and the Node seek regression passed.
- All 540 frozen benchmark/canonical files and all 1,940 rejected-rowhouse files are unchanged.
- These are planning/gate results; no new moving film was produced.

## Execution and boundaries

New planners return chapters/setups before beat detail. Setup spans quote the exact narration; each beat belongs to one ordered setup. Roles and environments agree with v1.1 shot contracts. Tokens declare origin, ordered state changes and destination. No quotas on setups, beats, duration, reactions or token counts.

A separate authenticated data-only critic reviews the whole plan. Missing assessment, semantic failure, incomplete correction coverage or stale input/policy blocks direction and rough. Macro failures receive bounded replanning before speech/animation; prior planning attempts are archived. Pre-animation replanning does not consume the two moving repairs. Story edits archive structure evidence along with direction evidence. Moving caption dependence requires replan. All ten existing gates, technical checks, asset lifecycle and human approval remain in place.

The schemas keep saved legacy plans readable. New direction/rough entry points require structure; this is not a grandfathered path for new production. A non-executable generic capability_error can use null film_structure. Unsupported creative worlds remain explicit agent-assisted development needs: this task did not add renderer capabilities to execute arbitrary worlds. Metadata alone is not execution proof.

## Audit notes

- Expected outcomes are stored outside critic prompts in each `expected.json`. Critics use the same ordinary `structure_review()`/`model_call()` path, in empty temporary working directories with no tools. These hand-authored fixtures test grammar/criticism, not autonomous first-storyboard quality.
- `fixtures/` retains the initial run. Its contracts accidentally inherited pricing/receipt fields from an older control. The long-setup critic correctly rejected those fields. The run was interrupted; partial calls are not accepted evidence. `fixtures-clean/` removes the irrelevant inherited fields and supplies the completed validation set. No report was edited to manufacture a pass.
- `backend-failed-configured/` retains the rejected gpt-6.1-sol CLI invocation. The CLI reported this configured model unsupported for the signed-in ChatGPT account. Validation explicitly selected gpt-5.6-sol via the existing `MOTIF_PLANNER_MODEL` option, matching prior v1.1 reviews and available local CLI models. Provider, credentials and global configuration were unchanged; no silent model fallback was used.
- Current Python/Node tests exercise updated code. Original, temporal-contact and minimal/dead-hold live evidence is checked for byte integrity and its recorded outcomes without rewriting it. Those historical reviews are not fresh rendered approval under the new grammar; the two authorized shared planning/gate source changes are listed in the regression record.
- The rejected rowhouse is excluded from gold retrieval. All its 1,940 files are checked against the baseline captured before implementation. The existing 540-file frozen manifest protects VoiceStudio v6 and canonical assets.

## Reproduce verification

Use the existing Python environment with jsonschema, Pillow, CairoSVG and numpy. No dependency upgrade is needed.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate_structure.py
PYTHONDONTWRITEBYTECODE=1 python3 scripts/verify_structure_regressions.py
```

`validate_structure.py --live` refuses to overwrite reviews. To start another live run, preserve this audit directory and author a fresh fixture run first. New ordinary productions in this current CLI environment can explicitly select the working model with `MOTIF_PLANNER_MODEL=gpt-5.6-sol`; configured gpt-6.1-sol still fails in the CLI. The validation scripts do not change that setting globally.

This is ready for structural-system review; all clean expectations passed. It is not a new-film acceptance, listening approval or factual verification. The rejected script's clean replan is a separate next production task. No commit or push is included.
