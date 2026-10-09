"""Optional, data-only reviewer intake gate. No model calls or media capture."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import time
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone

PROCESS_SCOPE = str(uuid.uuid4())
PROMPT = "Describe visible changes and uncertainties, citing decoded frame numbers."
SCHEMA = {"observations": "nonempty text", "uncertainties": "text", "viewed_image_hashes": "all supplied hashes"}


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def clock():
    return datetime.now(timezone.utc).isoformat(), time.monotonic_ns(), PROCESS_SCOPE


class IntakeError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


class ReviewIntake:
    """Trusted controller storage; reviewer must never receive the directory itself.

    Callers attest complete context/events and image masking. This controller cannot
    observe unmanaged access or authenticate those attestations.
    """

    def __init__(self, root, clock_fn=clock):
        self.root = Path(root)
        self.clock = clock_fn
        if self.root.is_symlink() or not self.root.is_dir():
            raise IntakeError("INVALID_STORAGE")

    @classmethod
    def create(cls, root, run_id, reviewer_id, sealed_packet, clock_fn=clock):
        root = Path(root)
        root.mkdir(mode=0o700, parents=False, exist_ok=False)
        obj = cls(root, clock_fn)
        obj._write("sealed.json", sealed_packet)
        manifest = {"run_id": run_id, "reviewer_id": reviewer_id,
                    "nonce": str(uuid.uuid4()), "reviewer_token": str(uuid.uuid4()),
                    "sealed_sha256": digest(sealed_packet)}
        obj._write("manifest.json", manifest)
        obj._write("manifest-hash.json", digest(manifest))
        (root / "events").mkdir()
        (root / "event-hashes").mkdir()
        (root / "rejections").mkdir()
        (root / "candidates").mkdir()
        return obj

    def _write(self, name, value):
        path = self.root / name
        if path.parent.is_symlink() or not path.parent.is_dir():
            raise IntakeError("INVALID_STORAGE")
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(path, flags, 0o600)
        with os.fdopen(fd, "wb") as handle:
            handle.write(encoded(value))
            handle.flush()
            os.fsync(handle.fileno())

    def _read(self, name):
        path = self.root / name
        if path.is_symlink() or not path.is_file():
            raise IntakeError("TAMPER")
        try:
            return json.loads(path.read_bytes())
        except (ValueError, OSError):
            raise IntakeError("TAMPER") from None

    def _reject(self, code, candidate=None):
        self._write(f"rejections/{uuid.uuid4()}.json", {
            "code": code, "clock": self.clock(), "candidate": candidate})
        raise IntakeError(code)

    @contextmanager
    def _transaction(self):
        lock = self.root / ".lock"
        try:
            lock.mkdir()
        except FileExistsError:
            raise IntakeError("BUSY") from None
        try:
            if any((self.root / "rejections").iterdir()):
                raise IntakeError("INVALIDATED")
            try:
                for directory in ("events", "event-hashes", "rejections", "candidates"):
                    if (self.root / directory).is_symlink() or not (self.root / directory).is_dir():
                        raise IntakeError("TAMPER")
                manifest = self._read("manifest.json")
                if digest(manifest) != self._read("manifest-hash.json"):
                    raise IntakeError("TAMPER")
                if digest(self._read("sealed.json")) != manifest["sealed_sha256"]:
                    raise IntakeError("TAMPER")
                events = []
                previous = digest(manifest)
                if {path.name for path in (self.root / "events").iterdir()} != {path.name for path in (self.root / "event-hashes").iterdir()}:
                    raise IntakeError("TAMPER")
                for index, path in enumerate(sorted((self.root / "events").iterdir()), 1):
                    if path.name != f"{index:06d}.json":
                        raise IntakeError("TAMPER")
                    event = self._read(f"events/{path.name}")
                    if digest(event) != self._read(f"event-hashes/{path.name}"):
                        raise IntakeError("TAMPER")
                    if event["sequence"] != index or event["previous_sha256"] != previous:
                        raise IntakeError("TAMPER")
                    if events and (event["scope"] != events[-1]["scope"] or
                                   event["monotonic_ns"] <= events[-1]["monotonic_ns"] or
                                   event["utc"] < events[-1]["utc"]):
                        raise IntakeError("CLOCK_ANOMALY")
                    previous = digest(event)
                    events.append(event)
                for event in events:
                    for name, expected in event["files"].items():
                        if digest(self._read(name)) != expected:
                            raise IntakeError("TAMPER")
            except (KeyError, TypeError):
                self._reject("TAMPER")
            except IntakeError as error:
                self._reject(error.code)
            yield manifest, events, previous
        finally:
            lock.rmdir()

    def _append(self, events, previous, kind, files):
        utc, mono, scope = self.clock()
        if events and (scope != events[-1]["scope"] or mono <= events[-1]["monotonic_ns"] or utc < events[-1]["utc"]):
            self._reject("CLOCK_ANOMALY")
        event = {"sequence": len(events) + 1, "previous_sha256": previous,
                 "utc": utc, "monotonic_ns": mono, "scope": scope,
                 "kind": kind, "files": {name: digest(self._read(name)) for name in files}}
        self._write(f"events/{len(events)+1:06d}.json", event)
        self._write(f"event-hashes/{len(events)+1:06d}.json", digest(event))

    def start_a(self, images, *, extra_context=None, schema=None):
        with self._transaction() as (manifest, events, previous):
            if events:
                self._reject("INVALID_STATE")
            if extra_context is not None:
                self._reject("EARLY_EXPOSURE", extra_context)
            if schema is not None:
                self._reject("FORBIDDEN_STAGE_A_INPUT", schema)
            if not isinstance(images, list) or not images:
                self._reject("INCOMPLETE")
            for image in images:
                if not isinstance(image, dict) or set(image) != {"name", "sha256", "frame", "masked"} or image["masked"] is not True:
                    self._reject("FORBIDDEN_STAGE_A_INPUT", images)
                if not isinstance(image["name"], str) or not isinstance(image["sha256"], str) or not re.fullmatch(r"frame-[0-9]{6}\.png", image["name"]) or not re.fullmatch(r"[a-f0-9]{64}", image["sha256"]):
                    self._reject("FORBIDDEN_STAGE_A_INPUT", images)
                if type(image["frame"]) is not int or image["frame"] < 0:
                    self._reject("FORBIDDEN_STAGE_A_INPUT", images)
            packet = {"run_id": manifest["nonce"], "reviewer_id": manifest["reviewer_token"],
                      "nonce": manifest["nonce"], "prompt": PROMPT, "schema": SCHEMA,
                      "images": images}
            self._write("stage-a-input.json", packet)
            self._append(events, previous, "A_STARTED", ["stage-a-input.json"])
            return packet

    def record_access(self, kind):
        with self._transaction():
            self._reject("INDEPENDENCE_FAILURE" if kind == "other_reviewer" else "EARLY_EXPOSURE", kind)

    def commit_a(self, response, invocation):
        with self._transaction() as (manifest, events, previous):
            candidate = f"candidates/{uuid.uuid4()}.json"
            self._write(candidate, {"response": response, "invocation": invocation})
            if not isinstance(response, dict) or not isinstance(invocation, dict):
                self._reject("INCOMPLETE", candidate)
            if len(events) != 1 or events[-1]["kind"] != "A_STARTED":
                self._reject("INVALID_STATE", candidate)
            packet = self._read("stage-a-input.json")
            binding = {key: packet[key] for key in ("run_id", "reviewer_id", "nonce")}
            binding["input_sha256"] = digest(packet)
            if any(response.get(key) != value for key, value in binding.items()):
                self._reject("RUN_OR_EVIDENCE_MISMATCH", candidate)
            if not isinstance(response.get("observations"), str) or not response["observations"].strip() or not isinstance(response.get("uncertainties"), str):
                self._reject("INCOMPLETE", candidate)
            viewed = response.get("viewed_image_hashes")
            if not isinstance(viewed, list) or not all(isinstance(value, str) for value in viewed) or sorted(viewed) != sorted(image["sha256"] for image in packet["images"]):
                self._reject("INCOMPLETE", candidate)
            if invocation.get("fresh_session") is not True or invocation.get("context_sha256") != digest(packet) or invocation.get("events_complete") is not True:
                self._reject("UNVERIFIED", candidate)
            log = invocation.get("events")
            # Strict grammar: every other event (including denied/started tools) is
            # unverifiable. We never infer no access from absence of completed tools.
            if not isinstance(log, list) or not log:
                self._reject("UNVERIFIED", candidate)
            if log != [{"type": "session.started"}, {"type": "response.completed", "response_sha256": digest(response)}]:
                self._reject("UNVERIFIED", candidate)
            self._write("stage-a-response.json", response)
            self._write("stage-a-invocation.json", invocation)
            self._append(events, previous, "A_COMMITTED", ["stage-a-response.json", "stage-a-invocation.json"])

    def release_b(self):
        with self._transaction() as (_, events, previous):
            if len(events) != 2 or events[-1]["kind"] != "A_COMMITTED":
                self._reject("EARLY_EXPOSURE")
            self._append(events, previous, "B_RELEASED", [])
            return {"packet": self._read("sealed.json"),
                    "result": "PASS_INTAKE_ORDER_ONLY",
                    "outside_managed_intake": "UNVERIFIABLE",
                    "context_events_and_masking": "CALLER_ATTESTED"}
