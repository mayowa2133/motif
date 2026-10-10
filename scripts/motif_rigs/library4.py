"""Rigs added after the v11 story review (2026-10-10).

The review of the Blender reel found that "Cycles traces real light, like a
real camera" was shown with a balance scale and stars: nothing in the frame
showed light producing an image. LightRender draws that claim directly: a
studio lamp shines on an object on a small stage, rays leave the lamp, bounce
off the object and enter a camera's lens, and each ray lands on one tile of the
camera's screen, which fills in with the picture of that same object, tile by
tile, out of render noise. At the contact frame the last ray lands on the last
tile, the picture is complete and the result label pops.

Same contract as library.py: original authored SVG through palette roles, the
local origin is the floor under the rig's centre, and the contact closes
exactly at its contact frame.
"""
import math

from motif_rigs import register
from motif_rigs.base import Action, Rig, ease, lerp
from motif_rigs.library import label_size, settle, t_after
from motif_rigs.library2 import burst
from motif_ui_components import g, path, rect, txt

RAY = '#FFD84A'      # warm lamp light; drawn with an ink outline so it reads in every palette
GLOW = '#FFF1B0'


class LightRender(Rig):
    """Lamp -> object -> lens -> screen tile: light rays build the rendered picture."""
    COLS, ROWS, TILE = 4, 3, 58
    SCREEN = (22, -676)                 # top-left of the camera screen
    LENS = (-70, -556)                  # mouth of the lens, facing the stage
    SUBJECT = (-128, -318)              # centre of the object on the stage
    R = 58                              # object radius
    LAMP = (-240, -660)                 # lamp head pivot
    TRAVEL = .17                        # one ray's flight time (share of the action)

    # Geometry ----------------------------------------------------------------

    def tiles(self):
        """Tile rects (x, y, w, h) in render order: row by row, top-left first."""
        sx, sy = self.SCREEN;s = self.TILE
        return [(sx + col * s, sy + row * s, s, s) for row in range(self.ROWS) for col in range(self.COLS)]

    def lamp_aim(self):
        lx, ly = self.LAMP;bx, by = self.SUBJECT
        return math.atan2(by - self.R * .6 - ly, bx - lx)

    def lamp_mouth(self):
        a = self.lamp_aim();lx, ly = self.LAMP
        return (lx + 56 * math.cos(a), ly + 56 * math.sin(a))

    def hit(self, k):
        """Where ray k strikes the object: across its lit top surface."""
        n = len(self.tiles());f = ((k * 5) % n) / max(1, n - 1)       # scatter so neighbouring rays use different spots
        a = math.radians(lerp(-160, -35, f));bx, by = self.SUBJECT
        return (bx + self.R * .92 * math.cos(a), by + self.R * .8 * math.sin(a))

    def route(self, k):
        x, y, w, h = self.tiles()[k]
        return [self.lamp_mouth(), self.hit(k), self.LENS, (x + w / 2, y + h / 2)]

    def arrival(self, k, tc):
        """Time ray k lands on its tile; the last one lands exactly at the contact."""
        n = len(self.tiles());first = tc * .32
        return tc if k == n - 1 else first + (tc - first) * k / (n - 1)

    def progress(self, k, t, tc):
        a = self.arrival(k, tc)
        if t >= a:return 1.0
        return max(0.0, (t - (a - self.TRAVEL)) / self.TRAVEL)

    @staticmethod
    def along(pts, u):
        """Point at arc-length fraction u of a polyline (exact endpoints)."""
        if u <= 0:return pts[0]
        if u >= 1:return pts[-1]
        segs = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:])];d = u * sum(segs)
        for (a, b), L in zip(zip(pts, pts[1:]), segs):
            if d <= L:f = d / L if L else 0;return (lerp(a[0], b[0], f), lerp(a[1], b[1], f))
            d -= L
        return pts[-1]

    def sub_path(self, pts, u0, u1, steps=18):
        return [self.along(pts, lerp(u0, u1, i / steps)) for i in range(steps + 1)] + [self.along(pts, u1)]

    # Pieces -------------------------------------------------------------------

    def subject(self, kind, c, r, lit=1.0):
        """The object, centred on (0, 0), lit from the upper left."""
        d = c['dark'];body = c['primary'];out = ''
        shade = f'opacity="{.24 * lit:.3f}"'
        if kind == 'ball':
            out += f'<circle cx="0" cy="0" r="{r:.1f}" fill="{body}" stroke="{d}" stroke-width="{max(2, r * .06):.1f}"/>'
            out += path(f'M{r * .55:.1f} {-r * .8:.1f}A{r:.1f} {r:.1f} 0 0 1 {-r * .8:.1f} {r * .58:.1f}A{r * 1.15:.1f} {r * 1.15:.1f} 0 0 0 {r * .55:.1f} {-r * .8:.1f}Z', d, 0, d, shade)
            out += f'<ellipse cx="{-r * .36:.1f}" cy="{-r * .38:.1f}" rx="{r * .26:.1f}" ry="{r * .16:.1f}" fill="#FFFFFF" opacity="{.75 * lit:.3f}" transform="rotate(-35 {-r * .36:.1f} {-r * .38:.1f})"/>'
            out += path(f'M{-r * .98:.1f} 0Q0 {r * .32:.1f} {r * .98:.1f} 0', d, max(1.5, r * .035), extra='opacity=".35"')
        elif kind == 'cube':
            s = r * .9;dx, dy = s * .55, s * .45
            front = f'M{-s:.1f} {-s + dy:.1f}H{s - dx:.1f}V{s:.1f}H{-s:.1f}Z'
            top = f'M{-s:.1f} {-s + dy:.1f}L{-s + dx:.1f} {-s:.1f}H{s:.1f}L{s - dx:.1f} {-s + dy:.1f}Z'
            side = f'M{s - dx:.1f} {-s + dy:.1f}L{s:.1f} {-s:.1f}V{s - dy:.1f}L{s - dx:.1f} {s:.1f}Z'
            sw = max(2, r * .06)
            out += path(front, d, sw, body) + path(top, d, sw, body) + path(side, d, sw, body)
            out += path(top, d, 0, '#FFFFFF', f'opacity="{.38 * lit:.3f}"') + path(side, d, 0, d, f'opacity="{.3 * lit:.3f}"')
            out += path(f'M{-s * .8:.1f} {-s * .3:.1f}V{s * .5:.1f}', '#FFFFFF', max(2, r * .07), extra=f'opacity="{.4 * lit:.3f}"')
        else:  # teapot
            sw = max(2, r * .06)
            out += path(f'M{r * .78:.1f} {-r * .05:.1f}Q{r * 1.18:.1f} {-r * .05:.1f} {r * 1.3:.1f} {-r * .62:.1f}L{r * 1.42:.1f} {-r * .6:.1f}Q{r * 1.3:.1f} {r * .3:.1f} {r * .7:.1f} {r * .32:.1f}Z', d, sw, body)
            out += path(f'M{-r * .8:.1f} {-r * .32:.1f}Q{-r * 1.38:.1f} {-r * .42:.1f} {-r * 1.22:.1f} {r * .1:.1f}Q{-r * 1.08:.1f} {r * .42:.1f} {-r * .78:.1f} {r * .36:.1f}', d, r * .2)
            out += path(f'M{-r * .8:.1f} {-r * .32:.1f}Q{-r * 1.38:.1f} {-r * .42:.1f} {-r * 1.22:.1f} {r * .1:.1f}Q{-r * 1.08:.1f} {r * .42:.1f} {-r * .78:.1f} {r * .36:.1f}', body, r * .1)
            out += f'<ellipse cx="0" cy="{r * .1:.1f}" rx="{r * .95:.1f}" ry="{r * .7:.1f}" fill="{body}" stroke="{d}" stroke-width="{sw:.1f}"/>'
            out += path(f'M{r * .7:.1f} {-r * .3:.1f}A{r * .95:.1f} {r * .7:.1f} 0 0 1 {-r * .55:.1f} {r * .67:.1f}A{r * 1.05:.1f} {r * .8:.1f} 0 0 0 {r * .7:.1f} {-r * .3:.1f}Z', d, 0, d, shade)
            out += path(f'M{-r * .55:.1f} {-r * .5:.1f}Q0 {-r * 1.05:.1f} {r * .55:.1f} {-r * .5:.1f}Z', d, sw, body)
            out += rect(-r * .66, -r * .58, r * 1.32, r * .16, c['metal'], r * .08, d, sw * .8)
            out += f'<circle cx="0" cy="{-r * .86:.1f}" r="{r * .14:.1f}" fill="{c["accent"]}" stroke="{d}" stroke-width="{sw * .8:.1f}"/>'
            out += f'<ellipse cx="{-r * .42:.1f}" cy="{-r * .12:.1f}" rx="{r * .22:.1f}" ry="{r * .12:.1f}" fill="#FFFFFF" opacity="{.7 * lit:.3f}" transform="rotate(-30 {-r * .42:.1f} {-r * .12:.1f})"/>'
        return out

    def picture(self, p, c):
        """The rendered image: the same object, stage and lamp light, at screen scale."""
        sx, sy = self.SCREEN;w, h = self.COLS * self.TILE, self.ROWS * self.TILE
        out = rect(sx, sy, w, h, c['light']) + rect(sx, sy + h * .7, w, h * .3, c['secondary'])
        out += path(f'M{sx:.1f} {sy + h * .7:.1f}H{sx + w:.1f}', c['dark'], 2.5, extra='opacity=".5"')
        out += f'<path d="M{sx:.1f} {sy:.1f}L{sx + w * .55:.1f} {sy:.1f}L{sx + w * .78:.1f} {sy + h:.1f}L{sx:.1f} {sy + h:.1f}Z" fill="{GLOW}" opacity=".45"/>'
        cx, cy = sx + w * .5, sy + h * .5;r = h * .3
        out += f'<ellipse cx="{cx + r * .5:.1f}" cy="{cy + r * 1.08:.1f}" rx="{r * 1.2:.1f}" ry="{r * .2:.1f}" fill="{c["dark"]}" opacity=".25"/>'
        out += g(self.subject(p['subject'], c, r), cx, cy)
        return out

    def noise(self, x, y, w, h, k, c, phase):
        """An unrendered tile: dark render noise, re-seeded every few frames."""
        out = rect(x, y, w, h, c['dark']);n = 5;s = w / n
        for i in range(n):
            for j in range(n):
                v = (i * 7 + j * 13 + k * 29 + phase * 17) % 11
                if v < 5:out += rect(x + i * s + 1, y + j * s + 1, s - 2, s - 2, (c['metal'], c['light'], c['primary'], c['metal'], c['secondary'])[v], 1).replace('<rect', f'<rect opacity="{.18 + .06 * (v % 3):.2f}"')
        return out

    def lamp(self, c, on):
        d = c['dark'];lx, ly = self.LAMP;a = math.degrees(self.lamp_aim())
        out = rect(-280, -14, 70, 14, c['metal'], 6, d, 3)                                            # foot
        out += path(f'M-246 -14L{lx:.1f} {ly + 40:.1f}', d, 14) + path(f'M-246 -14L{lx:.1f} {ly + 40:.1f}', c['metal'], 8)
        out += rect(-253, -330, 20, 34, c['metal'], 5, d, 3)                                          # height clamp
        out += path(f'M-240 -20Q-200 -10 -170 -4', d, 4, extra='opacity=".55"')                        # cable
        out += path(f'M{lx - 22:.1f} {ly + 48:.1f}L{lx:.1f} {ly:.1f}L{lx + 22:.1f} {ly + 48:.1f}', d, 6) # yoke
        head = rect(-50, -34, 84, 68, c['primary'], 14, d, 4) + rect(-58, -22, 12, 44, c['metal'], 4, d, 3)
        head += rect(30, -42, 16, 84, c['metal'], 5, d, 3)                                             # front rim
        head += path('M46 -42L70 -60M46 42L70 60', d, 5) + path('M46 -42L70 -60M46 42L70 60', c['metal'], 2)   # barn doors
        head += path('M-40 -24H18', '#FFFFFF', 5, extra='opacity=".35"')
        for vx in (-32, -18, -4):head += path(f'M{vx} 10V26', d, 3, extra='opacity=".5"')       # vents
        head += f'<ellipse cx="46" cy="0" rx="9" ry="32" fill="{GLOW if on > .5 else c["metal"]}" stroke="{d}" stroke-width="3"/>'
        out += g(head, lx, ly, a, 1.2)
        out += f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="9" fill="{c["metal"]}" stroke="{d}" stroke-width="3"/>'
        return out

    def stage(self, p, c, on):
        d = c['dark'];bx, by = self.SUBJECT;top = by + self.R * (.8 if p['subject'] != 'cube' else .9) + 2
        out = rect(-206, top + 4, 196, 26, c['secondary'], 8, d, 3) + rect(-196, top + 30, 176, 10, d, 4).replace('<rect', '<rect opacity=".2"')
        for lx_ in (-190, -44):out += rect(lx_, top + 30, 16, -top - 30, c['metal'], 4, d, 3)
        out += rect(-186, -110, 150, 12, c['metal'], 4, d, 3)
        out += f'<ellipse cx="{bx + 22:.1f}" cy="{top + 4:.1f}" rx="{self.R * 1.05:.1f}" ry="9" fill="{d}" opacity="{.12 + .16 * on:.3f}"/>'
        out += g(self.subject(p['subject'], c, self.R, on), bx, by)
        return out

    def camera(self, p, c, rec):
        d = c['dark'];sx, sy = self.SCREEN;w, h = self.COLS * self.TILE, self.ROWS * self.TILE
        out = ''
        # Tripod: three legs and a centre column under the body.
        for fx in (52, 140, 232):out += path(f'M140 -404L{fx} -6', d, 14) + path(f'M140 -404L{fx} -6', c['metal'], 8)
        out += rect(126, -420, 28, 160, c['metal'], 5, d, 3) + rect(110, -268, 60, 14, c['metal'], 5, d, 3)
        # Body with a viewfinder hump, grip and rivets.
        out += rect(-10, -704, 290, 300, d, 28).replace('<rect', '<rect opacity=".18" transform="translate(8 9)"')
        out += rect(70, -730, 120, 40, c['secondary'], 10, d, 4)
        out += rect(-4, -708, 284, 300, c['secondary'], 26, d, 4)
        out += rect(6, -698, 18, 280, '#FFFFFF', 9).replace('<rect', '<rect opacity=".22"')
        out += rect(214, -730, 44, 22, c['accent'], 8, d, 3)                                          # shutter key
        out += f'<circle cx="40" cy="-718" r="8" fill="{c["pop"] if rec else c["metal"]}" stroke="{d}" stroke-width="3"/>'
        # Lens barrel out of the left side, facing the stage.
        lx, ly = self.LENS
        out += rect(lx + 4, ly - 46, 74, 92, c['metal'], 10, d, 4) + rect(lx + 20, ly - 52, 14, 104, d, 4) + rect(lx + 48, ly - 50, 10, 100, d, 3)
        out += path(f'M{lx + 10} {ly - 36}H{lx + 70}', '#FFFFFF', 4, extra='opacity=".4"')
        out += f'<ellipse cx="{lx + 2}" cy="{ly}" rx="12" ry="42" fill="{c["light"]}" stroke="{d}" stroke-width="4"/>'
        out += f'<ellipse cx="{lx + 2}" cy="{ly}" rx="6" ry="26" fill="{c["metal"]}" opacity=".6"/>'
        # Screen bezel and plate for the engine name.
        out += rect(sx - 12, sy - 12, w + 24, h + 24, d, 12)
        bw = w + 24;out += rect(sx - 12, sy + h + 22, bw, 54, c['light'], 10, d, 3)
        out += txt(p['label'], sx - 12 + bw / 2, sy + h + 22 + 27 + label_size(p['label'], bw - 24, 34) * .36, label_size(p['label'], bw - 24, 34), d, 900, 'middle')
        for rx_ in (6, 270):
            for ry_ in (-690, -428):out += f'<circle cx="{rx_}" cy="{ry_}" r="5" fill="{c["metal"]}" stroke="{d}" stroke-width="2.5"/>'
        return out

    def ray(self, pts, u, c):
        """One ray in flight: a faint route, then a bright ink-outlined streak with a glowing tip."""
        route = ' '.join(f'{"M" if i == 0 else "L"}{x:.1f} {y:.1f}' for i, (x, y) in enumerate(pts))
        out = path(route, RAY, 3, extra='opacity=".35" stroke-dasharray="6 10"')
        seg = self.sub_path(pts, max(0.0, u - .22), u)
        d = ' '.join(f'{"M" if i == 0 else "L"}{x:.1f} {y:.1f}' for i, (x, y) in enumerate(seg))
        out += path(d, c['dark'], 17) + path(d, RAY, 10) + path(d, '#FFFFFF', 3, extra='opacity=".8"')
        tx, ty = seg[-1]
        out += f'<circle cx="{tx:.1f}" cy="{ty:.1f}" r="18" fill="{GLOW}" opacity=".6"/><circle cx="{tx:.1f}" cy="{ty:.1f}" r="9" fill="{RAY}" stroke="{c["dark"]}" stroke-width="3"/>'
        return out

    @staticmethod
    def spark(x, y, r, c, o):
        d = f'M{x} {y - r}Q{x + r * .2} {y - r * .2} {x + r} {y}Q{x + r * .2} {y + r * .2} {x} {y + r}Q{x - r * .2} {y + r * .2} {x - r} {y}Q{x - r * .2} {y - r * .2} {x} {y - r}Z'
        return path(d, c['dark'], 2.5, RAY, f'opacity="{o:.3f}"')

    # Rig interface -----------------------------------------------------------

    def draw(self, p, pose, c):
        start, end, action, t = pose;tc = self.contact_t('trace');tiles = self.tiles();n = len(tiles)
        if not action:t = 1.0 if start == 'done' else 0.0
        on = 0.0 if not action and start == 'idle' else (min(1.0, t / .06) if action else 1.0)
        after = t_after(t, tc) if action else (1.0 if start == 'done' else 0.0)
        body = ''
        # Light cone from the lamp across the stage.
        if on > 0:
            mx, my = self.lamp_mouth();bx, by = self.SUBJECT;a = self.lamp_aim();nx, ny = -math.sin(a), math.cos(a)
            top = by + self.R * .8 + 6
            body += f'<path d="M{mx + nx * 30:.1f} {my + ny * 30:.1f}L{bx + 112:.1f} {top:.1f}L{bx - 100:.1f} {top:.1f}L{mx - nx * 30:.1f} {my - ny * 30:.1f}Z" fill="{GLOW}" opacity="{.45 * on:.3f}"/>'
            body += f'<ellipse cx="{bx + 6:.1f}" cy="{top + 2:.1f}" rx="106" ry="12" fill="{GLOW}" opacity="{.6 * on:.3f}"/>'
        body += self.lamp(c, on) + self.stage(p, c, on)
        rendering = action is not None and t < tc
        body += self.camera(p, c, rendering and int(t * 40) % 2 == 0)
        # Screen: the finished picture under the tiles that are still noise.
        phase = int(t * 24);body += self.picture(p, c)
        for k, (x, y, w, h) in enumerate(tiles):
            u = self.progress(k, t, tc) if action else (1.0 if start == 'done' else 0.0)
            if u < 1:
                body += self.noise(x, y, w, h, k, c, phase)
                if u > 0:body += rect(x + 3, y + 3, w - 6, h - 6, 'none', 3, RAY, 3)            # bucket being traced
            elif action:
                since = (t - self.arrival(k, tc)) / .08
                if since < 1:body += rect(x, y, w, h, GLOW).replace('<rect', f'<rect opacity="{.85 * (1 - since):.3f}"')
        sx, sy = self.SCREEN;W, H = self.COLS * self.TILE, self.ROWS * self.TILE
        for col in range(1, self.COLS):body += path(f'M{sx + col * self.TILE} {sy}V{sy + H}', c['dark'], 1.5, extra=f'opacity="{.25 * (1 - after):.3f}"')
        for row in range(1, self.ROWS):body += path(f'M{sx} {sy + row * self.TILE}H{sx + W}', c['dark'], 1.5, extra=f'opacity="{.25 * (1 - after):.3f}"')
        # Rays in flight, with a spark where each one bounces off the object.
        if action:
            for k in range(n):
                u = self.progress(k, t, tc)
                if 0 < u < 1:
                    pts = self.route(k);body += self.ray(pts, u, c)
                    segs = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:])];uh = segs[0] / sum(segs)
                    if uh < u < uh + .12:hx, hy = pts[1];body += self.spark(hx, hy, 22 * (1 - (u - uh) / .12) + 6, c, 1 - (u - uh) / .12)
        # Payoff: the result label pops on the finished picture.
        if after > 0:
            pop = min(1.0, .55 + .45 * ease(after * 3)) + settle(after, .08)
            res = p['result'];rw = max(180, len(res) * 22 + 44);size = label_size(res, rw - 24, 32)
            fill = c['pop'] if c['pop'] != c['light'] else c['accent']
            card_ = rect(-rw / 2 + 5, -30, rw, 60, c['dark'], 12).replace('<rect', '<rect opacity=".25"') + rect(-rw / 2, -34, rw, 60, fill, 12, c['dark'], 3)
            from motif_rigs.library import ink
            card_ += txt(res, 0, -4 + size * .36, size, ink(fill, c), 900, 'middle')
            body += g(card_, sx + W / 2, sy + H - 6, -4, pop)
            if action:body += burst(sx + W - 10, sy + 10, after * 1.6, c, 8, 26, 90)
        return body

    def seams(self, p, pose):
        start, end, action, t = pose;tc = self.contact_t('trace');k = len(self.tiles()) - 1
        if not action:t = 1.0 if start == 'done' else 0.0
        x, y, w, h = self.tiles()[k]
        return {'ray-tile': (self.along(self.route(k), self.progress(k, t, tc) if action else (1.0 if start == 'done' else 0.0)), (x + w / 2, y + h / 2))}


register(LightRender(
    name='light-render', description='A studio lamp shines on an object on a small stage; light rays bounce off it into a camera lens and each ray fills one tile of the camera screen until the rendered picture is complete. Ray tracing, rendering, real light, like a real camera, photo-real images.',
    params_schema={'type': 'object', 'properties': {
        'label': {'type': 'string', 'maxLength': 14}, 'result': {'type': 'string', 'maxLength': 14},
        'subject': {'enum': ['teapot', 'ball', 'cube']}},
        'required': ['label', 'result'], 'additionalProperties': False},
    defaults={'label': 'CYCLES', 'result': 'REAL LIGHT', 'subject': 'teapot'},
    states=('idle', 'done'),
    actions={'trace': Action('trace', 'idle', 'done', 72, 'ray-tile', 54)},
    bot_slot={'x': 300, 'y': 0, 'scale': .24, 'role': 'stands by the camera and watches the picture fill in'},
    tags=('render', 'rendering', 'light', 'ray', 'rays', 'camera', 'photo', 'image', 'picture', 'realistic', '3d', 'engine', 'blender', 'cycles', 'graphics'),
    footprint=(-290, -740, 580, 740)))
