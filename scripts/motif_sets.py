"""Set layout solver: rooms, dressing, hero rig, Bot and the empty-field check.

A set is one beat's stage in the 720 x 1280 grid:

  backdrop      one of Motif's original rooms, drawn in the beat's palette
  dressing      2 to 4 props from motif_props; at least one crosses a frame
                edge and at least one partly overlaps the hero, so the frame
                reads as a place rather than a card on an empty field
  hero          a rig from motif_rigs, at 35% or more of frame height
  bot           Bot at the rig's bot_slot, with a costume
  bands         headline band (top) and caption band (bottom) stay clear
  lights        the finish-pass light kit for the room

solve() is deterministic for (room, rig, seed, beat). The palette rotates per
beat (Mayowa, 2026-10-09: reels must be colourful and varied), so consecutive
beats never share one. empty_field() measures a rendered frame: the share of
the focal band that is flat background. Over 45% fails.
"""
import argparse
import hashlib
import json
import random
import sys
from pathlib import Path

from motif_bot_kit import COSTUMES, dressed_bot
from motif_props import PROPS
from motif_rigs import get as get_rig
from motif_rigs.base import place
from motif_rigs.palettes import PALETTES, palette as get_palette, rotation

ROOT = Path(__file__).resolve().parents[1]
W, H = 720, 1280
FLOOR = 1040
HEADLINE = (0, 80, 720, 230)       # x, y, w, h
CAPTION = (0, 1090, 720, 190)
SIDE = 90                          # dressing may enter the headline band only inside these side margins
HERO_MIN = .35                     # hero height as a share of frame height
HERO_WIDE = (.3, .7)               # or, for a wide machine, this share of height and of width
EMPTY_FIELD_MAX = .45
EDGE_VISIBLE = .7                  # an edge prop shows at least this share of its width (no stray fragments)
BOT_SCALE = (.32, .4)              # Bot reads at about 17 to 21% of frame height
BOT_LANE = 150                    # width kept free beside the hero for Bot
HERO_SAFE = 40                    # hero clear of the frame edge so camera push-ins never crop it
PROP_MAX_SCALE = 1.8              # beyond this a small prop reads as a blank panel or a giant
BOT_TOUCH = .9                    # Bot stands at the hero edge, a sliver over it, clear of edge labels
BOT_HALF = 235                     # Bot half width in its local units
FOCAL = (.18, .82)                 # focal band as a share of frame height


# Rooms -------------------------------------------------------------------------

def _stripes(c, colour, step=60, width=24, opacity=.22):
    return ''.join(f'<rect x="{x}" y="0" width="{width}" height="{FLOOR}" fill="{colour}" opacity="{opacity}"/>' for x in range(0, W, step))


def _tiles(c, colour, y0, y1, size=60, opacity=.35):
    out = ''
    for row, y in enumerate(range(y0, y1, size)):
        for col, x in enumerate(range(0, W, size)):
            if (row + col) % 2:out += f'<rect x="{x}" y="{y}" width="{size}" height="{min(size, y1 - y)}" fill="{colour}" opacity="{opacity}"/>'
    return out


def _floor(c, kind):
    base = f'<rect y="{FLOOR}" width="{W}" height="{H - FLOOR}" fill="{c["floor"]}"/>'
    if kind == 'boards':base += ''.join(f'<path d="M0 {y}H{W}" stroke="{c["dark"]}" stroke-width="3" opacity=".18"/>' for y in range(FLOOR + 40, H, 48))
    elif kind == 'tiles':base += _tiles(c, c['light'], FLOOR, H, 80, .18)
    elif kind == 'street':base += f'<rect y="{FLOOR}" width="{W}" height="26" fill="{c["metal"]}"/>' + ''.join(f'<rect x="{x}" y="{FLOOR + 120}" width="60" height="12" fill="{c["light"]}" opacity=".6"/>' for x in range(20, W, 120))
    elif kind == 'stage':base += f'<rect y="{FLOOR}" width="{W}" height="18" fill="{c["secondary"]}"/>' + ''.join(f'<path d="M{x} {FLOOR + 18}V{H}" stroke="{c["dark"]}" stroke-width="3" opacity=".2"/>' for x in range(60, W, 90))
    elif kind == 'rug':base += f'<ellipse cx="360" cy="{FLOOR + 70}" rx="300" ry="46" fill="{c["pop"]}" opacity=".55"/>'
    return base + f'<path d="M0 {FLOOR + 2}H{W}" stroke="{c["dark"]}" stroke-width="4" opacity=".35"/>'


def _bands(c, colours, opacities):
    """Soft vertical light falloff across the wall (a gradient, no visible steps)."""
    key = hashlib.sha256(repr((colours, opacities)).encode()).hexdigest()[:10]
    stops = ''.join(f'<stop offset="{i / max(1, len(colours) - 1):.3f}" stop-color="{col}" stop-opacity="{op}"/>' for i, (col, op) in enumerate(zip(colours, opacities)))
    return f'<defs><linearGradient id="wall-falloff-{key}" x1="0" y1="0" x2="0" y2="1">{stops}</linearGradient></defs><rect width="{W}" height="{FLOOR}" fill="url(#wall-falloff-{key})"/>'


