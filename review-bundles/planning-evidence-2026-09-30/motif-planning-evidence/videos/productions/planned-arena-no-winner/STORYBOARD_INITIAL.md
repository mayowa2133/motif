# Production storyboard from validated plan

Message: Two candidate answers undergo the same check. Both fail. Instead of selecting a winner, the assistant sends the answers to a person for review.

Narration: Two answers face the same route check. Testing answer A, the stencil exposes a missing connection before its cross appears. Testing answer B exposes another missing connection before its cross appears. With both tested, the assistant sends them into a person’s hand for review.

Environment: arena

Ending: Both failed answer sheets finish moving into a separate person's hand and remain there for review, with no winner shown.

## beat-1

- subject: Both candidate answers
- action: The two answer sheets arrive side by side while the bot presents the shared test.
- before_after: Before: no candidates are visible. After: A and B are aligned together, both untested.
- focal_detail: Matching answer sheets positioned under one stencil-check setup.
- consequence: The comparison begins under equal conditions.
- shot: arena-pair
- narration: Two answers face the same route check.
- caption: One shared check
- headline: Same test
- Executable actions: [{"kind": "bot.pose", "subject": "bot", "cue": "face", "result": "presenting", "requires": []}]

## beat-2

- subject: Answer A
- action: The stencil lands on A, exposes a missing connection, and a cross registers.
- before_after: Before: A is untested. After: A shows a visible route gap and fail cross.
- focal_detail: The broken route beneath the identical stencil.
- consequence: Answer A fails the check.
- shot: arena-a
- narration: Testing answer A, the stencil exposes a missing connection before its cross appears.
- caption: Testing answer A
- headline: 
- Executable actions: [{"kind": "arena.check", "subject": "A", "cue": "Testing answer A", "result": "fail", "requires": []}]

## beat-3

- subject: Answer B
- action: The same stencil lands on B, exposes its missing connection, and a cross registers.
- before_after: Before: B is untested while A is already failed. After: B also shows a route gap and fail cross.
- focal_detail: B's broken route shown with the same stencil geometry used for A.
- consequence: Answer B fails; both candidates are tested and failed.
- shot: arena-b
- narration: Testing answer B exposes another missing connection before its cross appears.
- caption: Testing answer B
- headline: A failed
- Executable actions: [{"kind": "arena.check", "subject": "B", "cue": "Testing answer B", "result": "fail", "requires": []}]

## beat-4

- subject: Both failed answers
- action: Both marked sheets travel together into a separate person's receiving hand and remain there.
- before_after: Before: both failed sheets rest in the arena. After: a person holds both for review, and no winner appears.
- focal_detail: The receiving human hand holding both crossed answer sheets.
- consequence: Human review begins without an automatic selection.
- shot: arena-review
- narration: With both tested, the assistant sends them into a person’s hand for review.
- caption: To a person
- headline: No winner
- Executable actions: [{"kind": "arena.handoff", "subject": "both", "cue": "sends them", "result": "none", "requires": ["A-tested", "B-tested"]}]
