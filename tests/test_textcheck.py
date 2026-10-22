import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

import motif_lessons as L  # noqa: E402
import motif_textcheck as T  # noqa: E402
from motif_reel import CAPTION_LANES, caption_lanes  # noqa: E402


def _box(s, x0, y0, x1, y1, layer='shot'):
    return {'s': s, 'layer': layer, 'x0': x0, 'y0': y0, 'x1': x1, 'y1': y1}


def test_text_past_the_frame_edge_is_cut_off():
    kinds = [k for k, _, _ in T.classify([_box('AUDITS', -40, 600, 120, 650)])]
    assert kinds == ['cut off by the frame edge']


def test_text_under_instagrams_caption_or_buttons_is_flagged():
    bottom = _box('bugs.', 400, 1760, 560, 1830, 'captions')   # where captions used to sit
    rail = _box('LOGIN', 950, 900, 1070, 940)                   # under the like/comment/share rail
    clear = _box('bugs.', 400, 1400, 560, 1490, 'captions')    # where they sit now
    kinds = [k for k, _, _ in T.classify([bottom, rail, clear])]
    assert kinds == ['under the phone UI', 'under the phone UI']


def test_overlapping_strings_are_flagged_but_a_word_and_its_echo_are_not():
    a, b = _box('SENT BACK', 700, 600, 900, 650), _box('98% context left', 760, 610, 980, 640)
    echo = _box('SENT', 700, 600, 800, 650)
    issues = T.classify([a, b, echo])
    assert [k for k, _, _ in issues] == ['overlaps other text']
    assert 'SENT BACK' in issues[0][1] and '98% context' in issues[0][1]


def _group(text, start=0.0, end=1.0):
    return {'text': text, 'start': start, 'end': end, 'words': [{'text': w} for w in text.split()]}


def test_captions_take_the_lane_above_the_phone_ui_when_it_is_clear():
    groups = caption_lanes([_group('It had three bugs.')], [(0, ['<text x="100" y="500" font-size="20">PLAN</text>'] * 30)])
    assert (groups[0]['y'], groups[0]['dx']) == (CAPTION_LANES[0], 0)


def test_captions_move_off_a_label_in_their_lane():
    label = f'<text x="300" y="{CAPTION_LANES[0] + 8}" font-size="22">LOGIN</text>'
    groups = caption_lanes([_group('It had three bugs.')], [(0, [label] * 30)])
    assert (groups[0]['y'], groups[0]['dx']) != (CAPTION_LANES[0], 0)
    assert groups[0]['y'] in CAPTION_LANES


def test_caption_safe_gate(tmp_path):
    (tmp_path / 'caption-events.json').write_text(json.dumps([{'text': 'ok', 'start': 0, 'y': 975}, {'text': 'old', 'start': 1, 'y': 1200}]))
    found = L.check_caption_safe(tmp_path, {}, {})
    assert [f['where'] for f in found] == ['1.00s']
