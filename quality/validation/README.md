# Quality-system validation

These are **five independent 2.5-second regression variants**, concatenated only for convenient review. They are copied from v6's billing interaction; they are not a new film. Both native previews contain 375 frames at 30 fps, 360 × 640. Captions are actually removed in the second render. No narration or final audio production was added.

| Blind clip | Intervention withheld from critics | Live result |
|---|---|---|
| q01 | Original interaction control | PASS in every shot gate, both critics |
| q02 | Remove the visible receipts, retain subscription and slump | Story/cause-effect failure caught |
| q03 | Shrink the hero board/receipts, retain room and Bot | Mobile/focal hierarchy failure caught |
| q04 | Replace burden with shared canonical celebrating performance | Character-performance failure caught |
| q05 | Freeze the scene for 2.5 seconds | Energy failure caught without event/particle quotas |

See [results.json](results.json), [story critic](fixtures/quality-review/rough/story-critic.json), [visual critic](fixtures/quality-review/rough/visual-critic.json) and [blocked gate](fixtures/quality-review/rough/gate.json). The resulting state is REPLAN_REQUIRED, with publication false and human final approval required.

Two separate live calls used the existing authenticated Codex CLI with explicit `MOTIF_PLANNER_MODEL=gpt-5.6-sol`. Requested model, timestamps, argv, input/output schema hashes, responses and event streams are recorded. They inspected ordered painted sheets, individual native before/middle/after frames and timed pixel-motion observations; no claim of native MP4 playback or listening. The expected fault labels and assertion file were withheld.

The first global-only review missed q02/q04 and is preserved in `validation-attempt-01`. That exposed a real limitation: global failures masked individual shots and the large sheets made acting harder to inspect. The implemented critic now requires a full per-shot gate assessment and receives individual native frames. The rerun detected the missed faults on **unchanged media**. A separate rejected backend attempt is preserved; its schema lacked explicit enum types, which was corrected. Neither attempt was silently replaced with canned output or counted as a creative repair.

Focused unit tests also cover missing metadata blocking canonical promotion, operational performance changing compiled events and native painted pixels, actual canonical hand geometry following a reacting prop under squash/rotation, radius bounds/falloff, missing gate coverage, stale evidence, two meaningful repairs maximum, technical coverage and human-review states. Synthetic unit critic records are clearly labeled and are never used as live evidence.

```sh
python3 scripts/validate_quality_evidence.py
python3 -m unittest discover -s tests -p 'test_quality_system.py' -v
python3 -m unittest discover -s tests -p 'test_directing_controls.py' -v
python3 -m unittest discover -s tests -p 'test_paper_energy.py' -v
```

`build_quality_fixtures.py` reconstructs fixture source in a fresh directory using copied v6 components and the existing frame compiler/runtime. The committed-style source package keeps stable references to gold video ranges instead of copying the full film. Renders and review samples are local task evidence, not canonical assets.

The freeze manifest verifies **540 tracked v6/canonical Bot files unchanged**. Other approved productions have no source diff. This limited regression success does not prove general original-film quality, temporal perception between sampled frames, factual accuracy or listening quality. Human viewing remains mandatory.
