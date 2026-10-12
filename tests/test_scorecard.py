import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import motif_scorecard as S


def test_inside_the_reference_range_scores_ten():
    assert S.score(3.0, 1.8, 3.7) == 10.0


def test_score_falls_off_outside_the_range():
    assert S.score(.25, .5, 1.0) == 5.0
    assert S.score(0.0, .5, 1.0) == 0.0
    assert S.score(None, 0, 1) is None


def test_screen_detail_counts_lines_pane_cards_and_chrome():
    import motif_rigs
    rig = motif_rigs.get('app-screen')
    sparse = rig.detail(rig.params({'device': 'laptop', 'ui': 'note', 'lines': ['# Log', 'one']}))
    dense = rig.detail(rig.params({'device': 'monitor', 'ui': 'files', 'lines': ['a/', '  b.md'], 'pane': ['# B', 'x', 'y', 'z'], 'cards': ['B']}))
    assert sparse < 10 and dense > sparse


def test_shot_variety_exempts_the_hook_preview_like_gate_l033(tmp_path):
    import json
    race = {'rig': {'id': 'race-track'}}
    beats = [{'id': 'hook', 'kind': 'hook', 'shots': [race]}, {'id': 'a', 'kind': 'claim', 'shots': [race]},
             {'id': 'b', 'kind': 'claim', 'shots': [{'rig': {'id': 'conveyor'}}]}, {'id': 'c', 'kind': 'claim', 'shots': [{'rig': {'id': 'conveyor'}}]}]
    (tmp_path / 'production-plan.json').write_text(json.dumps({'beats': beats}))
    # hook->a is exempt, a->b differs, b->c repeats: one of two counted pairs varies
    assert S.plan_metrics(tmp_path)['shot_variety'] == .5
