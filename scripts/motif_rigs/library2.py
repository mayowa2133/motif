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

    @staticmethod
    def _chain(x0, y0, x1, y1, n, c):
        """Cut-paper chain from (x0, y0) to (x1, y1): alternating face-on and edge-on links."""
        ang = math.degrees(math.atan2(y1 - y0, x1 - x0));out = ''
        for k in range(n):
            f = (k + .5) / n;x = lerp(x0, x1, f);y = lerp(y0, y1, f)
            if k % 2 == 0:
                link = rect(-19, -11, 38, 22, 'none', 11, c['dark'], 11) + rect(-19, -11, 38, 22, 'none', 11, c['metal'], 6)
            else:
                link = rect(-19, -4, 38, 8, c['metal'], 4, c['dark'], 3)
            out += g(link, x, y, ang)
        return out

    @staticmethod
    def _sparkle(x, y, r, col, c, o):
        d = f'M{x} {y - r}Q{x + r * .18} {y - r * .18} {x + r} {y}Q{x + r * .18} {y + r * .18} {x} {y + r}Q{x - r * .18} {y + r * .18} {x - r} {y}Q{x - r * .18} {y - r * .18} {x} {y - r}Z'
        return path(d, c['dark'], 3, col, extra=f'opacity="{o:.3f}"')

    def _key(self, c):
        """Key in slot-local units: (0, 0) is the shoulder at the keyway; the blade runs +x into the lock."""
        d = c['dark'];k = c['secondary']
        blade = f'M-6 -12H92L104 -2V12H86V20H74V12H58V24H44V12H30V18H18V12H-6Z'
        s = path(blade, d, 0, d, 'transform="translate(5 6)" opacity=".18"') + path(blade, d, 3, k) + path('M4 -5H84', d, 2, extra='opacity=".35"')
        s += rect(-30, -18, 26, 36, k, 6, d, 3) + path('M-24 -18V18M-14 -18V18', d, 2, extra='opacity=".3"')
        s += f'<circle cx="-72" cy="0" r="44" fill="{k}" stroke="{d}" stroke-width="4"/>'
        s += f'<circle cx="-72" cy="0" r="26" fill="none" stroke="{d}" stroke-width="2" opacity=".35"/>'
        s += f'<circle cx="-72" cy="0" r="14" fill="{c["light"]}" stroke="{d}" stroke-width="3"/>'
        s += g(path('M-104 -14A34 34 0 0 1 -86 -34', '#FFFFFF', 6), opacity=.45)
        s += f'<circle cx="-100" cy="26" r="6" fill="{c["light"]}" stroke="{d}" stroke-width="3"/>'
        return s

    def draw(self, p, pose, c):
        start, end, action, t = pose;tc = self.contact_t('unlock') if action else 0
        after = t_after(t, tc) if action else (1.0 if start == 'open' else 0)
        lift = 90 * ease(min(1.0, after * 2.2));turn = 90 * ease(min(1.0, after * 3))
        d = c['dark'];sx, sy = self.SLOT
        body = g(rect(-230, -14, 460, 18, d, 9), opacity=.16) + rect(-190, -34, 380, 34, c['floor'], 8, d, 3)
        # Chain anchors and a chain threaded through the shackle; once the lock opens each half drops and hangs.
        drop = 84 * ease(min(1.0, after * 1.6)) + (settle(after, 7) if after else 0)
        chains = {}
        for side in (-1, 1):
            ax, ay = side * 252, -600
            body += rect(ax - 14, ay - 34, 28, 68, c['metal'], 6, d, 3) + f'<circle cx="{ax}" cy="{ay - 20}" r="4" fill="{d}"/><circle cx="{ax}" cy="{ay + 20}" r="4" fill="{d}"/>'
            L = math.hypot(252, 50);a0 = math.atan2(50, -side * 252) + math.radians(-side * drop)
            chains[side] = self._chain(ax, ay, ax + L * math.cos(a0), ay + L * math.sin(a0), 7, c)
        # Shackle: ink edge, metal bar, highlight, and the notch on the long leg.
        sh_d = f'M-90 {-420 - lift}V{-520 - lift}Q-90 {-640 - lift} 0 {-640 - lift}Q90 {-640 - lift} 90 {-520 - lift}V{-420 - lift}'
        body += chains[1] + path(sh_d, d, 42, extra='transform="translate(7 8)" opacity=".18"') + path(sh_d, d, 42) + path(sh_d, c['metal'], 34)
        body += g(path(f'M-98 {-440 - lift}V{-520 - lift}Q-98 {-630 - lift} -10 {-632 - lift}', '#FFFFFF', 6), opacity=.4)
        body += rect(80, -470 - lift, 20, 14, d, 3) + chains[-1]
        # Key goes behind the lock body so the blade disappears into the keyway.
        x = self.key_x(t, tc, action, start)
        squash = 1 - .75 * math.sin(math.radians(turn) * 2) if turn < 90 else 1.0
        body += f'<g transform="translate({x:.2f} {sy}) scale(1 {squash:.4f})">{self._key(c)}</g>'
        shell = 'M-150 -430H150V-60Q150 -30 120 -30H-120Q-150 -30 -150 -60Z'
        body += path(shell, d, 0, d, 'transform="translate(8 9)" opacity=".2"') + path(shell, d, 4, c['primary'])
        body += g(path('M-150 -60Q-150 -30 -120 -30H120Q150 -30 150 -60V-430H122V-74Q122 -58 106 -58H-150Z', d, 0, d), opacity=.14)
        body += g(rect(-138, -418, 18, 330, '#FFFFFF', 9), opacity=.22)
        body += rect(-150, -440, 300, 34, c['metal'], 8, d, 4) + g(rect(-140, -435, 200, 6, '#FFFFFF', 3), opacity=.35)
        for rx in (-128, 128):
            for ry in (-386, -56):body += f'<circle cx="{rx}" cy="{ry}" r="7" fill="{c["metal"]}" stroke="{d}" stroke-width="3"/>'
        # Side keyway plate on the left edge.
        body += rect(sx - 8, sy - 30, 34, 60, c['metal'], 6, d, 3) + rect(sx - 8, sy - 12, 22, 24, d, 4)
        # Keyhole escutcheon on the face.
        body += rect(-50, -320, 100, 150, c['metal'], 30, d, 4) + g(rect(-40, -312, 30, 6, '#FFFFFF', 3), opacity=.35)
        body += f'<circle cx="0" cy="-262" r="24" fill="{d}"/>' + path('M-10 -258L-18 -198H18L10 -258Z', d, 0, d)
        for ry in (-306, -184):body += f'<circle cx="0" cy="{ry}" r="5" fill="{c["light"]}" stroke="{d}" stroke-width="2"/>'
        body += g(card(220, 54, c['light'], .06) + txt(p['label'], 110, 37, label_size(p['label'], 200, 28), d, 900, 'middle'), -110, -140)
        # Paper tag on a string from the key's bow carries the key word.
        sway = settle(after, 5) if action else 0
        tx, ty = x - 100, sy + 26 * squash
        tag_card = card(140, 52, c['accent'], .08) + f'<circle cx="16" cy="26" r="6" fill="{c["wall"]}" stroke="{d}" stroke-width="2"/>'
        tag_card += txt(p['key'], 78, 36, label_size(p['key'], 100, 30), d if c['accent'] != d else c['light'], 900, 'middle')
        body += path(f'M{tx} {ty}Q{tx - 4} {ty + 22} {tx + 4} {ty + 40}', d, 3) + g(g(tag_card, -16, -26), tx + 4, ty + 64, -6 + sway)
        if action:
            body += burst(0, -560 - lift, after, c, 8, 40, 140)
            if 0 < after < 1:
                o = 1 - after
                for k, (px_, py_, r0) in enumerate(((-200, -470, 26), (196, -420, 22), (-178, -330, 16), (210, -300, 18), (160, -690, 20), (-150, -700, 15))):
                    sc = ease(min(1.0, after * 3 - k * .15)) if after * 3 > k * .15 else 0
                    if sc > 0:body += self._sparkle(px_, py_, r0 * sc, c['pop'] if k % 2 else c['accent'], c, o)
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

    @staticmethod
    def _drop_shape(x, y, r, c, o=1.0):
        """A cut-paper water drop whose bottom point sits at (x, y)."""
        return f'<path d="M{x:.1f} {y - 2.4 * r:.1f}Q{x + 1.3 * r:.1f} {y - .55 * r:.1f} {x:.1f} {y:.1f}Q{x - 1.3 * r:.1f} {y - .55 * r:.1f} {x:.1f} {y - 2.4 * r:.1f}Z" fill="{c["accent"]}" stroke="{c["dark"]}" stroke-width="2" opacity="{o:.3f}"/>'

    def _can(self, c):
        """Watering can in can-local units; the spout tip is at (120, -90)."""
        d = c['dark'];k = c['secondary']
        s = path('M-62 -60Q-20 -104 22 -60', d, 14) + path('M-62 -60Q-20 -104 22 -60', c['metal'], 8)
        s += path('M-80 -30Q-132 -14 -84 26', d, 14) + path('M-80 -30Q-132 -14 -84 26', k, 8)
        s += path('M30 -10L104 -78', d, 18) + path('M30 -10L104 -78', k, 12)
        s += g(path('M96 -96L128 -66L116 -54L84 -84Z', d, 3, c['metal']), 0, 0)
        s += ''.join(f'<circle cx="{106 + 5 * i:.1f}" cy="{-79 + 5 * i:.1f}" r="1.8" fill="{d}"/>' for i in range(3))
        body = 'M-84 -62H40Q46 -62 46 -56V36Q46 44 38 44H-76Q-84 44 -84 36Z'
        s += path(body, d, 0, d, 'transform="translate(6 7)" opacity=".18"') + path(body, d, 4, k)
        s += rect(-84, -40, 130, 14, c['metal'], 0, d, 3) + rect(-84, 18, 130, 12, c['metal'], 0, d, 3)
        s += g(rect(-74, -54, 10, 86, '#FFFFFF', 5), opacity=.3) + path('M-50 -18V10M-30 -18V10M-10 -18V10M10 -18V10', d, 2, extra='opacity=".18"')
        s += ''.join(f'<circle cx="{x}" cy="{y}" r="3" fill="{d}"/>' for x in (-72, 34) for y in (-33, 24))
        return s

    def _leaf(self, col, c):
        d = c['dark']
        s = path('M0 0Q46 -60 118 -6Q56 34 0 0Z', d, 3, col) + g(path('M0 0Q56 34 118 -6Q60 4 0 0Z', '#000000', 0, '#000000'), opacity=.12)
        s += path('M4 0Q60 -8 112 -6', d, 2.5, extra='opacity=".55"') + path('M40 -4L58 -24M70 -5L88 -22M48 -2L62 12', d, 2, extra='opacity=".4"')
        return s

    def _bloom(self, c):
        d = c['dark'];pop = c['pop'];s = ''
        for k in range(8):
            a = k * 45 + 22.5;s += g(f'<ellipse cx="0" cy="-42" rx="17" ry="30" fill="{pop}" stroke="{d}" stroke-width="3"/>', 0, 0, a)
        for k in range(6):
            a = k * 60;s += g(f'<ellipse cx="0" cy="-30" rx="15" ry="24" fill="{pop}" stroke="{d}" stroke-width="3"/>'
                              + f'<ellipse cx="0" cy="-30" rx="9" ry="16" fill="#FFFFFF" opacity=".22"/>', 0, 0, a)
        s += f'<circle r="24" fill="{c["secondary"]}" stroke="{d}" stroke-width="3"/>'
        s += ''.join(f'<circle cx="{12 * math.cos(k * 2.4):.1f}" cy="{12 * math.sin(k * 2.4):.1f}" r="2.6" fill="{d}" opacity=".55"/>' for k in range(9))
        s += '<ellipse cx="-8" cy="-10" rx="8" ry="5" fill="#FFFFFF" opacity=".4"/>'
        return s

    def draw(self, p, pose, c):
        start, end, action, t = pose;tc = self.contact_t('water') if action else 0
        grow = ease(t_after(t, tc)) if action else (1.0 if start == 'grown' else 0)
        after = t_after(t, tc) if action else 0
        tilt = 40 * ease(min(1.0, t / max(1e-9, tc * .5))) if action else 0
        d = c['dark'];body = g(self._can(c), -180, -450, tilt)
        # Pot shadow, saucer and terracotta body (drawn behind the stem only for the shadow).
        body += g(rect(-150, -10, 300, 14, d, 7), opacity=.16)
        top = self.SOIL - (40 + 100 * p['leaves']) * grow
        # Garden stake with twine ties beside the stem.
        body += path('M58 -150L66 -380', d, 12) + path('M58 -150L66 -380', c['metal'], 6) + path('M60 -376H72', d, 4)
        if grow > 0:
            stem = f'M0 {self.SOIL}Q-20 {(self.SOIL + top) / 2} 0 {top}'
            body += path(stem, d, 16) + path(stem, c['secondary'], 9) + g(path(f'M-3 {self.SOIL}Q-22 {(self.SOIL + top) / 2} -3 {top}', '#FFFFFF', 2.5), opacity=.3)
        for ty in (-230, -320):
            if top < ty - 10:body += path(f'M{-14 if ty < -300 else -12} {ty}Q24 {ty - 10} 64 {ty + 4}', c['accent'], 3) + path(f'M{-14 if ty < -300 else -12} {ty}Q24 {ty + 8} 64 {ty + 4}', d, 2, extra='opacity=".6"')
        for k in range(p['leaves']):
            ly = self.SOIL - 60 - 100 * k
            if ly > top + 10:
                side = -1 if k % 2 else 1;s = min(1.0, (ly - top) / 80);sway = settle(after, 4) * side
                body += g(self._leaf(c['secondary'] if k % 2 else c['accent'], c), -4 * side, ly, (-20 if side > 0 else 200) + sway, s)
        if grow > .8:
            u = (grow - .8) / .2
            body += g(self._bloom(c), 0, top, 12 * (1 - u), 1.2 * u)
            size = label_size(p['bloom'], 196, 28)
            body += path(f'M0 {top - 72}V{top - 86}', d, 3) + tag(p['bloom'], 0, top - 106, 214, c, c['light'], size)
        elif grow <= 0:
            # A seed with its first curl, waiting in the soil.
            body += path(f'M0 {self.SOIL - 2}Q-4 {self.SOIL - 18} 6 {self.SOIL - 26}', d, 7) + path(f'M0 {self.SOIL - 2}Q-4 {self.SOIL - 18} 6 {self.SOIL - 26}', c['secondary'], 3)
            body += g(self._leaf(c['accent'], c), 6, self.SOIL - 26, -30, .22)
        pot = 'M-128 -150H128L100 -4H-100Z'
        body += path(pot, d, 0, d, 'transform="translate(7 8)" opacity=".2"') + path(pot, d, 4, c['primary'])
        body += g(path('M70 -150H128L100 -4H58Z', '#000000', 0, '#000000'), opacity=.12) + g(path('M-112 -146L-90 -10', '#FFFFFF', 8), opacity=.25)
        body += rect(-118, -40, 236, 10, c['primary'], 0, d, 3) + rect(-112, -12, 224, 14, c['primary'], 6, d, 3)
        body += path('M-146 -176H146V-138H-146Z', d, 4, c['primary']) + g(rect(-138, -172, 200, 6, '#FFFFFF', 3), opacity=.3)
        body += g(rect(-146, -150, 292, 12, '#000000', 0), opacity=.14)
        # Soil with crumbs and pebbles; it darkens where the water lands.
        body += f'<ellipse cx="0" cy="{self.SOIL - 8}" rx="126" ry="14" fill="{d}"/>' + f'<ellipse cx="0" cy="{self.SOIL - 6}" rx="118" ry="10" fill="{c["floor"]}"/>'
        body += ''.join(f'<circle cx="{x}" cy="{self.SOIL - 6 + yy}" r="{r}" fill="{d}" opacity=".45"/>' for x, yy, r in ((-90, -2, 3), (-62, 3, 2.5), (-30, -4, 2), (34, 3, 3), (72, -3, 2.5), (98, 1, 2)))
        body += f'<ellipse cx="-74" cy="{self.SOIL - 8}" rx="9" ry="5" fill="{c["metal"]}" stroke="{d}" stroke-width="2"/><ellipse cx="88" cy="{self.SOIL - 7}" rx="7" ry="4" fill="{c["light"]}" stroke="{d}" stroke-width="2"/>'
        if after > 0 or (action and t >= tc):
            wet = min(1.0, after * 4 + .4)
            body += f'<ellipse cx="0" cy="{self.SOIL - 6}" rx="{30 + 40 * wet:.1f}" ry="6" fill="{d}" opacity=".35"/>'
            if after < .4:
                o = 1 - after / .4;r = 20 + 60 * after / .4
                body += path(f'M{-r:.1f} {self.SOIL - 12}Q{-r - 8:.1f} {self.SOIL - 30} {-r - 2:.1f} {self.SOIL - 40}M{r:.1f} {self.SOIL - 12}Q{r + 8:.1f} {self.SOIL - 30} {r + 2:.1f} {self.SOIL - 40}', c['accent'], 5, extra=f'opacity="{o:.3f}"')
        # Water drops fall in front of the pot so the contact with the soil stays visible.
        water = ''
        if action and tc * .5 <= t <= tc:
            x, y = self.drop(t, tc);water += self._drop_shape(x, y, 11, c)
            for k, lag in enumerate((.18, .36)):
                tt = t - lag * tc * .5
                if tt >= tc * .5:
                    x2, y2 = self.drop(tt, tc);water += self._drop_shape(x2, y2, 8 - 2 * k, c, .85)
        elif action and tc * .35 < t < tc * .5:
            water += self._drop_shape(self.SPOUT[0] + 4, self.SPOUT[1] + 18, 6, c, .8)
        body += water
        return body + g(card(200, 46, c['light'], .06) + txt(p['label'], 100, 32, label_size(p['label'], 180, 24), d, 900, 'middle'), -100, -96)

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
