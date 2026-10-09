import glob
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1];sys.path.insert(0, str(ROOT / 'scripts'))

import json
from jsonschema import Draft202012Validator

import motif_sets as ms
from motif_props import PROPS
from motif_rigs import all_rigs

SCHEMA = Draft202012Validator(json.loads((ROOT / 'schemas/set.schema.json').read_text()))
GOLD = sorted(glob.glob(str(ROOT / 'quality/gold/*/still.png')))
DOTS = sorted(glob.glob(str(ROOT / 'videos/productions/openai-dots-news/review/partial-native/b*.png')))


class SolverTests(unittest.TestCase):
    def test_deterministic(self):
        self.assertEqual(ms.solve('office', 'thermometer', seed=3, beat=2), ms.solve('office', 'thermometer', seed=3, beat=2))
        self.assertNotEqual(ms.solve('office', 'thermometer', seed=3, beat=2), ms.solve('office', 'thermometer', seed=4, beat=2))

    def test_layout_rules_for_every_room_and_rig(self):
        for room in ms.ROOMS:
            for beat, rig in enumerate(sorted(all_rigs())):
                layout = ms.solve(room, rig, seed=0, beat=beat);SCHEMA.validate(layout)
                hero = layout['hero']['box']
                self.assertGreaterEqual(hero[3], ms.HERO_MIN * ms.H - 1e-6, f'{room}/{rig} hero too small')
                boxes = [d['box'] for d in layout['dressing']]
                self.assertTrue(any(ms._crosses_edge(b) for b in boxes), f'{room}/{rig}: nothing crosses a frame edge')
                self.assertTrue(any(ms._overlap(b, hero) > 0 for b in boxes), f'{room}/{rig}: nothing overlaps the hero')
                for b in boxes:
                    self.assertFalse(ms._in_headline(b), f'{room}/{rig}: dressing in the headline band')
                    self.assertFalse(ms._in_caption(b), f'{room}/{rig}: dressing in the caption band')
                for d in layout['dressing']:self.assertIn(d['prop'], ms.ROOMS[room]['dressing'])

    def test_palette_rotates_per_beat(self):
        beats = [{'room': r, 'rig': g} for r, g in zip(sorted(ms.ROOMS), sorted(all_rigs()))][:6]
        palettes = [ms.solve(b['room'], b['rig'], seed=1, beat=i)['palette'] for i, b in enumerate(beats)]
        self.assertTrue(all(a != b for a, b in zip(palettes, palettes[1:])), palettes)
        self.assertGreaterEqual(len(set(palettes)), 5)

    def test_unknown_room_and_costume_rejected(self):
        with self.assertRaises(ValueError):ms.solve('moon-base', 'conveyor')
        with self.assertRaises(ValueError):ms.solve('office', 'conveyor', costume=['crown'])

    def test_compose_renders_all_layers(self):
        layout = ms.solve('workshop', 'stamp-gate', seed=2, beat=1);svg = ms.compose(layout, ('stamp', .5))
        self.assertIn('data-part="head"', svg);self.assertGreater(len(svg), 5000)


class LibraryTests(unittest.TestCase):
    def test_props_render_in_every_palette(self):
        from motif_rigs.palettes import PALETTES
        self.assertGreaterEqual(len(PROPS), 40)
        for name, prop in PROPS.items():
            self.assertIn(prop.mount, ('floor', 'wall', 'ceiling', 'sky'))
            renders = {prop.render(p) for p in PALETTES}
            self.assertGreater(len(renders), 1, f'{name} ignores the palette')

    def test_eight_rooms(self):
        self.assertEqual(len(ms.ROOMS), 8)
        for room, spec in ms.ROOMS.items():
            for name in spec['dressing']:self.assertIn(name, PROPS, room)


class EmptyFieldTests(unittest.TestCase):
    @unittest.skipUnless(GOLD, 'gold stills not checked out')
    def test_v6_gold_frames_pass(self):
        result = ms.check_frames(GOLD);self.assertEqual(result['status'], 'PASS', result['failures'])

    @unittest.skipUnless(DOTS, 'Dots rough frames not checked out')
    def test_dots_rough_frames_flagged(self):
        scores = [ms.empty_field(p) for p in DOTS]
        flagged = [s for s in scores if s > ms.EMPTY_FIELD_MAX]
        self.assertGreaterEqual(len(flagged), len(scores) // 2, scores)
        self.assertGreater(min(scores), max(ms.empty_field(p) for p in GOLD) if GOLD else 0)

    def test_checked_solver_passes_its_own_frames(self):
        layout = ms.solve_checked('diner', 'conveyor', seed=0, beat=0)
        self.assertLessEqual(layout['empty_field'], ms.EMPTY_FIELD_MAX);SCHEMA.validate(layout)


if __name__ == '__main__':
    unittest.main()
