"""Font transfer keeps exact bytes and fails closed for incomplete overrides."""
import hashlib
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from motif_runtime_portability import cleared_font, copy_cleared_font


class RuntimePortabilityTests(unittest.TestCase):
    def test_font_and_notice_copy_exact_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            font, notice = root / "font.ttf", root / "notice.txt"
            font.write_bytes(b"unit-only-font")
            notice.write_text("unit-only-redistribution-notice")
            with patch.dict(os.environ, {"MOTIF_FONT_PATH": str(font), "MOTIF_FONT_LICENSE_PATH": str(notice)}):
                record = copy_cleared_font(root / "output/font.ttf")
            self.assertEqual(Path(record["destination_font"]).read_bytes(), font.read_bytes())
            self.assertEqual(Path(record["destination_license"]).read_bytes(), notice.read_bytes())
            self.assertEqual(record["font_sha256"], hashlib.sha256(font.read_bytes()).hexdigest())

    def test_partial_override_and_missing_files_fail(self):
        with patch.dict(os.environ, {"MOTIF_FONT_PATH": "/missing/font.ttf", "MOTIF_FONT_LICENSE_PATH": ""}):
            with self.assertRaisesRegex(ValueError, "together"):
                cleared_font()
        with patch.dict(os.environ, {"MOTIF_FONT_PATH": "/missing/font.ttf", "MOTIF_FONT_LICENSE_PATH": "/missing/license.txt"}):
            with self.assertRaisesRegex(ValueError, "missing"):
                cleared_font()


if __name__ == "__main__":
    unittest.main()
