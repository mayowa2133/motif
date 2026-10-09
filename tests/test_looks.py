import json
import re
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

import motif_looks as looks
import motif_variety as variety
from motif_rigs.palettes import PALETTES, palette


def parses(markup):
    markup = re.sub(r' (data-[\w-]+)(?=[\s/>])', r' \1=""', markup)
    ET.fromstring(f'<svg xmlns="http://www.w3.org/2000/svg">{markup}</svg>')


class LookTests(unittest.TestCase):
    def test_looks_are_structurally_different(self):
        names = sorted(looks.LOOKS)
        for a in names:
            self.assertTrue(set(looks.LOOKS[a]['palettes']) <= set(PALETTES), a)
            for b in names:
                if a < b:
                    same = [k for k in looks.FEATURES if looks.LOOKS[a][k] == looks.LOOKS[b][k]]
                    self.assertLessEqual(len(same), 1, f'{a} and {b} share {same}')
                    self.assertFalse(set(looks.LOOKS[a]['palettes']) & set(looks.LOOKS[b]['palettes']), f'{a} and {b} share palettes')

    def test_scene_palettes_rotate_inside_the_family(self):
        for name, look in looks.LOOKS.items():
            order = looks.palettes(name, 7, seed=3)
            self.assertTrue(all(x != y for x, y in zip(order, order[1:])), name)
            self.assertTrue(set(order) <= set(look['palettes']))

    def test_headlines_captions_and_transitions_render(self):
        from fontTools.ttLib import TTFont
        fonts = {'serif': TTFont(ROOT / 'videos/productions/voicestudio-craft-v6/assets/fonts/EBGaramond-700.woff2'), 'sans': TTFont(ROOT / 'assets/fonts/Inter-900-latin.woff2')}
        groups = [{'start': 0, 'end': 2, 'words': [{'text': w, 'start': i * .2, 'end': i * .2 + .2} for i, w in enumerate(['Your', 'browser', 'runs', 'it'])]}]
        for name, look in looks.LOOKS.items():
            c = palette(look['palettes'][0])
            for f in (0, 3, 12):
                parses(looks.headline(look['headline'], 'A TRILLION DATABASES', c, f))
                parses(looks.captions(look['captions'], groups, 20 + f, fonts, look['caption_colours']))
                parses(looks.transition_in(look['transition'], f, look['transition_colour']) + looks.transition_out(look['transition'], f, 14, look['transition_colour']))
            self.assertIn('A TRILLION' if look['headline'] != 'tag' else 'TRILLION', looks.headline(look['headline'], 'A TRILLION DATABASES', c, 9))

    def test_choose_avoids_recent_looks(self):
        brief = {'slug': 'any-topic'};seen = []
        for _ in looks.LOOKS:seen.append(looks.choose(brief, seen))
        self.assertEqual(sorted(seen), sorted(looks.LOOKS))
        self.assertEqual(looks.choose({'slug': 'x', 'look': 'neon-arcade'}, ['neon-arcade']), 'neon-arcade')

    def test_finish_grade_keeps_approved_materials(self):
        import tempfile
        base = json.loads(looks.FINISH_V1.read_text())
        with tempfile.TemporaryDirectory() as tmp:
            style = json.loads(Path(looks.finish_style('neon-arcade', Path(tmp) / 's.json')).read_text())
        self.assertEqual(style['materials'], base['materials']);self.assertNotEqual(style['vignette'], base['vignette'])


class VarietyTests(unittest.TestCase):
    def film(self, slug, look, palettes, rooms, machines, colour=None):
        feats = variety.LEGACY_LOOK if look == 'legacy' else {k: looks.LOOKS[look][k] for k in variety.LOOK_FEATURES}
        return {'slug': slug, 'look': look, 'features': feats, 'palettes': palettes, 'rooms': rooms, 'machines': machines, 'colour': colour}

    def test_same_look_and_machines_fail(self):
        a = self.film('a', 'legacy', ['sunrise', 'berry'], ['office', 'diner'], ['thermometer', 'stamp-gate', 'balance-scale'])
        b = self.film('b', 'legacy', ['sunrise', 'berry'], ['office', 'street'], ['thermometer', 'stamp-gate', 'balance-scale'])
        result = variety.check([a, b]);self.assertEqual(result['status'], 'FAIL');self.assertEqual(len(result['failures']), 2)

    def test_different_looks_pass(self):
        a = self.film('a', 'neon-arcade', ['neon-violet'], ['arcade'], ['magnet-pull', 'thermometer'])
        b = self.film('b', 'great-outdoors', ['sky'], ['park'], ['bridge-span', 'thermometer'])
        self.assertEqual(variety.check([a, b])['status'], 'PASS')

    def test_benchmark_briefs_spread_looks_and_machines(self):
        briefs = [json.loads(p.read_text()) for p in sorted((ROOT / 'quality/benchmark-briefs').glob('*.json'))]
        self.assertEqual(len({b['look'] for b in briefs}), len(briefs))
        rigs = {b['slug']: {x['visual']['rig'] for x in b['beats']} for b in briefs}
        for a in rigs:
            for b in rigs:
                if a < b:self.assertLessEqual(len(rigs[a] & rigs[b]), variety.MAX_SHARED_RIGS, (a, b))


if __name__ == '__main__':
    unittest.main()
