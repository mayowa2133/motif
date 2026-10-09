import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1];sys.path.insert(0, str(ROOT / 'scripts'))

import motif_reel_script as rs

BRIEF = json.loads((ROOT / 'tests/fixtures/reel-brief-fixture.json').read_text())


class ReelScriptTests(unittest.TestCase):
    def test_fixture_is_valid(self):
        self.assertEqual(rs.validate(BRIEF), [])

    def test_missing_citation_rejected(self):
        b = copy.deepcopy(BRIEF);del b['facts'][0]['source_url']
        self.assertTrue(rs.validate(b))
        b = copy.deepcopy(BRIEF);b['beats'][0]['fact'] = 'nope'
        self.assertTrue(any('unknown fact' in e for e in rs.validate(b)))
        b = copy.deepcopy(BRIEF);b['facts'][0]['source_url'] = 'a blog post'
        self.assertTrue(rs.validate(b))

    def test_runtime_over_32s_rejected(self):
        b = copy.deepcopy(BRIEF);b['beats'][0]['narration'] = ' '.join(['word'] * 80)
        self.assertTrue(any('runtime' in e for e in rs.validate(b)))
        self.assertTrue(any('runtime' in e for e in rs.validate(BRIEF, measured=33.0)))

    def test_three_hooks_and_beat_count(self):
        self.assertEqual(len(rs.hooks(BRIEF)), 3)
        b = copy.deepcopy(BRIEF);b['beats'] = b['beats'][:3]
        self.assertTrue(rs.validate(b))

    def test_cta_must_say_keyword(self):
        b = copy.deepcopy(BRIEF);b['cta']['narration'] = 'Follow for more.'
        self.assertTrue(any('keyword' in e for e in rs.validate(b)))


if __name__ == '__main__':
    unittest.main()
