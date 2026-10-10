"""Lessons ledger: every reel Motif makes leaves the next one better.

Each time a film is reviewed (by Mayowa on a phone, by Codex, or by Claude's own
pass) the findings become lessons in quality/lessons.json. A lesson names the
symptom a viewer saw, the rule that prevents it, and how the rule is enforced:

  check    an automatic check in this module (CHECKS) that runs on every new
           reel's compiled project; "gate" lessons fail the run, "warn" lessons
           are recorded for the retrospective
  pacing / sound-off / provenance / motion
           enforced by an existing stage of scripts/motif_reel.py
  brief    a rule for brief authors (checked by hand until it can be automated)

scripts/motif_improve.py ties the loop together: `retro` writes a run's
findings and appends them to the run log, `lesson` records a new lesson from
feedback, `backlog` ranks missing library pieces across runs, and `regress`
re-checks every brief so a new rule is proven on old films too.
"""
import json
import math
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / 'quality/lessons.json'
DELIVERY_SCALE = 1080 / 720       # compositions are designed on 720 x 1280, delivered at 1080 x 1920
MIN_TEXT_PX = 24                  # smallest machine label that reads on a phone, in delivered pixels
OCCLUDED = .2                     # share of a label's box a front prop may cover


def ledger():
    return json.loads(LEDGER.read_text())


# SVG text geometry ----------------------------------------------------------------------

def _mul(a, b):
    return (a[0] * b[0] + a[2] * b[1], a[1] * b[0] + a[3] * b[1], a[0] * b[2] + a[2] * b[3], a[1] * b[2] + a[3] * b[3],
            a[0] * b[4] + a[2] * b[5] + a[4], a[1] * b[4] + a[3] * b[5] + a[5])


def _transform(spec):
    m = (1, 0, 0, 1, 0, 0)
    for name, args in re.findall(r'(\w+)\(([^)]*)\)', spec or ''):
        v = [float(x) for x in re.split(r'[\s,]+', args.strip()) if x]
        if name == 'translate':t = (1, 0, 0, 1, v[0], v[1] if len(v) > 1 else 0)
        elif name == 'scale':t = (v[0], 0, 0, v[1] if len(v) > 1 else v[0], 0, 0)
        elif name == 'rotate':
            a = math.radians(v[0]);c, s = math.cos(a), math.sin(a);t = (c, s, -s, c, 0, 0)
            if len(v) == 3:t = _mul(_mul((1, 0, 0, 1, v[1], v[2]), t), (1, 0, 0, 1, -v[1], -v[2]))
        elif name == 'matrix':t = tuple(v)
        else:continue
        m = _mul(m, t)
    return m


def texts(svg, base=(1, 0, 0, 1, 0, 0)):
    """Every <text> in an SVG fragment: {'text', 'size' (on-frame units), 'box' (x, y, w, h)}, with nested transforms applied."""
    doc = re.sub(r' (data-[\w-]+)(?=[\s/>])', r' \1=""', svg)
    root = ET.fromstring(f'<svg xmlns="http://www.w3.org/2000/svg">{doc}</svg>')
    out = []

    def walk(node, m):
        m = _mul(m, _transform(node.get('transform')))
        if node.tag.endswith('text') and (node.text or '').strip():
            if float(node.get('opacity', 1)) <= 0:return
            size = float(node.get('font-size', 16));text = node.text.strip();w = len(text) * size * .6
            x, y = float(node.get('x', 0)), float(node.get('y', 0))
            anchor = node.get('text-anchor', 'start');x0 = x - (w / 2 if anchor == 'middle' else w if anchor == 'end' else 0)
            pts = [(px * m[0] + py * m[2] + m[4], px * m[1] + py * m[3] + m[5]) for px, py in ((x0, y - size * .75), (x0 + w, y - size * .75), (x0, y + size * .2), (x0 + w, y + size * .2))]
            xs, ys = [p[0] for p in pts], [p[1] for p in pts];k = math.sqrt(abs(m[0] * m[3] - m[1] * m[2]))
            out.append({'text': text, 'size': size * k, 'box': (min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))})
        for child in node:
            if float(child.get('opacity', 1)) > 0:walk(child, m)
    walk(root, base)
    return out


def _overlap(a, b):
    w = min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0]);h = min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1])
    return max(0.0, w) * max(0.0, h)


