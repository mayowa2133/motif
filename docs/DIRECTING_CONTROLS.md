# Executable directing controls

New live-planned productions use schema **1.1**. Historical 1.0 plans and exports remain unchanged; they are evidence of the earlier implementation, not inputs to silently migrate or rerender.

## Operative fields

Every beat supplies:

```json
{
  "shot": "arena-a",
  "focus_target": "answer-A.connection",
  "framing": "detail",
  "focal_detail": "The missing connection explains why this answer fails.",
  "headline_mode": "clear",
  "headline": ""
}
```

`shot` chooses an existing scene container. `focus_target` chooses registered geometry inside it. `framing` changes its geometry-derived camera fit. `focal_detail` remains explanatory prose; arbitrary wording does not control pixels. No model selectors, coordinates, expressions, or executable animation code are accepted.

| Focus target | Available containers | Protected evidence |
|---|---|---|
| `calendar.board` | Both calendar shots | Whole calendar |
| `calendar.proposal` | Both calendar shots | Proposal including entrance |
| `calendar.booking` | Both calendar shots | Solid booked card |
| `calendar.decision` | Both calendar shots | Control, contacting finger, proposal/removal |
| `arena.answers` | `arena-pair` | Both answer sheets |
| `answer-A.sheet`, `answer-B.sheet` | Pair, matching candidate close, review | Selected sheet and its attached stamp |
| `answer-A.connection`, `answer-B.connection` | Matching candidate close | Actual route/gap, candidate letter, test window and result mark |
| `arena.handoff` | `arena-review` | Both sheets at source/destination, receiving hand, rotation margin |

`establish` fits the scene region; `subject` fits the target with generous context; `detail` fits it more closely. Scale/translation are computed from registered bounds, never from generated coordinates. Stored SVG viewBoxes supply asset envelopes. Shared placement constants drive both the scene builder and the bounds registry. Diagnostic/contact bounds are authored for the finite existing choreography; this is not arbitrary SVG geometry discovery or automatic semantic tracking.

The action safe region is x=90–990, y=260–1550 in a 1080×1920 frame. Its camera fit protects critical action/identity bounds and clamps scale; a clip keeps paper crops away from headline/caption cards. Motion can enter from outside the frame. Decorative sheet edges and peripheral stencil edges may crop; diagnostic connections, identity and marks must remain visible. A reframing cut replaces a tween if an early speech cue would otherwise start the action during the pan. Arena Bot stays complete in an authored supporting foreground slot outside the work-prop camera.

Checks require matching A/B connection targets and detail framing. Their shared local geometry gives identical transforms and diagnostic sizes. Selection stamps attach to the selected sheet in each existing representation. Subsequent framing must include that selected sheet and keep its stamp label at least 34 delivery pixels; otherwise validation fails. Handoff focus includes both source and destination bounds.

## Headline lifecycle

- **set:** requires nonempty text; clears the prior headline at beat start, reveals the new headline after that beat's completed physical evidence.
- **clear:** requires empty text; clears the prior headline at beat start.
- **keep:** requires empty text and an existing headline; allowed only in holds with no meaningful state action.

Empty text has no implicit lifecycle meaning. This prevents the previous PROPOSED-after-decline persistence. It does not automatically establish the semantic truth of arbitrary text; the model data review and actual-frame review remain separate responsibilities.

## Audience narration

The planner writes ideas, choices and consequences for the audience. Choreography belongs in structured visual fields. Natural narration phrases provide measured speech anchors without requiring viewers to hear descriptions of dashed graphics, stencil geometry or cross rendering.

Validation rejects a narrow list of known stage-direction phrases when the brief is not about those objects. The live reviewer separately evaluates `audience_narration`, semantic fidelity and explicit label lifecycle. It reviews plans and timing/bounds records, **not rendered frames**; it is not a guarantee of natural speech or painted readability.

## Verification provenance

1. `deterministic-review-*.json`, `planning-review.json` and `pre-render-checks.json`: state/order, model data review, sorted events and caption starts checked against measured speech anchors.
2. `verification.json` → `encoded_measurements`: measured loudness, true peak, duration and first/final encoded video-stream equality. Pre-render checks are referenced separately by path/hash, not asserted as new post-encode visual measurements.
3. Independent sampled-frame inspection and human playback/listening review: separate records. Unperformed subjective/human review remains explicitly unassessed.

Initial model output and each compiled planning attempt are preserved. One bounded automated correction is permitted for concrete issues. `first.mp4` is retained before encoded audio finishing. Invocation records now include measured wall-clock boundaries; a server-resolved model ID still remains unavailable when the CLI does not expose it.

## Limits

Two worlds, six containers, finite focus targets and predefined action choreography remain. The model chooses among these controls and writes narration; it does not generate unrestricted layouts, new assets, arbitrary camera paths, multiworld stories or actual answer-quality analysis. The arena's connection check is an illustrative metaphor.

New projects use HyperFrames 0.8.98, after an upgraded fixture passed its full check. Frozen projects retain their pins and artifacts. Differential evidence and the fresh supported Reel are indexed in [DIRECTING_CONTROLS_REVIEW.md](DIRECTING_CONTROLS_REVIEW.md).