def _diamonds(c, colour, size=56, opacity=.22, y1=FLOOR):
    out = ''
    for row, y in enumerate(range(0, y1, size)):
        for x in range(-size if row % 2 else -size // 2, W + size, size):
            out += f'<path d="M{x} {y + size / 2}L{x + size / 2} {y}L{x + size} {y + size / 2}L{x + size / 2} {y + size}Z" fill="{colour}" opacity="{opacity}"/>'
    return out


def _office(c):
    blinds = ''.join(f'<rect x="{x}" y="330" width="150" height="250" fill="{c["light"]}" opacity=".5"/>' + ''.join(f'<path d="M{x} {y}H{x + 150}" stroke="{c["metal"]}" stroke-width="5" opacity=".45"/>' for y in range(345, 580, 22)) for x in (40, 530))
    return (f'<rect width="{W}" height="{FLOOR}" fill="{c["wall"]}"/>' + _bands(c, (c['dark'], c['wall'], c['light']), (.12, 0, .1)) + _stripes(c, c['secondary'], 60, 22, .22) + blinds
            + f'<rect y="{FLOOR - 220}" width="{W}" height="220" fill="{c["secondary"]}" opacity=".55"/>' + ''.join(f'<rect x="{x}" y="{FLOOR - 196}" width="96" height="170" fill="none" stroke="{c["dark"]}" stroke-width="3" opacity=".22"/>' for x in range(16, W, 120))
            + f'<path d="M0 {FLOOR - 220}H{W}" stroke="{c["dark"]}" stroke-width="5" opacity=".3"/>' + _floor(c, 'boards'))


def _diner(c):
    return (f'<rect width="{W}" height="{FLOOR}" fill="{c["wall"]}"/>' + _stripes(c, c['secondary'], 80, 40, .35) + _tiles(c, c['light'], FLOOR - 340, FLOOR, 50, .45)
            + f'<rect y="{FLOOR - 352}" width="{W}" height="22" fill="{c["pop"]}"/>' + _floor(c, 'tiles'))


def _street(c):
    sky = f'<rect width="{W}" height="{FLOOR}" fill="{c["wall"]}"/>' + _bands(c, (c['accent'], c['wall'], c['light']), (.18, 0, .25)) + f'<circle cx="590" cy="250" r="70" fill="{c["light"]}" opacity=".55"/>'
    city = PROPS['skyline'].render(c)
    return sky + f'<g opacity=".55">{place(city, 360, FLOOR, 1.0)}</g>' + _floor(c, 'street')


def _stage(c):
    rays = ''.join(f'<path d="M360 -40L{x} {FLOOR}" stroke="{c["light"]}" stroke-width="70" opacity=".12"/>' for x in range(-100, 900, 100))
    arch = f'<path d="M0 0H{W}V{FLOOR}H640V260Q360 120 80 260V{FLOOR}H0Z" fill="{c["primary"]}" opacity=".85"/>'
    bulbs = ''.join(f'<circle cx="{x}" cy="{y}" r="9" fill="{c["secondary"]}" stroke="{c["dark"]}" stroke-width="2"/>' for x, y in [(40, yy) for yy in range(300, FLOOR, 70)] + [(680, yy) for yy in range(300, FLOOR, 70)])
    folds = ''.join(f'<path d="M{x} 0V{FLOOR}" stroke="{c["dark"]}" stroke-width="5" opacity=".18"/>' for x in range(100, 640, 46))
    return f'<rect width="{W}" height="{FLOOR}" fill="{c["wall"]}"/>' + folds + rays + arch + bulbs + f'<ellipse cx="360" cy="{FLOOR}" rx="320" ry="40" fill="{c["light"]}" opacity=".3"/>' + _floor(c, 'stage')


def _workshop(c):
    planks = ''.join(f'<rect x="{x}" y="0" width="118" height="{FLOOR}" fill="{c["secondary"] if (x // 120) % 2 else c["wall"]}" opacity=".5"/>' for x in range(0, W, 120))
    return f'<rect width="{W}" height="{FLOOR}" fill="{c["wall"]}"/>' + planks + _floor(c, 'boards')


def _night_sky(c):
    dots = ''.join(f'<circle cx="{(k * 137) % W}" cy="{(k * 251) % (FLOOR - 200) + 40}" r="{2 + k % 3}" fill="{c["light"]}" opacity=".75"/>' for k in range(160))
    trees = ''.join(f'<path d="M{x} {FLOOR - 120}L{x + 30} {FLOOR - 260 - (x * 13) % 90}L{x + 60} {FLOOR - 120}Z" fill="{c["floor"]}" opacity=".9"/>' for x in range(-20, W, 52))
    glow = ''.join(f'<circle cx="520" cy="300" r="{r}" fill="{c["secondary"]}" opacity=".07"/>' for r in (300, 220, 150))
    hills = (f'<path d="M0 {FLOOR - 300}Q200 {FLOOR - 420} 420 {FLOOR - 300}Q600 {FLOOR - 220} 720 {FLOOR - 330}V{FLOOR}H0Z" fill="{c["metal"]}" opacity=".45"/>'
             f'<path d="M0 {FLOOR - 120}Q180 {FLOOR - 220} 360 {FLOOR - 130}Q540 {FLOOR - 50} 720 {FLOOR - 160}V{FLOOR}H0Z" fill="{c["floor"]}" opacity=".8"/>')
    return f'<rect width="{W}" height="{FLOOR}" fill="{c["dark"]}"/><rect width="{W}" height="{FLOOR}" fill="{c["wall"]}" opacity=".55"/>' + _bands(c, (c['dark'], c['primary'], c['pop']), (.25, .12, .18)) + glow + dots + hills + trees + _floor(c, 'none')


def _server_room(c):
    lines = ''.join(f'<path d="M{x} 0V{FLOOR}" stroke="{c["accent"]}" stroke-width="3" opacity=".25"/>' for x in range(40, W, 80))
    lights = ''.join(f'<circle cx="{x}" cy="{y}" r="4" fill="{c["pop"]}" opacity=".6"/>' for x in range(40, W, 80) for y in range(140, FLOOR - 100, 170))
    racks = ''.join(f'<rect x="{x}" y="{FLOOR - 560}" width="110" height="560" fill="{c["dark"]}" opacity=".45"/>' + ''.join(f'<rect x="{x + 10}" y="{y}" width="90" height="30" fill="{c["metal"]}" opacity=".35"/><circle cx="{x + 88}" cy="{y + 15}" r="4" fill="{c["accent"] if (x + y) % 3 else c["pop"]}"/>' for y in range(FLOOR - 540, FLOOR - 20, 46)) for x in range(10, W, 140))
    return f'<rect width="{W}" height="{FLOOR}" fill="{c["dark"]}"/><rect width="{W}" height="{FLOOR}" fill="{c["wall"]}" opacity=".35"/>' + lines + lights + racks + _floor(c, 'tiles')


def _living_room(c):
    rail = ''.join(f'<rect x="{x}" y="250" width="{70 + (x * 7) % 50}" height="{60 + (x * 3) % 40}" fill="{c["light"]}" stroke="{c["dark"]}" stroke-width="3" opacity=".55"/>' for x in range(10, W, 130))
    return (f'<rect width="{W}" height="{FLOOR}" fill="{c["wall"]}"/>' + _diamonds(c, c['light'], 34, .3, FLOOR - 140) + rail + _bands(c, (c['dark'], c['wall'], c['light']), (.1, 0, .08))
            + f'<rect y="{FLOOR - 160}" width="{W}" height="22" fill="{c["primary"]}" opacity=".7"/><rect y="{FLOOR - 140}" width="{W}" height="140" fill="{c["secondary"]}" opacity=".45"/>' + _floor(c, 'rug'))



def _arcade(c):
    tubes = ''.join(f'<path d="M{x} 120V{FLOOR - 260}" stroke="{col}" stroke-width="10" stroke-linecap="round" opacity=".85"/><path d="M{x} 120V{FLOOR - 260}" stroke="{col}" stroke-width="34" stroke-linecap="round" opacity=".14"/>'
                    for x, col in ((60, c['primary']), (240, c['secondary']), (480, c['accent']), (660, c['primary'])))
    zig = f'<path d="M0 {FLOOR - 200}' + ''.join(f'L{x} {FLOOR - 200 - (40 if (x // 60) % 2 else 0)}' for x in range(60, W + 60, 60)) + f'" fill="none" stroke="{c["pop"]}" stroke-width="8" opacity=".7"/>'
    floor = f'<rect y="{FLOOR}" width="{W}" height="{H - FLOOR}" fill="{c["floor"]}"/>' + _tiles(c, c['secondary'], FLOOR, H, 60, .22) + f'<path d="M0 {FLOOR + 2}H{W}" stroke="{c["primary"]}" stroke-width="5" opacity=".7"/>'
    return f'<rect width="{W}" height="{FLOOR}" fill="{c["dark"]}"/><rect width="{W}" height="{FLOOR}" fill="{c["wall"]}" opacity=".6"/>' + _diamonds(c, c['dark'], 80, .25) + tubes + zig + floor


def _park(c):
    sky = f'<rect width="{W}" height="{FLOOR}" fill="{c["wall"]}"/>' + _bands(c, (c['light'], c['wall'], c['secondary']), (.35, 0, .3))
    hills = (f'<path d="M0 {FLOOR - 260}Q180 {FLOOR - 380} 380 {FLOOR - 270}Q560 {FLOOR - 180} 720 {FLOOR - 300}V{FLOOR}H0Z" fill="{c["floor"]}" opacity=".45"/>'
             f'<path d="M0 {FLOOR - 120}Q240 {FLOOR - 210} 460 {FLOOR - 120}Q600 {FLOOR - 70} 720 {FLOOR - 130}V{FLOOR}H0Z" fill="{c["floor"]}" opacity=".75"/>')
    trees = ''.join(f'<g opacity=".7">{place(PROPS["tree"].render(c), x, FLOOR - 90 - (x * 7) % 50, .45)}</g>' for x in (40, 200, 560, 690))
    path_ = f'<path d="M300 {FLOOR}Q340 {FLOOR + 120} 260 {H}H460Q420 {FLOOR + 120} 420 {FLOOR}Z" fill="{c["secondary"]}" opacity=".7"/>'
    clouds = ''.join(f'<g opacity=".8">{place(PROPS["cloud"].render(c), x, y, s)}</g>' for x, y, s in ((140, 300, .8), (520, 230, 1.0), (330, 470, .6), (650, 520, .55), (60, 560, .5)))
    kites = ''.join(f'<path d="M{x} {y}l26 -40l26 40l-26 30Z" fill="{col}" stroke="{c["dark"]}" stroke-width="3"/><path d="M{x + 26} {y + 30}q-20 40 10 80q-30 40 0 90" fill="none" stroke="{c["dark"]}" stroke-width="2" opacity=".5"/>' for x, y, col in ((470, 380, c['pop']), (200, 420, c['accent'])))
    fence = ''.join(f'<path d="M{x} {FLOOR - 10}V{FLOOR - 120}l12 -16l12 16V{FLOOR - 10}Z" fill="{c["light"]}" opacity=".75"/>' for x in range(0, W, 40)) + f'<rect y="{FLOOR - 90}" width="{W}" height="12" fill="{c["light"]}" opacity=".75"/>'
    bushes = ''.join(f'<circle cx="{x}" cy="{FLOOR - 40}" r="{r}" fill="{c["floor"]}" stroke="{c["dark"]}" stroke-width="3" opacity=".95"/>' for x, r in ((30, 70), (110, 50), (620, 64), (700, 54)))
    trees = trees + ''.join(f'<g opacity=".55">{place(PROPS["tree"].render(c), x, FLOOR - 230, .3)}</g>' for x in (120, 300, 420, 620))
    grass = f'<rect y="{FLOOR}" width="{W}" height="{H - FLOOR}" fill="{c["floor"]}"/>' + ''.join(f'<path d="M{x} {y}l6 -16l6 16" fill="none" stroke="{c["light"]}" stroke-width="3" opacity=".3"/>' for x, y in [((k * 53) % W, FLOOR + 30 + (k * 37) % 200) for k in range(40)])
    return sky + clouds + kites + hills + trees + fence + bushes + grass + path_ + f'<path d="M0 {FLOOR + 2}H{W}" stroke="{c["dark"]}" stroke-width="4" opacity=".2"/>'


def _beach(c):
    sky = f'<rect width="{W}" height="{FLOOR}" fill="{c["wall"]}"/>' + _bands(c, (c['light'], c['wall'], c['pop']), (.3, 0, .25))
    sea_y = FLOOR - 330
    sea = f'<rect y="{sea_y}" width="{W}" height="{FLOOR - sea_y}" fill="{c["accent"]}"/>' + ''.join(f'<path d="M{x} {y}q20 -12 40 0t40 0" fill="none" stroke="{c["light"]}" stroke-width="5" opacity=".55"/>' for x, y in [((k * 97) % 680, sea_y + 40 + (k * 61) % 240) for k in range(16)])
    sun = f'<circle cx="160" cy="{sea_y - 10}" r="90" fill="{c["secondary"]}" opacity=".9"/><rect y="{sea_y}" width="{W}" height="20" fill="{c["accent"]}"/>'
    sand = f'<path d="M0 {FLOOR - 80}Q360 {FLOOR - 140} 720 {FLOOR - 60}V{H}H0Z" fill="{c["secondary"]}"/>' + ''.join(f'<circle cx="{(k * 71) % W}" cy="{FLOOR + 20 + (k * 43) % 200}" r="3" fill="{c["dark"]}" opacity=".15"/>' for k in range(50))
    clouds = ''.join(f'<g opacity=".85">{place(PROPS["cloud"].render(c), x, y, s)}</g>' for x, y, s in ((470, 260, 1.0), (180, 380, .7), (620, 470, .6), (330, 520, .5)))
    birds = ''.join(f'<path d="M{x} {y}q14 -14 28 0q14 -14 28 0" fill="none" stroke="{c["dark"]}" stroke-width="4" opacity=".6"/>' for x, y in ((300, 330), (380, 290), (560, 380), (120, 250)))
    boats = ''.join(f'<path d="M{x} {sea_y + 70}h70l-12 18h-46Z" fill="{c["light"]}"/><path d="M{x + 34} {sea_y + 66}V{sea_y - 10}L{x + 70} {sea_y + 60}Z" fill="{col}"/>' for x, col in ((420, c['pop']), (560, c['primary'])))
    huts = ''.join(f'<rect x="{x}" y="{FLOOR - 230}" width="80" height="130" fill="{col}" stroke="{c["dark"]}" stroke-width="3"/><path d="M{x - 10} {FLOOR - 230}L{x + 40} {FLOOR - 280}L{x + 90} {FLOOR - 230}Z" fill="{c["light"]}" stroke="{c["dark"]}" stroke-width="3"/>'
                   + ''.join(f'<rect x="{x + k}" y="{FLOOR - 230}" width="10" height="130" fill="{c["light"]}" opacity=".5"/>' for k in (14, 44)) for x, col in ((20, c['pop']), (120, c['primary']), (610, c['pop'])))
    return sky + clouds + birds + sun + sea + boats + sand + huts + f'<path d="M0 {FLOOR + 2}H{W}" stroke="{c["dark"]}" stroke-width="3" opacity=".12"/>'


def _rooftop(c):
    sky = f'<rect width="{W}" height="{FLOOR}" fill="{c["wall"]}"/>' + _bands(c, (c['pop'], c['wall'], c['light']), (.25, 0, .35))
    city = ''.join(f'<rect x="{x}" y="{FLOOR - h}" width="{w}" height="{h}" fill="{c["metal"]}" opacity=".55"/>' + ''.join(f'<rect x="{x + 12 + i * 22}" y="{FLOOR - h + 20 + j * 34}" width="10" height="16" fill="{c["light"]}" opacity=".45"/>' for i in range(max(1, (w - 20) // 22)) for j in range(max(1, (h - 40) // 34)) if (i + j + x) % 3)
                   for x, w, h in ((0, 120, 420), (130, 90, 560), (230, 140, 380), (380, 100, 620), (490, 130, 460), (630, 90, 520)))
    parapet = f'<rect y="{FLOOR - 70}" width="{W}" height="70" fill="{c["primary"]}"/><rect y="{FLOOR - 80}" width="{W}" height="14" fill="{c["light"]}" opacity=".6"/>' + ''.join(f'<path d="M{x} {FLOOR - 66}V{FLOOR}" stroke="{c["dark"]}" stroke-width="3" opacity=".2"/>' for x in range(40, W, 80))
    return sky + city + parapet + _floor(c, 'tiles')


def _bakery(c):
    awning = ''.join(f'<path d="M{x} 0H{x + 60}V140Q{x + 30} 176 {x} 140Z" fill="{c["primary"] if (x // 60) % 2 else c["light"]}"/>' for x in range(0, W, 60))
    shelves = ''.join(f'<rect x="40" y="{y}" width="640" height="16" fill="{c["secondary"]}" opacity=".85"/>' + ''.join(f'<circle cx="{x}" cy="{y - 24}" r="22" fill="{[c["pop"], c["accent"], c["primary"]][(x // 90) % 3]}" opacity=".75"/>' for x in range(90, 680, 90)) for y in (330, 470))
    counter = f'<rect y="{FLOOR - 230}" width="{W}" height="230" fill="{c["secondary"]}" opacity=".6"/>'
    return f'<rect width="{W}" height="{FLOOR}" fill="{c["wall"]}"/>' + _diamonds(c, c['light'], 40, .35) + shelves + awning + counter + _floor(c, 'tiles')


ROOMS = {
    'office': {'draw': _office, 'dressing': ('plant', 'filing-cabinet', 'chair', 'bookshelf', 'cactus', 'trash-can', 'wall-clock', 'whiteboard', 'window', 'poster', 'wall-sign', 'pendant-lamp'), 'costumes': ('glasses', 'headset', 'bowtie'), 'lights': [{'kind': 'window', 'colour': '#FFF0CF'}]},
    'diner': {'draw': _diner, 'dressing': ('stool', 'diner-counter', 'fridge', 'trash-can', 'menu-board', 'neon-sign', 'wall-clock', 'pendant-lamp', 'string-lights'), 'costumes': ('chef-hat', 'apron', 'cap'), 'lights': [{'kind': 'lamp', 'colour': '#FFD58A'}]},
    'street': {'draw': _street, 'dressing': ('street-lamp', 'bench', 'traffic-cone', 'hydrant', 'trash-can', 'wall-sign', 'neon-sign', 'cloud', 'sun', 'hot-air-balloon'), 'costumes': ('cap', 'scarf', 'hi-vis', 'beanie'), 'lights': [{'kind': 'beam', 'colour': '#FFF0CF'}]},
    'stage': {'draw': _stage, 'dressing': ('curtain', 'spotlight-stand', 'speaker', 'mic-stand', 'bunting', 'stool'), 'costumes': ('bowtie', 'cape', 'party-hat', 'headset'), 'lights': [{'kind': 'beam', 'colour': '#FFE7A8'}, {'kind': 'lamp', 'colour': '#FFD58A'}]},
    'workshop': {'draw': _workshop, 'dressing': ('ladder', 'toolbox', 'crate', 'barrel', 'pegboard', 'shelf', 'pendant-lamp', 'stool'), 'costumes': ('hard-hat', 'hi-vis', 'apron', 'glasses'), 'lights': [{'kind': 'lamp', 'colour': '#FFD58A'}]},
    'night-sky': {'draw': _night_sky, 'dressing': ('moon', 'stars', 'cloud', 'street-lamp', 'bench', 'hot-air-balloon', 'cactus'), 'costumes': ('beanie', 'scarf', 'cape'), 'lights': [{'kind': 'lamp', 'colour': '#BFD8FF'}]},
    'server-room': {'draw': _server_room, 'dressing': ('server-rack', 'crate', 'trash-can', 'wall-sign', 'filing-cabinet', 'pendant-lamp'), 'costumes': ('headset', 'glasses', 'hi-vis'), 'lights': [{'kind': 'beam', 'colour': '#BFF3EA'}]},
    'arcade': {'draw': _arcade, 'dressing': ('arcade-cabinet', 'neon-sign', 'speaker', 'stool', 'string-lights', 'poster', 'trash-can'), 'costumes': ('headset', 'cap', 'glasses'), 'lights': [{'kind': 'beam', 'colour': '#E7C6FF'}]},
    'park': {'draw': _park, 'dressing': ('tree', 'bench', 'street-lamp', 'plant', 'trash-can', 'cloud', 'sun', 'hot-air-balloon'), 'costumes': ('cap', 'scarf', 'beanie'), 'lights': [{'kind': 'beam', 'colour': '#FFF6D8'}]},
    'beach': {'draw': _beach, 'dressing': ('beach-umbrella', 'crate', 'barrel', 'sun', 'cloud', 'hot-air-balloon', 'cactus'), 'costumes': ('cap', 'glasses', 'party-hat'), 'lights': [{'kind': 'beam', 'colour': '#FFF2C8'}]},
    'rooftop': {'draw': _rooftop, 'dressing': ('water-tower', 'crate', 'traffic-cone', 'string-lights', 'cloud', 'moon', 'barrel'), 'costumes': ('hi-vis', 'beanie', 'scarf'), 'lights': [{'kind': 'lamp', 'colour': '#FFD9B8'}]},
    'bakery': {'draw': _bakery, 'dressing': ('cake-stand', 'diner-counter', 'stool', 'menu-board', 'wall-clock', 'pendant-lamp', 'plant'), 'costumes': ('chef-hat', 'apron', 'bowtie'), 'lights': [{'kind': 'lamp', 'colour': '#FFE2C2'}]},
    'living-room': {'draw': _living_room, 'dressing': ('sofa', 'armchair', 'floor-lamp', 'plant', 'coffee-table', 'bookshelf', 'framed-picture', 'window', 'shelf', 'string-lights'), 'costumes': ('scarf', 'beanie', 'glasses'), 'lights': [{'kind': 'lamp', 'colour': '#FFD58A'}]},
}


# Geometry ----------------------------------------------------------------------

def _rng(*key):
    return random.Random(int(hashlib.sha256('|'.join(map(str, key)).encode()).hexdigest()[:16], 16))


def _box(x, y, scale, box):
    bx, by, bw, bh = box;return (x + bx * scale, y + by * scale, bw * scale, bh * scale)


def _overlap(a, b):
    w = min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0]);h = min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1])
    return max(0.0, w) * max(0.0, h)


