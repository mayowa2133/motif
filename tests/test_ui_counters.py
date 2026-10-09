import json
import re
import sys
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1];sys.path.insert(0, str(ROOT / 'scripts'))

from motif_inserts import comment_end_card, contrast, counter, counter_values, gauge, price_tag, progress_bar, screenshot_card, star_badge
from motif_provenance import check, project_rules
from motif_rigs.palettes import PALETTES


def parses(svg):
    # Browser-only bare data-layout-* attributes are valid HTML, not XML.
    svg = re.sub(r' (data-[\w-]+)(?=[\s/>])', r' \1=""', svg)
    ElementTree.fromstring(f'<svg xmlns="http://www.w3.org/2000/svg">{svg}</svg>')


class CounterTests(unittest.TestCase):
    def test_counter_values_monotonic_and_exact(self):
        for start, end, frames in ((0, 12480, 45), (900, 120, 30), (5, 5, 10), (0, 3, 60)):
            values = counter_values(start, end, frames)
            self.assertEqual(len(values), frames);self.assertEqual(values[-1], end);self.assertEqual(values[0], start)
            step = 1 if end >= start else -1
            self.assertTrue(all((b - a) * step >= 0 for a, b in zip(values, values[1:])))
            self.assertTrue(all(v == end for v in values[int(frames * .8) + 1:]), 'settles on target before the end')

    def test_digits_read_on_every_palette(self):
        for name, c in PALETTES.items():
            svg = counter(1234, name, prefix='$', label='per month');parses(svg)
            fill = svg.split('$1,234')[0].rsplit('fill="', 1)[1][:7]
            self.assertGreaterEqual(contrast(fill, c['dark']), 4.5, name)

    def test_inserts_render(self):
        for svg in (star_badge('berry', 5, 3, 1.2), price_tag('$9', 'cobalt', strike='$29'), gauge(.4, 'meadow', 'HYPE'), progress_bar(.3, 'sunrise', label='30%')):
            parses(svg)


class EndCardTests(unittest.TestCase):
    def test_end_card_renders_cta_word(self):
        svg = comment_end_card('agent', 'plum-night');parses(svg)
        self.assertIn('>AGENT<', svg);self.assertIn('>Comment<', svg)


class ScreenshotTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory();self.project = Path(self.tmp.name)
        shot = self.project / 'assets/screens/pricing.png';shot.parent.mkdir(parents=True)
        from PIL import Image
        Image.new('RGB', (8, 8), (10, 200, 90)).save(shot)

    def tearDown(self):
        self.tmp.cleanup()

    def test_screenshot_without_source_is_refused(self):
        with self.assertRaises(ValueError):screenshot_card('/assets/screens/pricing.png', 'lagoon', None, project=self.project)
        with self.assertRaises(ValueError):screenshot_card('/assets/screens/pricing.png', 'lagoon', 'pricing page', project=self.project)

    def test_unsourced_screenshot_fails_provenance(self):
        result = check(self.project, registry={'version': 1, 'assets': []})
        self.assertEqual(result['status'], 'FAIL');self.assertIn('assets/screens/pricing.png', result['unknown'])

    def test_sourced_screenshot_passes_provenance(self):
        parses(screenshot_card('/assets/screens/pricing.png', 'lagoon', 'https://example.com/pricing', project=self.project))
        result = check(self.project, registry={'version': 1, 'assets': []})
        self.assertEqual(result['status'], 'PASS', result);self.assertEqual(result['files'][0]['origin'], 'licensed')

    def test_licensed_rule_needs_source_url(self):
        (self.project / 'asset-provenance.json').write_text(json.dumps({'rules': [{'glob': 'assets/screens/*', 'origin': 'licensed', 'generator': 'x'}]}))
        with self.assertRaises(ValueError):project_rules(self.project)


if __name__ == '__main__':
    unittest.main()
