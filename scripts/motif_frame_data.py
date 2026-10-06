"""Separate finite Motif JSON data from HTML without changing frame states.

Useful when a large embedded explicit-frame table overwhelms HTML inspection.
One local script is written; the same existing Motif compiler consumes the data.
"""
import json, re
from pathlib import Path

def separate_frame_data(html_source, *, script_id, filename='frame-data.js'):
    name = Path(filename)
    if (name.is_absolute() or len(name.parts) != 1 or name.suffix != '.js'
            or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*\.js', str(filename))):
        raise ValueError('Frame data filename must be one local .js basename')
    escaped = re.escape(script_id)
    pattern = rf'<script\s+type="application/json"\s+id="{escaped}">(.*?)</script>'
    matches = list(re.finditer(pattern, html_source, re.S))
    if len(matches) != 1:
        raise ValueError('Exactly one declared frame-data script is required')
    raw = matches[0].group(1)
    spec = json.loads(raw)
    if spec.get('schemaVersion') != '1.0' or spec.get('fps') != 30 or not spec.get('initial'):
        raise ValueError('Expected an explicit Motif30fps frame table')
    readers = [f"JSON.parse(document.getElementById('{script_id}').textContent)",
               f'JSON.parse(document.getElementById("{script_id}").textContent)']
    if not any(reader in html_source for reader in readers):
        raise ValueError('Declared frame table has no supported reader')
    key = json.dumps(script_id)
    value = f'window.MotifFrameTables[{key}]'
    output = html_source[:matches[0].start()] + f'<script src="{filename}"></script>' + html_source[matches[0].end():]
    for reader in readers:
        output = output.replace(reader, value)
    script = 'window.MotifFrameTables=window.MotifFrameTables||{};\n' + value + '=' + raw + ';\n'
    return output, script