def _crosses_edge(box):
    return box[0] < 0 or box[0] + box[2] > W


def _in_headline(box):
    hx, hy, hw, hh = HEADLINE
    if _overlap(box, HEADLINE) == 0:return False
    return not (box[0] + box[2] <= SIDE or box[0] >= W - SIDE)


def _in_caption(box):
    return box[1] + box[3] > CAPTION[1] + 1e-6


def hero_big_enough(w, h):
    """The hero reads as the subject: HERO_MIN of frame height, or a wide machine
    at HERO_WIDE (share of height, share of width)."""
    return h >= HERO_MIN * H - 1e-6 or (h >= HERO_WIDE[0] * H - 1e-6 and w >= HERO_WIDE[1] * W - 1e-6)


def hero_placement(rig, rng):
    """Hero on the floor, as large as the bands allow while leaving a lane on the
    rig's Bot side (BOT_LANE) so Bot stands beside the machine, not over its labels."""
    fx, fy, fw, fh = rig.footprint;tall = (FLOOR - HEADLINE[1] - HEADLINE[3] - 10) / fh
    scale = min((W - BOT_LANE - HERO_SAFE) / fw, tall, 1.6)
    if not hero_big_enough(fw * scale, fh * scale):
        # Wide machine: just big enough (tall, or wide and nearly tall) so Bot keeps a lane clear of its edge labels.
        need = min(HERO_MIN * H / fh, max(HERO_WIDE[0] * H / fh, HERO_WIDE[1] * W / fw)) + 1e-4
        scale = min(need, (W - 2 * HERO_SAFE) / fw, tall)
    if not hero_big_enough(fw * scale, fh * scale):scale = min(700 / fw, tall, 1.6)   # the widest machines trade the camera margin for size
    if not hero_big_enough(fw * scale, fh * scale):raise ValueError(f'{rig.name}: cannot reach {HERO_MIN:.0%} of frame height inside the bands')
    side = -1 if rig.bot_slot['x'] < 0 else 1
    centre = -(fx + fw / 2) * scale;slack = max(0.0, (W - fw * scale) / 2 - HERO_SAFE)
    x = 360 + centre - side * (slack - rng.uniform(0, 1) * min(20, slack * .2))  # jitter inward only
    return {'rig': rig.name, 'x': round(x, 2), 'y': FLOOR, 'scale': round(scale, 4), 'box': [round(v, 2) for v in _box(x, FLOOR, scale, rig.footprint)]}


