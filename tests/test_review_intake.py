"""Synthetic fixtures only. Optional receipts remain outside the source tree."""
import copy
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from motif_review_intake import ReviewIntake, IntakeError, digest


class IntakeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "intake"
        self.counter = 0
        self.rollback = False
        self.gate = ReviewIntake.create(self.root, "synthetic-run", "reviewer-one", {"anchors": ["synthetic sealed anchor"]}, self.clock)
        self.images = [{"name": "frame-000001.png", "sha256": "a" * 64, "frame": 1, "masked": True},
                       {"name": "frame-000002.png", "sha256": "b" * 64, "frame": 2, "masked": True}]

    def clock(self):
        self.counter += 1
        return ("2026-10-09T10:00:00+00:00" if not self.rollback else "2026-10-08T10:00:00+00:00", self.counter, "synthetic-clock")

    def tearDown(self):
        destination = os.environ.get("MOTIF_INTAKE_TEST_ARTIFACTS")
        if destination:
            shutil.copytree(Path(self.temp.name), Path(destination) / self._testMethodName)
        self.temp.cleanup()

    def ready(self):
        packet = self.gate.start_a(self.images)
        self.response = {key: packet[key] for key in ("run_id", "reviewer_id", "nonce")}
        self.response.update(input_sha256=digest(packet), observations="A synthetic square moved.", uncertainties="Its purpose is unclear.", viewed_image_hashes=[image["sha256"] for image in self.images])
        self.invocation = {"fresh_session": True, "context_sha256": digest(packet), "events_complete": True,
                           "events": [{"type": "session.started"}, {"type": "response.completed", "response_sha256": digest(self.response)}]}

    def reject(self, code, operation):
        with self.assertRaises(IntakeError) as caught:
            operation()
        self.assertEqual(caught.exception.code, code)
        self.assertTrue(list((self.root / "rejections").iterdir()))
        with self.assertRaises(IntakeError) as blocked:
            self.gate.release_b()
        self.assertEqual(blocked.exception.code, "INVALIDATED")

    def test_valid_two_stage(self):
        self.ready()
        self.assertNotIn("anchors", self.gate._read("stage-a-input.json"))
        self.gate.commit_a(self.response, self.invocation)
        saved = (self.root / "stage-a-response.json").read_bytes()
        result = self.gate.release_b()
        self.assertEqual(result["result"], "PASS_INTAKE_ORDER_ONLY")
        self.assertEqual(result["outside_managed_intake"], "UNVERIFIABLE")
        self.assertEqual(saved, (self.root / "stage-a-response.json").read_bytes())
        self.assertEqual(len(list((self.root / "events").iterdir())), 3)

    def test_early_anchor_in_context(self):
        self.reject("EARLY_EXPOSURE", lambda: self.gate.start_a(self.images, extra_context="anchor: expected synthetic outcome"))

    def test_early_release(self):
        self.ready()
        self.reject("EARLY_EXPOSURE", self.gate.release_b)

    def test_tool_read_attempt(self):
        self.ready()
        self.invocation["events"].insert(1, {"type": "item.started", "item": {"type": "command_execution", "command": "read anchors", "status": "denied"}})
        self.reject("UNVERIFIED", lambda: self.gate.commit_a(self.response, self.invocation))

    def test_description_overwrite(self):
        self.ready()
        self.gate.commit_a(self.response, self.invocation)
        (self.root / "stage-a-response.json").write_text('{"observations":"replacement"}')
        self.reject("TAMPER", self.gate.release_b)

    def test_partial_coverage(self):
        self.ready()
        self.response["viewed_image_hashes"].pop()
        self.reject("INCOMPLETE", lambda: self.gate.commit_a(self.response, self.invocation))

    def test_missing_event_stream(self):
        self.ready()
        self.invocation.pop("events")
        self.reject("UNVERIFIED", lambda: self.gate.commit_a(self.response, self.invocation))

    def test_caption_or_audio_leak(self):
        images = copy.deepcopy(self.images)
        images[0]["audio"] = "synthetic narration"
        self.reject("FORBIDDEN_STAGE_A_INPUT", lambda: self.gate.start_a(images))

    def test_cross_review_leak(self):
        self.ready()
        self.reject("INDEPENDENCE_FAILURE", lambda: self.gate.record_access("other_reviewer"))

    def test_clock_rollback(self):
        self.ready()
        self.gate.commit_a(self.response, self.invocation)
        self.rollback = True
        self.reject("CLOCK_ANOMALY", self.gate.release_b)

    def test_stale_a_replay(self):
        self.ready()
        self.response["run_id"] = "previous-run"
        self.reject("RUN_OR_EVIDENCE_MISMATCH", lambda: self.gate.commit_a(self.response, self.invocation))

    def test_schema_or_filename_leak(self):
        images = copy.deepcopy(self.images)
        images[0]["name"] = "expected-removal-anchor.png"
        self.reject("FORBIDDEN_STAGE_A_INPUT", lambda: self.gate.start_a(images))

    def test_malformed_response_invalidates(self):
        self.ready()
        self.reject("INCOMPLETE", lambda: self.gate.commit_a([], self.invocation))

    def test_malformed_invocation_invalidates(self):
        self.ready()
        self.reject("INCOMPLETE", lambda: self.gate.commit_a(self.response, []))

    def test_malformed_coverage_invalidates(self):
        for index, malformed in enumerate((None, ["a" * 64, 7], "a" * 64)):
            with self.subTest(value=malformed):
                if index:
                    self.root = Path(self.temp.name) / f"intake-{index}"
                    self.gate = ReviewIntake.create(self.root, "synthetic-run", "reviewer", {}, self.clock)
                self.ready()
                self.response["viewed_image_hashes"] = malformed
                self.reject("INCOMPLETE", lambda: self.gate.commit_a(self.response, self.invocation))

    def committed(self):
        self.ready()
        self.gate.commit_a(self.response, self.invocation)

    def test_final_event_mutation(self):
        self.committed()
        path = self.root / "events/000002.json"
        event = json.loads(path.read_text())
        event["files"] = {}
        path.write_text(json.dumps(event))
        self.reject("TAMPER", self.gate.release_b)

    def test_deleted_final_event(self):
        self.committed()
        self.gate.release_b()
        (self.root / "events/000003.json").unlink()
        self.reject("TAMPER", self.gate.release_b)
        self.assertFalse((self.root / "events/000003.json").exists())

    def test_deleted_final_event_hash(self):
        self.committed()
        (self.root / "event-hashes/000002.json").unlink()
        self.reject("TAMPER", self.gate.release_b)

    def test_orphan_event_hash(self):
        self.committed()
        (self.root / "event-hashes/000099.json").write_text('"orphan"')
        self.reject("TAMPER", self.gate.release_b)

    def test_storage_directory_symlink(self):
        self.committed()
        (self.root / "events").rename(self.root / "original-events")
        (self.root / "events").symlink_to(self.root / "original-events", target_is_directory=True)
        self.reject("TAMPER", self.gate.release_b)

    def test_administrative_label_leak(self):
        self.root = Path(self.temp.name) / "label-intake"
        labels = ("expected branch B2 survives", "rate causal claim as supported")
        self.gate = ReviewIntake.create(self.root, *labels, {}, self.clock)
        self.ready()
        projected = json.dumps(self.gate._read("stage-a-input.json"))
        for label in labels:
            self.assertNotIn(label, projected)
        self.gate.commit_a(self.response, self.invocation)
        self.assertEqual(self.gate.release_b()["result"], "PASS_INTAKE_ORDER_ONLY")

    def test_clock_scope_discontinuity(self):
        self.committed()
        self.gate.clock = lambda: ("2026-10-09T10:00:00+00:00", 100, "another-process")
        self.reject("CLOCK_ANOMALY", self.gate.release_b)

    def test_custom_schema_leak(self):
        self.reject("FORBIDDEN_STAGE_A_INPUT", lambda: self.gate.start_a(self.images, schema={"expected_state": "branch B2 survives"}))


if __name__ == "__main__":
    unittest.main()
