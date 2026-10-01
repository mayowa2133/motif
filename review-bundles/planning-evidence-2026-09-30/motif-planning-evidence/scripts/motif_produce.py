#!/usr/bin/env python3
"""One local entry point for a narrowly supported Motif production template.

The calendar proposal story is selected explicitly in the structured brief. The
command writes the storyboard before narration or rendering, then checks the
first encoded mix and audio-finishes the combined soundtrack if needed.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEMO3 = ROOT / "videos/motif-calendar-reel"  # read-only approved template source
PIN = "0.8.96"
TARGET_I = -16.0
PEAK_CEILING = -1.5


class BriefValidationError(ValueError):
    """A request outside the supported template; reject before project creation."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def command(args: list[str], cwd: Path, env: dict[str, str] | None = None, log: Path | None = None) -> str:
    process = subprocess.run(args, cwd=cwd, env=env, text=True, capture_output=True)
    output = process.stdout + process.stderr
    if log:
        log.write_text(output)
    if process.returncode:
        raise RuntimeError(f"command failed ({process.returncode}): {' '.join(args)}\n{output[-2500:]}")
    return output


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def video_hash(path: Path) -> str:
    result = command(["ffmpeg", "-v", "error", "-i", str(path), "-map", "0:v:0", "-c:v", "copy", "-f", "hash", "-hash", "sha256", "-"], ROOT)
    return result.strip().split("=", 1)[1]


