"""Six more Motif rigs (added 2026-10-09 with the per-film looks, so five films
can each tell their story with different machines). Original designs in the
same cut-paper language as library.py: authored SVG through palette roles, no
reference frame traced or copied.

Same contract as library.py: local origin is the floor under the rig's centre,
moving parts follow lerp(start, seam, ease(t / t_contact)) and hold the seam
afterwards, so each contact closes exactly at its contact frame.
"""
import math

from motif_rigs import register
from motif_rigs.base import Action, Rig, ease, ease_in, lerp
from motif_rigs.library import label_size, mini_bot_head, settle, t_after, t_in, tag
from motif_ui_components import card, g, path, rect, txt


def burst(x, y, u, c, n=8, r0=30, r1=90):
    """Cut-paper spark rays after a contact (u in [0, 1])."""
    if u <= 0 or u >= 1:return ''
    r_in, r_out = lerp(r0, r1 * .7, u), lerp(r0 + 20, r1, u);out = ''
    for k in range(n):
        a = k * 2 * math.pi / n
        out += path(f'M{x + r_in * math.cos(a):.1f} {y + r_in * math.sin(a):.1f}L{x + r_out * math.cos(a):.1f} {y + r_out * math.sin(a):.1f}', c['pop'] if k % 2 else c['accent'], 7, extra=f'opacity="{1 - u:.3f}"')
    return out


# 11 Domino run -------------------------------------------------------------------

class DominoRun(Rig):
    H, W, GAP, X0, FINAL = 150, 26, 44, -270, math.radians(60)

    def right(self, k):return self.X0 + k * self.GAP + self.W

    def bell_point(self, p):
        xr = self.right(p['count'] - 1);return (xr + self.H * math.sin(self.FINAL), -self.H * math.cos(self.FINAL))

    def angle(self, p, k, t, tc, action, start):
        if not action:return (self.FINAL if k == p['count'] - 1 else math.radians(52)) if start == 'fallen' else 0.0
        n = p['count'];begin = tc * k / n;land = tc * (k + 1) / n
        u = 0.0 if t <= begin else min(1.0, (t - begin) / max(1e-9, land - begin))
        return (self.FINAL if k == n - 1 else math.radians(52)) * ease_in(u)

    def draw(self, p, pose, c):
        start, end, action, t = pose;tc = self.contact_t('topple') if action else 0
        body = rect(-280, -16, 560, 16, c['floor'], 4)
        bx, by = self.bell_point(p);ring = t_after(t, tc) if action else (1.0 if start == 'fallen' else 0)
        swing = settle(ring, 14) if action else 0
        bell = path('M0 0Q-6 -70 50 -78Q106 -70 100 0Z', c['dark'], 0, c['dark'], 'transform="translate(5 7)" opacity=".18"') + path('M0 0Q-6 -70 50 -78Q106 -70 100 0Z', c['secondary'], 3, c['secondary']) + f'<circle cx="50" cy="8" r="12" fill="{c["pop"]}"/>'
        body += rect(bx + 46, by - 10, 8, -by + 10, c['metal'], 3) + g(bell, bx, by + 30 - 30, swing) + tag(p['target'], bx + 50, by - 110, 150, c, c['light'])
        body += burst(bx + 50, by - 30, ring if action else 0, c)
        for k in range(p['count']):
            a = self.angle(p, k, t, tc, action, start);xr = self.right(k)
            face = rect(-self.W, -self.H, self.W, self.H, c['primary'] if k % 2 else c['accent'], 5, c['dark'], 3) + f'<circle cx="{-self.W / 2}" cy="{-self.H * .7}" r="5" fill="{c["light"]}"/><circle cx="{-self.W / 2}" cy="{-self.H * .3}" r="5" fill="{c["light"]}"/>'
            body += f'<g transform="translate({xr:.2f} 0) rotate({math.degrees(a):.3f})">{face}</g>'
        return body + tag(p['label'], -60, -200, 240, c, c['light'])

    def seams(self, p, pose):
        start, end, action, t = pose;tc = self.contact_t('topple');k = p['count'] - 1
        a = self.angle(p, k, t if action else 1, tc, action, 'fallen');xr = self.right(k)
        return {'last-domino-bell': ((xr + self.H * math.sin(a), -self.H * math.cos(a)), self.bell_point(p))}


