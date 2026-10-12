import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import motif_acts as A
from motif_springs import pop, spring, track


def test_spring_starts_at_zero_and_settles_at_one():
    assert spring(0) == 0 and abs(spring(1.0) - 1) < 1e-3
    assert spring(.05) > .1  # fast start, unlike an ease that creeps in


def test_pop_overshoots_and_lands_exactly():
    curve = [pop(i / 200, .5) for i in range(201)]
    assert curve[0] == 0 and curve[-1] == 1.0
    assert 1.1 < max(curve) < 1.25  # an object overshoots its mark
    assert 1.0 < max(pop(i / 200, .7) for i in range(201)) < 1.07  # UI barely does
    assert all(abs(b - a) < .08 for a, b in zip(curve, curve[1:]))  # no jump at the end


def test_track_carries_velocity_into_a_retarget():
    keys = [(0, 0), (0, 100), (.15, 50)]
    assert track(0, keys) == 0 and abs(track(1.5, keys) - 50) < .5
    # mid-move retarget: the value keeps rising for a moment before it turns, no dead stop
    assert track(.17, keys) > track(.15, keys)


def test_entrances_overshoot_their_mark():
    # Slide skids past its mark and rocks back; pop rises above the floor before settling.
    xs = [A.act_motion('types', 'slide', 'setup', f / 100, f, 100, .5, -1)[2] for f in range(22)]
    assert min(xs) < -0.05 * 260 and xs[0] < -200
    ys = [A.act_motion('types', 'pop', 'setup', f / 100, f, 100, .5, -1)[3] for f in range(22)]
    assert ys[0] > 300 and min(ys) < -20