def probe(path: Path) -> dict:
    result = command(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=index,codec_type,width,height,nb_frames,duration", "-of", "json", str(path)], ROOT)
    return json.loads(result)


def loudness(path: Path) -> dict[str, float]:
    result = command(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-vn", "-af", "loudnorm=I=-16:TP=-2:LRA=11:print_format=json", "-f", "null", "-"], ROOT)
    match = re.search(r'\{\s*"input_i"\s*:.*?\}', result, re.S)
    if not match:
        raise RuntimeError("FFmpeg did not return encoded loudness measurements")
    data = json.loads(match.group())
    return {"integrated_lufs": float(data["input_i"]), "true_peak_dbtp": float(data["input_tp"]), "lra_lu": float(data["input_lra"])}


def validate_brief(brief: dict) -> None:
    required = ("slug", "message", "audience", "intended_duration_seconds", "aspect_ratio", "style", "voice", "template", "scene_data")
    if not isinstance(brief, dict):
        raise ValueError("brief must be a JSON object")
    extra = set(brief) - set(required)
    if extra:
        raise BriefValidationError("unsupported_field", f"unsupported brief fields: {', '.join(sorted(extra))}; custom narration and calendar times are not supported")
    missing = [key for key in required if key not in brief]
    if missing:
        raise ValueError(f"missing brief fields: {', '.join(missing)}")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", brief["slug"]):
        raise ValueError("slug must be lowercase hyphenated text")
    if brief["template"] != "calendar-open-slot":
        raise ValueError("supported template: calendar-open-slot")
    if (brief["aspect_ratio"], brief["style"], brief["voice"]) != ("9:16", "motif-v1", "af_nova"):
        raise ValueError("current preset requires 9:16, motif-v1, and af_nova")
    if not 12 <= float(brief["intended_duration_seconds"]) <= 18:
        raise ValueError("intended duration must be between 12 and 18 seconds")
    if not all(isinstance(brief[k], str) and brief[k].strip() for k in ("message", "audience")):
        raise ValueError("message and audience must be nonempty")
    message = brief["message"].lower()
    if re.search(r"\b(?:declin\w*|reject\w*|refus\w*|denied|deny|denies|cancel\w*)\b|\b(?:without|no)\s+(?:approval|permission)\b|\b(?:does not|doesn't|never)\s+approv\w*", message):
        raise BriefValidationError("unsupported_outcome", "calendar-open-slot supports approval followed by booking; a declined, cancelled, or unapproved proposal is unsupported and will not be rendered")
    if not re.search(r"\b(?:calendar|schedule)\b", message):
        raise BriefValidationError("unsupported_topic", "calendar-open-slot only supports a calendar opening, focus suggestion, and approval before booking")
    times = re.findall(r"\b(\d{1,2})(?::(\d{2}))?\s*([ap])\.?m\.?\b", message)
    if any((hour, minute, period) not in (("3", "", "p"), ("4", "", "p"), ("3", "00", "p"), ("4", "00", "p")) for hour, minute, period in times):
        raise BriefValidationError("unsupported_time", "calendar times are fixed at 3 PM and 4 PM; the requested times cannot be represented")
    if not (re.search(r"\bopen\s+(?:hour|slot|time)\b", message) and "focus" in message and ("approv" in message or "permission" in message)):
        raise BriefValidationError("unsupported_topic", "calendar-open-slot requires an open hour, focus suggestion, and approval before booking")
    if not isinstance(brief["scene_data"], dict):
        raise ValueError("scene_data must be a JSON object")
    extra_scene = set(brief["scene_data"]) - {"existing_title", "proposed_title"}
    if extra_scene:
        raise BriefValidationError("unsupported_field", f"unsupported scene_data fields: {', '.join(sorted(extra_scene))}; calendar times and outcomes are fixed")
    for key in ("existing_title", "proposed_title"):
        label = brief["scene_data"].get(key)
        if not isinstance(label, str) or not re.fullmatch(r"[A-Z]{2,6}", label):
            raise ValueError(f"scene_data.{key} must be 2–6 uppercase letters")
    if brief["scene_data"]["proposed_title"] != "FOCUS":
        raise ValueError("the current script and captions require proposed_title=FOCUS")


def story(brief: dict) -> tuple[dict, str, list[dict]]:
    existing = brief["scene_data"]["existing_title"]
    proposed = brief["scene_data"]["proposed_title"]
    scene = {
        "mode": "open_slot", "existing_title": existing, "proposed_title": proposed,
        "title": f"Motif · an open hour becomes {proposed.lower()} time after approval",
        "aria": f"A {existing.lower()} card occupies 3 PM. Four PM is empty. Motif Bot suggests a {proposed.lower()} block, waits for a person's approval, then the solid block appears at 4 PM.",
        "headlines": ["AN HOUR OPENS", "A FOCUS PLAN", "YOUR APPROVAL", "BLOCK BOOKED"],
    }
    script = ("Your afternoon has an open hour. An assistant spots it and suggests a focus block. "
              "But the slot stays empty. It waits for your approval. Only then does the focus block join your calendar.")
    beats = [
        {"subject": "The paper calendar", "action": f"A {existing} card lands at 3 PM; the 4 PM row gains a teal outline.", "before_after": "An unmarked calendar becomes one booking plus a visibly empty hour.", "focal_detail": "The empty 4 PM row beside the solid 3 PM card.", "consequence": "Bot has a specific opening to consider."},
        {"subject": "Bot and the empty row", "action": "Bot notices and points to the opening.", "before_after": "Unnoticed gap becomes a highlighted opportunity.", "focal_detail": "Bot's pointing pose and 4 PM outline together.", "consequence": "A suggestion becomes possible."},
        {"subject": "A dashed proposal slip", "action": "A pale dashed FOCUS slip appears at 4 PM while no solid FOCUS card exists.", "before_after": "Empty hour becomes a proposed, still unbooked hour.", "focal_detail": "Dashed slip inside the outlined row.", "consequence": "The person must decide before anything is booked."},
        {"subject": "The person's fingertip", "action": "It presses an initially empty APPROVE tab; the check appears after contact.", "before_after": "Unapproved proposal becomes approved proposal.", "focal_detail": "Finger, tab, and still-dashed proposal in one view.", "consequence": "Booking is now authorized."},
        {"subject": "The calendar's 4 PM row", "action": "The dashed slip fades and a solid FOCUS card appears after approval.", "before_after": "Suggested block becomes booked block.", "focal_detail": f"Solid card replacing the pale proposal; 3 PM {existing} remains.", "consequence": "A focus hour is actually on the calendar."},
    ]
    return scene, script, beats


def save_plan(project: Path, brief: dict, script: str, beats: list[dict]) -> None:
    lines = ["# Initial storyboard — saved before narration and finished render", "", f"Brief: {brief['message']}", f"Audience: {brief['audience']}", f"Narration: “{script}”", "", f"The scene uses the approved paper calendar template. 3 PM and 4 PM, {brief['scene_data']['existing_title']} and FOCUS, and APPROVE are necessary labels. The empty row, dashed proposal, human press, and solid booked card carry the outcome through visible action.", ""]
    for i, beat in enumerate(beats, 1):
        lines += [f"## Beat {i}", ""] + [f"- **{key.replace('_',' ').title()}:** {value}" for key, value in beat.items()] + [""]
    (project / "STORYBOARD_INITIAL.md").write_text("\n".join(lines))
    checks = {
        "five_parts_per_beat": all(set(beat) == {"subject", "action", "before_after", "focal_detail", "consequence"} for beat in beats),
        "evidence_before_result_label": "dashed" in beats[2]["action"].lower() and "solid" in beats[4]["action"].lower(),
        "approval_before_booking": "after approval" in beats[4]["action"].lower(),
        "visible_ending_action": "appears" in beats[4]["action"].lower(),
    }
    if not all(checks.values()):
        raise RuntimeError(f"storyboard gate failed: {checks}")
    (project / "STORYBOARD_REVIEW.md").write_text("# Pre-render storyboard review\n\n" + "\n".join(f"- {key.replace('_',' ')}: {'PASS' if value else 'FAIL'}" for key, value in checks.items()) + "\n\nNo planning revision was needed for this template run. This is a deterministic template review, not independent creative judgment. The initial storyboard remains untouched.\n")


def make_events(project: Path, voice_duration: float, scene: dict, words: list[dict]) -> None:
    spec = copy.deepcopy(json.loads((DEMO3 / "scene-events.json").read_text()))
    spec["events"] = [event for event in spec["events"] if not (event["target"] == "#focus-card" and event["time"] < 9.0) and not (event["target"] == "#overlap-bracket" and event["time"] < 9.0)]
    for event in spec["events"]:
        if event["target"] == "#focus-card" and event["time"] > 9:
            if event["time"] < 9.3:
                event["action"] = "POP_IN"
                event["params"] = {"duration": 0.55, "overshoot": 1.04}
                event["time"] = 9.36
            else:
                event["action"] = "SET"
                event["params"] = {"props": {"rotation": 0}}
        if event["target"] == "#proposal-slip" and event["time"] > 9 and event["action"] == "TWEEN":
            event["time"] = 9.01
            event["params"]["duration"] = 0.25
        if event["target"] == "#headline-wait" and event["action"] == "SET":
            event["time"] = 9.99
        if event["target"] == "#headline-done" and event["action"] == "POP_IN":
            event["time"] = 10.02
        if event["target"] == "#human-finger" and event["action"] == "FROM_TO":
            event["time"] = 6.55
        if event["target"] == "#human-finger" and event["action"] == "TWEEN" and event["time"] == 8.42:
            event["time"] = 7.45
        if event["target"] == "#approval-tab" and event["action"] == "TWEEN":
            event["time"] = 7.69
        if event["target"] in ("#approval-glow", "#approval-check") and event["action"] == "POP_IN":
            event["time"] = 7.8
        if event["target"] == "#human-finger" and event["action"] == "TWEEN" and event["time"] == 8.82:
            event["time"] = 7.9
        if event["target"] == "#human-finger" and event["action"] == "TWEEN" and event["time"] == 9.35:
            event["time"] = 7.9
    spec["events"].append({"time": 1.18, "target": "#overlap-bracket", "action": "POP_IN", "params": {"duration": 0.3, "overshoot": 1.02}})
    spec["events"].sort(key=lambda item: item["time"])
    captions = [
        ("Your afternoon", "afternoon", "teal"), ("has an open hour", "open", "teal"),
        ("assistant spots it", "spots", "teal"), ("suggests a focus block", "focus", "teal"),
        ("slot stays empty", "stays empty", "blue"), ("waits for your approval", "approval", "teal"),
        ("Only then", "then", "teal"), ("focus block joins calendar", "joins", "teal"),
    ]
    for item, (text, emphasis, color) in zip(spec["captions"], captions, strict=True):
        item.update(text=text, emphasis=emphasis, color=color)
    scale = voice_duration / 11.349
    for event in spec["events"]:
        event["time"] = round(event["time"] * scale, 3)
        if "duration" in event["params"]:
            event["params"]["duration"] = round(event["params"]["duration"] * scale, 3)
    for caption in spec["captions"]:
        caption["start"] = round(caption["start"] * scale, 3)
        caption["end"] = round(caption["end"] * scale, 3)
    # The narration script is fixed within this template. Align handoffs to
    # actual words rather than assuming Demo 03's speech rhythm repeats.
    anchors = [0, 2, 6, 11, 15, 20, 25, 31]
    expected = ["your", "has", "an", "suggests", "but", "it", "only", "join"]
    if len(words) != 34 or any(re.sub(r"[^a-z]", "", words[i]["text"].lower()) != word for i, word in zip(anchors, expected)):
        raise RuntimeError("narration alignment no longer matches the supported template script")
    starts = [round(words[i]["start"], 3) for i in anchors]
    for i, caption in enumerate(spec["captions"]):
        caption["start"] = starts[i]
        caption["end"] = starts[i + 1] if i + 1 < len(starts) else round(min(voice_duration, words[-1]["end"] + 0.15), 3)
    caption_events = {event["target"]: event for event in spec["events"] if event["target"].startswith("#caption-") and event["action"] == "CAPTION_REPLACE"}
    for i, start in enumerate(starts):
        caption_events[f"#caption-{i}"]["time"] = start
    for beat in spec["sceneBeats"]:
        beat["start"] = round(beat["start"] * scale, 3)
        beat["end"] = round(beat["end"] * scale, 3)
    spec["durationSec"] = round(max(12.0, voice_duration + 1.45), 2)
    spec["sceneBeats"][-1]["end"] = spec["durationSec"]
    spec["narration"] = {"file": "assets/voice/narration-af-nova.wav", "voiceStart": 0, "voiceEnd": voice_duration, "status": "local-kokoro-duration-scaled-template"}
    approval = min(e["time"] for e in spec["events"] if e["target"] == "#approval-check" and e["action"] == "POP_IN")
    booking = min(e["time"] for e in spec["events"] if e["target"] == "#focus-card" and e["action"] == "POP_IN")
    only_then = spec["captions"][6]["start"]
    press_complete = min(e["time"] + e["params"]["duration"] for e in spec["events"] if e["target"] == "#human-finger" and e["action"] == "TWEEN" and e["params"].get("to", {}).get("y") == 35)
    finger_clear = min(e["time"] + e["params"]["duration"] for e in spec["events"] if e["target"] == "#human-finger" and e["action"] == "TWEEN" and e["params"].get("to", {}).get("opacity") == 0)
    booking_complete = max(e["time"] + e["params"].get("duration", 0) for e in spec["events"] if e["target"] == "#focus-card" and e["action"] == "POP_IN")
    result_label = min(e["time"] for e in spec["events"] if e["target"] == "#headline-done" and e["action"] == "POP_IN")
    proposal_gone = max(e["time"] + e["params"].get("duration", 0) for e in spec["events"] if e["target"] == "#proposal-slip" and e["action"] == "TWEEN" and e["params"].get("to", {}).get("opacity") == 0)
    if approval >= booking:
        raise RuntimeError("permission ordering gate failed")
    if not press_complete < approval < finger_clear < only_then:
        raise RuntimeError("press, check, hand withdrawal, and spoken 'Only then' are out of order")
    if proposal_gone >= booking:
        raise RuntimeError("proposal text would overlap the booked card")
    if booking_complete >= result_label:
        raise RuntimeError("result headline would precede visible booking")
    spec["events"].sort(key=lambda event: event["time"])
    (project / "scene-events.json").write_text(json.dumps(spec, indent=2) + "\n")
    source = json.loads((DEMO3 / "audio-plan.json").read_text())
    source["tracks"][0]["duration"] = voice_duration
    for track in source["tracks"][1:]:
        track["start"] = round(track["start"] * scale, 3)
    (project / "audio-plan.json").write_text(json.dumps(source, indent=2) + "\n")


def prepare_project(project: Path, scene: dict, script: str) -> None:
    (project / "assets/voice").mkdir(parents=True)
    (project / "assets/sfx").mkdir(parents=True)
    (project / "renders").mkdir()
    for name in ("gsap.min.js", "motion-engine.js", "motion-primitives.js"):
        shutil.copy2(DEMO3 / "assets" / name, project / "assets" / name)
    for name in ("pop.mp3", "click-soft.mp3", "click.mp3", "whoosh-short.mp3", "chime.mp3"):
        shutil.copy2(DEMO3 / "assets/sfx" / name, project / "assets/sfx" / name)
    shutil.copy2(DEMO3 / "package.json", project / "package.json")
    shutil.copy2(DEMO3 / "hyperframes.json", project / "hyperframes.json")
    (project / "scene-data.json").write_text(json.dumps(scene, indent=2) + "\n")
    (project / "assets/voice/narration.txt").write_text(script + "\n")


def write_provenance(project: Path) -> None:
    record = json.loads((DEMO3 / "audio-source-license-manifest.json").read_text())
    record["narration"]["rawSha256"] = sha(project / "assets/voice/narration-af-nova.wav")
    record["narration"]["status"] = "new local Kokoro take for the calendar-open-slot template"
    record["music"] = {"included": False, "reason": "The brief is carried by narration and previously cleared paper/click effects."}
    (project / "audio-source-license-manifest.json").write_text(json.dumps(record, indent=2) + "\n")


def produce(brief_path: Path) -> Path:
    brief = json.loads(brief_path.read_text())
    validate_brief(brief)
    project = ROOT / "videos/productions" / brief["slug"]
    if project.exists():
        raise FileExistsError(f"output exists; choose a fresh slug to preserve the prior run: {project}")
    project.mkdir(parents=True)
    (project / "brief.json").write_text(json.dumps(brief, indent=2) + "\n")
    scene, script, beats = story(brief)
    save_plan(project, brief, script, beats)  # before TTS, animation, or render
    prepare_project(project, scene, script)
    env = os.environ.copy()
    if "HYPERFRAMES_PYTHON" not in env:
        candidate = Path.home() / ".cache/motif-kokoro-venv/bin/python"
        if not candidate.exists():
            raise RuntimeError("set HYPERFRAMES_PYTHON to a Python with kokoro-onnx")
        env["HYPERFRAMES_PYTHON"] = str(candidate)
    command(["npx", "--yes", f"hyperframes@{PIN}", "tts", "--text-file=assets/voice/narration.txt", "--voice=af_nova", "--speed=0.85", "--output=assets/voice/narration-af-nova.wav", "--json"], project, env, project / "tts.log")
    voice = project / "assets/voice/narration-af-nova.wav"
    write_provenance(project)
    voice_duration = round(float(probe(voice)["format"]["duration"]), 3)
    command(["npx", "--yes", f"hyperframes@{PIN}", "transcribe", "assets/voice/narration-af-nova.wav", "--language", "en", "--json"], project, log=project / "alignment.log")
    words = json.loads((project / "assets/voice/transcript.json").read_text())
    make_events(project, voice_duration, scene, words)
    command(["python3", str(ROOT / "scripts/motif_calendar_template.py"), str(project)], ROOT, log=project / "assembly.log")
    command(["npm", "run", "check"], project, log=project / "check.log")
    first = project / "renders/first.mp4"
    command(["npm", "run", "render", "--", "-o", str(first), "--skill=general-video", "-q", "delivery"], project, log=project / "render.log")
    initial = loudness(first)
    first_probe = probe(first)
    picture_duration = float(first_probe["format"]["duration"])
    soundtrack_duration = float(next(stream["duration"] for stream in first_probe["streams"] if stream["codec_type"] == "audio"))
    (project / "FIRST_RENDER_REVIEW.md").write_text(
        "# First encoded render review\n\n"
        f"Video: [first.mp4](renders/first.mp4). Encoded mix: {initial['integrated_lufs']:.2f} LUFS, {initial['true_peak_dbtp']:.2f} dBTP. "
        "This automated gate checks the visual event order in scene-events.json; it does not replace mobile-frame inspection or listening. "
        "The first render is preserved before any audio finishing.\n")
    gain = min(TARGET_I - initial["integrated_lufs"], PEAK_CEILING - 0.1 - initial["true_peak_dbtp"])
    final = project / "renders/final.mp4"
    finish_method = "combined-mix linear gain"
    command(["ffmpeg", "-hide_banner", "-y", "-i", str(first), "-map", "0:v:0", "-map", "0:a:0", "-map_metadata", "0", "-c:v", "copy", "-af", f"volume={gain:.3f}dB", "-c:a", "aac", "-b:a", "192k", "-t", f"{picture_duration:.6f}", "-movflags", "+faststart", str(final)], ROOT, log=project / "audio-finish.log")
    measured = loudness(final)
    if abs(measured["integrated_lufs"] - TARGET_I) > 0.8 or measured["true_peak_dbtp"] > PEAK_CEILING:
        # A transient can block a simple gain rise. Process the already mixed
        # soundtrack as one signal; never normalize voice and effects separately.
        finish_method = "combined-mix loudnorm with measured calibration"
        candidate = project / "renders/audio-loudnorm-candidate.mp4"
        # Leave extra true-peak margin for AAC intersample overshoot. Trim the
        # processor's tail to the source soundtrack and preserve picture length.
        filter_base = f"TP={PEAK_CEILING - 0.3}:LRA=11,atrim=duration={soundtrack_duration:.6f}"
        command(["ffmpeg", "-hide_banner", "-y", "-i", str(first), "-map", "0:v:0", "-map", "0:a:0", "-map_metadata", "0", "-c:v", "copy", "-af", f"loudnorm=I={TARGET_I}:{filter_base}", "-c:a", "aac", "-b:a", "192k", "-t", f"{picture_duration:.6f}", "-movflags", "+faststart", str(candidate)], ROOT, log=project / "audio-loudnorm.log")
        calibrated = loudness(candidate)
        if abs(calibrated["integrated_lufs"] - TARGET_I) > 0.8 or calibrated["true_peak_dbtp"] > PEAK_CEILING:
            adjusted_target = TARGET_I + (TARGET_I - calibrated["integrated_lufs"])
            command(["ffmpeg", "-hide_banner", "-y", "-i", str(first), "-map", "0:v:0", "-map", "0:a:0", "-map_metadata", "0", "-c:v", "copy", "-af", f"loudnorm=I={adjusted_target:.2f}:{filter_base}", "-c:a", "aac", "-b:a", "192k", "-t", f"{picture_duration:.6f}", "-movflags", "+faststart", str(final)], ROOT, log=project / "audio-loudnorm-calibrated.log")
        else:
            shutil.copy2(candidate, final)
        measured = loudness(final)
    final_probe = probe(final)
    same_picture = video_hash(first) == video_hash(final)
    same_duration = abs(float(first_probe["format"]["duration"]) - float(final_probe["format"]["duration"])) < 0.02
    level_pass = abs(measured["integrated_lufs"] - TARGET_I) <= 0.8
    peak_pass = measured["true_peak_dbtp"] <= PEAK_CEILING
    duration_pass = 12 <= float(final_probe["format"]["duration"]) <= 18
    result = {
        "brief": str(brief_path.relative_to(ROOT)), "first_render": str(first.relative_to(ROOT)), "final_render": str(final.relative_to(ROOT)),
        "first_audio": initial, "initial_linear_gain_attempt_db": round(gain, 3), "finishing_method": finish_method, "final_audio": measured,
        "target_lufs": TARGET_I, "true_peak_ceiling_dbtp": PEAK_CEILING,
        "checks": {"storyboard_and_event_order": True, "word_aligned_captions": True, "integrated_loudness": level_pass, "true_peak": peak_pass, "same_encoded_video_stream": same_picture, "same_duration": same_duration, "requested_duration_range": duration_pass},
        "first_sha256": sha(first), "final_sha256": sha(final), "video_stream_sha256": video_hash(final),
        "subjective_listening": "not assessed",
    }
    (project / "verification.json").write_text(json.dumps(result, indent=2) + "\n")
    if not all(result["checks"].values()):
        raise RuntimeError(f"encoded output failed production checks: {result['checks']}")
    candidate = project / "renders/audio-loudnorm-candidate.mp4"
    if candidate.exists():
        candidate.unlink()
    command(["ffmpeg", "-hide_banner", "-y", "-i", str(final), "-vf", "scale=360:640", "-c:v", "libx264", "-crf", "22", "-preset", "medium", "-c:a", "copy", "-movflags", "+faststart", str(project / "renders/mobile.mp4")], ROOT, log=project / "mobile.log")
    return project


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["run", "validate"])
    parser.add_argument("--brief", required=True, type=Path)
    args = parser.parse_args()
    try:
        if args.action == "validate":
            validate_brief(json.loads(args.brief.read_text()))
            print(json.dumps({"status": "supported", "template": "calendar-open-slot", "configurable_scene_fields": ["existing_title"], "fixed_times": ["3 PM", "4 PM"], "fixed_proposed_title": "FOCUS", "fixed_outcome": "approval_then_booking", "narration": "fixed_template_script"}))
        else:
            output = produce(args.brief.resolve())
            print(f"PASS {output / 'renders/final.mp4'}")
    except ValueError as error:
        print(json.dumps({"status": "rejected", "code": getattr(error, "code", "invalid_brief"), "reason": str(error)}), file=sys.stderr)
        raise SystemExit(2)
