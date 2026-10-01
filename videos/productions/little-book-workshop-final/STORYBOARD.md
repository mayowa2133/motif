# Production storyboard from validated plan

Message: A project can be divided into independent jobs, worked on at the same time, and brought together as one finished deliverable.

Narration: One project splits into three independent jobs for three Bots. Together, they work at once: folding the cover, pressing pages, and preparing the binding. Then the finished pieces join, becoming one complete book together. Finally, the book reaches your hands as one finished deliverable.

Environment: workshop

Ending: The receiving hands withdraw with the delivered book, followed by a short still hold.

## dispatch-jobs

- subject: The project folio and three Bots
- action: The folio unfolds, distributing its cover, pages and binding into three Bot grips.
- before_after: One intact folio becomes three distinct job pieces held by separate Bots.
- focal_detail: Each component retains part of the shared project seal, keeping its origin clear.
- focus_target: workshop.project
- framing: subject
- consequence: The project is distributed into three independent jobs.
- shot: workshop-wide
- narration: One project splits into three independent jobs for three Bots.
- caption: Splitting the project
- headline_mode: clear
- headline: 
- Executable actions: [{"kind": "workshop.dispatch", "subject": "project", "cue": "splits", "result": "none", "requires": []}]

## parallel-work

- subject: The cover, pages and binding
- action: All three Bots work simultaneously: folding the cover, pressing the pages and preparing the binding.
- before_after: A flat cover, uneven pages and curled binding become prepared book components.
- focal_detail: All three operations remain visible together, with the page press contact unobstructed.
- focus_target: workshop.jobs
- framing: subject
- consequence: The separate components become ready for assembly at nearly the same time.
- shot: workshop-wide
- narration: Together, they work at once: folding the cover, pressing pages, and preparing the binding.
- caption: Working at the same time
- headline_mode: clear
- headline: 
- Executable actions: [{"kind": "workshop.work_parallel", "subject": "project", "cue": "work", "result": "none", "requires": ["jobs-distributed"]}]

## assemble-book

- subject: The three prepared book components
- action: The same cover, pages and binding slide together, wrap closed and receive one shared press.
- before_after: Three separate components become one bound book with a complete project seal.
- focal_detail: The joining spine and recombined seal make the shared result legible.
- focus_target: workshop.assembly
- framing: detail
- consequence: The parallel jobs resolve into one finished deliverable.
- shot: workshop-wide
- narration: Then the finished pieces join, becoming one complete book together.
- caption: Bringing the pieces together
- headline_mode: clear
- headline: 
- Executable actions: [{"kind": "workshop.assemble", "subject": "project", "cue": "finished pieces", "result": "none", "requires": ["jobs-worked"]}]

## deliver-book

- subject: The finished book and receiving hands
- action: The center Bot extends the assembled book; separate hands receive it and withdraw as the Bot releases.
- before_after: The completed book moves from the workshop into the recipient's hands.
- focal_detail: The same complete book and project seal remain visible throughout the handoff.
- focus_target: workshop.delivery
- framing: subject
- consequence: One finished deliverable reaches the recipient.
- shot: workshop-wide
- narration: Finally, the book reaches your hands as one finished deliverable.
- caption: Delivering one result
- headline_mode: clear
- headline: 
- Executable actions: [{"kind": "workshop.deliver", "subject": "project", "cue": "reaches", "result": "none", "requires": ["book-assembled"]}]
