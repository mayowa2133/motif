"""Review loop: two workstations that check each other's work, one carried film object.

Built for the second reel adaptation (2026-10-11): a reel about a skill that
puts two AI models on one task, one writing and one auditing, then swapping
roles. The library had a stamp (approve) but nothing where a piece of work
travels between two parties, collects objections and comes back better, so
this machine keeps two desks on screen, each under its maker's badge, with one
PLAN sheet and one build that every beat changes:

  solo    one desk alone plans, builds a block tower and stamps its own work
          with a gold A+ star; then bugs crawl out of the tower. Contact: the
          star meets the tower.
  plan    the left desk writes the steps onto the PLAN sheet, then the sheet
          flies across and lands on the right desk. Contact: the sheet meets
          the right stand.
  audit   the right desk's red pen strikes rows and red objection tabs slap
          onto the sheet's edge. Contact: the last tab meets its slot.
  loop    the sheet flies back and forth; each trip a tab peels off and its
          row turns into a green tick while the ROUND counter rises, until a
          stamp lands HOLDS UP. Contact: the stamp meets the sheet.
  swap    the old role tags drop off both signs and new ones slap on (the
          planner becomes the auditor, the auditor the builder). Contact: the
          second tag meets its hook.
  build   blocks named after the plan's steps fly from the right desk onto a
          tower; the left desk's magnifier finds a bug in one, it is knocked
          out and a fixed block drops in. Contact: the fixed block seats.
  ship    both badges fire a seal onto the finished tower. Contact: the
          second seal lands.

Every mode starts where the previous one ends, so consecutive beats read as
one continuing machine (lesson L008). Original authored SVG through palette
roles; no reference frame was traced or copied (style inputs:
docs/STYLE_BIBLE.md, docs/style-reference-analysis.md). Status: DRAFT.
"""
import math

from motif_rigs import register
from motif_rigs.base import Action, Rig, ease, ease_in, lerp
from motif_rigs.library import ink, label_size, settle, t_after, t_in
from motif_rigs.library2 import burst
from motif_rigs.library5 import WARN, clamp, mix
from motif_ui_components import card, g, path, rect, txt

GREEN = '#2FA36B'          # semantic "passed" green, the same in every palette
GOLD = '#F2B829'
MAX_STEPS = 5


def seg(u, a, b):
    return clamp((u - a) / max(1e-9, b - a))


def arc(p0, p1, k, lift=150):
    """Point along a thrown arc from p0 to p1 (k in [0, 1])."""
    x = lerp(p0[0], p1[0], ease(k) if k < 1 else 1);y = lerp(p0[1], p1[1], k) - lift * math.sin(math.pi * k)
    return x, y


