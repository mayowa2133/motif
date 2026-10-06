# Optional timing and frame-data utilities

These original agent-authored helpers were developed in an isolated film study. They are standalone opt-in utilities; existing production compilers retain their behavior. Their source bytes were checked against the study packet's embedded hashes before consolidation. This contribution adds regression coverage and bounded input validation. No study film, narration, scene code, reference material or creative asset is promoted.

## Speech markers

`scripts/motif_speech_markers.py` exposes `resolve_markers(words, requests)`. It resolves explicit phrases to the first aligned word's measured `start`, preserving per-word alignment status. It performs no ASR call, creative scene selection, equal-fraction timing or script rewrite.

```python
from motif_speech_markers import resolve_markers

words = [
    {"text": "Open", "start": 0.27, "status": "measured"},
    {"text": "door", "start": 1.8, "status": "uncertain"},
]
markers = resolve_markers(words, [{"id": "reveal", "phrase": "open door"}])
# time: 0.27; word_range: [0, 2]; both alignment statuses are retained.
```

Marker IDs must be nonempty and unique. A phrase needs exactly one match after case/punctuation normalization. Use an explicit half-open `word_range` to disambiguate repeated phrases. Requested markers must remain in temporal order; negative and nonfinite onsets fail. Preserved uncertainty is evidence metadata, not a claim of phoneme-perfect timing.

## External frame data

`scripts/motif_frame_data.py` exposes `separate_frame_data(html_source, script_id=..., filename=...)`, returning updated HTML and one local JavaScript data file. It moves the declared JSON frame table without reserializing it, then changes the supported `JSON.parse(document.getElementById(...).textContent)` reader to the corresponding `window.MotifFrameTables` entry. The external data script loads synchronously where the inline data appeared.

```python
from pathlib import Path
from motif_frame_data import separate_frame_data

html, data = separate_frame_data(source_html, script_id="frames")
Path("index.html").write_text(html)
Path("frame-data.js").write_text(data)
```

Exactly one declared JSON script and a supported reader are required. The table must identify schema `1.0`, 30 fps and an initial state. The output filename must be one local `.js` basename using letters, digits, dots, underscores or hyphens, beginning with a letter or digit. The existing finite-frame compiler continues to validate duration and contiguous explicit states. This utility reduces embedded HTML size; it does not reduce frame-table memory or certify render speed.

The regression probe executes synthetic packed data with the existing compiler and checks exact states through forward, end-boundary, reverse and repeated seeks. Invalid or ambiguous marker schedules, unsupported declarations, and unsafe output names are rejected. These are mechanical checks, separate from rendering, playback, listening and creative review.
