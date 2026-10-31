"""Motif Atelier engine. Classic helpers in scripts/ are imported, never modified."""
import sys
from pathlib import Path

_SCRIPTS = str(Path(__file__).resolve().parents[2] / 'scripts')
if _SCRIPTS not in sys.path:
    sys.path.append(_SCRIPTS)
