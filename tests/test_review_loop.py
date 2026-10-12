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


class AgentScreenTests(unittest.TestCase):
    def test_cli_screen_prints_the_agent_and_its_cards(self):
        rig = motif_rigs.get('app-screen')
        v = {'device': 'laptop', 'ui': 'cli', 'title': 'claude', 'logo': 'claude', 'lines': ['> plan it', '* Write(PLAN.md)', '- 4 steps'], 'cards': ['PLAN.MD']}
        text = rig.printed_text(rig.params(v))
        for word in ('Claude Code', 'PLAN.MD', '> plan it'):self.assertIn(word, text)
        svg = rig.render(v, ('run', 1.0))
        self.assertIn('Claude Code', svg);self.assertIn('PLAN.MD', svg)

    def test_cli_session_draws_every_line_kind_and_scrolls(self):
        rig = motif_rigs.get('app-screen')
        v = {'device': 'laptop', 'ui': 'cli', 'logo': 'openai', 'agent': 'GPT-6 Astra', 'cwd': '~/my-app',
             'lines': ['> audit PLAN.md', '* Read(PLAN.md)', '- 4 steps', '[x] Schema', '[ ] Tests', 'x old route', '+ new route', '- No tests', '- No auth', '- No limit', '? Send 3 gaps back?']}
        early, late = rig.render(v, ('run', .1)), rig.render(v, ('run', 1.0))
        self.assertIn('Thinking', early);self.assertNotIn('Thinking', late)
        self.assertIn('clip-path', late);self.assertIn('1. Yes', late);self.assertIn('98% context left', late)
        self.assertRegex(late, r'translate\(0 -[1-9]')  # the long session has scrolled

    def test_pull_request_turns_merged_at_the_result(self):
        rig = motif_rigs.get('app-screen')
        v = {'device': 'monitor', 'ui': 'pr', 'title': 'Pull request #42', 'lines': ['Add login API', '✓ Plan audited', 'x Lint', '@astra: holds up'], 'result': 'MERGED'}
        self.assertIn('Open', rig.render(v, ('run', .1)));late = rig.render(v, ('run', 1.0))
        self.assertIn('Merged', late);self.assertIn('holds up', late);self.assertIn('Files changed', late)

    def test_files_pane_opens_the_last_file(self):
        rig = motif_rigs.get('app-screen')
        v = {'device': 'monitor', 'ui': 'files', 'lines': ['app/', '  SKILL.md'], 'pane': ['name: claudex', '# Claudex']}
        svg = rig.render(v, ('run', 1.0))
        self.assertGreaterEqual(svg.count('SKILL.md'), 2);self.assertIn('claudex', svg)
        self.assertIn('# Claudex', rig.printed_text(rig.params(v)))

    def test_terminal_marks_commands_and_keeps_lines_above_the_key(self):
        rig = motif_rigs.get('app-screen')
        v = {'device': 'monitor', 'ui': 'terminal', 'lines': ['$ uv init app', 'Initialized', '$ uv add rich', 'Resolved 6', 'Prepared 5', 'Installed 5', ' + rich', ' + pygments']}
        svg = rig.render(v, ('run', 1.0))
        self.assertIn('>$<', svg)
        import re
        bottom = max(float(y_) for y_, word in re.findall(r'<text x="[\d.-]+" y="([\d.-]+)"[^>]*>([^<]*)<', svg) if word not in ('RUN', 'DONE'))
        self.assertLess(bottom, rig.button(rig.params(v))[1] - 22)

    def test_result_chip_never_takes_the_ink_colour(self):
        # Claudex cut 6: sunflower's pop is its ink, so SKILL ADDED printed black on black.
        rig = motif_rigs.get('app-screen')
        svg = rig.render({'device': 'monitor', 'ui': 'files', 'lines': ['a/', '  b.md'], 'result': 'ADDED'}, ('run', 1.0), 'sunflower')
        self.assertNotIn('rx="14" fill="#141414" stroke', svg)

    def test_host_carries_the_sheet_in_the_loop(self):
        rig = motif_rigs.get('review-loop')
        xs = [rig.host_track(rig.params({'mode': 'loop'}), ('run', t))[0] for t in (.05, .2, .35)]
        self.assertGreater(max(xs) - min(xs), 100)
        self.assertIsNone(rig.host_track(rig.params({'mode': 'audit'}), ('run', .3)))

