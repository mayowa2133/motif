"""The host's acting library (plan-to-9 phase 2).

Claudex cut 6 grade: Bot helped, but the reference character performs. Each claim beat now names an
act: what the host does while the machine works, how it winds up and hits on the contact (which the
pipeline already times to the narration), and the reaction it holds in the payoff. Each beat also
names how the host arrives in its set. No act ever holds a plain standing pose.

act_motion() returns the same tuple bot_motion() always did, (pose, face, dx, dy, squash, cycle), so
every mascot plays every act.
"""
import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Act:
    work: tuple          # poses the host alternates while it works the machine
    work_face: str
    hit: tuple           # (pose, face) on the contact, held as the reaction starts
    react: tuple         # ((pose, face), ...) the payoff plays through in order
    beat: int = 14       # frames per work gesture
    lean: float = 6.0    # sideways lean while working
    jump: float = 30.0   # lift on the hit
    note: str = ''


ACTS = {
    'types': Act(('typing',), 'determined', ('presenting', 'happy'), (('presenting', 'proud'), ('celebrating', 'excited')), beat=6, lean=2.0, jump=22,
                 note='types at the keys, sits back proud when it runs'),
    'stamps': Act(('holding-object', 'pushing'), 'determined', ('pushing', 'determined'), (('presenting', 'proud'), ('pointing', 'happy')), beat=12, jump=40,
                  note='winds up and slams the stamp, then shows it off'),
    'gasps': Act(('inspecting', 'magnifying-glass'), 'thinking', ('falling', 'shocked'), (('pointing', 'surprised'), ('thinking', 'worried')), beat=16, jump=46,
                 note='studies it, jumps back at what it finds'),
    'smug': Act(('pointing', 'presenting'), 'determined', ('presenting', 'proud'), (('presenting', 'proud'), ('pointing', 'happy')), beat=18, lean=3.0, jump=16,
                note='calm and sure: points, then a proud lean'),
    'shrugs': Act(('thinking',), 'confused', ('presenting', 'confused'), (('presenting', 'confused'), ('thinking', 'annoyed')), beat=20, jump=12,
                  note='puzzles over it, then an open-armed shrug'),
    'cheers': Act(('pointing', 'pushing'), 'excited', ('celebrating', 'excited'), (('celebrating', 'excited'), ('presenting', 'happy')), beat=10, jump=52,
                  note='eggs the machine on and celebrates the result'),
    'inspects': Act(('magnifying-glass', 'inspecting'), 'thinking', ('pointing', 'surprised'), (('pointing', 'proud'), ('inspecting', 'happy')), beat=16,
                    note='checks it with a glass, points at the catch'),
}
ENTRANCES = ('walk', 'pop', 'drop', 'slide')
# What the host does by default for a claim's relation; the brief's visual.act wins.
BY_RELATION = {'demo': 'types', 'approve': 'stamps', 'transform': 'cheers', 'compare': 'inspects', 'contrast': 'shrugs', 'cause': 'gasps'}


def default_act(relation, rig, previous=None):
    """The act for a beat with none authored: by relation, else by machine, never the previous beat's."""
    first = BY_RELATION.get(relation) or ('types' if rig == 'app-screen' else 'cheers')
    if first != previous:return first
    return next(a for a in ACTS if a != previous)


def _ease(k):
    k = max(0.0, min(1.0, k));return k * k * (3 - 2 * k)


def act_motion(act, entrance, role, u, f, n, tc, side, entering=True):
    """(pose, face, dx, dy, squash, cycle) for frame f of n (u = f / n) in a setup or payoff shot."""
    a = ACTS[act]
    if role == 'setup':
        arrive = min(1.0, u / .22) if entering else 1.0
        if arrive < 1:
            k = _ease(arrive)
            if entrance == 'pop':   # springs up from below the frame, stretches, lands with a squash
                return a.work[0], 'excited', 0.0, 320 * (1 - k) - 40 * math.sin(k * math.pi), 1 + .12 * math.sin(k * math.pi), None
            if entrance == 'drop':  # falls in from above and lands
                return 'falling' if k < .7 else a.work[0], 'surprised', 0.0, -560 * (1 - k) ** 2, (1 - .14 * math.sin((k - .7) / .3 * math.pi)) if k > .7 else 1.06, None
            if entrance == 'slide':  # skids in from its side
                return 'pushing', 'determined', side * 260 * (1 - k), 0.0, 1.0, None
            return 'standing', 'determined', side * 80 * (1 - k), 0.0, 1.0, 'walk'  # legs cycle, so not a held pose
        at = u / max(1e-6, tc * .92) if tc else 1.0
        if at < .82:  # works the machine: alternating gestures with a bob, never a held pose
            return a.work[(f // a.beat) % len(a.work)], a.work_face, a.lean * math.sin(f * .17), -9 * abs(math.sin(f * (.6 if a.beat < 8 else .3))), 1.0, None
        if at < .92:  # anticipation: crouch before the hit
            k = (at - .82) / .1;return a.work[-1], a.work_face, -side * 10 * k, 10 * k, 1 - .08 * k, None
        hit = max(0.0, min(1.0, (at - .92) / .3))
        return a.hit[0], a.hit[1], 0.0, -a.jump * math.sin(hit * math.pi), 1 + .1 * math.sin(hit * math.pi * 2), None
    if role == 'payoff':
        if u < .12:return a.hit[0], a.hit[1], 0.0, -a.jump * .5 * (1 - u / .12), 1.0, None  # the held reaction carries over the cut
        step = a.react[min(len(a.react) - 1, int((u - .12) / .88 * len(a.react)))]
        return step[0], step[1], 5 * math.sin(f * .2), -abs(math.sin(f * .24)) * 12, 1.0, None
    return 'celebrating', 'excited', 0.0, -abs(math.sin(f * .2)) * 20, 1.0, None


def standing_run(act, entrance, n=60, tc=.5):
    """Longest run of frames in which the host holds a plain standing pose across setup and payoff."""
    best = run = 0
    for role in ('setup', 'payoff'):
        for f in range(n):
            pose, *_, cycle = act_motion(act, entrance, role, f / n, f, n, tc, -1)
            run = run + 1 if pose == 'standing' and not cycle else 0;best = max(best, run)
    return best