register(DominoRun(
    name='domino-run', description='A row of dominoes topples in turn until the last one rings a bell. Chain reaction, adoption spreading, one thing leads to the next.',
    params_schema={'type': 'object', 'properties': {'count': {'type': 'integer', 'minimum': 4, 'maximum': 8}, 'label': {'type': 'string', 'maxLength': 14}, 'target': {'type': 'string', 'maxLength': 10}},
                   'required': ['count', 'label', 'target'], 'additionalProperties': False},
    defaults={'count': 7, 'label': 'ONE CHANGE', 'target': 'EVERYONE'}, states=('standing', 'fallen'),
    actions={'topple': Action('topple', 'standing', 'fallen', 54, 'last-domino-bell', 36)},
    bot_slot={'x': -240, 'y': 0, 'scale': .22, 'role': 'taps the first domino'}, tags=('chain', 'spread', 'adoption', 'reaction', 'network', 'effect', 'everyone'),
    footprint=(-280, -420, 560, 420)))


# 12 Launch pad -------------------------------------------------------------------

class LaunchPad(Rig):
    RING_Y, NOSE, BASE0 = -770, 300, -40

    def base_y(self, t, tc, action, start):
        if not action:return self.RING_Y + self.NOSE if start == 'flying' else self.BASE0
        return lerp(self.BASE0, self.RING_Y + self.NOSE, ease_in(t_in(t, tc)))

    def draw(self, p, pose, c):
        start, end, action, t = pose;tc = self.contact_t('lift') if action else 0
        y = self.base_y(t, tc, action, start);after = t_after(t, tc) if action else (1.0 if start == 'flying' else 0)
        body = rect(-200, -40, 400, 40, c['metal'], 6) + rect(-150, -60, 300, 24, c['dark'], 6) + path('M-170 -40L-120 -360M170 -40L120 -360', c['metal'], 10)
        # The target ring: rocket nose meets its lower edge at the contact.
        body += f'<ellipse cx="0" cy="{self.RING_Y}" rx="120" ry="30" fill="none" stroke="{c["secondary"]}" stroke-width="14"/>' + tag(p['target'], 0, self.RING_Y - 80, 150, c, c['secondary'])
        flame_h = 40 + 90 * min(1.0, t * 3) if action else (120 if start == 'flying' else 0)
        if flame_h:
            body += path(f'M-40 {y}Q0 {y + flame_h * 1.4} 40 {y}Z', c['pop'], 0, c['pop']) + path(f'M-22 {y}Q0 {y + flame_h} 22 {y}Z', c['secondary'], 0, c['secondary'])
            if action:body += ''.join(f'<circle cx="{(k * 47) % 260 - 130}" cy="{-20 - (k * 13) % 30}" r="{18 + (k % 3) * 8}" fill="{c["light"]}" opacity="{.5 * min(1.0, t * 4):.3f}"/>' for k in range(7))
        rocket = (path(f'M-60 {y}V{y - 200}Q0 {y - self.NOSE - 40} 60 {y - 200}V{y}Z', c['dark'], 0, c['dark'], 'transform="translate(6 8)" opacity=".18"')
                  + path(f'M-60 {y}V{y - 200}Q0 {y - self.NOSE - 40} 60 {y - 200}V{y}Z', c['light'], 3, c['light'])
                  + path(f'M-60 {y - 20}L-110 {y + 20}V{y - 80}L-60 {y - 110}Z', c['primary'], 3, c['primary']) + path(f'M60 {y - 20}L110 {y + 20}V{y - 80}L60 {y - 110}Z', c['primary'], 3, c['primary'])
                  + f'<circle cx="0" cy="{y - 170}" r="30" fill="{c["accent"]}" stroke="{c["dark"]}" stroke-width="4"/>')
        nose_fix = path(f'M-20 {y - self.NOSE + 6}Q0 {y - self.NOSE - 4} 20 {y - self.NOSE + 6}', c['pop'], 8)
        body += rocket + nose_fix + burst(0, self.RING_Y, after, c, 10, 60, 170)
        return body + tag(p['label'], 0, -14, 240, c, c['light'])

    def seams(self, p, pose):
        start, end, action, t = pose;tc = self.contact_t('lift')
        y = self.base_y(t if action else 1, tc, action, 'flying')
        return {'nose-ring': ((0, y - self.NOSE), (0, self.RING_Y))}


