import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1];sys.path.insert(0, str(ROOT / 'scripts'))

import motif_narration as mn

BRIEF = json.loads((ROOT / 'tests/fixtures/reel-brief-fixture.json').read_text())


def with_line(text, beat=0):
    b = copy.deepcopy(BRIEF);b['beats'][beat]['narration'] = text
    return b


class NarrationVoiceTests(unittest.TestCase):
    def test_fixture_passes(self):
        self.assertEqual(mn.lint(BRIEF)['status'], 'PASS')

    def test_stated_moral_fails(self):
        report = mn.lint(with_line("That's why 5 billion passkeys are already in use."))
        self.assertEqual(report['status'], 'FAIL');self.assertIn('moral', report['failures'][0])

    def test_not_x_its_y_fails(self):
        self.assertEqual(mn.lint(with_line("It's not a notes app, it's a second brain with 12 pages."))['status'], 'FAIL')

    def test_stock_words_and_dashes_fail(self):
        self.assertEqual(mn.lint(with_line('Sync your 12 notes seamlessly.'))['status'], 'FAIL')
        self.assertEqual(mn.lint(with_line('Sync 12 notes — free.'))['status'], 'FAIL')

    def test_vague_line_and_filler_only_warn(self):
        report = mn.lint(with_line('They go back and forth until it actually holds up.'))
        self.assertEqual(report['status'], 'PASS')
        self.assertTrue(any('filler "actually"' in w for w in report['warnings']))
        self.assertTrue(any('no number, name or command' in w for w in report['warnings']))

    def test_names_numbers_and_commands_are_specific(self):
        for line in ['Then GPT-6 audits it.', 'Open notes.md and find the line.', 'It keeps entries for ninety days.']:
            where = BRIEF['beats'][0]['id'] + ':'
            self.assertFalse(any(w.startswith(where) and 'no number' in w for w in mn.lint(with_line(line))['warnings']), line)

    def test_every_repo_brief_passes(self):
        for path in sorted((ROOT / 'quality').glob('*-briefs/*.json')):
            self.assertEqual(mn.lint(json.loads(path.read_text()))['failures'], [], path.name)


if __name__ == '__main__':
    unittest.main()
