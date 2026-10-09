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
    # Neon family: dark rooms, hot accents (film look neon-arcade).
    'neon-violet': {'wall': '#3A2A78', 'floor': '#1B1240', 'primary': '#FF4FA3', 'secondary': '#22D3EE', 'accent': '#FDE047', 'pop': '#A3E635', 'light': '#FFF6E8', 'dark': '#0E0A1F', 'metal': '#8C88C0'},
    'neon-teal': {'wall': '#11535E', 'floor': '#08262E', 'primary': '#2EF2C8', 'secondary': '#FF6B9A', 'accent': '#FFD23F', 'pop': '#B388FF', 'light': '#F2FFF9', 'dark': '#061418', 'metal': '#78AAB0'},
    'neon-ember': {'wall': '#5A1F3A', 'floor': '#2A0C1C', 'primary': '#FF8A3D', 'secondary': '#FF3D7F', 'accent': '#5CE1E6', 'pop': '#FFE14D', 'light': '#FFF3E6', 'dark': '#16060E', 'metal': '#B08799'},
    # Primary pop family: flat, saturated, high contrast (film look primary-pop).
    'poppy': {'wall': '#FF6A55', 'floor': '#2440C8', 'primary': '#FFD23F', 'secondary': '#2440C8', 'accent': '#18B26B', 'pop': '#FFF8EC', 'light': '#FFF8EC', 'dark': '#141414', 'metal': '#9AA0B5'},
    'royal': {'wall': '#4C6EF5', 'floor': '#FFC93C', 'primary': '#FF5A4E', 'secondary': '#FFC93C', 'accent': '#18B26B', 'pop': '#FFF8EC', 'light': '#FFF8EC', 'dark': '#141414', 'metal': '#B4BEE6'},
    'sunflower': {'wall': '#FFC93C', 'floor': '#E63E2F', 'primary': '#3B5BDB', 'secondary': '#E63E2F', 'accent': '#18B26B', 'pop': '#141414', 'light': '#FFF8EC', 'dark': '#141414', 'metal': '#8C8C8C'},
    # Candy pastel family (film look candy-pastel).
    'candy': {'wall': '#FFD6E8', 'floor': '#B58BD9', 'primary': '#FF7FB0', 'secondary': '#9EE6D3', 'accent': '#7B6CF6', 'pop': '#FFB255', 'light': '#FFFDF7', 'dark': '#3A2A4A', 'metal': '#B9A8C9'},
    'lilac': {'wall': '#DCD3FF', 'floor': '#8B7FD1', 'primary': '#A98BFF', 'secondary': '#FFC2D9', 'accent': '#3CC9A6', 'pop': '#FF8A65', 'light': '#FFFDF7', 'dark': '#2E2A4F', 'metal': '#A9A3CC'},
    'peach': {'wall': '#FFE1C7', 'floor': '#E89A7A', 'primary': '#FF9E7A', 'secondary': '#B9E5F5', 'accent': '#6E7FF0', 'pop': '#F0609A', 'light': '#FFFDF7', 'dark': '#3D2B2B', 'metal': '#C9AFA3'},
    # Outdoor family: sky, grass, sun (film look great-outdoors).
    'sky': {'wall': '#9FD8F5', 'floor': '#4C9A4F', 'primary': '#F2994A', 'secondary': '#F6E27A', 'accent': '#E2574C', 'pop': '#2F6FD6', 'light': PAPER, 'dark': '#1E2B33', 'metal': '#8AA0AA'},
    'forest': {'wall': '#BFE3AE', 'floor': '#2F5E3A', 'primary': '#D2603F', 'secondary': '#F2C14E', 'accent': '#2E86AB', 'pop': '#F28FAD', 'light': PAPER, 'dark': '#1C2A20', 'metal': '#86967F'},
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