register(LaunchPad(
    name='launch-pad', description='A rocket lifts off its pad and its nose punches through a target ring. Launch, release, going live, hitting a goal.',
    params_schema={'type': 'object', 'properties': {'label': {'type': 'string', 'maxLength': 14}, 'target': {'type': 'string', 'maxLength': 10}},
                   'required': ['label', 'target'], 'additionalProperties': False},
    defaults={'label': 'VERSION 1', 'target': 'LIVE'}, states=('ready', 'flying'),
    actions={'lift': Action('lift', 'ready', 'flying', 48, 'nose-ring', 30)},
    bot_slot={'x': -250, 'y': 0, 'scale': .22, 'role': 'presses the launch button'}, tags=('launch', 'release', 'ship', 'live', 'goal', 'speed', 'new', 'version'),
    footprint=(-280, -830, 560, 830)))


# 13 Magnet pull ------------------------------------------------------------------

class MagnetPull(Rig):
    FACE = 120

    def stuck(self, k):return (self.FACE - 70, -440 + k * 70)

    def origin(self, k):return (-130 + (k % 2) * 60, -120 - k * 60)

    def pos(self, k, n, t, tc, action, start):
        if not action:return self.stuck(k) if start == 'stuck' else self.origin(k)
        land = tc * (k + 1) / n;u = ease_in(t_in(t, land));(x0, y0), (x1, y1) = self.origin(k), self.stuck(k)
        return (lerp(x0, x1, u), lerp(y0, y1, u) - 60 * math.sin(math.pi * u))

    def draw(self, p, pose, c):
        start, end, action, t = pose;tc = self.contact_t('pull') if action else 0;n = p['count']
        mag = (path(f'M{self.FACE} -520H230Q300 -520 300 -330Q300 -140 230 -140H{self.FACE}V-210H220Q230 -210 230 -330Q230 -450 220 -450H{self.FACE}Z', c['primary'], 3, c['primary'])
               + rect(self.FACE, -520, 36, 70, c['light'], 2, c['dark'], 3) + rect(self.FACE, -210, 36, 70, c['light'], 2, c['dark'], 3) + rect(250, -140, 20, 140, c['metal'], 4))
        after = t_after(t, tc) if action else 0
        waves = ''.join(path(f'M{self.FACE - 20 - r} -400Q{self.FACE - 40 - r} -330 {self.FACE - 20 - r} -260', c['accent'], 5, extra=f'opacity="{.6 * (1 - after):.3f}"') for r in (30, 70, 110)) if action and after < 1 else ''
        body = rect(-280, -16, 560, 16, c['floor'], 4) + mag + waves
        for k in range(n):
            x, y = self.pos(k, n, t, tc, action, start)
            body += g(card(70, 56, [c['secondary'], c['accent'], c['pop']][k % 3], .08) + txt(p['item'], 35, 36, label_size(p['item'], 62, 18), c['dark'], 900, 'middle'), x - 70, y - 28, -6 + 4 * (k % 3))
        body += burst(self.FACE, -330, after, c)
        return body + tag(p['label'], 200, -40, 200, c, c['light'])

    def seams(self, p, pose):
        start, end, action, t = pose;tc = self.contact_t('pull');k = p['count'] - 1
        x, y = self.pos(k, p['count'], t if action else 1, tc, action, 'stuck')
        return {'last-item-magnet': ((x, y), self.stuck(k))}


