# Production storyboard from validated plan

Message: Two candidate answers undergo the same check. Both fail. Instead of selecting a winner, the assistant sends the answers to a person for review.

Narration: Here are answers A and B. Checking A reveals a route gap before its cross appears. Checking B with the same stencil reveals its gap before the cross. Both answers failed the same check. No winner; both go to a person for review.

Environment: arena

Ending: Both failed answer sheets finish moving into a separate person's receiving hand and remain there for review, with no winner shown.

## beat-1

- subject: Answers A and B
- action: The bot presents two already aligned, untested answer sheets.
- before_after: Before: the bot is neutral beside the aligned sheets. After: the bot presents A and B as the candidates.
- focal_detail: Two untested answer sheets shown side by side with identical geometry.
- consequence: Both candidates are introduced without claiming the check has occurred.
- shot: arena-pair
- narration: Here are answers A and B.
- caption: Meet A and B
- headline: Two answers
- Executable actions: [{"kind": "bot.pose", "subject": "bot", "cue": "Here are", "result": "presenting", "requires": []}]

## beat-2

- subject: Answer A
- action: The stencil lands on A, exposes a missing route connection, and registers a cross.
- before_after: Before: A is untested. After: A shows a visible route gap and fail cross.
- focal_detail: A's broken route beneath the tactile stencil.
- consequence: Answer A fails the check.
- shot: arena-a
- narration: Checking A reveals a route gap before its cross appears.
- caption: Checking answer A
- headline: 
- Executable actions: [{"kind": "arena.check", "subject": "A", "cue": "Checking A", "result": "fail", "requires": []}]

## beat-3

- subject: Answer B
- action: The identical stencil lands on B with matching geometry, exposes its route gap, and registers a cross.
- before_after: Before: B is untested while A is failed. After: B also shows a visible route gap and fail cross.
- focal_detail: The same stencil and framing used for A exposing B's broken route.
- consequence: Both candidates have now undergone the same physical check.
- shot: arena-b
- narration: Checking B with the same stencil reveals its gap before the cross.
- caption: Checking answer B
- headline: Same check
- Executable actions: [{"kind": "arena.check", "subject": "B", "cue": "Checking B", "result": "fail", "requires": []}]

## beat-4

- subject: Both failed answers
- action: Both crossed sheets remain side by side for a clear result hold.
- before_after: Before: B's check has just completed. After: both route gaps and both crosses remain plainly visible.
- focal_detail: Matching failed sheets with no winner marker anywhere in frame.
- consequence: The shared outcome is established before review begins.
- shot: arena-pair
- narration: Both answers failed the same check.
- caption: Both answers failed
- headline: Both failed
- Executable actions: []

## beat-5

- subject: Both failed answers
- action: Both marked sheets travel together into a separate person's receiving hand and remain there.
- before_after: Before: both failed sheets rest in the arena with no winner. After: a person holds both for review, still with no winner.
- focal_detail: The receiving human hand holding both crossed answer sheets.
- consequence: Human review begins without automatic selection.
- shot: arena-review
- narration: No winner; both go to a person for review.
- caption: To a person
- headline: Human review
- Executable actions: [{"kind": "arena.handoff", "subject": "both", "cue": "both go", "result": "none", "requires": ["A-tested", "B-tested"]}]
