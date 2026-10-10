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
BOT_BEHIND = .25                  # Bot overlapping the hero by more than this share of its width stands behind it
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


def _office_boards(c, vy=600):
    """Floor planks running toward the viewer, converging on a far vanishing point, with staggered end joints."""
    px = lambda x, y: x + (x - 360) * (y - FLOOR) / vy
    out = ''.join(f'<path d="M{x} {FLOOR}L{px(x, H):.1f} {H}" stroke="{c["dark"]}" stroke-width="2.5" opacity=".16"/>' for x in range(-300, W + 320, 58))
    for k, x in enumerate(range(-300, W + 320, 58)):
        for y in (FLOOR + 30 + (k * 37) % 70, FLOOR + 130 + (k * 53) % 80):
            out += f'<path d="M{px(x, y):.1f} {y}L{px(x + 58, y):.1f} {y}" stroke="{c["dark"]}" stroke-width="2" opacity=".14"/>'
    grain = ''.join(f'<path d="M{px(x + 20, FLOOR + 10):.1f} {FLOOR + 10}L{px(x + 22, H):.1f} {H}" stroke="{c["light"]}" stroke-width="1.5" opacity=".07"/>' for x in range(-300, W + 320, 58))
    return f'<rect y="{FLOOR}" width="{W}" height="{H - FLOOR}" fill="{c["floor"]}"/>' + out + grain


def _office_window(c, x):
    """Window with blinds, frame and sill, and the soft shaft of light it throws down the wall and across the floor."""
    shaft = f'<path d="M{x} 580H{x + 150}L{x + 330} {FLOOR + 150}H{x + 150}Z" fill="{c["light"]}" opacity=".09"/>'
    glass = f'<rect x="{x}" y="330" width="150" height="250" fill="{c["light"]}" opacity=".5"/>' + ''.join(f'<path d="M{x} {y}H{x + 150}" stroke="{c["metal"]}" stroke-width="5" opacity=".4"/>' for y in range(345, 580, 22))
    frame = (f'<rect x="{x - 4}" y="326" width="158" height="258" fill="none" stroke="{c["secondary"]}" stroke-width="10" opacity=".75"/><path d="M{x + 75} 330V580" stroke="{c["secondary"]}" stroke-width="6" opacity=".6"/>'
             f'<rect x="{x - 16}" y="584" width="182" height="14" fill="{c["light"]}" opacity=".7"/><rect x="{x - 12}" y="598" width="174" height="8" fill="{c["dark"]}" opacity=".1"/>')
    return shaft + glass + frame


def _diner_checker(c, vy=520):
    """Black-and-white diner checkerboard laid in perspective."""
    px = lambda x, y: x + (x - 360) * (y - FLOOR) / vy
    rows = [FLOOR + round((H - FLOOR) * (i / 5) ** 1.35) for i in range(6)]
    out = f'<rect y="{FLOOR}" width="{W}" height="{H - FLOOR}" fill="{c["floor"]}"/>'
    for r, (ya, yb) in enumerate(zip(rows, rows[1:])):
        for k, x in enumerate(range(-280, W + 280, 70)):
            if (r + k) % 2:out += f'<path d="M{px(x, ya):.1f} {ya}H{px(x + 70, ya):.1f}L{px(x + 70, yb):.1f} {yb}H{px(x, yb):.1f}Z" fill="{c["light"]}" opacity=".22"/>'
    return out + f'<rect y="{FLOOR}" width="{W}" height="16" fill="{c["dark"]}" opacity=".14"/>'


