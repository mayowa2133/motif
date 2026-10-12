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
from motif_rigs.library import ink, label_size, settle, t_after, t_in, tag
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

    def identity(self, p):
        # One window or terminal is one object; a different title is a different screen.
        return f'{self.name}:{p.get("title")}'

    def screen(self, p):
        """(x, y, w, h) of the screen area; local origin is the floor under the rig."""
        w, h = self.SIZES[p['device']]
        top = -620 if p['device'] == 'phone' else (-560 if p['device'] == 'monitor' else -440)
        return (-w / 2, top, w, h)

    def focus(self, p, role):
        # Close framing: the screen itself fills the frame (the references show the product big).
        if role != 'close':return None
        x, y, w, h = self.screen(p);return (x + w / 2, y + h / 2, w, h)

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
        dark = kind in ('terminal', 'cli');bg = ('#262624' if kind == 'cli' else '#1E2430') if dark else ('#FFFFFF' if kind == 'pr' else c['light']);ink = '#E8F0EA' if dark else c['dark']
        out = rect(x, y, w, h, bg, 8)
        bar = 44
        out += rect(x, y, w, bar, c['metal'] if not dark else '#2E3646', 8) + rect(x, y + bar - 8, w, 8, c['metal'] if not dark else '#2E3646')
        if p['device'] != 'phone':
            out += ''.join(f'<circle cx="{x + 20 + i * 18:.1f}" cy="{y + bar / 2:.1f}" r="5.5" fill="{col}"/>' for i, col in enumerate(('#FF6159', '#FFBD2E', '#28C941')))
        title = p.get('title') or '';tx = x + (78 if p['device'] != 'phone' else 18)
        if kind == 'browser' or (kind == 'calendar' and '.' in title):
            out += rect(tx - 6, y + 6, w - (tx - x) - 14, bar - 12, c['light'], 11)
            out += path(f'M{tx + 6:.1f} {y + bar / 2 + 4:.1f}h12v-7h-12z M{tx + 8:.1f} {y + bar / 2 - 3:.1f}v-3a4 4 0 0 1 8 0v3', c['accent'], 2.4)
            out += txt(title, tx + 26, y + bar / 2 + 7, 20, c['dark'], 700)
        else:
            out += txt(title, tx, y + bar / 2 + 7, 20, ink, 800)
        if logo:
            from motif_brand import glyph
            s = 28;out += f'<g transform="translate({x + w - s - 12:.1f} {y + (bar - s) / 2:.1f})">{glyph(logo, s, None if not dark else "#FFFFFF")}</g>'
        size = min(40 if p['device'] != 'phone' else 30, (w - 50) / max(8, max((len(l) for l in lines), default=8) * .62))
        # Lines end above the run key (uv film rough: an 8-line terminal ran under RUN and off the screen).
        size = min(size, (h - bar - 24 - 84) / max(1.0, len(lines) * 1.55 - .55))
        ly = y + bar + 24 + size;budget = typed
        if kind == 'map':
            out += self.map_view(p, c, typed, done);lines = []
        elif kind in self.VIEWS:
            out += getattr(self, kind + '_view')(p, c, typed, done);lines = []
        for i, line in enumerate(lines):
            shown = line[:max(0, int(budget))];budget -= len(line)
            if kind == 'terminal' and any(l.startswith('$ ') for l in lines):
                # '$ ' lines are commands, the rest their output in grey, as a real shell reads.
                cmd = line.startswith('$ ')
                out += (txt('$', x + 20, ly, size, '#7FD08A', 800) + txt(shown[2:], x + 20 + size * .9, ly, size, ink, 700)) if cmd else txt(shown, x + 20 + size * .9, ly, size * .92, '#9AA6B8', 600)
            elif kind == 'terminal':
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
        bx, by = self.button(p);label = p.get('button') or ('RUN' if kind == 'terminal' else ('ENTER' if kind == 'cli' else ('MERGE' if kind == 'pr' else 'OK')))
        out += rect(bx - 52, by - 22, 104, 44, c['accent'] if not done else c['primary'], 12, c['dark'], 3) + txt(label, bx, by + 7, 20, c['dark'], 900, 'middle')
        if p.get('credit'):
            cw = len(p['credit']) * 9.4 + 18
            out += rect(x + w - cw - 8, y + h - 34, cw, 26, '#FFFFFF', 6).replace('<rect', '<rect opacity=".9"') + txt(p['credit'], x + w - 17, y + h - 15, 15, c['dark'], 700, 'end')
        if done and p.get('result'):
            res = p['result'];rw = max(170, len(res) * 30 + 50);rx, ry = x + w / 2, (y + bar + 46 if kind == 'map' else y + h * .68);fit = min(1.0, (w - 16) / rw)
            if kind in self.VIEWS or kind == 'terminal':
                if kind == 'cli':kind = 'terminal'
                # A corner sticker clear of the content: below it where text runs down the screen
                # (chat, terminal, file tree; cut 6 stills: CLAUDE IS IN and VAULT READY covered lines).
                fit = min(.72, (w * .5) / rw);rx, ry = x + w - rw * fit / 2 - 14, (y + h - 34 if kind in ('chat', 'terminal', 'files', 'note', 'pr', 'calendar') else y + 44 + 34)
            out += g(rect(-rw / 2 + 5, -40, rw, 80, c['dark'], 14).replace('<rect', '<rect opacity=".22"') + rect(-rw / 2, -44, rw, 80, c['pop'] if c['pop'] not in (c['light'], c['dark']) else c['accent'], 14, c['dark'], 3)
                     + txt(res, 0, 12, 40, c['dark'], 900, 'middle'), rx, ry, -3, done * fit)
        return out

    # Product views (2026-10-11 reference comparison): the references show the real app doing the
    # thing in most shots. These recreate common app surfaces in Motif's own drawing, with the
    # brief's lines as the content, so a film can show the product rather than a machine about it.
    VIEWS = ('files', 'note', 'graph', 'chat', 'cli', 'pr', 'calendar')

    def _shown(self, lines, typed):
        """(line, visible share) per line as the typing budget reaches it."""
        out, budget = [], typed
        for line in lines:
            out.append((line, max(0.0, min(1.0, budget / max(1, len(line))))));budget -= len(line)
        return out

    def files_view(self, p, c, typed, done):
        """A file tree: names ending in / are folders, leading spaces indent; rows pop in as they type.
        With a pane (plan-to-9 phase 1: editors show the open file beside the tree), the last file in
        the tree is open on the right in a tab, its lines numbered, typing in after the tree."""
        lines = p.get('lines') or [];pane = p.get('pane') or []
        x, y, w, h = self.screen(p);top = y + 44;tw = w * (.42 if pane else .3)
        out = rect(x, top, tw, h - 44, c['metal']).replace('<rect', '<rect opacity=".35"')
        rows = self._shown(lines, typed);size = min(30, (h - 130) / max(4, len(rows)) / 1.6)
        if pane:
            size = min(size, max(12, (tw - 30) / max(1.0, max(((len(l) - len(l.lstrip(' '))) // 2) * .9 + 1.35 + len(l.strip()) * .55 for l in lines))))
        indent = size * .9 if pane else 34
        for i, (line, k) in enumerate(rows):
            if k <= 0:break
            depth = (len(line) - len(line.lstrip(' '))) // 2;name = line.strip();folder = name.endswith('/')
            ry = top + 24 + i * size * 1.6;rx = x + 16 + depth * indent
            icon = (path(f'M0 0H{size * .45:.1f}L{size * .6:.1f} {size * .18:.1f}H{size * 1.1:.1f}V{size * .85:.1f}H0Z', c['dark'], 2.5, c['secondary']) if folder
                    else path(f'M0 0H{size * .6:.1f}L{size * .85:.1f} {size * .25:.1f}V{size:.1f}H0Z', c['dark'], 2.5, '#FFFFFF'))
            if pane and not folder and name == next((l.strip() for l in reversed(lines) if not l.strip().endswith('/')), None):
                out += rect(x + 4, ry - size * .3, tw - 8, size * 1.5, c['accent'], 5).replace('<rect', '<rect opacity=".35"')
            row = g(icon, rx, ry, 0, 1) + txt(name, rx + size * 1.35, ry + size * .78, size * .9, c['dark'], 800 if folder else 600)
            out += g(row, 0, 0, 0, 1, 1, min(1.0, k * 1.5))
        if pane:
            open_file = next((l.strip() for l in reversed(lines) if not l.strip().endswith('/')), 'file')
            px = x + tw;pw = w - tw;left = typed - sum(len(l) for l in lines)
            out += rect(px, top, pw, 34, c['metal']).replace('<rect', '<rect opacity=".55"') + rect(px + 8, top + 4, len(open_file) * 10 + 34, 30, '#FFFFFF', 5)
            out += txt(open_file, px + 24, top + 25, 16, c['dark'], 800)
            ps = min(19, (pw - 60) / max(14, max(len(l) for l in pane) * .56), (h - 44 - 34 - 70) / max(1, len(pane) * 1.5))
            for i, (line, k) in enumerate(self._shown(pane, max(0, left))):
                if k <= 0:break
                ly = top + 34 + 16 + ps + i * ps * 1.5;shown = line[:max(1, int(len(line) * k))]
                out += txt(str(i + 1), px + 30, ly, ps * .8, '#9A968E', 600, 'end')
                head = line.startswith('#');meta = line == '---' or (':' in line and not head and i < 5)
                if meta and ':' in shown:
                    key, _, val = shown.partition(':');out += txt(key + ':', px + 40, ly, ps, '#8250DF', 700) + txt(val.strip(), px + 40 + (len(key) + 1.6) * ps * .58, ly, ps, c['dark'], 600)
                else:
                    out += txt(shown, px + 40, ly, ps * (1.15 if head else 1), c['dark'] if not line == '---' else '#9A968E', 900 if head else 600)
        return out

    def note_view(self, p, c, typed, done):
        """A Markdown note: the first line is the page title, the rest body lines where [[name]] is a link chip."""
        import re
        x, y, w, h = self.screen(p);top = y + 44;lines = p.get('lines') or [];rows = self._shown(lines, typed)
        out = ''
        if rows and rows[0][1] > 0:
            title = rows[0][0];ts = min(40, (w - 60) / max(6, len(title) * .62))
            out += txt(title, x + 26, top + 18 + ts, ts, c['dark'], 900) + rect(x + 26, top + 30 + ts, w - 52, 3, c['secondary'])
        ts = min(40, (w - 60) / max(6, len(lines[0] if lines else 'x') * .62));size = min(30, (w - 60) / max(14, max((len(l) for l in lines[1:]), default=14) * .6))
        # Body lines end above the run key (Claudex cut 3: the OK key covered the last line).
        size = min(size, (y + h - 72 - top - 34 - ts) / (1.1 + max(0, len(lines) - 2) * 1.55));body_top = top + 34 + ts + size * 1.1
        for i, (line, k) in enumerate(rows[1:]):
            if k <= 0:break
            ly = body_top + i * size * 1.55;lx = x + 26
            shown = line[:max(1, int(len(line) * k))]
            for part in re.split(r'(\[\[[^\]]*\]?\]?)', shown):
                if not part:continue
                if part.startswith('[['):
                    name = part.strip('[]');pw = len(name) * size * .6 + 16
                    out += rect(lx, ly - size * .86, pw, size * 1.2, c['accent'], 8).replace('<rect', '<rect opacity=".28"') + txt(name, lx + 8, ly, size, c['dark'], 800) + rect(lx + 8, ly + 4, pw - 16, 2.5, c['dark'])
                    lx += pw + 8
                else:
                    out += txt(part, lx, ly, size, c['dark'], 600);lx += len(part) * size * .58
        return out

    def graph_view(self, p, c, typed, done):
        """A knowledge graph: one node per line, linked to the first (the hub) and to their neighbours;
        nodes and links grow in as the lines type, and the newest node pulses at the result."""
        x, y, w, h = self.screen(p);top = y + 44;gh = h - 44;out = rect(x, top, w, gh, '#232532')
        lines = p.get('lines') or [];rows = self._shown(lines, typed);n = len(lines)
        cx, cy = x + w / 2, top + gh * .45
        pts = [(cx, cy)] + [(cx + w * .38 * math.cos(-math.pi / 2 + 2 * math.pi * i / max(1, n - 1)), cy + gh * .33 * math.sin(-math.pi / 2 + 2 * math.pi * i / max(1, n - 1))) for i in range(n - 1)]
        for i in range(1, n):
            k = rows[i][1]
            if k <= 0:continue
            (x0, y0), (x1, y1) = pts[0], pts[i]
            out += path(f'M{x0:.1f} {y0:.1f}L{x0 + (x1 - x0) * k:.1f} {y0 + (y1 - y0) * k:.1f}', '#8C8FA8', 3)
            if i > 1 and rows[i - 1][1] >= 1:
                (x2, y2) = pts[i - 1];out += path(f'M{x2:.1f} {y2:.1f}L{x2 + (x1 - x2) * k:.1f} {y2 + (y1 - y2) * k:.1f}', '#5C5F78', 2)
        fs = min(22, w / 18)
        for i, (line, k) in enumerate(rows):
            if k <= 0:continue
            px, py = pts[i];r = (22 if i == 0 else 13) * min(1.0, k * 2);col = c['accent'] if i == 0 else ('#A88BFA' if i < n - 1 or not done else c['pop'])
            if i == n - 1 and done:out += f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r + 8 + 12 * done:.1f}" fill="none" stroke="{c["pop"]}" stroke-width="3" opacity="{max(0, 1 - done * .6):.2f}"/>'
            out += f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r:.1f}" fill="{col}"/>'
            out += txt(line, px, py + r + fs + 2, fs, '#E8E9F2', 700, 'middle')
        return out

    AGENTS = {'claude': ('Claude Code', '#D97757'), 'openai': ('Codex', '#E8E8E8')}
    # The footer each agent's terminal shows (plan-to-9 phase 1: the real product's chrome, not a blank box).
    FOOTERS = {'claude': ('? for shortcuts', 'accept edits on'), 'openai': ('Enter to send', '98% context left')}
    CLI_KINDS = {'> ': 1, '* ': 1, '- ': 1, '+ ': 1, 'x ': 1, '[ ] ': 1, '[x] ': 1, '? ': 3.25}

    @staticmethod
    def star(cx, cy, r, col, turn=0.0):
        """The thinking spinner: a six-armed asterisk drawn as paths (fonts may lack the glyph)."""
        d = ''.join(f'M{cx:.1f} {cy:.1f}L{cx + r * math.cos(turn + i * math.pi / 3):.1f} {cy + r * math.sin(turn + i * math.pi / 3):.1f}' for i in range(6))
        return path(d, col, max(2.0, r * .32))

    @staticmethod
    def _clip(x, y, w, h, body):
        import zlib
        cid = f'clip{zlib.crc32(f"{x:.1f},{y:.1f},{w:.1f},{h:.1f}".encode()) % 10 ** 8}'
        return f'<clipPath id="{cid}"><rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}"/></clipPath><g clip-path="url(#{cid})">{body}</g>'

    def cli_view(self, p, c, typed, done):
        """A coding agent in the terminal, redrawn in Motif's paper style with the real product's layout
        (plan-to-9 phase 1: reference 09's screens are dense, ours were a sparse block of text).

        A welcome box carries the agent's mark, name and folder; then the session, where '> ' is the
        prompt, '* ' an action (a dot that turns green once done), '- ' its result under a hook,
        '+ ' / 'x ' added and removed diff lines, '[ ] ' / '[x] ' todos ([x] ticks and strikes through
        once typed) and '? ' a permission prompt with Yes / No. While the agent works a spinner turns
        under the last line; long sessions scroll up as they type. An input box and the agent's footer
        sit at the bottom."""
        from motif_brand import glyph
        x, y, w, h = self.screen(p);top = y + 44;lines = p.get('lines') or [];rows = self._shown(lines, typed)
        logo = p.get('logo') or '';name, accent = self.AGENTS.get(logo, (p.get('title') or 'Agent', c['accent']))
        name = p.get('agent') or name;bh = 54;out = ''
        # The welcome box is the first thing in the session and scrolls away with it, as in the real tool.
        head = rect(x + 14, top + 10, w - 28, bh, 'none', 10, accent, 2.5)
        if logo:head += f'<g transform="translate({x + 28:.1f} {top + 10 + (bh - 30) / 2:.1f})">{glyph(logo, 30, accent)}</g>'
        nx = x + (72 if logo else 30)
        head += txt(name, nx, top + 10 + bh * .47, 21, '#F5F2EC', 800) + txt(p.get('cwd') or '/help for help', nx, top + 10 + bh * .83, 14, '#9A968E', 600)
        foot_l, foot_r = self.FOOTERS.get(logo, ('Enter to send', ''))
        box = 36;by = y + h - box - 26;bx = x + 140
        area_top = top + 10 + bh + 8;area_h = by - 6 - area_top
        units = sum(self.CLI_KINDS.get(next((m for m in self.CLI_KINDS if l.startswith(m)), ''), 1) for l in lines) + 1
        size = max(14.5, min(20, (w - 70) / max(14, max((len(l) for l in lines), default=14) * .55), (area_h + bh + 8) / max(1, units * 1.42)))
        step = size * 1.42;body = head;ly = bh + 8 + size * 1.05;turn = typed * .35
        area_top -= bh + 8;area_h += bh + 8
        for line, k in rows:
            if k <= 0:break
            mark = next((m for m in self.CLI_KINDS if line.startswith(m)), '');text = line[len(mark):]
            shown = text[:max(1, int(len(text) * k))];lx = x + 26;yy = area_top + ly
            if mark == '> ':
                body += rect(x + 18, yy - size * 1.0, w - 36, size * 1.35, '#3A3835', 6) + txt('>', lx, yy, size, '#9A968E', 800) + txt(shown, lx + size * .9, yy, size, '#F5F2EC', 600)
            elif mark == '* ':
                col = '#5FB85F' if k >= 1 else accent
                body += f'<circle cx="{lx + size * .3:.1f}" cy="{yy - size * .33:.1f}" r="{size * .26:.1f}" fill="{col}"/>' + txt(shown, lx + size * .9, yy, size, '#F5F2EC', 800)
            elif mark == '- ':
                body += path(f'M{lx + size * .6:.1f} {yy - size * .9:.1f}V{yy - size * .3:.1f}H{lx + size * 1.1:.1f}', '#8A867E', 2.2) + txt(shown, lx + size * 1.4, yy, size * .92, '#B9B4AA', 600)
            elif mark in ('+ ', 'x '):
                add = mark == '+ ';n = sum(1 for l, _ in rows[:rows.index((line, k))] if l[:2] in ('+ ', 'x ')) + 12
                body += rect(lx + size * 1.2, yy - size * .98, w - 52 - size * 1.2, size * 1.3, '#23482A' if add else '#5A2424', 3)
                body += txt(str(n), lx + size * 1.05, yy, size * .8, '#7D7A73', 600, 'end') + txt('+' if add else '-', lx + size * 1.5, yy, size, '#7FD08A' if add else '#F08A8A', 800)
                body += txt(shown, lx + size * 2.3, yy, size * .92, '#DDF5DF' if add else '#F7DADA', 600)
            elif mark in ('[ ] ', '[x] '):
                ticked = mark == '[x] ' and k >= 1;bs = size * .78;bx0 = lx + size * 1.3
                body += rect(bx0, yy - bs * 1.05, bs, bs, 'none', 2, '#B9B4AA', 2)
                if ticked:body += path(f'M{bx0 + bs * .2:.1f} {yy - bs * .55:.1f}l{bs * .25:.1f} {bs * .28:.1f}l{bs * .45:.1f} -{bs * .6:.1f}', '#5FB85F', 3)
                body += txt(shown, bx0 + bs * 1.5, yy, size * .92, '#8A867E' if ticked else '#F5F2EC', 600)
                if ticked:body += rect(bx0 + bs * 1.5, yy - size * .33, len(shown) * size * .5, 2, '#8A867E')
            elif mark == '? ':
                ph = step * 3.05;py0 = yy - size * 1.05
                body += rect(x + 18, py0, w - 36, ph, 'none', 8, accent, 2) + txt(shown, lx, py0 + size * 1.25, size, '#F5F2EC', 800)
                for j, opt in enumerate(('1. Yes', '2. No')):
                    oy = py0 + size * 1.25 + step * (j + 1) * .9;on = j == 0
                    body += txt(('> ' if on else '  ') + opt, lx + size * .4, oy, size * .92, accent if on else '#B9B4AA', 800 if on else 600)
                ly += step * 2.25
            else:
                body += txt(shown, lx, yy, size, '#D8D4CC', 600)
            ly += step
            if k < 1:break
        if done <= 0 and typed > 0:
            sy = area_top + ly;body += self.star(x + 26 + size * .35, sy - size * .35, size * .42, accent, turn) + txt('Thinking... (esc to interrupt)', x + 26 + size * 1.1, sy, size * .9, accent, 700)
            ly += step
        # Scroll a whole row at a time, as a terminal does, so no half-cut line sits under the welcome box.
        over = ly - size * .6 - area_h;shift = math.ceil(over / step) * step if over > 0 else 0.0
        out += self._clip(x + 4, area_top - 2, w - 8, area_h + 4, f'<g transform="translate(0 {-shift:.1f})">{body}</g>')
        out += rect(bx, by, x + w - 14 - bx, box, 'none', 10, '#6E6A63', 2) + txt('>', bx + 14, by + box / 2 + 7, 20, '#9A968E', 800)
        if done <= 0:out += rect(bx + 34, by + 9, 10, box - 18, '#F5F2EC')
        out += txt(foot_l, bx + 4, y + h - 8, 13, '#7D7A73', 600) + txt(foot_r, x + w - 18, y + h - 8, 13, '#7D7A73', 600, 'end')
        return out

    def pr_view(self, p, c, typed, done):
        """A pull request page in the style of a code host (plan-to-9 phase 1): the first line is the PR
        title with an Open pill that turns Merged at the result, a tab row, then rows where '✓ ' (or '+ ') / 'x '
        are passing and failing checks and '@name: text' a review comment with an avatar."""
        x, y, w, h = self.screen(p);top = y + 44;lines = p.get('lines') or [];rows = self._shown(lines, typed);out = ''
        if not rows or rows[0][1] <= 0:return out
        title = rows[0][0];ts = min(26, (w - 60) / max(8, len(title) * .58))
        out += txt(title[:max(1, int(len(title) * rows[0][1]))], x + 22, top + 14 + ts, ts, c['dark'], 900)
        merged = done > 0;pill = 'Merged' if merged else 'Open';pc = '#8250DF' if merged else '#1F883D'
        py = top + 26 + ts;out += rect(x + 22, py, 92, 28, pc, 14) + txt(pill, x + 68, py + 20, 16, '#FFFFFF', 800, 'middle')
        out += txt(f'{max(0, len(lines) - 1)} checks, 2 reviewers', x + 126, py + 20, 15, '#6E7781', 600)
        ty = py + 44
        for i, (tab, tw) in enumerate((('Conversation', 118), ('Commits', 80), ('Checks', 70), ('Files changed', 120))):
            tx = x + 22 + sum((118, 80, 70, 120)[:i]) + i * 10
            if tx + tw > x + w - 10:break
            out += txt(tab, tx, ty, 15, c['dark'] if i == 0 else '#6E7781', 800 if i == 0 else 600)
            if i == 0:out += rect(tx - 4, ty + 9, tw, 3, '#FD8C73', 1)
        out += rect(x + 14, ty + 13, w - 28, 1.5, '#D0D7DE')
        size = min(19, (w - 90) / max(16, max((len(l) for l in lines[1:]), default=16) * .55), (y + h - 70 - ty - 24) / max(1, (len(lines) - 1) * 1.75));ly = ty + 24 + size
        for line, k in rows[1:]:
            if k <= 0:break
            mark = line[:2] if line[:2] in ('+ ', 'x ', '✓ ') else ('@' if line.startswith('@') else '')
            text = line[len(mark):] if mark != '@' else line;shown = text[:max(1, int(len(text) * k))];lx = x + 26
            if mark in ('+ ', 'x ', '✓ '):
                ok = mark != 'x ';col = '#1F883D' if ok else '#CF222E';cx, cy, r = lx + size * .5, ly - size * .35, size * .55
                out += f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{col}"/>'
                out += path(f'M{cx - r * .45:.1f} {cy:.1f}l{r * .32:.1f} {r * .35:.1f}l{r * .6:.1f} -{r * .7:.1f}', '#FFFFFF', 2.4) if ok else path(f'M{cx - r * .4:.1f} {cy - r * .4:.1f}l{r * .8:.1f} {r * .8:.1f}M{cx + r * .4:.1f} {cy - r * .4:.1f}l-{r * .8:.1f} {r * .8:.1f}', '#FFFFFF', 2.4)
                out += txt(shown, lx + size * 1.5, ly, size, c['dark'], 700)
            elif mark == '@':
                who, _, said = shown.partition(':');bw = w - 52;cy0 = ly - size * 1.05
                out += f'<circle cx="{lx + size * .55:.1f}" cy="{ly - size * .2:.1f}" r="{size * .6:.1f}" fill="{c["secondary"]}" stroke="{c["dark"]}" stroke-width="1.5"/>'
                out += rect(lx + size * 1.5, cy0 - size * .15, bw - size * 1.5, size * 1.5, '#F6F8FA', 6, '#D0D7DE', 1.5)
                out += txt(who.lstrip('@'), lx + size * 1.9, ly, size * .9, c['dark'], 900) + txt(said.strip(), lx + size * 1.9 + (len(who.lstrip('@')) + 1.2) * size * .58, ly, size * .9, '#424A53', 600)
                ly += size * .25
            else:
                out += txt(shown, lx, ly, size, '#424A53', 600)
            ly += size * 1.75
        return out

    DAYS = ('MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN')

    @classmethod
    def calendar_events(cls, lines):
        """Parse calendar lines: '# title', 'DAY closed', or 'DAY HH:MM label' (label 'open' = a free slot)."""
        import re
        out = []
        for i, line in enumerate(lines):
            m = re.match(r'^(MON|TUE|WED|THU|FRI|SAT|SUN)\s+(?:(closed)|(\d{1,2}):(\d{2})\s*(.*))$', line.strip(), re.I)
            if not m:continue
            day = m.group(1).upper()
            if m.group(2):out.append((i, day, None, 'closed'))
            else:out.append((i, day, int(m.group(3)) + int(m.group(4)) / 60, (m.group(5) or 'booked').strip()))
        return out

    def calendar_view(self, p, c, typed, done):
        """A week calendar (booking-app reel cut 1 grade: the app was described, never seen; the source
        reel's strongest frames are its calendar). A '# ' line is the header; 'DAY closed' greys a column;
        'DAY HH:MM label' drops an hour block, 'open' an outlined free slot, anything else a booked slot
        in the accent colour. Blocks pop in as their lines type; at the result the last booked one pulses."""
        x, y, w, h = self.screen(p);top = y + 44;lines = p.get('lines') or [];rows = self._shown(lines, typed);out = ''
        events = self.calendar_events(lines)
        head = next((l[2:] for l in lines if l.startswith('# ')), None);hy = top + 10
        if head:
            k = rows[lines.index('# ' + head)][1]
            hs = min(26, (w - 40) / max(8, len(head) * .6))
            out += txt(head[:max(1, int(len(head) * k))] if k > 0 else '', x + 18, top + 10 + hs, hs, c['dark'], 900);hy = top + 22 + hs
        used = {d for _, d, _, _ in events}
        days = [d for d in self.DAYS if d in used or d not in ('SUN',)]
        hours = [hr for _, _, hr, _ in events if hr is not None] or [9.0]
        h0 = max(0, int(min(hours)));h1 = min(24, max(h0 + 4, int(max(hours)) + 1))
        gx = x + 52;gw = x + w - 12 - gx;cw = gw / len(days);dh = 30;gy = hy + dh
        gh = (y + h - 76) - gy;rh = gh / max(1, h1 - h0)
        ds = min(18, cw * .3)
        for j, d in enumerate(days):
            out += txt(d, gx + cw * j + cw / 2, hy + dh * .7, ds, c['dark'], 800, 'middle')
        out += rect(gx, gy, gw, gh, '#FFFFFF', 4, c['metal'], 2)
        for r in range(h1 - h0 + 1):
            ly = gy + r * rh
            out += rect(gx, ly, gw, 1.5, c['metal'])
            if r < h1 - h0:out += txt(f'{(h0 + r - 1) % 12 + 1}{"am" if h0 + r < 12 else "pm"}', gx - 6, ly + min(16, rh * .5), min(15, rh * .45), '#7D7A73', 600, 'end')
        for j in range(1, len(days)):out += rect(gx + cw * j, gy, 1.5, gh, c['metal'])
        booked = [e for e in events if e[3] not in ('open', 'closed')];last = booked[-1][0] if booked else None
        for i, day, hr, label in events:
            k = rows[i][1]
            if k <= 0 or day not in days:continue
            j = days.index(day);bx = gx + cw * j + 3;bw = cw - 6;pop = min(1.0, k * 1.6)
            if label == 'closed':
                hatch = ''.join(path(f'M{bx:.1f} {gy + t:.1f}l{bw:.1f} {-bw:.1f}', c['metal'], 2) for t in range(int(bw), int(gh), 18))
                out += g(rect(bx, gy + 2, bw, gh - 4, '#E4DED2') + self._clip(bx, gy + 2, bw, gh - 4, hatch), 0, 0, 0, 1, 1, pop)
                out += g(txt('CLOSED', 0, 0, min(18, bw * .26), '#7D7A73', 900, 'middle'), bx + bw / 2, gy + gh / 2, -90, pop)
                continue
            by = gy + (hr - h0) * rh + 2;bh = rh - 4;free = label == 'open'
            hot = i == last and done > 0 and c['pop'] not in (c['light'], c['dark'])
            fill = '#FFFFFF' if free else (c['pop'] if hot else c['accent']);fs = min(17, bw / max(4, len(label) * .58), bh * .42)
            blk = rect(0, 0, bw, bh, fill, 6, c['dark'] if not free else c['secondary'], 2.5 if not free else 2)
            col = '#7D7A73' if free else ink(fill, c)
            if bh >= 44:
                blk += txt(f'{int(hr) % 12 or 12}:{int(round(hr % 1 * 60)):02d}', 6, fs * 1.05, fs * .8, col, 700) + txt(label, 6, fs * 2.25, fs, col, 900 if not free else 600)
            else:  # short rows: one line, the name only, as big as the block allows
                fs = min(20, (bw - 10) / max(3, len(label) * .6), bh * .62);blk += txt(label, bw / 2, bh / 2 + fs * .36, fs, col, 900 if not free else 600, 'middle')
            if i == last and done:
                out += rect(bx - 6 - 8 * done, by - 6 - 8 * done, bw + 12 + 16 * done, bh + 12 + 16 * done, 'none', 10, c['pop'], 4).replace('<rect', f'<rect opacity="{max(0, 1 - done * .6):.2f}"')
            out += g(blk, bx + bw / 2 * (1 - pop), by + bh / 2 * (1 - pop), 0, pop)
        return out

    def printed_text(self, p):
        name = (p.get('agent') or self.AGENTS.get(p.get('logo') or '', ('',))[0]) if p['ui'] == 'cli' else None
        return [t for t in [p.get('title'), *(p.get('lines') or []), *(p.get('pane') or []), p.get('cwd'), *(((p.get('stack') or {}).get('title'),) + tuple((p.get('stack') or {}).get('lines') or [])), p.get('result'), p.get('credit'), *(p.get('cards') or []), name] if t]

    # Chrome each view draws besides its lines (title bar, welcome box, input, footer, tabs, pills).
    CHROME = {'cli': 5, 'pr': 7, 'calendar': 4, 'files': 2, 'note': 2, 'chat': 2, 'graph': 1, 'map': 6, 'terminal': 2, 'window': 2, 'browser': 3}

    def detail(self, p):
        """Pieces of UI on the screen: its lines, the open file's lines, the cards and the view's chrome
        (scorecard line screen_detail; reference 09's product screens carry about 10 to 24)."""
        return len(p.get('lines') or []) + len(p.get('pane') or []) + len(p.get('cards') or []) + (1 + len((p.get('stack') or {}).get('lines') or []) if p.get('stack') else 0) + self.CHROME.get(p['ui'], 1) + (1 if p.get('logo') else 0)

    def cards(self, p, c, typed):
        """Collage cards (Claudex cut 4 grade: reference 09 layers tilted paper cards over its screens):
        up to two taped notes overhanging the screen edges, pasted on as the session types."""
        x, y, w, h = self.screen(p);total = max(1, sum(len(l) for l in (p.get('lines') or [])));out = ''
        # On the screen's top and bottom edges, clear of its lines, its mark and the result chip.
        spots = ((x + w * .06, y - 46, -6), (x + w * .04, y + h + 2, 4))
        for i, label in enumerate((p.get('cards') or [])[:2]):
            k = min(1.0, max(0.0, (typed / total - (.35 + .3 * i)) * 6))
            if k <= 0:continue
            cw = len(label) * 17 + 44;cx, cy, ang = spots[i]
            card = (rect(5, 7, cw, 58, '#000000', 6).replace('<rect', '<rect opacity=".2"') + rect(0, 0, cw, 58, '#FFF7E3', 6, c['dark'], 2.5)
                    + rect(cw / 2 - 30, -10, 60, 20, c['accent'], 3).replace('<rect', '<rect opacity=".7"') + txt(label, cw / 2, 39, 28, c['dark'], 900, 'middle'))
            out += g(card, cx, cy, ang * (2 - k), .9 + .1 * k, .9 + .1 * k, k)
        return out

    def stack(self, p, c, typed):
        """A second window pasted behind the screen, offset up and out with its own tilt (plan-to-9 phase 2:
        reference 09 layers the site, a price tag and the bill in one frame). It slides out from behind
        the screen as the session starts typing."""
        st = p.get('stack')
        if not st:return ''
        x, y, w, h = self.screen(p);total = max(1, sum(len(l) for l in (p.get('lines') or [])))
        k = min(1.0, max(0.0, (typed / total - .05) * 5));k = k * k * (3 - 2 * k)
        # Peeking out above the screen's top-right edge, no higher than the gap under the headline strip
        # in a close shot (the host stands bottom right, the cards sit top left and bottom left).
        sw, sh = w * .56, h * .6;sx = x + w * .5;sy = y - 118
        lines = st.get('lines') or [];fs = min(20, (sw - 40) / max(10, max((len(l) for l in lines), default=10) * .56))
        body = rect(6, 8, sw, sh, '#000000', 10).replace('<rect', '<rect opacity=".2"') + rect(0, 0, sw, sh, '#FFFDF7', 10, c['dark'], 3)
        body += rect(0, 0, sw, 34, c['metal'], 10) + rect(0, 26, sw, 8, c['metal'])
        body += ''.join(f'<circle cx="{16 + i * 14}" cy="17" r="4.5" fill="{col}"/>' for i, col in enumerate(('#FF6159', '#FFBD2E', '#28C941')))
        body += txt(st.get('title') or '', 62, 24, 16, c['dark'], 800)
        for i, line in enumerate(lines[:5]):
            head = line.startswith('#');ly = 34 + 14 + fs + i * fs * 1.5
            body += txt(line.lstrip('# ') if head else line, 16, ly, fs * (1.1 if head else 1), c['dark'], 900 if head else 600)
        return g(body, sx - (1 - k) * sw * .4, sy + (1 - k) * 100, 4 - 3 * (1 - k), .85 + .15 * k, 1, min(1.0, k * 1.5))

    def chat_view(self, p, c, typed, done):
        """An assistant chat: the first line is the question (right bubble), the rest the answer (left),
        where [n] becomes a citation chip."""
        import re
        x, y, w, h = self.screen(p);top = y + 44;lines = p.get('lines') or [];rows = self._shown(lines, typed)
        size = min(26, (w * .7) / max(14, max((len(l) for l in lines), default=14) * .56));out = ''
        if rows and rows[0][1] > 0:
            q = rows[0][0];qw = min(w - 40, len(q) * size * .56 + 34)
            out += rect(x + w - 20 - qw, top + 18, qw, size * 1.9, c['secondary'], 16) + txt(q[:max(1, int(len(q) * rows[0][1]))], x + w - 20 - qw + 17, top + 18 + size * 1.28, size, ink(c['secondary'], c), 700)
        ay = top + 40 + size * 2.4
        if len(rows) > 1 and rows[1][1] > 0:
            aw = w * .8;ah = (len(rows) - 1) * size * 1.6 + 26
            out += rect(x + 20, ay - 10, aw, ah, '#FFFFFF', 16, c['dark'], 2)
        for i, (line, k) in enumerate(rows[1:]):
            if k <= 0:break
            ly = ay + 16 + size * .8 + i * size * 1.6;lx = x + 36
            for part in re.split(r'(\[\d+\])', line[:max(1, int(len(line) * k))]):
                if not part:continue
                if re.fullmatch(r'\[\d+\]', part):
                    out += f'<circle cx="{lx + size * .5:.1f}" cy="{ly - size * .32:.1f}" r="{size * .5:.1f}" fill="{c["pop"]}" stroke="{c["dark"]}" stroke-width="2"/>' + txt(part[1:-1], lx + size * .5, ly - size * .32 + size * .3, size * .7, c['dark'], 900, 'middle')
                    lx += size * 1.2
                else:
                    out += txt(part, lx, ly, size, c['dark'], 600);lx += len(part) * size * .58
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
        total = sum(len(l) for l in (p.get('lines') or []) + (p.get('pane') or []))
        # The screen is already full on the first frame and finishes fast (cut 5 review: the terminal
        # read "> cd sec" and the chat sat half blank for most of their shots). A chat's answer is the
        # result, so it appears only after the question is sent.
        lines = p.get('lines') or []
        if action and p['ui'] == 'chat' and lines:
            q = len(lines[0]);typed = q * min(1.0, .5 + t / max(1e-6, tc)) if t < tc else q + (total - q) * min(1.0, t_after(t, tc) * 4)
        elif action and p['ui'] in ('cli', 'pr', 'files', 'terminal'):
            # Dense screens keep typing up to the contact so the software moves all through the shot (plan-to-9 phase 1).
            typed = total * min(1.0, .3 + .7 * t / max(1e-6, tc))
        elif action:typed = total * min(1.0, .4 + .6 * t / max(1e-6, tc * .6))
        if action:done = 0.0 if t < tc else min(1.0, .55 + .45 * ease(t_after(t, tc) * 3)) + settle(t_after(t, tc), .08)
        else:typed, done = (total, 1.0) if start == 'done' else (0, 0.0)
        if p.get('prefilled'):typed = total
        body = self.stack(p, c, typed) + self.device(p, c) + self.ui(p, c, typed, done) + self.cards(p, c, typed)
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
    name='app-screen', description='The product in use: a monitor, laptop or phone showing a Motif-drawn terminal, coding-agent session (cli: > prompt, * action, - result, + / x diff, [ ] / [x] todo, ? permission), pull request (pr: title, then ✓ / x checks and @name: comments), file tree (files, with pane = the open file), week calendar (calendar: # header, DAY closed, DAY HH:MM name booked or open slots), stack = a second window pasted behind, app window, browser page or street map (lines become map pins); the brief\'s lines type in, the cursor presses run and the result pops. send_to puts a USB stick in front and the file flies into it; credit adds a corner attribution; prefilled starts with the lines already in. Demos, commands, settings, checkboxes, downloads.',
    params_schema={'type': 'object', 'properties': {
        'device': {'enum': ['monitor', 'laptop', 'phone']}, 'ui': {'enum': ['terminal', 'window', 'browser', 'map', 'files', 'note', 'graph', 'chat', 'cli', 'pr', 'calendar']},
        'stack': {'type': ['object', 'null'], 'properties': {'title': {'type': 'string', 'maxLength': 20}, 'lines': {'type': 'array', 'items': {'type': 'string', 'maxLength': 30}, 'maxItems': 5}}, 'additionalProperties': False},
        'pane': {'type': 'array', 'items': {'type': 'string', 'maxLength': 34}, 'maxItems': 10}, 'cwd': {'type': ['string', 'null'], 'maxLength': 24},
        'agent': {'type': ['string', 'null'], 'maxLength': 16}, 'cards': {'type': 'array', 'items': {'type': 'string', 'maxLength': 18}, 'maxItems': 2},
        'title': {'type': 'string', 'maxLength': 26}, 'lines': {'type': 'array', 'items': {'type': 'string', 'maxLength': 34}, 'minItems': 1, 'maxItems': 12},
        'result': {'type': 'string', 'maxLength': 14}, 'button': {'type': ['string', 'null'], 'maxLength': 8}, 'logo': {'type': ['string', 'null']},
        'send_to': {'type': ['string', 'null'], 'maxLength': 6}, 'credit': {'type': ['string', 'null'], 'maxLength': 34}, 'prefilled': {'type': 'boolean'}},
        'required': ['device', 'ui', 'lines'], 'additionalProperties': False},
    defaults={'device': 'monitor', 'ui': 'terminal', 'title': 'Terminal', 'lines': ['run the thing'], 'result': 'DONE', 'button': None, 'logo': None, 'send_to': None, 'credit': None, 'prefilled': False, 'agent': None, 'cards': [], 'pane': [], 'cwd': None, 'stack': None},
    states=('idle', 'done'),
    actions={'run': Action('run', 'idle', 'done', 60, 'cursor-press', 30)},
    bot_slot={'x': 300, 'y': 0, 'scale': .24, 'role': 'watches the screen and reacts to the result'},
    tags=('demo', 'screen', 'app', 'terminal', 'command', 'install', 'download', 'checkbox', 'setting', 'browser', 'website', 'click'),
    footprint=(-300, -680, 600, 680)))
