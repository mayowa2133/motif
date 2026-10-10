"""Certificate card: one document that keeps its identity across two beats.

Codex's review of the v11 HTTPS reel (2026-10-10): the reel "loses the
certificate's identity instead of showing that same certificate renew". It
used a thermometer for "each certificate lasts 90 days" and dominoes for
"software renews it automatically", so the viewer never saw one object age
and come back. Certificate is that object drawn directly: a framed
certificate on a stand with the site's domain, its issuer, a padlock seal and
a big days-left counter.

  mode "expire"  the counter ticks down (90 -> 3), the paper yellows, the
                 corner curls, the hourglass empties and the counter panel
                 turns to a warning colour. Contact: the life bar reaches the
                 days_to mark.
  mode "renew"   the same card starts aged at days_from; a ceiling stamp arm
                 comes down and stamps it, the paper refreshes and the counter
                 rolls back up to days_to. Contact: the stamp face meets the
                 paper.

Same contract as library.py: original authored SVG through palette roles, the
local origin is the floor under the rig's centre, and each contact closes
exactly at its contact frame. Status: DRAFT (awaiting Mayowa approval).
"""
import math

from motif_rigs import register
from motif_rigs.base import Action, Rig, ease, ease_in, lerp
from motif_rigs.library import StampGate, ink, label_size, settle, t_after, t_in
from motif_rigs.library2 import burst
from motif_ui_components import g, path, rect, txt

WARN = '#E5484D'            # warning red: a semantic colour, the same in every palette
AGED = '#D6AE62'            # the yellow old paper drifts toward
STAIN = '#9C6B2E'


def mix(a, b, f):
    """Blend two #RRGGBB colours (f = 0 -> a, 1 -> b)."""
    f = max(0.0, min(1.0, f))
    ca = [int(a[i:i + 2], 16) for i in (1, 3, 5)];cb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return '#' + ''.join(f'{round(x + (y - x) * f):02X}' for x, y in zip(ca, cb))


def smooth(u):
    u = max(0.0, min(1.0, u));return u * u * (3 - 2 * u)


def clamp(u):
    return max(0.0, min(1.0, u))