class ReviewLoop(Rig):
    DESK_X = 200
    DESK_TOP = -232
    SHEET = (200, 262)                 # w, h
    SHEET_Y = -385                     # sheet centre on its stand
    TAG_Y = -594
    PLATE_Y = -628
    BADGE_Y = -716
    COUNTER = (0, -700)
    BLOCK = (144, 64)
    SOLO_DESK = -170
    SOLO_TOWER = 150

    # Geometry -----------------------------------------------------------------

    def sheet_at(self, side):
        return (side * self.DESK_X, self.SHEET_Y)

    def row_y(self, i, n):
        return self.SHEET_Y - self.SHEET[1] / 2 + 78 + i * min(40, 176 / max(1, n))

    def tab_slot(self, side, j):
        """Where the j-th objection tab sticks out of a sheet on `side` (toward the middle)."""
        sx, sy = self.sheet_at(side)
        return sx - side * (self.SHEET[0] / 2 + 62), sy - 74 + j * 58

    def focus(self, p, role):
        # The setup eases in on the station doing the work: Astra's desk tabbing the plan, the
        # tower Astra builds. The payoff cuts back wide for the result.
        spots = {'audit': (self.DESK_X - 60, self.SHEET_Y), 'build': (80, -260)}
        return spots.get(p['mode']) if role == 'setup' else None

    def block_slot(self, i, x=0):
        return x, -self.BLOCK[1] / 2 - 4 - i * (self.BLOCK[1] + 4)

    def timeline(self, pose):
        start, end, action, t = pose;tc = self.contact_t('run')
        if not action:t = 1.0 if start == 'done' else 0.0
        return t, tc, t_in(t, tc) if t <= tc else 1.0, t_after(t, tc)

    # Parts ----------------------------------------------------------------------

    def desk(self, x, c, w=220):
        d = c['dark'];top = c['secondary'] if c['secondary'] not in (c['wall'], c['light']) else c['primary']
        y = self.DESK_TOP;out = g(rect(x - w / 2, y, w, -y, d, 8), 6, 8, opacity=.14)
        for lx in (x - w / 2 + 16, x + w / 2 - 34):out += rect(lx, y + 20, 18, -y - 20, c['metal'], 3, d, 2.5)
        out += rect(x - w / 2 + 30, y + 26, w - 60, 70, mix(top, d, .22), 6, d, 3)
        out += rect(x - 26, y + 56, 52, 10, c['metal'], 4, d, 2)
        out += rect(x - w / 2, y, w, 30, top, 7, d, 3.5) + g(rect(x - w / 2 + 10, y + 5, w * .55, 5, '#FFFFFF', 3), opacity=.3)
        mx = x + (w / 2 - 34) * (1 if x > 0 else -1)
        out += rect(mx - 15, y - 36, 30, 36, c['pop'] if c['pop'] not in (c['light'],) else c['accent'], 5, d, 2.5) + path(f'M{mx + 15} {y - 28}q12 2 0 16', d, 3)
        out += path(f'M{mx - 6} {y - 46}q-5 -8 0 -14M{mx + 5} {y - 46}q-5 -8 0 -14', d, 2.5, extra='opacity=".35"')
        # The sheet stand: a slanted clipboard easel.
        out += path(f'M{x - 40} {y}L{x - 18} {self.SHEET_Y + 60}M{x + 40} {y}L{x + 18} {self.SHEET_Y + 60}', d, 9) + path(f'M{x - 40} {y}L{x - 18} {self.SHEET_Y + 60}M{x + 40} {y}L{x + 18} {self.SHEET_Y + 60}', c['metal'], 5)
        return out

    def sign(self, x, c, logo, name, tag, tag_k=1.0, tag_drop=0.0, old_tag=None, bob=0.0):
        """Post, brand badge, name plate and the hanging role tag."""
        d = c['dark'];out = rect(x - 6, self.BADGE_Y, 12, self.DESK_TOP - self.BADGE_Y - 120, c['metal'], 3, d, 2.5)
        out += self.tag(x, c, old_tag, 1.0, tag_drop) if old_tag and tag_drop < 1 else ''
        if tag and tag_k > 0:out += self.tag(x, c, tag, tag_k, 0.0)
        w = max(150, len(name) * 22 + 40)
        out += g(card(w, 46, d, .05) + txt(name, w / 2, 33, label_size(name, w - 24, 30), c['light'], 900, 'middle'), x - w / 2, self.PLATE_Y - 23)
        out += g(self.badge(logo, c), x, self.BADGE_Y + bob)
        return out

    def badge(self, logo, c, r=62):
        if logo:
            from motif_brand import badge
            return badge(logo, 2 * r, c, title=False)
        d = c['dark']
        out = f'<circle cx="7" cy="10" r="{r}" fill="#000" opacity=".18"/><circle r="{r}" fill="{c["light"]}" stroke="{d}" stroke-width="4"/>'
        out += rect(-34, -24, 68, 48, d, 12) + f'<circle cx="-14" cy="0" r="8" fill="{c["accent"]}"/><circle cx="14" cy="0" r="8" fill="{c["accent"]}"/>'
        out += rect(-4, -r + 2, 8, 18, d, 3) + f'<circle cy="{-r + 2}" r="8" fill="{c["pop"]}" stroke="{d}" stroke-width="3"/>'
        return out

    def tag(self, x, c, text, k, drop):
        """A role tag on two strings; k drops it in and slaps it on, drop lets it fall away."""
        d = c['dark'];fill = c['pop'] if c['pop'] not in (c['light'], c['dark']) else c['accent'];w = max(140, len(text) * 20 + 36);h = 44
        dy = -230 * (1 - ease_in(clamp(k))) + 380 * ease_in(drop);ang = -4 + 40 * drop + (6 * settle(clamp((k - .999) * 1000), 1) if k >= 1 else 0)
        body = path(f'M{-w / 2 + 18} {-h / 2}L0 {-38}L{w / 2 - 18} {-h / 2}', d, 3) + g(card(w, h, fill, .08), -w / 2, -h / 2)
        body += txt(text, 0, label_size(text, w - 22, 28) * .36, label_size(text, w - 22, 28), ink(fill, c), 900, 'middle')
        return g(body, x, self.TAG_Y + 38 + dy, ang, 1, 1, 1 - clamp(drop * 1.4))

    def sheet(self, c, steps, written=None, struck=(), ticked=(), stamp_k=0.0, stamp=None, scale=1.0):
        """The PLAN sheet centred on (0, 0). written: rows shown (each 0..1)."""
        w, h = self.SHEET;d = c['dark'];base = c['light'];n = len(steps)
        out = g(card(w, h, base, .1), -w / 2, -h / 2)
        out += rect(-36, -h / 2 - 12, 72, 24, c['metal'], 6, d, 2.5)
        out += txt('PLAN', -w / 2 + 16, -h / 2 + 44, 34, d, 900) + rect(-w / 2 + 16, -h / 2 + 54, w - 32, 3, mix(base, d, .4), 1)
        for i, step in enumerate(steps):
            k = 1.0 if written is None else written[i]
            if k <= 0:continue
            y = self.row_y(i, n) - self.SHEET_Y;bx = -w / 2 + 16
            row = rect(bx, y - 16, 24, 24, c['light'], 4, d, 2.5) + txt(step, bx + 32, y + 5, label_size(step, w - 60, 26), d, 900)
            out += g(row, 0, 0, 0, 1, 1, ease(k))
            if i in struck:
                sk = struck[i] if isinstance(struck, dict) else 1.0
                out += path(f'M{bx - 4} {y - 3}L{bx - 4 + (w - 24) * ease(sk):.1f} {y - 6}', WARN, 5)
            if i in ticked:
                tk = ticked[i] if isinstance(ticked, dict) else 1.0
                out += g(path('M-7 0L-2 6L9 -7', GREEN, 5), bx + 10, y - 3, 0, ease(clamp(tk * 1.5)))
        if stamp and stamp_k > 0:
            st = g(rect(-74, -24, 148, 48, 'none', 8, GREEN, 5) + txt(stamp, 0, 9, label_size(stamp, 132, 26), GREEN, 900, 'middle'), 0, h / 2 - 20, -8, 1 + .3 * (1 - ease(clamp(stamp_k * 2))))
            out += g(st, 0, 0, 0, 1, 1, clamp(stamp_k * 3))
        return g(out, 0, 0, 0, scale) if scale != 1 else out

    def objection(self, text, c, k=1.0):
        w, h = 140, 44;fs = label_size(text, w - 14, 25)
        return g(rect(-w / 2, -h / 2, w, h, WARN, 6, c['dark'], 2.5) + txt(text, 0, fs * .36, fs, '#FFFFFF', 900, 'middle'), 0, 0, -4, 1, 1, clamp(k * 4))

    def pen(self, x, y, c, colour, angle=35):
        d = c['dark']
        body = rect(-10, -96, 20, 82, colour, 4, d, 2.5) + rect(-10, -104, 20, 14, c['metal'], 3, d, 2) + path('M-10 -14L0 6L10 -14Z', d, 2.5, '#F1D7A8') + path('M-3 -2L0 6L3 -2Z', colour, 1, colour)
        return g(body, x, y, angle)

    def block(self, text, c, k_col=0, bad=0.0, tick=0.0, bugged=False):
        w, h = self.BLOCK;d = c['dark']
        cols = [c['primary'], c['accent'], c['secondary'], c['pop']]
        col = cols[k_col % 4]
        if col in (c['light'], c['wall']):col = c['primary']
        col = mix(col, WARN, bad)
        out = g(card(w, h, col, .1), -w / 2, -h / 2)
        out += f'<circle cx="{-w / 2 + 14}" cy="{-h / 2 + 12}" r="4" fill="{mix(col, d, .4)}"/><circle cx="{w / 2 - 14}" cy="{-h / 2 + 12}" r="4" fill="{mix(col, d, .4)}"/>'
        fs = label_size(text, w - 20, 24);out += txt(text, 0, fs * .36 + 4, fs, ink(col, c), 900, 'middle')
        if bugged:out += self.bug(w / 2 - 16, h / 2 - 10, c, .45, 0)
        if tick > 0:out += g(f'<circle r="14" fill="{GREEN}" stroke="{d}" stroke-width="2.5"/>' + path('M-6 0L-2 5L7 -6', '#FFFFFF', 3.5), w / 2 - 6, -h / 2 + 6, 0, ease(clamp(tick * 1.6)))
        return out

    def bug(self, x, y, c, s=1.0, walk=0.0, angle=0):
        d = c['dark'];legs = ''
        for k, ly in enumerate((-8, 0, 8)):
            sw = 5 * math.sin(walk * 9 + k * 2)
            legs += path(f'M-6 {ly}L-20 {ly - 6 + sw:.1f}M6 {ly}L20 {ly - 6 - sw:.1f}', d, 3)
        body = legs + f'<ellipse rx="12" ry="16" fill="{WARN}" stroke="{d}" stroke-width="3"/><circle cy="-17" r="7" fill="{d}"/>'
        body += path('M0 -8V14', d, 2.5) + path('M-4 -22L-10 -32M4 -22L10 -32', d, 2.5)
        return g(body, x, y, angle, s)

    def counter(self, c, n, k=1.0, flip=0.0):
        x, y = self.COUNTER;d = c['dark'];text = f'ROUND {n}'
        out = rect(-92, -28, 184, 56, d, 10) + rect(-82, -20, 164, 40, mix(d, c['light'], .12), 6)
        out += g(txt(text, 0, 12, 32, c['light'], 900, 'middle'), 0, 0, 0, 1, max(.05, abs(math.cos(math.pi * flip))))
        return g(out, x, y - 40 * (1 - ease(k)), 0, 1, 1, clamp(k * 3))

    def stamp_tool(self, x, y_face, c, label):
        """A hand stamp whose rubber face bottom is at (x, y_face)."""
        d = c['dark'];out = rect(x - 70, y_face - 30, 140, 30, GREEN, 6, d, 3) + rect(x - 60, y_face - 52, 120, 24, c['metal'], 6, d, 3)
        out += rect(x - 14, y_face - 130, 28, 80, c['secondary'] if c['secondary'] != c['wall'] else c['primary'], 6, d, 3)
        out += f'<circle cx="{x}" cy="{y_face - 146}" r="28" fill="{c["primary"]}" stroke="{d}" stroke-width="3"/>'
        return out

    def seal(self, logo, c, r=40):
        d = c['dark'];out = f'<circle r="{r + 6}" fill="{GREEN}" stroke="{d}" stroke-width="3"/>'
        out += g(self.badge(logo, c, r - 4), 0, 0, 0, 1)
        out += g(f'<circle r="15" fill="{GREEN}" stroke="{d}" stroke-width="2.5"/>' + path('M-6 0L-2 5L7 -6', '#FFFFFF', 3.5), r - 2, r - 8)
        return out

    def star(self, c, label, r=58):
        pts = ' '.join(f'{(r if k % 2 == 0 else r * .5) * math.cos(-math.pi / 2 + k * math.pi / 5):.1f},{(r if k % 2 == 0 else r * .5) * math.sin(-math.pi / 2 + k * math.pi / 5):.1f}' for k in range(10))
        return (f'<polygon points="{pts}" fill="#000" opacity=".18" transform="translate(5 7)"/><polygon points="{pts}" fill="{GOLD}" stroke="{c["dark"]}" stroke-width="4" stroke-linejoin="round"/>'
                + txt(label, 0, 10, label_size(label, r * .9, 30), c['dark'], 900, 'middle'))

    # Mode drawing ---------------------------------------------------------------------

    def stations(self, p, c, tags=None, tag_k=(1, 1), drops=(0, 0), old=(None, None), bob=(0, 0)):
        tags = tags or p['roles']
        out = self.desk(-self.DESK_X, c) + self.desk(self.DESK_X, c)
        out += self.sign(-self.DESK_X, c, p['left_logo'], p['left'], tags[0], tag_k[0], drops[0], old[0], bob[0])
        out += self.sign(self.DESK_X, c, p['right_logo'], p['right'], tags[1], tag_k[1], drops[1], old[1], bob[1])
        return out

    def floor_shadow(self, c):
        return g(rect(-330, -12, 660, 12, c['dark'], 6), opacity=.14)

    def draw(self, p, pose, c):
        t, tc, u, after = self.timeline(pose);mode = p['mode']
        return getattr(self, 'draw_' + mode)(p, c, t, tc, u, after)

    def gaps(self, p):
        return list(p['gaps'])[:3]

    def gap_rows(self, p):
        n = len(p['steps']);return [min(n - 1, (1 + 2 * j) % n) for j in range(len(self.gaps(p)))]

    def draw_plan(self, p, c, t, tc, u, after):
        steps = p['steps'];n = len(steps);out = self.floor_shadow(c) + self.stations(p, c)
        written = [seg(u, .04 + .5 * i / n, .04 + .5 * (i + 1) / n) for i in range(n)]
        k = seg(u, .66, 1.0)
        if k <= 0:pos = self.sheet_at(-1);ang = 0
        else:pos = arc(self.sheet_at(-1), self.sheet_at(1), ease_in(k) if k < 1 else 1, 170);ang = 20 * math.sin(math.pi * k)
        bump = 14 * settle(clamp(after * 1.6), 1)
        out += g(self.sheet(c, steps, written), pos[0], pos[1] + bump, ang)
        if u < .62:
            i = min(n - 1, int(u / .54 * n));px = -self.DESK_X - self.SHEET[0] / 2 + 40 + 90 * ((u / .54 * n) % 1)
            out += self.pen(px, self.row_y(i, n), c, c['accent'], 30 + 8 * math.sin(u * 60))
        if after > 0:out += burst(*self.sheet_at(1), clamp(after * 2.4), c, 8, 70, 140)
        return out

    def draw_audit(self, p, c, t, tc, u, after):
        steps = p['steps'];n = len(steps);gaps = self.gaps(p);rows = self.gap_rows(p);m = len(gaps)
        out = self.floor_shadow(c) + self.stations(p, c) + self.counter(c, 1, seg(u, 0, .15))
        struck = {};tabs = ''
        for j in range(m):
            a = .12 + .84 * j / m;b = .12 + .84 * (j + 1) / m
            sk = seg(u, a, a + (b - a) * .45)
            if sk > 0:struck[rows[j]] = sk
            tk = seg(u, a + (b - a) * .4, b)
            if tk > 0:
                tx, ty = self.tab_slot(1, j);x = lerp(tx + 260, tx, ease_in(tk));y = ty - 120 * math.sin(math.pi * tk)
                jolt = 8 * settle(clamp(after * 1.5), 1) if j == m - 1 else 0
                tabs += g(self.objection(gaps[j], c, tk), x, y + jolt)
        sx, sy = self.sheet_at(1)
        out += g(self.sheet(c, steps, struck=struck), sx, sy) + tabs
        if u < 1:
            j = min(m - 1, int(u * m));rx = sx - self.SHEET[0] / 2 + 30 + 110 * ((u * m) % 1)
            out += self.pen(rx, self.row_y(rows[j], n) - 2, c, WARN, -30 - 8 * math.sin(u * 50))
        else:
            out += self.pen(sx + self.SHEET[0] / 2 + 30, sy + 40 + 6 * settle(clamp(after), 1), c, WARN, -20)
        return out

    def loop_state(self, p, u):
        """(position, remaining gaps, round, round flip) of the sheet in the loop."""
        m = len(self.gaps(p));R = p['rounds'];trips = 2 * (R - 1);span = .8
        k = clamp(u / span) * trips;i = min(trips - 1, int(k));f = k - i if u < span else 1.0
        src = 1 if i % 2 == 0 else -1;dst = -src
        pos = arc(self.sheet_at(src), self.sheet_at(dst), f, 150) if u < span else self.sheet_at(1)
        fixed_cycles = (i + (1 if f >= 1 else 0)) // 2 if u < span else R - 1
        if u < span and i % 2 == 1:fixed_cycles = (i + 1) // 2 if f > .5 else i // 2
        remaining = max(0, m - math.ceil(m * fixed_cycles / max(1, R - 1)))
        rnd = 1 + (i + 1) // 2 if u < span else R
        flip = f if (u < span and i % 2 == 1) else 0.0
        return pos, remaining, rnd, flip, (math.sin(math.pi * f) * 20 * src if u < span else 0)

    def draw_loop(self, p, c, t, tc, u, after):
        steps = p['steps'];gaps = self.gaps(p);rows = self.gap_rows(p);m = len(gaps)
        pos, remaining, rnd, flip, ang = self.loop_state(p, u)
        out = self.floor_shadow(c) + self.stations(p, c, bob=(-10 * abs(math.sin(u * 20)) if pos[0] < 0 else 0, -10 * abs(math.sin(u * 20)) if pos[0] > 0 else 0))
        out += self.counter(c, rnd, 1.0, flip)
        fixed = m - remaining
        struck = {rows[j]: 1.0 for j in range(fixed, m)};ticked = {rows[j]: 1.0 for j in range(fixed)}
        if u >= .8:ticked.update({i: clamp(after * 2 - .1 * i) for i in range(len(steps)) if i not in ticked and t > tc})
        stamp_k = clamp(after * 3) if t > tc else 0.0
        bump = 10 * settle(clamp(after * 1.6), 1)
        out += g(self.sheet(c, steps, struck=struck, ticked=ticked, stamp=p['stamp'], stamp_k=stamp_k), pos[0], pos[1] + bump, ang)
        # Objection tabs ride along with the sheet and peel off as they are fixed.
        for j in range(fixed, m):
            tx, ty = self.tab_slot(1, j);side = 1 if pos[0] >= 0 else -1
            dx = tx - self.sheet_at(1)[0];out += g(self.objection(gaps[j], c), pos[0] + dx * side, pos[1] + (ty - self.SHEET_Y) + bump)
        if u >= .8:
            k = seg(u, .8, 1.0);sx, sy = self.sheet_at(1);face = sy + self.SHEET[1] / 2 - 22
            y = lerp(-1000, face, ease_in(k)) if t <= tc else lerp(face, -1000, ease(seg(after, .25, .9)))
            out += self.stamp_tool(sx, y, c, p['stamp'])
            if t > tc:out += burst(sx, face - 20, clamp(after * 2.2), c, 10, 70, 150)
        return out

    def draw_swap(self, p, c, t, tc, u, after):
        steps = p['steps'];old = p['roles'];new = p['new_roles']
        ka = seg(u, .1, .5);kb = seg(u, .55, 1.0)
        drops = (seg(u, 0, .3), seg(u, .42, .72))
        out = self.floor_shadow(c) + self.stations(p, c, tags=new, tag_k=(ka, kb), drops=drops, old=old)
        sx, sy = self.sheet_at(1)
        out += g(self.sheet(c, steps, ticked=set(range(len(steps))), stamp=p['stamp'], stamp_k=1.0), sx, sy)
        out += self.counter(c, p['rounds'], 1.0)
        if after > 0:out += burst(self.DESK_X, self.TAG_Y + 38, clamp(after * 2.4), c, 8, 50, 110)
        return out

    def build_parts(self, p, u, t, tc, after):
        steps = p['steps'];n = len(steps);f = p['bug'] % n
        land = [.06 + .44 * (i + 1) / n for i in range(n)]
        return steps, n, f, land

    def draw_build(self, p, c, t, tc, u, after):
        steps, n, f, land = self.build_parts(p, u, t, tc, after)
        out = self.floor_shadow(c) + self.stations(p, c, tags=p['new_roles'], bob=(-8 * abs(math.sin(u * 18)) * (u > .5), -8 * abs(math.sin(u * 22)) * (u < .5)))
        sx, sy = self.sheet_at(1)
        out += g(self.sheet(c, steps, ticked=set(range(n)), stamp=p['stamp'], stamp_k=1.0), sx, sy)
        tower = ''
        for i, step in enumerate(steps):
            bx, by = self.block_slot(i);l0 = land[i] - .14
            if u < l0:continue
            if i == f:
                if u >= .74 and u < .86:  # knocked out sideways
                    k = seg(u, .74, .86);tower += g(self.block(step, c, i, 1.0, bugged=True), bx - 260 * ease(k), by + 300 * ease_in(k) - 60 * math.sin(math.pi * k), -60 * k, 1, 1, 1 - k)
                if u >= .86:
                    k = seg(u, .86, 1.0);y = lerp(by - 520, by, ease_in(k))
                    tower += g(self.block(step, c, i, 0.0, tick=clamp(after * 2)), bx, y + 8 * settle(clamp(after * 1.5), 1))
                    continue
                if u >= .74:continue
                bad = seg(u, .6, .7)
                k = seg(u, l0, land[i]);x, y = arc((sx, sy), (bx, by), k, 160)
                tower += g(self.block(step, c, i, bad, bugged=bad > 0), x, y, 25 * (1 - k))
                if bad > 0:tower += g(self.objection(p['bug_label'], c, bad), bx + self.BLOCK[0] / 2 + 40, by - 10)
                continue
            k = seg(u, l0, land[i]);x, y = arc((sx, sy), (bx, by), k, 160)
            tower += g(self.block(step, c, i, tick=clamp(after * 2 - .15 * i) if t > tc else 0.0), x, y, 25 * (1 - k))
        out += tower
        if .5 <= u < .76:
            k = seg(u, .5, .66);lx, ly = self.block_slot(f);ox, oy = -self.DESK_X, self.SHEET_Y
            x = lerp(ox, lx - 20, ease(k));y = lerp(oy, ly, ease(k))
            out += self.magnifier(x, y, c, 1 - seg(u, .7, .76))
        if t > tc:out += burst(*self.block_slot(f), clamp(after * 2.2), c, 10, 60, 130)
        return out

    def magnifier(self, x, y, c, o=1.0):
        d = c['dark']
        lens = f'<circle cx="{x:.1f}" cy="{y:.1f}" r="56" fill="#FFFFFF" opacity=".3"/><circle cx="{x:.1f}" cy="{y:.1f}" r="56" fill="none" stroke="{d}" stroke-width="12"/><circle cx="{x:.1f}" cy="{y:.1f}" r="56" fill="none" stroke="{c["metal"]}" stroke-width="6"/>'
        lens += path(f'M{x - 40:.1f} {y + 40:.1f}L{x - 96:.1f} {y + 96:.1f}', d, 24) + path(f'M{x - 42:.1f} {y + 42:.1f}L{x - 94:.1f} {y + 94:.1f}', c['secondary'], 14)
        return g(lens, 0, 0, 0, 1, 1, o)

    def seal_path(self, p, side, k):
        n = len(p['steps']);top = self.block_slot(n - 1)[1];mid = (self.block_slot(0)[1] + top) / 2
        dst = (side * 46, top - self.BLOCK[1] / 2 - 50 - 14 * (side > 0));src = (side * self.DESK_X, self.BADGE_Y)
        return arc(src, dst, k, 120), dst

    def draw_ship(self, p, c, t, tc, u, after):
        steps = p['steps'];n = len(steps)
        out = self.floor_shadow(c) + self.stations(p, c, tags=p['new_roles'], bob=(-14 * abs(math.sin(u * 16)), -14 * abs(math.sin(u * 16 + 1))))
        sx, sy = self.sheet_at(1)
        out += g(self.sheet(c, steps, ticked=set(range(n)), stamp=p['stamp'], stamp_k=1.0), sx, sy)
        jolt = 10 * settle(clamp(after * 1.4), 1)
        for i, step in enumerate(steps):
            bx, by = self.block_slot(i);out += g(self.block(step, c, i, tick=1.0), bx, by + jolt * (i / n))
        for side, (a, b) in ((-1, (.2, .62)), (1, (.5, 1.0))):
            k = seg(u, a, b)
            if k <= 0:continue
            (x, y), _ = self.seal_path(p, side, ease_in(k) if k < 1 else 1.0)
            logo = p['left_logo'] if side < 0 else p['right_logo']
            out += g(self.seal(logo, c), x, y + (jolt if k >= 1 else 0), -10 * side * (1 - k), .9 + .1 * k)
        if t > tc:
            out += burst(0, self.block_slot(n // 2)[1], clamp(after * 2), c, 12, 90, 190)
            if p.get('banner'):
                w = max(220, len(p['banner']) * 26 + 40);k = ease(seg(after, .1, .5))
                out += g(card(w, 60, GREEN, .05) + txt(p['banner'], w / 2, 42, label_size(p['banner'], w - 30, 36), '#FFFFFF', 900, 'middle'), -w / 2, self.COUNTER[1] - 30 + 60 * (1 - k), -3, 1, 1, k)
        return out

    def draw_solo(self, p, c, t, tc, u, after):
        steps = p['steps'];n = len(steps);x0 = self.SOLO_DESK;tx = self.SOLO_TOWER;d = c['dark']
        roles = p['solo_roles'];phase = 0 if u < .3 else (1 if u < .6 else 2)
        flip = min(seg(u, .27, .33), 1) if phase == 1 else (seg(u, .57, .63) if phase == 2 else 0)
        out = self.floor_shadow(c) + self.desk(x0, c)
        out += self.sign(x0, c, p['solo_logo'], p['solo'], None)
        # One tag cycling through all three jobs.
        tag = roles[phase];sq = max(.05, abs(math.cos(math.pi * flip))) if 0 < flip < 1 else 1.0
        out += g(self.tag(0, c, tag, 1.0, 0.0), x0, 0, 0, sq, 1 / sq)
        written = [seg(u, .02 + .25 * i / n, .02 + .25 * (i + 1) / n) for i in range(n)]
        out += g(self.sheet(c, steps, written), x0, self.SHEET_Y)
        if u < .3:out += self.pen(x0 - 40 + 90 * ((u / .27 * n) % 1), self.row_y(min(n - 1, int(u / .27 * n)), n), c, c['accent'], 30)
        bug_i = p['bug'] % n
        for i, step in enumerate(steps):
            bx, by = self.block_slot(i, tx);l1 = .32 + .26 * (i + 1) / n;l0 = l1 - .1
            if u < l0:continue
            k = seg(u, l0, l1);x, y = arc((x0, self.SHEET_Y), (bx, by), k, 140)
            wob = 6 * math.sin(after * 18) * (1 - after) * (i / n) if t > tc else 0
            out += g(self.block(step, c, i, bugged=(i == bug_i)), x + wob, y, 25 * (1 - k) + wob * .4)
        # Gold star: the same desk grades its own work.
        top = self.block_slot(n - 1, tx)[1] - self.BLOCK[1] / 2
        if u >= .62:
            k = seg(u, .62, 1.0);src = (x0, self.BADGE_Y);dst = (tx, top - 60)
            x, y = arc(src, dst, ease_in(k) if k < 1 else 1, 130)
            out += g(self.star(c, p['grade']), x, y + 10 * settle(clamp(after * 1.5), 1), 360 * (1 - k), 1 + .2 * settle(clamp(after * 1.5), 1))
        if t > tc:
            for b in range(p['bugs']):
                k = clamp(after * 1.3 - b * .18)
                if k <= 0:continue
                bx, by = self.block_slot(bug_i, tx);ex = tx + (-1) ** b * (70 + 120 * k) + 40 * b
                out += self.bug(lerp(bx + 40, ex, k), lerp(by, -24 - 16 * b, ease(k)), c, 1.4, after * 4 + b, 90 * (-1) ** b)
            out += burst(tx, top - 60, clamp(after * 2.2), c, 10, 60, 140)
        return out

    # Contacts --------------------------------------------------------------------------

    def seams(self, p, pose):
        start, end, action, t = pose
        if not action:t = 1.0
        tc = self.contact_t('run');t_ = min(t, tc);u = t_in(t_, tc);mode = p['mode']
        if mode == 'plan':
            k = seg(u, .66, 1.0);pos = self.sheet_at(-1) if k <= 0 else arc(self.sheet_at(-1), self.sheet_at(1), ease_in(k) if k < 1 else 1, 170)
            pair = (pos, self.sheet_at(1))
        elif mode == 'audit':
            m = len(self.gaps(p));j = m - 1;a = .12 + .84 * j / m;b = .12 + .84 * (j + 1) / m;tk = seg(u, a + (b - a) * .4, b)
            tx, ty = self.tab_slot(1, j);pair = ((lerp(tx + 260, tx, ease_in(tk)), ty - 120 * math.sin(math.pi * tk)), (tx, ty))
        elif mode == 'loop':
            k = seg(u, .8, 1.0);sx, sy = self.sheet_at(1);face = sy + self.SHEET[1] / 2 - 22
            pair = ((sx, lerp(-1000, face, ease_in(k))), (sx, face))
        elif mode == 'swap':
            kb = seg(u, .55, 1.0);y = self.TAG_Y + 38;pair = ((self.DESK_X, y - 230 * (1 - ease_in(kb))), (self.DESK_X, y))
        elif mode == 'build':
            f = p['bug'] % len(p['steps']);bx, by = self.block_slot(f);k = seg(u, .86, 1.0)
            pair = ((bx, lerp(by - 520, by, ease_in(k))), (bx, by))
        elif mode == 'ship':
            k = seg(u, .5, 1.0);(x, y), dst = self.seal_path(p, 1, ease_in(k) if k < 1 else 1.0);pair = ((x, y), dst)
        else:
            n = len(p['steps']);top = self.block_slot(n - 1, self.SOLO_TOWER)[1] - self.BLOCK[1] / 2;k = seg(u, .62, 1.0)
            dst = (self.SOLO_TOWER, top - 60);pair = (arc((self.SOLO_DESK, self.BADGE_Y), dst, ease_in(k) if k < 1 else 1, 130), dst)
        return {'loop-contact': pair}

    def identity(self, p):
        return None if p['mode'] == 'solo' else self.name

    def printed_text(self, p):
        mode = p['mode']
        if mode == 'solo':return [p['solo'], *p['solo_roles'], 'PLAN', *p['steps'], p['grade']]
        out = [p['left'], p['right'], 'PLAN', *p['steps']]
        out += list(p['new_roles'] if mode in ('swap', 'build', 'ship') else p['roles'])
        if mode == 'swap':out += list(p['roles'])
        if mode in ('audit', 'loop'):out += [*self.gaps(p), 'ROUND']
        if mode in ('loop', 'swap', 'build', 'ship'):out += [p['stamp']]
        if mode == 'build':out += [p['bug_label']]
        if mode == 'ship' and p.get('banner'):out += [p['banner']]
        return [x for x in out if x]


LABEL = {'type': 'string', 'minLength': 1, 'maxLength': 10}
register(ReviewLoop(
    name='review-loop',
    description='Two workstations, each under its maker\'s badge, that check each other\'s work: one PLAN sheet and one block-tower build carried across beats. Modes: solo (one desk plans, builds and gives itself a gold A+ while bugs crawl out), plan (the left desk writes the steps and throws the sheet across), audit (a red pen strikes rows and objection tabs slap on), loop (the sheet goes back and forth, objections peel off as the ROUND counter rises, a HOLDS UP stamp lands), swap (the role tags drop off and new ones slap on), build (blocks named after the steps stack into a tower; the other desk\'s magnifier finds a bug and a fixed block drops in), ship (both badges fire a seal onto the tower). Code review, second opinions, audits, pair work, two AI models, checks and balances.',
    params_schema={'type': 'object', 'properties': {
        'mode': {'enum': ['solo', 'plan', 'audit', 'loop', 'swap', 'build', 'ship']},
        'steps': {'type': 'array', 'items': LABEL, 'minItems': 2, 'maxItems': MAX_STEPS},
        'left': {'type': 'string', 'minLength': 1, 'maxLength': 10}, 'right': {'type': 'string', 'minLength': 1, 'maxLength': 10},
        'left_logo': {'type': ['string', 'null']}, 'right_logo': {'type': ['string', 'null']},
        'roles': {'type': 'array', 'items': LABEL, 'minItems': 2, 'maxItems': 2},
        'new_roles': {'type': 'array', 'items': LABEL, 'minItems': 2, 'maxItems': 2},
        'gaps': {'type': 'array', 'items': LABEL, 'minItems': 1, 'maxItems': 3},
        'rounds': {'type': 'integer', 'minimum': 2, 'maximum': 4},
        'stamp': {'type': 'string', 'minLength': 1, 'maxLength': 10},
        'bug': {'type': 'integer', 'minimum': 0, 'maximum': MAX_STEPS - 1}, 'bug_label': LABEL,
        'banner': {'type': ['string', 'null'], 'maxLength': 12},
        'solo': {'type': 'string', 'minLength': 1, 'maxLength': 10}, 'solo_logo': {'type': ['string', 'null']},
        'solo_roles': {'type': 'array', 'items': LABEL, 'minItems': 3, 'maxItems': 3},
        'grade': {'type': 'string', 'minLength': 1, 'maxLength': 3}, 'bugs': {'type': 'integer', 'minimum': 1, 'maximum': 4}},
        'required': ['mode'], 'additionalProperties': False},
    defaults={'mode': 'plan', 'steps': ['SCHEMA', 'LOGIN', 'API', 'TESTS'], 'left': 'WRITER', 'right': 'CHECKER', 'left_logo': None, 'right_logo': None,
              'roles': ['PLANS', 'AUDITS'], 'new_roles': ['AUDITS', 'BUILDS'], 'gaps': ['NO TESTS', 'AUTH?'], 'rounds': 3, 'stamp': 'HOLDS UP',
              'bug': 2, 'bug_label': 'BUG', 'banner': None, 'solo': '1 MODEL', 'solo_logo': None, 'solo_roles': ['PLANS', 'BUILDS', 'GRADES'], 'grade': 'A+', 'bugs': 3},
    states=('idle', 'done'),
    actions={'run': Action('run', 'idle', 'done', 66, 'loop-contact', 46)},
    bot_slot={'x': -340, 'y': 0, 'scale': .22, 'role': 'carries the sheet between desks, points at objections and cheers the stamp',
              'keep_clear': ((-310, -520, 220, 520), (90, -520, 220, 520))},
    tags=('review', 'audit', 'plan', 'check', 'checks', 'second', 'opinion', 'pair', 'two', 'models', 'feedback', 'homework', 'grade', 'judge', 'critic', 'swap', 'roles', 'build', 'bug', 'bugs', 'loop', 'rounds'),
    footprint=(-320, -800, 640, 800)))
