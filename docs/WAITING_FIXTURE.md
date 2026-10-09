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
active/elapsed seconds/reasons. It executes no arbitrary code. Ready-for-QA is
neither fulfillment, editable-source verification nor film approval. The existing
quality sampler and admission gates evaluate the actual artifact; task records
cannot bypass them. No generic timeline editor or universal compiler is claimed.

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
