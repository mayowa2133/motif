# Optional experiment gate

This standard-library CLI plans one optional addition at a time and records a
reversible local decision. It does not change Motif's producer, choose artwork,
enable candidates by default, or perform Git/network operations.

`registry.json` is a scoped research ledger. Positive findings keep their actual
limits; negative/inconclusive/unassessed findings remain available for research.
`default_enabled` is empty. Only the exact frontal-kit v0.1.2 setup contract is
eligible for a source-only trial. The full artwork rig and local research reports
are not distributed. Missing local evidence blocks assessment. Source-only
acceptance supplies no artistic approval or production default.

The key-pose pilot's narrow release/settled-ownership finding did not recur in its
fresh transfer pair. Its overall verdict is inconclusive; the reader-contact and
agency negative remains disputed and separate from accepted hard regressions.
No universal harmfulness or automatic research deletion is inferred.

## Plan and assess

Supply an exact context JSON with `id`, `scope`, `claims`, `artifact_type`,
`brief_sha256`, `baseline_artifact_sha256`, `baseline_git_commit` and preregistered
`events`. Each event names inclusive `baseline` and `trial` frame intervals.
Scopes and permitted evidence kinds are defined in `criteria.json`.

```sh
python3 scripts/motif_experiment_gate.py plan \
  --registry quality/experiment-gate/registry.json \
  --policy quality/experiment-gate/criteria.json \
  --context /path/to/context.json --output /path/to/plan.json
```

An empty request retains the previous accepted version set. Add one explicit
`--candidate ID` and pass `--state` for a combination trial. A state contains
`last_good`, `active`, `history` and `blocked_combinations`. Unknown component
hashes, unsuitable scope, unaccepted dependencies and known regressions reject an
addition. Individual wins do not certify a combined version.

`assess` also requires `--trial`, `--result` and `--evidence-root`. A result binds
its plan hash and references `brief`, `original`, `previous`, `trial`, exact
`components`, local `research_evidence` and comparisons against original and last
good. All evidence paths are relative to and contained within the supplied root;
each carries a SHA-256. Every comparison includes all six policy guardrails.

Each check has `result`, `kind`, `observation` and a hashed JSON `report`. The
report repeats `trial_sha256`, the pair identities and `criteria` assessments, excluding the
circular report reference. Supplementary evidence is hash-verified as well.

A reproduced hard regression restores the prior accepted artifact/version set
and blocks that exact combination/context. Ties, disputed findings and missing
evidence hold promotion while preserving research. Absence claims require all
frames in both declared intervals. Timing, motion and audio claims require
explicit full-speed picture/listening evidence; stills cannot supply it.
Playback reports also bind `trial_sha256`, so changed briefs, claims or event
intervals require fresh scoped review rather than reused approval evidence.
Encoded byte identity may establish unchanged output for a declared technical
refactor. Source-state identity cannot approve visual or audiovisual quality.

Optional `--state-out` requires `--state` and writes only the requested local
transition. Decisions are scope-bound and replay-idempotent. Human PR review is
separate from this local gate; `promotion_ready` never performs a merge.

## Validate without capture

```sh
python3 -m unittest discover -s tests -p 'test_experiment_gate.py' -v
node --test tests/test_setup_validation.cjs
```

`scripts/motif_setup_validation.cjs` provides optional finite-number, dense-array,
fixed-coordinate and string-ID guards extracted from the reviewed v0.1.2 setup
boundary. It contains no artwork, geometry or production wiring. Fresh tests cover
sparse/inherited entries, nonfinite/coerced values and input preservation. This
smaller utility is not the full rig's replacement or an artistic gain.
