# Optional reviewer intake controller

`scripts/motif_review_intake.py` is a standalone, standard-library controller.
Existing production critics and capture paths do not call it. It makes no model
calls and creates no media. Run its synthetic suite with
`python3 -m unittest discover -s tests -p test_review_intake.py -v`.

Create a fresh controller-owned directory using `ReviewIntake.create`, sealing
script/anchors/criteria before stage A. Send only the return value of `start_a`
to a fresh reviewer session. Stage A accepts neutral frame names and declared
masked images only. Administrative run/reviewer labels stay in controller storage;
the reviewer packet uses generated opaque identifiers. Submit the free description with complete caller-attested
context and invocation records through `commit_a`. `release_b` returns sealed
criteria only after validating the committed description and receipt chain.
Use a separate fresh session for stage B. Never give either reviewer the storage
directory, source files, another reviewer's report, or inherited conversation.

Writes are exclusive and fsynced; a directory lock serializes API transactions.
Description mutation, changed bound files, early release, incomplete coverage,
replay, unexpected invocation events, and clock discontinuity fail closed.
Rejection records and candidate descriptions remain available for inspection;
an invalidated session requires a new directory, not a repaired receipt.
Unknown or denied tool events produce UNVERIFIED and block release. The event
grammar is deliberately narrow: session.started then response.completed bound
to the submitted description. A backend adapter must truthfully capture and
normalize the complete event stream; this module is not that adapter.

The process-scoped monotonic clock intentionally blocks resumption across
processes because same-clock continuity cannot be authenticated. A crashed
transaction leaves a BUSY lock; inspect and archive it rather than clearing it
and claiming an uninterrupted intake. Exclusive creation prevents API overwrite,
and hash checks detect later ordinary mutation. These are not external
attestation, WORM storage, or protection against an administrator rewriting the
entire directory.

Successful output says PASS_INTAKE_ORDER_ONLY. Image masking, complete context,
freshness, and event completeness are caller attestations. Image pixels are not
examined. Hidden information already known to an agent or accessed outside this
managed API is always UNVERIFIABLE. No result certifies general blindness or
independence outside this intake. This optional controller must not bypass
existing sampled-review, film approval, or capture gates.

For durable synthetic receipts only, set MOTIF_INTAKE_TEST_ARTIFACTS to a fresh
directory outside the source tree. Each test copies its controller record there;
existing destinations are never overwritten. No real images or pilot evidence
are read by the tests.
