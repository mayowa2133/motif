"""Motif's original set-dressing props, authored as cut-paper SVG.

Every prop is drawn here from simple shapes in palette roles (motif_rigs.palettes),
so each one renders in all eight palettes and the provenance origin is
motif-authored-svg. Nothing is traced or sampled from any reference.

A prop's local origin is the bottom centre of its footprint; its box is
(-w/2, -h, w, h). `mount` says where the set solver may put it:

  floor    stands on the floor line
  wall     hangs on the back wall, inside the focal band
  ceiling  hangs from the top edge
  sky      floats in the upper frame (outdoor rooms)
"""
import math
from dataclasses import dataclass

from motif_rigs.palettes import palette as get_palette


def P(d, fill, c, edge=True, extra=''):
    """A cut-paper piece: soft offset shadow, the piece, a thin ink edge."""
    shadow = f'<path d="{d}" fill="{c["dark"]}" opacity=".16" transform="translate(5 7)"/>' if edge else ''
    stroke = f' stroke="{c["dark"]}" stroke-width="3" stroke-linejoin="round"' if edge else ''
    return f'{shadow}<path d="{d}" fill="{fill}"{stroke} {extra}/>'


def L(d, color, w=4, extra=''):
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round" {extra}/>'


def R(x, y, w, h, fill, c, r=6, edge=True):
    return P(f'M{x + r} {y}H{x + w - r}Q{x + w} {y} {x + w} {y + r}V{y + h - r}Q{x + w} {y + h} {x + w - r} {y + h}H{x + r}Q{x} {y + h} {x} {y + h - r}V{y + r}Q{x} {y} {x + r} {y}Z', fill, c, edge)


def O(cx, cy, r, fill, c, edge=True):
    stroke = f' stroke="{c["dark"]}" stroke-width="3"' if edge else ''
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"{stroke}/>'


@dataclass(frozen=True)
class Prop:
    name: str
    w: float
    h: float
    mount: str
    tags: tuple
    draw: object

    def render(self, palette='sunrise'):
        c = get_palette(palette) if isinstance(palette, str) else palette
        return self.draw(self, c)

    @property
    def box(self):
        return (-self.w / 2, -self.h, self.w, self.h)


PROPS = {}


def prop(name, w, h, mount, tags):
    def wrap(fn):
        PROPS[name] = Prop(name, w, h, mount, tuple(tags), fn);return fn
    return wrap


# Floor props ----------------------------------------------------------------

@prop('plant', 130, 230, 'floor', ('home', 'office', 'calm', 'growth'))
def _(p, c):
    body = P('M-42 -84L-30 0H30L42 -84Z', c['primary'], c) + R(-50, -100, 100, 20, c['secondary'], c, 4)
    for k, (dx, a) in enumerate(((-34, -32), (-10, -8), (16, 14), (36, 36), (2, 0))):
        tip_y = -230 + abs(dx) * 1.4 + k * 6
        body += P(f'M0 -96Q{dx - 30} {(tip_y - 96) / 2} {dx} {tip_y}Q{dx + 26} {(tip_y - 96) / 2} 0 -96Z', c['secondary'] if k % 2 else '#3FA45B', c)
    return body


@prop('floor-lamp', 120, 360, 'floor', ('home', 'cosy', 'light'))
def _(p, c):
    return R(-44, -14, 88, 14, c['dark'], c, 5) + L('M0 -14V-280', c['metal'], 9) + P('M-56 -270L-34 -350H34L56 -270Z', c['secondary'], c) + f'<ellipse cx="0" cy="-268" rx="50" ry="10" fill="{c["light"]}" opacity=".7"/>'


@prop('stool', 110, 170, 'floor', ('diner', 'workshop', 'studio'))
def _(p, c):
    return L('M-36 0L-24 -140M36 0L24 -140M-30 -60H30', c['metal'], 8) + R(-52, -170, 104, 30, c['primary'], c, 14)


