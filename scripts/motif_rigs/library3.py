"""Rigs added with the metaphor-fit pass (2026-10-09).

The review of the PR #14 benchmarks found no machine for the commonest claim
shape in product reels, "it is inside everything" (every phone, every
browser). The planner reached for an overflowing bus instead. DeviceWall is
that relation drawn directly: a wall of devices, a stamp lands the product's
mark on the first screen, and the mark spreads screen by screen until every
device shows it.

Same contract as library.py: original authored SVG through palette roles, the
local origin is the floor under the rig's centre, and the contact closes
exactly at its contact frame.
"""
import math

from motif_rigs import register
from motif_rigs.base import Action, Rig, ease, lerp
from motif_rigs.library import label_size, settle, t_after, t_in, tag
from motif_ui_components import card, g, path, rect, txt


class DeviceWall(Rig):
    SHELF_Y = (-40, -330)         # shelf tops, bottom row first

    def layout(self, p):
        """Device centres and sizes, bottom row first."""
        n = p['count'];kind = p['kind'];per = math.ceil(n / 2) if n > 3 else n
        w, h = {'phone': (104, 190), 'browser': (170, 128), 'laptop': (170, 116)}[kind]
        if n <= 3:w, h = w * 1.3, h * 1.3          # one row: bigger devices
        if per * (w + 22) > 580:s = 580 / (per * (w + 22));w, h = w * s, h * s
        out = []
        for k in range(n):
            row = 0 if k < per else 1;col = k if row == 0 else k - per;cols = per if row == 0 else n - per
            x = (col - (cols - 1) / 2) * (w + 22);y = self.SHELF_Y[row] - h / 2 - 8
            out.append((x, y, w, h))
        return out

    def stamp_end(self, p):
        x, y, w, h = self.layout(p)[0];return (x, y - h * .1)

    def stamp_pos(self, p, t, tc, action):
        ex, ey = self.stamp_end(p)
        if not action:return (ex, ey)
        u = t_in(t, tc);return (ex, lerp(ey - 520, ey, ease(u) if u < 1 else 1.0))

    def lit(self, p, k, t, tc, action, start):
        if not action:return 1.0 if start == 'lit' else 0.0
        if k == 0:return 1.0 if t >= tc else 0.0
        after = t_after(t, tc);n = p['count'];begin = (k - 1) / n * .8
        return max(0.0, min(1.0, (after - begin) / .12))

    def device(self, p, k, x, y, w, h, c, glow):
        kind = p['kind'];slug = p.get('logo');screen_off = c['dark']
        if kind == 'phone':
            frame = rect(x - w / 2, y - h / 2, w, h, c['dark'], 16) + rect(x - w / 2 + 6, y - h / 2 + 14, w - 12, h - 28, screen_off, 6)
            sx, sy, sw, sh = x - w / 2 + 6, y - h / 2 + 14, w - 12, h - 28
        elif kind == 'browser':
            frame = rect(x - w / 2, y - h / 2, w, h, c['light'], 10, c['dark'], 3) + rect(x - w / 2, y - h / 2, w, 20, c['metal'], 8)
            frame += ''.join(f'<circle cx="{x - w / 2 + 12 + i * 12:.1f}" cy="{y - h / 2 + 10:.1f}" r="3.5" fill="{col}"/>' for i, col in enumerate((c['pop'], c['secondary'], c['accent'])))
            sx, sy, sw, sh = x - w / 2 + 6, y - h / 2 + 24, w - 12, h - 30
            frame += rect(sx, sy, sw, sh, screen_off, 4)
        else:
            frame = rect(x - w / 2, y - h / 2, w, h * .82, c['dark'], 8) + path(f'M{x - w / 2 - 14:.1f} {y + h * .32:.1f}H{x + w / 2 + 14:.1f}L{x + w / 2:.1f} {y + h * .44:.1f}H{x - w / 2:.1f}Z', c['metal'], 2, c['metal'])
            sx, sy, sw, sh = x - w / 2 + 7, y - h / 2 + 7, w - 14, h * .82 - 14
            frame += rect(sx, sy, sw, sh, screen_off, 4)
        shadow = rect(x - w / 2 + 6, y - h / 2 + 9, w, h, c['dark'], 12).replace('<rect', '<rect opacity=".18"')
        out = shadow + frame
        if glow > 0:
            out += rect(sx, sy, sw, sh, c['light'], 4).replace('<rect', f'<rect opacity="{glow:.3f}"')
            size = min(sw, sh) * .62 * (.6 + .4 * ease(glow))
            if slug:
                from motif_brand import glyph
                out += f'<g opacity="{glow:.3f}" transform="translate({x - size / 2:.2f} {sy + sh / 2 - size / 2:.2f})">{glyph(slug, size)}</g>'
            else:
                out += f'<circle cx="{x:.1f}" cy="{sy + sh / 2:.1f}" r="{size / 2:.1f}" fill="{c["accent"]}" opacity="{glow:.3f}"/>'
        names = p.get('names') or []
        if k < len(names):out += tag(names[k], x, y + h / 2 + 26, max(w + 10, len(names[k]) * 14 + 24), c, c['secondary'], 18)
        return out

    def draw(self, p, pose, c):
        start, end, action, t = pose;tc = self.contact_t('light-up') if action else 0
        body = ''
        for top in self.SHELF_Y[:1 if p['count'] <= 3 else 2]:  # cut-paper shelves on brackets
            body += rect(-300, top, 600, 18, c['secondary'], 5, c['dark'], 3) + rect(-260, top + 18, 14, 40, c['metal'], 3) + rect(246, top + 18, 14, 40, c['metal'], 3)
        body += rect(-300, -16, 600, 16, c['floor'], 4)
        for k, (x, y, w, h) in enumerate(self.layout(p)):
            bounce = settle(max(0.0, self.lit(p, k, t, tc, action, start) - .0), 5) if action else 0
            body += g(self.device(p, k, x, y, w, h, c, self.lit(p, k, t, tc, action, start)), 0, -bounce)
        # The stamp: the product mark on a handle; it presses the first screen, then lifts away.
        sx, sy = self.stamp_pos(p, t, tc, action) if action else self.stamp_end(p)
        press = t_after(t, tc) if action else (1.0 if start == 'lit' else 0.0)
        if action:show, lift = press < .4, (140 * ease(min(1.0, press / .4)) if t > tc else 0.0)
        else:show, lift = start == 'dark', 520.0
        if show:
            head = 74;stamp = rect(-12, -head - 120, 24, 120, c['metal'], 6, c['dark'], 3) + rect(-head / 2 - 10, -head - 10, head + 20, 26, c['primary'], 8, c['dark'], 3)
            if p.get('logo'):
                from motif_brand import sticker
                stamp += g(sticker(p['logo'], head, 0), 0, -head / 2 + 8)
            body += g(stamp, sx, sy - lift)
        count = sum(1 for k in range(p['count']) if self.lit(p, k, t, tc, action, start) >= 1)
        top = self.SHELF_Y[1] if p['count'] > 3 else self.SHELF_Y[0] - 160
        body += tag(p['label'], 0, top - 240, max(240, len(p['label']) * 20 + 40), c, c['light'], 26)
        body += tag(f'{count} / {p["count"]}', 210, top - 180, 120, c, c['pop'], 22, 4)
        return body

    def seams(self, p, pose):
        start, end, action, t = pose;tc = self.contact_t('light-up')
        return {'stamp-screen': (self.stamp_pos(p, t if action else 1, tc, action), self.stamp_end(p))}


register(DeviceWall(
    name='device-wall', description='Shelves of phones, browsers or laptops; a stamp lands the product mark on one screen and it spreads until every device shows it. Inside everything, everywhere, on every device.',
    params_schema={'type': 'object', 'properties': {
        'kind': {'enum': ['phone', 'browser', 'laptop']}, 'count': {'type': 'integer', 'minimum': 3, 'maximum': 8},
        'label': {'type': 'string', 'maxLength': 18}, 'logo': {'type': ['string', 'null']},
        'names': {'type': 'array', 'items': {'type': 'string', 'maxLength': 10}, 'maxItems': 8}},
        'required': ['kind', 'count', 'label'], 'additionalProperties': False},
    defaults={'kind': 'phone', 'count': 6, 'label': 'EVERY DEVICE', 'logo': None, 'names': []}, states=('dark', 'lit'),
    actions={'light-up': Action('light-up', 'dark', 'lit', 60, 'stamp-screen', 22)},
    bot_slot={'x': 300, 'y': 0, 'scale': .24, 'role': 'points at the screens as they light'}, tags=('everywhere', 'inside', 'every', 'device', 'phone', 'browser', 'ubiquitous', 'installed', 'ships'),
    footprint=(-300, -640, 600, 640)))