def _street_facade(c, x, w, top, colour):
    """A near building cut off by the frame edge: cornice, window grid with sills, a striped awning over the shopfront."""
    wins = ''.join(f'<rect x="{x + 14 + i * 40}" y="{y}" width="24" height="40" fill="{c["light"]}" opacity=".4"/><rect x="{x + 10 + i * 40}" y="{y + 40}" width="32" height="5" fill="{c["light"]}" opacity=".6"/>'
                   for i in range(max(1, (w - 10) // 40)) for y in range(top + 50, FLOOR - 230, 80))
    awning = ''.join(f'<path d="M{x + k} {FLOOR - 200}h20v46q-10 10 -20 0Z" fill="{c["light"] if (k // 20) % 2 else c["pop"]}" opacity=".7"/>' for k in range(0, w, 20))
    return (f'<rect x="{x}" y="{top}" width="{w}" height="{FLOOR - top}" fill="{c["metal"]}" opacity=".7"/><rect x="{x}" y="{top}" width="{w}" height="{FLOOR - top}" fill="{colour}" opacity=".3"/><rect x="{x - 6}" y="{top - 14}" width="{w + 12}" height="18" fill="{c["dark"]}" opacity=".22"/>'
            f'<rect x="{x}" y="{top + 4}" width="{w}" height="10" fill="{c["dark"]}" opacity=".08"/>' + wins + awning + f'<rect x="{x}" y="{FLOOR - 140}" width="{w}" height="140" fill="{c["dark"]}" opacity=".18"/>')


def _stage_valance(c):
    """Pelmet across the top: swagged scallops with fold shading and a fringe."""
    swags = ''.join(f'<path d="M{x} 0H{x + 120}V70Q{x + 60} 130 {x} 70Z" fill="{c["primary"]}"/><path d="M{x + 20} 74Q{x + 60} 116 {x + 100} 74" fill="none" stroke="{c["dark"]}" stroke-width="4" opacity=".2"/>'
                    f'<path d="M{x + 30} 90Q{x + 60} 112 {x + 90} 90" fill="none" stroke="{c["light"]}" stroke-width="3" opacity=".25"/>' for x in range(-60, W, 120))
    fringe = ''.join(f'<path d="M{x} {round(70 + 30 * (1 - ((x + 60) % 120 / 60 - 1) ** 2))}v12" stroke="{c["secondary"]}" stroke-width="3" opacity=".8"/>' for x in range(-56, W, 8))
    return f'<rect width="{W}" height="70" fill="{c["primary"]}"/>' + swags + fringe + f'<rect y="0" width="{W}" height="16" fill="{c["dark"]}" opacity=".15"/>'


def _workshop_concrete(c, vy=520):
    """Poured slab floor: perspective expansion joints, scuffs, and a hazard stripe along the wall."""
    px = lambda x, y: x + (x - 360) * (y - FLOOR) / vy
    joints = ''.join(f'<path d="M{x} {FLOOR}L{px(x, H):.1f} {H}" stroke="{c["dark"]}" stroke-width="3" opacity=".16"/>' for x in range(-360, W + 400, 180)) + ''.join(f'<path d="M0 {y}H{W}" stroke="{c["dark"]}" stroke-width="3" opacity=".14"/>' for y in (FLOOR + 70, FLOOR + 170))
    scuffs = ''.join(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{rx // 4}" fill="{c["dark"]}" opacity=".07"/>' for x, y, rx in ((90, FLOOR + 120, 50), (620, FLOOR + 210, 70), (480, FLOOR + 60, 34), (200, FLOOR + 220, 40)))
    flecks = ''.join(f'<circle cx="{(k * 89) % W}" cy="{FLOOR + 24 + (k * 47) % 210}" r="2" fill="{c["light"]}" opacity=".18"/>' for k in range(36))
    hazard = f'<rect y="{FLOOR}" width="{W}" height="16" fill="{c["secondary"]}" opacity=".55"/>' + ''.join(f'<path d="M{x} {FLOOR + 16}l16 -16h14l-16 16Z" fill="{c["dark"]}" opacity=".35"/>' for x in range(-16, W, 30))
    return f'<rect y="{FLOOR}" width="{W}" height="{H - FLOOR}" fill="{c["floor"]}"/>' + joints + scuffs + flecks + hazard + f'<rect y="{FLOOR + 16}" width="{W}" height="10" fill="{c["dark"]}" opacity=".12"/>'


def _server_ceiling(c):
    """Ceiling slab with recessed light strips, a ladder cable tray and drooping cable loops."""
    tray = f'<rect y="58" width="{W}" height="6" fill="{c["metal"]}" opacity=".5"/><rect y="84" width="{W}" height="6" fill="{c["metal"]}" opacity=".5"/>' + ''.join(f'<rect x="{x}" y="58" width="4" height="32" fill="{c["metal"]}" opacity=".4"/>' for x in range(10, W, 30))
    loops = ''.join(f'<path d="M{x} 88q{w / 2} {d} {w} 0" fill="none" stroke="{col}" stroke-width="4" opacity=".35"/>' for x, w, d, col in ((10, 120, 40, c['accent']), (90, 90, 26, c['pop']), (520, 110, 34, c['pop']), (600, 110, 44, c['accent']), (260, 200, 18, c['primary'])))
    hangers = ''.join(f'<path d="M{x} 36V60" stroke="{c["metal"]}" stroke-width="3" opacity=".45"/>' for x in range(40, W, 160))
    return (f'<rect width="{W}" height="36" fill="{c["dark"]}" opacity=".55"/>' + ''.join(f'<rect x="{x}" y="12" width="120" height="8" rx="4" fill="{c["light"]}" opacity=".35"/>' for x in (30, 300, 570))
            + f'<rect y="36" width="{W}" height="8" fill="{c["dark"]}" opacity=".2"/>' + hangers + tray + loops)


def _office(c):
    paper = ''.join(f'<path d="M{x} {y}l5 -9l5 9l-5 9Z" fill="{c["light"]}" opacity=".16"/>' for x in range(25, W, 60) for y in range(110 + (x // 60) % 2 * 60, FLOOR - 240, 120))
    crown = (f'<rect width="{W}" height="40" fill="{c["secondary"]}" opacity=".7"/><rect y="40" width="{W}" height="6" fill="{c["light"]}" opacity=".55"/><rect y="46" width="{W}" height="12" fill="{c["dark"]}" opacity=".07"/>'
             + ''.join(f'<rect x="{x}" y="22" width="12" height="12" fill="{c["dark"]}" opacity=".12"/>' for x in range(6, W, 26)))
    y0 = FLOOR - 220
    panels = ''.join(f'<rect x="{x}" y="{y0 + 30}" width="96" height="140" fill="{c["light"]}" opacity=".07"/><path d="M{x} {y0 + 170}V{y0 + 30}H{x + 96}" fill="none" stroke="{c["light"]}" stroke-width="3" opacity=".35"/>'
                     f'<path d="M{x + 96} {y0 + 30}V{y0 + 170}H{x}" fill="none" stroke="{c["dark"]}" stroke-width="3" opacity=".2"/>' for x in range(16, W, 120))
    wainscot = (f'<rect y="{y0}" width="{W}" height="220" fill="{c["secondary"]}" opacity=".55"/>' + panels
                + f'<rect y="{y0 - 14}" width="{W}" height="18" fill="{c["secondary"]}"/><rect y="{y0 - 14}" width="{W}" height="4" fill="{c["light"]}" opacity=".5"/><rect y="{y0 + 4}" width="{W}" height="8" fill="{c["dark"]}" opacity=".1"/>'
                + f'<rect y="{FLOOR - 30}" width="{W}" height="30" fill="{c["secondary"]}"/><rect y="{FLOOR - 30}" width="{W}" height="4" fill="{c["light"]}" opacity=".45"/><rect y="{FLOOR - 26}" width="{W}" height="26" fill="{c["dark"]}" opacity=".08"/>')
    return (f'<rect width="{W}" height="{FLOOR}" fill="{c["wall"]}"/>' + _bands(c, (c['dark'], c['wall'], c['light']), (.12, 0, .1)) + _stripes(c, c['secondary'], 60, 22, .16) + paper
            + crown + wainscot + _office_boards(c) + _office_window(c, 40) + _office_window(c, 530)
            + f'<rect y="{FLOOR}" width="{W}" height="14" fill="{c["dark"]}" opacity=".12"/><path d="M0 {FLOOR + 2}H{W}" stroke="{c["dark"]}" stroke-width="4" opacity=".35"/>')


def _diner(c):
    y0 = FLOOR - 352
    soffit = (f'<rect width="{W}" height="54" fill="{c["secondary"]}" opacity=".55"/>' + ''.join(f'<circle cx="{x}" cy="54" r="15" fill="{c["secondary"]}" opacity=".55"/>' for x in range(15, W + 30, 30))
              + f'<rect y="62" width="{W}" height="10" fill="{c["dark"]}" opacity=".06"/>' + ''.join(f'<circle cx="{x}" cy="28" r="5" fill="{c["light"]}" opacity=".5"/>' for x in range(30, W, 60)))
    grout = ''.join(f'<path d="M0 {y}H{W}" stroke="{c["dark"]}" stroke-width="1.5" opacity=".07"/>' for y in range(y0 + 22, FLOOR, 50)) + ''.join(f'<path d="M{x} {y0 + 22}V{FLOOR}" stroke="{c["dark"]}" stroke-width="1.5" opacity=".07"/>' for x in range(0, W, 50))
    chrome = (f'<rect y="{y0 - 8}" width="{W}" height="8" fill="{c["metal"]}" opacity=".8"/><rect y="{y0 - 8}" width="{W}" height="2" fill="{c["light"]}" opacity=".7"/>'
              f'<rect y="{y0 + 22}" width="{W}" height="8" fill="{c["metal"]}" opacity=".8"/><rect y="{y0 + 22}" width="{W}" height="2" fill="{c["light"]}" opacity=".7"/><rect y="{y0 + 30}" width="{W}" height="8" fill="{c["dark"]}" opacity=".08"/>')
    kick = f'<rect y="{FLOOR - 44}" width="{W}" height="44" fill="{c["metal"]}" opacity=".75"/>' + ''.join(f'<path d="M0 {y}H{W}" stroke="{c["light"]}" stroke-width="2" opacity=".35"/>' for y in range(FLOOR - 38, FLOOR, 9))
    ports = ''.join(f'<circle cx="{x}" cy="470" r="58" fill="{c["metal"]}" opacity=".7"/><circle cx="{x}" cy="470" r="46" fill="{c["light"]}" opacity=".55"/><path d="M{x - 26} 450a32 32 0 0 1 30 -22" fill="none" stroke="{c["light"]}" stroke-width="6" stroke-linecap="round" opacity=".8"/>' for x in (40, 680))
    return (f'<rect width="{W}" height="{FLOOR}" fill="{c["wall"]}"/>' + _bands(c, (c['dark'], c['wall'], c['light']), (.1, 0, .06)) + _stripes(c, c['secondary'], 80, 40, .3) + soffit + ports
            + _tiles(c, c['light'], y0, FLOOR, 50, .45) + grout + f'<rect y="{y0}" width="{W}" height="22" fill="{c["pop"]}"/>' + chrome + kick
            + _diner_checker(c) + f'<path d="M0 {FLOOR + 2}H{W}" stroke="{c["dark"]}" stroke-width="4" opacity=".35"/>')


def _street(c):
    px = lambda x, y: x + (x - 360) * (y - FLOOR) / 500
    sky = f'<rect width="{W}" height="{FLOOR}" fill="{c["wall"]}"/>' + _bands(c, (c['accent'], c['wall'], c['light']), (.18, 0, .25))
    sun = ''.join(f'<circle cx="590" cy="250" r="{r}" fill="{c["light"]}" opacity="{o}"/>' for r, o in ((150, .07), (110, .09), (70, .55)))
    clouds = ''.join(f'<rect x="{x}" y="{y}" width="{w}" height="18" rx="9" fill="{c["light"]}" opacity=".35"/><rect x="{x + 30}" y="{y - 14}" width="{w - 70}" height="16" rx="8" fill="{c["light"]}" opacity=".3"/>' for x, y, w in ((-30, 150, 200), (520, 110, 230), (40, 420, 120), (590, 470, 150)))
    wires = ''.join(f'<path d="M-10 {y}Q360 {y + 70} 730 {y - 10}" fill="none" stroke="{c["dark"]}" stroke-width="2" opacity=".22"/>' for y in (40, 62))
    city = PROPS['skyline'].render(c)
    far = f'<g opacity=".22">{place(city, 200, FLOOR - 40, .8)}</g><g opacity=".22">{place(city, 600, FLOOR - 60, .7)}</g>'
    near = _street_facade(c, -20, 120, 330, c['primary']) + _street_facade(c, 618, 130, 410, c['secondary'])
    walk = (f'<rect y="{FLOOR}" width="{W}" height="{H - FLOOR}" fill="{c["floor"]}"/><rect y="{FLOOR}" width="{W}" height="86" fill="{c["light"]}" opacity=".18"/>'
            + ''.join(f'<path d="M{x} {FLOOR}L{px(x, FLOOR + 86):.1f} {FLOOR + 86}" stroke="{c["dark"]}" stroke-width="2" opacity=".14"/>' for x in range(-120, W + 140, 90))
            + f'<path d="M0 {FLOOR + 40}H{W}" stroke="{c["dark"]}" stroke-width="2" opacity=".1"/><rect y="{FLOOR + 86}" width="{W}" height="16" fill="{c["metal"]}"/><rect y="{FLOOR + 86}" width="{W}" height="3" fill="{c["light"]}" opacity=".5"/>'
            + f'<rect y="{FLOOR + 102}" width="{W}" height="{H - FLOOR - 102}" fill="{c["dark"]}" opacity=".2"/><rect y="{FLOOR + 102}" width="{W}" height="14" fill="{c["dark"]}" opacity=".12"/>'
            + ''.join(f'<path d="M{x} {FLOOR + 170}h{w}l6 14h{-w - 12}Z" fill="{c["light"]}" opacity=".55"/>' for x, w in ((-40, 70), (110, 74), (270, 78), (440, 78), (610, 74)))
            + f'<rect x="40" y="{FLOOR + 104}" width="56" height="12" fill="{c["dark"]}" opacity=".3"/>' + ''.join(f'<path d="M{x} {FLOOR + 104}v12" stroke="{c["metal"]}" stroke-width="2" opacity=".6"/>' for x in range(46, 96, 8)))
    return sky + sun + clouds + wires + far + f'<g opacity=".55">{place(city, 360, FLOOR, 1.0)}</g>' + near + walk + f'<path d="M0 {FLOOR + 2}H{W}" stroke="{c["dark"]}" stroke-width="4" opacity=".35"/>'


def _stage(c):
    rays = ''.join(f'<path d="M360 -40L{x} {FLOOR}" stroke="{c["light"]}" stroke-width="70" opacity=".12"/>' for x in range(-100, 900, 100))
    arch = f'<path d="M0 0H{W}V{FLOOR}H640V260Q360 120 80 260V{FLOOR}H0Z" fill="{c["primary"]}" opacity=".85"/>'
    trim = (f'<path d="M80 {FLOOR}V260Q360 120 640 260V{FLOOR}" fill="none" stroke="{c["secondary"]}" stroke-width="6" opacity=".6"/><path d="M92 {FLOOR}V268Q360 138 628 268V{FLOOR}" fill="none" stroke="{c["dark"]}" stroke-width="5" opacity=".15"/>'
            + ''.join(f'<path d="M{x} 300V{FLOOR}" stroke="{c["dark"]}" stroke-width="3" opacity=".12"/>' for x in (12, 26, 54, 68, 652, 666, 694, 708)))
    bulbs = ''.join(f'<circle cx="{x}" cy="{y}" r="16" fill="{c["secondary"]}" opacity=".15"/><circle cx="{x}" cy="{y}" r="9" fill="{c["secondary"]}" stroke="{c["dark"]}" stroke-width="2"/>' for x, y in [(40, yy) for yy in range(300, FLOOR, 70)] + [(680, yy) for yy in range(300, FLOOR, 70)])
    folds = ''.join(f'<path d="M{x} 0V{FLOOR}" stroke="{c["dark"]}" stroke-width="5" opacity=".18"/><path d="M{x + 12} 0V{FLOOR}" stroke="{c["light"]}" stroke-width="3" opacity=".07"/>' for x in range(100, 640, 46))
    px = lambda x, y: x + (x - 360) * (y - FLOOR) / 450
    boards = (f'<rect y="{FLOOR}" width="{W}" height="{H - FLOOR}" fill="{c["floor"]}"/>' + ''.join(f'<path d="M{x} {FLOOR + 18}L{px(x, H):.1f} {H}" stroke="{c["dark"]}" stroke-width="3" opacity=".18"/>' for x in range(-240, W + 260, 60))
              + f'<path d="M0 {H - 70}Q360 {H - 100} {W} {H - 70}V{H}H0Z" fill="{c["dark"]}" opacity=".18"/><path d="M0 {H - 70}Q360 {H - 100} {W} {H - 70}" fill="none" stroke="{c["secondary"]}" stroke-width="5" opacity=".5"/>'
              + f'<rect y="{FLOOR}" width="{W}" height="18" fill="{c["secondary"]}"/><rect y="{FLOOR + 18}" width="{W}" height="10" fill="{c["dark"]}" opacity=".15"/>')
    return (f'<rect width="{W}" height="{FLOOR}" fill="{c["wall"]}"/>' + folds + rays + arch + trim + bulbs + _stage_valance(c)
            + f'<ellipse cx="360" cy="{FLOOR}" rx="320" ry="40" fill="{c["light"]}" opacity=".3"/>' + boards + f'<path d="M0 {FLOOR + 2}H{W}" stroke="{c["dark"]}" stroke-width="4" opacity=".35"/>')


def _workshop(c):
    planks = ''.join(f'<rect x="{x}" y="0" width="118" height="{FLOOR}" fill="{c["secondary"] if (x // 120) % 2 else c["wall"]}" opacity=".5"/><path d="M{x + 118} 0V{FLOOR}" stroke="{c["dark"]}" stroke-width="3" opacity=".14"/>'
                     + ''.join(f'<path d="M{x + g} 60q-8 {120 + g} 4 {260 + g * 2}t-4 {300 + g}" fill="none" stroke="{c["dark"]}" stroke-width="1.5" opacity=".07"/>' for g in (30, 74))
                     + ''.join(f'<circle cx="{x + n}" cy="{y}" r="3" fill="{c["dark"]}" opacity=".25"/>' for n in (14, 104) for y in (150, FLOOR - 300)) for x in range(0, W, 120))
    battens = ''.join(f'<rect y="{y}" width="{W}" height="20" fill="{c["floor"]}" opacity=".5"/><rect y="{y}" width="{W}" height="3" fill="{c["light"]}" opacity=".3"/><rect y="{y + 20}" width="{W}" height="8" fill="{c["dark"]}" opacity=".08"/>' for y in (140, FLOOR - 310))
    beam = (f'<rect width="{W}" height="50" fill="{c["floor"]}" opacity=".75"/><rect y="50" width="{W}" height="10" fill="{c["dark"]}" opacity=".1"/>'
            f'<path d="M-10 200L150 40M{W + 10} 200L{W - 150} 40" stroke="{c["floor"]}" stroke-width="18" opacity=".6"/><path d="M-4 206L156 46M{W + 4} 206L{W - 156} 46" stroke="{c["dark"]}" stroke-width="4" opacity=".1"/>')
    win = (f'<path d="M20 460H150L420 {FLOOR + 160}H190Z" fill="{c["light"]}" opacity=".08"/><rect x="20" y="380" width="130" height="80" fill="{c["light"]}" opacity=".55"/>'
           f'<rect x="20" y="380" width="130" height="80" fill="none" stroke="{c["floor"]}" stroke-width="8" opacity=".7"/><path d="M85 380V460M20 420H150" stroke="{c["floor"]}" stroke-width="5" opacity=".6"/>')
    ply = f'<rect y="{FLOOR - 120}" width="{W}" height="120" fill="{c["secondary"]}" opacity=".35"/><rect y="{FLOOR - 124}" width="{W}" height="6" fill="{c["light"]}" opacity=".3"/>' + ''.join(f'<path d="M{x} {FLOOR - 118}V{FLOOR}" stroke="{c["dark"]}" stroke-width="2" opacity=".12"/>' for x in range(0, W, 240)) + ''.join(f'<circle cx="{x}" cy="{y}" r="2.5" fill="{c["dark"]}" opacity=".2"/>' for x in range(12, W, 60) for y in (FLOOR - 108, FLOOR - 12))
    return f'<rect width="{W}" height="{FLOOR}" fill="{c["wall"]}"/>' + planks + battens + beam + win + ply + _workshop_concrete(c) + f'<path d="M0 {FLOOR + 2}H{W}" stroke="{c["dark"]}" stroke-width="4" opacity=".35"/>'


def _night_sky(c):
    dots = ''.join(f'<circle cx="{(k * 137) % W}" cy="{(k * 251) % (FLOOR - 200) + 40}" r="{2 + k % 3}" fill="{c["light"]}" opacity=".75"/>' for k in range(160))
    sparks = ''.join(f'<path d="M{x} {y - 12}Q{x + 2} {y - 2} {x + 12} {y}Q{x + 2} {y + 2} {x} {y + 12}Q{x - 2} {y + 2} {x - 12} {y}Q{x - 2} {y - 2} {x} {y - 12}Z" fill="{c["light"]}" opacity=".85"/>' for x, y in ((50, 130), (680, 90), (120, 420), (640, 560), (30, 640), (250, 60), (700, 330)))
    cloud = lambda y, o, d: f'<path d="M-20 {y}' + ''.join(f'Q{x + 45} {y - 34 - d * (x % 3) * 6} {x + 90} {y}' for x in range(-20, W + 20, 90)) + f'V{y + 40}H-20Z" fill="{c["light"]}" opacity="{o}"/>'
    clouds = f'<g transform="translate(-60 0)">{cloud(100, .06, 1)}</g>' + cloud(150, .05, 2)
    trees = ''.join(f'<path d="M{x} {FLOOR - 120}L{x + 30} {FLOOR - 260 - (x * 13) % 90}L{x + 60} {FLOOR - 120}Z" fill="{c["floor"]}" opacity=".9"/>' for x in range(-20, W, 52))
    near = ''.join(f'<path d="M{x} {FLOOR}L{x + 45} {FLOOR - 330 + (x * 7) % 60}L{x + 90} {FLOOR}Z" fill="{c["dark"]}" opacity=".55"/><path d="M{x + 45} {FLOOR - 300 + (x * 7) % 60}V{FLOOR}" stroke="{c["light"]}" stroke-width="2" opacity=".06"/>' for x in (-50, 10, 640, 690))
    glow = ''.join(f'<circle cx="520" cy="300" r="{r}" fill="{c["secondary"]}" opacity=".07"/>' for r in (300, 220, 150))
    peaks = f'<path d="M0 {FLOOR - 380}L90 {FLOOR - 470}L170 {FLOOR - 400}L280 {FLOOR - 520}L390 {FLOOR - 410}L470 {FLOOR - 460}L590 {FLOOR - 380}L660 {FLOOR - 430}L720 {FLOOR - 400}V{FLOOR}H0Z" fill="{c["metal"]}" opacity=".18"/>'
    hills = (f'<path d="M0 {FLOOR - 300}Q200 {FLOOR - 420} 420 {FLOOR - 300}Q600 {FLOOR - 220} 720 {FLOOR - 330}V{FLOOR}H0Z" fill="{c["metal"]}" opacity=".45"/>'
             f'<path d="M0 {FLOOR - 120}Q180 {FLOOR - 220} 360 {FLOOR - 130}Q540 {FLOOR - 50} 720 {FLOOR - 160}V{FLOOR}H0Z" fill="{c["floor"]}" opacity=".8"/>')
    town = ''.join(f'<rect x="{x}" y="{FLOOR - 330 + (x * 11) % 40 - (60 if x > 360 else 0)}" width="6" height="6" fill="{c["secondary"]}" opacity=".6"/>' for x in list(range(20, 140, 17)) + list(range(590, 710, 19)))
    px = lambda x, y: x + (x - 360) * (y - FLOOR) / 300
    ground = (f'<rect y="{FLOOR}" width="{W}" height="{H - FLOOR}" fill="{c["floor"]}"/><path d="M330 {FLOOR}H390L{px(470, H):.1f} {H}H{px(250, H):.1f}Z" fill="{c["metal"]}" opacity=".22"/>'
              + ''.join(f'<path d="M{x} {y}l5 -14l5 14l5 -10l5 10" fill="none" stroke="{c["light"]}" stroke-width="2.5" opacity=".15"/>' for x, y in [((k * 61) % W, FLOOR + 30 + (k * 43) % 200) for k in range(30)])
              + f'<rect y="{FLOOR}" width="{W}" height="20" fill="{c["dark"]}" opacity=".18"/>')
    flies = ''.join(f'<circle cx="{x}" cy="{y}" r="10" fill="{c["pop"]}" opacity=".15"/><circle cx="{x}" cy="{y}" r="3" fill="{c["pop"]}" opacity=".85"/>' for x, y in ((40, 820), (90, 760), (660, 800), (690, 880), (610, 740)))
    return (f'<rect width="{W}" height="{FLOOR}" fill="{c["dark"]}"/><rect width="{W}" height="{FLOOR}" fill="{c["wall"]}" opacity=".55"/>' + _bands(c, (c['dark'], c['primary'], c['pop']), (.25, .12, .18))
            + glow + dots + sparks + clouds + peaks + town + hills + trees + near + flies + ground + f'<path d="M0 {FLOOR + 2}H{W}" stroke="{c["dark"]}" stroke-width="4" opacity=".35"/>')


def _server_room(c):
    lines = ''.join(f'<path d="M{x} 0V{FLOOR}" stroke="{c["accent"]}" stroke-width="3" opacity=".2"/>' for x in range(40, W, 80))
    lights = ''.join(f'<circle cx="{x}" cy="{y}" r="4" fill="{c["pop"]}" opacity=".6"/>' for x in range(40, W, 80) for y in range(140, FLOOR - 100, 170))
    racks = ''.join(f'<rect x="{x}" y="{FLOOR - 560}" width="110" height="560" fill="{c["dark"]}" opacity=".45"/><rect x="{x - 4}" y="{FLOOR - 572}" width="118" height="12" fill="{c["metal"]}" opacity=".35"/>'
                    + ''.join(f'<rect x="{x + 10}" y="{y}" width="90" height="30" fill="{c["metal"]}" opacity=".35"/><circle cx="{x + 88}" cy="{y + 15}" r="4" fill="{c["accent"] if (x + y) % 3 else c["pop"]}"/>' for y in range(FLOOR - 540, FLOOR - 20, 46)) for x in range(10, W, 140))
    side = ''.join(f'<rect x="{x}" y="{FLOOR - 720}" width="90" height="720" fill="{c["dark"]}" opacity=".7"/><rect x="{x}" y="{FLOOR - 720}" width="90" height="6" fill="{c["metal"]}" opacity=".5"/>'
                   + ''.join(f'<rect x="{x + 10}" y="{y}" width="70" height="6" fill="{c["metal"]}" opacity=".25"/><rect x="{x + (14 if x < 0 else 62)}" y="{y + 1}" width="8" height="4" fill="{c["accent"] if (y // 40) % 3 else c["pop"]}" opacity=".9"/>' for y in range(FLOOR - 690, FLOOR - 20, 40)) for x in (-20, 650))
    px = lambda x, y: x + (x - 360) * (y - FLOOR) / 420
    rows = [FLOOR + round((H - FLOOR) * (i / 4) ** 1.3) for i in range(5)]
    floor = f'<rect y="{FLOOR}" width="{W}" height="{H - FLOOR}" fill="{c["floor"]}"/>' + ''.join(f'<path d="M{x} {FLOOR}L{px(x, H):.1f} {H}" stroke="{c["metal"]}" stroke-width="2.5" opacity=".3"/>' for x in range(-280, W + 300, 90)) + ''.join(f'<path d="M0 {y}H{W}" stroke="{c["metal"]}" stroke-width="2.5" opacity=".3"/>' for y in rows[1:-1])
    for r, (ya, yb) in enumerate(zip(rows, rows[1:])):
        for k, x in enumerate(range(-280, W + 300, 90)):
            if (r + k) % 2:continue
            for t in (.3, .5, .7):
                y = ya + (yb - ya) * t;floor += ''.join(f'<circle cx="{px(x + 90 * s, y):.1f}" cy="{y:.1f}" r="{1.5 + (y - FLOOR) / 120:.1f}" fill="{c["light"]}" opacity=".12"/>' for s in (.25, .5, .75))
    glow = f'<rect y="{FLOOR - 10}" width="{W}" height="10" fill="{c["accent"]}" opacity=".25"/><rect y="{FLOOR}" width="{W}" height="18" fill="{c["accent"]}" opacity=".08"/>'
    return (f'<rect width="{W}" height="{FLOOR}" fill="{c["dark"]}"/><rect width="{W}" height="{FLOOR}" fill="{c["wall"]}" opacity=".35"/>' + lines + lights + racks + side + _server_ceiling(c)
            + floor + glow + f'<path d="M0 {FLOOR + 2}H{W}" stroke="{c["dark"]}" stroke-width="4" opacity=".35"/>')


def _room_key(*parts):
    return hashlib.sha256(repr(parts).encode()).hexdigest()[:10]


def _room_persp(y, x0, vx=360, k0=.52):
    """Floor point: column x0 (its x at the bottom edge) at height y, converging towards the horizon at FLOOR."""
    return vx + (x0 - vx) * (k0 + (1 - k0) * (y - FLOOR) / (H - FLOOR))


def _room_floor_grid(c, fill, line, check=None, check_op=.2, line_op=.16, step=96, rows=6, k0=.52):
    """Perspective floor: columns converge towards the back wall, rows widen towards the viewer, optional checker."""
    ys = [FLOOR + (H - FLOOR) * (i / rows) ** 1.45 for i in range(rows + 1)];span = 360 / k0
    xs = [360 + d for d in range(-int(span // step + 1) * step, int(span) + step, step)];out = f'<rect y="{FLOOR}" width="{W}" height="{H - FLOOR}" fill="{fill}"/>'
    if check:
        for i in range(rows):
            for j in range(len(xs) - 1):
                if (i + j) % 2:
                    y0, y1, a, b = ys[i], ys[i + 1], xs[j], xs[j + 1]
                    out += f'<path d="M{_room_persp(y0, a, k0=k0):.1f} {y0:.1f}L{_room_persp(y0, b, k0=k0):.1f} {y0:.1f}L{_room_persp(y1, b, k0=k0):.1f} {y1:.1f}L{_room_persp(y1, a, k0=k0):.1f} {y1:.1f}Z" fill="{check}" opacity="{check_op}"/>'
    out += ''.join(f'<path d="M{_room_persp(FLOOR, x, k0=k0):.1f} {FLOOR}L{x} {H}" stroke="{line}" stroke-width="2.5" opacity="{line_op}"/>' for x in xs)
    return out + ''.join(f'<path d="M0 {y:.1f}H{W}" stroke="{line}" stroke-width="2.5" opacity="{line_op}"/>' for y in ys[1:-1])


def _room_planks(c, fill, line, step=72, rows=7):
    """Perspective floorboards with staggered butt joints."""
    out = _room_floor_grid(c, fill, line, None, 0, .2, step, 1)
    ys = [FLOOR + (H - FLOOR) * (i / rows) ** 1.35 for i in range(rows + 1)]
    for j, x in enumerate(range(360 - 10 * step, 360 + 10 * step, step)):
        for i in range(1, rows):
            if (i + j * 2) % 3 == 0:
                y = ys[i];out += f'<path d="M{_room_persp(y, x):.1f} {y:.1f}L{_room_persp(y, x + step):.1f} {y:.1f}" stroke="{line}" stroke-width="2" opacity=".18"/>'
    return out


def _room_floor_light(c, key, shade=.22, glow=.12):
    """Soft contact shadow where floor meets wall, lifting to a pale front edge."""
    k = _room_key('floor', key, c['dark'])
    return (f'<defs><linearGradient id="floor-light-{k}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c["dark"]}" stop-opacity="{shade}"/>'
            f'<stop offset=".35" stop-color="{c["dark"]}" stop-opacity="0"/><stop offset="1" stop-color="{c["light"]}" stop-opacity="{glow}"/></linearGradient></defs>'
            f'<rect y="{FLOOR}" width="{W}" height="{H - FLOOR}" fill="url(#floor-light-{k})"/>')


def _room_edges(c, key, op=.22, y1=H):
    """Paper vignette: the side edges fall off into shadow so the centre stays the brightest, calmest field."""
    k = _room_key('edge', key, c['dark'])
    return (f'<defs><linearGradient id="edge-{k}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{c["dark"]}" stop-opacity="{op}"/>'
            f'<stop offset=".2" stop-color="{c["dark"]}" stop-opacity="0"/><stop offset=".8" stop-color="{c["dark"]}" stop-opacity="0"/>'
            f'<stop offset="1" stop-color="{c["dark"]}" stop-opacity="{op}"/></linearGradient></defs><rect width="{W}" height="{y1}" fill="url(#edge-{k})"/>')


def _room_grain(c, seed, n=220, y0=0, y1=FLOOR, op=.08):
    """Paper fibre: fine light and dark flecks, too faint to read as pattern."""
    return ''.join(f'<rect x="{(k * 211 + seed * 37) % W}" y="{y0 + (k * 157 + seed * 53) % (y1 - y0)}" width="{2 + k % 3}" height="2" fill="{c["light"] if k % 2 else c["dark"]}" opacity="{op}"/>' for k in range(n))


def _room_shaft(c, x_top, w_top, x_bot, w_bot, y0=0, y1=FLOOR, op=.1, colour=None):
    return f'<path d="M{x_top} {y0}H{x_top + w_top}L{x_bot + w_bot} {y1}H{x_bot}Z" fill="{colour or c["light"]}" opacity="{op}"/>'


def _room_skirting(c, colour, h=26, op=1):
    """Skirting board: a cut-paper strip with a bevel highlight and a soft cast shadow on the floor."""
    return (f'<rect y="{FLOOR - h}" width="{W}" height="{h}" fill="{colour}" opacity="{op}"/><rect y="{FLOOR - h}" width="{W}" height="4" fill="{c["light"]}" opacity=".35"/>'
            f'<rect y="{FLOOR - h - 6}" width="{W}" height="6" fill="{c["dark"]}" opacity=".08"/><rect y="{FLOOR}" width="{W}" height="10" fill="{c["dark"]}" opacity=".16"/>')


def _living_room_trim(c):
    crown = (f'<rect width="{W}" height="54" fill="{c["light"]}" opacity=".5"/><rect y="54" width="{W}" height="8" fill="{c["dark"]}" opacity=".12"/>'
             + ''.join(f'<rect x="{x}" y="34" width="14" height="14" fill="{c["dark"]}" opacity=".1"/>' for x in range(8, W, 30)))
    dado = FLOOR - 170
    panels = ''.join(f'<rect x="{x + 10}" y="{dado + 34}" width="{100}" height="{106}" rx="4" fill="none" stroke="{c["dark"]}" stroke-width="3" opacity=".14"/>'
                     f'<path d="M{x + 12} {dado + 37}H{x + 108}" stroke="{c["light"]}" stroke-width="3" opacity=".3"/>' for x in range(0, W, 120))
    return crown, panels


def _arcade_marquee(c):
    soffit = f'<rect width="{W}" height="62" fill="{c["dark"]}" opacity=".55"/><rect y="62" width="{W}" height="6" fill="{c["primary"]}" opacity=".6"/>'
    return soffit + ''.join(f'<circle cx="{x}" cy="34" r="6" fill="{[c["secondary"], c["accent"], c["pop"]][(x // 36) % 3]}" opacity=".55"/><circle cx="{x}" cy="34" r="14" fill="{c["light"]}" opacity=".06"/>' for x in range(18, W, 36))


def _park_far(c):
    """Distant layers: pale ridge, a far treeline of lollipop trees and soft sun rays, all faded into the sky."""
    ridge = f'<path d="M0 {FLOOR - 330}Q90 {FLOOR - 410} 200 {FLOOR - 360}Q300 {FLOOR - 450} 430 {FLOOR - 370}Q560 {FLOOR - 430} 720 {FLOOR - 360}V{FLOOR}H0Z" fill="{c["secondary"]}" opacity=".22"/>'
    line = ''.join(f'<rect x="{x - 2}" y="{FLOOR - 312 - (x * 11) % 30}" width="4" height="22" fill="{c["floor"]}" opacity=".3"/><circle cx="{x}" cy="{FLOOR - 320 - (x * 11) % 30}" r="{12 + (x * 5) % 8}" fill="{c["floor"]}" opacity=".3"/>' for x in range(14, W, 34))
    rays = ''.join(_room_shaft(c, x, 70, x - 260, 150, 0, FLOOR - 300, .08) for x in (430, 600, 760))
    birds = ''.join(f'<path d="M{x} {y}q8 -8 16 0q8 -8 16 0" fill="none" stroke="{c["dark"]}" stroke-width="2.5" opacity=".3"/>' for x, y in ((40, 110), (78, 96), (612, 120), (650, 140)))
    return rays + ridge + line + birds


def _beach_sea(c, sea_y):
    """Sea in depth: paler bands at the horizon, a far headland, glitter under the sun, foam scallops at the shore."""
    bands = ''.join(f'<rect y="{sea_y + y}" width="{W}" height="{h}" fill="{c["light"]}" opacity="{op}"/>' for y, h, op in ((0, 26, .3), (26, 30, .18), (56, 40, .09)))
    land = (f'<path d="M430 {sea_y + 2}Q500 {sea_y - 46} 560 {sea_y - 30}Q640 {sea_y - 70} 720 {sea_y - 40}V{sea_y + 2}Z" fill="{c["floor"]}" opacity=".35"/>'
            f'<path d="M0 {sea_y + 2}V{sea_y - 26}Q50 {sea_y - 40} 110 {sea_y + 2}Z" fill="{c["floor"]}" opacity=".3"/>')
    glitter = ''.join(f'<rect x="{160 - w / 2 + (k * 29) % 30 - 15:.0f}" y="{sea_y + 24 + k * 22}" width="{w:.0f}" height="4" rx="2" fill="{c["secondary"]}" opacity=".35"/>' for k, w in enumerate((60, 50, 70, 40, 56, 34, 48)))
    return bands + land + glitter


def _rooftop_far(c):
    """Far skyline: paler, shorter blocks with water tanks and masts, sunk in haze behind the near towers."""
    blocks = ((0, 80, 300), (70, 70, 360), (150, 100, 330), (260, 60, 400), (330, 90, 350), (430, 70, 420), (510, 110, 320), (610, 70, 390), (670, 60, 340))
    out = ''.join(f'<rect x="{x}" y="{FLOOR - h - 120}" width="{w}" height="{h}" fill="{c["metal"]}" opacity=".25"/>' for x, w, h in blocks)
    out += ''.join(f'<path d="M{x + w / 2} {FLOOR - h - 120}V{FLOOR - h - 170}" stroke="{c["metal"]}" stroke-width="4" opacity=".3"/>' for x, w, h in blocks[1::3])
    out += ''.join(f'<rect x="{x + 14}" y="{FLOOR - h - 150}" width="26" height="24" rx="4" fill="{c["metal"]}" opacity=".28"/><path d="M{x + 18} {FLOOR - h - 126}V{FLOOR - h - 120}M{x + 36} {FLOOR - h - 126}V{FLOOR - h - 120}" stroke="{c["metal"]}" stroke-width="3" opacity=".28"/>' for x, w, h in blocks[2::3])
    haze = f'<rect y="{FLOOR - 520}" width="{W}" height="520" fill="{c["light"]}" opacity=".12"/>'
    streaks = ''.join(f'<rect x="{x}" y="{y}" width="{w}" height="6" rx="3" fill="{c["light"]}" opacity=".2"/>' for x, y, w in ((-20, 120, 220), (520, 90, 240), (40, 190, 140), (560, 170, 180)))
    return streaks + out + haze


def _bakery_tiles(c, y0, y1, w=60, h=30, op=.12):
    """Subway tiles on the lower wall: staggered bricks drawn as thin grout lines."""
    rows = ''.join(f'<path d="M0 {y}H{W}" stroke="{c["light"]}" stroke-width="3" opacity="{op * 2.5}"/>' for y in range(y0 + h, y1, h))
    joints = ''.join(f'<path d="M{x + (w // 2 if k % 2 else 0)} {y0 + k * h}v{h}" stroke="{c["light"]}" stroke-width="3" opacity="{op * 2.5}"/>' for k in range((y1 - y0) // h) for x in range(0, W + w, w))
    return f'<rect y="{y0}" width="{W}" height="{y1 - y0}" fill="{c["light"]}" opacity="{op}"/>' + rows + joints


def _living_room(c):
    crown, panels = _living_room_trim(c)
    rail = ''.join(f'<rect x="{x}" y="250" width="{70 + (x * 7) % 50}" height="{60 + (x * 3) % 40}" fill="{c["light"]}" stroke="{c["dark"]}" stroke-width="3" opacity=".55"/>'
                   f'<rect x="{x + 6}" y="{256}" width="{70 + (x * 7) % 50}" height="{60 + (x * 3) % 40}" fill="{c["dark"]}" opacity=".07"/>' for x in range(10, W, 130))
    picture_rail = f'<rect y="226" width="{W}" height="10" fill="{c["primary"]}" opacity=".45"/><rect y="236" width="{W}" height="4" fill="{c["dark"]}" opacity=".1"/>'
    floor = _room_planks(c, c['floor'], c['dark']) + _room_floor_light(c, 'living') + f'<path d="M120 {FLOOR}H420L620 {H}H200Z" fill="{c["light"]}" opacity=".05"/>'
    rug = (f'<ellipse cx="360" cy="{FLOOR + 78}" rx="318" ry="54" fill="{c["dark"]}" opacity=".12"/><ellipse cx="360" cy="{FLOOR + 70}" rx="300" ry="46" fill="{c["pop"]}" opacity=".55"/>'
           f'<ellipse cx="360" cy="{FLOOR + 70}" rx="262" ry="34" fill="none" stroke="{c["light"]}" stroke-width="4" stroke-dasharray="14 10" opacity=".35"/>')
    return (f'<rect width="{W}" height="{FLOOR}" fill="{c["wall"]}"/>' + _diamonds(c, c['light'], 34, .3, FLOOR - 170) + _room_grain(c, 1) + crown + picture_rail + rail
            + _bands(c, (c['dark'], c['wall'], c['light']), (.1, 0, .08)) + _room_shaft(c, 0, 150, 120, 300, 140, FLOOR, .07)
            + f'<rect y="{FLOOR - 170}" width="{W}" height="170" fill="{c["secondary"]}" opacity=".45"/><rect y="{FLOOR - 176}" width="{W}" height="16" fill="{c["primary"]}" opacity=".7"/><rect y="{FLOOR - 160}" width="{W}" height="5" fill="{c["dark"]}" opacity=".12"/>'
            + panels + _room_skirting(c, c['primary'], 24, .75) + floor + rug + _room_edges(c, 'living', .1)
            + f'<path d="M0 {FLOOR + 2}H{W}" stroke="{c["dark"]}" stroke-width="4" opacity=".3"/>')



def _arcade(c):
    cols = ((60, c['primary']), (240, c['secondary']), (480, c['accent']), (660, c['primary']))
    tubes = ''.join(f'<path d="M{x} 120V{FLOOR - 260}" stroke="{col}" stroke-width="10" stroke-linecap="round" opacity=".85"/><path d="M{x} 120V{FLOOR - 260}" stroke="{col}" stroke-width="34" stroke-linecap="round" opacity=".14"/>'
                    f'<rect x="{x - 9}" y="108" width="18" height="14" rx="3" fill="{c["metal"]}" opacity=".7"/><rect x="{x - 9}" y="{FLOOR - 266}" width="18" height="14" rx="3" fill="{c["metal"]}" opacity=".7"/>' for x, col in cols)
    pools = ''.join(f'<ellipse cx="{x}" cy="{FLOOR - 240}" rx="70" ry="16" fill="{col}" opacity=".12"/>' for x, col in cols)
    zig = f'<path d="M0 {FLOOR - 200}' + ''.join(f'L{x} {FLOOR - 200 - (40 if (x // 60) % 2 else 0)}' for x in range(60, W + 60, 60)) + f'" fill="none" stroke="{c["pop"]}" stroke-width="8" opacity=".7"/>'
    wainscot = (f'<rect y="{FLOOR - 170}" width="{W}" height="170" fill="{c["dark"]}" opacity=".3"/><rect y="{FLOOR - 176}" width="{W}" height="8" fill="{c["metal"]}" opacity=".45"/>'
                + ''.join(f'<rect x="{x + 8}" y="{FLOOR - 150}" width="74" height="112" rx="6" fill="none" stroke="{c["metal"]}" stroke-width="3" opacity=".2"/>' for x in range(0, W, 90)))
    reflect = ''.join(f'<path d="M{_room_persp(FLOOR, x) - 10:.1f} {FLOOR}H{_room_persp(FLOOR, x) + 10:.1f}L{x + 24} {H}H{x - 24}Z" fill="{col}" opacity=".1"/>' for x, col in cols)
    floor = (_room_floor_grid(c, c['floor'], c['secondary'], c['secondary'], .2, .22, 90, 6) + reflect + _room_floor_light(c, 'arcade', .3, .06)
             + f'<path d="M0 {FLOOR + 2}H{W}" stroke="{c["primary"]}" stroke-width="5" opacity=".7"/>')
    stars = ''.join(f'<circle cx="{(k * 173) % W}" cy="{90 + (k * 97) % (FLOOR - 300)}" r="{1.5 + k % 2}" fill="{c["light"]}" opacity=".18"/>' for k in range(60))
    return (f'<rect width="{W}" height="{FLOOR}" fill="{c["dark"]}"/><rect width="{W}" height="{FLOOR}" fill="{c["wall"]}" opacity=".6"/>' + _diamonds(c, c['dark'], 80, .25)
            + _room_grain(c, 2, 160) + stars + pools + tubes + zig + wainscot + _arcade_marquee(c) + _room_skirting(c, c['dark'], 18, .6) + floor + _room_edges(c, 'arcade', .16))


def _park(c):
    sky = f'<rect width="{W}" height="{FLOOR}" fill="{c["wall"]}"/>' + _bands(c, (c['light'], c['wall'], c['secondary']), (.35, 0, .3)) + _room_grain(c, 3, 140, 0, FLOOR - 300, .06)
    hills = (f'<path d="M0 {FLOOR - 260}Q180 {FLOOR - 380} 380 {FLOOR - 270}Q560 {FLOOR - 180} 720 {FLOOR - 300}V{FLOOR}H0Z" fill="{c["floor"]}" opacity=".45"/>'
             f'<path d="M0 {FLOOR - 120}Q240 {FLOOR - 210} 460 {FLOOR - 120}Q600 {FLOOR - 70} 720 {FLOOR - 130}V{FLOOR}H0Z" fill="{c["floor"]}" opacity=".75"/>')
    hill_rows = ''.join(f'<path d="M0 {FLOOR - 230 + k * 40}Q200 {FLOOR - 300 + k * 40} 380 {FLOOR - 236 + k * 40}Q560 {FLOOR - 170 + k * 40} 720 {FLOOR - 262 + k * 40}" fill="none" stroke="{c["light"]}" stroke-width="3" opacity=".14"/>' for k in range(3))
    trees = ''.join(f'<g opacity=".7">{place(PROPS["tree"].render(c), x, FLOOR - 90 - (x * 7) % 50, .45)}</g>' for x in (40, 200, 560, 690))
    path_ = (f'<path d="M300 {FLOOR}Q340 {FLOOR + 120} 260 {H}H460Q420 {FLOOR + 120} 420 {FLOOR}Z" fill="{c["secondary"]}" opacity=".7"/>'
             f'<path d="M300 {FLOOR}Q340 {FLOOR + 120} 260 {H}" fill="none" stroke="{c["dark"]}" stroke-width="3" opacity=".12"/><path d="M420 {FLOOR}Q420 {FLOOR + 120} 460 {H}" fill="none" stroke="{c["dark"]}" stroke-width="3" opacity=".12"/>'
             + ''.join(f'<ellipse cx="{360 + (k * 37) % 50 - 25}" cy="{y}" rx="{8 + (y - FLOOR) * .06:.1f}" ry="{3 + (y - FLOOR) * .02:.1f}" fill="{c["dark"]}" opacity=".1"/>' for k, y in enumerate(range(FLOOR + 30, H, 40))))
    clouds = ''.join(f'<g opacity=".8">{place(PROPS["cloud"].render(c), x, y, s)}</g>' for x, y, s in ((140, 300, .8), (520, 230, 1.0), (330, 470, .6), (650, 520, .55), (60, 560, .5)))
    kites = ''.join(f'<path d="M{x} {y}l26 -40l26 40l-26 30Z" fill="{col}" stroke="{c["dark"]}" stroke-width="3"/><path d="M{x + 26} {y + 30}q-20 40 10 80q-30 40 0 90" fill="none" stroke="{c["dark"]}" stroke-width="2" opacity=".5"/>' for x, y, col in ((470, 380, c['pop']), (200, 420, c['accent'])))
    fence = (''.join(f'<path d="M{x} {FLOOR - 10}V{FLOOR - 120}l12 -16l12 16V{FLOOR - 10}Z" fill="{c["light"]}" opacity=".75"/><path d="M{x + 20} {FLOOR - 118}V{FLOOR - 10}" stroke="{c["dark"]}" stroke-width="3" opacity=".08"/>' for x in range(0, W, 40))
             + f'<rect y="{FLOOR - 90}" width="{W}" height="12" fill="{c["light"]}" opacity=".75"/><rect y="{FLOOR - 78}" width="{W}" height="5" fill="{c["dark"]}" opacity=".08"/><rect y="{FLOOR - 10}" width="{W}" height="10" fill="{c["dark"]}" opacity=".1"/>')
    bushes = ''.join(f'<circle cx="{x}" cy="{FLOOR - 40}" r="{r}" fill="{c["floor"]}" stroke="{c["dark"]}" stroke-width="3" opacity=".95"/><circle cx="{x - r * .3:.0f}" cy="{FLOOR - 40 - r * .35:.0f}" r="{r * .45:.0f}" fill="{c["light"]}" opacity=".1"/>' for x, r in ((30, 70), (110, 50), (620, 64), (700, 54)))
    trees = trees + ''.join(f'<g opacity=".55">{place(PROPS["tree"].render(c), x, FLOOR - 230, .3)}</g>' for x in (120, 300, 420, 620))
    stripes = ''.join(f'<path d="M{_room_persp(FLOOR, x, k0=.4):.1f} {FLOOR}L{_room_persp(FLOOR, x + 70, k0=.4):.1f} {FLOOR}L{x + 70} {H}H{x}Z" fill="{c["light"]}" opacity=".045"/>' for x in range(-460, 1200, 140))
    flowers = ''.join(f'<circle cx="{x}" cy="{y}" r="5" fill="{col}" opacity=".55"/><circle cx="{x}" cy="{y}" r="2" fill="{c["light"]}" opacity=".7"/>'
                      for x, y, col in ((30, 1150, c['pop']), (62, 1186, c['secondary']), (20, 1232, c['accent']), (90, 1250, c['pop']), (660, 1160, c['accent']), (694, 1200, c['pop']), (640, 1244, c['secondary'])))
    grass = (f'<rect y="{FLOOR}" width="{W}" height="{H - FLOOR}" fill="{c["floor"]}"/>' + stripes + _room_floor_light(c, 'park', .18, .08)
             + ''.join(f'<path d="M{x} {y}l6 -16l6 16" fill="none" stroke="{c["light"]}" stroke-width="3" opacity=".3"/>' for x, y in [((k * 53) % W, FLOOR + 30 + (k * 37) % 200) for k in range(40)]))
    return sky + _park_far(c) + clouds + kites + hills + hill_rows + trees + fence + bushes + grass + path_ + flowers + _room_edges(c, 'park', .08) + f'<path d="M0 {FLOOR + 2}H{W}" stroke="{c["dark"]}" stroke-width="4" opacity=".2"/>'


def _beach(c):
    sky = f'<rect width="{W}" height="{FLOOR}" fill="{c["wall"]}"/>' + _bands(c, (c['light'], c['wall'], c['pop']), (.3, 0, .25)) + _room_grain(c, 4, 120, 0, 600, .06)
    sea_y = FLOOR - 330
    haze = f'<rect y="{sea_y - 60}" width="{W}" height="60" fill="{c["light"]}" opacity=".16"/><rect y="{sea_y - 26}" width="{W}" height="26" fill="{c["light"]}" opacity=".14"/>'
    rays = ''.join(f'<path d="M160 {sea_y - 10}L{x} 0H{x + 70}Z" fill="{c["light"]}" opacity=".06"/>' for x in (-60, 120, 300))
    sea = f'<rect y="{sea_y}" width="{W}" height="{FLOOR - sea_y}" fill="{c["accent"]}"/>' + ''.join(f'<path d="M{x} {y}q20 -12 40 0t40 0" fill="none" stroke="{c["light"]}" stroke-width="5" opacity=".55"/>' for x, y in [((k * 97) % 680, sea_y + 40 + (k * 61) % 240) for k in range(16)])
    sun = f'<circle cx="160" cy="{sea_y - 10}" r="130" fill="{c["secondary"]}" opacity=".14"/><circle cx="160" cy="{sea_y - 10}" r="90" fill="{c["secondary"]}" opacity=".9"/><rect y="{sea_y}" width="{W}" height="20" fill="{c["accent"]}"/>'
    shore = f'M0 {FLOOR - 80}Q360 {FLOOR - 140} 720 {FLOOR - 60}'
    foam = (f'<path d="M0 {FLOOR - 94}Q360 {FLOOR - 156} 720 {FLOOR - 74}V{FLOOR - 60}Q360 {FLOOR - 140} 0 {FLOOR - 80}Z" fill="{c["light"]}" opacity=".55"/>'
            f'<path d="M0 {FLOOR - 104}Q360 {FLOOR - 166} 720 {FLOOR - 84}" fill="none" stroke="{c["light"]}" stroke-width="3" stroke-dasharray="18 12" opacity=".4"/>')
    sand = (f'<path d="{shore}V{H}H0Z" fill="{c["secondary"]}"/><path d="{shore}V{FLOOR - 36}Q360 {FLOOR - 100} 0 {FLOOR - 50}Z" fill="{c["dark"]}" opacity=".1"/>'
            + ''.join(f'<path d="M{x} {y}q{w / 2:.0f} -{w / 9:.0f} {w} 0" fill="none" stroke="{c["dark"]}" stroke-width="2.5" opacity=".1"/>' for x, y, w in [((k * 131) % 640, FLOOR + 30 + (k * 47) % 210, 40 + (k * 17) % 60) for k in range(22)])
            + ''.join(f'<circle cx="{(k * 71) % W}" cy="{FLOOR + 20 + (k * 43) % 200}" r="3" fill="{c["dark"]}" opacity=".15"/>' for k in range(50))
            + _room_floor_light(c, 'beach', .06, .14))
    clouds = ''.join(f'<g opacity=".85">{place(PROPS["cloud"].render(c), x, y, s)}</g>' for x, y, s in ((470, 260, 1.0), (180, 380, .7), (620, 470, .6), (330, 520, .5)))
    birds = ''.join(f'<path d="M{x} {y}q14 -14 28 0q14 -14 28 0" fill="none" stroke="{c["dark"]}" stroke-width="4" opacity=".6"/>' for x, y in ((300, 330), (380, 290), (560, 380), (120, 250)))
    boats = ''.join(f'<path d="M{x} {sea_y + 70}h70l-12 18h-46Z" fill="{c["light"]}"/><path d="M{x + 34} {sea_y + 66}V{sea_y - 10}L{x + 70} {sea_y + 60}Z" fill="{col}"/><path d="M{x + 4} {sea_y + 94}h62" stroke="{c["dark"]}" stroke-width="3" opacity=".12"/>' for x, col in ((420, c['pop']), (560, c['primary'])))
    huts = ''.join(f'<rect x="{x + 6}" y="{FLOOR - 100}" width="88" height="14" fill="{c["dark"]}" opacity=".12"/><rect x="{x}" y="{FLOOR - 230}" width="80" height="130" fill="{col}" stroke="{c["dark"]}" stroke-width="3"/><path d="M{x - 10} {FLOOR - 230}L{x + 40} {FLOOR - 280}L{x + 90} {FLOOR - 230}Z" fill="{c["light"]}" stroke="{c["dark"]}" stroke-width="3"/>'
                   + ''.join(f'<rect x="{x + k}" y="{FLOOR - 230}" width="10" height="130" fill="{c["light"]}" opacity=".5"/>' for k in (14, 44)) for x, col in ((20, c['pop']), (120, c['primary']), (610, c['pop'])))
    return sky + rays + clouds + birds + haze + sun + sea + _beach_sea(c, sea_y) + boats + sand + foam + huts + _room_edges(c, 'beach', .07) + f'<path d="M0 {FLOOR + 2}H{W}" stroke="{c["dark"]}" stroke-width="3" opacity=".12"/>'


def _rooftop(c):
    sky = f'<rect width="{W}" height="{FLOOR}" fill="{c["wall"]}"/>' + _bands(c, (c['pop'], c['wall'], c['light']), (.25, 0, .35)) + _room_grain(c, 5, 120, 0, 500, .06)
    towers = ((0, 120, 420), (130, 90, 560), (230, 140, 380), (380, 100, 620), (490, 130, 460), (630, 90, 520))
    city = ''.join(f'<rect x="{x}" y="{FLOOR - h}" width="{w}" height="{h}" fill="{c["metal"]}" opacity=".55"/><rect x="{x}" y="{FLOOR - h}" width="{w}" height="10" fill="{c["light"]}" opacity=".18"/><rect x="{x + w - 14}" y="{FLOOR - h}" width="14" height="{h}" fill="{c["dark"]}" opacity=".08"/>'
                   + ''.join(f'<rect x="{x + 12 + i * 22}" y="{FLOOR - h + 20 + j * 34}" width="10" height="16" fill="{c["light"]}" opacity=".45"/>' for i in range(max(1, (w - 20) // 22)) for j in range(max(1, (h - 40) // 34)) if (i + j + x) % 3)
                   for x, w, h in towers)
    parapet = (f'<rect y="{FLOOR - 70}" width="{W}" height="70" fill="{c["primary"]}"/><rect y="{FLOOR - 80}" width="{W}" height="14" fill="{c["light"]}" opacity=".6"/><rect y="{FLOOR - 66}" width="{W}" height="6" fill="{c["dark"]}" opacity=".12"/>'
               + ''.join(f'<path d="M{x} {FLOOR - 66}V{FLOOR}" stroke="{c["dark"]}" stroke-width="3" opacity=".2"/>' for x in range(40, W, 80))
               + ''.join(f'<path d="M0 {y}H{W}" stroke="{c["dark"]}" stroke-width="2" opacity=".1"/>' for y in (FLOOR - 44, FLOOR - 22))
               + ''.join(f'<path d="M{x + (20 if k % 2 else 0)} {FLOOR - 66 + k * 22}v22" stroke="{c["dark"]}" stroke-width="2" opacity=".1"/>' for k in range(3) for x in range(0, W, 40))
               + ''.join(f'<rect x="{x}" y="{FLOOR - 84}" width="28" height="6" fill="{c["dark"]}" opacity=".1"/>' for x in range(26, W, 80)))
    floor = (_room_floor_grid(c, c['floor'], c['dark'], c['light'], .1, .14, 120, 5) + _room_floor_light(c, 'rooftop', .3, .08)
             + ''.join(f'<rect x="{_room_persp(FLOOR + 140, x) - 12:.0f}" y="{FLOOR + 136}" width="24" height="8" rx="3" fill="{c["dark"]}" opacity=".14"/>' for x in (60, 660))
             + f'<path d="M0 {FLOOR + 2}H{W}" stroke="{c["dark"]}" stroke-width="4" opacity=".35"/>')
    return sky + _rooftop_far(c) + city + parapet + floor + _room_edges(c, 'rooftop', .1)


def _bakery(c):
    awning = (f'<rect y="0" width="{W}" height="176" fill="{c["dark"]}" opacity=".04"/>'
              + ''.join(f'<path d="M{x} 0H{x + 60}V140Q{x + 30} 176 {x} 140Z" fill="{c["primary"] if (x // 60) % 2 else c["light"]}"/><path d="M{x} 140Q{x + 30} 176 {x + 60} 140" fill="none" stroke="{c["dark"]}" stroke-width="2" opacity=".12"/>' for x in range(0, W, 60))
              + f'<rect y="0" width="{W}" height="16" fill="{c["dark"]}" opacity=".18"/>' + ''.join(f'<path d="M{x} 16V140" stroke="{c["dark"]}" stroke-width="2" opacity=".08"/>' for x in range(30, W, 60)))
    shelves = ''.join(f'<rect x="44" y="{y + 16}" width="640" height="8" fill="{c["dark"]}" opacity=".1"/><rect x="40" y="{y}" width="640" height="16" fill="{c["secondary"]}" opacity=".85"/><rect x="40" y="{y}" width="640" height="4" fill="{c["light"]}" opacity=".3"/>'
                      + ''.join(f'<path d="M{x} {y + 16}v20h18" fill="none" stroke="{c["dark"]}" stroke-width="4" opacity=".18"/>' for x in (64, 640))
                      + ''.join(f'<circle cx="{x}" cy="{y - 24}" r="22" fill="{[c["pop"], c["accent"], c["primary"]][(x // 90) % 3]}" opacity=".75"/><path d="M{x - 10} {y - 30}q10 -8 20 0" fill="none" stroke="{c["light"]}" stroke-width="3" opacity=".35"/>' for x in range(90, 680, 90)) for y in (330, 470))
    counter_y = FLOOR - 230
    counter = (f'<rect y="{counter_y}" width="{W}" height="230" fill="{c["secondary"]}" opacity=".6"/>' + _bakery_tiles(c, counter_y + 22, FLOOR - 26)
               + f'<rect y="{counter_y - 6}" width="{W}" height="16" fill="{c["primary"]}" opacity=".55"/><rect y="{counter_y + 10}" width="{W}" height="6" fill="{c["dark"]}" opacity=".1"/>')
    window_glow = _room_shaft(c, 520, 200, 320, 300, 160, FLOOR, .09) + _room_shaft(c, -40, 120, -160, 220, 160, FLOOR, .07)
    floor = _room_floor_grid(c, c['floor'], c['dark'], c['light'], .2, .1, 80, 6) + _room_floor_light(c, 'bakery', .24, .1)
    return (f'<rect width="{W}" height="{FLOOR}" fill="{c["wall"]}"/>' + _diamonds(c, c['light'], 40, .35) + _room_grain(c, 6, 160) + window_glow + shelves + awning + counter
            + _room_skirting(c, c['primary'], 26, .8) + floor + _room_edges(c, 'bakery', .09) + f'<path d="M0 {FLOOR + 2}H{W}" stroke="{c["dark"]}" stroke-width="4" opacity=".35"/>')


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
            'bot': {'x': round(bx, 2), 'y': round(by, 2), 'scale': round(bscale, 4), 'costume': costume, 'role': rig.bot_slot.get('role', ''), 'side': side,
                    # Squeezed onto a wide machine: Bot peeks from behind it so the machine's labels stay readable.
                    'behind': min(bx + half, hero_box[0] + hero_box[2]) - max(bx - half, hero_box[0]) > BOT_BEHIND * 2 * half},
            'dressing': placed, 'lights': ROOMS[room]['lights'], 'bands': {'headline': list(HEADLINE), 'caption': list(CAPTION)}}


def compose(layout, pose=None, face='happy', bot_pose='standing'):
    """World markup for a solved layout at one rig pose."""
    c = get_palette(layout['palette']);room = ROOMS[layout['room']];rig = get_rig(layout['hero']['rig'])
    out = [room['draw'](c)]
    for item in layout['dressing']:
        if item['layer'] == 'back':out.append(place(PROPS[item['prop']].render(c), item['x'], item['y'], item['scale']))
    h = layout['hero'];out.append(place(rig.render(h.get('values') or None, pose, layout['palette']), h['x'], h['y'], h['scale']))
    b = layout['bot']
    if b and b.get('behind'):out.insert(len(out) - 1, dressed_bot(b['x'], b['y'], b['scale'], face=face, pose=bot_pose, costume=b['costume'], palette=layout['palette']))
    elif b:out.append(dressed_bot(b['x'], b['y'], b['scale'], face=face, pose=bot_pose, costume=b['costume'], palette=layout['palette']))
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
