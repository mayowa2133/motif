import re
import sys
import unittest
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1];sys.path.insert(0, str(ROOT / 'scripts'))

import motif_bot_kit as kit
from motif_rigs.palettes import PALETTES


def parses(svg):
    svg = re.sub(r' (data-[\w-]+)(?=[\s/>])', r' \1=""', svg)
    ElementTree.fromstring(f'<svg xmlns="http://www.w3.org/2000/svg">{svg}</svg>')


class CostumeTests(unittest.TestCase):
    def test_every_costume_renders_in_every_palette(self):
        for name in kit.COSTUMES:
            for pal in PALETTES:parses(kit.dressed_bot(360, 1000, .3, costume=[name], palette=pal))

    def test_costumes_take_palette_colour_and_bot_stays_canonical(self):
        a = kit.dressed_bot(0, 0, costume=['hard-hat'], palette='sunrise');b = kit.dressed_bot(0, 0, costume=['hard-hat'], palette='cobalt')
        self.assertIn(PALETTES['sunrise']['secondary'], a);self.assertIn(PALETTES['cobalt']['secondary'], b)
        bare_a, bare_b = kit.dressed_bot(0, 0, palette='sunrise'), kit.dressed_bot(0, 0, palette='cobalt')
        self.assertEqual(bare_a, bare_b, 'Bot itself never changes colour')

    def test_head_piece_turns_with_the_head(self):
        svg = kit.dressed_bot(0, 0, pose='inspecting', costume=['cap'])
        self.assertIn('rotate(-8 512 350)', svg)

    def test_tilted_pose_tilts_the_costume(self):
        svg = kit.dressed_bot(0, 0, pose='pushing', costume=['hi-vis'])
        self.assertGreaterEqual(svg.count('rotate(9 512 620)'), 2)

    def test_unknown_costume_rejected(self):
        with self.assertRaises(ValueError):kit.outfit(['crown'], PALETTES['berry'])


class CycleTests(unittest.TestCase):
    def test_walk_cycle_alternates_and_loops(self):
        for cycle in kit.CYCLES:
            feet = [kit.walk_pose(i / kit.PHASES, cycle)[1]['feet'] for i in range(kit.PHASES + 1)]
            self.assertEqual(feet[0], feet[-1], f'{cycle} loops')
            lead = [f[0][0] > 512 - 87 for f in feet[:-1]]
            self.assertIn(True, lead);self.assertIn(False, lead)
            for (lx, ly, _), (rx, ry, _) in feet:self.assertLessEqual(max(ly, ry), 861 + 1e-9, 'feet never sink below the floor')

    def test_cycle_frames_differ(self):
        frames = {kit.dressed_bot(0, 0, cycle='walk', phase=i / 8) for i in range(8)}
        self.assertEqual(len(frames), 8)

    def test_framing_presets(self):
        self.assertGreater(kit.FRAMING['hero'], kit.FRAMING['medium']);self.assertGreater(kit.FRAMING['wide'], kit.FRAMING['crowd'])
        with self.assertRaises(ValueError):kit.framed_bot('macro', 0, 0)


class CrowdTests(unittest.TestCase):
    def test_crowd_is_seeded(self):
        self.assertEqual(kit.crowd(10, seed=4), kit.crowd(10, seed=4))
        self.assertNotEqual(kit.crowd(10, seed=4), kit.crowd(10, seed=5))

    def test_crowd_varies_and_sorts_back_to_front(self):
        members = kit.crowd_layout(16, seed=2, area=(40, 680, 700, 1230))
        self.assertEqual(len(members), 16)
        self.assertEqual([m['y'] for m in members], sorted(m['y'] for m in members))
        self.assertGreater(len({m['face'] for m in members}), 3);self.assertGreater(len({m['pose'] for m in members}), 2)
        self.assertGreater(len({tuple(m['costume']) for m in members}), 4);self.assertEqual({True, False}, {m['flip'] for m in members})

    def test_crowd_palettes_vary_costume_colours(self):
        svg = kit.crowd(12, seed=1, palettes=['berry', 'meadow', 'cobalt'], area=(40, 680, 700, 1230))
        hits = [name for name in ('berry', 'meadow', 'cobalt') if any(PALETTES[name][r] in svg for r in ('primary', 'secondary', 'pop', 'accent'))]
        self.assertGreaterEqual(len(hits), 2);parses(svg)

    def test_crowd_too_dense_is_refused(self):
        with self.assertRaises(ValueError):kit.crowd_layout(80, seed=0, area=(300, 420, 1000, 1010))


if __name__ == '__main__':
    unittest.main()
