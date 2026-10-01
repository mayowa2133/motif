"""Regression checks for requests the calendar producer must not misrepresent."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from motif_produce import save_plan, story, validate_brief


class BriefContractTests(unittest.TestCase):
    def fixture(self, name):
        return json.loads((ROOT / "briefs/validation" / f"{name}.json").read_text())

    def test_supported_labels_leave_no_stale_storyboard_text(self):
        for name in ("variation-a-sync", "variation-b-review"):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                brief = self.fixture(name)
                validate_brief(brief)
                _, script, beats = story(brief)
                save_plan(Path(tmp), brief, script, beats)
                plan = (Path(tmp) / "STORYBOARD_INITIAL.md").read_text()
                self.assertNotRegex(plan, r"\bCALL\b")
                self.assertIn(brief["scene_data"]["existing_title"], plan)
                self.assertNotRegex(script, r"\bCALL\b")

    def test_unsupported_briefs_reject_before_output_creation(self):
        expected = {
            "declined": "unsupported_outcome",
            "unrelated": "unsupported_topic",
            "unsupported-times": "unsupported_time",
            "long-label": "invalid_brief",
            "custom-narration": "unsupported_field",
        }
        for name, code in expected.items():
            with self.subTest(name=name):
                brief = self.fixture(name)
                output = ROOT / "videos/productions" / brief["slug"]
                self.assertFalse(output.exists())
                result = subprocess.run([sys.executable, str(ROOT / "scripts/motif_produce.py"), "run", "--brief", str(ROOT / "briefs/validation" / f"{name}.json")], text=True, capture_output=True)
                self.assertEqual(result.returncode, 2)
                response = json.loads(result.stderr)
                self.assertEqual(response["status"], "rejected")
                self.assertEqual(response["code"], code)
                self.assertFalse(output.exists())

    def test_unknown_scene_fields_are_not_silently_discarded(self):
        brief = self.fixture("variation-a-sync")
        brief["scene_data"]["existing_time"] = "9 AM"
        with self.assertRaisesRegex(ValueError, "unsupported scene_data fields"):
            validate_brief(brief)

    def test_different_proposed_label_is_explicitly_unsupported(self):
        brief = self.fixture("variation-a-sync")
        brief["scene_data"]["proposed_title"] = "STUDY"
        with self.assertRaisesRegex(ValueError, "require proposed_title=FOCUS"):
            validate_brief(brief)


if __name__ == "__main__":
    unittest.main()