def _place_prop(name, rng, hero_box, role, bot_side=0):
    """Candidate placement for one prop. role: edge | overlap | back."""
    p = PROPS[name];target_h = {'floor': (260, 520), 'wall': (150, 260), 'ceiling': (120, 300), 'sky': (110, 200)}[p.mount]
    hx, hy, hw, hh = hero_box
    scale = min(rng.uniform(*target_h) / p.h, 760 / p.w, PROP_MAX_SCALE)
    if role == 'overlap':scale = min(scale, rng.uniform(.25, .38) * hh / p.h)  # a foreground corner, never a wall in front of the hero
    w, h = p.w * scale, p.h * scale
    if role == 'edge':
        # Cropped by the frame edge, but by at most 1 - EDGE_VISIBLE of its width: it reads as a whole object.
        side = rng.choice((-1, 1));cut = rng.uniform(.08, 1 - EDGE_VISIBLE - .02);left = p.box[0] * scale
        x = (-w * cut - left) if side < 0 else (W + w * cut - left - w)
    elif role == 'overlap':
        side = rng.choice((-1, 1)) if not bot_side else -bot_side  # the foreground corner away from Bot
        x = (hx + w * rng.uniform(.0, .3) if side < 0 else hx + hw - w * rng.uniform(.0, .3))
    else:  # fill the wider empty side beside the hero
        left, right = hx, W - (hx + hw)
        if max(left, right) > w * .5:x = rng.uniform(w * .1, max(w * .1, left - w * .3)) if left >= right else rng.uniform(min(W - w * .1, hx + hw + w * .3), W - w * .1)
        else:x = rng.uniform(w / 2 + 20, W - w / 2 - 20)
    if p.mount == 'floor':y = FLOOR + (rng.uniform(10, 36) if role == 'overlap' else 0)
    elif p.mount == 'wall':y = rng.uniform(max(HEADLINE[1] + HEADLINE[3] + h + 20, 520), FLOOR - 160)
    elif p.mount == 'ceiling':y = h if name in ('bunting', 'string-lights') else rng.uniform(h * .6, h)
    else:y = rng.uniform(HEADLINE[1] + HEADLINE[3] + h + 30, 640)
    box = _box(x, y, scale, p.box)
    return {'prop': name, 'x': round(x, 2), 'y': round(y, 2), 'scale': round(scale, 4), 'box': [round(v, 2) for v in box], 'role': role,
            'layer': 'front' if role == 'overlap' else 'back'}


