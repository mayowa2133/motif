# Bounded waiting fixture and custom-authoring records

`waiting-1.0` is optional, technical-fixture-only and limited to one illustrative
request → stop → pending → response → resume → retained-result family. It uses
native front-facing placeholder shapes. It cannot enter original-film mode or
the canonical asset catalog; approved mascot identity is still a dependency.
Production defaults and the existing PR #8 adoption gate remain unchanged.

Run a fresh silent fixture with existing test/runtime dependencies:

```sh
python scripts/motif_waiting.py --scene quality/causal-pilot/waiting-scene.json \
  --project /tmp/my-fresh-waiting-fixture --encode
```

No new dependency is declared. The optional encode uses existing CairoSVG,
FontTools/Brotli and FFmpeg; data-only compilation needs FontTools only when text
is declared. No model/API call, new provider or implicit narration occurs.

For text/audio projects, prepare a fresh project and copy **only explicitly
declared resources** under its relative paths, save `brief.json` and the exact
`production-plan.json`, declare `technical-fixture`, then call
`motif_waiting.encode(project, saved_scene, captions=True)`. The silent JSON-only
CLI does not discover/copy resources. Captions require font and license hashes,
matching font weight, exact lines, size, position, native bounds and manual frame
locks. `simple-ltr-unshaped-v1` preserves admitted Unicode glyphs but supplies no
kerning/shaping, bidi, translation, segmentation or speech-pronunciation proof.
Combining/RTL text and measured speech timing fail explicitly. There is no font
fallback. Optional saved 16-bit PCM WAV must contain exactly `frames × 1600`
samples at 48kHz, mono/stereo. Listening remains unassessed.

Actor/object rectangles use top-left coordinates; the moving input's position
is its center. Six unique roles and layer numbers are required. Generated hand
and progress IDs must also be unique. Actual painted eyes, arms, hands, progress
and moving input extrema must fit 360×640. Event frames are ordered integers;
the causal map must match request/stop and the retained final frame. Pure frame
state supports repeated/reverse seeks. Contact math does not certify readable
contact. Result and progress are distinct native elements.

Compilation writes a narrow composition manifest, state trace, execution
bindings, causal/critical evidence routes and relative hashed resource inventory.
Capture freezes these saved input/config identities before painting and binds the
actual output. Existing outputs fail rather than being overwritten. Source edits
require a fresh output/project; prior captures and findings remain recoverable.

`motif_custom_authoring.resolve_requirement` records an **explicit operator
binding** to the registered capability or a scoped custom task. Unsupported film
requirements cannot silently select this placeholder. `start_task` freezes named
inputs/expected outputs; `checkpoint` validates unchanged inputs, monotonic
PLAN/BUILD/READY_FOR_SHARED_QA stages, actual output hashes and operator-recorded
active/elapsed seconds/reasons. Effort values may be explicitly null/UNAVAILABLE
when uninstrumented; they never
support an efficiency result. It executes no arbitrary code. Ready-for-QA is
neither fulfillment, editable-source verification nor film approval. The existing
quality sampler and admission gates evaluate the actual artifact; task records
cannot bypass them. No generic timeline editor or universal compiler is claimed.

`sample_task(project, captions_movie, captionless_movie, shots)` connects the
READY task to the existing rough-evidence sampler. Capture must already bind
both distinct, project-local movies to the current inputs. The receipt locks the
requested mode, current task/checkpoint, authored outputs, capture, evidence and
all generated sample files. `require_sampled_task(project)` rejects changed or
missing inputs, outputs, runtime code, movies, sheets or traces. Recapture and
resample after edits. Its status is `SAMPLED_REVIEW_REQUIRED`; it never grants
structure, direction, painted, final or human approval and never executes the
authored source. A film requirement must use actual film authoring and its gates.

## Optional semantic repair and approved flat binding

