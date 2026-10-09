"""Rig interface: reusable, parameterised metaphor props with proven contacts.

A rig is authored SVG in Motif's 720 x 1280 grid. Its local origin (0, 0) is
the floor point under its centre; callers place it with `place()`. Each rig
declares:

  params      JSON schema for labels, counts, values
  states      named, ordered resting states
  actions     finite keyframed transitions between two states, each with the
              frame where its named contact closes
  contacts    named seams: two points (one on each part) that must coincide
              exactly at the action's CONTACT frame
  palettes    every rig renders in any palette from motif_rigs.palettes, so
              films and scenes can vary colour without new art
  bot_slot    where Bot stands or grips, and its scale
  caption_safe  the band the rig never draws into

render(params, pose, palette) returns layered SVG; pose is either a resting
state name or (action, t) with t in [0, 1]. Everything is deterministic.
"""
import copy
import json
import math
from dataclasses import dataclass, field
from pathlib import Path

from jsonschema import Draft202012Validator

from motif_rigs.palettes import PALETTES, palette as get_palette

ROOT = Path(__file__).resolve().parents[2]
GRID = (720, 1280)
FPS = 30


@dataclass(frozen=True)
class Action:
    name: str
    start: str
    end: str
    frames: int
    contact: str            # name of the contact seam that closes
    contact_frame: int      # frame index (0-based) inside the action where it closes


@dataclass
class Rig:
    name: str
    description: str
    params_schema: dict
    states: tuple
    actions: dict
    bot_slot: dict
    caption_safe: tuple = (0, 1090, 720, 190)
    tags: tuple = ()
    defaults: dict = field(default_factory=dict)
    footprint: tuple = (-280, -560, 560, 560)   # x, y, w, h in local units

    # Subclasses implement these two.
    def draw(self, p, pose, c):  # pragma: no cover - abstract
        raise NotImplementedError

    def seams(self, p, pose):  # pragma: no cover - abstract
        """{contact name: ((x, y) on part A, (x, y) on part B)} in local units."""
        raise NotImplementedError

    # Shared behaviour -----------------------------------------------------

    def params(self, values=None):
        merged = {**copy.deepcopy(self.defaults), **(values or {})}
        Draft202012Validator(self.params_schema).validate(merged)
        return merged

    def pose(self, pose):
        """Normalise a pose to (state_from, state_to, action, t)."""
        if isinstance(pose, str):
            if pose not in self.states:raise ValueError(f'{self.name}: unknown state {pose}')
            return pose, pose, None, 0.0
        name, t = pose;action = self.actions[name]
        return action.start, action.end, action, max(0.0, min(1.0, float(t)))

    def render(self, values=None, pose=None, palette='sunrise'):
        p = self.params(values);c = get_palette(palette)
        return self.draw(p, self.pose(pose or self.states[0]), c)

    def contacts(self, values=None, pose=None):
        return self.seams(self.params(values), self.pose(pose or self.states[0]))

    def contact_t(self, action):
        a = self.actions[action];return a.contact_frame / max(1, a.frames - 1)

    def contact_gap(self, values=None, action=None):
        """Distance between the two seam points at the action's CONTACT frame."""
        a = self.actions[action];(x1, y1), (x2, y2) = self.contacts(values, (action, self.contact_t(action)))[a.contact]
        return math.hypot(x1 - x2, y1 - y2)

    def frames(self, values=None, action=None, palette='sunrise'):
        a = self.actions[action]
        return [self.render(values, (action, i / max(1, a.frames - 1)), palette) for i in range(a.frames)]

    def events(self, values, action, target, start_time=0.0, x=360, y=1000, scale=1.0, palette='sunrise', backdrop=''):
        """Event-engine SET data for one action (motif-frame-sequence contract)."""
        out = []
        for i, svg in enumerate(self.frames(values, action, palette)):
            out.append({'time': round(start_time + i / FPS, 6), 'target': target, 'action': 'SET',
                        'params': {'props': {'innerHTML': backdrop + place(svg, x, y, scale)}}})
        return out

    def proof(self, out_dir, values=None, action=None, palette='sunrise', backdrop=None):
        """BEFORE / CONTACT / AFTER stills at 360 x 640 for the concept critic."""
        action = action or next(iter(self.actions));a = self.actions[action]
        out_dir = Path(out_dir);out_dir.mkdir(parents=True, exist_ok=True)
        # Fill the frame the way a set would: at least 35% of frame height, inside the side margins.
        fx, fy, fw, fh = self.footprint;scale = min(660 / fw, 820 / fh, 1.6)
        stills = {'before': (action, 0.0), 'contact': (action, self.contact_t(action)), 'after': (action, 1.0)}
        paths = {}
        for label, pose in stills.items():
            svg = (backdrop if backdrop is not None else default_backdrop(get_palette(palette))) + place(self.render(values, pose, palette), 360 - (fx + fw / 2) * scale, 1040, scale)
            paths[label] = raster(svg, out_dir / f'{self.name}-{action}-{label}.png')
        record = {'rig': self.name, 'action': action, 'palette': palette, 'params': self.params(values),
                  'contact': a.contact, 'contact_frame': a.contact_frame, 'contact_gap': self.contact_gap(values, action),
                  'stills': {k: str(v) for k, v in paths.items()}}
        (out_dir / f'{self.name}-{action}-proof.json').write_text(json.dumps(record, indent=2) + '\n')
        return record

    def manifest(self):
        return {'name': self.name, 'description': self.description, 'tags': list(self.tags), 'states': list(self.states),
                'actions': {k: {'from': v.start, 'to': v.end, 'frames': v.frames, 'contact': v.contact, 'contact_frame': v.contact_frame} for k, v in self.actions.items()},
                'params_schema': self.params_schema, 'defaults': self.defaults, 'bot_slot': self.bot_slot,
                'caption_safe': list(self.caption_safe), 'footprint': list(self.footprint), 'palettes': sorted(PALETTES)}


# Helpers shared by rigs -------------------------------------------------------

def lerp(a, b, t):return a + (b - a) * t


def ease(t):t = max(0.0, min(1.0, t));return 1 - (1 - t) ** 3


def ease_in(t):t = max(0.0, min(1.0, t));return t ** 3


def place(svg, x, y, scale=1.0):
    return f'<g transform="translate({x:.3f} {y:.3f}) scale({scale:.5f})">{svg}</g>'


def default_backdrop(c):
    return (f'<rect width="720" height="1280" fill="{c["wall"]}"/>'
            f'<rect y="1040" width="720" height="240" fill="{c["floor"]}"/><path d="M0 1042H720" stroke="{c["dark"]}" stroke-width="3" opacity=".35"/>')


def raster(svg, path, size=(360, 640)):
    """Rasterise a 720 x 1280 grid SVG fragment with the Motif defs (Bot, worldPaper)."""
    import cairosvg
    from motif_ui_components import DEFS
    material = (ROOT / 'assets/materials/legacy-v0/wall.png').as_uri()
    defs = DEFS.replace('assets/materials/world-paper.webp', material)
    doc = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{size[0]}" height="{size[1]}" viewBox="0 0 720 1280">'
           f'<defs>{defs}</defs>{svg}</svg>')
    # Browser-only bare attributes (data-layout-*) are not valid XML for the rasteriser.
    import re
    doc = re.sub(r' (data-[\w-]+)(?=[\s/>])', r' \1=""', doc)
    path = Path(path);path.parent.mkdir(parents=True, exist_ok=True)
    cairosvg.svg2png(bytestring=doc.encode(), write_to=str(path), output_width=size[0], output_height=size[1], unsafe=True)
    return path
