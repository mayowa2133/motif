#!/usr/bin/env python3
"""Verify production regressions without rendering or changing approval reports."""
import copy
import importlib.util
import sys
import math
import re
from pathlib import Path
from xml.etree import ElementTree as ET

sys.dont_write_bytecode = True
P = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('production_build', P / 'source/build.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
plan = b.read(P / 'production-plan.json')
b.plan_check(plan)
b.validate_timing(plan)
b.PARTS = b.load_parts()
b.ANCHORS = b.read(P / 'assets/props/reversible-rowhouse-folio.json')['local_anchors']
for shot in plan['shots']:
    for event in shot['events']:
        for ref in event.get('anchor_refs', []):
            assert ref['part'] in b.PARTS
            assert ref['anchor'] in b.ANCHORS[ref['part']]

painted_contacts = 0
maximum_painted_residual = 0
def transform(text):
    result = b.matrix()
    for name, raw in re.findall(r'(matrix|translate|rotate|scale)\(([^)]+)\)', text):
        values = [float(x) for x in re.findall(r'-?\d+(?:\.\d+)?(?:e[+-]?\d+)?', raw)]
        if name == 'matrix': local = tuple(values)
        elif name == 'translate': local = b.matrix(values[0], values[1] if len(values)>1 else 0)
        elif name == 'scale': local = b.matrix(sx=values[0], sy=values[1] if len(values)>1 else values[0])
        else:
            local = b.matrix(rotation=values[0])
            if len(values)==3:
                local = b.compose(b.matrix(values[1], values[2]), b.compose(local, b.matrix(-values[1], -values[2])))
        result = b.compose(result, local)
    return result
def painted_hands(element, parent=None):
    total = b.compose(parent or b.matrix(), transform(element.attrib.get('transform','')))
    found = {}
    if element.attrib.get('data-part') in ('leftHand','rightHand'):
        found['l' if element.attrib['data-part']=='leftHand' else 'r'] = b.point(total, [0,0])
    for child in element:
        found.update(painted_hands(child,total))
    return found

for shot in plan['shots']:
    count = shot['endFrame'] - shot['startFrame']
    for frame in range(count):
        before = len(b.CONTACTS)
        markup = b.frame(shot, frame, count, shot['startFrame'] + frame)
        contacts = [c for c in b.CONTACTS[before:] if c['hand'] in ('l','r')]
        if contacts:
            actual = painted_hands(ET.fromstring('<svg>'+markup+'</svg>'))
            for contact in contacts:
                residual = math.dist(actual[contact['hand']], contact['world_anchor'])
                assert residual < .1, 'emitted SVG hand misses grip: '+str(contact)
                maximum_painted_residual = max(maximum_painted_residual, residual)
                painted_contacts += 1

def roof_transform(shot):
    tree = ET.fromstring('<svg>' + b.frame(shot, 16, 50, 324) + '</svg>')
    return next(x.attrib['transform'] for x in tree.iter()
                if x.attrib.get('id') == 'teal-original-roof')

shot = plan['shots'][3]
delayed = copy.deepcopy(shot)
for event in delayed['events']:
    event['local_frame'] += 10
assert roof_transform(shot) != roof_transform(delayed), 'main action ignored event timing'

missing = copy.deepcopy(shot)
missing['timing']['landmarks']['teal-original-roof-handoff']['event_id'] = 'unknown-event'
try:
    roof_transform(missing)
except ValueError as error:
    assert 'missing or duplicate event' in str(error)
else:
    raise AssertionError('missing event route accepted')

anchors = b.ANCHORS
b.ANCHORS = copy.deepcopy(anchors)
del b.ANCHORS['teal-original-roof']['eave']
try:
    roof_transform(shot)
except ValueError as error:
    assert 'unsupported anchor' in str(error)
else:
    raise AssertionError('missing named anchor accepted')
b.ANCHORS = anchors

if (P / 'compile-record.json').exists():
    record = b.read(P / 'compile-record.json')
    for kind in ('inputs', 'outputs'):
        assert all((P / name).is_file() and b.sha(P / name) == digest
                   for name, digest in record[kind].items()), 'stale compilation: ' + kind

print('PASS: all finite frames, roof-event timing, missing event/anchor rejection, compile freshness')
print('Emitted SVG contacts:',painted_contacts,'maximum residual:',round(maximum_painted_residual,5),'author pixels; visibility remains a critic gate')
