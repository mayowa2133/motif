import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import motif_acts as A
from build_motif_bot import EXPRESSIONS, POSES


def test_every_act_and_entrance_uses_real_poses_and_faces():
    for act in A.ACTS:
        for entrance in A.ENTRANCES:
            for role in ('setup', 'payoff'):
                for f in range(60):
                    pose, face, dx, dy, squash, cycle = A.act_motion(act, entrance, role, f / 60, f, 60, .5, -1)
                    assert pose in POSES and face in EXPRESSIONS, (act, entrance, role, f, pose, face)
                    assert .8 < squash < 1.25


def test_no_act_holds_a_plain_standing_pose():
    for act in A.ACTS:
        for entrance in A.ENTRANCES:
            assert A.standing_run(act, entrance) <= 30, (act, entrance)


def test_the_hit_lands_on_the_contact_and_the_reaction_carries_over():
    a = A.ACTS['gasps']
    pose, face, *_ = A.act_motion('gasps', 'walk', 'setup', .48, 29, 60, .5, -1)
    assert (pose, face) == a.hit
    assert A.act_motion('gasps', 'walk', 'payoff', .05, 3, 60, .5, -1)[:2] == a.hit


def test_default_act_follows_the_relation_and_never_repeats():
    assert A.default_act('demo', 'app-screen') == 'types'
    assert A.default_act('demo', 'app-screen', previous='types') != 'types'


def test_host_acts_gate_flags_a_repeat_and_an_unknown_act():
    import motif_lessons as L
    beat = lambda i, act: {'id': f'b{i}', 'kind': 'claim', 'shots': [{'bot': {'act': act, 'entrance': 'pop'}}]}
    assert L.check_host_acts(None, {'beats': [beat(0, 'types'), beat(1, 'gasps')]}, None) == []
    out = L.check_host_acts(None, {'beats': [beat(0, 'types'), beat(1, 'types'), beat(2, 'juggles')]}, None)
    assert [o['where'] for o in out] == ['b1', 'b2']


def test_race_track_never_frames_close_and_the_hook_pair_keeps_its_framing():
    import motif_rigs
    import motif_reel as R
    race = motif_rigs.get('race-track')
    assert race.focus(race.params(None), 'close') is None
    shot = lambda: {'rig': {'id': 'race-track', 'params': {}}, 'role': 'setup'}
    beats = [{'id': 'hook', 'kind': 'hook', 'shots': [shot()]}, {'id': 'b1', 'kind': 'claim', 'shots': [shot()]}]
    R._vary_framing(beats)
    assert 'framing' not in beats[1]['shots'][0]['rig']


def test_cta_short_warns_on_a_long_end_card():
    import motif_lessons as L
    plan = lambda n: {'beats': [{'id': 'cta', 'kind': 'cta', 'narration': ' '.join(['word'] * n)}]}
    assert L.check_cta_short(None, plan(10), None) == []
    assert L.check_cta_short(None, plan(12), None)


def test_carried_object_card_prints_its_label():
    import motif_reel as R
    from motif_rigs.palettes import palette
    svg = R.carried_note(100, 100, 0, palette('lilac'), 1.0, 'weather.py')
    assert 'weather.py' in svg and '<text' in svg
    assert 'weather.py' not in R.carried_note(100, 100, 0, palette('lilac'))


def test_brief_carry_reaches_every_shot_and_hook_framing_is_kept():
    import json, motif_reel as R
    from pathlib import Path
    brief = json.loads((Path(__file__).resolve().parents[1] / 'quality/new-topic-briefs/uv-python-fast.json').read_text())
    plan = R.plan_reel(brief, allow_draft=True)
    assert plan['carry'] == 'weather.py'
    assert plan['beats'][0]['shots'][0]['rig'].get('framing') == 'close'


def test_bridge_span_only_reads_wide():
    from motif_rigs import get
    rig = get('bridge-span');assert rig.focus(rig.params(None), 'close') is None


def test_host_stands_clear_of_the_stamp_gate_document():
    import motif_sets as S
    from motif_rigs import get
    lay = S.solve('street', 'stamp-gate', {'document': 'YOUR PROMPTS', 'stamp': 'LOCAL', 'verdict': 'rejected'}, 'berry/mauve', 83, 3)
    hero = lay['hero'];doc = S._box(hero['x'], S.FLOOR, hero['scale'], get('stamp-gate').bot_slot['keep_clear'][0])
    half = S.BOT_HALF * lay['bot']['scale'];host = (lay['bot']['x'] - half, S.FLOOR - 4.2 * half, 2 * half, 4.2 * half)
    assert S._overlap(host, doc) == 0


def test_big_number_reads_the_headline_number_not_a_name():
    import motif_reel as R
    assert R.big_number('3 TOOLS, 1 COMMAND EACH') == {'value': '3', 'unit': 'TOOLS'}
    assert R.big_number('KEPT FOR 90 DAYS') == {'value': '90', 'unit': 'DAYS'}
    assert R.big_number('LOCALHOST:11434')['value'] == '11434'
    assert R.big_number('PULL GEMMA4 ONCE') is None and R.big_number('GPT-6 AUDITS') is None


def test_big_number_skips_machines_that_count_and_hook_host_acts():
    import json, motif_reel as R
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    git = R.plan_reel(json.loads((root / 'quality/new-topic-briefs/git-reflog-rescue.json').read_text()), True)
    assert not [b for b in git['beats'] if b['shots'][-1].get('number')]  # stacked-meter and receipt-stack count on their own
    uv = R.plan_reel(json.loads((root / 'quality/new-topic-briefs/uv-python-fast.json').read_text()), True)
    speed = next(b for b in uv['beats'] if b['id'] == 'speed')
    assert speed['shots'][1]['number']['value'] == '10-100X'
    assert uv['beats'][0]['shots'][0]['bot']['act'] in R.HOST_ACTS


def test_note_pictures_render_and_are_not_labels():
    import motif_rigs
    rig = motif_rigs.get('app-screen')
    p = rig.params({'device': 'laptop', 'ui': 'note', 'title': 'j', 'lines': ['# Week', 'one line', '![tree] ![@ollama] ![nothing-here]']})
    svg = rig.render(p, ('run', 1.0), 'lagoon')
    assert '![' not in svg and 'circle' in svg
    assert not any('![' in t for t in rig.printed_text(p))
