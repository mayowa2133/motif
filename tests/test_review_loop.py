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
        self.assertEqual(plan['beats'][0]['shots'][0]['rig']['params']['mode'], 'solo')


    def test_setup_eases_in_on_the_acting_station(self):
        rig = motif_rigs.get('review-loop')
        for mode in ('audit', 'build'):
            p = rig.params({'mode': mode});x, y = rig.focus(p, 'setup')
            fx, fy, fw, fh = rig.footprint
            self.assertTrue(fx <= x <= fx + fw and fy <= y <= fy + fh, mode)
            self.assertIsNone(rig.focus(p, 'payoff'))
        self.assertIsNone(rig.focus(rig.params({'mode': 'loop'}), 'setup'))

    def test_hook_can_drop_the_product_badge(self):
        from motif_reel import plan_reel
        plan = plan_reel(BRIEF, allow_draft=True)
        self.assertIsNone(plan['beats'][0]['shots'][0]['brand'])


class CheckTests(unittest.TestCase):
    def test_check_sees_the_hook_second_headline(self):
        # Claudex brief: check passed, then run failed L010 because the hook's second headline was only split after voicing.
        from motif_reel import check_brief
        self.assertEqual(check_brief(BRIEF, True)['status'], 'PASS')
        bad = json.loads(json.dumps(BRIEF));bad['hook']['headline_b'] = 'AI MISSED 3 BUGS'
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


class ApprovedLookTests(unittest.TestCase):
    def test_every_look_keeps_the_approved_base(self):
        # Claudex cut 1: primary-pop's wipes and snap zooms came back because the approved styles lived in one look.
        import motif_looks
        for look in motif_looks.LOOKS:self.assertEqual(motif_looks.unapproved(look), [], look)

    def test_a_rejected_style_fails_the_gate(self):
        import motif_looks
        from motif_lessons import check_approved_look
        saved = motif_looks.LOOKS['primary-pop']
        try:
            motif_looks.LOOKS['primary-pop'] = {**saved, 'camera': 'snap', 'transition': 'wipe'}
            self.assertEqual(len(check_approved_look(None, {'look': 'primary-pop'}, {})), 2)
        finally:
            motif_looks.LOOKS['primary-pop'] = saved

    def test_every_look_gets_the_paper_finish(self):
        import tempfile
        import motif_looks
        with tempfile.TemporaryDirectory() as tmp:
            for look in motif_looks.LOOKS:
                style = json.loads(motif_looks.finish_style(look, Path(tmp) / f'{look}.json').read_text())
                self.assertEqual(style['materials']['overlay'], 'motif-v1-1024/crumpled', look)
