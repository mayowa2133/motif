# Original reel pipeline (brief to review render, no per-film code)

```
python scripts/motif_reel.py run --brief quality/benchmark-briefs/bench-sqlite-everywhere.json \
    --out /tmp/reels --render --tts-python <python with kokoro-onnx>
```

A reel is data only. The brief holds the following:
- the narration lines
- a cited fact packet
- optional visual hints per beat: rig and its labels, room, insert, costume, palette

Everything drawn comes from the library:

| Library | Module | Status file |
|---|---|---|
| 10 rigs with proven contacts | `scripts/motif_rigs/` | `assets/library/approvals.json` |
| 8 rooms, set solver, empty-field check | `scripts/motif_sets.py` | same |
| 46 props | `scripts/motif_props.py` | same |
| 12 Bot costumes, walk cycles, crowds | `scripts/motif_bot_kit.py` | same |
| Counters and inserts | `scripts/motif_inserts.py` | same |
| 8 palettes, rotated per beat | `scripts/motif_rigs/palettes.py` | n/a |

Only CANONICAL entries are offered to the planner. `--allow-draft` adds DRAFT entries for review renders made before Mayowa approves a batch. All 82 Phase 2 and 3 entries were approved by Mayowa on 2026-10-09, so `--allow-draft` is only needed for new, unreviewed entries.

## Stages

1. **Script** (`motif_reel_script.py`):
   - The brief needs 4 to 6 beats, each citing a fact with an http(s) source.
   - It needs a CTA that says its keyword.
   - The script step produces 3 hook alternates.
   - Runtime must be 20 to 32 s, checked first at the measured rate (3.7 words/s, Kokoro af_nova at speed 1.2) and again after voicing.
2. **Plan** (`motif_reel.plan_reel` / `validate_plan`):
   - The reel is a hook shot, then two shots per claim (setup to the rig contact, then payoff with the insert), then a CTA shot.
   - Unknown IDs or invalid rig params fail. Anything missing is written to `library-requests.json`.
   - Rig text left at library defaults is flagged.
3. **Structure:** plan-level pacing (`motif_pacing.check_plan`).
4. **Voice:** one TTS take per line. Timing comes from measured take lengths.
5. **Compile:** per-shot frame sequences. The set is solved and checked for empty field. The camera pushes per piece. Bot walks in, reacts and hops. The insert counts or fills. Captions sit in the bottom band. SFX land at rig contacts.
6. **Rough:** pacing check on the built compositions, plus the empty-field check on stills.
7. **Critics:** live Codex critics when the Codex CLI exists. Otherwise the stage is recorded as not run.
8. **Finish:** `motif_finish` with per-room lights.
9. **Gate:** provenance and pacing on the finished project.
10. **Review render:** `motif_frame_render.py` draws each frame in Chromium and pipes it to ffmpeg. The audio mix is narration plus SFX at -16 LUFS. The run stops at REVIEW_REQUIRED.

Every stage's result is in `reel-record.json`.

## Known limits

- Word timing inside a take is proportional to characters, not measured. Whisper needs Hugging Face, which the cloud container can't reach.
- Without a brief's `visual` hints, the deterministic planner picks rigs and rooms by tag overlap. It also writes headlines from the claim text. That works but reads generic, so author the hints.
- Music is not in yet (plan 5.2 needs Mayowa's choice).
