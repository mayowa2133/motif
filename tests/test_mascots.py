import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

from build_motif_bot import POSES  # noqa: E402
from motif_bot_kit import COSTUMES, CYCLES, FACES, dressed_bot  # noqa: E402
from motif_mascots import MASCOTS, catalog, ids  # noqa: E402


def _parse(svg):
    import re
    ET.fromstring('<svg xmlns="http://www.w3.org/2000/svg">' + re.sub(r' (data-[\w-]+)(?=[\s/>])', r' \1=""', svg) + '</svg>')


@pytest.mark.parametrize('mascot', sorted(MASCOTS))
def test_every_pose_and_face_renders(mascot):
    for pose in POSES:
        for face in FACES:
            svg = dressed_bot(360, 900, mascot=mascot, pose=pose, face=face)
            assert '<path' in svg
            _parse(svg)


@pytest.mark.parametrize('mascot', sorted(MASCOTS))
def test_cycles_and_costumes(mascot):
    frames = {dressed_bot(360, 900, mascot=mascot, cycle=c, phase=k / 8) for c in CYCLES for k in range(8)}
    assert len(frames) > len(CYCLES) * 4, 'walk cycles should animate'
    for costume in COSTUMES:
        _parse(dressed_bot(360, 900, mascot=mascot, costume=(costume,)))


def test_mascots_differ_from_bot_and_each_other():
    svgs = {m: dressed_bot(360, 900, mascot=m) for m in ids()}
    assert len(set(svgs.values())) == len(svgs)


def test_catalog_marks_new_mascots_draft():
    rows = {m['id']: m for m in catalog()['mascots']}
    assert rows['bot']['status'] == 'CANONICAL'
    assert set(rows) == set(ids())
    assert all(rows[m]['status'] == 'DRAFT' and rows[m]['description'] for m in MASCOTS)


def test_schema_lists_every_mascot():
    import json
    schema = json.loads((ROOT / 'schemas/reel-brief.schema.json').read_text())
    assert set(schema['properties']['mascot']['enum']) == set(ids())
