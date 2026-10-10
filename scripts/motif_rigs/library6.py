"""Knowledge vault: one second-brain machine that carries a whole how-to film.

Built for the first reel adaptation (2026-10-10): a talking-head reel about
building an AI second brain with Claude and Obsidian, retold in Motif's paper
style. The lesson of the quality rounds was that objects and consequences must
stay connected, so instead of a new metaphor per step the film keeps one
machine on screen and every beat changes it:

  forget   no vault yet: saved items rain through a leaky paper brain, land in
           a heap on the floor and fade grey. Contact: the last item lands.
  setup    the vault stands empty (a RAW crate, a WIKI pinboard, a gantry claw
           and the brain on top); the two folder labels slap on. Contact: the
           WIKI label meets its mount.
  collect  labelled items (ARTICLE, BOOK, PODCAST...) arc into the RAW crate.
           Contact: the last item lands on the pile.
  compile  Claude's claw shuttles from the crate to the board while new wiki
           pages appear, each pinned with a string to a page it links to;
           the claw pins the last one. Contact: that page meets its slot.
  ask      a question card slides in, the pages it draws on light up with
           numbered badges, and the answer card drops in with matching
           citation chips. Contact: the answer card settles.
  save     the claw lifts that answer card onto the board as a new page; the
           page counter ticks up and the brain fills further. Contact: the
           page meets its slot.
  check    a magnifier sweeps the pages, one goes red with a warning tab, the
           claw swaps in a fresh copy and ticks pop on every page. Contact:
           the fresh page meets the flagged slot.

The brain on top fills with colour as pages are added: the "gets smarter"
claim drawn directly. Every mode starts in the state the previous one ends
in, so consecutive beats read as one continuing machine.

Same contract as library.py: original authored SVG through palette roles; no
reference frame was traced or copied (style inputs: docs/STYLE_BIBLE.md and
docs/style-reference-analysis.md). Status: DRAFT (awaiting Mayowa approval).
"""
import math

from motif_rigs import register
from motif_rigs.base import Action, Rig, ease, ease_in, lerp
from motif_rigs.library import ink, label_size, settle, t_after, t_in
from motif_rigs.library2 import burst
from motif_rigs.library5 import WARN, clamp, mix, smooth
from motif_ui_components import card, g, path, rect, txt

GREEN = '#2FA36B'          # semantic "checked" green, the same in every palette
GREY = '#9A9A94'           # forgotten paper
MAX_PAGES = 8


def seg(u, a, b):
    """Local progress of u across [a, b], clamped to [0, 1]."""
    return clamp((u - a) / max(1e-9, b - a))