`response_cue={"shape":"check-packet","color":"#488553"}` adds a distinct
response color and native check only during response frames. Its authoring floor
keeps the check inside the packet; it does not certify phone perception. Leaving
the field absent preserves the preceding SVG/state output. No gain is accepted
until fresh encoded review. Optional `state_label` values pending/response/complete
bind the limited phrases `Await input`, `Response in transit`, `Complete` to their
declared state intervals. `Response received` is rejected during transit: a
numeric response state cannot establish receipt while the pictured packet is
travelling. This also rejects the failed pending `Input ready` package;
unbound arbitrary text still needs semantic review.

An optional integer `arrival` between response and resume separates transport
from receipt. The response reaches its fixed work-side target at arrival and
remains there through the final frame. Transit text ends at arrival-1. A received
label requires the explicit event and begins after arrival, while reaction/work
resumption must occur later. Request/resumed labels bind `Request submitted` and
`Work resumes` to their event intervals. These data guards need encoded boundary
review; they do not certify human comprehension. Omitting arrival preserves the
preceding frame state and artwork.

`--delivery` directly rasterizes the same saved vectors at 1080×1920 before encode;
it does not upscale an earlier video. Its config records delivery dimensions.
Native captions-off and delivery captions-on are distinct evidence outputs.
The reviewed retained-packet fixture masks part of the resumed grip. Perceived
contact remains unassessed; this path cannot claim a fully visible hand/work grip
or a creative gain. Preserve the packetless prior artifact as the visibility
comparator and route requirements for visible grip to further native authoring.

Optional `receipt_dock={"clear_frame":198,"offset":[0,-48]}` keeps the input
unchanged through its explicit arrival, then moves the received packet linearly
to a retained parking position before resume. Require
`arrival < clear_frame < resume`, finite coordinates, painted bounds and enough
separation from the resumed hand. Omitting it preserves prior SVG/state output.
This is a bounded visibility repair: its numeric clearance cannot certify other
occlusion, handling, full-speed contact or artistic gain. Actual encoded review
of the tested dock sees the resumed endpoint clearly, with a transient neutral
tab overlap during parking still recorded as a limitation.

An optional `mascot_contract` points to a project-relative copy of the pinned
approved reusable anchor JSON, SHA-256
`e530fab90984ec06e109afe937ab478b935c62a5698ac518e93bab0ba91c87d9`.
It is the generic geometry named by `SAFE_REUSE_PATHS_V01.json`, not source shot
material. The fixture resource is in `quality/causal-pilot`. Actor dimensions
must preserve its 240:251 overall aspect and fixed orange. The native binding
keeps its shell/four integral feet, eyes and tabs and adds an authored flat target
connector. Older grain, rim/depth, shadow and perspective fields are omitted in
accordance with the user's latest flat front-facing direction. Declared malformed
resources fail; they cannot select placeholders. Contact math and unique IDs are
checked; painted identity, contact and semantic benefit remain unassessed until
the allocated encode/review. Film-mode rejection is retained even with this
binding. No canonical asset promotion occurs.

The 2026-10-09 isolated pilot decoded all 240 frames of five variants. Preview and
export rebuilt from the same synthetic tone had identical decoded audio/picture
hashes on one runtime. Actual caption/recolor/retime source edits reached their
encodes; two-location glyph/event rebuilds matched. These findings establish
bounded technical behavior, not cross-platform or artistic reliability.

Independent still review preserves response ambiguity and a semantic caption
failure: `Input ready` appears while work is pending. That edit is rejected for
creative use, with `Await input` its rollback target. Fault controls
`no-stimulus`/`continues-pending` are deliberately bad diagnostic fixtures, not
unchanged-main baselines. The new family has no admitted main-method film baseline.
No creative candidate is eligible. Human playback/listening, four unfamiliar
matched script pairs, approved mascot style, source reconstruction and a second
supported environment remain pending. Review subsets never establish absence of
errors in unreviewed frames. See the backlog and pilot results for exact scope.

Rollback is the preceding compiler/scene input commit/hash; optional dispatch is
removed independently of existing film compilers. Preserve negative research.
Use `motif_experiment_gate` for any later combined-method trial/promotion, after
same-brief evidence and its six guardrails are present. Never promote this fixture
as artwork or infer normal-speed AV quality from its stills or synthetic mix.