@prop('crate', 150, 130, 'floor', ('workshop', 'street', 'shipping', 'storage'))
def _(p, c):
    return R(-75, -130, 150, 130, c['secondary'], c, 4) + L('M-75 -65H75M-75 -130L75 0', c['dark'], 4, 'opacity=".45"') + R(-30, -84, 60, 26, c['light'], c, 3, False)


@prop('toolbox', 170, 110, 'floor', ('workshop', 'repair', 'build'))
def _(p, c):
    return L('M-46 -96V-132H46V-96', c['dark'], 8) + R(-85, -100, 170, 100, c['pop'], c, 8) + L('M-85 -64H85', c['dark'], 4) + R(-14, -72, 28, 16, c['metal'], c, 3)


@prop('ladder', 140, 420, 'floor', ('workshop', 'build', 'growth', 'climb'))
def _(p, c):
    rungs = ''.join(f'M{-50 + 6 * k * .2} {-40 - k * 64}H{50 - 6 * k * .2}' for k in range(6))
    return L('M-62 0L-38 -420M62 0L38 -420', c['secondary'], 12) + L(rungs, c['secondary'], 9)


@prop('traffic-cone', 110, 150, 'floor', ('street', 'warning', 'block', 'construction'))
def _(p, c):
    return R(-55, -14, 110, 14, c['dark'], c, 4) + P('M-42 -14L-12 -150H12L42 -14Z', c['pop'], c) + L('M-30 -56H30M-20 -100H20', c['light'], 12)


@prop('street-lamp', 120, 620, 'floor', ('street', 'night', 'city'))
def _(p, c):
    return R(-30, -30, 60, 30, c['dark'], c, 6) + L('M0 -30V-560Q0 -600 50 -600', c['metal'], 12) + P('M30 -602H90L80 -570H40Z', c['dark'], c) + f'<ellipse cx="60" cy="-566" rx="22" ry="8" fill="{c["secondary"]}"/>'


@prop('bench', 300, 150, 'floor', ('street', 'park', 'wait'))
def _(p, c):
    return L('M-120 0V-70M120 0V-70', c['dark'], 10) + R(-150, -84, 300, 22, c['primary'], c, 5) + R(-150, -150, 300, 22, c['primary'], c, 5) + L('M-110 -128V-84M110 -128V-84', c['dark'], 8)


@prop('mic-stand', 90, 330, 'floor', ('stage', 'studio', 'voice', 'talk'))
def _(p, c):
    return L('M-40 0L0 -24L40 0M0 -24V-250L40 -290', c['dark'], 8) + R(26, -340, 34, 58, c['metal'], c, 16)


@prop('server-rack', 170, 470, 'floor', ('server', 'cloud', 'data', 'compute', 'ai'))
def _(p, c):
    body = R(-85, -470, 170, 470, c['dark'], c, 8)
    for k in range(7):
        y = -440 + k * 62;body += R(-70, y, 140, 46, c['secondary'] if k % 3 else c['primary'], c, 4, False) + O(48, y + 23, 6, c['pop'] if k % 2 else c['accent'], c, False) + L(f'M-56 {y + 23}H10', c['dark'], 4, 'opacity=".5"')
    return body


@prop('sofa', 380, 200, 'floor', ('home', 'living', 'relax', 'streaming'))
def _(p, c):
    return R(-190, -150, 380, 110, c['primary'], c, 30) + R(-160, -96, 150, 60, c['secondary'], c, 14) + R(10, -96, 150, 60, c['secondary'], c, 14) + R(-200, -120, 50, 100, c['primary'], c, 18) + R(150, -120, 50, 100, c['primary'], c, 18) + L('M-160 -20V0M160 -20V0', c['dark'], 10)


@prop('bookshelf', 220, 440, 'floor', ('home', 'office', 'library', 'learn', 'research'))
def _(p, c):
    body = R(-110, -440, 220, 440, c['secondary'], c, 6)
    colours = (c['primary'], c['accent'], c['pop'], c['light'], c['metal'])
    for row in range(4):
        y = -420 + row * 104;body += L(f'M-100 {y + 94}H100', c['dark'], 5);x = -94
        for k in range(6 + row % 2):
            bw = 18 + (k * 7 + row * 5) % 12;bh = 64 + (k * 13 + row * 3) % 24
            body += R(x, y + 92 - bh, bw, bh, colours[(k + row) % 5], c, 2, False);x += bw + 4
            if x > 80:break
    return body


