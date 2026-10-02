# Motif Quality System v1

**Status: implementation ready for review; no new film.** VoiceStudio v6 is frozen and accepted as the visual benchmark. This does not establish autonomous original-film quality or verify its narrated product claims.

## Production path

New `motif_direct.py run` and `script-plan` calls request `quality_mode: motif-gold-v1` and retrieve three relevant internal examples. Existing saved plans without that field retain their original behavior and explicit style choice.

1. Validate the existing plan schema and per-shot contract. Record reuse, production-specific artwork, reusable candidates and explicitly promoted assets in `asset_usage`.
2. Run the separate **pre-animation direction/art review**. This is a data review; it cannot approve painted quality.
3. Compile rough geometry with actual performance, contacts, camera and captions. New artwork/choreography is allowed as identified agent-assisted development.
4. Render **native 360 × 640 moving previews**, with and without captions. New runs stop here, after the two critic calls.
5. Pass every required story and visual gate before final artwork. A story/staging failure requires replanning. Art/motion failures require a focused repair.
6. Review the final moving picture through the same two critics, then clear the separate picture technical checks before audio finishing.
7. Measure the finished audio and clear all technical checks. **Human viewing and listening approval remains required.** There is no automatic acceptance or publishing command.

[QUALITY_CONTRACT.md](QUALITY_CONTRACT.md) defines ten independent gates. [ENERGY_CONTRACT.md](ENERGY_CONTRACT.md) overrides fully-settle-then-wait only in this explicit mode. No averages, particle quotas or global jitter.

## Executable bindings and limitations

| Shot field | Consumer |
|---|---|
| purpose, hero, primary_action, before, after | Pre-animation direction critic; painted story critic compares intended change to actual frames. Existing `actions` still choose the executable dominant action. |
| focal_target, framing | Must agree with existing operative fields when present; static calendar/arena camera compiler executes them. Frame recipes retain their own staging, assessed by critics. |
| performance.state/target | Named canonical puppet binding in calendar/arena and the high-energy paper renderer. |
| reaction_radius | Selected targets only; bounded amplitude, relevance/distance falloff, delay and duration. A separate local transform composes with main action; paper grips resolve after both. |
| secondary_motion, environment, exit_overlap, energy | Mandatory direction-review inputs; story/visual critics inspect their visible execution. They are intentions, not a fabricated event count. |
| art_direction | Mandatory hero, Bot role, two–three environment cues, materials, depth, composition and intentional irregularity; direction then visual critic. |

The performance registry contains thirteen states. Geometry comes from the locked canonical puppet. Static targets are registered in `motif_quality.apply_bindings`; attached finger targets are rejected. High-energy paper targets are `bot` and the actual persistent prop names rendered by the finite action. Its inverse grip hook preserves contacts after performance and reaction transforms. The calmer paper and text-directed UI adapters explicitly stop for an anchor-aware quality hook; they do not ignore requested acting. This is a bounded capability extension, not arbitrary original scene generation.

## Painted review and retrieval

Twelve [gold examples](quality/gold/index.json) contain native representative PNGs, tags, short notes and hash-bound frame ranges into the existing v6 mobile MP4. No external creator video is needed. Retrieval returns 2–4 examples by behavioral tags, never all examples or pixel matching.

`codex exec` currently accepts images, not native MP4 input. Each critic receives ordered decoded native frames from **both moving previews**, individual native before/middle/after frames, declared contact frames, full-rate painted motion observations sampled into the prompt, and ordered frames from three gold ranges. The story and visual critics are **two separate live model invocations**; saved responses are not substituted. They must disclose sampling limits and use NOT_ASSESSED when frames cannot establish a gate. This is not full playback or listening review.

Each critic must assess every shot against its gates. Every violation specifies shot/time, gate, observed problem, retrieved gold and smallest correction. Reports, invocation records, image inputs, media, plans/events and render sources are hashed. Changed evidence invalidates advancement. Critical failure or incomplete coverage blocks; Bot performance alone may be inapplicable when Bot is explicitly absent. Two meaningful repair passes maximum, then unresolved failures require human review. Backend retries are not creative repairs.

## Commands

Use the existing authenticated backend. `MOTIF_PLANNER_MODEL` is an explicit existing override; there is no fallback, provider or credential change.

```sh
python3 scripts/motif_quality.py retrieve --tags burden ui-contact
python3 scripts/motif_quality.py direction --project /absolute/new-project
python3 scripts/motif_quality.py rough --project /absolute/new-project
python3 scripts/motif_quality.py sample --project /absolute/new-project --phase rough \
  --with-captions /absolute/new-project/quality-review/rough/captions.mp4 \
  --without-captions /absolute/new-project/quality-review/rough/no-captions.mp4 \
  --shots /absolute/new-project/shot-ranges.json
python3 scripts/motif_quality.py critique --project /absolute/new-project --phase rough
python3 scripts/motif_quality.py gate --project /absolute/new-project --phase rough
```

Repeat `sample`/`critique` with `--phase final --delivery-picture /absolute/delivery.mp4` for final moving QA. The matching delivery picture is hash-bound to the native review before audio finishing. After changing plan/events, `repair --note "specific correction"` counts the pass and archives prior evidence. A plan change requires direction review again. The final gate retains the approved rough story while allowing finished art to change its event data; final evidence must match the current sources.

## Assets and technical evidence

[Asset gate](quality/asset-quality-gate/README.md): GENERATED → REVIEW → CANONICAL. Promotion needs current metadata, ten separate passing checks and explicit human asset approval. A one-off remains scene-specific; generation never promotes it.

`technical --with-captions /absolute/final-native.mp4 --checks /absolute/supplemental-checks.json` measures encoded count/fps/dimensions/duration and loudness/true peak. Existing technical reports supply hash-bound evidence for assets, clipping, contrast, caption overflow, safe areas, runtime, TTS alignment, anchors, unresolved artifacts, provenance/licensing and reproducibility. New production-specific/candidate artwork also needs complete metadata and a current asset review before final advancement. Missing evidence is NOT_ASSESSED and blocks. PICTURE_PASS_AUDIO_PENDING permits audio finishing; only PASS clears all technical checks. Technical results never imply creative, factual or listening approval.

## Validation

[Validation record](quality/validation/README.md) describes copied short fixtures and the live critic results. Focused tests cover actual event/frame changes, contacts, bounded reactions, metadata/promotion, evidence staleness, independent hard gates and repair limits. Legacy directing and paper-energy checks protect opt-in compatibility. The freeze manifest verifies v6 and canonical Bot bytes; no accepted project was edited. No v7, prop library, provider change, dependency upgrade, commit or push was performed.
