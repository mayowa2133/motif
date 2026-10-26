import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import motif_jury as J


def test_longest_static_finds_the_frozen_run():
    diffs = [2, 2, .1, .1, .1, .1, 2, .1, 2]
    assert J.longest_static(diffs, fps=2) == (2.0, 1.0)


def test_fastest_moves_skip_cuts_and_stay_apart():
    diffs = [0] * 300
    diffs[59] = 90   # a cut at 2.0 s
    diffs[149] = 20  # a fast move at 5.0 s
    diffs[152] = 19  # the same move, too close to count twice
    diffs[239] = 12  # a second move at 8.0 s
    assert J.fastest_moves(diffs, cuts=[2.0]) == [5.0, 8.0]


def test_hero_placement_reports_payoff_shares():
    hero = J.hero_placement([5.0, 21.0], 30.0)
    assert hero['payoff_shares'] == [.17, .7] and hero['in_window']
    assert not J.hero_placement([5.0], 30.0)['in_window']


def test_run_context_reads_payoffs_and_story(tmp_path):
    (tmp_path / 'audio-plan.json').write_text(json.dumps({'sfx_cues': [
        {'start': 4.0, 'meaning': 'claim accent'}, {'start': 9.5, 'meaning': 'payoff accent'}]}))
    (tmp_path / 'production-plan.json').write_text(json.dumps({'title': 'T', 'story': {'ending': 'board full'},
        'beats': [{'id': 'hook', 'kind': 'hook', 'headline': 'H', 'story': {'promise': 'p'}}]}))
    ctx = J.run_context(tmp_path)
    assert ctx['payoffs'] == [9.5] and ctx['ending'] == 'board full' and ctx['promise'] == 'p' and ctx['beats'][0]['headline'] == 'H'


@pytest.mark.skipif(not shutil.which('ffmpeg'), reason='needs ffmpeg')
def test_pack_builds_sheet_strips_stills_and_prompt(tmp_path):
    video = tmp_path / 'film.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'testsrc2=size=216x384:rate=30:duration=4',
                    '-f', 'lavfi', '-i', 'sine=frequency=440:duration=4', '-shortest', '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                    '-c:a', 'aac', str(video)], check=True)
    r = J.pack(video, out=tmp_path / 'jury')
    out = tmp_path / 'jury'
    assert (out / 'contact-sheet.png').exists() and r['stills'] and r['filmstrips']
    assert r['spec']['width'] == 216 and abs(r['spec']['duration'] - 4) < .1 and r['spec']['loudness_lufs'] is not None
    prompt = (out / 'jury-prompt.md').read_text()
    assert 'You did NOT make this film' in prompt and 'jury.json' in prompt and all(k in prompt for k in J.DIMENSIONS)