def visible_share(box):
    return max(0.0, min(W, box[0] + box[2]) - max(0.0, box[0])) / max(1e-9, box[2])


def _valid_item(item, hero_box, placed, bot_box=None):
    box = item['box']
    # Nothing in front of Bot, and nothing on its patch of floor even behind it.
    if bot_box and _overlap(box, bot_box) > (0 if item['layer'] == 'front' else .2 * box[2] * box[3]):return False
    if _in_headline(box) or _in_caption(box):return False
    if visible_share(box) < EDGE_VISIBLE - 1e-6:return False
    if item['role'] == 'overlap':
        share = _overlap(box, hero_box) / (hero_box[2] * hero_box[3])
        if not 0 < share <= .08 or box[3] > .4 * hero_box[3]:return False
    elif item['layer'] == 'back' and item['role'] == 'back' and _overlap(box, hero_box) > .5 * box[2] * box[3]:return False
    for other in placed:
        if _overlap(box, other['box']) > .25 * min(box[2] * box[3], other['box'][2] * other['box'][3]):return False
    return True


def bot_placement(rig, hero, hero_box):
    """Bot inside the action: on the floor at the rig's slot side, large enough to
    read (BOT_SCALE), overlapping the hero's edge so it touches the machine, and
    never cropped by the frame. Returns (x, y, scale, side)."""
    slot = rig.bot_slot;s = min(BOT_SCALE[1], max(BOT_SCALE[0], slot['scale'] * hero['scale'] * 1.6))
    half = BOT_HALF * s;left, right = hero_box[0], hero_box[0] + hero_box[2]
    side = -1 if slot['x'] < 0 else 1
    # Feet at the hero's edge, a sliver over the machine so it touches it.
    x = left - half * BOT_TOUCH if side < 0 else right + half * BOT_TOUCH
    lo, hi = half + 55, W - half - 55  # room for camera push-ins (punch/pan) without cropping Bot
    if not lo <= x <= hi:
        other = right + half * BOT_TOUCH if side < 0 else left - half * BOT_TOUCH
        x, side = (other, -side) if lo <= other <= hi else (min(hi, max(lo, x)), side)
    return x, FLOOR, s, side


