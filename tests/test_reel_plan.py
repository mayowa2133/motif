import copy
import json
import sys
import unittest
from unittest import mock
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1];sys.path.insert(0, str(ROOT / 'scripts'))

import motif_reel as reel
from motif_library import catalog, retrieve

BRIEF = json.loads((ROOT / 'tests/fixtures/reel-brief-fixture.json').read_text())


class PlanTests(unittest.TestCase):
    def test_fixture_plan_is_valid_and_deterministic(self):
        plan = reel.plan_reel(BRIEF, allow_draft=True)
        self.assertEqual(reel.validate_plan(plan, True), ([], []))
        self.assertEqual(plan, reel.plan_reel(BRIEF, allow_draft=True))
        self.assertEqual([b['kind'] for b in plan['beats']], ['hook'] + ['claim'] * 5 + ['cta'])

    def test_unknown_rig_fails_with_library_request(self):
        plan = reel.plan_reel(BRIEF, allow_draft=True);plan['beats'][1]['shots'][0]['rig']['id'] = 'rocket-launch'
        errors, requests = reel.validate_plan(plan, True)
        self.assertTrue(errors);self.assertEqual(requests[0], {'kind': 'rig', 'id': 'rocket-launch', 'needed_by': plan['beats'][1]['shots'][0]['id']})

    def test_drafts_are_not_offered_without_approval(self):
        plan = reel.plan_reel(BRIEF, allow_draft=True)
        with mock.patch('motif_library.approvals', return_value={'entries': {}}):
            errors, requests = reel.validate_plan(plan, allow_draft=False)
        self.assertTrue(errors and requests)

    def test_approved_library_needs_no_draft_flag(self):
        self.assertEqual(reel.validate_plan(reel.plan_reel(BRIEF), allow_draft=False), ([], []))

    def test_bad_rig_params_fail(self):
        plan = reel.plan_reel(BRIEF, allow_draft=True);plan['beats'][1]['shots'][0]['rig']['params'] = {'label': 'X' * 40}
        errors, _ = reel.validate_plan(plan, True)
        self.assertTrue(any('params' in e for e in errors))

    def test_neighbouring_beats_change_palette_and_room(self):
        plan = reel.plan_reel(BRIEF, allow_draft=True)
        palettes = [b['palette'] for b in plan['beats']];rooms = [b['shots'][0]['room'] for b in plan['beats']]
        self.assertTrue(all(a != b for a, b in zip(palettes, palettes[1:])))
        self.assertTrue(all(a != b for a, b in zip(rooms, rooms[1:])))

    def test_default_labels_are_flagged(self):
        b = copy.deepcopy(BRIEF)
        for beat in b['beats']:beat.pop('visual')
        plan = reel.plan_reel(b, allow_draft=True)
        self.assertTrue(plan['warnings'])

    def test_retrieval_uses_tags(self):
        cat = catalog(True)
        self.assertEqual(retrieve(cat, 'monthly subscription bills pile up', 'rig', 1)[0]['id'], 'receipt-stack')
        self.assertEqual(retrieve(cat, 'servers in the cloud', 'room', 1)[0]['id'], 'server-room')

    def test_headlines_never_end_on_filler(self):
        self.assertEqual(reel._short('The notes app is free and', 26), 'NOTES APP IS FREE')
        self.assertNotIn(reel._short('syncs notes across every device you own', 22).split()[-1], reel.EDGE_WORDS)


class ScheduleTests(unittest.TestCase):
    def test_shots_tile_the_timeline(self):
        plan = reel.plan_reel(BRIEF, allow_draft=True);ids = [b['id'] for b in plan['beats']]
        spans = [(i, k * 4.0, k * 4.0 + 3.6) for k, i in enumerate(ids)]
        shots = reel.schedule(plan, spans, spans[-1][2])
        frames = [(s['start_frame'], s['frames']) for s in shots]
        self.assertEqual(frames[0][0], 0)
        self.assertTrue(all(a[0] + a[1] == b[0] for a, b in zip(frames, frames[1:])))
        self.assertEqual(len(shots), 12)


if __name__ == '__main__':
    unittest.main()
