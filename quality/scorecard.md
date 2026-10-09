# Motif reel scorecard

Fill in one row per reel after watching it on a phone at normal speed. Re-run after each milestone with `python scripts/motif_benchmark.py` (renders every brief in `quality/benchmark-briefs/` and builds a contact sheet).

Score each column 1 to 5. "Same league" asks whether the reel could sit beside the private reference reels without looking amateur (yes/no).

| Reel | Date | Phone readability | Texture and light | Set density | Bot acting | Pace | Story clarity | Same league | Notes |
|---|---|---|---|---|---|---|---|---|---|
| bench-sqlite-everywhere | | | | | | | | | |
| bench-free-https | | | | | | | | | |
| bench-python-no-gil | | | | | | | | | |
| bench-blender-free | | | | | | | | | |
| bench-open-map | | | | | | | | | |

The plan is done when three new-topic reels render with no per-film code, every asset traces to a Motif source, and Mayowa rates at least two of them "same league".

Automatic gates (pacing, empty field, provenance) are recorded in each run's `reel-record.json`. They are necessary but they do not score a reel; only a person watching on a phone does.
