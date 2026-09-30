#!/usr/bin/env python3
"""Check mascot exports, metadata and representative small-size renders."""

from __future__ import annotations

import io
import json
import xml.etree.ElementTree as ET
from pathlib import Path

import cairosvg
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'assets/characters/motif-bot/canonical/v1'
PROOFS = ROOT / 'previews/motif-bot-a-v1/proofs'
NS = {'svg': 'http://www.w3.org/2000/svg'}


def main() -> None:
    manifest = json.loads((BASE / 'motif-bot-v1.json').read_text())
    assert manifest['status'] in {'review', 'canonical'}
    assert len(manifest['visualGroups']) == 10
    assert len(manifest['handStates']) == 5
    assert len(manifest['faceStates']) == 12
    assert len(manifest['views']) == 6
    assert len(manifest['supportedActions']) == 16
    presets = json.loads((BASE / 'pose-presets.json').read_text())
    assert presets['representation'] == 'parameters'
    assert len(presets['presets']) == 16
    assert not (BASE / 'poses').exists()
    assert not (BASE / 'pose-demos').exists()
    assert not (BASE / 'expressions').exists()
    for name, p in manifest['anchors'].items():
        assert 0 <= p['x'] <= 1 and 0 <= p['y'] <= 1, (name, p)
    svg_files = sorted(BASE.rglob('*.svg'))
    for path in svg_files:
        tree = ET.parse(path)
        assert tree.getroot().tag.endswith('svg'), path
        assert tree.find('.//svg:title', NS) is not None, path
        sidecar = path.with_suffix('.json')
        assert sidecar.is_file(), path
        m = json.loads(sidecar.read_text())
        assert m['source']['file'] == str(path.relative_to(ROOT)), path
        assert m['dimensions'] == {'width': 1024, 'height': 1024, 'unit': 'px'}, path
        assert m['status'] == manifest['status'], path
    master = ET.parse(BASE / 'motif-bot-front-neutral-v1.svg')
    ids = {e.attrib['id'] for e in master.iter() if 'id' in e.attrib}
    assert set(manifest['visualGroups']).issubset(ids)
    for sample in [BASE / 'motif-bot-front-neutral-v1.svg',
                   PROOFS / 'poses' / 'pointing.svg',
                   PROOFS / 'poses' / 'running.svg',
                   PROOFS / 'expressions' / 'happy.svg']:
        data = cairosvg.svg2png(url=str(sample), output_width=96, output_height=96)
        image = Image.open(io.BytesIO(data)).convert('RGBA')
        alpha = image.getchannel('A')
        assert alpha.getbbox() is not None, sample
        assert alpha.getextrema()[0] == 0 and alpha.getextrema()[1] >= 240, sample
    print(f'Validated {len(svg_files)} editable SVG components/views, pose parameters, sidecars and four 96px renders ({manifest["status"]}).')


if __name__ == '__main__':
    main()