@prop('fridge', 190, 420, 'floor', ('kitchen', 'diner', 'home', 'food'))
def _(p, c):
    return R(-95, -420, 190, 420, c['light'], c, 22) + L('M-95 -280H95', c['dark'], 4) + L('M64 -380V-310M64 -250V-160', c['metal'], 10) + R(-60, -390, 46, 46, c['pop'], c, 6)


@prop('filing-cabinet', 150, 300, 'floor', ('office', 'records', 'paperwork', 'bureaucracy'))
def _(p, c):
    body = R(-75, -300, 150, 300, c['metal'], c, 6)
    for k in range(3):body += R(-62, -288 + k * 96, 124, 84, c['secondary'], c, 4) + L(f'M-24 {-246 + k * 96}H24', c['dark'], 8)
    return body


@prop('trash-can', 120, 160, 'floor', ('street', 'office', 'waste', 'cost'))
def _(p, c):
    return P('M-50 -140L-40 0H40L50 -140Z', c['metal'], c) + R(-60, -160, 120, 24, c['dark'], c, 6) + L('M-24 -120V-20M0 -120V-20M24 -120V-20', c['dark'], 4, 'opacity=".4"')


@prop('desk', 400, 230, 'floor', ('office', 'work', 'study'))
def _(p, c):
    return R(-200, -230, 400, 30, c['secondary'], c, 6) + R(80, -200, 110, 200, c['secondary'], c, 4) + L('M-180 -200V0', c['dark'], 12) + L('M100 -134H170M100 -66H170', c['dark'], 5)


@prop('chair', 160, 260, 'floor', ('office', 'work', 'meeting'))
def _(p, c):
    return R(-50, -260, 100, 130, c['primary'], c, 18) + R(-70, -126, 140, 30, c['primary'], c, 10) + L('M0 -96V-30M-50 0L0 -30L50 0', c['dark'], 9)


@prop('speaker', 140, 300, 'floor', ('stage', 'music', 'loud', 'launch'))
def _(p, c):
    return R(-70, -300, 140, 300, c['dark'], c, 10) + O(0, -90, 46, c['metal'], c) + O(0, -90, 18, c['dark'], c, False) + O(0, -220, 26, c['metal'], c) + O(0, -220, 9, c['dark'], c, False)


@prop('coffee-table', 280, 110, 'floor', ('home', 'living', 'relax'))
def _(p, c):
    return R(-140, -110, 280, 26, c['secondary'], c, 8) + L('M-110 -84V0M110 -84V0', c['dark'], 10) + R(-80, -150, 50, 40, c['pop'], c, 6) + R(20, -134, 70, 24, c['light'], c, 4)


@prop('hydrant', 110, 170, 'floor', ('street', 'city', 'emergency'))
def _(p, c):
    return R(-46, -24, 92, 24, c['dark'], c, 4) + R(-34, -140, 68, 120, c['pop'], c, 12) + P('M-38 -140Q0 -190 38 -140Z', c['pop'], c) + R(-56, -104, 112, 26, c['pop'], c, 8)


@prop('barrel', 150, 200, 'floor', ('workshop', 'storage', 'oil', 'energy'))
def _(p, c):
    return P('M-60 -200Q-80 -100 -60 0H60Q80 -100 60 -200Z', c['primary'], c) + L('M-70 -150H70M-70 -50H70', c['dark'], 6)


@prop('spotlight-stand', 150, 380, 'floor', ('stage', 'launch', 'spotlight', 'attention'))
def _(p, c):
    return L('M-60 0L0 -60L60 0M0 -60V-280', c['dark'], 8) + P('M-34 -330L34 -354L52 -290L-16 -266Z', c['metal'], c) + P('M52 -290L34 -354L60 -360L80 -296Z', c['secondary'], c)