register(MagnetPull(
    name='magnet-pull', description='A giant magnet pulls small cards across the floor until they all stick to it. Attraction, pull, everyone flocking to one thing.',
    params_schema={'type': 'object', 'properties': {'count': {'type': 'integer', 'minimum': 2, 'maximum': 6}, 'item': {'type': 'string', 'maxLength': 8}, 'label': {'type': 'string', 'maxLength': 12}},
                   'required': ['count', 'item', 'label'], 'additionalProperties': False},
    defaults={'count': 5, 'item': 'USERS', 'label': 'FREE'}, states=('loose', 'stuck'),
    actions={'pull': Action('pull', 'loose', 'stuck', 50, 'last-item-magnet', 34)},
    bot_slot={'x': -200, 'y': 0, 'scale': .22, 'role': 'watches the cards fly past'}, tags=('attract', 'pull', 'popular', 'users', 'magnet', 'flock', 'draw'),
    footprint=(-280, -540, 580, 540)))


# 14 Lock and key -----------------------------------------------------------------

class LockAndKey(Rig):
    SLOT = (-150, -250)

    def key_x(self, t, tc, action, start):
        if not action:return self.SLOT[0] if start == 'open' else -520
        return lerp(-520, self.SLOT[0], ease(t_in(t, tc)))

    def draw(self, p, pose, c):
        start, end, action, t = pose;tc = self.contact_t('unlock') if action else 0
        after = t_after(t, tc) if action else (1.0 if start == 'open' else 0)
        lift = 90 * ease(min(1.0, after * 2.2));turn = 90 * ease(min(1.0, after * 3))
        shackle = path(f'M-90 {-420 - lift}V{-520 - lift}Q-90 {-640 - lift} 0 {-640 - lift}Q90 {-640 - lift} 90 {-520 - lift}V{-420 - lift + (0 if lift else 0)}', c['metal'], 34)
        body = rect(-200, -30, 400, 30, c['floor'], 6) + shackle
        body += path('M-150 -430H150V-60Q150 -30 120 -30H-120Q-150 -30 -150 -60Z', c['dark'], 0, c['dark'], 'transform="translate(7 9)" opacity=".2"')
        body += path('M-150 -430H150V-60Q150 -30 120 -30H-120Q-150 -30 -150 -60Z', c['primary'], 4, c['primary'])
        body += f'<circle cx="0" cy="-250" r="34" fill="{c["dark"]}"/>' + rect(-12, -250, 24, 70, c['dark'], 6) + rect(-150, -264, 26, 28, c['dark'], 4)
        body += g(card(220, 54, c['light'], .06) + txt(p['label'], 110, 37, label_size(p['label'], 200, 28), c['dark'], 900, 'middle'), -110, -140)
        x = self.key_x(t, tc, action, start)
        key = (rect(-150, -14, 150, 28, c['secondary'], 6, c['dark'], 3) + path('M-60 14V34M-30 14V40', c['dark'], 8)
               + f'<circle cx="-200" cy="0" r="62" fill="{c["secondary"]}" stroke="{c["dark"]}" stroke-width="4"/><circle cx="-200" cy="0" r="46" fill="{c["light"]}"/>')
        bow = g(txt(p['key'], 0, 9, label_size(p['key'], 96, 24), c['dark'], 900, 'middle'), -200, 0)
        # The turn reads as the key flattening edge-on, then springing back (no swing out of the slot).
        squash = 1 - .75 * math.sin(math.radians(turn) * 2) if turn < 90 else 1.0
        body += f'<g transform="translate({x:.2f} {self.SLOT[1]}) scale(1 {squash:.4f})">{key}{bow}</g>'
        body += burst(0, -560 - lift, after if action else 0, c, 8, 40, 140)
        return body

    def seams(self, p, pose):
        start, end, action, t = pose;tc = self.contact_t('unlock')
        return {'key-slot': ((self.key_x(t if action else 1, tc, action, 'open'), self.SLOT[1]), self.SLOT)}


register(LockAndKey(
    name='lock-and-key', description='A big key slides into a giant padlock, turns, and the shackle springs open. Unlocking, access, free, open, security.',
    params_schema={'type': 'object', 'properties': {'label': {'type': 'string', 'maxLength': 12}, 'key': {'type': 'string', 'maxLength': 8}},
                   'required': ['label', 'key'], 'additionalProperties': False},
    defaults={'label': 'LOCKED', 'key': 'FREE'}, states=('locked', 'open'),
    actions={'unlock': Action('unlock', 'locked', 'open', 50, 'key-slot', 26)},
    bot_slot={'x': 230, 'y': 0, 'scale': .22, 'role': 'cheers as the lock opens'}, tags=('unlock', 'access', 'open', 'free', 'security', 'key', 'lock', 'padlock', 'secure'),
    footprint=(-280, -760, 560, 760)))


