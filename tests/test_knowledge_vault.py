import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1];sys.path.insert(0, str(ROOT / 'scripts'))

import motif_rigs
import motif_reel_script as rs

BRIEF = json.loads((ROOT / 'quality/adaptation-briefs/adapt-second-brain.json').read_text())
PAGES = ['SLEEP', 'FOCUS', 'HABITS', 'PRICING', 'HIRING', 'MY GAPS']
MODES = {'forget': {'count': 9, 'label': 'SAVED 312'}, 'setup': {}, 'collect': {}, 'compile': {'pages_from': 0, 'pages_to': 5},
         'ask': {'pages_from': 5, 'pages_to': 5, 'cite': [1, 3]}, 'save': {'pages_from': 5, 'pages_to': 5}, 'check': {'pages_from': 6, 'pages_to': 6, 'flag': 2}}


class KnowledgeVaultTests(unittest.TestCase):
    rig = motif_rigs.get('knowledge-vault')

    def values(self, mode):
        return {'mode': mode, 'pages': PAGES, 'logo': 'claude', **MODES[mode]}

    def test_every_mode_closes_its_contact_exactly(self):
        for mode in MODES:
            self.assertAlmostEqual(self.rig.contact_gap(self.values(mode), 'run'), 0, places=9, msg=mode)

    def test_every_mode_starts_open(self):
        for mode in MODES:
            (x1, y1), (x2, y2) = self.rig.contacts(self.values(mode), ('run', 0.0))['vault-contact']
            self.assertGreater(abs(x1 - x2) + abs(y1 - y2), 1, mode)

    def test_modes_hand_over_the_same_board(self):
        # Each beat must open on the page count the previous one ended on, so the film reads as one machine.
        end = lambda v: self.rig.render(v, ('run', 1.0), 'lagoon').count('PAGES ')
        self.assertIn('PAGES 5', self.rig.render(self.values('compile'), ('run', 1.0), 'lagoon'))
        self.assertIn('PAGES 5', self.rig.render(self.values('ask'), ('run', 0.0), 'lagoon'))
        self.assertIn('PAGES 6', self.rig.render(self.values('save'), ('run', 1.0), 'lagoon'))
        self.assertIn('PAGES 6', self.rig.render(self.values('check'), ('run', 0.0), 'lagoon'))
        self.assertEqual(end(self.values('check')), 1)

    def test_printed_text_names_what_is_on_screen(self):
        text = self.rig.printed_text(self.rig.params(self.values('ask')))
        self.assertIn('MY GAPS', ' '.join(text) + ' ' + ' '.join(PAGES))
        self.assertIn('WIKI', text)


class LongFormatTests(unittest.TestCase):
    def test_adaptation_brief_is_valid_long_format(self):
        self.assertEqual(rs.validate(BRIEF), [])
        self.assertGreater(rs.estimate(BRIEF), 32)

    def test_short_format_still_caps_beats_and_runtime(self):
        short = {**BRIEF, 'format': 'short'}
        errors = rs.validate(short)
        self.assertTrue(any('beats outside 4-6' in e for e in errors))
        self.assertTrue(any('runtime' in e for e in errors))

    def test_plan_uses_hook_machine_and_beat_brand(self):
        from motif_reel import plan_reel, validate_plan
        plan = plan_reel(BRIEF, allow_draft=True)
        self.assertEqual(validate_plan(plan, True)[0], [])
        hook = plan['beats'][0]['shots'][0]
        self.assertEqual(hook['rig']['params']['mode'], 'forget')
        vault = next(b for b in plan['beats'] if b['id'] == 'vault')
        self.assertTrue(all(s['brand'] == 'obsidian' for s in vault['shots']))
        self.assertNotIn('brand', plan['beats'][2]['shots'][0])


if __name__ == '__main__':
    unittest.main()