def solve(room, rig_name, values=None, palette=None, seed=0, beat=0, costume=None, count=4):
    """Deterministic set layout for one beat."""
    if room not in ROOMS:raise ValueError(f'unknown room {room}; choose from {sorted(ROOMS)}')
    rig = get_rig(rig_name);rng = _rng(room, rig_name, seed, beat)
    palette = palette or rotation(beat + 1, seed)[beat]
    if palette not in PALETTES:raise ValueError(f'unknown palette {palette}')
    hero = hero_placement(rig, rng);hero_box = hero['box']
    bx, by, bscale, side = bot_placement(rig, hero, hero_box);half = BOT_HALF * bscale
    bot_box = (bx - half, by - 4.2 * half, 2 * half, 4.2 * half)
    pool = list(ROOMS[room]['dressing']);rng.shuffle(pool)
    roles = ['edge', 'overlap', 'back', 'back'][:max(2, min(4, count))];placed = []
    for role in roles:
        candidates = [n for n in pool if n not in {i['prop'] for i in placed}]
        if role == 'overlap':candidates = [n for n in candidates if PROPS[n].mount == 'floor']
        if role == 'edge':candidates = [n for n in candidates if PROPS[n].mount in ('floor', 'wall', 'ceiling')]
        for attempt in range(60):
            if not candidates:break
            item = _place_prop(candidates[attempt % len(candidates)], rng, hero_box, role, side)
            if _valid_item(item, hero_box, placed, bot_box):placed.append(item);break
    if not any(_crosses_edge(i['box']) for i in placed):raise ValueError(f'{room}/{rig_name}: no dressing reaches a frame edge')
    if not any(_overlap(i['box'], hero_box) > 0 for i in placed):raise ValueError(f'{room}/{rig_name}: no dressing overlaps the hero')
    costume = costume if costume is not None else [rng.choice(ROOMS[room]['costumes'])]
    for name in costume:
        if name not in COSTUMES:raise ValueError(f'unknown costume {name}')
    return {'room': room, 'palette': palette, 'seed': seed, 'beat': beat, 'floor_y': FLOOR, 'hero': {**hero, 'values': values or {}},
            'bot': {'x': round(bx, 2), 'y': round(by, 2), 'scale': round(bscale, 4), 'costume': costume, 'role': rig.bot_slot.get('role', ''), 'side': side},
            'dressing': placed, 'lights': ROOMS[room]['lights'], 'bands': {'headline': list(HEADLINE), 'caption': list(CAPTION)}}


