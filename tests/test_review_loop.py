import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1];sys.path.insert(0, str(ROOT / 'scripts'))

import motif_rigs

BRIEF = json.loads((ROOT / 'quality/adaptation-briefs/adapt-claudex.json').read_text())
BASE = {'steps': ['SCHEMA', 'LOGIN', 'API', 'TESTS'], 'left': 'CLAUDE', 'right': 'ASTRA', 'left_logo': 'claude', 'right_logo': 'openai',
        'gaps': ['NO TESTS', 'AUTH?', 'RATE LIMIT'], 'banner': '2 JUDGES'}
MODES = ('solo', 'plan', 'audit', 'loop', 'swap', 'build', 'ship')


class ReviewLoopTests(unittest.TestCase):
    rig = motif_rigs.get('review-loop')

    def values(self, mode, **extra):
        return {**BASE, 'mode': mode, **extra}

    def test_every_mode_closes_its_contact_exactly(self):
        for mode in MODES:
            for steps in (['A', 'B'], BASE['steps'], ['A', 'B', 'C', 'D', 'E']):
                self.assertAlmostEqual(self.rig.contact_gap(self.values(mode, steps=steps), 'run'), 0, places=9, msg=(mode, len(steps)))

    def test_every_mode_starts_open(self):
        for mode in MODES:
            (x1, y1), (x2, y2) = self.rig.contacts(self.values(mode), ('run', 0.0))['loop-contact']
            self.assertGreater(abs(x1 - x2) + abs(y1 - y2), 1, mode)

    def test_loop_fixes_every_gap_and_counts_rounds(self):
        for rounds in (2, 3, 4):
            v = self.rig.params(self.values('loop', rounds=rounds))
            _, remaining, rnd, _, _ = self.rig.loop_state(v, 0.0)
            self.assertEqual((remaining, rnd), (3, 1))
            _, remaining, rnd, _, _ = self.rig.loop_state(v, 1.0)
            self.assertEqual((remaining, rnd), (0, rounds))
        self.assertIn(f'ROUND 3', self.rig.render(self.values('loop'), ('run', 1.0)))

    def test_modes_hand_over_the_same_sheet(self):
        # The audit opens on the sheet where the plan landed; the swap opens on the stamped sheet the loop ended on.
        v = self.values('plan');self.assertEqual(self.rig.contacts(v, ('run', 1.0))['loop-contact'][1], self.rig.sheet_at(1))
        self.assertIn('HOLDS UP', self.rig.render(self.values('loop'), ('run', 1.0)))
        self.assertIn('HOLDS UP', self.rig.render(self.values('swap'), ('run', 0.0)))
        self.assertIn('BUILDS', self.rig.render(self.values('build'), ('run', 0.0)))

    def test_printed_text_names_what_is_on_screen(self):
        text = self.rig.printed_text(self.rig.params(self.values('audit')))
        for word in ('CLAUDE', 'ASTRA', 'NO TESTS', 'PLANS', 'AUDITS'):self.assertIn(word, text)
        self.assertIn('2 JUDGES', self.rig.printed_text(self.rig.params(self.values('ship'))))
        self.assertIsNone(self.rig.identity(self.rig.params(self.values('solo'))))

    def test_adaptation_brief_plans(self):
        from motif_reel import plan_reel, validate_plan
        plan = plan_reel(BRIEF, allow_draft=True)
        self.assertEqual(validate_plan(plan, True)[0], [])
        self.assertEqual(plan['beats'][0]['shots'][0]['rig']['params']['mode'], 'plan')


class CheckTests(unittest.TestCase):
    def test_check_sees_the_hook_second_headline(self):
        # Claudex brief: check passed, then run failed L010 because the hook's second headline was only split after voicing.
        from motif_reel import check_brief
        self.assertEqual(check_brief(BRIEF, True)['status'], 'PASS')
        bad = json.loads(json.dumps(BRIEF));bad['hook']['headline_b'] = '1 TASK, 2 MODELS'
        report = check_brief(bad, True)
        self.assertEqual(report['status'], 'FAIL')
        self.assertTrue(any(x.startswith('L010') for x in report['lessons']))

    def test_no_second_sticker_on_a_machine_that_draws_the_mark(self):
        from motif_reel import rig_shows_mark
        shot = {'rig': {'id': 'review-loop', 'params': {'left_logo': 'claude', 'right_logo': 'openai'}}}
        self.assertTrue(rig_shows_mark(shot, 'claude'))
        self.assertFalse(rig_shows_mark(shot, 'obsidian'))
        self.assertFalse(rig_shows_mark({'rig': None}, 'claude'))

    def test_cta_second_headline_cannot_repeat_comment(self):
        import motif_reel_script as rs
        bad = json.loads(json.dumps(BRIEF));bad['cta']['headline_b'] = 'COMMENT CLAUDEX'
        self.assertTrue(any('headline_b' in e for e in rs.validate(bad)))


class NumberTests(unittest.TestCase):
    def test_names_and_commas_are_not_numbers(self):
        # The Claudex brief (2026-10-11) crashed on "plan, then audit" and would have counted to 6 for "GPT-6 Astra".
        from motif_reel import _number
        self.assertIsNone(_number('plan, then audit'))
        self.assertIsNone(_number('GPT-6 Astra'))
        self.assertEqual(_number('$1,200')['value'], 1200)
        self.assertEqual(_number('90 days')['value'], 90)


if __name__ == '__main__':
    unittest.main()