def hero_labels(layout, pose='end'):
    """The machine's printed labels in frame coordinates at its end state (what the payoff shows)."""
    from motif_rigs import get
    h = layout.get('hero')
    if not h:return []
    rig = get(h['rig']);action = next(iter(rig.actions))
    svg = rig.render(h.get('values') or None, (action, 1.0 if pose == 'end' else rig.contact_t(action)), layout.get('palette') or 'sunrise')
    return texts(svg, (h['scale'], 0, 0, h['scale'], h['x'], h['y']))


# Checks ------------------------------------------------------------------------------------
# Each check takes (project, plan, layouts) and returns findings: {'where', 'detail'}.

def check_label_legibility(project, plan, layouts):
    """Machine labels must read on a phone: at least MIN_TEXT_PX tall in the delivered frame."""
    out = []
    for beat, layout in layouts.items():
        small = sorted({(round(t['size'] * DELIVERY_SCALE, 1), t['text']) for t in hero_labels(layout) if t['size'] * DELIVERY_SCALE < MIN_TEXT_PX})
        if small:out.append({'where': beat, 'detail': f'{len(small)} labels under {MIN_TEXT_PX}px: ' + ', '.join(f'{t} ({s}px)' for s, t in small[:6])})
    return out


def check_label_occlusion(project, plan, layouts):
    """No front-layer set dressing may cover a machine label (cut 2 of the second-brain reel hid PAGES 7 behind a crate)."""
    out = []
    for beat, layout in layouts.items():
        fronts = [d for d in layout.get('dressing', []) if d.get('layer') == 'front']
        for t in hero_labels(layout):
            area = t['box'][2] * t['box'][3]
            for d in fronts:
                if area and _overlap(t['box'], d['box']) / area > OCCLUDED:
                    out.append({'where': beat, 'detail': f'{d["prop"]} covers "{t["text"]}"'})
    return out


def check_headline_openers(project, plan, layouts):
    """Consecutive headlines must not open with the same word: on a phone the change does not register
    (cut 2: ANSWERS WITH SOURCES -> ANSWERS GET SAVED read as one 4.3 s headline)."""
    heads = []
    for beat in plan['beats']:
        for shot in beat['shots']:
            heads.append((shot['id'], shot['headline']))
            if shot.get('split_headline') and shot.get('headline_b'):heads.append((shot['id'] + '/b', shot['headline_b']))
    out = []
    for (a, x), (b, y) in zip(heads, heads[1:]):
        if x != y and x.split()[0] == y.split()[0]:out.append({'where': b, 'detail': f'"{x}" then "{y}" open with the same word'})
    return out


def check_shared_object_palette(project, plan, layouts):
    """Beats that carry the same machine keep its colours (Codex's v11 critique: the Python lock went pink then teal)."""
    out = [];last = {}
    from motif_rigs import get
    from motif_rigs.palettes import palette
    for beat in plan['beats']:
        shot = beat['shots'][0]
        if not shot.get('rig'):continue
        try:rig = get(shot['rig']['id']);key = rig.identity(rig.params(shot['rig'].get('params')))
        except Exception:continue  # the plan stage reports unknown rigs and bad params
        if key is None:continue
        if key in last:
            a, b = palette(last[key]), palette(beat['palette'])
            if any(a[k] != b[k] for k in ('primary', 'secondary', 'accent', 'pop')):
                out.append({'where': beat['id'], 'detail': f'{key} changes colours ({last[key]} -> {beat["palette"]}); use "{last[key].split("/")[0]}/<room>" to vary only the walls'})
        last[key] = beat['palette']
    return out


CHECKS = {
    'label-legibility': check_label_legibility,
    'label-occlusion': check_label_occlusion,
    'headline-openers': check_headline_openers,
    'shared-object-palette': check_shared_object_palette,
}


def run(project, plan=None, layouts=None):
    """Run every ledger lesson enforced by a check here. Returns {'status', 'lessons': [...]}."""
    project = Path(project)
    plan = plan or json.loads((project / 'production-plan.json').read_text())
    if layouts is None:layouts = json.loads((project / 'set-layouts.json').read_text())
    rows = [];failed = False
    for lesson in ledger()['lessons']:
        check = lesson.get('check')
        if check not in CHECKS:continue
        findings = CHECKS[check](project, plan, layouts)
        status = 'PASS' if not findings else ('FAIL' if lesson.get('level') == 'gate' else 'WARN')
        failed |= status == 'FAIL'
        rows.append({'lesson': lesson['id'], 'check': check, 'status': status, 'findings': findings})
    return {'status': 'FAIL' if failed else 'PASS', 'lessons': rows}