# 15 Sprout grow ------------------------------------------------------------------

class SproutGrow(Rig):
    SOIL = -150;SPOUT = (-30, -442)

    def drop(self, t, tc):
        u = ease_in(max(0.0, t - tc * .5) / (tc * .5)) if t < tc else 1.0;return (lerp(self.SPOUT[0], 0, u), lerp(self.SPOUT[1], self.SOIL, u))

    def draw(self, p, pose, c):
        start, end, action, t = pose;tc = self.contact_t('water') if action else 0
        grow = ease(t_after(t, tc)) if action else (1.0 if start == 'grown' else 0)
        tilt = 40 * ease(min(1.0, t / max(1e-9, tc * .5))) if action else 0
        can = g(path('M-80 -60H40V40H-80Z', c['secondary'], 3, c['secondary']) + path('M40 -40L120 -90', c['secondary'], 16) + path('M-80 -30Q-130 -10 -80 30', c['dark'], 8), -180, -450, tilt)
        body = can
        if action and tc * .5 <= t <= tc:
            x, y = self.drop(t, tc);body += f'<path d="M{x:.1f} {y - 26:.1f}Q{x + 14:.1f} {y - 6:.1f} {x:.1f} {y:.1f}Q{x - 14:.1f} {y - 6:.1f} {x:.1f} {y - 26:.1f}Z" fill="{c["accent"]}" stroke="{c["dark"]}" stroke-width="2"/>'
        top = self.SOIL - (40 + 100 * p['leaves']) * grow
        body += path(f'M0 {self.SOIL}Q-20 {(self.SOIL + top) / 2} 0 {top}', c['floor'], 12) if grow > 0 else ''
        for k in range(p['leaves']):
            ly = self.SOIL - 60 - 100 * k
            if ly > top + 10:
                side = -1 if k % 2 else 1;s = min(1.0, (ly - top) / 80)
                body += g(path('M0 0Q50 -50 100 0Q50 30 0 0Z', c['floor'], 3, c['secondary'] if k % 2 else c['accent']), 0, ly, -20 if side > 0 else 200, s)
        if grow > .8:
            u = (grow - .8) / .2
            body += g(''.join(f'<circle cx="{34 * math.cos(a):.1f}" cy="{34 * math.sin(a):.1f}" r="26" fill="{c["pop"]}" stroke="{c["dark"]}" stroke-width="3"/>' for a in [k * math.pi / 3 for k in range(6)]) + f'<circle r="24" fill="{c["secondary"]}" stroke="{c["dark"]}" stroke-width="3"/>', 0, top, 0, u) + tag(p['bloom'], 0, top - 90, 170, c, c['light'])
        body += path('M-130 -150H130L100 0H-100Z', c['primary'], 4, c['primary']) + rect(-140, -170, 280, 34, c['primary'], 8, c['dark'], 3) + f'<ellipse cx="0" cy="{self.SOIL}" rx="118" ry="14" fill="{c["dark"]}" opacity=".6"/>'
        return body + g(card(200, 46, c['light'], .06) + txt(p['label'], 100, 32, label_size(p['label'], 180, 24), c['dark'], 900, 'middle'), -100, -96)

    def seams(self, p, pose):
        start, end, action, t = pose;tc = self.contact_t('water')
        return {'drop-soil': (self.drop(t if action else 1, tc), (0, self.SOIL))}


