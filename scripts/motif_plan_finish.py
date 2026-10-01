"""Existing encoded combined-mix finishing, adapted for a plan duration range.

The legacy producer is preserved; this stage uses its command/probe/hash/level tools.
"""
import shutil
import json
from motif_produce import ROOT, TARGET_I, PEAK_CEILING, command, loudness, probe, video_hash, sha

def finish(project, first, duration_range):
    initial = loudness(first)
    first_probe = probe(first)
    picture_duration = float(first_probe["format"]["duration"])
    soundtrack_duration = float(next(stream["duration"] for stream in first_probe["streams"] if stream["codec_type"] == "audio"))
    (project / "FIRST_RENDER_REVIEW.md").write_text(
        "# First encoded render review\n\n"
        f"Video: [first.mp4](renders/first.mp4). Encoded mix: {initial['integrated_lufs']:.2f} LUFS, {initial['true_peak_dbtp']:.2f} dBTP. "
        "This finishing stage measures encoded media only. Pre-render plan/events/alignment checks are recorded separately in pre-render-checks.json; rendered visual inspection and listening are not inferred from those checks. "
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
    duration_pass = duration_range[0] <= float(final_probe["format"]["duration"]) <= duration_range[1]
    result = {
        "production_plan": str((project / "production-plan.json").relative_to(ROOT)), "first_render": str(first.relative_to(ROOT)), "final_render": str(final.relative_to(ROOT)),
        "first_audio": initial, "initial_linear_gain_attempt_db": round(gain, 3), "finishing_method": finish_method, "final_audio": measured,
        "target_lufs": TARGET_I, "true_peak_ceiling_dbtp": PEAK_CEILING,
        "pre_render": {"record":"pre-render-checks.json", "sha256":sha(project/'pre-render-checks.json'), "scope":"Earlier structured plan/event/alignment checks, not post-encode visual measurement"},
        "encoded_measurements": {"integrated_loudness": level_pass, "true_peak": peak_pass, "same_encoded_video_stream": same_picture, "same_duration": same_duration, "requested_duration_range": duration_pass},
        "first_sha256": sha(first), "final_sha256": sha(final), "video_stream_sha256": video_hash(final),
        "subjective_listening": "not assessed",
        "human_visual_review": "not assessed",
    }
    (project / "verification.json").write_text(json.dumps(result, indent=2) + "\n")
    if not all(result["encoded_measurements"].values()):
        raise RuntimeError(f"encoded output failed production checks: {result['encoded_measurements']}")
    candidate = project / "renders/audio-loudnorm-candidate.mp4"
    if candidate.exists():
        candidate.unlink()
    command(["ffmpeg", "-hide_banner", "-y", "-i", str(final), "-vf", "scale=360:640", "-c:v", "libx264", "-crf", "22", "-preset", "medium", "-c:a", "copy", "-movflags", "+faststart", str(project / "renders/mobile.mp4")], ROOT, log=project / "mobile.log")
    return final