def compose(layout, pose=None, face='happy', bot_pose='standing'):
    """World markup for a solved layout at one rig pose."""
    c = get_palette(layout['palette']);room = ROOMS[layout['room']];rig = get_rig(layout['hero']['rig'])
    out = [room['draw'](c)]
    for item in layout['dressing']:
        if item['layer'] == 'back':out.append(place(PROPS[item['prop']].render(c), item['x'], item['y'], item['scale']))
    h = layout['hero'];out.append(place(rig.render(h.get('values') or None, pose, layout['palette']), h['x'], h['y'], h['scale']))
    b = layout['bot']
    if b:out.append(dressed_bot(b['x'], b['y'], b['scale'], face=face, pose=bot_pose, costume=b['costume'], palette=layout['palette']))
    for item in layout['dressing']:
        if item['layer'] == 'front':out.append(place(PROPS[item['prop']].render(c), item['x'], item['y'], item['scale']))
    return ''.join(out)


def solve_checked(room, rig_name, values=None, palette=None, seed=0, beat=0, costume=None, tries=8, work=None):
    """solve(), rendered and measured: re-solves with new seeds until the frame
    passes the empty-field limit at both the start and the end of the rig's first action."""
    import tempfile
    rig = get_rig(rig_name);action = next(iter(rig.actions))
    with tempfile.TemporaryDirectory() as tmp:
        last = None
        for k in range(tries):
            try:layout = solve(room, rig_name, values, palette, seed * 101 + k, beat, costume)
            except ValueError as error:last = str(error);continue
            if palette is None:layout['palette'] = rotation(beat + 1, seed)[beat]
            scores = [empty_field(render_png(layout, Path(work or tmp) / f'{room}-{rig_name}-{beat}-{k}-{t}.png', (action, t))) for t in (0.0, 1.0)]
            layout['empty_field'] = round(max(scores), 4)
            if layout['empty_field'] <= EMPTY_FIELD_MAX:layout['seed'] = seed;layout['variant'] = k;return layout
            last = f'empty field {layout["empty_field"]}'
    raise ValueError(f'{room}/{rig_name}: no layout passed after {tries} tries ({last})')