register(SproutGrow(
    name='sprout-grow', description='A watering can drips onto a pot and a plant shoots up into bloom. Growth from small beginnings, community, nurturing, patience.',
    params_schema={'type': 'object', 'properties': {'leaves': {'type': 'integer', 'minimum': 2, 'maximum': 5}, 'label': {'type': 'string', 'maxLength': 12}, 'bloom': {'type': 'string', 'maxLength': 10}},
                   'required': ['leaves', 'label', 'bloom'], 'additionalProperties': False},
    defaults={'leaves': 4, 'label': 'ONE IDEA', 'bloom': 'MILLIONS'}, states=('seed', 'grown'),
    actions={'water': Action('water', 'seed', 'grown', 56, 'drop-soil', 20)},
    bot_slot={'x': 220, 'y': 0, 'scale': .22, 'role': 'waters the pot'}, tags=('growth', 'grow', 'community', 'nurture', 'small', 'start', 'bloom', 'volunteer', 'garden'),
    footprint=(-280, -740, 560, 740)))


# 16 Bridge span ------------------------------------------------------------------

class BridgeSpan(Rig):
    LEFT, RIGHT, TOP = -150, 150, -300

    def plank(self, p, k):
        w = (self.RIGHT - self.LEFT) / p['planks'];return self.LEFT + k * w, w

    def plank_y(self, p, k, t, tc, action, start):
        if not action:return self.TOP if start == 'spanned' else None
        land = tc * (k + 1) / p['planks'];u = t_in(t, land)
        return lerp(-900, self.TOP, ease_in(u)) if t > land * .3 or k == 0 else None

    def draw(self, p, pose, c):
        start, end, action, t = pose;tc = self.contact_t('span') if action else 0
        cliff = lambda x0, x1: path(f'M{x0} 0V{self.TOP}H{x1}V0Z', c['dark'], 3, c['secondary']) + path(f'M{x0} {self.TOP}H{x1}', c['pop'], 14) + ''.join(path(f'M{x0 + 16} {y}H{x1 - 16}', c['dark'], 3, extra='opacity=".2"') for y in range(-60, self.TOP, -60))
        body = cliff(-280, self.LEFT) + cliff(self.RIGHT, 280) + path(f'M{self.LEFT} -30Q0 30 {self.RIGHT} -30', c['secondary'], 30, extra='opacity=".7"')
        body += tag(p['left'], -215, self.TOP - 140, 120, c, c['light']) + tag(p['right'], 215, self.TOP - 140, 120, c, c['light'])
        for k in range(p['planks']):
            y = self.plank_y(p, k, t, tc, action, start)
            if y is None:continue
            x, w = self.plank(p, k);body += rect(x, y - 24, w, 24, c['primary'] if k % 2 else c['secondary'], 3, c['dark'], 3)
        after = t_after(t, tc) if action else (1.0 if start == 'spanned' else 0)
        if after > 0:
            cx = lerp(-230, 230, ease(after));body += mini_bot_head(cx, self.TOP - 60, 1.1, c, c['pop'])
        body += burst(self.RIGHT, self.TOP - 12, after if action else 0, c, 8, 20, 80)
        return body

    def seams(self, p, pose):
        start, end, action, t = pose;tc = self.contact_t('span');k = p['planks'] - 1;x, w = self.plank(p, k)
        y = self.plank_y(p, k, t if action else 1, tc, action, 'spanned')
        return {'last-plank-cliff': ((x + w, y if y is not None else -900), (self.RIGHT, self.TOP))}


register(BridgeSpan(
    name='bridge-span', description='Planks drop in one by one to bridge a gap between two cliffs; then a traveller crosses. Connecting people or systems, closing a gap.',
    params_schema={'type': 'object', 'properties': {'planks': {'type': 'integer', 'minimum': 3, 'maximum': 7}, 'left': {'type': 'string', 'maxLength': 8}, 'right': {'type': 'string', 'maxLength': 8}},
                   'required': ['planks', 'left', 'right'], 'additionalProperties': False},
    defaults={'planks': 5, 'left': 'YOU', 'right': 'WORLD'}, states=('gap', 'spanned'),
    actions={'span': Action('span', 'gap', 'spanned', 50, 'last-plank-cliff', 34)},
    bot_slot={'x': -220, 'y': 0, 'scale': .2, 'role': 'stands on the near cliff'}, tags=('connect', 'bridge', 'gap', 'link', 'together', 'share', 'map', 'open', 'interoperate'),
    footprint=(-280, -520, 560, 520)))
