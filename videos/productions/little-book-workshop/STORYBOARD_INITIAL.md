# Production storyboard from validated plan

Message: A project can be divided into independent jobs, worked on at the same time, and brought together as one finished deliverable.

Narration: The project splits, sending three jobs to three Bots. They work in parallel, folding, pressing, and carrying each piece toward shared assembly. The pieces assemble, and three grips press one finished book together. They deliver forward; waiting hands take the finished book's full weight.

Environment: workshop

Ending: Receiving hands take the finished book's weight, and the same book withdraws with them during a brief final hold.

## dispatch-jobs

- subject: One project folio and three Bots
- action: The folio unfolds and distributes its cover, pages, and binding into three separate Bot grips.
- before_after: One intact folio becomes three traceable job pieces held by three workers.
- focal_detail: The divided project seal remains visible across the separated components.
- focus_target: workshop.project
- framing: subject
- consequence: Each Bot receives a distinct job piece.
- shot: workshop-wide
- narration: The project splits, sending three jobs to three Bots.
- caption: Dividing the project
- headline_mode: clear
- headline: 
- Executable actions: [{"kind": "workshop.dispatch", "subject": "project", "cue": "splits", "result": "none", "requires": []}]

## parallel-work

- subject: Cover, pages, and binding jobs
- action: All three Bots work simultaneously: folding the cover, pressing the pages, and carrying the binding toward assembly.
- before_after: A flat cover, uneven pages, and curled binding become a creased cover, aligned stack, and positioned binding.
- focal_detail: All three overlapping operations and their persistent component colors remain visible together.
- focus_target: workshop.jobs
- framing: establish
- consequence: The three worked pieces reach the shared assembly area.
- shot: workshop-wide
- narration: They work in parallel, folding, pressing, and carrying each piece toward shared assembly.
- caption: Working at the same time
- headline_mode: clear
- headline: 
- Executable actions: [{"kind": "workshop.work_parallel", "subject": "project", "cue": "work in parallel", "result": "none", "requires": ["jobs-distributed"]}]

## assemble-book

- subject: Three completed components
- action: The cover, pages, and binding slide together before all three Bot grips complete one firm press.
- before_after: Three separate worked pieces become one closed, bound book with a complete project seal.
- focal_detail: The same components visibly align inside the assembly cradle.
- focus_target: workshop.assembly
- framing: detail
- consequence: The distributed work becomes one finished deliverable.
- shot: workshop-wide
- narration: The pieces assemble, and three grips press one finished book together.
- caption: Bringing the pieces together
- headline_mode: clear
- headline: 
- Executable actions: [{"kind": "workshop.assemble", "subject": "project", "cue": "assemble", "result": "none", "requires": ["jobs-worked"]}]

## deliver-book

- subject: The finished book and receiving hands
- action: The center Bot extends the assembled book; receiving hands take its weight before the Bot releases it.
- before_after: The finished book moves from the workshop into separate waiting hands without changing identity.
- focal_detail: The complete cover seal, source grip, and receiving contact remain unobstructed.
- focus_target: workshop.delivery
- framing: subject
- consequence: One finished result reaches its recipient.
- shot: workshop-wide
- narration: They deliver forward; waiting hands take the finished book's full weight.
- caption: Delivering one result
- headline_mode: clear
- headline: 
- Executable actions: [{"kind": "workshop.deliver", "subject": "project", "cue": "deliver", "result": "none", "requires": ["book-assembled"]}]