@prop('cactus', 120, 240, 'floor', ('home', 'office', 'desert', 'calm'))
def _(p, c):
    return P('M-40 -80L-30 0H30L40 -80Z', c['secondary'], c) + R(-24, -230, 48, 160, '#3FA45B', c, 24) + R(-64, -180, 30, 70, '#3FA45B', c, 15) + R(34, -200, 30, 80, '#3FA45B', c, 15) + O(0, -232, 10, c['pop'], c, False)


@prop('armchair', 240, 230, 'floor', ('home', 'living', 'relax', 'read'))
def _(p, c):
    return R(-90, -230, 180, 150, c['secondary'], c, 30) + R(-120, -130, 240, 90, c['secondary'], c, 24) + R(-80, -110, 160, 50, c['primary'], c, 14) + L('M-90 -40V0M90 -40V0', c['dark'], 10)


@prop('diner-counter', 460, 220, 'floor', ('diner', 'kitchen', 'food', 'order'))
def _(p, c):
    return R(-230, -190, 460, 190, c['primary'], c, 6) + R(-240, -220, 480, 34, c['light'], c, 8) + L('M-230 -120H230', c['light'], 10) + R(-160, -290, 70, 74, c['metal'], c, 10) + R(60, -270, 120, 50, c['secondary'], c, 20)


@prop('skyline', 720, 520, 'floor', ('street', 'city', 'night', 'scale'))
def _(p, c):
    body = '';x = -360
    for k, (bw, bh) in enumerate(((110, 360), (90, 470), (140, 300), (100, 520), (130, 390), (150, 440))):
        fill = c['metal'] if k % 2 else c['floor']
        body += P(f'M{x} 0V{-bh}H{x + bw}V0Z', fill, c, extra='opacity=".85"')
        for wy in range(-bh + 30, -30, 54):
            for wx in range(x + 16, x + bw - 24, 30):body += f'<rect x="{wx}" y="{wy}" width="14" height="22" fill="{c["secondary"]}" opacity="{.35 + .5 * ((wx * 7 + wy) % 3 == 0):.2f}"/>'
        x += bw
    return body


# Wall props ------------------------------------------------------------------

@prop('wall-clock', 120, 120, 'wall', ('office', 'time', 'deadline', 'wait'))
def _(p, c):
    return O(0, -60, 56, c['light'], c) + O(0, -60, 50, 'none', c, False) + L('M0 -60V-100M0 -60L26 -46', c['dark'], 6) + ''.join(L(f'M{44 * math.cos(a):.1f} {-60 + 44 * math.sin(a):.1f}L{50 * math.cos(a):.1f} {-60 + 50 * math.sin(a):.1f}', c['dark'], 4) for a in [k * math.pi / 6 for k in range(12)])


@prop('poster', 170, 230, 'wall', ('office', 'home', 'street', 'brand', 'launch'))
def _(p, c):
    return R(-85, -230, 170, 230, c['pop'], c, 3) + O(0, -150, 44, c['secondary'], c, False) + R(-60, -80, 120, 16, c['light'], c, 3, False) + R(-44, -52, 88, 12, c['light'], c, 3, False) + O(-70, -218, 6, c['metal'], c, False) + O(70, -218, 6, c['metal'], c, False)


@prop('window', 240, 300, 'wall', ('home', 'office', 'kitchen', 'day', 'outside'))
def _(p, c):
    sky = '#BFE3F2'
    return R(-120, -300, 240, 300, c['light'], c, 6) + R(-104, -284, 208, 268, sky, c, 2, False) + P('M-104 -60Q-40 -110 20 -70Q70 -120 104 -80V-16H-104Z', '#A9C46B', c, False) + O(56, -220, 26, c['secondary'], c, False) + L('M0 -284V-16M-104 -150H104', c['light'], 12)


