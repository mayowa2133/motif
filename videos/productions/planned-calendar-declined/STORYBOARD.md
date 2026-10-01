# Production storyboard from validated plan

Message: An assistant finds a free hour and proposes a focus session. The person declines, so the calendar remains unchanged.

Narration: Assistant spots an open hour at four. It proposes focus time, placing a dashed card there. The person presses decline, removing the proposal while the existing meeting stays. The original calendar remains visibly unchanged.

Environment: calendar

Ending: Hold on the unchanged calendar with the original 3 PM TEAM appointment and an empty 4 PM hour.

## beat-1

- subject: Assistant and calendar
- action: The assistant points to the empty 4 PM hour.
- before_after: Before: the board shows TEAM at 3 PM and an empty 4 PM slot. After: the assistant visibly indicates the open hour.
- focal_detail: The empty 4 PM row beside the pointing assistant.
- consequence: The available hour is clearly identified.
- shot: calendar-wide
- narration: Assistant spots an open hour at four.
- caption: Finding a free hour
- headline: OPEN HOUR
- Executable actions: [{"kind": "bot.pose", "subject": "bot", "cue": "spots", "result": "pointing", "requires": []}]

## beat-2

- subject: Calendar proposal
- action: A dashed FOCUS card appears in the empty 4 PM slot.
- before_after: Before: 4 PM is empty. After: a dashed FOCUS proposal occupies the slot.
- focal_detail: The dashed border distinguishing the proposal from the solid TEAM appointment.
- consequence: The focus session is visible but not booked.
- shot: calendar-detail
- narration: It proposes focus time, placing a dashed card there.
- caption: Proposing focus time
- headline: PROPOSED
- Executable actions: [{"kind": "calendar.propose", "subject": "calendar", "cue": "placing", "result": "none", "requires": []}]

## beat-3

- subject: Person and proposal
- action: A person's finger presses DECLINE; a cross registers and the dashed FOCUS card disappears.
- before_after: Before: the dashed FOCUS proposal is visible at 4 PM. After: the proposal is removed while TEAM remains solid at 3 PM.
- focal_detail: The fingertip on DECLINE, followed by the cross and removal.
- consequence: The proposed focus session is rejected without changing the existing appointment.
- shot: calendar-detail
- narration: The person presses decline, removing the proposal while the existing meeting stays.
- caption: Your decision
- headline: 
- Executable actions: [{"kind": "calendar.decline", "subject": "calendar", "cue": "presses decline", "result": "none", "requires": ["proposal-visible"]}]

## beat-4

- subject: Calendar
- action: The board visibly holds on the original schedule.
- before_after: Before: the declined proposal has been removed. After: TEAM remains at 3 PM and 4 PM is empty.
- focal_detail: The solid TEAM card and clean, empty 4 PM row.
- consequence: The ending confirms that nothing was added or moved.
- shot: calendar-wide
- narration: The original calendar remains visibly unchanged.
- caption: Original schedule
- headline: CALENDAR UNCHANGED
- Executable actions: []
