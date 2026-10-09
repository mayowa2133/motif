import json
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
class ReelEndToEnd(unittest.TestCase):
    def test_fixture_brief_runs_without_per_film_code(self):
        from motif_reel import run
        with tempfile.TemporaryDirectory() as tmp:
            record = run(FIXTURE, Path(tmp), allow_draft=True, stub_voice=True, local_draft=True)
            stages = {s['stage']: s['status'] for s in record['stages']}
            for name in ('script', 'plan', 'structure', 'compile', 'rough', 'finish', 'gate'):self.assertEqual(stages[name], 'PASS', (name, record))
            self.assertEqual(stages['review'], 'DRAFT_REVIEW_REQUIRED')
            for project in Path(tmp).iterdir():
                self.assertEqual(list(project.rglob('*.py')), [], 'no project-local Python')
            final = Path(tmp) / 'fixture-paper-notes-finished'
            self.assertTrue((final / 'finish-record.json').exists());self.assertTrue((final / 'index.html').exists())


if __name__ == '__main__':
    unittest.main()
