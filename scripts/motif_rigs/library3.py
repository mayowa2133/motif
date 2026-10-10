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
        kind = p['kind'];slug = p.get('logo');screen_off = c['metal']  # an unlit screen is grey glass, not a black slab
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
        frame += f'<path d="M{sx + sw * .15:.1f} {sy + sh * .1:.1f}L{sx + sw * .55:.1f} {sy + sh * .1:.1f}L{sx + sw * .15:.1f} {sy + sh * .55:.1f}Z" fill="#FFFFFF" opacity="{.22 * (1 - glow):.3f}"/>'
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


class AppScreen(Rig):
    """The product in use, recreated as a cut-paper screen (no screenshots).

    Round-2 critique against the references (2026-10-10): their strongest
    frames show the product doing the thing (a signup form, a tool panel, a
    download page), while Motif only ever showed machines *about* the
    product. AppScreen is a large monitor, laptop or phone whose screen is a
    Motif-drawn terminal, app window or browser page. The brief's own lines
    type in, a cursor travels to the run key, and the result pops at contact.
    """
    SIZES = {'monitor': (550, 380), 'laptop': (470, 320), 'phone': (270, 480)}

    def screen(self, p):
        """(x, y, w, h) of the screen area; local origin is the floor under the rig."""
        w, h = self.SIZES[p['device']]
        top = -620 if p['device'] == 'phone' else (-560 if p['device'] == 'monitor' else -440)
        return (-w / 2, top, w, h)

    def button(self, p):
        x, y, w, h = self.screen(p)
        return (x + 70, y + h - 46)  # bottom-left: Bot stands on the right and must not hide the key

    def cursor_pos(self, p, t, tc, action):
        bx, by = self.button(p)
        if not action:return (bx, by)
        u = ease(min(1.0, t_in(t, tc) * 1.25)) if t < tc else 1.0
        return (lerp(bx + 260, bx, u), lerp(by + 170, by, u))

    def device(self, p, c):
        x, y, w, h = self.screen(p);d = p['device'];out = ''
        if d == 'monitor':
            out += rect(-40, y + h + 22, 80, -(y + h + 22) - 40, c['metal'], 6, c['dark'], 3) + rect(-120, -46, 240, 30, c['metal'], 10, c['dark'], 3)
            out += rect(x - 22, y - 22, w + 44, h + 44, c['dark'], 22)
        elif d == 'laptop':
            out += rect(x - 18, y - 18, w + 36, h + 36, c['dark'], 18)
            out += path(f'M{x - 70:.1f} {y + h + 18:.1f}H{x + w + 70:.1f}L{x + w + 30:.1f} {y + h + 64:.1f}H{x - 30:.1f}Z', c['dark'], 3, c['metal'])
            out += rect(-170, -24, 340, 24, c['floor'], 4).replace('<rect', '<rect opacity=".35"')
        else:
            out += rect(x - 16, y - 34, w + 32, h + 68, c['dark'], 34) + rect(-26, y - 22, 52, 8, c['metal'], 4)
        return rect(x - 10, y - 4, w + 44, h + 48, c['dark'], 22).replace('<rect', '<rect opacity=".16"') + out

    def ui(self, p, c, typed, done):
        x, y, w, h = self.screen(p);kind = p['ui'];lines = p.get('lines') or [];logo = p.get('logo')
        dark = kind == 'terminal';bg = '#1E2430' if dark else c['light'];ink = '#E8F0EA' if dark else c['dark']
        out = rect(x, y, w, h, bg, 8)
        bar = 44
        out += rect(x, y, w, bar, c['metal'] if not dark else '#2E3646', 8) + rect(x, y + bar - 8, w, 8, c['metal'] if not dark else '#2E3646')
        if p['device'] != 'phone':
            out += ''.join(f'<circle cx="{x + 20 + i * 18:.1f}" cy="{y + bar / 2:.1f}" r="5.5" fill="{col}"/>' for i, col in enumerate(('#FF6159', '#FFBD2E', '#28C941')))
        title = p.get('title') or '';tx = x + (78 if p['device'] != 'phone' else 18)
        if kind == 'browser':
            out += rect(tx - 6, y + 6, w - (tx - x) - 14, bar - 12, c['light'], 11)
            out += path(f'M{tx + 6:.1f} {y + bar / 2 + 4:.1f}h12v-7h-12z M{tx + 8:.1f} {y + bar / 2 - 3:.1f}v-3a4 4 0 0 1 8 0v3', c['accent'], 2.4)
            out += txt(title, tx + 26, y + bar / 2 + 7, 20, c['dark'], 700)
        else:
            out += txt(title, tx, y + bar / 2 + 7, 20, ink, 800)
        if logo:
            from motif_brand import glyph
            s = 28;out += f'<g transform="translate({x + w - s - 12:.1f} {y + (bar - s) / 2:.1f})">{glyph(logo, s, None if not dark else "#FFFFFF")}</g>'
        size = min(40 if p['device'] != 'phone' else 30, (w - 50) / max(8, max((len(l) for l in lines), default=8) * .62))
        ly = y + bar + 24 + size;budget = typed
        if kind == 'map':
            out += self.map_view(p, c, typed, done);lines = []
        for i, line in enumerate(lines):
            shown = line[:max(0, int(budget))];budget -= len(line)
            if kind == 'terminal':
                out += txt(('> ' if i == 0 else '  ') + shown, x + 20, ly, size, ink, 600)
            elif kind == 'window':
                tick = budget >= 0
                out += rect(x + 20, ly - size * .8, size * .9, size * .9, c['light'], 4, c['dark'], 2.5)
                if tick and shown:out += path(f'M{x + 24:.1f} {ly - size * .38:.1f}l{size * .22:.1f} {size * .22:.1f}l{size * .38:.1f} -{size * .5:.1f}', c['accent'], 3.5)
                out += txt(shown, x + 32 + size, ly, size * .86, c['dark'], 700)
            else:
                out += rect(x + 20, ly - size * .78, max(40, len(shown) * size * .56), size * 1.0, c['secondary'], 6).replace('<rect', '<rect opacity=".28"') + txt(shown, x + 26, ly, size * .86, c['dark'], 700)
            ly += size * 1.55
            if budget < 0:
                if 0 <= int(budget + len(line)) < len(line) + 1 and kind == 'terminal':
                    cx = x + 20 + (len(shown) + 2) * size * .58
                    out += rect(cx, ly - size * 1.55 - size * .8, size * .5, size * .95, ink)
                break
        bx, by = self.button(p);label = p.get('button') or ('RUN' if kind == 'terminal' else 'OK')
        out += rect(bx - 52, by - 22, 104, 44, c['accent'] if not done else c['primary'], 12, c['dark'], 3) + txt(label, bx, by + 7, 20, c['dark'], 900, 'middle')
        if p.get('credit'):
            cw = len(p['credit']) * 9.4 + 18
            out += rect(x + w - cw - 8, y + h - 34, cw, 26, '#FFFFFF', 6).replace('<rect', '<rect opacity=".9"') + txt(p['credit'], x + w - 17, y + h - 15, 15, c['dark'], 700, 'end')
        if done and p.get('result'):
            res = p['result'];rw = max(170, len(res) * 30 + 50);rx, ry = x + w / 2, (y + bar + 46 if kind == 'map' else y + h * .68);fit = min(1.0, (w - 16) / rw)
            out += g(rect(-rw / 2 + 5, -40, rw, 80, c['dark'], 14).replace('<rect', '<rect opacity=".22"') + rect(-rw / 2, -44, rw, 80, c['pop'] if c['pop'] != c['light'] else c['accent'], 14, c['dark'], 3)
                     + txt(res, 0, 12, 40, c['dark'], 900, 'middle'), rx, ry, -3, done * fit)
        return out

    USB = (-172, -34)  # left of centre: Bot stands on the right
    PINS = ((.22, .58), (.74, .5), (.55, .86), (.86, .72))  # below the result card's band

    def map_view(self, p, c, typed, done):
        """A Motif-drawn street map: blocks, a park, water, roads, and one pin per line.

        Round 8 (Codex's v11 critique): OpenStreetMap's editor showed checkbox rows, so the
        edit never looked like a map, and the next beat lost it. Pins drop in as the lines
        'type'; the last line is the new edit and gets the accent colour and a pulse.
        """
        x, y, w, h = self.screen(p);bar = 44;my, mh = y + bar, h - bar;out = rect(x, my, w, mh, '#EDE6D6')
        X = lambda u: x + w * u;Y = lambda v: my + mh * v
        for bx0, by0, bx1, by1 in ((.04, .06, .26, .26), (.32, .06, .66, .26), (.04, .34, .26, .58), (.32, .34, .66, .58), (.72, .64, .96, .94), (.04, .66, .26, .94)):
            out += rect(X(bx0), Y(by0), X(bx1) - X(bx0), Y(by1) - Y(by0), '#DCCFB8', 6)
        out += rect(X(.72), Y(.06), X(.96) - X(.72), Y(.56) - Y(.06), '#B7D99A', 14)          # park
        out += path(f'M{X(.32):.1f} {Y(1):.1f}C{X(.4):.1f} {Y(.78):.1f} {X(.58):.1f} {Y(.9):.1f} {X(.66):.1f} {Y(.66):.1f}V{Y(1):.1f}Z', '#9CC6E8', 1, '#9CC6E8')  # river bend
        road = lambda d, wd:path(d, '#C9BDA6', wd + 4) + path(d, '#FFFFFF', wd)
        for v in (.3, .62):out += road(f'M{x:.1f} {Y(v):.1f}H{x + w:.1f}', 12)
        for u in (.29, .69):out += road(f'M{X(u):.1f} {my:.1f}V{my + mh:.1f}', 12)
        out += road(f'M{x:.1f} {Y(.96):.1f}L{x + w:.1f} {Y(.12):.1f}', 7)                    # the new bike lane cuts across
        lines = p.get('lines') or [];budget = typed;fs = 17 if p['device'] == 'phone' else 18
        for i, line in enumerate(lines):
            shown = budget > 0;budget -= len(line)
            if not shown:break
            new = i == len(lines) - 1;px, py = X(self.PINS[i % 4][0]), Y(self.PINS[i % 4][1])
            drop = 1.0 if budget >= 0 else max(.2, 1 + budget / max(1, len(line)))
            col = c['accent'] if new else c['secondary'];r = 15 if new else 11
            if new and done:out += f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r + 10 + 14 * done:.1f}" fill="none" stroke="{col}" stroke-width="4" opacity="{max(0, 1 - done * .7):.2f}"/>'
            pin = path(f'M0 0C-{r * .2:.1f} -{r:.1f} -{r * 1.2:.1f} -{r * 1.3:.1f} -{r * 1.2:.1f} -{r * 2.2:.1f}A{r * 1.2:.1f} {r * 1.2:.1f} 0 1 1 {r * 1.2:.1f} -{r * 2.2:.1f}C{r * 1.2:.1f} -{r * 1.3:.1f} {r * .2:.1f} -{r:.1f} 0 0Z', c['dark'], 3, col)
            pin += f'<circle cx="0" cy="{-r * 2.2:.1f}" r="{r * .45:.1f}" fill="#FFFFFF"/>'
            out += g(pin, px, py, 0, drop)
            right = self.PINS[i % 4][0] < .6;lw = len(line) * fs * .58 + 14;lx = px + 20 if right else px - 20 - lw
            out += rect(lx, py - r * 2.2 - fs * .8, lw, fs * 1.35, '#FFFFFF', 6, c['dark'] if new else None, 2) + txt(line, lx + 7, py - r * 2.2 + fs * .3, fs, c['dark'], 800 if new else 700)
        return out

    def file_icon(self, c, name):
        body = path('M-30 -38H14L30 -22V38H-30Z', c['dark'], 3, '#FFFFFF') + path('M14 -38V-22H30', c['dark'], 3)
        body += rect(-20, -8, 40, 6, c['secondary'], 3) + rect(-20, 6, 30, 6, c['secondary'], 3)
        return body

    def usb(self, p, c, filled):
        """A USB stick on the floor in front of the device: where COPY sends the file."""
        ux, uy = self.USB
        body = rect(-92, -26, 150, 52, c['primary'], 16, c['dark'], 3) + rect(58, -16, 42, 32, c['metal'], 4, c['dark'], 3)
        body += rect(70, -8, 9, 7, c['dark']) + rect(84, -8, 9, 7, c['dark'])
        body += f'<circle cx="-70" cy="0" r="7" fill="{c["accent"] if filled else c["dark"]}"/>' + txt(p['send_to'], -8, 8, 22, c['dark'], 900, 'middle')
        return g(rect(-88, -18, 150, 52, c['dark'], 16).replace('<rect', '<rect opacity=".18"') + body, ux, uy, -6, 1.35)

    def send(self, p, c, k):
        """k in [0, 1]: the file leaves the screen and lands in the stick's slot."""
        x, y, w, h = self.screen(p);sx, sy = x + 44, y + 84;ex, ey = self.USB[0], self.USB[1] - 50
        u = k * k * (3 - 2 * k);fx = lerp(sx, ex, u) - 110 * math.sin(math.pi * u);fy = lerp(sy, ey, u) - 140 * math.sin(math.pi * u)
        return g(self.file_icon(c, (p.get('lines') or ['file'])[0].split()[0]), fx, fy, -14 + 20 * u, lerp(1.25, .9, u))

    def draw(self, p, pose, c):
        start, end, action, t = pose;tc = self.contact_t('run') if action else 0
        total = sum(len(l) for l in (p.get('lines') or []))
        if action:typed = total * min(1.0, t / max(1e-6, tc * .8));done = 0.0 if t < tc else min(1.0, .55 + .45 * ease(t_after(t, tc) * 3)) + settle(t_after(t, tc), .08)
        else:typed, done = (total, 1.0) if start == 'done' else (0, 0.0)
        if p.get('prefilled'):typed = total
        body = self.device(p, c) + self.ui(p, c, typed, done)
        if p.get('send_to'):
            k = (min(1.0, t_after(t, tc) * 1.5) if t >= tc else 0.0) if action else (1.0 if start == 'done' else 0.0)
            body += self.usb(p, c, k >= 1)
            if 0 < k < 1:body += self.send(p, c, k)
            elif k >= 1:body += g(self.file_icon(c, (p.get('lines') or ['file'])[0].split()[0]), self.USB[0], self.USB[1] - 84, 8, .85)
        cx, cy = self.cursor_pos(p, t, tc, action) if action else self.button(p)
        press = .85 if action and abs(t - tc) < .03 else 1.0
        body += g(path('M0 0L0 34L9 26L16 41L23 38L16 23L28 23Z', c['dark'], 3, '#FFFFFF'), cx - 2, cy - 2, 0, press)
        return body

    def seams(self, p, pose):
        start, end, action, t = pose;tc = self.contact_t('run')
        return {'cursor-press': (self.cursor_pos(p, t if action else 1, tc, action), self.button(p))}


