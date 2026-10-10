import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

import motif_improve  # noqa: E402
import motif_lessons as L  # noqa: E402
from motif_rigs import get  # noqa: E402

VAULT = {'mode': 'check', 'pages': ['SLEEP', 'FOCUS', 'HABITS', 'PRICING', 'HIRING', 'WRITING', 'HEALTH', 'MY GAPS'], 'pages_from': 8, 'pages_to': 8}


def _layout(dressing=()):
    rig = get('knowledge-vault')
    return {'hero': {'rig': 'knowledge-vault', 'values': rig.params(VAULT), 'scale': .5, 'x': 360, 'y': 1000},
            'palette': 'lagoon', 'dressing': list(dressing)}


def _plan(*beats):
    return {'beats': [{'id': b, 'palette': pal, 'shots': [{'id': f'{b}-1', 'headline': head, 'rig': {'id': 'knowledge-vault', 'params': VAULT}}]}
                      for b, head, pal in beats]}


def test_ledger_checks_exist():
    lessons = L.ledger()['lessons']
    assert len({l['id'] for l in lessons}) == len(lessons)
    for l in lessons:
        assert l['level'] in ('gate', 'warn', 'brief') and l['rule']
        assert l.get('check') is None or l['check'] in L.CHECKS


def test_texts_apply_nested_transforms():
    svg = '<g transform="translate(100 50) scale(2)"><text x="10" y="20" font-size="12">HI</text></g>'
    t, = L.texts(svg)
    assert t['text'] == 'HI' and t['size'] == 24
    assert t['box'][0] == pytest.approx(120) and t['box'][1] == pytest.approx(50 + 2 * (20 - 9))


def test_hero_labels_found():
    found = {t['text'] for t in L.hero_labels(_layout())}
    assert {'SLEEP', 'MY GAPS'} <= found


def test_label_occlusion_flags_front_prop_only():
    label = next(t for t in L.hero_labels(_layout()) if t['text'] == 'MY GAPS')
    prop = {'prop': 'crate', 'box': label['box']}
    assert L.check_label_occlusion(None, None, {'b': _layout([dict(prop, layer='back')])}) == []
    found = L.check_label_occlusion(None, None, {'b': _layout([dict(prop, layer='front')])})
    assert found and 'MY GAPS' in found[0]['detail']


def test_label_legibility_reports_small_labels():
    small = _layout();small['hero']['scale'] = .2
    assert L.check_label_legibility(None, None, {'b': small})
    big = _layout();big['hero']['scale'] = 2
    assert L.check_label_legibility(None, None, {'b': big}) == []


def test_headline_openers():
    plan = _plan(('a', 'ANSWERS WITH SOURCES', 'lagoon'), ('b', 'ANSWERS GET SAVED', 'lagoon'), ('c', 'SAVED BACK', 'lagoon'))
    found = L.check_headline_openers(None, plan, {})
    assert [f['where'] for f in found] == ['b-1']


def test_shared_object_palette():
    assert L.check_shared_object_palette(None, _plan(('a', 'X', 'lagoon'), ('b', 'Y', 'lagoon/berry')), {}) == []
    found = L.check_shared_object_palette(None, _plan(('a', 'X', 'lagoon'), ('b', 'Y', 'berry')), {})
    assert found and found[0]['where'] == 'b'


def test_run_gates_on_gate_lessons(tmp_path):
    plan = _plan(('a', 'ANSWERS ONE', 'lagoon'), ('b', 'ANSWERS TWO', 'lagoon'))
    out = L.run(tmp_path, plan, {})
    assert out['status'] == 'FAIL'
    assert L.run(tmp_path, _plan(('a', 'ONE', 'lagoon'), ('b', 'TWO', 'lagoon')), {})['status'] == 'PASS'


def test_every_repo_brief_passes_regress():
    out = motif_improve.regress()
    assert out['briefs'] and out['status'] == 'PASS', [b for b in out['briefs'] if b['status'] != 'PASS']


def test_retro_and_backlog(tmp_path, monkeypatch):
    monkeypatch.setattr(motif_improve, 'RUN_LOG', tmp_path / 'run-log.jsonl')
    monkeypatch.setattr(motif_improve, 'BACKLOG', tmp_path / 'backlog.json')
    project = tmp_path / 'reel';project.mkdir()
    (project / 'reel-record.json').write_text(json.dumps({'stages': [{'stage': 'plan', 'status': 'PASS'}, {'stage': 'gate', 'status': 'PASS'}]}))
    (project / 'brief.json').write_text(json.dumps({'slug': 'demo', 'mascot': 'kit'}))
    (project / 'lessons.json').write_text(json.dumps({'status': 'PASS', 'lessons': [{'lesson': 'L012', 'status': 'WARN', 'findings': [{'where': 'b', 'detail': 'small'}]}]}))
    (project / 'library-requests.json').write_text(json.dumps([{'kind': 'rig', 'id': 'tide-pool', 'needed_by': 'b2'}]))
    entry = motif_improve.retro(project, 'labels too small', 'Mayowa')
    assert entry['mascot'] == 'kit' and entry['feedback'][0]['by'] == 'Mayowa'
    text = (project / 'retro.md').read_text()
    assert 'L012 WARN' in text and 'tide-pool' in text and 'labels too small' in text
    out = motif_improve.backlog()
    assert out['missing_library'][0]['entry'] == 'rig/tide-pool' and out['recurring_findings'][0]['lesson'] == 'L012'


def test_add_lesson_requires_known_check(tmp_path, monkeypatch):
    ledger = tmp_path / 'lessons.json';ledger.write_text(L.LEDGER.read_text())
    monkeypatch.setattr(L, 'LEDGER', ledger)
    with pytest.raises(SystemExit):
        motif_improve.add_lesson('s', 'sym', 'rule', check='nope')
    new = motif_improve.add_lesson('s', 'sym', 'rule', check='headline-openers')
    assert new['level'] == 'gate' and new['id'] == f'L{len(L.ledger()["lessons"]):03d}'