class Certificate(Rig):
    CARD = (-220, -630, 420, 530)        # x, y, w, h of the certificate sheet
    BAR = (-180, -248, 340, 24)          # life bar under the counter
    STAMP_X = 74                         # stamp column; the imprint lands at (STAMP_X, PAPER_Y)
    PAPER_Y = -150
    PARK_Y = -634                        # stamp face bottom when retracted (above the card)

    # Timeline ---------------------------------------------------------------

    def printed_text(self, p):
        """The card prints its title, counter and caption as well as the params' strings."""
        return [p['domain'], p.get('issuer') or '', 'CERTIFICATE', 'DAYS LEFT', str(p['days_from']), str(p['days_to'])] + ([p['stamp']] if p['mode'] == 'renew' else [])

    def life(self, p):
        return max(1, p['days_from'], p['days_to'])

    def days(self, p, pose):
        """Continuous days left for this pose (the seam uses it unrounded)."""
        start, end, action, t = pose;a, b = p['days_from'], p['days_to']
        if not action:return float(b if start == 'done' else a)
        tc = self.contact_t('run')
        if p['mode'] == 'expire':
            u = t_in(t, tc);return lerp(a, b, smooth((u - .12) / .88) if u < 1 else 1.0)
        return lerp(a, b, ease(clamp((t_after(t, tc) - .08) / .5)))

    def age(self, p, pose, days):
        """0 = crisp new paper, 1 = old. Expire tracks the days; renew snaps fresh at the stamp."""
        start, end, action, t = pose;L = self.life(p)
        old = clamp(1 - days / L)
        if p['mode'] == 'renew':
            first = clamp(1 - p['days_from'] / L)
            if not action:return 0.0 if start == 'done' else first
            return first * (1 - ease(clamp(t_after(t, self.contact_t('run')) / .3)))
        return old

    def bar_x(self, p, days):
        x, y, w, h = self.BAR;return x + w * clamp(days / self.life(p))

    def stamp_y(self, p, pose):
        """Stamp face bottom y."""
        start, end, action, t = pose
        if p['mode'] != 'renew' or not action:return self.PARK_Y
        tc = self.contact_t('run')
        if t <= tc:return lerp(self.PARK_Y, self.PAPER_Y, ease_in(t_in(t, tc)))
        return lerp(self.PAPER_Y, self.PARK_Y, ease(clamp((t_after(t, tc) - .06) / .4)))

    # Parts --------------------------------------------------------------------

    @staticmethod
    def padlock(x, y, s, body, d):
        """Small padlock icon centred on (x, y), s = body width."""
        sh = f'M{x - s * .3:.1f} {y - s * .1:.1f}V{y - s * .42:.1f}A{s * .3:.1f} {s * .3:.1f} 0 0 1 {x + s * .3:.1f} {y - s * .42:.1f}V{y - s * .1:.1f}'
        out = path(sh, d, s * .2) + path(sh, mix(body, '#FFFFFF', .2), s * .1)
        out += rect(x - s / 2, y - s * .15, s, s * .75, body, s * .14, d, max(2, s * .07))
        out += f'<circle cx="{x:.1f}" cy="{y + s * .17:.1f}" r="{s * .1:.1f}" fill="{d}"/>' + rect(x - s * .04, y + s * .17, s * .08, s * .2, d)
        return out

    def seal(self, x, y, r, c, age):
        d = c['dark'];gold = mix(c['secondary'], AGED, age * .5);ribbon = mix(c['primary'], '#A08A6A', age * .4)
        out = path(f'M{x - 26} {y + 10}L{x - 40} {y + r + 46}L{x - 22} {y + r + 34}L{x - 10} {y + r + 52}L{x - 2} {y + 12}Z', d, 3, ribbon)
        out += path(f'M{x + 26} {y + 10}L{x + 40} {y + r + 46}L{x + 22} {y + r + 34}L{x + 10} {y + r + 52}L{x + 2} {y + 12}Z', d, 3, ribbon)
        pts = []
        for k in range(32):
            a = k * math.pi / 16;rr = r if k % 2 == 0 else r * .86
            pts.append(f'{x + rr * math.cos(a):.1f} {y + rr * math.sin(a):.1f}')
        star = 'M' + 'L'.join(pts) + 'Z'
        out += path(star, d, 0, d, 'transform="translate(4 5)" opacity=".18"') + path(star, d, 3, gold)
        out += f'<circle cx="{x}" cy="{y}" r="{r * .66:.1f}" fill="{mix(gold, "#FFFFFF", .25)}" stroke="{d}" stroke-width="2.5"/>'
        out += f'<circle cx="{x}" cy="{y}" r="{r * .54:.1f}" fill="none" stroke="{d}" stroke-width="1.5" stroke-dasharray="3 4" opacity=".5"/>'
        out += self.padlock(x, y + 4, r * .62, c['accent'] if c['accent'] != gold else c['primary'], d)
        out += g(path(f'M{x - r * .6:.1f} {y - r * .5:.1f}A{r * .78:.1f} {r * .78:.1f} 0 0 1 {x - r * .1:.1f} {y - r * .8:.1f}', '#FFFFFF', 4), opacity=.5)
        return out

    def hourglass(self, x, y, frac, c, warn):
        """Hourglass centred on (x, y): frac of the sand still in the top bulb."""
        d = c['dark'];wood = c['primary'] if c['primary'] != c['light'] else c['secondary'];sand = mix(c['secondary'] if c['secondary'] != wood else c['pop'], WARN, warn * .6)
        hw, hh = 34, 58
        out = rect(x - hw - 10, y - hh - 16, 2 * hw + 20, 14, wood, 5, d, 3) + rect(x - hw - 10, y + hh + 2, 2 * hw + 20, 14, wood, 5, d, 3)
        for sx in (-1, 1):out += rect(x + sx * (hw + 2) - 4, y - hh - 2, 8, 2 * hh + 4, c['metal'], 3, d, 2)
        glass = f'M{x - hw} {y - hh}H{x + hw}C{x + hw} {y - 18} {x + 6} {y - 8} {x + 6} {y}C{x + 6} {y + 8} {x + hw} {y + 18} {x + hw} {y + hh}H{x - hw}C{x - hw} {y + 18} {x - 6} {y + 8} {x - 6} {y}C{x - 6} {y - 8} {x - hw} {y - 18} {x - hw} {y - hh}Z'
        out += path(glass, d, 0, '#FFFFFF', 'opacity=".55"')
        top = hh * .82 * frac
        if top > 1:
            ty = y - 6 - top;tw = hw * (.25 + .7 * clamp(top / (hh * .8)))
            out += path(f'M{x - tw:.1f} {ty:.1f}Q{x} {ty - 6:.1f} {x + tw:.1f} {ty:.1f}L{x + 3} {y - 4}H{x - 3}Z', d, 0, sand)
        bot = hh * .82 * (1 - frac)
        if bot > 1:
            by = y + hh - bot;bw = hw * .95
            out += path(f'M{x - bw:.1f} {y + hh}L{x - bw * .8:.1f} {by + bot * .4:.1f}Q{x} {by - 10:.1f} {x + bw * .8:.1f} {by + bot * .4:.1f}L{x + bw:.1f} {y + hh}Z', d, 0, sand)
        if 0 < frac < 1:out += rect(x - 1.5, y - 2, 3, hh - bot, sand)
        out += path(glass, d, 3) + g(path(f'M{x - hw + 8} {y - hh + 8}C{x - hw + 8} {y - 30} {x - 12} {y - 16} {x - 12} {y - 6}', '#FFFFFF', 4), opacity=.6)
        return out

    def stamp_arm(self, p, c, fy, inked):
        """Ceiling mount, telescoping piston and stamp head; fy = face bottom y."""
        d = c['dark'];x = self.STAMP_X;out = ''
        mount = -756
        out += g(rect(x - 120, mount - 6, 240, 22, d, 6), 5, 6, opacity=.18) + rect(x - 120, mount - 6, 240, 22, c['metal'], 6, d, 3)
        for bx in (x - 104, x + 104):out += f'<circle cx="{bx}" cy="{mount + 5}" r="5" fill="{c["light"]}" stroke="{d}" stroke-width="2"/>'
        out += rect(x - 30, mount + 14, 60, 22, c['secondary'], 5, d, 3)
        top, bottom = mount + 36, fy - 84            # rod runs from the collar to the head
        if bottom > top:
            mid = top + (bottom - top) * .5
            out += rect(x - 12, top, 24, bottom - top, c['metal'], 4, d, 3) + g(rect(x - 6, top + 4, 5, bottom - top - 8, '#FFFFFF', 2), opacity=.4)
            out += rect(x - 20, top, 40, min(bottom - top, 60), c['primary'], 6, d, 3) + rect(x - 16, mid - 8, 32, 16, c['secondary'], 4, d, 3)
            # Coiled cable down the side of the piston.
            cab = 'M' + ' L'.join(f'{x + 36 + 7 * math.sin(k * .9):.1f} {lerp(top, bottom, k / 24):.1f}' for k in range(25))
            out += path(cab, d, 5) + path(cab, c['accent'], 2.5)
        # Head: housing with a status light and the stamp word, then the rubber face.
        hx = x;hy = fy
        out += g(rect(hx - 108, hy - 84, 216, 58, d, 12), 6, 7, opacity=.18)
        out += rect(hx - 108, hy - 84, 216, 58, c['primary'], 12, d, 3) + g(rect(hx - 98, hy - 79, 130, 7, '#FFFFFF', 3), opacity=.35)
        out += rect(hx - 84, hy - 74, 168, 38, c['light'], 7, d, 2.5)
        out += txt(p['stamp'], hx, hy - 46, label_size(p['stamp'], 150, 26), d, 900, 'middle')
        for rx in (hx - 96, hx + 96):out += f'<circle cx="{rx}" cy="{hy - 36}" r="4.5" fill="{c["metal"]}" stroke="{d}" stroke-width="2"/>'
        out += rect(hx - 96, hy - 26, 192, 12, c['metal'], 3, d, 3)
        out += rect(hx - 100, hy - 16, 200, 16, c['accent'] if inked else c['metal'], 4, d, 3)
        return out

    # Drawing -----------------------------------------------------------------

    def draw(self, p, pose, c):
        start, end, action, t = pose;tc = self.contact_t('run') if action else 1
        d = c['dark'];renew = p['mode'] == 'renew';L = self.life(p)
        days = self.days(p, pose);age = self.age(p, pose, days)
        after = t_after(t, tc) if action else (1.0 if start == 'done' else 0.0)
        warn = clamp((.3 - days / L) / .22)
        cx, cy, cw, ch = self.CARD;x1, y1 = cx + cw, cy + ch
        shake = 0.0
        if action and not renew and after:shake = settle(after, 2.5)
        if action and renew and 0 < after < .3:shake = settle(after / .3, 1.6)
        body = ''
        # Stand: floor shadow, easel legs and the ledge the card leans on.
        body += g(rect(-260, -10, 520, 12, d, 6), opacity=.15)
        for lx, fx in ((-150, -196), (130, 176)):
            body += path(f'M{lx} -130L{fx} 0', d, 18) + path(f'M{lx} -130L{fx} 0', c['metal'], 11)
        body += path('M-10 -300L-10 0', d, 16) + path('M-10 -300L-10 0', c['metal'], 9)
        # The certificate sheet (rotates a hair as it shakes).
        paper = mix(c['light'], AGED, .62 * age);border = mix(c['primary'], '#A08A6A', .45 * age)
        f = 92 * smooth(clamp((age - .25) / .7))          # curl size, bottom-right corner
        sheet = f'M{cx} {cy}H{x1}V{y1 - f:.1f}L{x1 - f:.1f} {y1}H{cx}Z'
        card = path(sheet, d, 0, d, 'transform="translate(8 10)" opacity=".2"') + path(sheet, d, 3.5, paper)
        card += path(sheet, d, 0, 'url(#worldPaper)', f'opacity="{.08 + .14 * age:.3f}"')
        # Printed border: thick band, thin inner rule, corner rosettes.
        bi = 14
        band = f'M{cx + bi} {cy + bi}H{x1 - bi}V{y1 - bi - max(0, f - bi):.1f}' + (f'L{x1 - bi - max(0, f - bi):.1f} {y1 - bi}' if f > bi else '') + f'H{cx + bi}Z'
        card += path(band, border, 10)
        inner = f'M{cx + 28} {cy + 28}H{x1 - 28}V{y1 - 28 - max(0, f - 28):.1f}' + (f'L{x1 - 28 - max(0, f - 28):.1f} {y1 - 28}' if f > 28 else '') + f'H{cx + 28}Z'
        card += path(inner, border, 2.5, extra='opacity=".7"')
        for kx, ky in ((cx + bi, cy + bi), (x1 - bi, cy + bi), (cx + bi, y1 - bi)):
            card += f'<circle cx="{kx}" cy="{ky}" r="9" fill="{c["secondary"]}" stroke="{d}" stroke-width="2.5"/>'
        mid = cx + cw / 2
        # Header.
        card += txt('CERTIFICATE', mid, cy + 74, 26, mix(d, border, .35), 900, 'middle', True)
        card += path(f'M{mid - 168} {cy + 66}H{mid - 104}M{mid + 104} {cy + 66}H{mid + 168}', border, 3)
        card += f'<circle cx="{mid - 176}" cy="{cy + 66}" r="4" fill="{border}"/><circle cx="{mid + 176}" cy="{cy + 66}" r="4" fill="{border}"/>'
        # Domain row with the browser padlock, then the issuer.
        dom = p['domain'];ds = min(40, 300 / max(1, len(dom) * .56));dw = len(dom) * ds * .56
        lx = mid - (dw + 44) / 2
        card += rect(cx + 34, cy + 92, cw - 68, 58, mix(paper, '#FFFFFF', .5), 29, d, 2.5)
        card += self.padlock(lx + 14, cy + 124, 28, c['accent'] if c['accent'] != c['light'] else c['primary'], d)
        card += txt(dom, lx + 44, cy + 121 + ds * .36, ds, d, 900)
        iss = 'issued by ' + p['issuer']
        card += txt(iss, mid, cy + 182, min(24, 340 / max(1, len(iss) * .52)), mix(d, paper, .25), 700, 'middle')
        # Days-left counter panel with the hourglass.
        px, py, pw, ph = cx + 30, cy + 202, cw - 60, 140
        fill = mix(c['accent'], WARN, warn);pulse = 0.0
        if action and not renew and after:pulse = .5 + .5 * math.sin(after * math.pi * 6)
        card += rect(px + 5, py + 6, pw, ph, d, 16).replace('<rect', '<rect opacity=".18"')
        card += rect(px, py, pw, ph, fill, 16, d, 3.5) + g(rect(px + 10, py + 8, pw * .55, 8, '#FFFFFF', 4), opacity=.3)
        if pulse:card += rect(px - 6, py - 6, pw + 12, ph + 12, 'none', 20, WARN, 6).replace('<rect', f'<rect opacity="{pulse * (1 - after):.3f}"')
        win = (px + 16, py + 16, 238, ph - 32)
        card += rect(*win, mix(fill, d, .22), 12, d, 2.5)
        shown = int(round(days));roll = (days - shown) * 34
        num = str(shown);ns = min(112, 220 / max(1, len(num) * .6))
        fg = ink(mix(fill, d, .22), c)
        card += f'<clipPath id="certCounterClip"><rect x="{win[0]:.1f}" y="{win[1]:.1f}" width="{win[2]:.1f}" height="{win[3]:.1f}" rx="12"/></clipPath>'
        card += f'<g clip-path="url(#certCounterClip)">' + txt(num, win[0] + win[2] / 2, win[1] + win[3] / 2 + ns * .36 + roll, ns, fg, 900, 'middle') + '</g>'
        card += path(f'M{win[0] + 6} {win[1] + win[3] / 2}H{win[0] + 18}M{win[0] + win[2] - 18} {win[1] + win[3] / 2}H{win[0] + win[2] - 6}', fg, 3, extra='opacity=".5"')
        card += self.hourglass(px + pw - 62, py + ph / 2, clamp(days / L), c, warn)
        card += txt('DAYS LEFT', win[0] + win[2] / 2, py + ph + 34, 28, d, 900, 'middle')
        # Life bar with the days_to mark (the expire contact).
        bx, by, bw, bh = self.BAR
        card += rect(bx, by + 12, bw, bh, mix(paper, d, .12), bh / 2, d, 2.5)
        fx_ = self.bar_x(p, days)
        if fx_ - bx > 2:card += rect(bx, by + 12, fx_ - bx, bh, fill, bh / 2, d, 2.5)
        mx = self.bar_x(p, p['days_to'])
        card += path(f'M{mx} {by + 2}V{by + bh + 22}', d, 4) + path(f'M{mx - 9} {by - 4}H{mx + 9}L{mx} {by + 8}Z', d, 2, WARN if not renew else c['accent'])
        # Seal, signature and the curled corner.
        card += self.seal(cx + 80, y1 - 70, 40, c, age)
        sx0 = cx + 190
        card += path(f'M{sx0} {y1 - 74}C{sx0 + 20} {y1 - 110} {sx0 + 30} {y1 - 60} {sx0 + 50} {y1 - 92}S{sx0 + 80} {y1 - 70} {sx0 + 104} {y1 - 96}', d, 3)
        card += path(f'M{sx0 - 4} {y1 - 62}H{sx0 + 120}', mix(d, paper, .4), 2.5)
        if age > .2:
            o = clamp((age - .2) / .6)
            for k, (ex, ey, rx, ry) in enumerate(((cx + 70, cy + 160, 22, 12), (x1 - 60, cy + 46, 16, 10), (cx + 46, y1 - 46, 26, 14), (mid + 30, y1 - 40, 14, 8))):
                card += f'<ellipse cx="{ex}" cy="{ey}" rx="{rx}" ry="{ry}" fill="{STAIN}" opacity="{.22 * o:.3f}" transform="rotate({-18 + k * 23} {ex} {ey})"/>'
        if f > 2:
            flap = f'M{x1} {y1 - f:.1f}L{x1 - f:.1f} {y1}Q{x1 - f * .98:.1f} {y1 - f * .62:.1f} {x1 - f * .9:.1f} {y1 - f * .9:.1f}Q{x1 - f * .5:.1f} {y1 - f * 1.02:.1f} {x1} {y1 - f:.1f}Z'
            card += path(flap, d, 0, d, 'transform="translate(-6 -4)" opacity=".2"') + path(flap, d, 3, mix(paper, d, .14))
            card += g(path(f'M{x1 - f * .82:.1f} {y1 - f * .84:.1f}L{x1 - f * .2:.1f} {y1 - f * .78:.1f}', '#FFFFFF', 3), opacity=.4)
        # Warning badge pops in as the days run low.
        if warn > .05:
            wx, wy, ws = x1 - 22, py + 4, 30 + 6 * settle(clamp(after), 1)
            tri = f'M{wx} {wy - ws}L{wx + ws * 1.1:.1f} {wy + ws * .8:.1f}H{wx - ws * 1.1:.1f}Z'
            card += g(path(tri, d, 4, '#FFD23F') + txt('!', wx, wy + ws * .62, ws * 1.15, d, 900, 'middle'), 0, 0, 0, 1, 1, warn)
        # Renew: shine sweep across fresh paper, the imprint and sparkles.
        if renew and after > 0:
            if after < .45:
                s = after / .45;sx = lerp(cx - 200, x1 + 200, ease(s))
                card += f'<clipPath id="certSheetClip"><path d="{sheet}"/></clipPath>'
                card += f'<g clip-path="url(#certSheetClip)"><path d="M{sx - 60:.1f} {cy}L{sx + 10:.1f} {cy}L{sx - 150:.1f} {y1}L{sx - 220:.1f} {y1}Z" fill="#FFFFFF" opacity="{.55 * (1 - s):.3f}"/></g>'
            pop = 1 + .2 * (1 - ease(min(1.0, after * 3)));mark = c['accent'] if c['accent'] != c['light'] else c['primary'];fg2 = ink(mark, c)
            imp = path(StampGate._rough_rect(210, 70, seed=2), mark, 5, mark, extra='opacity=".93"') + path(StampGate._rough_rect(190, 52, 11, 1.4, 5), fg2, 2, extra='opacity=".55"')
            imp += txt(p['stamp'], 0, 13, label_size(p['stamp'], 170, 36), fg2, 900, 'middle')
            card += g(imp, self.STAMP_X, self.PAPER_Y - 28, -8, pop, opacity=min(1.0, after * 5))
        body += g(card, 0, 0, shake * .6)
        # Ledge in front of the sheet's foot.
        body += g(rect(-244, -110, 468, 26, d, 6), 5, 6, opacity=.18) + rect(-244, -110, 468, 26, c['secondary'], 6, d, 3) + g(rect(-236, -106, 300, 6, '#FFFFFF', 3), opacity=.3)
        for rx in (-226, 206):body += f'<circle cx="{rx}" cy="-97" r="5" fill="{c["metal"]}" stroke="{d}" stroke-width="2"/>'
        if renew:
            fy = self.stamp_y(p, pose);u = t_in(t, tc) if action else 0
            if action and .3 < u and after < .3:
                k = (u - .3) / .7 if after == 0 else 1 - after / .3
                body += f'<ellipse cx="{self.STAMP_X}" cy="{self.PAPER_Y + 4}" rx="{40 + 60 * k:.1f}" ry="6" fill="{d}" opacity="{.18 * k:.3f}"/>'
            body += self.stamp_arm(p, c, fy, True)
            if action:
                body += burst(self.STAMP_X, self.PAPER_Y - 30, clamp(after * 2.2), c, 10, 110, 190)
                if .15 < after < .9:
                    from motif_rigs.library2 import LockAndKey
                    o = 1 - (after - .15) / .75
                    for k, (sx_, sy_, r0) in enumerate(((cx - 20, cy + 60, 24), (x1 + 22, cy + 150, 20), (cx - 24, y1 - 200, 16), (x1 + 18, y1 - 70, 22))):
                        sc = ease(clamp((after - .15) * 4 - k * .2))
                        if sc > 0:body += LockAndKey._sparkle(sx_, sy_, r0 * sc, c['pop'] if k % 2 else c['accent'], c, o)
        return body

    def seams(self, p, pose):
        start, end, action, t = pose
        if not action:pose = (start, end, self.actions['run'], 1.0)
        if p['mode'] == 'renew':
            pair = ((self.STAMP_X, self.stamp_y(p, pose)), (self.STAMP_X, self.PAPER_Y))
            return {'cert-contact': pair, 'stamp-card': pair}
        y = self.BAR[1] + 12 + self.BAR[3] / 2
        pair = ((self.bar_x(p, self.days(p, pose)), y), (self.bar_x(p, p['days_to']), y))
        return {'cert-contact': pair, 'counter-mark': pair}


