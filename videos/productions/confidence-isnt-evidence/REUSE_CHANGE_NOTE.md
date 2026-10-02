# Confidence Isn’t Evidence — moving-preview handoff

**REVIEW_REQUIRED.** One original script-led production, not another reconstruction. Final material treatment and final sound design are paused for story/staging approval.

## Creative decisions and actual workflow

The supplied script is unchanged. The existing authenticated, data-only Codex CLI (`gpt-5.6-sol`, recorded in `backend.json` and `initial-plan-invocation.json`) chose the paper-investigation idea, six beats, spoken action cues, focal details, headlines, and ending. `STORYBOARD_INITIAL.md` and `initial-plan.json` preserve that first proposal; `production-plan.json` retains the same creative plan.

The idea makes the answer’s support inspectable: a confident paper structure buckles; Bot follows its attached source; a summary saying **WILL** lifts to reveal **MAY / in some cases**; a loose scrap is moved away from missing support; a **NEEDS REVIEW** bookmark is placed beside it; the layers are arranged so the gap remains visible. Every document is explicitly **SAMPLE**. Finding a source does not close the evidence gap or establish correctness.

Execution uses the shared `motif_direct.py` entry point, `motif_plan.review_plan`, `motif_plan_compile.compile_plan`, existing lexical speech alignment, and unchanged Motif `SET`/`TWEEN`/`CAPTION_REPLACE` engine with pinned HyperFrames 0.8.99. No runtime model code executes. The script schema and small script adapter are additions to this shared path; the message-driven calendar/arena/workshop branches remain intact.

## Reuse and necessary additions

- Reused: canonical Bot generator and its existing arm/hand controls, scene-01 desk, project-folio cover component, existing quiet wall material, existing paper definitions, GSAP/event runtime, local Kokoro `af_nova`, local Inter/EB Garamond rendering fonts, and existing review loudness/peak constants.
- `reference-expressive-v1` is explicitly registered as an opt-in production presentation in `assets/styles/`. The reconstruction’s original preset and default style bible are unchanged.
- Seven new independent SVG props with metadata: answer card, source leaf, summary flap, connector strip, empty evidence frame, blank scrap, decision bookmark. They are available under `assets/scenes/paper-investigation/`, with saved production copies under `assets/props/`.
- Six finite paper interactions were **agent-authored**, then exposed to the shared script producer in `motif_paper_investigation.py`. The live model requested the interaction concepts; it did not generate executable geometry or motion code. Canonical grips and carried objects use matched finite poses at 30 fps.
- `execution-bindings.json` records each requested focal detail’s actual geometry binding and camera fit. Framing is executed, not inferred from caption text. Missing actions/assets are explicit capability errors.
- The initial model’s “glossy” description was implemented as matte paper to preserve the locked visual direction. No new raster generation, speculative library, provider, account, credentials, or dependency upgrade.

## Narration and timing

The first speed-1 take (17.237 s) was too brisk for the checking sequence; it remains `assets/voice/take-01-brisk.wav`. A new generated take at speed **0.75** lasts **23.616 s**, with no post-generation speech stretching. The complete preview lasts **24.333 s / 730 frames at 30 fps**, including a 0.7-second ending hold. This is **0.667 seconds below** the suggested 25–35-second range; the edit is not padded to meet it.

Installed Whisper `small.en` DTW, with flash attention disabled, measured the actual take. The existing lexical matcher finds all script words; automatic boundaries remain approximate, not phoneme-perfect. `speech-timing.json`, `alignment-review.json`, `action-trace.json`, `scene-events.json`, and provisional `caption-events.json` are the saved timing inputs.

Review audio uses the existing −16 LUFS target and −1.5 dBTP ceiling. The delivered encoded mix measures **−16.01 LUFS / −3.90 dBTP**. Its final adjustment is combined linear gain with picture streams copied unchanged; native mobile carries the same adjusted AAC. No music or SFX were added at this staging gate. Subjective narration/SFX listening approval is **not established**.

## One bounded internal correction

The first complete full and native previews remain `renders/preview-01.mp4` and `renders/mobile-01.mp4`; initial compiled layout and project data remain in `versions/initial/`.

The single correction pass:

- Kept the initial fold, supporting base, and catch in the same action envelope; matched grip points stay near the paper’s edge.
- Moved the source connector clear of MAY and separated the emerging original from the answer’s wording.
- Put the decision bookmark outside the source wording and central gap.
- Separated the closing source leaf and empty evidence frame; retained the unresolved gap.
- Corrected native sub-composition dimensions to 360 × 640.
- Set comfortable review audio levels, with preserved narration and pictures.

`preview-02.mp4` / `mobile-02.mp4` preserve the corrected render before its final review-level adjustment. `moving-preview.mp4` / `mobile.mp4` are the review deliveries. There is no second polish loop.

## What was checked, and what remains

Automated: 19 targeted shared-plan/directing/script tests passed across this run; explicit script fidelity, unsupported asset/action rejection, prerequisite order, framing effect/safety, and existing branches. Strict lint, runtime, layout and contrast checks passed for full and native compositions. **Motion assertions are disabled in the pinned CLI’s recorded checks**; these results do not automatically verify all contacts or engagement.

Visual inspection: six settled native frames plus eighteen decoded action samples, including catch, source trace, wording reveal, scrap removal, bookmark placement, and closing arrangement. Essential WILL/MAY, qualification, open tabs and review marker were inspected in delivered 360 × 640 frames; no enlarged diagnostic crop substituted for phone readability. Caption handoffs use the measured speech. Supporting SAMPLE labels and document lines remain secondary. Native 1× muted browser playback completed with captions and with the caption band hidden; this is separate from subjective listening. Not every encoded frame was visually examined.

Remaining limits: rough material surfaces and transitions; restrained character expression and some long arm reaches; small supporting document text; approximate caption timing; subjective voice quality unassessed. This is live creative planning plus agent-assisted capability development, not reliable arbitrary-script autonomous filmmaking. The new finite paper world is appropriate to this supplied message; unrelated scripts may require new explicit artwork/actions. No film composition becomes a mandatory global template.

The accepted reconstruction’s three delivery hashes were checked unchanged. No frozen production, canonical mascot source, or approved source asset was edited. No commit, push, publishing, or final production was performed.

## Reproduce this saved preview

From the repository root:

```bash
python3 scripts/motif_direct.py script-preview \
  --project videos/productions/confidence-isnt-evidence --render
```

This uses the saved plan, layout, narration and events; it does not call the planner or regenerate speech/art. A new render attempt gets a fresh numbered filename. `review-state.json` checks saved inputs and marks the gate **REVIEW_REQUIRED**. After approval, finishing must resume these creative decisions rather than silently replace them.
