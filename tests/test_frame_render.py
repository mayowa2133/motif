import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1];sys.path.insert(0, str(ROOT / 'scripts'))

FIXTURE = ROOT / 'tests/fixtures/reel-brief-fixture.json'


def chromium():
    try:
        from motif_frame_snapshot import _chromium
        return Path(_chromium()).exists()
    except Exception:
        return False


@unittest.skipUnless(chromium() and shutil.which('ffmpeg') and os.environ.get('MOTIF_SKIP_E2E') != '1', 'needs Chromium and ffmpeg')
class FrameRenderCache(unittest.TestCase):
    def test_parallel_render_redraws_only_changed_shots(self):
        from motif_frame_render import clips, render
        from motif_reel import run
        with tempfile.TemporaryDirectory() as tmp:
            run(FIXTURE, Path(tmp), allow_draft=True, stub_voice=True)
            project = next(p for p in Path(tmp).iterdir() if p.name.endswith('-finished'))
            shots = [c for c in clips(project) if c['id'] != 'captions']
            first = render(project, Path(tmp) / 'a.mp4', (90, 160), audio=False, workers=2)
            self.assertEqual((first['shots_drawn'], first['shots']), (len(shots), len(shots)))
            again = render(project, Path(tmp) / 'b.mp4', (90, 160), audio=False, workers=2)
            self.assertEqual((again['shots_drawn'], again['frames']), (0, first['frames']))
            with open(project / shots[1]['src'], 'a') as f:f.write('<!-- edited -->')
            edited = render(project, Path(tmp) / 'c.mp4', (90, 160), audio=False, workers=2)
            self.assertEqual((edited['shots_drawn'], edited['frames']), (1, first['frames']))
            self.assertEqual(len(list((project / '.render-cache').glob('*.mp4'))), len(shots))