register(Certificate(
    name='certificate', description='One certificate card that keeps its identity: the site\'s domain, its issuer, a padlock seal and a big days-left counter. Expire mode ticks the days down while the paper ages; renew mode stamps the same card, it turns fresh and the counter rolls back up. Expiry, lifetimes, automatic renewal, HTTPS, licences.',
    params_schema={'type': 'object', 'properties': {
        'mode': {'enum': ['expire', 'renew']}, 'domain': {'type': 'string', 'minLength': 1, 'maxLength': 20},
        'issuer': {'type': 'string', 'maxLength': 16}, 'days_from': {'type': 'integer', 'minimum': 0, 'maximum': 365},
        'days_to': {'type': 'integer', 'minimum': 0, 'maximum': 365}, 'stamp': {'type': 'string', 'maxLength': 10}},
        'required': ['mode', 'domain', 'days_from', 'days_to'], 'additionalProperties': False},
    defaults={'mode': 'expire', 'domain': 'yoursite.com', 'issuer': "Let's Encrypt", 'days_from': 90, 'days_to': 3, 'stamp': 'RENEWED'},
    states=('idle', 'done'),
    actions={'run': Action('run', 'idle', 'done', 66, 'cert-contact', 46)},
    bot_slot={'x': 300, 'y': 0, 'scale': .24, 'role': 'watches the days run down, then cheers as the stamp renews the same card'},
    tags=('certificate', 'expire', 'expires', 'lasts', 'days', 'renew', 'renews', 'automatic', 'https', 'ssl', 'tls', 'licence', 'license', 'deadline'),
    footprint=(-290, -760, 580, 760)))
