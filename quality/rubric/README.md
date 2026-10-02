# Gate ownership

`gates.json` partitions ten critical gates between two live critics. Each must cover its full set exactly once; PASS elsewhere cannot compensate for FAIL or NOT_ASSESSED. Story/staging failures return REPLAN_REQUIRED. Art/motion failures return REPAIR_REQUIRED. Two meaningful changes without resolution return HUMAN_REVIEW_REQUIRED.

Passing rough review yields FINAL_ART_ALLOWED. Passing final moving review and separate picture technical checks allows audio finishing. Neither response is human approval. Unit-test synthetic reports are never used as live validation evidence.
