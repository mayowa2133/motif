import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

import motif_face_acting as fa
from motif_bot_kit import dressed_bot
from motif_mascots import ids

TRACK = ['neutral'] * 10 + ['shocked'] * 30


def test_face_squints_before_a_change_and_lands_as_a_take():
    assert fa.face_scale(TRACK, 2) == (1.0, 1.0)
    squint = [fa.face_scale(TRACK, f)[1] for f in (7, 8, 9)]
    assert squint == sorted(squint, reverse=True) and squint[-1] < .7
    take = [fa.face_scale(TRACK, f)[1] for f in range(10, 10 + fa.TAKE_FRAMES)]
    assert take[0] > 1.2 and min(take) < 1 and abs(take[-1] - 1) < .03
    assert fa.face_scale(TRACK, 30) == (1.0, 1.0)


def test_every_mascot_face_is_acted_without_touching_the_body():
    for m in ids():
        body = dressed_bot(100, 200, .2, 'happy', 'standing', (), 'sunrise', mascot=m)
        acted = fa.act_face(body, m, 1.1, .5)
        assert acted != body and acted.count('scale(1.1000 0.5000)') == 1, m
        assert re.sub(r' transform="translate\([^"]*scale\(1\.1000 0\.5000\)[^"]*"', '', acted) == body, m
        assert fa.act_face(body, m, 1.0, 1.0) == body


def test_marks_pop_on_strong_reactions_and_fade():
    track = ['neutral'] * 5 + ['shocked'] * 10 + ['confused'] * 10 + ['happy'] * 5 + ['worried'] * 40
    events = fa.emote_events(track)
    assert events[0] == (5, 'bang') and all(b[0] - a[0] >= fa.EMOTE_GAP for a, b in zip(events, events[1:]))
    for kind in set(fa.EMOTES.values()):
        assert fa.mark(kind).startswith('<')
        assert fa.emote(kind, 10, 10, 70, -1) == '' and fa.emote(kind, 10, 10, 70, fa.EMOTE_FRAMES) == ''
        assert 'opacity="1.000"' in fa.emote(kind, 10, 10, 70, 8)


def test_lines_boil_on_twos():
    a, b, c = (fa.boil_lines('<g/>', f, 'host') for f in (4, 5, 6))
    assert a == b and a != c and 'feDisplacementMap' in a


def test_brief_schema_allows_host_acting():
    schema = json.loads((ROOT / 'schemas/reel-brief.schema.json').read_text())
    assert schema['properties']['host_acting']['type'] == 'boolean'