class KnowledgeVault(Rig):
    CRATE = (-290, -300, 250, 260)             # x, y, w, h (back panel); front wall from y -150
    CRATE_FRONT = -118
    BOARD = (0, -600, 300, 560)
    PAGE = (132, 96)
    COLS = (80, 220)
    ROWS = (-528, -416, -304, -192)
    RAIL = -640
    BRAIN = (0, -722)
    REST = (0, -590)                            # claw rest (card top-centre)
    QUESTION = (-165, -560, 236, 92)            # centre x, centre y, w, h
    ANSWER = (-165, -425, 236, 104)
    LOBES = ((-95, -8, 46), (-52, -42, 50), (8, -52, 52), (64, -38, 48), (102, 0, 42),
             (68, 34, 44), (10, 40, 48), (-52, 34, 46), (-98, 24, 38))

    # Geometry ---------------------------------------------------------------

    def slot(self, i):
        return self.COLS[i % 2], self.ROWS[i // 2]

    def pile_at(self, k):
        """Centre and tilt of the k-th raw item in the crate."""
        x0, y0, w, h = self.CRATE
        return x0 + w / 2 + (-34, 30, -12, 38, -40, 14)[k % 6], -112 - k * 30, (-9, 7, -4, 10, -7, 5)[k % 6]

    def heap_at(self, k):
        """Centre and tilt of the k-th forgotten item on the floor heap."""
        col, row = k % 5, k // 5
        return -240 + col * 120 + (row % 2) * 50 + (-10, 12, -6, 8, 0)[col], -44 - row * 60, (-12, 8, -5, 14, -9, 6, 11)[k % 7]

    def counts(self, p):
        a = min(p['pages_from'], len(p['pages']));b = min(max(p['pages_to'], a), len(p['pages']))
        return a, b

    def phase(self, p, pose):
        """(t, tc, after): normalised time, contact time, post-contact progress."""
        start, end, action, t = pose;tc = self.contact_t('run')
        if not action:t = 1.0 if start == 'done' else 0.0
        return t, tc, t_after(t, tc)

    # Claw path ----------------------------------------------------------------

    def claw(self, p, t, tc):
        """(x, y, carrying) of the claw's card top-centre for this time, or None at rest."""
        mode = p['mode'];u = t_in(t, tc);a, b = self.counts(p)
        if mode in ('compile', 'save', 'check'):
            if mode == 'compile':src = (self.pile_at(max(0, len(p['items']) - 1))[0], self.pile_at(max(0, len(p['items']) - 1))[1] - 28);dst = self.slot(max(0, b - 1))
            elif mode == 'save':src = (self.ANSWER[0], self.ANSWER[1] - self.ANSWER[3] / 2);dst = self.slot(min(a, MAX_PAGES - 1))
            else:src = (-165, -700);dst = self.slot(p['flag'])
            top = dst[1] - self.PAGE[1] / 2;hover = -600
            if t <= tc:
                if u < .22:return (lerp(self.REST[0], src[0], ease(u / .22)), lerp(self.REST[1], hover, ease(u / .22)), False)
                if u < .36:return (src[0], lerp(hover, src[1], ease(seg(u, .22, .36))), False)
                if u < .48:return (src[0], lerp(src[1], hover, ease(seg(u, .36, .48))), True)
                if u < .74:return (lerp(src[0], dst[0], ease(seg(u, .48, .74))), hover, True)
                return (dst[0], lerp(hover, top, ease_in(seg(u, .74, 1.0))), True)
            k = ease(seg(t_after(t, tc), .1, .6))
            return (lerp(dst[0], self.REST[0], k), lerp(top, self.REST[1], k), False)
        return None

    # Parts --------------------------------------------------------------------

    def brain(self, level, c, leaky=False, glow=0.0):
        bx, by = self.BRAIN;d = c['dark'];shell = GREY if leaky else c['light']
        out = ''
        lobes = [(bx + x, by + y, r) for x, y, r in self.LOBES]
        out += ''.join(f'<circle cx="{x + 6}" cy="{y + 8}" r="{r}" fill="{d}" opacity=".16"/>' for x, y, r in lobes)
        out += ''.join(f'<circle cx="{x}" cy="{y}" r="{r + 4}" fill="{d}"/>' for x, y, r in lobes)
        out += ''.join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{mix(shell, c["secondary"], .25)}"/>' for x, y, r in lobes)
        if level > 0:
            top = by + 96 - 196 * level;fill = c['pop'] if c['pop'] not in (c['light'], c['dark']) else c['accent']
            clip = ''.join(f'<circle cx="{x}" cy="{y}" r="{r}"/>' for x, y, r in lobes)
            out += f'<clipPath id="kvBrainClip">{clip}</clipPath><g clip-path="url(#kvBrainClip)">'
            wave = f'M{bx - 160} {top:.1f}' + ''.join(f'Q{bx - 140 + 40 * k} {top + (8 if k % 2 else -8):.1f} {bx - 120 + 40 * k} {top:.1f}' for k in range(8))
            out += path(wave + f'V{by + 120}H{bx - 160}Z', fill, 0, fill) + path(wave, '#FFFFFF', 4, extra='opacity=".45"') + '</g>'
        # Folds: the two hemispheres and their wrinkles.
        out += path(f'M{bx + 4} {by - 92}C{bx - 12} {by - 40} {bx + 18} {by + 20} {bx + 2} {by + 82}', d, 4)
        for fx, fy, s in ((-70, -20, 1), (-40, 22, -1), (52, -10, 1), (82, 26, -1), (-96, 18, 1), (40, -56, -1)):
            x, y = bx + fx, by + fy
            out += path(f'M{x - 22} {y}C{x - 10} {y - 16 * s} {x + 4} {y + 14 * s} {x + 22} {y - 4 * s}', d, 3.5)
        out += g(path(f'M{bx - 110} {by - 30}A60 60 0 0 1 {bx - 40} {by - 86}', '#FFFFFF', 6), opacity=.45)
        if leaky:
            for hx, hy, rx in ((-70, 62, 18), (-10, 78, 22), (52, 66, 16), (-112, 44, 12)):
                out += f'<ellipse cx="{bx + hx}" cy="{by + hy}" rx="{rx}" ry="{rx * .55:.1f}" fill="{d}"/>'
        if glow > 0:
            from motif_rigs.library2 import LockAndKey
            for k, (sx, sy, r) in enumerate(((-150, -60, 20), (150, -40, 24), (-120, 70, 14), (140, 70, 16))):
                sc = ease(clamp(glow * 3 - k * .4)) * (1 - glow)
                if sc > 0:out += LockAndKey._sparkle(bx + sx, by + sy, r * (.4 + sc), c['accent'] if k % 2 else c['pop'], c, 1)
        return out

    def page(self, title, c, fill=None, hi=0.0, number=None, tick=0.0, flagged=0.0, flag_label='', alpha=1.0):
        """A wiki page card centred on (0, 0) with a pin at its top."""
        w, h = self.PAGE;d = c['dark'];base = fill or c['light']
        base = mix(base, mix(WARN, '#FFFFFF', .35), flagged)
        out = ''
        if hi > 0:out += rect(-w / 2 - 9, -h / 2 - 9, w + 18, h + 18, 'none', 14, c['accent'] if c['accent'] != base else c['pop'], 7).replace('<rect', f'<rect opacity="{hi:.3f}"')
        out += g(card(w, h, base, .08), -w / 2, -h / 2)
        fs = label_size(title, w - 18, 25)
        out += txt(title, 0, -h / 2 + 34, fs, ink(base, c), 900, 'middle')
        for k, lw in enumerate((.74, .58, .66)):
            out += rect(-w / 2 + 16, -h / 2 + 50 + k * 12, (w - 32) * lw, 6, mix(base, d, .28), 3)
        out += f'<circle cx="0" cy="{-h / 2 + 4}" r="8" fill="{c["secondary"] if c["secondary"] != base else c["primary"]}" stroke="{d}" stroke-width="2.5"/>'
        if number is not None and hi > 0:
            out += g(f'<circle r="17" fill="{c["accent"]}" stroke="{d}" stroke-width="3"/>' + txt(str(number), 0, 7, 20, ink(c['accent'], c), 900, 'middle'), w / 2 - 4, -h / 2 + 2, 0, ease(clamp(hi * 1.4)))
        if flagged > 0:
            tab = g(rect(-50, -15, 100, 30, WARN, 6, d, 2.5) + txt(flag_label, 0, 7, label_size(flag_label, 90, 17), '#FFFFFF', 900, 'middle'), 0, h / 2 - 2, -6, ease(clamp(flagged * 1.5)))
            out += tab
        if tick > 0:
            out += g(f'<circle r="16" fill="{GREEN}" stroke="{d}" stroke-width="3"/>' + path('M-7 0L-2 6L8 -6', '#FFFFFF', 4), -w / 2 + 6, h / 2 - 6, 0, ease(clamp(tick * 1.6)) + .15 * settle(clamp(tick), 1))
        return g(out, 0, 0, 0, 1, 1, alpha) if alpha < 1 else out

    def item(self, label, k, c, grey=0.0, q=0.0):
        """A raw saved item (article, book, podcast...) centred on (0, 0)."""
        cols = [c['primary'], c['accent'], c['secondary'], c['pop'], c['metal'], c['primary']]
        col = cols[k % len(cols)]
        if col in (c['light'],):col = c['secondary']
        col = mix(col, GREY, grey);d = c['dark']
        out = g(card(104, 58, col, .1), -52, -29)
        out += rect(-44, -20, 22, 18, mix(col, '#FFFFFF', .5), 3, d, 2) + rect(-16, -16, 52, 4, mix(col, d, .35), 2) + rect(-16, -8, 38, 4, mix(col, d, .35), 2)
        out += txt(label, 0, 20, label_size(label, 92, 17), ink(col, c), 900, 'middle')
        if q > 0:out += g(f'<circle r="15" fill="{c["light"]}" stroke="{d}" stroke-width="2.5"/>' + txt('?', 0, 8, 22, d, 900, 'middle'), 40, -24, 0, ease(clamp(q * 1.8)))
        return out

    def crate_back(self, c):
        x, y, w, h = self.CRATE;d = c['dark'];wood = c['secondary'] if c['secondary'] not in (c['wall'],) else c['primary']
        out = g(rect(x, y, w, h, d, 10), 6, 8, opacity=.16) + rect(x, y, w, h, mix(wood, d, .18), 10, d, 3.5)
        for k in range(1, 4):out += path(f'M{x + 8} {y + k * h / 4:.1f}H{x + w - 8}', mix(wood, d, .4), 3)
        return out

    def crate_front(self, c, label, label_k=1.0):
        x, y, w, h = self.CRATE;d = c['dark'];wood = c['secondary'] if c['secondary'] not in (c['wall'],) else c['primary']
        fy = self.CRATE_FRONT;out = rect(x - 6, fy, w + 12, -40 - fy, wood, 8, d, 3.5)
        for k in range(1, 3):out += path(f'M{x + 4} {fy + k * (-40 - fy) / 3:.1f}H{x + w - 4}', mix(wood, d, .3), 3)
        for nx in (x + 10, x + w - 10):
            for ny in (fy + 12, -54):out += f'<circle cx="{nx}" cy="{ny}" r="4.5" fill="{c["metal"]}" stroke="{d}" stroke-width="2"/>'
        if label_k > 0:out += self.label_tag(label, x + w / 2, fy + 40, 150, c, c['light'], label_k, -3)
        return out

    def label_tag(self, text, x, y, w, c, fill, k, angle):
        """A folder label that drops in and slaps onto (x, y); k = 0 above frame, 1 landed."""
        h = 48;s = label_size(text, w - 24, 30);dy = -260 * (1 - ease_in(clamp(k)))
        tab = rect(-w / 2 + 10, -h / 2 - 14, 54, 18, mix(fill, c['dark'], .1), 5, c['dark'], 2.5)
        body = tab + g(card(w, h, fill, .08), -w / 2, -h / 2) + txt(text, 0, s * .36, s, ink(fill, c), 900, 'middle')
        return g(body, x, y + dy, angle)

    def board(self, c, label, label_k, pages_n, stamp=None, stamp_k=0.0):
        x, y, w, h = self.BOARD;d = c['dark'];frame = c['primary']
        cork = mix(c['secondary'] if c['secondary'] != frame else c['pop'], '#E2C08F', .7)
        out = g(rect(x, y, w, h, d, 12), 6, 8, opacity=.16) + rect(x, y, w, h, frame, 12, d, 3.5)
        out += rect(x + 14, y + 16, w - 28, h - 32, cork, 6, d, 2.5) + rect(x + 14, y + 16, w - 28, h - 32, 'url(#worldPaper)', 6).replace('<rect', '<rect opacity=".18"')
        for k in range(14):
            px, py = x + 26 + (k * 53) % (w - 50), y + 40 + (k * 97) % (h - 80)
            out += f'<circle cx="{px}" cy="{py}" r="2.2" fill="{mix(cork, d, .35)}"/>'
        if label_k > 0:out += self.label_tag(label, x + w / 2, y - 6, 150, c, c['light'], label_k, 2)
        # Page counter on the bottom rail.
        num = str(pages_n);out += rect(x + w / 2 - 70, -98, 140, 40, d, 8) + txt(f'PAGES {num}', x + w / 2, -71, 22, c['light'], 900, 'middle')
        if stamp and stamp_k > 0:
            st = g(rect(-96, -24, 192, 48, GREEN, 8, d, 3) + txt(stamp, 0, 9, label_size(stamp, 176, 24), '#FFFFFF', 900, 'middle'), x + w / 2, y + 56, -5, 1 + .25 * (1 - ease(clamp(stamp_k * 2))))
            out += g(st, 0, 0, 0, 1, 1, clamp(stamp_k * 4))
        return out

    def gantry(self, c, claw, carrying_svg=''):
        """Rail across the top, two posts, the carriage and claw (claw = (x, y) card top-centre)."""
        d = c['dark'];m = c['metal'];out = ''
        for px in (-302, 309):out += rect(px - 7, self.RAIL, 14, -40 - self.RAIL, m, 4, d, 3)
        out += g(rect(-312, self.RAIL - 14, 632, 26, d, 8), 5, 6, opacity=.18) + rect(-312, self.RAIL - 14, 632, 26, m, 8, d, 3)
        out += ''.join(f'<circle cx="{-290 + k * 58}" cy="{self.RAIL - 1}" r="3.5" fill="{d}" opacity=".45"/>' for k in range(11))
        cx, cy = claw;arm = c['accent'] if c['accent'] != c['light'] else c['primary']
        out += rect(cx - 46, self.RAIL - 30, 92, 40, arm, 10, d, 3) + f'<circle cx="{cx - 28}" cy="{self.RAIL + 12}" r="8" fill="{m}" stroke="{d}" stroke-width="2.5"/><circle cx="{cx + 28}" cy="{self.RAIL + 12}" r="8" fill="{m}" stroke="{d}" stroke-width="2.5"/>'
        top = self.RAIL + 10;bottom = cy - 30
        if bottom > top:out += rect(cx - 5, top, 10, bottom - top, d, 3) + rect(cx - 2, top, 3, bottom - top, '#FFFFFF', 1).replace('<rect', '<rect opacity=".35"')
        out += carrying_svg
        out += rect(cx - 30, cy - 34, 60, 22, arm, 7, d, 3)
        for s in (-1, 1):out += path(f'M{cx + s * 24} {cy - 14}L{cx + s * 34} {cy + 4}L{cx + s * 22} {cy + 16}', d, 9) + path(f'M{cx + s * 24} {cy - 14}L{cx + s * 34} {cy + 4}L{cx + s * 22} {cy + 16}', m, 5)
        return out, (cx, self.RAIL - 10)

    def counter(self, c):
        d = c['dark'];top = c['primary'] if c['primary'] != c['wall'] else c['secondary']
        out = g(rect(-320, -42, 640, 14, d, 6), 0, 34, opacity=.15)
        out += rect(-320, -42, 640, 22, mix(top, d, .15), 6, d, 3) + g(rect(-312, -38, 380, 5, '#FFFFFF', 3), opacity=.3)
        for lx in (-300, 284):out += rect(lx, -22, 16, 22, c['metal'], 3, d, 2.5)
        return out

    def logo_badge(self, p, at, c):
        if not p.get('logo'):return ''
        from motif_brand import sticker
        return g(sticker(p['logo'], 50, 0), at[0], at[1] - 26)

    # Drawing -----------------------------------------------------------------

    def draw(self, p, pose, c):
        t, tc, after = self.phase(p, pose);mode = p['mode']
        if mode == 'forget':return self.draw_forget(p, t, tc, after, c)
        u = t_in(t, tc);d = c['dark'];a, b = self.counts(p);items = p['items'];n_items = len(items)
        titles = p['pages']
        # Which pages are on the board, and how.
        shown = {};crate_n = n_items;claw_card = '';level = a / MAX_PAGES;glow = 0.0;stamp_k = 0.0
        board_n = a;flag_k = 0.0;fresh = False
        if mode == 'setup':crate_n = 0;level = 0.0
        elif mode == 'collect':crate_n = 0
        for i in range(a):shown[i] = {}
        claw = self.claw(p, t, tc);carry = False
        if claw:carry = claw[2];claw = claw[:2]
        if mode == 'compile':
            new = list(range(a, b));last = new[-1] if new else None
            for j, i in enumerate(new[:-1]):
                k = seg(u, .12 + .6 * j / max(1, len(new) - 1), .3 + .6 * j / max(1, len(new) - 1)) if t <= tc else 1.0
                if k > 0:shown[i] = {'pop': k}
            if last is not None and t > tc:shown[last] = {}
            crate_n = max(0, n_items - (1 if (t > tc or (claw and carry)) else 0))
            board_n = a + sum(1 for i in new if i in shown)
            level = board_n / MAX_PAGES;glow = clamp(after * 1.4) if t > tc else 0.0
            if carry and t <= tc and last is not None:claw_card = g(self.page(titles[last], c), claw[0], claw[1] + self.PAGE[1] / 2)
        elif mode == 'save':
            slot = min(a, MAX_PAGES - 1)
            if t > tc:shown[slot] = {'fill': c['accent'] if c['accent'] != c['light'] else None};board_n = a + 1;level = board_n / MAX_PAGES;glow = clamp(after * 1.4)
            elif carry:claw_card = g(self.answer_card(p, c, chips=1.0, w=self.PAGE[0], h=self.PAGE[1]), claw[0], claw[1] + self.PAGE[1] / 2)
        elif mode == 'ask':
            for j, i in enumerate(p['cite']):
                if i in shown:shown[i] = {'hi': seg(u, .35 + .15 * j, .5 + .15 * j) if t <= tc else 1.0, 'number': j + 1}
        elif mode == 'check':
            f = p['flag']
            sweep = seg(u, 0, .45)
            flag_k = seg(u, .3, .45) if t <= tc else 0.0
            if f in shown and t <= tc:shown[f] = {'flagged': flag_k}
            if t > tc:
                for i in shown:shown[i] = {**shown[i], 'tick': seg(after, .1 + .08 * i, .35 + .08 * i)}
                stamp_k = seg(after, .55, .8)
            if carry and t <= tc:
                claw_card = g(self.page(titles[f], c, fill=mix(c['light'], GREEN, .25)), claw[0], claw[1] + self.PAGE[1] / 2)
        body = self.counter(c)
        # Board and its pages.
        wiki_k = 1.0;raw_k = 1.0
        if mode == 'setup':raw_k = seg(u, .15, .5) if t <= tc else 1.0;wiki_k = seg(u, .55, 1.0) if t <= tc else 1.0
        body += self.board(c, p['wiki_label'], wiki_k, board_n, p.get('stamp') if mode == 'check' else None, stamp_k)
        body += self.strings(shown, c, mode, u if t <= tc else 1.0, a)
        for i, st in shown.items():
            sx, sy = self.slot(i);pop = st.get('pop', 1.0)
            if pop <= 0:continue
            sc = .4 + .6 * ease(pop) + .12 * settle(clamp(pop), 1) if pop < 1 else 1.0
            jolt = 0.0
            if mode in ('compile', 'save', 'check') and t > tc and i == (b - 1 if mode == 'compile' else (min(a, MAX_PAGES - 1) if mode == 'save' else p['flag'])):jolt = 10 * settle(clamp(after * 1.5), 1)
            if mode == 'save' and i == min(a, MAX_PAGES - 1):title = p['answer']
            else:title = titles[i] if i < len(titles) else ''
            fill = st.get('fill') or (mix(c['light'], GREEN, .25) if mode == 'check' and i == p['flag'] and t > tc else None)
            body += g(self.page(title, c, fill=fill, hi=st.get('hi', 0), number=st.get('number'), tick=st.get('tick', 0), flagged=st.get('flagged', 0), flag_label=p['flag_label']), sx, sy + jolt, 0, sc)
        if mode == 'check' and t <= tc:
            # The old page falls away as the fresh copy comes down.
            f = p['flag'];fx, fy = self.slot(f)
            if u > .74:
                k = seg(u, .74, 1.0)
                body += g(self.page(titles[f], c, flagged=1.0, flag_label=p['flag_label']), fx + 40 * k, fy + 260 * ease_in(k), 18 * k, 1, 1, 1 - k)
        if mode == 'check' and t <= tc and u < .5:
            body += self.magnifier(p, c, u)
        # Crate with the raw pile.
        body += self.crate_back(c)
        for k in range(crate_n):
            x, y, a_ = self.pile_at(k);body += g(self.item(items[k], k, c), x, y, a_)
        if mode == 'collect':
            for k in range(n_items):
                land = tc * (.3 + .7 * (k + 1) / n_items);launch = land - .3 * tc
                tt = t if t <= tc else 1.0
                if tt < launch:continue
                x1, y1, a1 = self.pile_at(k);x0, y0 = -470 + 30 * k, -820
                if tt >= land:x, y, ang = x1, y1, a1;k_ = 1.0
                else:
                    k_ = (tt - launch) / (land - launch);x = lerp(x0, x1, ease(k_));y = lerp(y0, y1, ease_in(k_)) - 180 * math.sin(k_ * math.pi);ang = lerp(-40, a1, k_)
                bump = 6 * settle(clamp((tt - land) / (.2 * tc)), 1) if tt >= land else 0
                body += g(self.item(items[k], k, c), x, y + bump, ang)
        body += self.crate_front(c, p['raw_label'], raw_k)
        if mode in ('ask', 'save'):body += self.ask_cards(p, c, t, tc, after, mode)
        # Gantry, claw, brain on top.
        cpos = claw or self.REST
        gan, carriage = self.gantry(c, cpos, claw_card)
        body += gan + self.logo_badge(p, carriage, c)
        if mode in ('compile', 'save') and t > tc:body += burst(*self.slot(b - 1 if mode == 'compile' else min(a, MAX_PAGES - 1)), clamp(after * 2.2), c, 10, 60, 130)
        if mode == 'check' and t > tc:body += burst(*self.slot(p['flag']), clamp(after * 2.2), c, 10, 60, 130)
        body += g(rect(-18, self.RAIL - 40, 36, 30, c['metal'], 4, d, 3))
        body += self.brain(level, c, glow=glow)
        return body

    def strings(self, shown, c, mode, u, a):
        """Red-string links between pinned pages: page i ties to i - 1 (and i - 3 when it exists)."""
        col = c['pop'] if c['pop'] not in (c['light'], c['dark']) else WARN;out = ''
        for i, st in sorted(shown.items()):
            k = st.get('pop', 1.0)
            for j in (i - 1, i - 3):
                if j < 0 or j not in shown or (j == i - 3 and i % 2 == 0):continue
                (x1, y1), (x2, y2) = self.slot(i), self.slot(j);y1 -= self.PAGE[1] / 2 - 4;y2 -= self.PAGE[1] / 2 - 4
                xe, ye = lerp(x2, x1, ease(k)), lerp(y2, y1, ease(k))
                mx, my = (x2 + xe) / 2, (y2 + ye) / 2 + 26
                out += path(f'M{x2} {y2}Q{mx:.1f} {my:.1f} {xe:.1f} {ye:.1f}', c['dark'], 6, extra='opacity=".35"') + path(f'M{x2} {y2}Q{mx:.1f} {my:.1f} {xe:.1f} {ye:.1f}', col, 5)
        return out

    def magnifier(self, p, c, u):
        """The lens sweeps the pages in order and stops on the flagged one."""
        f = p['flag'];a, _ = self.counts(p);n = max(1, a)
        k = seg(u, 0, .32);pos = min(f, k * n)
        i0 = int(pos);fr = pos - i0;(x0, y0) = self.slot(min(i0, n - 1));(x1, y1) = self.slot(min(i0 + 1, n - 1, f))
        x, y = lerp(x0, x1, ease(fr)), lerp(y0, y1, ease(fr))
        d = c['dark'];o = 1 - seg(u, .4, .5)
        lens = f'<circle cx="{x:.1f}" cy="{y:.1f}" r="62" fill="#FFFFFF" opacity=".28"/><circle cx="{x:.1f}" cy="{y:.1f}" r="62" fill="none" stroke="{d}" stroke-width="12"/><circle cx="{x:.1f}" cy="{y:.1f}" r="62" fill="none" stroke="{c["metal"]}" stroke-width="6"/>'
        lens += path(f'M{x + 44:.1f} {y + 44:.1f}L{x + 104:.1f} {y + 104:.1f}', d, 24) + path(f'M{x + 46:.1f} {y + 46:.1f}L{x + 102:.1f} {y + 102:.1f}', c['secondary'], 14)
        lens += path(f'M{x - 38:.1f} {y - 22:.1f}A44 44 0 0 1 {x - 10:.1f} {y - 44:.1f}', '#FFFFFF', 6, extra='opacity=".7"')
        return g(lens, 0, 0, 0, 1, 1, o)

    def answer_card(self, p, c, chips=1.0, w=None, h=None):
        """The answer: a bright card with citation chips [1] [2] [3]. Centred on (0, 0)."""
        w = w or self.ANSWER[2];h = h or self.ANSWER[3];d = c['dark'];fill = c['accent'] if c['accent'] != c['light'] else c['secondary']
        small = w < 150
        out = g(card(w, h, fill, .08), -w / 2, -h / 2)
        fs = label_size(p['answer'], w - 20, 21 if small else 28)
        out += txt(p['answer'], 0, -h / 2 + (30 if small else 38), fs, ink(fill, c), 900, 'middle')
        n = len(p['cite']);cw = 22 if small else 36;gap = 6 if small else 10;x0 = -(n * cw + (n - 1) * gap) / 2
        for j in range(n):
            k = ease(clamp(chips * n - j))
            if k <= 0:continue
            cx = x0 + j * (cw + gap) + cw / 2;cy = h / 2 - (20 if small else 28)
            out += g(rect(-cw / 2, -12 if small else -15, cw, 24 if small else 30, c['light'], 6, d, 2.5) + txt(str(j + 1), 0, 6 if small else 8, 15 if small else 20, d, 900, 'middle'), cx, cy, 0, k)
        out += f'<circle cx="0" cy="{-h / 2 + 4}" r="8" fill="{c["secondary"] if c["secondary"] != fill else c["primary"]}" stroke="{d}" stroke-width="2.5"/>' if small else ''
        return out

    def ask_cards(self, p, c, t, tc, after, mode):
        qx, qy, qw, qh = self.QUESTION;ax, ay, aw, ah = self.ANSWER;d = c['dark'];u = t_in(t, tc);out = ''
        # Question card.
        if mode == 'ask':qk = ease(seg(u, 0, .3)) if t <= tc else 1.0;qo = 1.0
        else:qk = 1.0;qo = 1 - seg(t_in(t, tc), 0, .25) if t <= tc else 0.0
        if qo > 0:
            q = g(card(qw, qh, c['light'], .08), -qw / 2, -qh / 2) + txt('ASK', -qw / 2 + 16, -qh / 2 + 26, 17, mix(d, c['light'], .35), 900)
            words = p['question'].split();lines, cur = [], ''
            for w_ in words:
                if len(cur + ' ' + w_) > 13 and cur:lines.append(cur);cur = w_
                else:cur = (cur + ' ' + w_).strip()
            lines.append(cur)
            for k, line in enumerate(lines[:2]):q += txt(line, 0, -qh / 2 + (54 if len(lines) > 1 else 64) + k * 26, label_size(line, qw - 24, 24), d, 900, 'middle')
            q += path(f'M{-qw / 2 + 40} {qh / 2 - 2}L{-qw / 2 + 30} {qh / 2 + 22}L{-qw / 2 + 64} {qh / 2 - 2}Z', d, 2.5, c['light'])
            out += g(q, lerp(-560, qx, qk), qy, -2, 1, 1, qo)
        # Answer card: drops in, settles at the contact (ask); is lifted away by the claw (save).
        if mode == 'ask':
            if t > tc or u > .55:
                k = seg(u, .55, 1.0) if t <= tc else 1.0
                y = lerp(-900, ay, ease_in(k)) + (8 * settle(clamp(after * 1.5), 1) if t > tc else 0)
                chips = clamp(after * 1.6) if t > tc else 0.0
                # Citation threads from the lit pages to the chips.
                if t > tc:
                    n = len(p['cite']);cw, gap = 36, 10;x0 = -(n * cw + (n - 1) * gap) / 2
                    for j, i in enumerate(p['cite']):
                        sx, sy = self.slot(i);ex, ey = ax + x0 + j * (cw + gap) + cw / 2, ay + ah / 2 - 28
                        k2 = ease(clamp(after * 2 - j * .25))
                        if k2 <= 0:continue
                        mx, my = lerp(ex, sx - 60, k2), lerp(ey, sy, k2)
                        out += path(f'M{ex:.1f} {ey:.1f}Q{(ex + mx) / 2:.1f} {min(ey, my) - 60:.1f} {mx:.1f} {my:.1f}', c['accent'], 4, extra='stroke-dasharray="2 10" opacity=".9"')
                out += g(self.answer_card(p, c, chips), ax, y, 2)
        elif t <= tc and u < .36:
            out += g(self.answer_card(p, c, 1.0), ax, ay, 2)
        return out

    def draw_forget(self, p, t, tc, after, c):
        """No vault yet: items fall through a leaky brain onto a heap and fade."""
        d = c['dark'];n = p['count'];items = p['items'];body = ''
        bx, by = self.BRAIN
        body += g(rect(-300, -12, 600, 12, d, 6), opacity=.15)
        tt = t if t <= tc else 1.0
        falling, landed = '', ''
        for k in range(n):
            land = tc * (.15 + .85 * (k + 1) / n);launch = land - .28 * tc
            x1, y1, a1 = self.heap_at(k);x0 = bx + (-70, 30, -20, 60, -50, 10)[k % 6]
            label = items[k % len(items)]
            grey = clamp(after * 1.6 - k * .06) if t > tc else 0.0
            if tt >= land:
                bump = 5 * settle(clamp((tt - land) / (.2 * tc)), 1)
                landed += g(self.item(label, k, c, grey, q=clamp(after * 1.6 - k * .08) if t > tc else 0), x1, y1 + bump, a1, 1.4)
            elif tt >= launch:
                k_ = (tt - launch) / (land - launch)
                x = lerp(x0, x1, ease(k_));y = lerp(-900, y1, ease_in(k_));ang = lerp(-25 + 10 * (k % 5), a1, k_)
                falling += g(self.item(label, k, c), x, y, ang, 1.4)
        body += falling + landed
        body += f'<g transform="translate({bx} {by + 60}) scale(1.45) translate({-bx} {-by})">{self.brain(0.0, c, leaky=True)}</g>'
        lab = p['label'];w = max(220, len(lab) * 24 + 50)
        body += g(card(w, 64, d, .05) + txt(lab, w / 2, 44, label_size(lab, w - 28, 36), c['light'], 900, 'middle'), -w / 2, -400 + 6 * math.sin(t * 12), -3)
        return body

    def seams(self, p, pose):
        start, end, action, t = pose
        if not action:pose = (start, end, self.actions['run'], 1.0)
        _, _, action, t = pose;tc = self.contact_t('run');t_ = min(t, tc);mode = p['mode'];a, b = self.counts(p)
        if mode == 'forget':
            k = p['count'] - 1;land = tc * (.15 + .85 * (k + 1) / p['count']);launch = land - .28 * tc
            x1, y1, _ = self.heap_at(k);x0 = self.BRAIN[0] + (-70, 30, -20, 60, -50, 10)[k % 6];k_ = clamp((t_ - launch) / (land - launch))
            pair = ((lerp(x0, x1, ease(k_)), lerp(-900, y1, ease_in(k_))), (x1, y1))
            return {'vault-contact': pair, 'item-heap': pair}
        if mode == 'setup':
            x, y, w, h = self.BOARD;k = seg(t_in(t_, tc), .55, 1.0)
            pair = ((x + w / 2, y - 6 - 260 * (1 - ease_in(k))), (x + w / 2, y - 6))
            return {'vault-contact': pair, 'label-mount': pair}
        if mode == 'collect':
            n = len(p['items']);k = n - 1;land = tc;launch = land - .3 * tc;x1, y1, _ = self.pile_at(k);x0, y0 = -470 + 30 * k, -820
            k_ = clamp((t_ - launch) / (land - launch))
            pair = ((lerp(x0, x1, ease(k_)), lerp(y0, y1, ease_in(k_)) - 180 * math.sin(k_ * math.pi)), (x1, y1))
            return {'vault-contact': pair, 'item-crate': pair}
        if mode == 'ask':
            ax, ay = self.ANSWER[:2];k = seg(t_in(t_, tc), .55, 1.0)
            pair = ((ax, lerp(-900, ay, ease_in(k))), (ax, ay))
            return {'vault-contact': pair, 'answer-desk': pair}
        cx, cy, _ = self.claw(p, t_, tc)
        dst = self.slot(b - 1 if mode == 'compile' else (min(a, MAX_PAGES - 1) if mode == 'save' else p['flag']))
        pair = ((cx, cy + self.PAGE[1] / 2), dst)
        return {'vault-contact': pair, 'page-slot': pair}

    def printed_text(self, p):
        mode = p['mode']
        if mode == 'forget':return [p['label']] + p['items']
        out = [p['raw_label'], p['wiki_label'], 'PAGES']
        if mode in ('collect', 'compile', 'ask', 'save', 'check'):out += p['items']
        a, b = self.counts(p)
        out += p['pages'][:b if mode == 'compile' else a]
        if mode in ('ask', 'save'):out += [p['question'], p['answer']]
        if mode == 'check':out += [p['flag_label'], p.get('stamp') or '']
        return [x for x in out if x]


register(KnowledgeVault(
    name='knowledge-vault',
    description='A second-brain machine that keeps its identity across beats: a RAW crate, a WIKI pinboard of linked pages, a gantry claw and a paper brain that fills as pages are added. Modes: forget (items fall through a leaky brain and fade), setup (folder labels slap on), collect (items arc into the crate), compile (the claw pins linked wiki pages), ask (cited answer card), save (the answer becomes a page), check (a lens finds an outdated page, the claw swaps it). Notes, wikis, knowledge bases, research, memory, second brains, personal knowledge management.',
    params_schema={'type': 'object', 'properties': {
        'mode': {'enum': ['forget', 'setup', 'collect', 'compile', 'ask', 'save', 'check']},
        'items': {'type': 'array', 'items': {'type': 'string', 'minLength': 1, 'maxLength': 10}, 'minItems': 1, 'maxItems': 6},
        'pages': {'type': 'array', 'items': {'type': 'string', 'minLength': 1, 'maxLength': 10}, 'minItems': 1, 'maxItems': MAX_PAGES},
        'pages_from': {'type': 'integer', 'minimum': 0, 'maximum': MAX_PAGES}, 'pages_to': {'type': 'integer', 'minimum': 0, 'maximum': MAX_PAGES},
        'count': {'type': 'integer', 'minimum': 3, 'maximum': 14}, 'label': {'type': 'string', 'maxLength': 16},
        'question': {'type': 'string', 'maxLength': 28}, 'answer': {'type': 'string', 'maxLength': 12},
        'cite': {'type': 'array', 'items': {'type': 'integer', 'minimum': 0, 'maximum': MAX_PAGES - 1}, 'minItems': 1, 'maxItems': 3},
        'flag': {'type': 'integer', 'minimum': 0, 'maximum': MAX_PAGES - 1}, 'flag_label': {'type': 'string', 'maxLength': 10},
        'stamp': {'type': ['string', 'null'], 'maxLength': 12},
        'raw_label': {'type': 'string', 'minLength': 1, 'maxLength': 8}, 'wiki_label': {'type': 'string', 'minLength': 1, 'maxLength': 8},
        'logo': {'type': ['string', 'null']}},
        'required': ['mode'], 'additionalProperties': False},
    defaults={'mode': 'collect', 'items': ['ARTICLE', 'BOOK', 'PODCAST', 'MEETING'], 'pages': ['IDEA', 'PEOPLE', 'PROJECTS', 'HABITS', 'TOOLS', 'READING', 'GOALS', 'NOTES'],
              'pages_from': 0, 'pages_to': 0, 'count': 10, 'label': 'SAVED', 'question': 'WHAT AM I MISSING?', 'answer': 'ANSWER',
              'cite': [0, 2, 3], 'flag': 1, 'flag_label': 'OUTDATED', 'stamp': 'CHECKED', 'raw_label': 'RAW', 'wiki_label': 'WIKI', 'logo': None},
    states=('idle', 'done'),
    actions={'run': Action('run', 'idle', 'done', 66, 'vault-contact', 46)},
    bot_slot={'x': -330, 'y': 0, 'scale': .22, 'role': 'feeds the crate, watches the claw and cheers as the brain fills'},
    tags=('knowledge', 'notes', 'wiki', 'brain', 'second', 'memory', 'research', 'library', 'obsidian', 'vault', 'folder', 'sources', 'organize', 'answer', 'question', 'cite', 'citations', 'smarter', 'remember', 'forget'),
    footprint=(-320, -800, 640, 800)))
