"""Motif palette variants for rigs, sets and costumes.

Mayowa asked (2026-10-09) that reels stay colourful and varied, so every rig,
set and costume renders through palette roles rather than fixed colours, and
the planner rotates palettes between scenes (see rotation()). All colours are
Motif's own: the Style Bible roles plus brighter companions in the same
matte-paper family. Bot itself never changes colour (canonical v1).

Roles
  wall, floor     backdrop surfaces
  primary         the rig's main body
  secondary       second large mass
  accent          small high-attention parts (buttons, flags, needles)
  pop             a contrasting accent for the payoff state
  light, dark     paper and ink for labels and outlines
  metal           hardware, rails, hinges
"""
PAPER = '#F4EBD8';INK = '#202C32'

PALETTES = {
    'sunrise': {'wall': '#F2C9A0', 'floor': '#B8735A', 'primary': '#DF806B', 'secondary': '#EBC46B', 'accent': '#56BFB1', 'pop': '#B60B50', 'light': PAPER, 'dark': INK, 'metal': '#7D8A8C'},
    'lagoon': {'wall': '#A6D8CF', 'floor': '#2F6E6A', 'primary': '#56BFB1', 'secondary': '#254D50', 'accent': '#DF806B', 'pop': '#EBC46B', 'light': PAPER, 'dark': INK, 'metal': '#8FA3A6'},
    'berry': {'wall': '#E7B6CB', 'floor': '#554565', 'primary': '#B9457A', 'secondary': '#F293B6', 'accent': '#EBC46B', 'pop': '#56BFB1', 'light': PAPER, 'dark': INK, 'metal': '#8E7F95'},
    'meadow': {'wall': '#CFE3B0', 'floor': '#5E7F3E', 'primary': '#3FA45B', 'secondary': '#A9C46B', 'accent': '#E8833A', 'pop': '#3E64B8', 'light': PAPER, 'dark': INK, 'metal': '#7F8C78'},
    'cobalt': {'wall': '#B9C9EA', 'floor': '#3A4C7A', 'primary': '#3E64B8', 'secondary': '#7FB8D9', 'accent': '#F2C94C', 'pop': '#DF806B', 'light': PAPER, 'dark': INK, 'metal': '#8794A8'},
    'citrus': {'wall': '#F7DE8E', 'floor': '#C0662F', 'primary': '#E8833A', 'secondary': '#F2C94C', 'accent': '#554565', 'pop': '#3FA45B', 'light': PAPER, 'dark': INK, 'metal': '#9C8A70'},
    'plum-night': {'wall': '#554565', 'floor': '#2B2236', 'primary': '#8A6FB0', 'secondary': '#F293B6', 'accent': '#EBC46B', 'pop': '#56BFB1', 'light': PAPER, 'dark': '#1A1622', 'metal': '#A39BB0'},
    'mint-coral': {'wall': '#CBE8DC', 'floor': '#64869A', 'primary': '#F07F6A', 'secondary': '#7CCFB8', 'accent': '#3E64B8', 'pop': '#EBC46B', 'light': PAPER, 'dark': INK, 'metal': '#8FA0A0'},
}


def palette(name):
    if name not in PALETTES:raise ValueError(f'unknown palette {name}; choose from {sorted(PALETTES)}')
    return PALETTES[name]


def rotation(count, seed=0, avoid=()):
    """A palette per scene: no two neighbours share a palette, cycling through the
    whole set before repeating. Deterministic for a seed."""
    names = [n for n in sorted(PALETTES) if n not in avoid]
    if len(names) < 2:raise ValueError('need at least two palettes to rotate')
    start = seed % len(names);step = 3 if len(names) % 3 else 1
    order = [names[(start + i * step) % len(names)] for i in range(len(names))]
    return [order[i % len(order)] for i in range(count)]
