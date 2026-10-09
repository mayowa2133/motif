"""Synthetic contract inputs only: these tests do not watch films or judge art."""
import copy
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from motif_evidence import declare, require_scope, completion, technical_coverage, write, sha
from motif_causal import validate_map, coverage, verify_coverage, freeze_study, playback_counts, QUESTIONS


def causal_map():
    return {'propositions': [{'id': 'pending', 'word_range': [0, 3], 'text': 'Wait for input',
            'shot_id': 'wait', 'subject': 'worker', 'initiator': 'requester', 'stimulus': 'external request',
            'action': 'stop', 'before': 'working', 'after': 'pending',
            'persistent_result': 'pending work retained', 'diagnostic_feature': 'stationary work object',
            'review_interval': [0, 29], 'stimulus_frame': 3, 'action_frame': 4, 'persistent_until_frame': 29,
            'claim': {'status': 'illustrative'}}]}


class ScopeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.p = Path(self.tmp.name)
        write(self.p / 'brief.json', {'script': 'Wait for input'})
        write(self.p / 'production-plan.json', {'quality_mode': 'motif-gold-v1'})

    def test_missing_mode_and_substitution_rejected(self):
        with self.assertRaisesRegex(ValueError, 'missing'): require_scope(self.p)
        for mode in (None, '', 'unknown'):
            with self.assertRaises(ValueError): declare(self.p, mode, 'unit')
        with self.assertRaisesRegex(ValueError, 'substituted'):
            declare(self.p, 'faithful-editable', 'unit', 'raster-animatic')

    def test_scope_freshness_and_explicit_legacy(self):
        declare(self.p, 'original-film', 'unit')
        write(self.p / 'production-plan.json', {})
        with self.assertRaisesRegex(ValueError, 'Gold'): require_scope(self.p)
        write(self.p / 'production-plan.json', {'quality_mode': 'motif-gold-v1'})
        write(self.p / 'brief.json', {'changed': True})
        with self.assertRaisesRegex(ValueError, 'brief changed'): require_scope(self.p)

    def test_output_never_infers_playback_or_film_approval(self):
        for mode in ('technical-fixture', 'original-film'):
            (self.p / 'production-scope.json').unlink(missing_ok=True)
            declare(self.p, mode, 'unit')
            artifact = self.p / 'unit.bin'; artifact.write_bytes(b'UNIT_ONLY')
            r = completion(self.p, artifact)
            self.assertFalse(r['film_approved'])
            self.assertEqual(set(r['dimensions'].values()), {'UNASSESSED'})
            self.assertEqual(r['artifact_sha256'], sha(artifact))

    def test_disabled_and_empty_coverage_never_pass(self):
        valid = {'coverage': {'enabled': True, 'required': 2, 'checked': 2, 'scope': 'UNIT'}}
        technical_coverage('caption-overflow', valid)
        for change in ({'required': 0}, {'checked': 0}, {'checked': 1}, {'enabled': False}, {'checked': True}):
            r = copy.deepcopy(valid); r['coverage'].update(change)
            with self.assertRaises(ValueError): technical_coverage('caption-overflow', r)


class CausalTests(unittest.TestCase):
    def test_exact_proposition_scope_and_cause_order(self):
        self.assertEqual(validate_map(causal_map(), 'Wait for input', 30)['semantic_perception'], 'UNASSESSED')
        for field, value in [('text', 'Go now'), ('stimulus_frame', 5), ('persistent_result', ''), ('review_interval', [0, 30])]:
            m = causal_map(); m['propositions'][0][field] = value
            with self.assertRaises(ValueError): validate_map(m, 'Wait for input', 30)

    def test_fact_support_needs_provenance_and_is_not_fact_checking(self):
        m = causal_map(); m['propositions'][0]['claim'] = {'status': 'supported'}
        with self.assertRaisesRegex(ValueError, 'attribution'): validate_map(m, 'Wait for input', 30)
        m['propositions'][0]['claim'].update(source='UNIT', as_of='2026-10-09', excerpt='UNIT', uncertainty='UNIT')
        self.assertEqual(validate_map(m, 'Wait for input', 30)['factual_truth'], 'UNASSESSED')

    def test_full_inclusive_interval_not_contact_point(self):
        required = coverage([{'id': 'wait', 'critical_intervals': [[3, 9], [15, 18]]}], 30, ['wait'])
        verify_coverage(required, {'wait': list(range(3, 10)) + list(range(15, 19))})
        for actual in ({'wait': [6, 17]}, {}, {'wait': list(range(3, 10))}):
            with self.assertRaises(ValueError): verify_coverage(required, actual)
        with self.assertRaises(ValueError): coverage([{'id': 'other', 'critical_intervals': [[0, 2]]}], 30, ['wait'])

    def test_stills_cannot_be_submitted_as_playback(self):
        records = [{'viewer': str(i), 'viewer_is_author': False, 'artifact_sha256': 'UNIT',
                    'protocol_sha256': 'PROTO', 'method': 'human-normal-speed-playback',
                    'speed': 1, 'first_exposure': True, 'producer_rationale_shown': False,
                    'observation': 'UNIT ONLY', 'correct': dict.fromkeys(QUESTIONS, True)} for i in range(5)]
        self.assertTrue(playback_counts(records, 'UNIT', 'PROTO')['proposed_floor_met'])
        for field, value in [('method', 'stills'), ('speed', .5), ('artifact_sha256', 'STALE'), ('first_exposure', False), ('viewer_is_author', True)]:
            changed = copy.deepcopy(records); changed[0][field] = value
            with self.assertRaises(ValueError): playback_counts(changed, 'UNIT', 'PROTO')

    def test_unfamiliar_study_requires_frozen_actual_inputs(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d); component = p / 'component'; component.write_bytes(b'UNIT')
            pair = {'script': 'UNIT', 'style': 'UNIT', 'mode': 'technical-fixture', 'audio': 'UNIT',
                    'geometry': [360,640], 'unfamiliar_to_author_attestation': 'UNIT',
                    'baseline': {'components': {str(component): sha(component)}},
                    'candidate': {'components': {str(component): sha(component)}}}
            pairs = [dict(pair, id=str(i)) for i in range(4)]
            protocol = {'author_minutes_ceiling': 10, 'randomization_seed': 42}
            r = freeze_study(p / 'study', protocol, pairs)
            self.assertEqual(r['normal_speed'], 'UNASSESSED')
            with self.assertRaisesRegex(ValueError, 'exists'): freeze_study(p / 'study', protocol, pairs)
            component.write_bytes(b'CHANGED')
            with self.assertRaisesRegex(ValueError, 'hash'): freeze_study(p / 'changed', protocol, pairs)


if __name__ == '__main__': unittest.main()
