"""Negative reel boundaries; no renderer, voice or model service execution."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import motif_reel as reel
import motif_reel_script as script
from motif_evidence import freeze_capture, require_capture, seal_capture
from motif_frame_render import finish_encoder
from motif_inserts import counter_values
from motif_library import catalog
from motif_rigs import get

BRIEF = json.loads((ROOT / 'tests/fixtures/reel-brief-fixture.json').read_text())
PASS = {'status': 'PASS', 'failures': [], 'measured': {}}
FAIL = {'status': 'FAIL', 'failures': ['UNIT failure'], 'measured': {}}
ORIGIN = {'status': 'PASS', 'checked': 0, 'unknown': [], 'reference_derived': [], 'rejected': []}


def composition(project):
    (project / 'compositions').mkdir(exist_ok=True)
    spec = {'schemaVersion': '1.0', 'fps': 30, 'durationSec': 1,
            'initial': [{'target': '#unit-world', 'props': {'innerHTML': '<rect/>'}}],
            'events': [{'time': 1/30, 'target': '#unit-world', 'action': 'SET', 'params': {'props': {'innerHTML': '<circle/>'}}}]}
    (project / 'compositions/unit.html').write_text('<template><script>window.MotifEventEngine.compileFrames(' + json.dumps(spec) + ',"unit");</script></template>')
    (project / 'index.html').write_text('<div data-composition-id="unit" data-composition-src="compositions/unit.html" data-start="0" data-duration="1"></div>')
    (project / 'assets').mkdir(exist_ok=True)
    (project / 'assets/unit.txt').write_text('UNIT_ONLY')


class InputSafetyTests(unittest.TestCase):
    def test_negative_facts_keep_sign_and_unit_label(self):
        for value in ('-20%', '\u221220%', '-$20', '$-20', '-20'):
            with self.subTest(value=value):
                insert = reel._insert_for({'value': value, 'claim': 'Measured decrease'}, 'decrease', catalog())
                self.assertEqual(insert['args']['end'], -20)
                self.assertEqual(insert['args']['label'], 'MEASURED')
                values = counter_values(0, insert['args']['end'], 40)
                self.assertEqual(values[-1], -20)
                self.assertTrue(all(a >= b for a, b in zip(values, values[1:])))
        self.assertEqual(reel._number('20%')['value'], 20)
        self.assertEqual(reel._number('+20%')['value'], 20)
        self.assertEqual(reel._number('\u22120.5%')['value'], -.5)
        decimal = reel._insert_for({'value': '\u22120.5%', 'claim': 'Measured decrease'}, 'decrease', catalog())
        self.assertEqual(decimal['args']['label'], '-0.5%')

    def test_missing_or_invalid_insert_args_fail_plan(self):
        for insert in ({'kind': 'counter', 'args': {}}, {'kind': 'price_tag', 'args': {}},
                       {'kind': 'comment_end_card', 'args': {}}, {'kind': 'counter', 'args': {'end': 'twenty'}},
                       {'kind': 'gauge', 'args': {'value': float('inf')}},
                       {'kind': 'progress_bar', 'args': {'fraction': float('nan')}},
                       {'kind': 'star_badge', 'args': {'rating': 2, 'filled': 5}}):
            with self.subTest(insert=insert):
                b = copy.deepcopy(BRIEF);b['beats'][0]['visual']['insert'] = insert
                self.assertTrue(any('insert args invalid' in e for e in reel.validate_plan(reel.plan_reel(b))[0]))

    def test_unknown_rig_survives_warning_generation_for_library_request(self):
        b = copy.deepcopy(BRIEF);b['beats'][0]['visual']['rig'] = 'rocket-launch'
        plan = reel.plan_reel(b)
        errors, requests = reel.validate_plan(plan)
        self.assertTrue(errors)
        self.assertEqual(requests[0]['id'], 'rocket-launch')

    def test_race_lengths_and_finish_are_validated_before_compile(self):
        for params, message in (({'labels': ['A', 'B', 'C'], 'progress': [1, .8]}, 'matching lengths'),
                                ({'labels': ['A', 'B', 'C'], 'progress': [.8, .6, .4]}, 'leader must reach')):
            with self.subTest(params=params):
                with self.assertRaisesRegex(ValueError, message):get('race-track').params(params)
                b = copy.deepcopy(BRIEF);b['beats'][0]['visual'] = {'rig': 'race-track', 'params': params}
                self.assertTrue(any(message in e for e in reel.validate_plan(reel.plan_reel(b))[0]))
        for n in (2, 3, 4):
            p = {'labels': ['A'] * n, 'progress': [1] + [.5] * (n - 1)}
            self.assertEqual(get('race-track').contact_gap(p, 'race'), 0)


class PipelineSafetyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name);self.brief = self.root / 'brief.json'
        self.brief.write_text(json.dumps(BRIEF));self.project = self.root / 'out' / BRIEF['slug']

    def record(self):return json.loads((self.project / 'reel-record.json').read_text())

    def mocks(self, stack, rough=PASS, empty=PASS, gate=PASS, origin=ORIGIN):
        spans = [];cursor = 0
        for id_, text in script.lines(BRIEF):
            duration = script.count(text) / script.WORDS_PER_SECOND
            spans.append((id_, cursor, cursor + duration));cursor += duration + script.GAP
        prepare = stack.enter_context(patch('motif_reel.prepare'))
        stack.enter_context(patch('motif_reel.voice', return_value=(spans, cursor - script.GAP)))
        def compile_(project, *args):
            composition(project)
            return {'duration': cursor - script.GAP + .7, 'shots': 1, 'frames_index': [{'start': 0, 'duration': 1}]}
        compile_mock = stack.enter_context(patch('motif_reel.compile_reel', side_effect=compile_))
        stack.enter_context(patch('motif_pacing.check', side_effect=[rough, gate]))
        stack.enter_context(patch('motif_frame_snapshot.at_times', return_value=[]))
        def snapshot(project, requests, out, **kw):
            out.mkdir(parents=True);path = out / 'UNIT.bin';path.write_bytes(b'UNIT_ONLY');return [path]
        snapshots = stack.enter_context(patch('motif_frame_snapshot.snapshot', side_effect=snapshot))
        stack.enter_context(patch('motif_sets.check_frames', return_value=empty))
        stack.enter_context(patch('motif_provenance.check', return_value=origin))
        def render(project, out):
            out.parent.mkdir(parents=True);out.write_bytes(b'UNIT_ONLY_NOT_MEDIA');return {'frames': 30}
        renderer = stack.enter_context(patch('motif_frame_render.render', side_effect=render))
        finish = stack.enter_context(patch('motif_finish.apply'))
        stack.enter_context(patch('motif_direct.model_call', side_effect=AssertionError('model service forbidden')))
        return prepare, compile_mock, snapshots, renderer, finish

    def test_normal_run_and_allow_draft_do_not_bypass_structure(self):
        with patch('motif_reel.prepare') as prepare, patch('motif_reel.voice') as voice:
            with self.assertRaisesRegex(reel.ReelFailure, 'film_structure'):
                reel.run(self.brief, self.root / 'out', allow_draft=True)
            prepare.assert_not_called();voice.assert_not_called()
        self.assertEqual(self.record()['status'], 'BLOCKED')
        self.assertEqual(self.record()['failure']['stage'], 'production-boundary')
        self.assertFalse(self.record()['film_approved'])

    def test_unknown_rig_writes_failure_and_library_requests_before_voice(self):
        b = copy.deepcopy(BRIEF);b['beats'][0]['visual']['rig'] = 'rocket-launch'
        self.brief.write_text(json.dumps(b))
        with patch('motif_reel.prepare') as prepare, patch('motif_reel.voice') as voice:
            with self.assertRaisesRegex(reel.ReelFailure, 'library_request'):reel.run(self.brief, self.root / 'out')
            prepare.assert_not_called();voice.assert_not_called()
        self.assertEqual(self.record()['failure']['stage'], 'plan')
        self.assertEqual(json.loads((self.project / 'library-requests.json').read_text())[0]['id'], 'rocket-launch')

    def test_rough_pacing_failure_stops_before_snapshot_finish_render(self):
        with ExitStack() as stack:
            _, _, snapshots, renderer, finish = self.mocks(stack, rough=FAIL)
            with self.assertRaisesRegex(reel.ReelFailure, 'rough'):reel.run(self.brief, self.root / 'out', local_draft=True, render=True)
            snapshots.assert_not_called();renderer.assert_not_called();finish.assert_not_called()
        self.assertEqual(self.record()['status'], 'BLOCKED')
        self.assertEqual(self.record()['stages'][-1]['pacing'], FAIL)

    def test_empty_field_failure_stops_finish_render(self):
        with ExitStack() as stack:
            _, _, _, renderer, finish = self.mocks(stack, empty=FAIL)
            with self.assertRaisesRegex(reel.ReelFailure, 'rough'):reel.run(self.brief, self.root / 'out', local_draft=True, render=True)
            renderer.assert_not_called();finish.assert_not_called()
        self.assertEqual(self.record()['status'], 'BLOCKED')

    def test_final_pacing_failure_stops_render(self):
        with ExitStack() as stack:
            _, _, _, renderer, _ = self.mocks(stack, gate=FAIL)
            with self.assertRaisesRegex(reel.ReelFailure, 'gate'):reel.run(self.brief, self.root / 'out', local_draft=True, render=True, finish=False)
            renderer.assert_not_called()
        self.assertEqual(self.record()['status'], 'BLOCKED')
        self.assertFalse(any(s['stage'] == 'render' for s in self.record()['stages']))

    def test_provenance_failure_stops_render(self):
        with ExitStack() as stack:
            _, _, _, renderer, _ = self.mocks(stack, origin={**ORIGIN, 'status': 'FAIL', 'unknown': ['assets/x.png']})
            with self.assertRaisesRegex(reel.ReelFailure, 'gate'):reel.run(self.brief, self.root / 'out', local_draft=True, render=True, finish=False)
            renderer.assert_not_called()
        self.assertEqual(self.record()['failure']['stage'], 'gate')

    def test_local_draft_keeps_reviews_unperformed_and_capture_bound(self):
        with ExitStack() as stack:
            self.mocks(stack)
            record = reel.run(self.brief, self.root / 'out', local_draft=True, finish=False, render=True)
        self.assertEqual(record['status'], 'DRAFT_REVIEW_REQUIRED')
        critics = next(s for s in record['stages'] if s['stage'] == 'critics')
        self.assertEqual(set(critics['reviews'].values()), {'NOT_PERFORMED'})
        self.assertEqual(json.loads((self.project / 'production-scope.json').read_text())['actual_mode'], 'technical-fixture')
        require_capture(self.project, artifacts=[self.project / 'renders/review.mp4'])
        (self.project / 'assets/unit.txt').write_text('CHANGED')
        with self.assertRaisesRegex(ValueError, 'resource missing or changed'):require_capture(self.project)

    def test_cli_failure_has_nonzero_exit_and_receipt(self):
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/motif_reel.py'), 'run', '--brief', str(self.brief), '--out', str(self.root / 'out')], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Reel blocked:', result.stderr)
        self.assertEqual(self.record()['status'], 'BLOCKED')

    def test_production_check_uses_existing_interfaces_in_order(self):
        order = []
        with patch('motif_evidence.require_scope', return_value={'actual_mode': 'original-film'}), \
             patch('motif_structure.require_structure', side_effect=lambda p: order.append('structure')), \
             patch('motif_evidence.evidence_inputs', side_effect=lambda p: order.append('causal')), \
             patch('motif_evidence.require_capture', side_effect=lambda p: order.append('capture')), \
             patch('motif_quality.require_gate', side_effect=lambda p, phase: order.append(phase)):
            reel.check_production(self.project, 'final')
        self.assertEqual(order, ['structure', 'causal', 'capture', 'final'])

    def test_production_check_rejects_technical_fixture(self):
        with patch('motif_evidence.require_scope', return_value={'actual_mode': 'technical-fixture'}), patch('motif_quality.require_gate') as gate:
            with self.assertRaisesRegex(ValueError, 'film project'):reel.check_production(self.project)
            gate.assert_not_called()


class EncoderSafetyTests(unittest.TestCase):
    def test_nonzero_encoder_exit_is_rejected_even_with_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'unit.bin';output.write_bytes(b'UNIT_ONLY')
            encoder = Mock();encoder.args = ['ffmpeg', 'UNIT'];encoder.wait.return_value = 7
            with self.assertRaises(subprocess.CalledProcessError):finish_encoder(encoder, 30, 30, output)
            encoder.wait.assert_called_once()

    def test_incomplete_frame_count_and_missing_output_are_rejected(self):
        encoder = Mock();encoder.wait.return_value = 0
        with self.assertRaisesRegex(ValueError, 'capture incomplete'):finish_encoder(encoder, 30, 29, Path('/UNIT_MISSING'))
        with self.assertRaisesRegex(ValueError, 'no video'):finish_encoder(encoder, 30, 30, Path('/UNIT_MISSING'))


if __name__ == '__main__':unittest.main()
