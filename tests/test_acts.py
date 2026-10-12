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
