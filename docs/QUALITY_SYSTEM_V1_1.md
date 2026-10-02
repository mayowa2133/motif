# Quality System v1.1

**Ready for review · 2026-10-02.** Narrow hardening of accepted v1 (`7a7f1bc`). No new production film, frozen artwork edit, provider/credential change, dependency upgrade, commit or push.

## Changes

### Audited art-only repairs

`motif_quality.state_fingerprint()` records semantic plan/event hashes separately from a deterministic render fingerprint. Render inputs include local assets, composition HTML/motion files, CSS/JS, production `source/`, style/config/audio/caption inputs, declared asset files and registered shared renderer sources. Paths and byte hashes are sorted; review evidence, exports, logs and caches are excluded.

New evidence stores the complete fingerprint. Edits, additions and removals invalidate advancement and critic invocation. `repair()` compares the current state with the latest active reviewed evidence, records both fingerprints and changed categories, and archives rough/final evidence. An SVG-only edit can consume a meaningful pass. Unchanged state cannot. A semantic plan edit also archives direction-review files so direction must run again. Event-only/art-only repairs retain the data review when its plan is unchanged. The maximum remains two meaningful passes.

Old v1 evidence retains its original hashed format and checks its recorded source map. Approved files are never rewritten for migration. New v1.1 evidence audits the complete source set, including added and removed files.

### Structured optionality

- `energy.dominant_action` is always a nonempty string.
- Other energy channels may be omitted or null. Live planner output uses explicit nulls; dummy “none/not applicable/no reaction” is rejected.
- `exit_overlap` may be null.
- `art_direction.environment_mode` distinguishes `physical` from `minimal-isolated`.
- Physical scenes need 2–3 cues. Minimal scenes may have none, with a nonempty story-specific `environment_justification`. `plan_check()` enforces these conditional constraints; the visual critic evaluates whether the justification is realized.
- Legacy contracts normalize in memory to physical and nullable missing channels. Canonical and approved plan bytes are unchanged.

The shared shot schema and its three embedded copies match. Planner, direction review and both critic instructions explain purposeful quiet pauses and minimal compositions. Missing optional channels never excuse a dead caption hold.

### Executable renderer coverage

| Renderer | Supported binding | Contact protection / explicit limits |
|---|---|---|
| Interactive/text-directed UI, ordinary `interactive-ui-v1` | Canonical `bot` acting; Bot and standalone plant/mug/lamp/clock reactions | Existing world contacts solve through primary placement/impact, outer local reaction and named performance. Missing/unknown targets reject. Screen, token, keyboard and pointer reactions lack complete anchor enrollment and reject. Production-scoped art revisions require their own adapter. |
| Workshop | `worker-0/1/2`, `carrier-bot`; focused/listening/talking/worried head, face and antenna channels | Authored arm, hand and tool choreography stays intact. `workshop-interaction` is one outer reaction around the complete assembly ensemble, excluding wall/floor/camera; every grip and held constituent shares it. Independent gripped-worker/tool/prop reactions, whole-body performance and absent-Bot choreography raise specific capability errors. |
| Calm paper | Canonical Bot acting, including absent; registered safe moving papers | Authored hand owners are explicit. Selected paper responses remap contacts before solving hands through the complete performance transform. Linked source/thread, hinge and static supports reject when geometry cannot safely update all attachments. Per-action targets are in `quality/bindings.json`. |
| Calendar/arena/high-energy paper | Existing v1 bindings | Preserved. |

These hooks use the current event engine and pure frame builders. No new renderer or arbitrary scene generator was introduced. Changing an operative field changes actual events/paint. UI frame context resets after each call, including errors; seeking does not accumulate state.

### Consecutive temporal evidence

Eight ordered samples, three individual native frames, declared contacts and full-rate painted pixel traces remain. Each declared contact/landing/handoff/impact adds six native frames before and after its event, clipped at shot boundaries. Up to eight declared meaningful events per shot keep context bounded.

Short, labeled four-cell rows retain native 360 × 640 images. The manifest records consecutive frame numbers, timestamps, event frame and strip order. All strips enter both independent critic invocations and the image hash ledger. Critics inspect anticipation, contact, continuous attachment, compression, consequence and recovery. This is decoded image evidence, **not MP4 playback**; final human viewing/listening remains required. Gold retrieval and its frozen clip ranges remain unchanged.

## Verification

- **59 Python regressions pass:** the entire relevant quality, directing, energy, UI, workshop, script, production-plan and brief suite; ten focused v1.1 tests.
- **One Node frame-sequence test passes:** exact boundaries, reverse/repeated seeks and invalid timing rejection.
- Existing recorded v1 live validation still catches all four faults and passes its control. No cached output was substituted.
- Four new independent live calls (two critics per fixture set) used the existing authenticated backend and explicit existing `MOTIF_PLANNER_MODEL=gpt-5.6-sol` override. Invocation inputs, schemas, image arguments and reports are retained.
- **Temporal defect:** both live critics catch the paper detachment at frames 91–93. Before/contact/after images remain valid; native pixel comparisons confirm the difference is concentrated in the three intervening frames. The simple temporal control passes physicality/energy but fails art/composition; those failures remain blocking and visible.
- **Minimal/quiet control:** all ten owned gates pass across the two independent critics with nullable optional energy and zero environment cues. Its unchanged matched variant fails energy and story. Both mixed fixture sets remain `REPLAN_REQUIRED`, with publishing disabled.
- UI canonical hand error is under **0.005 native pixels** under focused/burdened acting and local reactions. Calm-paper hand error is under **0.032 authoring pixels**. Bot-absent UI contains no character geometry/contact. Workshop compiled events and native delivery stills show the same held/assembled constituents under the common response.
- Native fixture MP4s are 360 × 640, 30 fps, 120 frames/4 seconds each, captioned and caption-free. HyperFrames checks pass; the short frame fixtures retain two Studio ID warnings, with zero errors and all contrast checks passing. Workshop check has zero warnings/errors.
- **540 frozen v6/canonical files verify unchanged.** Git changes contain no accepted-production edits.

See [recorded results](../quality/validation/v1.1/results.json), [regression log](../quality/validation/v1.1/regression-tests.txt), and [evidence guide](../quality/validation/v1.1/README.md).

## Preserved gates and stop

Ten independent gates, separate critics, per-shot coverage, stale evidence hashing, gold retrieval, GENERATED → REVIEW → CANONICAL with human promotion approval, two repair passes, separate technical checks, no automatic publishing and final human playback/listening approval remain intact. Fixture artwork is production-specific validation material and is not promoted into the canonical library.

Stop for v1.1 review. The original script-to-film run remains a separate task after approval.
