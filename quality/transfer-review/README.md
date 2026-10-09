# Explicit review without private reference pixels

An independent transfer worker may receive an immutable kit containing learned relationship metadata and a human-accepted quality rubric, but be prohibited from consulting original films. The normal reference-calibration path remains the default. This opt-in path reviews fresh project-owned evidence against the frozen text; it does not claim source calibration, reference parity, or human approval.

Enable before planning:

```sh
python scripts/motif_transfer_review.py enable --project /absolute/new-project --kit /absolute/frozen-kit
```

The kit must contain `references/quality.md`, `references/learned-prior.json`, and `references/frozen-package.json`. The manifest supplies package file hashes, package digest and repository dependency hashes. Mutating any dependency invalidates the profile. Projects with existing required/accepted reference calibration cannot mix modes.

Existing director, structure, direction and moving-critic APIs dispatch explicitly from `transfer-review/required.json`. Structure review precedes contract preparation. Then:

```sh
python scripts/motif_concept.py prepare --project /absolute/new-project
python scripts/motif_transfer_review.py concept --project /absolute/new-project --evidence /absolute/new-project/concept-evidence.json
python scripts/motif_transfer_review.py opening --project /absolute/new-project --evidence /absolute/new-project/opening-evidence.json
```

Use normal rough/story/visual/repair/QA APIs after concept and opening admission. Contract preparation is data-only with no image attachments. Concept evidence uses the existing contact-proof contract plus `origin: "project-authored"`, all setup IDs, own `source_hashes`, `caption_free: true`, one hashed native `previews` image per setup, and clean native BEFORE/CONTACT/AFTER for every interaction. `images` is a nonempty ordered hashed list of own evidence. Opening evidence adds own hashed `setup_timing` JSON (saved plan_sha256 and ordered setup_id/start/end intervals partitioning actual choreography; include its resolved path in source_hashes), plus `video` and `without_captions`: matching native 360×640, fps/frame count, duration 3–5 seconds. Opening reviews exactly the known setup subset intersecting [0, actual decoded opening duration). The gate derives ordered native samples and full-rate observations directly from BOTH movies with existing motif_quality.evidence; arbitrary caller stills cannot substitute for motion evidence. All evidence paths resolve within the new project; outside paths and escaping symlinks are rejected. An origin attestation is not forensic authorship proof.

Concept/opening receipts live separately under `transfer-gates`, use schema `transfer-gate.schema.json`, and bind scope `transfer-independent-v1`, project root, profile, plan, source evidence, actual invocation attachments, response, invocation and policies. `basis_id` identifies only `transfer-rubric` or `learned-prior`. Moving critics retain the existing `gold_id` schema field for compatibility, explicitly redefined in their prompt/receipt as a textual basis, never a retrieved clip. They attach only the fresh project's rendered evidence. Human approval stays false.

All original substantive checks remain: complete setup/check coverage, native readable contact/support/ownership, causal actor, hero hierarchy/material/acting, temporal opening development, full story/visual/shot checks and bounded repair. FAIL and NOT_ASSESSED block; NOT_APPLICABLE is limited to explicitly absent Bot acting/role. Two completed concept rejections for the same critical setup/check stop cosmetic iteration. Historical failed receipts remain bound to their original inputs rather than requiring old pixels to match newly repaired art.

Protocol tests use synthetic art and mocked model output. They establish routing, isolation, receipt freshness and criteria coverage, never creative quality. A successful live transfer requires a fresh worker to execute these gates and bring the actual native moving rough to human review.


Transfer supports the news/script-data intake and a fresh project-authored custom builder using only the frozen kit's owned materials, canonical generator and new art. Do not invoke legacy scene/script/UI compilers that copy prior production scenery; those routes are outside this input scope. Shared planning and critic contracts remain available without their old-film/debugging examples in explicit transfer mode.

A concept change after deadlock requires a bounded data escape, not edited setup IDs or paraphrased visual-rule prose:

```sh
python scripts/motif_transfer_review.py escape --project /absolute/new-project --old-plan /absolute/new-project/transfer-gates/concept/reviewed-plan.json --setup failed-setup --patch /absolute/new-project/own-escape-patch.json
```

The patch uses the existing concept-replan schema and pure apply_patch validation (exact script/beat coverage, untouched setups, token scope and full plan/structure consistency). The saved current plan must equal the validated result. Non-split escape must change relationship archetype; split must create multiple distinct relationships. The previous plan must be an immutable completed own review. Families ignore identifiers/layout/palette/free-text rule rewording; old failures remain archived. The receipt grants only permission for fresh full-project concept review, never inherited approval. The calibrated replan workflow and its reference-gate history are not used.