register(AppScreen(
    name='app-screen', description='The product in use: a monitor, laptop or phone showing a Motif-drawn terminal, app window, browser page or street map (lines become map pins); the brief\'s lines type in, the cursor presses run and the result pops. send_to puts a USB stick in front and the file flies into it; credit adds a corner attribution; prefilled starts with the lines already in. Demos, commands, settings, checkboxes, downloads.',
    params_schema={'type': 'object', 'properties': {
        'device': {'enum': ['monitor', 'laptop', 'phone']}, 'ui': {'enum': ['terminal', 'window', 'browser', 'map']},
        'title': {'type': 'string', 'maxLength': 26}, 'lines': {'type': 'array', 'items': {'type': 'string', 'maxLength': 30}, 'minItems': 1, 'maxItems': 4},
        'result': {'type': 'string', 'maxLength': 14}, 'button': {'type': ['string', 'null'], 'maxLength': 8}, 'logo': {'type': ['string', 'null']},
        'send_to': {'type': ['string', 'null'], 'maxLength': 6}, 'credit': {'type': ['string', 'null'], 'maxLength': 34}, 'prefilled': {'type': 'boolean'}},
        'required': ['device', 'ui', 'lines'], 'additionalProperties': False},
    defaults={'device': 'monitor', 'ui': 'terminal', 'title': 'Terminal', 'lines': ['run the thing'], 'result': 'DONE', 'button': None, 'logo': None, 'send_to': None, 'credit': None, 'prefilled': False},
    states=('idle', 'done'),
    actions={'run': Action('run', 'idle', 'done', 60, 'cursor-press', 30)},
    bot_slot={'x': 300, 'y': 0, 'scale': .24, 'role': 'watches the screen and reacts to the result'},
    tags=('demo', 'screen', 'app', 'terminal', 'command', 'install', 'download', 'checkbox', 'setting', 'browser', 'website', 'click'),
    footprint=(-300, -680, 600, 680)))