def plan_sets(beats, seed=0):
    """Layouts for a sequence of beats [{room, rig, values?, costume?}], palettes rotated so neighbours differ."""
    palettes = rotation(len(beats), seed)
    return [solve_checked(b['room'], b['rig'], b.get('values'), b.get('palette') or palettes[i], seed, i, b.get('costume')) for i, b in enumerate(beats)]


# Empty-field check ---------------------------------------------------------------

def empty_field(image, cell=16, std_max=6.0, colour_dist=18.0):
    """Share of the focal band that is flat background: cells with almost no
    texture whose colour sits near the frame's dominant colour. Measured at
    360 px wide so sizes compare across renders."""
    import numpy as np
    from PIL import Image
    im = image if hasattr(image, 'convert') else Image.open(image)
    im = im.convert('RGB');w, h = im.size;im = im.resize((360, round(360 * h / w)), Image.BILINEAR)
    a = np.asarray(im).astype(float);rows = a.shape[0]
    band = a[int(rows * FOCAL[0]):int(rows * FOCAL[1])]
    q = (band // 16).reshape(-1, 3);vals, counts = np.unique(q, axis=0, return_counts=True)
    dominant = band.reshape(-1, 3)[(q == vals[counts.argmax()]).all(1)].mean(0)
    total = flat = 0
    for y in range(0, band.shape[0] - cell + 1, cell):
        for x in range(0, band.shape[1] - cell + 1, cell):
            block = band[y:y + cell, x:x + cell];total += 1
            if block.std(axis=(0, 1)).max() < std_max and np.linalg.norm(block.mean((0, 1)) - dominant) < colour_dist:flat += 1
    return flat / total if total else 0.0


def check_frames(paths):
    rows = [{'frame': str(p), 'empty_field': round(empty_field(p), 4)} for p in paths]
    failures = [r for r in rows if r['empty_field'] > EMPTY_FIELD_MAX]
    return {'status': 'FAIL' if failures else 'PASS', 'limit': EMPTY_FIELD_MAX, 'frames': rows, 'failures': [r['frame'] for r in failures]}


def render_png(layout, path, pose=None, size=(360, 640)):
    from motif_rigs.base import raster
    return raster(compose(layout, pose), path, size)


def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n')[0]);sub = p.add_subparsers(dest='cmd', required=True)
    e = sub.add_parser('empty-field');e.add_argument('frames', nargs='+', type=Path)
    s = sub.add_parser('solve');s.add_argument('room');s.add_argument('rig');s.add_argument('--seed', type=int, default=0);s.add_argument('--beat', type=int, default=0);s.add_argument('--png', type=Path)
    a = p.parse_args()
    if a.cmd == 'empty-field':
        r = check_frames(a.frames);print(json.dumps(r, indent=2));sys.exit(0 if r['status'] == 'PASS' else 1)
    layout = solve(a.room, a.rig, seed=a.seed, beat=a.beat);print(json.dumps(layout, indent=2))
    if a.png:render_png(layout, a.png)


if __name__ == '__main__':
    main()
