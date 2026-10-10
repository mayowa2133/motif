"""The 2026-10-09 quality pass: metaphor fit, brand marks, Bot staging, edge
props, motion floor (review items 1-5 and 7)."""
import copy
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1];sys.path.insert(0, str(ROOT / 'scripts'))

import motif_brand as brand
import motif_reel as reel
import motif_semantics as sem
import motif_sets as ms
from motif_rigs import all_rigs

BENCH = sorted((ROOT / 'quality/benchmark-briefs').glob('*.json'))
FIXTURE = json.loads((ROOT / 'tests/fixtures/reel-brief-fixture.json').read_text())


class MetaphorFitTests(unittest.TestCase):
    def test_every_rig_declares_relations(self):
        self.assertEqual(set(sem.RIG_RELATIONS), set(all_rigs()))
        for rels in sem.RIG_RELATIONS.values():self.assertTrue(set(rels) <= set(sem.RELATIONS))

    def test_classifier_reads_the_common_claim_shapes(self):
        self.assertEqual(sem.classify('It ships inside every Android phone and every iPhone.'), 'everywhere')
        self.assertEqual(sem.classify('Certificates used to cost real money. Now they cost zero.'), 'cost-crush')
        self.assertIsNone(sem.classify('It is a lovely day.'))

    def test_mismatched_rig_is_a_plan_error(self):
        brief = copy.deepcopy(FIXTURE);brief['beats'][0]['visual']['rig'] = 'thermometer'
        errors, _ = reel.validate_plan(reel.plan_reel(brief, allow_draft=True), True)
        self.assertTrue(any('metaphor mismatch' in e for e in errors), errors)

    def test_planner_picks_a_fitting_rig_when_the_brief_names_none(self):
        brief = copy.deepcopy(FIXTURE);del brief['beats'][2]['visual']['rig'];del brief['beats'][2]['visual']['params']
        plan = reel.plan_reel(brief, allow_draft=True)
        self.assertTrue(sem.fits(plan['beats'][3]['shots'][0]['rig']['id'], 'cost-crush'))

    def test_benchmarks_pass_sound_off(self):
        for path in BENCH:
            b = json.loads(path.read_text());plan = reel.plan_reel(b, allow_draft=True)
            self.assertEqual(reel.validate_plan(plan, True)[0], [], path.name)
            self.assertEqual(sem.sound_off(plan, b)['failures'], [], path.name)

    def test_sound_off_flags_placeholder_labels_and_missing_brand(self):
        brief = json.loads(BENCH[-1].read_text());plan = reel.plan_reel(brief, allow_draft=True)
        plan['beats'][1]['shots'][0]['rig']['params'] = {'kind': 'phone', 'count': 6, 'label': 'ITEMS'};plan['brand'] = None
        result = sem.sound_off(plan, brief)
        self.assertEqual(result['status'], 'FAIL')
        self.assertTrue(any('placeholders' in f for f in result['failures']));self.assertTrue(any('brand' in f for f in result['failures']))


class BrandTests(unittest.TestCase):
    def test_vendored_marks_load_and_are_registered(self):
        registry = json.loads((ROOT / 'assets/PROVENANCE.json').read_text())
        ids = {e['id'] for e in registry['assets']}
        for slug in brand.catalogue():
            m = brand.mark(slug);self.assertTrue(m['path'].startswith('M'));self.assertRegex(m['hex'], r'^#[0-9A-Fa-f]{6}$')
            self.assertIn(f'brand/simple-icons/{slug}', ids)
        self.assertIn('<path', brand.badge('sqlite', 200, {'dark': '#000', 'light': '#fff'}))

    def test_unknown_brand_is_rejected(self):
        brief = copy.deepcopy(FIXTURE);brief['brand'] = {'slug': 'not-a-brand'}
        errors, _ = reel.validate_plan(reel.plan_reel(brief, allow_draft=True), True)
        self.assertTrue(any('brand' in e for e in errors), errors)


class StagingTests(unittest.TestCase):
    def test_edge_props_read_as_whole_objects_and_bot_stands_clear(self):
        for room in ms.ROOMS:
            for beat, rig in enumerate(sorted(all_rigs())):
                layout = ms.solve(room, rig, seed=1, beat=beat);bot = layout['bot']
                self.assertTrue(ms.BOT_SCALE[0] - 1e-6 <= bot['scale'] <= ms.BOT_SCALE[1] + 1e-6)
                half = ms.BOT_HALF * bot['scale'];self.assertTrue(half <= bot['x'] <= ms.W - half, (room, rig))
                bot_box = (bot['x'] - half, bot['y'] - 4.2 * half, 2 * half, 4.2 * half)
                for item in layout['dressing']:
                    self.assertGreaterEqual(ms.visible_share(item['box']), ms.EDGE_VISIBLE - 1e-6, (room, rig, item['prop']))
                    if item['layer'] == 'front':self.assertEqual(ms._overlap(item['box'], bot_box), 0, (room, rig, item['prop']))


@unittest.skipUnless(shutil.which('ffmpeg'), 'needs ffmpeg')
class MotionTests(unittest.TestCase):
    def clip(self, folder, source):
        out = Path(folder) / 'clip.mp4'
        subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-f', 'lavfi', '-i', source, '-t', '2', '-pix_fmt', 'yuv420p', str(out)], check=True)
        return out

    def test_static_reel_fails_and_moving_reel_passes(self):
        import motif_motion
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(motif_motion.measure(self.clip(tmp, 'color=c=red:s=180x320:r=30'))['status'], 'FAIL')
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(motif_motion.measure(self.clip(tmp, 'testsrc2=s=180x320:r=30'))['status'], 'PASS')