@prop('shelf', 260, 170, 'wall', ('home', 'office', 'kitchen', 'storage'))
def _(p, c):
    return R(-130, -20, 260, 20, c['secondary'], c, 3) + L('M-100 0L-100 30M100 0V30', c['dark'], 6) + R(-110, -100, 60, 80, c['primary'], c, 6) + P('M-30 -20L-10 -140L10 -20Z', c['accent'], c) + O(70, -60, 40, c['pop'], c) + R(40, -170, 60, 66, c['light'], c, 4)


@prop('whiteboard', 340, 230, 'wall', ('office', 'plan', 'meeting', 'strategy', 'learn'))
def _(p, c):
    return R(-170, -230, 340, 210, c['light'], c, 6) + L('M-130 -180H-20M-130 -150H40', c['primary'], 7) + L('M-120 -60L-60 -110L0 -80L80 -150', c['accent'], 7) + P('M80 -150L64 -140L80 -130Z', c['accent'], c, False) + R(-150, -24, 300, 12, c['metal'], c, 4)


@prop('neon-sign', 280, 140, 'wall', ('diner', 'street', 'night', 'open', 'launch'))
def _(p, c):
    return R(-140, -140, 280, 140, c['dark'], c, 16) + L('M-60 -120L-90 -70H-56L-80 -24', c['pop'], 9) + f'<circle cx="40" cy="-70" r="40" fill="none" stroke="{c["secondary"]}" stroke-width="9"/>' + L('M24 -70H56', c['accent'], 9)


@prop('framed-picture', 180, 150, 'wall', ('home', 'living', 'memory', 'art'))
def _(p, c):
    return R(-90, -150, 180, 150, c['secondary'], c, 4) + R(-74, -134, 148, 118, c['light'], c, 2, False) + P('M-74 -16L-20 -90L20 -50L46 -76L74 -16Z', c['primary'], c, False) + O(40, -110, 14, c['pop'], c, False)


@prop('pegboard', 300, 220, 'wall', ('workshop', 'tools', 'repair', 'build'))
def _(p, c):
    holes = ''.join(f'<circle cx="{x}" cy="{y}" r="3" fill="{c["dark"]}" opacity=".35"/>' for x in range(-130, 140, 26) for y in range(-200, -10, 26))
    return R(-150, -220, 300, 220, c['secondary'], c, 4) + holes + L('M-100 -170V-60M-120 -170H-80', c['metal'], 10) + P('M-20 -180H20V-60H-20Z', c['pop'], c) + L('M80 -180Q120 -120 80 -60', c['metal'], 10)


@prop('menu-board', 300, 200, 'wall', ('diner', 'kitchen', 'food', 'price', 'pricing'))
def _(p, c):
    body = R(-150, -200, 300, 200, c['dark'], c, 8)
    for k in range(4):body += L(f'M-120 {-160 + k * 40}H40', c['light'], 7, 'opacity=".85"') + R(70, -168 + k * 40, 50, 16, c['secondary'], c, 3, False)
    return body


@prop('wall-sign', 260, 90, 'wall', ('office', 'street', 'brand', 'label'))
def _(p, c):
    return L('M-80 -90V-120M80 -90V-120', c['metal'], 4) + R(-130, -90, 260, 90, c['accent'], c, 10) + R(-100, -60, 200, 22, c['light'], c, 4, False)


# Ceiling props ---------------------------------------------------------------

@prop('pendant-lamp', 140, 300, 'ceiling', ('home', 'diner', 'office', 'cosy', 'light'))
def _(p, c):
    return L('M0 -300V-90', c['dark'], 4) + P('M-70 0Q-70 -90 0 -96Q70 -90 70 0Z', c['primary'], c) + f'<ellipse cx="0" cy="2" rx="40" ry="8" fill="{c["secondary"]}"/>'


