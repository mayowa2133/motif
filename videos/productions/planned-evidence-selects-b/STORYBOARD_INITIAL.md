# Production storyboard from validated plan

Message: Two candidate answers receive the same check. A fails and B passes. The assistant selects B based on that evidence.

Narration: Two candidate answers face the same connection check. First, the assistant checks A; a missing link shows why it fails. Then it checks B; the complete route provides passing evidence. Based on both results, it chooses B, so the evidence drives the decision.

Environment: arena

Ending: Answer B remains visibly selected after passing the shared check.

## beat-1

- subject: both candidates
- action: Present A and B together before testing begins.
- before_after: Before: two untested answer sheets await evaluation. After: both are clearly established as candidates for the same check.
- focal_detail: Matching sheets and identical test setup emphasize equal treatment.
- focus_target: arena.answers
- framing: establish
- consequence: The viewer understands that A and B will be judged consistently.
- shot: arena-pair
- narration: Two candidate answers face the same connection check.
- caption: The same check
- headline_mode: clear
- headline: 
- Executable actions: [{"kind": "bot.pose", "subject": "bot", "cue": "face", "result": "presenting", "requires": []}]

## beat-2

- subject: A
- action: Apply the stencil to A, exposing a broken route before the failure cross registers.
- before_after: Before: A is untested. After: A shows a missing connection and a failure mark.
- focal_detail: The enlarged route gap supplies visible evidence before the cross.
- focus_target: answer-A.connection
- framing: detail
- consequence: A is tested and fails.
- shot: arena-a
- narration: First, the assistant checks A; a missing link shows why it fails.
- caption: Testing answer A
- headline_mode: set
- headline: A FAILS
- Executable actions: [{"kind": "arena.check", "subject": "A", "cue": "checks A", "result": "fail", "requires": []}]

## beat-3

- subject: B
- action: Apply the identical stencil to B, exposing a complete route before the passing check registers.
- before_after: Before: B is untested. After: B shows a complete connection and a passing mark.
- focal_detail: The same detail framing makes B's complete route directly comparable with A's gap.
- focus_target: answer-B.connection
- framing: detail
- consequence: B is tested and passes.
- shot: arena-b
- narration: Then it checks B; the complete route provides passing evidence.
- caption: Testing answer B
- headline_mode: set
- headline: B PASSES
- Executable actions: [{"kind": "arena.check", "subject": "B", "cue": "checks B", "result": "pass", "requires": []}]

## beat-4

- subject: B
- action: Select B and hold its attached SELECTED indicator beside the passing evidence.
- before_after: Before: A has failed and B has passed, with no winner selected. After: B is visibly selected while its pass mark remains present.
- focal_detail: B's sheet, pass mark, and SELECTED stamp remain large and readable.
- focus_target: answer-B.sheet
- framing: subject
- consequence: B becomes the winner because it passed the shared check.
- shot: arena-b
- narration: Based on both results, it chooses B, so the evidence drives the decision.
- caption: Choosing from evidence
- headline_mode: set
- headline: B SELECTED
- Executable actions: [{"kind": "arena.select", "subject": "B", "cue": "chooses B", "result": "none", "requires": ["B-pass"]}, {"kind": "bot.pose", "subject": "bot", "cue": "evidence drives", "result": "pointing", "requires": []}]
