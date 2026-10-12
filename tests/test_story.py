import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1];sys.path.insert(0, str(ROOT / 'scripts'))

import motif_reel_script as rs
import motif_story as st

BRIEF = json.loads((ROOT / 'tests/fixtures/reel-brief-fixture.json').read_text())


def storied():
    b = copy.deepcopy(BRIEF)
    b['story'] = {'premises': ['a pricey notebook', 'a notebook that pays its owner', 'a free notebook that sorts itself'], 'chosen': 2,
                  'object': 'the notebook', 'ending': 'the sorted notebook stamped YOUR NOTES'}
    b['hook'] = {**b.get('hook', {}), 'story': {'promise': 'a free notes app that beats paid ones', 'sets_up': ['free']}}
    rows = [('demonstrate', 'therefore', 'one star', '12 github stars', [], ['stars']),
            ('complicate', 'but', 'no bills', '$10 every month', ['stars'], ['bill']),
            ('reveal', 'but', 'a paid plan', 'free sync crushes the paid plan', ['bill'], []),
            ('demonstrate', 'therefore', 'a messy pile', 'notes sorted into folders', [], []),
            ('resolve', 'therefore', 'unchecked notes', 'your notes reviewed', ['free'], [])]
    for beat, (purpose, link, before, after, pays, sets) in zip(b['beats'], rows):
        beat['story'] = {'purpose': purpose, 'link': link, 'before': before, 'after': after, 'action': 'the host acts', 'pays_off': pays, 'sets_up': sets}
    b['beats'][-1]['story']['line_job'] = 'land'
    return b


class StoryPassTests(unittest.TestCase):
    def test_briefs_without_story_are_not_judged(self):
        self.assertEqual(st.check(BRIEF)['status'], 'NOT_USED')

    def test_storied_fixture_passes_schema_and_check(self):
        b = storied();self.assertEqual(rs.validate(b), [])
        report = st.check(b);self.assertEqual(report['status'], 'PASS', report)

    def test_beat_without_story_fails(self):
        b = storied();del b['beats'][1]['story']
        self.assertIn('cost', ' '.join(st.check(b)['failures']))

    def test_and_then_link_is_not_allowed(self):
        b = storied();b['beats'][1]['story']['link'] = 'and then'
        self.assertTrue(rs.validate(b))

    def test_after_state_must_be_on_screen(self):
        b = storied();b['beats'][3]['story']['after'] = 'a happy owner'
        self.assertTrue(any('sort' in f and 'on screen' in f for f in st.check(b)['failures']))

    def test_no_change_fails(self):
        b = storied();b['beats'][3]['story']['before'] = 'notes sorted into folders'
        self.assertTrue(any('nothing changes' in f for f in st.check(b)['failures']))

    def test_a_list_without_complication_fails(self):
        b = storied()
        for beat in b['beats']:beat['story']['link'] = 'therefore';beat['story']['purpose'] = 'demonstrate' if beat is not b['beats'][-1] else 'resolve'
        self.assertTrue(any('list, not a story' in f for f in st.check(b)['failures']))

    def test_ledger_needs_payoffs(self):
        b = storied();b['beats'][2]['story']['pays_off'] = []
        self.assertTrue(any('"bill"' in f and 'no later beat' in f for f in st.check(b)['failures']))
        b = storied();b['beats'][0]['story']['pays_off'] = ['ghost']
        self.assertTrue(any('ghost' in f for f in st.check(b)['failures']))
        b = storied();b['beats'][-1]['story']['pays_off'] = [];b['beats'][2]['story']['pays_off'] = ['bill', 'free']
        self.assertTrue(any('hook promised' in f for f in st.check(b)['failures']))

    def test_ending_must_reveal_or_resolve(self):
        b = storied();b['beats'][-1]['story']['purpose'] = 'demonstrate'
        self.assertTrue(any('last beat' in f for f in st.check(b)['failures']))

    def test_premises_must_differ(self):
        b = storied();b['story']['premises'] = ['same idea'] * 3
        self.assertTrue(any('repeat' in f for f in st.check(b)['failures']))


if __name__ == '__main__':
    unittest.main()
