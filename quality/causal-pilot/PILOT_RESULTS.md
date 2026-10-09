# Waiting technical pilot — exact-scope results

Baseline code: merged PR #9, `a75893ce0b06121afe5871a38f3f4f3e3c6942e3`. Capture inputs were frozen before local synthetic rendering. Capture is released for Main Cycle 7. Current checkout/production defaults were preserved.

This is one bounded technical-fixture family with placeholder front-facing actors, not an admitted main-method film A/B or approved mascot artwork. Existing approved mascot resources are available in the named safe-reuse manifest; their action-specific flat binding was not used here. Fault controls are deliberately broken fixtures.

## Encoded evidence

| Artifact | MP4 SHA-256 | Actual decode |
| --- | --- | --- |
| candidate-v2 | `2b6a8c05844fdef30d04ce79bad38895c6ed7693b88755a942697f8eb8bcf4e2` | 240 frames, 30fps, 360×640, 8s |
| control-no-stimulus | `57f9d17c0a8e29ffdb08029a2fecccaa87be322f0b7b7ebc1a752a4afa979dac` | 240 frames, 30fps, 360×640, 8s |
| control-continues-pending | `830815cbcf5840bb3b6227def41b64e711dd2c00d51fe91b79044ef3f53d014b` | 240 frames, 30fps, 360×640, 8s |
| caption-audio | `382b6375e62cc872de73e4302ecdb58f9283c222c0df3d67b92036b03b1189fb` | 240 frames, 30fps, 360×640, 8s |
| edited-caption-recolor-retime | `0033645aac941774a0d5855d04e47cb045d5d7495c59f54978415534041f1fca` | 240 frames, 30fps, 360×640, 8s |

Each of five variants has a saved shared-quality-sampler manifest covering all 240 decoded frames. Reviewers inspected subsets; decode completeness never supplies unobserved semantic absence claims. Six MP4 outputs include a second same-input preview encode. Native source edits (caption wording, worker recolor, event retiming) reached actual encoded evidence.

## Saved-media and rebuild findings

On this local runtime, preview/export decoded RGB24 SHA-256 is `47d8ea4d8cd5e956d9fa2afe0ef4b897fe71fe183e907d3715ab75f8439e9675` and decoded PCM16 SHA-256 is `c326dfd5c1c33d495c6a85ed809ccdd3dc3fd190b7c477bf43f25af653e62e50`. Both arms match exactly: 165888000 RGB bytes and 768000 audio bytes (384000 mono samples). Input is an eight-second synthetic tone, not spoken narration. This establishes same-input local parity; listening, AV quality and cross-platform parity remain UNASSESSED.

Two filesystem locations rebuilt equal native SVG glyph markup and event bytes using explicit licensed Inter700 resources. Same machine/runtime only. No hidden resource or OS-font fallback; missing/changed/escaping resources fail. A second supported environment has not been demonstrated.

## Independent still findings and gate outcome

Reviewer one inspected 27 hash-recorded PNGs across candidate/caption/edit variants. Reviewer two inspected 40 labelled candidate frames across nine hash-recorded PNGs. Both preserve an inconclusive response/ownership finding: the same yellow cue jumps back to the requester at the response boundary and can read as reset or repeated delivery. Reviewer two also finds endpoint/bar overlap and unclear pending ownership.

Reviewer one identifies a scoped negative caption edit: `Input ready` appears while work is pending, whereas prior caption `Await input` is consistent. This edit is rejected for creative use and its rollback plan/artifact hashes are saved. The visible editing capability is retained; this is not a general method harm or matched-main negative claim.

The unchanged PR #8 gate was executed against a separate local pilot registry. Both proposals return `no_ready_addition`, with empty enabled lists. Missing main-film baseline, inconclusive causality, negative caption semantics and absent eligible scope block promotion. No artistic gains, aggregate aesthetic score, human comprehension, playback/listening or full-speed AV result is claimed.

## Verification and limitations

Independent code reviewer reproduced input/geometry/resource/text/audio/task edge failures, then cleared the final guarded snapshot with 76 independently run tests. Author ran 115 applicable Python tests and six Node tests, all passed; `git diff --check` passed. No new project dependency. Reviewed code includes stricter validation fixes made after capture; those fixes do not paint new frames. Exact captured compiler hashes remain in frozen criteria/render configs; artifact conclusions apply to those identities.

The nine backlog packages have implemented technical increments, not completed artistic validation. Approved-resource binding/semantic repair, actual human review, four fresh matched scripts, adequate existing authorized reconstruction intake and a second environment remain to execute. Independent review availability is not a fabricated approval prerequisite.

## Local receipts (media and archives stay out of Git)

| Receipt | SHA-256 |
| --- | --- |
| `frozen-criteria-v2.json` | `8788941adfc40280569de6e1a9d7f3c8a8615364b86b62a23bf70764a6dd5ea7` |
| `technical-results.json` | `4c10c20e76b7da09a01993d406d29add546e5aeb85d87a812238ff0ba7035599` |
| `review-independent-visual1/review.json` | `ac83d8a808dcc97d27d7c8b0ea88573a989f4fca2a8ae5582f030c08e6d2f422` |
| `review-independent-visual2/REVIEW.json` | `7f20b818ea7997d6920f4632ad2d777648e405a436f280c4a0fe1fe4b0d248e5` |
| `candidate-registry.json` | `f0d977b886247b2e1c03ec834814321957d17bb1bc9cc0d2537acc302cf8acda` |
| `gate-decisions.json` | `a672d8368412070dca91cc0ee02f15ad1970656688ed41b4009eb7918d6c7299` |
| `caption-rollback.json` | `f45f0886ee59804d08801829ecc8e041ea486d35a9f39736697a2d0cbdf4f69e` |

All receipts are under `research/experiments/causal-meaning-pilot-20261009` in the shared workspace. Only this concise report enters Git. No current/sealed/held-out source visuals, reference media or production archives were copied.