@prop('bunting', 720, 140, 'ceiling', ('party', 'launch', 'celebrate', 'stage'))
def _(p, c):
    body = L('M-360 -120Q0 -30 360 -120', c['dark'], 4);cols = (c['pop'], c['secondary'], c['accent'], c['primary'])
    for k in range(9):
        x = -320 + k * 80;y = -120 + 90 * (1 - ((x / 360) ** 2)) - 4
        body += P(f'M{x - 26} {y}L{x + 26} {y + 4}L{x + 2} {y + 54}Z', cols[k % 4], c)
    return body


@prop('string-lights', 720, 120, 'ceiling', ('home', 'night', 'party', 'cosy'))
def _(p, c):
    body = L('M-360 -110Q-180 -20 0 -90Q180 -20 360 -110', c['dark'], 3)
    for k in range(12):
        t = (k + .5) / 12;x = -360 + 720 * t;half = (t * 2) % 1;y = -110 + 70 * math.sin(math.pi * half) - 10 * (t > .5)
        body += f'<circle cx="{x:.1f}" cy="{y + 12:.1f}" r="11" fill="{c["secondary"] if k % 2 else c["pop"]}" stroke="{c["dark"]}" stroke-width="2"/>'
    return body


@prop('curtain', 200, 760, 'ceiling', ('stage', 'theatre', 'reveal', 'launch'))
def _(p, c):
    return P('M-100 -760H100V-200Q60 -80 30 0H-100Z', c['pop'], c) + L('M-60 -740V-120M-20 -740V-60M20 -740V-120M60 -740V-260', c['dark'], 4, 'opacity=".25"') + R(-110, -780, 220, 30, c['secondary'], c, 6)


# Sky props -------------------------------------------------------------------

@prop('moon', 150, 150, 'sky', ('night', 'sleep', 'dream', 'space'))
def _(p, c):
    return P('M30 -150A75 75 0 1 0 75 -30A62 62 0 1 1 30 -150Z', c['secondary'], c) + O(-20, -60, 9, c['light'], c, False) + O(10, -34, 6, c['light'], c, False)


@prop('cloud', 260, 120, 'sky', ('sky', 'cloud', 'weather', 'day', 'storage'))
def _(p, c):
    return P('M-110 0Q-150 -40 -100 -64Q-90 -120 -20 -104Q20 -140 70 -100Q130 -100 120 -40Q140 0 100 0Z', c['light'], c)


@prop('stars', 260, 200, 'sky', ('night', 'space', 'rating', 'dream'))
def _(p, c):
    body = ''
    for k, (x, y, s) in enumerate(((-90, -150, 1.2), (20, -170, .8), (100, -100, 1.0), (-30, -60, .7), (80, -30, .6), (-110, -40, .9))):
        body += f'<g transform="translate({x} {y}) scale({s})">' + P('M0 -20L5 -6L20 -6L8 3L12 18L0 9L-12 18L-8 3L-20 -6L-5 -6Z', c['secondary'] if k % 2 else c['light'], c) + '</g>'
    return body


@prop('sun', 180, 180, 'sky', ('day', 'energy', 'heat', 'summer'))
def _(p, c):
    rays = ''.join(L(f'M{70 * math.cos(a):.1f} {-90 + 70 * math.sin(a):.1f}L{88 * math.cos(a):.1f} {-90 + 88 * math.sin(a):.1f}', c['secondary'], 10) for a in [k * math.pi / 6 for k in range(12)])
    return rays + O(0, -90, 56, c['secondary'], c)


@prop('hot-air-balloon', 160, 260, 'sky', ('growth', 'lift', 'travel', 'rise'))
def _(p, c):
    return P('M0 -260Q80 -260 80 -170Q80 -110 20 -70H-20Q-80 -110 -80 -170Q-80 -260 0 -260Z', c['pop'], c) + P('M0 -260Q30 -200 20 -70H-20Q-30 -200 0 -260Z', c['secondary'], c, False) + L('M-20 -70L-16 -36M20 -70L16 -36', c['dark'], 3) + R(-20, -36, 40, 36, c['primary'], c, 4)


def names(mount=None, tag=None):
    return sorted(n for n, p in PROPS.items() if (mount is None or p.mount == mount) and (tag is None or tag in p.tags))
