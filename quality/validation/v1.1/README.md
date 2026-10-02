# v1.1 hardening evidence

Status: ready for review. Fixtures/copies only; no new original film or canonical asset promotion.

## Results

- [Machine verification](results.json): new live critic records, source/image/media freshness, actual intermediate-frame differences, minimal scene and dead-hold outcomes, binding measurements and frozen hashes.
- [59 Python regressions](regression-tests.txt), [Node seek regression](frame-sequence-tests.txt).
- [Existing v1 live validation rerun](v1-regression-results.json): all four original faults caught, control passes, 540 frozen files unchanged.
- [Change note and binding limits](../../../docs/QUALITY_SYSTEM_V1_1.md).

## Fixture sets

### Temporal contact

[Caption-free native preview](temporal/renders/no-captions.mp4) · [captioned preview](temporal/renders/captions.mp4) · [manifest](temporal/quality-review/rough/evidence.json) · [visual report](temporal/quality-review/rough/visual-critic.json) · [story report](temporal/quality-review/rough/story-critic.json).

`t01` holds a paper continuously. `t02` matches its sparse before/contact/after samples but detaches at native frames 91–93. Consecutive frames 84–96 are supplied in explicitly ordered strips in both caption modes. Both live critics catch the intervening defect. This control also has art/composition failures; it is a focused contact test, not an approved artwork benchmark. No gate was relaxed to make it pass.

### Optional energy and minimal composition

[Caption-free native preview](minimal/renders/no-captions.mp4) · [manifest](minimal/quality-review/rough/evidence.json) · [visual report](minimal/quality-review/rough/visual-critic.json) · [story report](minimal/quality-review/rough/story-critic.json).

The enlarged, folded-paper `t01` has a brief intentional inspection pause, explicit minimal-isolated justification, zero environment cues and null optional energy channels. All ten owned gates pass across the independent critics. `t02` freezes its picture while promising a lift; story and energy fail. Mixed fixture gates remain blocking (`REPLAN_REQUIRED`).

### Renderer bindings

[UI focused](bindings/ui-focused.png) · [UI burdened](bindings/ui-burdened.png) · [UI absent](bindings/ui-absent.png) · [calm contact](bindings/calm-contact.png) · [workshop delivery](bindings/workshop/snapshots/frame-01-at-13.28s.png) · [measurements](bindings/results.json).

These are actual canonical SVG paint, compiled event data, and two native snapshots of a copied approved workshop workflow. Head acting and a shared assembly reaction preserve authored workshop contacts; independent gripped targets are explicitly unsupported. The ordinary UI compiler is also exercised by the regression suite; unrelated audio I/O is isolated in that unit test.

## Audit/reproduction

`build_quality_hardening_fixtures.py`, `build_quality_minimal_checks.py`, and `build_quality_binding_checks.py` author only isolated validation material. Frame builders reject overwriting an existing fixture run. Preserve audit directories when starting another run.

The two critic calls per set are separate authenticated `codex exec` invocations, with no tools, saved-response substitution, provider change or fallback. `*-invocation.json`, input prompts, wire schemas, CLI event streams, outputs and image ledgers are retained. Expected intervention labels stay in `expected.json` and are withheld from critics. `validate_quality_hardening.py` verifies every audited image was actually supplied.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
node --test tests/test_frame_sequence.cjs
PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate_quality_evidence.py
PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate_quality_hardening.py
```

Use Python with the repository's installed PIL/numpy/CairoSVG/jsonschema dependencies. Pinned HyperFrames versions remain 0.8.98/0.8.99. Native frame strips and pixel traces are not full playback or listening approval. Human final viewing/listening remains required; publishing is always false.