if __name__ == '__main__':
    unittest.main()


class MusicTests(unittest.TestCase):
    def test_bed_is_deterministic_and_fits_the_reel(self):
        import wave
        import motif_music
        with tempfile.TemporaryDirectory() as tmp:
            a = motif_music.bed(Path(tmp) / 'a.wav', 3.0, 'neon-arcade', 4);b = motif_music.bed(Path(tmp) / 'b.wav', 3.0, 'neon-arcade', 4)
            self.assertEqual((Path(tmp) / 'a.wav').read_bytes(), (Path(tmp) / 'b.wav').read_bytes());self.assertEqual(a['mode'], 'minor')
            with wave.open(str(Path(tmp) / 'a.wav')) as w:self.assertAlmostEqual(w.getnframes() / w.getframerate(), 3.0, places=2)
            motif_music.bed(Path(tmp) / 'c.wav', 3.0, 'candy-pastel', 4)
            self.assertNotEqual((Path(tmp) / 'a.wav').read_bytes(), (Path(tmp) / 'c.wav').read_bytes())


class Round4SlipTests(unittest.TestCase):
    def test_range_values_get_no_counter_and_cta_offer_drops_the_keyword(self):
        brief = copy.deepcopy(FIXTURE);brief['facts'][0]['value'] = '1 to 8%';brief['beats'][0]['visual'].pop('insert', None)
        brief['cta']['narration'] = f'For the setup steps, comment {brief["cta"]["keyword"]}.'
        plan = reel.plan_reel(brief, allow_draft=True)
        self.assertNotEqual((plan['beats'][1]['shots'][1].get('insert') or {}).get('kind'), 'counter')
        self.assertNotIn('COMMENT', plan['beats'][-1]['shots'][0]['headline_b'])

    def test_heroes_keep_a_camera_margin_and_props_stay_in_scale(self):
        for room in ms.ROOMS:
            for beat, rig in enumerate(sorted(all_rigs())):
                layout = ms.solve(room, rig, seed=1, beat=beat);x, _, w, _ = layout['hero']['box']
                if all_rigs()[rig].footprint[2] * layout['hero']['scale'] <= ms.W - 2 * ms.HERO_SAFE + 1e-6:
                    self.assertGreaterEqual(x, ms.HERO_SAFE - 1e-6, (room, rig));self.assertLessEqual(x + w, ms.W - ms.HERO_SAFE + 1e-6, (room, rig))
                for item in layout['dressing']:self.assertLessEqual(item['scale'], ms.PROP_MAX_SCALE + 1e-6)

    def test_app_screen_key_sits_away_from_bot(self):
        rig = all_rigs()['app-screen']
        for device in rig.SIZES:self.assertLess(rig.button({**rig.defaults, 'device': device})[0], 0)


class Round8StoryTests(unittest.TestCase):
    """Codex's v11 critique: each machine must demonstrate the claim and carry its object forward."""

    def test_held_beat_keeps_the_lock_shut_and_the_next_beat_opens_the_same_lock(self):
        brief = json.loads((ROOT / 'quality/benchmark-briefs/bench-python-no-gil.json').read_text())
        lock, freed = reel.plan_reel(brief, allow_draft=True)['beats'][1:3]
        self.assertTrue(all(s['rig'].get('hold') for s in lock['shots']))
        self.assertEqual(lock['shots'][0]['rig']['id'], freed['shots'][0]['rig']['id'])
        self.assertEqual(lock['shots'][0]['rig']['params'], freed['shots'][0]['rig']['params'])
        self.assertFalse(freed['shots'][0]['rig'].get('hold'))

    def test_copy_sends_the_file_to_the_stick_and_the_map_shows_its_pins(self):
        rig = all_rigs()['app-screen']
        usb = {**rig.defaults, 'device': 'laptop', 'ui': 'window', 'lines': ['app.db'], 'send_to': 'USB'}
        before, after = rig.render(usb, ('run', .2), 'sunrise'), rig.render(usb, ('run', 1.0), 'sunrise')
        self.assertIn('USB', before);self.assertGreater(len(after), len(before))
        m = {**rig.defaults, 'device': 'phone', 'ui': 'map', 'lines': ['shop', 'bus stop'], 'prefilled': True, 'credit': 'OSM'}
        svg = rig.render(m, ('run', 0.0), 'sunrise')
        self.assertIn('bus stop', svg);self.assertIn('OSM', svg)


class CloseupTests(unittest.TestCase):
    def test_reveal_beats_snap_in_on_what_changed(self):
        brief = json.loads((ROOT / 'quality/benchmark-briefs/bench-sqlite-everywhere.json').read_text())
        beat = [b for b in reel.plan_reel(brief, allow_draft=True)['beats'] if b['id'] == 'onefile'][0]
        self.assertTrue(beat['shots'][1].get('closeup'));self.assertFalse(beat['shots'][0].get('closeup'))
        rig = all_rigs()['app-screen']
        self.assertEqual(rig.reveal({**rig.defaults, 'send_to': 'USB'})[0], rig.USB[0])


class ContinuityTests(unittest.TestCase):
    def test_poof_swells_then_clears_and_camera_never_holds_still(self):
        import motif_looks
        from motif_rigs.palettes import palette
        c = palette('sunrise')
        self.assertIn('<circle', reel.poof(100, 100, 3, c));self.assertEqual(reel.poof(100, 100, 12, c), '')
        frames = [motif_looks.camera('push', 'setup', f / 59, f, 60) for f in range(60)]
        self.assertGreater(max(d for _, d, _ in frames) - min(d for _, d, _ in frames), 4)
