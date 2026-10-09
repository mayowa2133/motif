# Test baseline, October 2026

Recorded on `main` at fb11ea5 (2026-10-09) before the original-reel plan work, in a Linux container with Python 3.13 and Node 22.

| Suite | Command | Result |
|---|---|---|
| Python | `python -m unittest discover -s tests` | 202 tests, 1 failure |
| Node | `node --test tests/*.cjs` | 6 tests, all pass |

## Failing on main

- `test_structure.StructureTests.test_ordinary_direction_and_rough_require_structure_before_io`
  `AssertionError: "fresh structure" does not match "production scope missing; explicitly declare saved project mode"`

  Cause: commit 87e32cc made `rough()` validate the declared production scope and freeze a capture record first. The older test used a project with no scope, so it stopped at the scope check, and the structure check now ran after a capture record was written.

  Fixed on `claude/original-2d-reels-gff322`: `rough()` validates scope, then plan and structure, and only then freezes the capture record. The test declares a technical-fixture scope so the structure gate is what it exercises. Both orderings that tests require now hold: scope before anything (`test_evidence_integration`), structure before any capture or render side effect (`test_structure`).

After the fix the suite passes in full.
