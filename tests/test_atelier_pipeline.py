"""Motif Atelier end to end on a 36-frame smoke film: real Chromium renders, real ffmpeg encodes.

Labelled stand-ins, so nothing here is mistaken for creative proof:
- reviews are TEST STUB responses (contracts gate logic, not film quality);
- narration, where a test needs it, is a STUB tone per line instead of TTS
  (the approved Kokoro voice needs a network fetch on first use).
Everything else (playback, capture, encode, mix, loudness, captions,
fingerprints, technical checks) is the real pipeline.
"""
import json
import os
import shutil
import sys
import tempfile
import unittest
import wave
from pathlib import Path
from unittest import mock

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT));sys.path.insert(0, str(ROOT / 'scripts'))

from atelier.engine import playback, sound, studio  # noqa: E402
from atelier.engine.project import Project, read, sha, write  # noqa: E402
from test_atelier_contracts import FIXTURE, stub_review  # noqa: E402


def can_render():
    return bool(playback.chromium()) and shutil.which('ffmpeg') and os.environ.get('MOTIF_SKIP_E2E') != '1'


def stub_take(text, voice, speed, cache, python=None):
    """STUB narration: a quiet tone whose length follows the word count. Not a voice."""
    folder = Path(cache) / 'voice';folder.mkdir(parents=True, exist_ok=True)
    out = folder / f'stub-{abs(hash((text, voice, speed))) % 10**8}.wav'
    if out.is_file():return out, True
    n = int(len(text.split()) / 4.5 * 24000);t = np.arange(n) / 24000
    with wave.open(str(out), 'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes((np.sin(2 * np.pi * 220 * t) * 0.3 * 32767).astype('<i2').tobytes())
    return out, False


@unittest.skipUnless(can_render(), 'needs the pre-installed Chromium and ffmpeg')
class Pipeline(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory();self.home = Path(self.tmp.name)
        self.old = os.environ.get('MOTIF_ATELIER_HOME');os.environ['MOTIF_ATELIER_HOME'] = str(self.home)

    def tearDown(self):
        if self.old is None:os.environ.pop('MOTIF_ATELIER_HOME', None)
        else:os.environ['MOTIF_ATELIER_HOME'] = self.old
        self.tmp.cleanup()

    # helpers -------------------------------------------------------------
    def project(self, narrated=False):
        brief = json.loads((FIXTURE / 'brief.json').read_text())
        project = studio.start(brief, reviewer='handoff', workers=2)
        for name in ('concepts.json', 'direction.json'):shutil.copy(FIXTURE / name, project.dir / name)
        shutil.copytree(FIXTURE / 'source', project.source)
        if narrated:
            d = read(project.dir / 'direction.json');d['audio']['narration'] = 'voice-over';d['audio']['voice'] = 'af_heart';d['applicability'].pop('picture_sound_link')
            write(project.dir / 'direction.json', d)
            f = read(project.source / 'film.json');f['sound']['voice'] = 'af_heart'
            f['sound']['narration'] = [{'id': 'drop', 'text': 'Drop it, little ball.', 'at': 0}];write(project.source / 'film.json', f)
            studio.refresh_ledger(project)
        return project

    def answer(self, project, role, status='PASS', **kw):
        req = project.dir / f'reviews/{role}-request.json'
        write(project.dir / f'reviews/{role}.json', stub_review(read(req), sha(req), role, status, kind='builder' if role == 'proof' else 'model', **kw))

    def resume(self, project):
        return studio.advance(Project.locate(project.dir), reviewer='handoff', workers=2)

    def to_review_required(self, project):
        p = self.resume(project);self.assertEqual(p.state['status'], 'AWAITING_REVIEW:proof')
        self.answer(p, 'proof');p = self.resume(p);self.assertEqual(p.state['status'], 'AWAITING_REVIEW:story,visual')
        self.answer(p, 'story');self.answer(p, 'visual');p = self.resume(p)
        return p

    # tests -----------------------------------------------------------------
    def test_full_path_delivers_real_encodes_and_stops_at_review_required(self):
        p = self.to_review_required(self.project())
        self.assertEqual(p.state['status'], 'REVIEW_REQUIRED', p.state.get('next_step'))
        record = read(p.root / p.stage('delivery')['delivery']).get if False else read(next((p.runs / 'delivery').glob('*/delivery.json')))
        checks = record['checks']
        for name in ('delivery-format', 'delivery-frames', 'delivery-audio-stream', 'preview-format', 'preview-frames', 'loudness', 'true-peak', 'clipping',
                     'reviewed-picture', 'deterministic-seek', 'rights-ledger'):
            self.assertEqual(checks[name]['status'], 'PASS', (name, checks[name]))
        self.assertEqual(checks['delivery-captions']['status'], 'NOT_APPLICABLE')      # silent smoke film: nothing to caption
        info = playback.probe(p.root / p.stage('delivery')['delivery'])
        self.assertEqual((info['video']['width'], info['video']['height'], info['video']['frames']), (1080, 1920, 36))
        self.assertTrue((p.dir / 'production-metadata.json').is_file())
        self.assertIsNone(p.state['human_decision'])                                     # only a person can approve
        studio.approve(p, 'Test Person', 'approved', 'test only');self.assertEqual(p.state['status'], 'HUMAN_APPROVED')

    def test_narrated_film_carries_soft_captions_and_line_timing(self):
        with mock.patch.object(sound, 'take', stub_take):
            p = self.to_review_required(self.project(narrated=True))
        self.assertEqual(p.state['status'], 'REVIEW_REQUIRED', p.state.get('next_step'))
        info = playback.probe(p.root / p.stage('delivery')['delivery'])
        self.assertEqual(info['subtitles'], ['mov_text'])
        timing = read(next((p.runs / 'audio').glob('*/timing.json')))
        self.assertIn('no word-level alignment', timing['method'])

    def test_failed_review_blocks_and_three_failed_rounds_exhaust_the_approach(self):
        p = self.resume(self.project());self.answer(p, 'proof');p = self.resume(p)
        for k in range(3):
            self.answer(p, 'story');self.answer(p, 'visual', 'FAIL');p = self.resume(p)
            self.assertNotEqual(p.state['status'], 'REVIEW_REQUIRED')
            if k < 2:
                self.assertEqual(p.state['status'], 'BLOCKED:VISUAL_FAILED')
                (p.source / 'film.js').write_text((p.source / 'film.js').read_text() + f'\n// repair {k + 1}\n');studio.refresh_ledger(p)
                p = self.resume(p);self.assertTrue(p.state['status'].startswith('AWAITING_REVIEW'))
        self.assertEqual(p.state['status'], 'BLOCKED:REPAIR_BUDGET_EXHAUSTED')
        renders = len(p.state['renders'])
        (p.source / 'film.js').write_text((p.source / 'film.js').read_text() + '\n// a fourth try\n');studio.refresh_ledger(p)
        p = self.resume(p)
        self.assertEqual(p.state['status'], 'BLOCKED:REPAIR_BUDGET_EXHAUSTED');self.assertEqual(len(p.state['renders']), renders)   # no render spent past the budget

    def test_changed_source_makes_reviews_stale_and_delivery_not_current(self):
        p = self.to_review_required(self.project());first = p.stage('delivery')['delivery_sha256']
        studio.approve(p, 'Test Person', 'approved', 'test only')
        (p.source / 'film.js').write_text((p.source / 'film.js').read_text().replace('#E8682A', '#2A68E8'));studio.refresh_ledger(p)
        p = self.resume(p)
        self.assertEqual(p.state['status'], 'AWAITING_REVIEW:story,visual')
        self.assertTrue(list((p.dir / 'reviews/history').glob('story-*.json')))
        self.assertEqual(p.stage('delivery')['status'], 'SUPERSEDED')
        self.assertIsNone(p.state['human_decision'])                                       # an approval never carries to a changed film
        self.assertEqual(p.stage('proof')['status'], 'DONE')                               # the proof is per approach, kept

    def test_missing_asset_and_failed_authoring_never_reach_review(self):
        p = self.project();f = read(p.source / 'film.json');f['images'] = {'hero': 'art/hero.png'};write(p.source / 'film.json', f);studio.refresh_ledger(p)
        p = self.resume(p)
        self.assertEqual(p.state['status'], 'AWAITING_AUTHORING:proof')
        self.assertIn('authoring task', (p.dir / 'handoff/proof.md').read_text())

    def test_resume_keeps_identity_history_and_cached_work(self):
        p = self.to_review_required(self.project());pid = p.state['project_id'];renders = len(p.state['renders']);events = len(p.state['history'])
        p = self.resume(p)
        self.assertEqual(p.state['project_id'], pid);self.assertEqual(p.state['status'], 'REVIEW_REQUIRED')
        self.assertEqual(len(p.state['renders']), renders)                                 # nothing re-rendered
        self.assertGreaterEqual(len(p.state['history']), events)

    def test_resume_reuses_voice_takes(self):
        calls = []
        def counting(*a, **k):
            out = stub_take(*a, **k);calls.append(out[1]);return out
        with mock.patch.object(sound, 'take', counting):
            p = self.to_review_required(self.project(narrated=True))
            f = read(p.source / 'film.json');f['sound']['sfx'][0]['gain_db'] = -8;write(p.source / 'film.json', f);studio.refresh_ledger(p)
            self.resume(p)
        self.assertEqual(calls[0], False);self.assertTrue(all(calls[1:]))                   # the take was generated once, then reused

    def test_film_cannot_reach_the_network_or_use_clocks(self):
        src = self.home / 'bad';shutil.copytree(FIXTURE / 'source', src)
        film = read(src / 'film.json')
        js = (src / 'film.js').read_text()
        (src / 'film.js').write_text(js.replace('render(ctx, env) {', 'render(ctx, env) { if (env.frame === 3) { const i = new Image(); i.src = "//example.invalid/x.png"; }'))
        with self.assertRaises(playback.RenderError) as ctx:playback.render(src, film, {'lines': {}}, self.home / 'o.mp4', playback.PREVIEW, (0, 12), 1)
        self.assertIn('blocked request', str(ctx.exception))
        (src / 'film.js').write_text(js.replace('render(ctx, env) {', 'render(ctx, env) { Math["ran" + "dom"]();'))
        with self.assertRaises(playback.RenderError) as ctx:playback.render(src, film, {'lines': {}}, self.home / 'o.mp4', playback.PREVIEW, (0, 12), 1)
        self.assertIn('Math.random is disabled', str(ctx.exception))

    def test_a_hung_frame_times_out(self):
        src = self.home / 'hang';shutil.copytree(FIXTURE / 'source', src)
        (src / 'film.js').write_text((src / 'film.js').read_text().replace('render(ctx, env) {', 'render(ctx, env) { if (env.frame === 2) { for (;;) {} }'))
        with mock.patch.object(playback, 'FRAME_TIMEOUT_MS', 3000), self.assertRaises(playback.RenderError):
            playback.render(src, read(src / 'film.json'), {'lines': {}}, self.home / 'o.mp4', playback.PREVIEW, (0, 12), 1)

    def test_saved_build_reproduces_frames_in_any_segment_order(self):
        film = read(FIXTURE / 'source/film.json')
        a = playback.render(FIXTURE / 'source', film, {'lines': {}}, self.home / 'a.mp4', playback.PREVIEW, None, 1)
        b = playback.render(FIXTURE / 'source', film, {'lines': {}}, self.home / 'b.mp4', playback.PREVIEW, None, 3)
        self.assertEqual(a['frames'], b['frames'])
        frames = list(range(0, 36, 5));fa, fb = playback.fingerprint(a['file'], frames), playback.fingerprint(b['file'], frames)
        worst = max(playback.thumb_distance(fa[k], fb[k])['mean'] for k in fa)
        self.assertLessEqual(worst, 1.0)                                                    # declared tolerance, not byte identity
        ia, ib = playback.probe(a['file']), playback.probe(b['file'])
        self.assertAlmostEqual(ia['duration'], ib['duration'], places=2)


if __name__ == '__main__':
    unittest.main()
