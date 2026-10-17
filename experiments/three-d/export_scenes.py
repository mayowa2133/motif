#!/usr/bin/env python3
"""Export Motif's existing 2D art as layered SVG scenes for the three.js experiment.

Nothing here draws new art: every layer is the library's own SVG (Bot puppet,
rooms, props, rigs), split into the depth layers a set already composes in.
Run from the repo root: python experiments/three-d/export_scenes.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))

import build_motif_bot as bot  # noqa: E402
from motif_bot_kit import dressed_bot  # noqa: E402
from motif_props import PROPS  # noqa: E402
from motif_rigs import get as get_rig  # noqa: E402
from motif_rigs.base import place  # noqa: E402
from motif_rigs.palettes import palette as get_palette  # noqa: E402
from motif_sets import ROOMS, solve  # noqa: E402

OUT = Path(__file__).resolve().parent / 'scenes'


def bot_scene(name, pose, face=None):
    body, _ = bot.assemble_pose(pose, face)
    return {'name': name, 'size': [bot.W, bot.H], 'kind': 'character', 'layers': [{'name': 'bot', 'svg': body}]}


def set_scene(name, room, rig_name, action=None, values=None, palette=None, seed=0, face='happy', bot_pose='pointing'):
    """Same split as motif_sets.compose, one layer per depth plane. The rig layer also
    carries every frame of one action, so the 3D stage can play the machine's change."""
    layout = solve(room, rig_name, values, palette, seed)
    c = get_palette(layout['palette']);rig = get_rig(rig_name);h = layout['hero'];b = layout['bot']
    layers = [{'name': 'room', 'svg': ROOMS[room]['draw'](c)}]
    back = ''.join(place(PROPS[i['prop']].render(c), i['x'], i['y'], i['scale']) for i in layout['dressing'] if i['layer'] == 'back')
    if back:layers.append({'name': 'back-props', 'svg': back})
    action = action or next(iter(rig.actions))
    frames = [place(f, h['x'], h['y'], h['scale']) for f in rig.frames(h.get('values') or None, action, layout['palette'])]
    layers.append({'name': 'rig', 'svg': frames[0], 'frames': frames, 'action': action, 'fps': 30})
    layers.append({'name': 'bot', 'svg': dressed_bot(b['x'], b['y'], b['scale'], face=face, pose=bot_pose, costume=b['costume'], palette=layout['palette'])})
    front = ''.join(place(PROPS[i['prop']].render(c), i['x'], i['y'], i['scale']) for i in layout['dressing'] if i['layer'] == 'front')
    if front:layers.append({'name': 'front-props', 'svg': front})
    return {'name': name, 'size': [720, 1280], 'kind': 'set', 'floor_y': layout['floor_y'], 'room': room, 'rig': rig_name,
            'palette': layout['palette'], 'layers': layers}


def main():
    OUT.mkdir(exist_ok=True)
    scenes = [
        bot_scene('bot-standing', 'standing', 'happy'),
        bot_scene('bot-celebrating', 'celebrating'),
        set_scene('set-workshop-press', 'workshop', 'hydraulic-press', palette='sunrise'),
        set_scene('set-office-vault', 'office', 'knowledge-vault', palette='lagoon'),
    ]
    for s in scenes:
        (OUT / f'{s["name"]}.json').write_text(json.dumps(s) + '\n')
        print(s['name'], [l['name'] for l in s['layers']])


if __name__ == '__main__':
    main()
