"""The first ten Motif rigs. Original designs: authored SVG geometry in the
Style Bible's cut-paper language, drawn through palette roles so every rig can
appear in any Motif palette. No reference frame was traced or copied; the only
style inputs are docs/STYLE_BIBLE.md and docs/style-reference-analysis.md.

Local origin (0, 0) is the floor under the rig's centre; y grows downward, so
everything stands at negative y. Each action reaches its contact exactly at its
contact frame: moving parts follow lerp(start, seam, ease(t / t_contact)) and
hold the seam afterwards, so the contact test is geometric, not visual.
"""
import math

from motif_rigs import register
from motif_rigs.base import Action, Rig, ease, ease_in, lerp
from motif_ui_components import card, g, path, rect, txt, bot


def label_size(text, width, cap=30):
    return min(cap, width / max(1, len(text) * .58))


def ink(fill, c):
    """Dark or light label colour, whichever reads on this fill (WCAG luminance)."""
    r, g_, b = (int(fill[i:i + 2], 16) / 255 for i in (1, 3, 5))
    lum = lambda v: v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4
    y = .2126 * lum(r) + .7152 * lum(g_) + .0722 * lum(b)
    return c['dark'] if (y + .05) / .07 >= 1.05 / (y + .05) else c['light']


def tag(text, x, y, w, c, fill=None, size=None, angle=0):
    """A small cut-paper label card centred on (x, y)."""
    h = 40;size = size or label_size(text, w - 16, 22)
    fill = fill or c['light']
    return g(card(w, h, fill, .08) + txt(text, w / 2, h / 2 + size * .36, size, ink(fill, c), 800, 'middle'), x - w / 2, y - h / 2, angle)


def mini_bot_head(x, y, s, c, hat=None):
    """Tiny Motif Bot head for windows and crowds: cream shell, dark display, teal eyes."""
    body = (rect(-26, -22, 52, 44, '#F4EBD8', 12, '#DCCDB3', 3) + rect(-19, -15, 38, 26, '#202C32', 7)
            + '<circle cx="-8" cy="-2" r="3.4" fill="#A6E5D6"/><circle cx="8" cy="-2" r="3.4" fill="#A6E5D6"/>'
            + path('M-13 -22L-17 -36M13 -22L17 -36', '#56BFB1', 4) + '<circle cx="-17" cy="-37" r="4" fill="#56BFB1"/><circle cx="17" cy="-37" r="4" fill="#56BFB1"/>')
    if hat:body += path('M-24 -24Q0 -44 24 -24Z', hat, 2, hat)
    return g(body, x, y, s=s)


def t_in(t, t_c):
    """Progress toward the contact (1.0 exactly at the contact frame)."""
    return min(1.0, t / t_c) if t_c > 0 else 1.0


def t_after(t, t_c):
    return 0.0 if t <= t_c else (t - t_c) / max(1e-9, 1 - t_c)


def settle(u, amp=1.0):
    """Damped post-contact response that starts and ends at zero."""
    return amp * math.sin(u * math.pi * 3) * math.exp(-u * 4) if 0 < u < 1 else 0.0


# 1 Overflow vehicle --------------------------------------------------------------

class OverflowVehicle(Rig):
    ROOF = -300

    def layout(self, p):
        seats = p['seats'];spacing = 440 / seats
        return [(-220 + spacing * (i + .5), -215) for i in range(seats)]

    def roof_riders(self, p):
        extra = max(0, p['riders'] - p['seats'])
        return [(-180 + 360 * (i + .5) / max(1, extra), self.ROOF) for i in range(extra)]

    def draw(self, p, pose, c):
        start, end, action, t = pose;tc = self.contact_t('overflow') if action else 0
        body = path('M-270 -30Q-280 -300 -230 -300H230Q275 -300 275 -230V-30Z', c['dark'], 0, c['dark'], 'transform="translate(6 9)" opacity=".18"')
        body += path('M-270 -30Q-280 -300 -230 -300H230Q275 -300 275 -230V-30Z', c['primary'], 3, c['primary'])
        body += rect(-262, -110, 534, 22, c['secondary'], 4) + g(card(130, 30, c['light'], .06) + txt(p['label'], 65, 21, label_size(p['label'], 118, 18), c['dark'], 900, 'middle'), -65, -290)
        for x, y in self.layout(p):
            body += rect(x - 20, y - 45, 40, 70, '#CFE6EA', 8, c['dark'], 2)
        for i, (x, y) in enumerate(self.layout(p)):
            if i < p['riders']:body += mini_bot_head(x, y - 4, .62, c, c['accent'] if i % 3 == 0 else None)
        for wx in (-170, 170):
            body += f'<circle cx="{wx}" cy="-30" r="38" fill="{c["dark"]}"/><circle cx="{wx}" cy="-30" r="16" fill="{c["metal"]}"/>'
        riders = self.roof_riders(p);n = len(riders)
        for i, (x, y) in enumerate(riders):
            if start == 'overflow' and not action:fy, sq = y, 0
            elif action:
                # Riders land in turn; the last one lands exactly at the contact frame.
                land = tc * (i + 1) / n;u = t_in(t, land) if land else 1
                fy = lerp(-640, y, ease_in(u)) if u < 1 else y;sq = settle(t_after(t, land) * 2, .5) if u >= 1 else 0
            else:continue
            body += bot(x, fy, 0, s=.11, face='surprised' if i % 2 else 'happy', pose='celebrating' if i % 2 else 'standing', jitter=False, impact=max(0, sq))
        return body + tag(f'{p["riders"]} riders / {p["seats"]} seats', 0, -60, 220, c, c['light'])

    def seams(self, p, pose):
        start, end, action, t = pose;riders = self.roof_riders(p)
        if not riders:return {'roof': ((0, self.ROOF), (0, self.ROOF))}
        x, y = riders[-1];tc = self.contact_t('overflow')
        fy = lerp(-640, y, ease_in(t_in(t, tc))) if action else y
        return {'roof': ((x, fy), (x, self.ROOF))}


register(OverflowVehicle(
    name='overflow-vehicle', description='A bus with fixed seats; extra riders pile on the roof. Demand exceeds capacity.',
    params_schema={'type': 'object', 'properties': {'seats': {'type': 'integer', 'minimum': 2, 'maximum': 10}, 'riders': {'type': 'integer', 'minimum': 0, 'maximum': 18}, 'label': {'type': 'string', 'maxLength': 14}}, 'required': ['seats', 'riders', 'label'], 'additionalProperties': False},
    defaults={'seats': 6, 'riders': 10, 'label': 'FREE TIER'}, states=('seated', 'overflow'),
    actions={'overflow': Action('overflow', 'seated', 'overflow', 45, 'roof', 30)},
    bot_slot={'x': 250, 'y': 0, 'scale': .22, 'role': 'driver waving from the door side'}, tags=('capacity', 'demand', 'limit', 'crowd', 'queue', 'scarcity'),
    footprint=(-280, -660, 560, 680)))


# 2 Plate stack ----------------------------------------------------------------

class PlateStack(Rig):
    PLATE = 26

    def plate_y(self, k):
        """Origin of plate k; its underside (y + 6) rests on the rim below (y - 20) or the counter (-46)."""
        return -52 - k * self.PLATE

    def _counter(self, c):
        """Buffet counter: floor shadow, panelled cabinet with knobs, top slab with lip; top surface at y=-46."""
        d = c['dark'];s = g(rect(-236, -8, 472, 12, d, 6), opacity=.16)
        s += g(rect(-220, -40, 440, 40, d, 6), 6, 4, opacity=.15) + rect(-220, -40, 440, 40, c['primary'], 6, d, 3)
        s += rect(-216, -8, 432, 6, d, 3)
        for x in (-206, 132):
            s += rect(x, -30, 74, 20, 'none', 4, d, 2) + g(rect(x + 4, -27, 40, 3, '#FFFFFF', 1.5), opacity=.3)
            s += f'<circle cx="{x + (62 if x > 0 else 12)}" cy="-20" r="4" fill="{c["metal"]}" stroke="{d}" stroke-width="2"/>'
        s += g(rect(-230, -46, 460, 14, d, 6), 4, 4, opacity=.18) + rect(-230, -46, 460, 14, c['secondary'], 6, d, 3)
        s += g(rect(-222, -43, 300, 3, '#FFFFFF', 1.5), opacity=.45) + path('M-226 -35H226', d, 2, extra='opacity=".2"')
        return s

    def _props(self, c):
        """Napkin stack (left) and a cutlery pot (right), both standing on the counter top."""
        d = c['dark'];s = ''
        for k, col in enumerate((c['light'], c['pop'], c['light'])):
            y = -58 - k * 10;s += rect(-214 + k * 2, y, 66 - k * 4, 11, col, 3, d, 2)
        s += path('M-190 -88V-58', c['accent'], 4)
        for dx, a, kind in ((-12, -12, 0), (2, 4, 1), (14, 14, 0)):
            stem = rect(-3, -66, 6, 60, c['metal'], 3, d, 2)
            head = (path('M-7 -84V-66H7V-84M0 -84V-66', d, 2.5, c['metal']) if kind == 0 else f'<ellipse cx="0" cy="-74" rx="9" ry="12" fill="{c["metal"]}" stroke="{d}" stroke-width="2"/>')
            s += g(stem + head, 186 + dx, -70, a)
        pot = 'M160 -112H212L206 -48H166Z'
        s += path(pot, d, 0, d, 'transform="translate(4 4)" opacity=".18"') + path(pot, d, 3, c['accent'])
        s += path('M164 -92H208M166 -70H206', d, 2, extra='opacity=".3"') + g(path('M170 -106L174 -54', '#FFFFFF', 4), opacity=.35)
        return s

    def _plate(self, y, k, c, wob=0):
        """One dinner plate: ink rim, inner well, coloured band with dots, glint, foot ring shadow."""
        d = c['dark'];rim = 'M-110 0Q-118 -16 -96 -20H96Q118 -16 110 0Q100 8 0 8Q-100 8 -110 0Z'
        col = [c['primary'], c['accent'], c['pop']][k % 3]
        s = path(rim, d, 0, d, 'transform="translate(3 5)" opacity=".2"') + path(rim, d, 3, c['light'])
        s += path('M-100 2Q0 13 100 2', d, 2, extra='opacity=".22"') + path('M-84 -16Q0 -11 84 -16', d, 2, extra='opacity=".2"')
        s += path('M-80 -8H80', col, 4) + ''.join(f'<circle cx="{x}" cy="-8" r="2.6" fill="{col}"/>' for x in (-94, 94))
        s += g(path('M-104 -4Q-108 -14 -90 -17', '#FFFFFF', 3), opacity=.6)
        return g(s, 0, y, wob)

    def draw(self, p, pose, c):
        start, end, action, t = pose;tc = self.contact_t('stack') if action else 0
        n0, n1 = p['count_from'], p['count_to'];resting = n1 if (start == 'tall' and not action) else n0
        body = self._counter(c) + self._props(c)
        lean = settle(t_after(t, tc), 3) if action else 0
        for k in range(resting):body += self._plate(self.plate_y(k), k, c, lean * k / max(1, resting))
        if action:
            # Plates n0 .. n1-1 drop in turn; the last lands exactly at the contact frame.
            for j, k in enumerate(range(n0, n1)):
                land = tc * (j + 1) / max(1, n1 - n0);u = t_in(t, land)
                y = lerp(-900, self.plate_y(k), ease_in(u))
                body += self._plate(y, k, c, lean * k / max(1, n1) if u >= 1 else 4 * (1 - u))
            # Puff lines at the top plate the moment it lands.
            after = t_after(t, tc)
            if 0 < after < .4:
                o = 1 - after / .4;yt = self.plate_y(n1 - 1);r = 124 + 30 * after / .4
                body += path(f'M{-r} {yt - 6}L{-r - 22} {yt - 16}M{r} {yt - 6}L{r + 22} {yt - 16}M{-r + 4} {yt + 6}H{-r - 22}M{r - 4} {yt + 6}H{r + 22}', c['dark'], 4, extra=f'opacity="{o:.3f}"')
        body += tag(p['label'], 0, -14, 260, c, c['light'])
        return body

    def seams(self, p, pose):
        start, end, action, t = pose;k = p['count_to'] - 1;tc = self.contact_t('stack')
        y = lerp(-900, self.plate_y(k), ease_in(t_in(t, tc))) if action else self.plate_y(k)
        return {'top-plate': ((0, y + 6), (0, self.plate_y(k - 1) - 20 if k else -46))}


register(PlateStack(
    name='plate-stack', description='Plates pile onto a buffet counter. Workload, backlog or consumption growing.',
    params_schema={'type': 'object', 'properties': {'count_from': {'type': 'integer', 'minimum': 0, 'maximum': 16}, 'count_to': {'type': 'integer', 'minimum': 1, 'maximum': 18}, 'label': {'type': 'string', 'maxLength': 18}}, 'required': ['count_from', 'count_to', 'label'], 'additionalProperties': False},
    defaults={'count_from': 3, 'count_to': 12, 'label': 'TOKENS USED'}, states=('short', 'tall'),
    actions={'stack': Action('stack', 'short', 'tall', 54, 'top-plate', 40)},
    bot_slot={'x': -270, 'y': 0, 'scale': .24, 'role': 'carries the next plate'}, tags=('backlog', 'growth', 'usage', 'workload', 'pile', 'consumption'),
    footprint=(-240, -560, 480, 560)))


# 3 Hydraulic press ----------------------------------------------------------------

class HydraulicPress(Rig):
    OBJ_TOP = -230

    @staticmethod
    def _rivets(pts, c, r=4.5):
        return ''.join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c["metal"]}" stroke="{c["dark"]}" stroke-width="2"/>' for x, y in pts)

    def _frame(self, c):
        """Base with hazard band, two riveted columns with foot collars, crown beam with rivets and lower lip."""
        d = c['dark'];s = g(rect(-262, -8, 524, 12, d, 6), opacity=.16)
        s += rect(-250, -40, 500, 40, d, 6) + g(rect(-242, -36, 330, 4, '#FFFFFF', 2), opacity=.2)
        s += ''.join(path(f'M{x} -12L{x + 10} -30H{x + 22}L{x + 12} -12Z', c['secondary'], 0, c['secondary']) for x in range(-124, 112, 26))
        s += rect(-130, -32, 260, 22, 'none', 3, c['metal'], 2) + self._rivets([(-160, -20), (160, -20), (-236, -20), (236, -20)], c, 4)
        for x0 in (-230, 190):
            s += g(rect(x0, -640, 40, 600, d, 6), 6, 0, opacity=.18) + rect(x0, -640, 40, 600, c['metal'], 6, d, 3)
            s += g(rect(x0 + 6, -628, 7, 576, '#FFFFFF', 3), opacity=.3) + g(rect(x0 + 28, -628, 6, 576, '#000000', 3), opacity=.12)
            s += path(f'M{x0 + 4} -460H{x0 + 36}M{x0 + 4} -300H{x0 + 36}', d, 2, extra='opacity=".25"')
            s += rect(x0 - 8, -66, 56, 26, c['primary'], 5, d, 3) + self._rivets([(x0 + 6, -53), (x0 + 34, -53)], c, 3.5)
        s += g(rect(-250, -690, 500, 60, d, 10), 6, 6, opacity=.18) + rect(-250, -690, 500, 60, c['primary'], 10, d, 3)
        s += g(rect(-240, -684, 340, 6, '#FFFFFF', 3), opacity=.35) + g(rect(-246, -642, 492, 9, '#000000', 4), opacity=.15)
        s += self._rivets([(x, y) for x in (-226, -186, -146, 146, 186, 226) for y in (-674, -648)], c, 4)
        # Cylinder housing under the crown: the ram slides out of it.
        s += rect(-46, -634, 92, 40, c['metal'], 6, d, 3) + path('M-46 -620H46M-46 -606H46', d, 2, extra='opacity=".3"') + g(rect(-38, -630, 12, 32, '#FFFFFF', 4), opacity=.3)
        return s

    def _gauge(self, c, level):
        """Pressure gauge on the right column, hose up to the crown; needle swings with level 0..1."""
        d = c['dark'];gx, gy = 210, -470;s = path(f'M{gx + 14} {gy - 26}C246 -540 248 -600 238 -630', d, 9) + path(f'M{gx + 14} {gy - 26}C246 -540 248 -600 238 -630', c['secondary'], 5)
        s += f'<circle cx="{gx + 5}" cy="{gy + 6}" r="32" fill="{d}" opacity=".18"/><circle cx="{gx}" cy="{gy}" r="32" fill="{c["metal"]}" stroke="{d}" stroke-width="3"/>'
        s += f'<circle cx="{gx}" cy="{gy}" r="24" fill="{c["light"]}" stroke="{d}" stroke-width="2"/>'
        red = f'M{gx + 24 * math.cos(math.radians(-30)):.1f} {gy + 24 * math.sin(math.radians(-30)):.1f}A24 24 0 0 1 {gx + 24 * math.cos(math.radians(40)):.1f} {gy + 24 * math.sin(math.radians(40)):.1f}'
        s += path(red, c['pop'], 6)
        for k in range(5):
            a = math.radians(-210 + k * 62.5);s += path(f'M{gx + 17 * math.cos(a):.1f} {gy + 17 * math.sin(a):.1f}L{gx + 22 * math.cos(a):.1f} {gy + 22 * math.sin(a):.1f}', d, 2)
        s += g(path('M-3 0L0 -20L3 0Z', d, 2.5, d), gx, gy, -120 + 220 * level) + f'<circle cx="{gx}" cy="{gy}" r="4" fill="{d}"/>'
        s += g(path(f'M{gx - 20} {gy - 8}A22 22 0 0 1 {gx - 6} {gy - 21}', '#FFFFFF', 3), opacity=.6)
        return s

    def draw(self, p, pose, c):
        start, end, action, t = pose;tc = self.contact_t('press') if action else 0
        u = t_in(t, tc) if action else (1 if start == 'crushed' else 0);squash = ease(t_after(t, tc)) if action else (1 if start == 'crushed' else 0)
        plate_y = lerp(-600, self.OBJ_TOP, ease_in(u)) + 90 * squash;d = c['dark']
        body = self._frame(c) + self._gauge(c, min(1.0, .15 + .65 * ease_in(u) + .2 * squash))
        # Chrome ram rod out of the cylinder.
        rod_h = plate_y - 40 + 598
        if rod_h > 0:body += rect(-13, -598, 26, rod_h, c['metal'], 4, d, 3) + g(rect(-8, -596, 5, rod_h - 4, '#FFFFFF', 2), opacity=.45)
        # The block: soft floor shadow, paper card, side creases once crushed.
        h = (-self.OBJ_TOP - 40) * (1 - .45 * squash);w = 200 * (1 + .35 * squash)
        body += g(rect(-w / 2 - 6, -46, w + 20, 8, d, 4), opacity=.2)
        blk = card(w, h, c['secondary'], .1) + g(rect(8, 8, w - 40, 6, '#FFFFFF', 3), opacity=.35)
        blk += path(f'M12 {h - 14}H{w - 12}', d, 2, extra='opacity=".18"')
        if squash > .05:
            o = min(1.0, squash * 2)
            blk += path(f'M0 {h * .3}L14 {h * .42}L4 {h * .55}M{w} {h * .35}L{w - 16} {h * .5}L{w - 4} {h * .62}', d, 3, extra=f'opacity="{o:.3f}"')
        blk += txt(p['object'], w / 2, h / 2 + 8, label_size(p['object'], w - 20, 26), ink(c['secondary'], c), 900, 'middle')
        body += g(blk, -w / 2, -40 - h)
        # Approach shadow on the block's top, tightening as the plate closes in.
        if .3 < u < 1:
            k = (u - .3) / .7;body += f'<ellipse cx="0" cy="{self.OBJ_TOP + 6}" rx="{60 + 70 * k:.1f}" ry="5" fill="{d}" opacity="{.2 * k:.3f}"/>'
        # Press plate with guide arms riding collars on both columns.
        py = plate_y - 40
        for sd in (-1, 1):
            body += rect(150 if sd > 0 else -190, py + 12, 40, 14, c['metal'], 3, d, 3)
            body += rect(184 if sd > 0 else -236, py + 4, 52, 30, c['primary'], 6, d, 3) + self._rivets([(sd * 210, py + 19)], c, 4)
        body += g(rect(-150, py, 300, 40, d, 8), 5, 6, opacity=.2) + rect(-150, py, 300, 40, c['accent'], 8, d, 3)
        body += g(rect(-140, py + 5, 200, 5, '#FFFFFF', 2), opacity=.4) + g(rect(-146, py + 29, 292, 8, '#000000', 3), opacity=.18)
        body += self._rivets([(-128, py + 20), (-96, py + 20), (96, py + 20), (128, py + 20)], c, 4) + rect(-30, py - 6, 60, 10, c['metal'], 3, d, 3)
        for k, sd in enumerate((-1, 1, -1, 1) if squash > .05 else ()):
            body += path(f'M{sd * (w / 2 + 12):.1f} {-56 - (k // 2) * 26}l{20 * sd} {-6}', c['pop'], 6)
        if 0 < squash < 1:
            o = 1 - squash;sx = w / 2 + 18
            body += path(f'M{-sx} {-70}l-22 -10M{sx} {-70}l22 -10M{-sx} {-100}l-26 0M{sx} {-100}l26 0', d, 4, extra=f'opacity="{o:.3f}"')
        body += tag(p['force'], 0, -660, 240, c, c['light'])
        return body

    def seams(self, p, pose):
        start, end, action, t = pose;tc = self.contact_t('press')
        u = t_in(t, tc) if action else 1
        h = (-self.OBJ_TOP - 40) * (1 - .45 * ease(t_after(t, tc)) if action else 1)
        return {'plate-object': ((0, lerp(-600, self.OBJ_TOP, ease_in(u)) + 90 * (ease(t_after(t, tc)) if action else 0)), (0, -40 - h))}


register(HydraulicPress(
    name='hydraulic-press', description='A press plate comes down on a labelled block and flattens it. Pressure, cost cuts, compression.',
    params_schema={'type': 'object', 'properties': {'object': {'type': 'string', 'maxLength': 12}, 'force': {'type': 'string', 'maxLength': 16}}, 'required': ['object', 'force'], 'additionalProperties': False},
    defaults={'object': 'PRICE', 'force': 'COMPETITION'}, states=('open', 'crushed'),
    actions={'press': Action('press', 'open', 'crushed', 48, 'plate-object', 24)},
    bot_slot={'x': 300, 'y': 0, 'scale': .22, 'role': 'pulls the lever'}, tags=('pressure', 'compression', 'cost', 'squeeze', 'cut', 'price'),
    footprint=(-260, -700, 520, 700)))


# 4 Race track -------------------------------------------------------------------

class RaceTrack(Rig):
    START, FINISH = -140, 230

    def lane_y(self, p, i):return -60 - i * (360 / len(p['labels']))

    def runner_x(self, p, i, t, tc):
        target = lerp(self.START, self.FINISH, p['progress'][i])
        return lerp(self.START, target, ease(t_in(t, tc)))

    def draw(self, p, pose, c):
        start, end, action, t = pose;tc = self.contact_t('race') if action else 1;t = t if action else (1 if start == 'finish' else 0)
        n = len(p['labels']);body = rect(-280, -440, 560, 420, c['floor'], 14)
        colours = [c['primary'], c['accent'], c['secondary'], c['pop']]
        for i in range(n):
            y = self.lane_y(p, i);body += rect(-270, y - 40, 540, 72, c['light'] if i % 2 else c['wall'], 8)
            x = self.runner_x(p, i, t, tc);bob = math.sin(t * 40 + i) * 3 if t < tc else 0
            body += g(card(110, 46, colours[i % 4], .1) + txt(p['labels'][i], 55, 31, label_size(p['labels'][i], 96, 20), ink(colours[i % 4], c), 900, 'middle'), x - 110, y - 35 + bob)
            body += f'<circle cx="{x - 85:.1f}" cy="{y + 14:.1f}" r="10" fill="{c["dark"]}"/><circle cx="{x - 25:.1f}" cy="{y + 14:.1f}" r="10" fill="{c["dark"]}"/>'
        for k in range(12):body += rect(self.FINISH, -440 + k * 35, 14, 35, c['dark'] if k % 2 else c['light'])
        win = max(range(n), key=lambda i: p['progress'][i])
        if t > tc:body += g(path('M0 0V-70', c['dark'], 4) + path('M0 -70L48 -58L0 -44Z', c['pop'], 2, c['pop']), self.FINISH + 30, self.lane_y(p, win) - 30, a=settle(t_after(t, tc), 8))
        return body

    def seams(self, p, pose):
        start, end, action, t = pose;tc = self.contact_t('race');win = max(range(len(p['labels'])), key=lambda i: p['progress'][i])
        x = self.runner_x(p, win, t if action else 1, tc)
        return {'finish-line': ((x, self.lane_y(p, win)), (self.FINISH, self.lane_y(p, win)))}


register(RaceTrack(
    name='race-track', description='Two to four labelled racers; the leader reaches the finish line. Competition, benchmark, speed.',
    params_schema={'type': 'object', 'properties': {'labels': {'type': 'array', 'items': {'type': 'string', 'maxLength': 10}, 'minItems': 2, 'maxItems': 4},
                                                    'progress': {'type': 'array', 'items': {'type': 'number', 'minimum': 0, 'maximum': 1}, 'minItems': 2, 'maxItems': 4}},
                   'required': ['labels', 'progress'], 'additionalProperties': False},
    defaults={'labels': ['OPEN', 'CLOSED', 'LOCAL'], 'progress': [1.0, .62, .8]}, states=('start', 'finish'),
    actions={'race': Action('race', 'start', 'finish', 60, 'finish-line', 44)},
    bot_slot={'x': -300, 'y': 0, 'scale': .2, 'role': 'waves the start flag beside the track'}, tags=('competition', 'benchmark', 'speed', 'ranking', 'versus'),
    footprint=(-280, -470, 560, 470)))


# 5 Balance scale ----------------------------------------------------------------

class BalanceScale(Rig):
    PIVOT = (0, -420);ARM = 200;HANG = 150;TILT = 14

    def angle(self, p, t, tc):
        sign = 1 if p['right_weight'] > p['left_weight'] else -1 if p['right_weight'] < p['left_weight'] else 0
        return sign * self.TILT * ease(t_in(t, tc))

    def pan_bottom(self, side, a):
        r = math.radians(a);px, py = self.PIVOT;x = px + side * self.ARM * math.cos(r);y = py + side * self.ARM * math.sin(r)
        return x, y + self.HANG

    def stop_top(self, p):
        side = 1 if p['right_weight'] > p['left_weight'] else -1
        return self.pan_bottom(side, self.angle(p, 1, 0))

    @staticmethod
    def _weight(col, c, w=44, h=34, knob=False):
        """One stacked weight block: ink outline, top-edge highlight, a small handle on the top row."""
        d = c['dark'];s = ''
        if knob:s += path(f'M{w / 2 - 8} 2V-6H{w / 2 + 8}V2', d, 4)
        s += rect(1, 1, w - 2, h - 2, col, 5, d, 3) + g(rect(5, 4, w - 16, 4, '#FFFFFF', 2), opacity=.45)
        s += g(rect(w - 9, 5, 4, h - 10, '#000000', 2), opacity=.15)
        return s

    def _dial(self, a, c):
        """Arc dial under the pivot with a needle that turns with the beam."""
        d = c['dark'];px, py = self.PIVOT;r0, r1 = 58, 96
        def pt(r, deg):return px + r * math.cos(math.radians(deg)), py + r * math.sin(math.radians(deg))
        (ax, ay), (bx, by), (cx_, cy_), (dx, dy) = pt(r1, 58), pt(r1, 122), pt(r0, 122), pt(r0, 58)
        fan = f'M{ax:.1f} {ay:.1f}A{r1} {r1} 0 0 1 {bx:.1f} {by:.1f}L{cx_:.1f} {cy_:.1f}A{r0} {r0} 0 0 0 {dx:.1f} {dy:.1f}Z'
        s = path(fan, d, 0, d, 'transform="translate(5 6)" opacity=".18"') + path(fan, d, 3, c['light'])
        for k in range(-3, 4):
            (x1, y1), (x2, y2) = pt(r1 - 4, 90 + k * 9), pt(r1 - (16 if k == 0 else 10), 90 + k * 9)
            s += path(f'M{x1:.1f} {y1:.1f}L{x2:.1f} {y2:.1f}', c['accent'] if k == 0 else d, 4 if k == 0 else 2.5)
        s += g(path(f'M-4 0L0 {r1 - 8}L4 0Z', d, 3, c['pop']), px, py, a)
        return s

    def draw(self, p, pose, c):
        start, end, action, t = pose;tc = self.contact_t('tip') if action else 1;t = t if action else (1 if start == 'tipped' else 0)
        a = self.angle(p, t, tc);px, py = self.PIVOT;d = c['dark']
        # Stepped plinth with feet, fluted pillar with collars.
        body = g(rect(-200, -10, 400, 14, d, 7), opacity=.16)
        body += rect(-150, -14, 30, 14, d, 4) + rect(120, -14, 30, 14, d, 4)
        body += g(rect(-160, -42, 320, 30, d, 8), 6, 6, opacity=.18) + rect(-160, -42, 320, 30, c['metal'], 8, d, 3) + g(rect(-150, -38, 220, 5, '#FFFFFF', 2), opacity=.35)
        body += rect(-100, -64, 200, 24, c['primary'], 8, d, 3) + g(rect(-92, -60, 120, 4, '#FFFFFF', 2), opacity=.3)
        body += g(rect(-18, py, 36, -py - 64, d, 6), 6, 0, opacity=.18) + rect(-18, py, 36, -py - 64, c['metal'], 6, d, 3)
        body += path(f'M-6 {py + 30}V-80M6 {py + 30}V-80', d, 2, extra='opacity=".3"') + g(rect(-13, py + 10, 5, -py - 84, '#FFFFFF', 2), opacity=.3)
        for cy in (-84, py + 104):body += rect(-28, cy, 56, 18, c['primary'], 6, d, 3)
        if p['left_weight'] != p['right_weight']:
            sx, sy = self.stop_top(p)
            body += g(rect(sx - 30, sy + 18, 60, -40 - sy - 18, d, 6), 6, 6, opacity=.18) + rect(sx - 30, sy + 18, 60, -40 - sy - 18, c['secondary'], 6, d, 3)
            body += path(f'M{sx - 30} {sy + 60}H{sx + 30}M{sx - 30} {sy + 100}H{sx + 30}', d, 2, extra='opacity=".3"')
            body += rect(sx - 44, sy, 88, 20, c['accent'], 8, d, 3) + g(rect(sx - 36, sy + 4, 50, 4, '#FFFFFF', 2), opacity=.4)
        body += self._dial(a, c)
        # Beam: ink-edged bar with a centre rib, end caps and hooks; pivot cap and finial on top.
        beam = rect(-self.ARM - 14, -11, 2 * self.ARM + 28, 22, c['primary'], 10, d, 3) + g(rect(-self.ARM, -7, 2 * self.ARM - 40, 5, '#FFFFFF', 2), opacity=.35)
        beam += path(f'M{-self.ARM + 30} 4H{-40}M40 4H{self.ARM - 30}', d, 2, extra='opacity=".25"')
        for side in (-1, 1):
            beam += f'<circle cx="{side * (self.ARM + 6)}" cy="0" r="16" fill="{c["secondary"]}" stroke="{d}" stroke-width="3"/>'
        body += g(g(beam, 6, 7, opacity=.15) + beam, px, py, a)
        body += path(f'M-40 {py + 12}L0 {py - 30}L40 {py + 12}Z', d, 3, c['primary'])
        body += f'<circle cx="{px}" cy="{py}" r="14" fill="{c["metal"]}" stroke="{d}" stroke-width="3"/><circle cx="{px}" cy="{py}" r="4" fill="{d}"/>'
        body += f'<circle cx="{px}" cy="{py - 40}" r="10" fill="{c["secondary"]}" stroke="{d}" stroke-width="3"/>'
        swing = settle(t_after(t, tc), 4)
        for side, label, weight in ((-1, p['left_label'], p['left_weight']), (1, p['right_label'], p['right_weight'])):
            bx, by = self.pan_bottom(side, a);top = by - self.HANG
            # Chains: dashed ink links over metal, from a ring under the beam end to the pan rim.
            ch = f'M{bx} {top + 14}L{bx - 70} {by - 24}M{bx} {top + 14}L{bx + 70} {by - 24}M{bx} {top + 14}L{bx} {by - 30}'
            body += path(ch, d, 7) + path(ch, c['metal'], 4) + path(ch, d, 2, extra='stroke-dasharray="3 7" opacity=".7"')
            body += f'<circle cx="{bx}" cy="{top + 10}" r="8" fill="none" stroke="{d}" stroke-width="6"/><circle cx="{bx}" cy="{top + 10}" r="8" fill="none" stroke="{c["metal"]}" stroke-width="3"/>'
            bowl = f'M{bx - 88} {by - 22}Q{bx} {by + 14} {bx + 88} {by - 22}Z'
            body += path(bowl, d, 0, d, 'transform="translate(5 7)" opacity=".18"') + path(bowl, d, 3, c['secondary'])
            body += g(path(f'M{bx - 70} {by - 16}Q{bx - 30} {by - 2} {bx + 10} {by - 4}', '#FFFFFF', 4), opacity=.35)
            for k in range(weight):
                body += g(self._weight(c['accent'] if side < 0 else c['pop'], c, knob=(k // 3 == (weight - 1) // 3)), bx - 66 + (k % 3) * 44, by - 56 - (k // 3) * 34, swing)
            body += rect(bx - 94, by - 28, 188, 10, c['metal'], 5, d, 3)
            body += tag(label, bx, by + 40, 190, c, c['light'], max(22, label_size(label, 150, 26)))
        return body

    def seams(self, p, pose):
        start, end, action, t = pose;tc = self.contact_t('tip');a = self.angle(p, t if action else 1, tc)
        side = 1 if p['right_weight'] > p['left_weight'] else -1
        return {'pan-stop': (self.pan_bottom(side, a), self.stop_top(p))}


register(BalanceScale(
    name='balance-scale', description='Two labelled pans; the heavier side tips down onto its stop. Trade-off, comparison, value.',
    params_schema={'type': 'object', 'properties': {'left_label': {'type': 'string', 'maxLength': 12}, 'right_label': {'type': 'string', 'maxLength': 12},
                                                    'left_weight': {'type': 'integer', 'minimum': 0, 'maximum': 9}, 'right_weight': {'type': 'integer', 'minimum': 0, 'maximum': 9}},
                   'required': ['left_label', 'right_label', 'left_weight', 'right_weight'], 'additionalProperties': False},
    defaults={'left_label': 'COST', 'right_label': 'VALUE', 'left_weight': 2, 'right_weight': 6}, states=('level', 'tipped'),
    actions={'tip': Action('tip', 'level', 'tipped', 45, 'pan-stop', 30)},
    bot_slot={'x': -290, 'y': 0, 'scale': .22, 'role': 'adds the last weight'}, tags=('tradeoff', 'comparison', 'value', 'weigh', 'versus', 'balance'),
    footprint=(-300, -480, 600, 480)))


# 6 Stacked meter (tower and rocket) --------------------------------------------------

class StackedMeter(Rig):
    BLOCK = 42

    def top(self, k):
        """Top edge of block k; block k's underside (top + BLOCK) rests on block k-1's top or the base (-40)."""
        return -40 - (k + 1) * self.BLOCK

    def draw(self, p, pose, c):
        start, end, action, t = pose;tc = self.contact_t('build') if action else 0
        n0, n1 = p['from'], p['to'];resting = n1 if (start == 'high' and not action) else n0
        body = rect(-140, -40, 280, 40, c['dark'], 6)
        cols = [c['primary'], c['secondary'], c['accent'], c['pop']]
        def block(k, y, a=0):return g(card(150, self.BLOCK, cols[k % 4], .1), -75, y, a)
        for k in range(resting):body += block(k, self.top(k))
        if action:
            for j, k in enumerate(range(n0, n1)):
                land = tc * (j + 1) / max(1, n1 - n0);u = t_in(t, land)
                body += block(k, lerp(-1000, self.top(k), ease_in(u)), 0 if u >= 1 else 6 * (1 - u))
        shown = n1 if (action and t >= tc) or (start == 'high' and not action) else n0
        top = self.top(max(0, (n1 if action and t >= tc else resting) - 1))
        if p['rocket']:body += path(f'M-75 {top}Q0 {top - 120} 75 {top}Z', c['pop'], 2, c['pop']) + f'<circle cx="0" cy="{top - 40}" r="16" fill="{c["light"]}" stroke="{c["dark"]}" stroke-width="3"/>'
        body += g(card(150, 54, c['light'], .06) + txt(f'{shown}{p["unit"]}', 75, 38, 30, c['dark'], 900, 'middle'), 110, top - 20)
        return body + tag(p['label'], 0, -14, 240, c, c['light'])

    def seams(self, p, pose):
        start, end, action, t = pose;k = p['to'] - 1;tc = self.contact_t('build')
        y = lerp(-1000, self.top(k), ease_in(t_in(t, tc))) if action else self.top(k)
        return {'top-block': ((0, y + self.BLOCK), (0, self.top(k - 1) if k else -40))}


register(StackedMeter(
    name='stacked-meter', description='Coloured blocks stack into a tower (optionally a rocket) with a live count. Growth, scale, momentum.',
    params_schema={'type': 'object', 'properties': {'from': {'type': 'integer', 'minimum': 0, 'maximum': 12}, 'to': {'type': 'integer', 'minimum': 1, 'maximum': 14},
                                                    'unit': {'type': 'string', 'maxLength': 4}, 'label': {'type': 'string', 'maxLength': 16}, 'rocket': {'type': 'boolean'}},
                   'required': ['from', 'to', 'unit', 'label', 'rocket'], 'additionalProperties': False},
    defaults={'from': 2, 'to': 9, 'unit': 'x', 'label': 'USERS', 'rocket': True}, states=('low', 'high'),
    actions={'build': Action('build', 'low', 'high', 50, 'top-block', 38)},
    bot_slot={'x': -230, 'y': 0, 'scale': .24, 'role': 'stacks the blocks'}, tags=('growth', 'scale', 'momentum', 'launch', 'increase', 'record'),
    footprint=(-140, -800, 420, 800)))


# 7 Thermometer star meter ---------------------------------------------------------

class Thermometer(Rig):
    BOTTOM, TOP = -120, -620

    def level(self, v):return lerp(self.BOTTOM, self.TOP, v / 100)

    def _mount(self, c):
        """Screwed wooden backing board, stepped stand and top cap with hanging ring."""
        d = c['dark'];s = g(rect(-170, -8, 340, 12, d, 6), opacity=.16)
        s += g(rect(-112, -676, 236, 630, d, 18), 6, 6, opacity=.18) + rect(-112, -676, 236, 630, c['primary'], 18, d, 3)
        s += g(rect(-102, -666, 12, 600, '#FFFFFF', 6), opacity=.25) + path('M-80 -640V-120M104 -640V-120', d, 2, extra='opacity=".14"')
        s += ''.join(f'<circle cx="{x}" cy="{y}" r="6" fill="{c["metal"]}" stroke="{d}" stroke-width="2"/>' + path(f'M{x - 3} {y - 3}L{x + 3} {y + 3}', d, 2) for x, y in ((-92, -656), (104, -656), (-92, -232), (104, -232)))
        s += rect(-160, -46, 320, 46, c['secondary'], 8, d, 3) + g(rect(-152, -42, 200, 5, '#FFFFFF', 2), opacity=.35)
        s += rect(-130, -64, 260, 22, c['metal'], 6, d, 3) + g(rect(-122, -60, 140, 4, '#FFFFFF', 2), opacity=.35)
        return s

    def draw(self, p, pose, c):
        start, end, action, t = pose;tc = self.contact_t('heat') if action else 1;t = t if action else (1 if start == 'hot' else 0)
        y = lerp(self.level(p['from']), self.level(p['to']), ease(t_in(t, tc)));d = c['dark'];heat = ease(t_in(t, tc))
        body = self._mount(c)
        # Glass tube: ink edge, faint bore, long glint; cap at the top.
        body += rect(30, -646, 100, 520, c['light'], 10, d, 3) + g(rect(116, -640, 8, 508, '#000000', 3), opacity=.08)
        body += g(rect(-70, -660, 140, 620, d, 70), 5, 6, opacity=.15) + rect(-70, -660, 140, 620, c['light'], 70, d, 4)
        body += g(rect(-36, -632, 72, 520, c['metal'], 30), opacity=.18)
        body += rect(-34, -676, 68, 22, c['metal'], 6, d, 3) + path('M-34 -665H34', d, 2, extra='opacity=".3"')
        # Bulb with inner ring and highlight.
        body += f'<circle cx="0" cy="-110" r="80" fill="{c["pop"]}" stroke="{d}" stroke-width="4"/>'
        body += f'<circle cx="0" cy="-110" r="62" fill="none" stroke="{d}" stroke-width="2" opacity=".18"/>'
        body += f'<ellipse cx="-30" cy="-140" rx="20" ry="13" fill="#FFFFFF" opacity=".4"/><circle cx="-46" cy="-116" r="5" fill="#FFFFFF" opacity=".35"/>'
        # Mercury column with a bright core and a meniscus line at its top.
        body += rect(-30, y, 60, -110 - y, c['pop'], 20) + g(rect(-18, y + 10, 10, max(0, -130 - y), '#FFFFFF', 5), opacity=.35)
        body += path(f'M-22 {y + 6}Q0 {y - 2} 22 {y + 6}', d, 2, extra='opacity=".25"')
        body += g(rect(-58, -630, 10, 470, '#FFFFFF', 5), opacity=.45) + g(rect(-56, -164, 6, 20, '#FFFFFF', 3), opacity=.45)
        for k in range(0, 101, 10):
            ty = self.level(k);major = k % 20 == 0
            body += path(f'M{40 if major else 52} {ty}H70', d, 3 if major else 2)
            if major:body += txt(str(k), 82, ty + 8, 22, d, 800)
        # Heat waves either side of the bulb, stronger as it warms.
        if heat > .05:
            for sd in (-1, 1):
                for j in range(2):
                    x = sd * (140 + j * 20);w = f'M{x} -96q{-8 * sd} -14 0 -28q{8 * sd} -14 0 -28'
                    body += path(w, c['pop'], 4, extra=f'opacity="{heat * (.9 - .3 * j):.3f}"')
        ty = self.level(p['to'])
        body += path(f'M-90 {ty}H90', c['accent'], 5) + path(f'M90 {ty - 10}L104 {ty}L90 {ty + 10}Z', d, 2, c['accent'])
        body += tag(p['target'], -190, ty, 160, c, c['secondary'])
        stars = p['stars'];after = t_after(t, tc)
        for k in range(stars):
            u = max(0.0, min(1.0, after * stars - k));s = ease(u) * (1 + settle(u, .3))
            if s > 0:
                st = path('M0 -30L9 -9L30 0L9 9L0 30L-9 9L-30 0L-9 -9Z', d, 3, c['secondary']) + g(path('M-3 -18L0 -8', '#FFFFFF', 3), opacity=.6)
                body += g(st, 150 + (k % 2) * 60, -560 + k * 70, a=20 * k, s=s)
        return body + tag(p['label'], 0, -20, 240, c, c['light'])

    def seams(self, p, pose):
        start, end, action, t = pose;tc = self.contact_t('heat')
        y = lerp(self.level(p['from']), self.level(p['to']), ease(t_in(t if action else 1, tc)))
        return {'mercury-target': ((0, y), (0, self.level(p['to'])))}


register(Thermometer(
    name='thermometer', description='A thermometer rises to a target mark, then stars pop. Hype, demand, heat, rating.',
    params_schema={'type': 'object', 'properties': {'from': {'type': 'number', 'minimum': 0, 'maximum': 100}, 'to': {'type': 'number', 'minimum': 0, 'maximum': 100},
                                                    'target': {'type': 'string', 'maxLength': 10}, 'label': {'type': 'string', 'maxLength': 16}, 'stars': {'type': 'integer', 'minimum': 0, 'maximum': 5}},
                   'required': ['from', 'to', 'target', 'label', 'stars'], 'additionalProperties': False},
    defaults={'from': 15, 'to': 90, 'target': 'VIRAL', 'label': 'HYPE', 'stars': 3}, states=('cold', 'hot'),
    actions={'heat': Action('heat', 'cold', 'hot', 54, 'mercury-target', 34)},
    bot_slot={'x': 220, 'y': 0, 'scale': .24, 'role': 'fans the bulb or reacts to the heat'}, tags=('hype', 'heat', 'rating', 'demand', 'temperature', 'stars'),
    footprint=(-280, -680, 560, 680)))


# 8 Receipt stack ----------------------------------------------------------------

class ReceiptStack(Rig):
    SLIP = 18

    def top(self, k):return -40 - k * self.SLIP

    def draw(self, p, pose, c):
        start, end, action, t = pose;tc = self.contact_t('pile') if action else 0
        n0, n1 = p['from'], p['to'];resting = n1 if (start == 'pile' and not action) else n0
        body = rect(-200, -40, 400, 40, c['floor'], 6)
        def slip(k, y, a=0):
            return g(card(220, 120, c['light'], .1) + path('M20 30H160M20 52H140M20 74H170', c['metal'], 3) + txt(p['amount'], 200, 104, 18, c['pop'], 900, 'end'), -110 + ((k * 37) % 40 - 20), y - 120 + self.SLIP, a)
        for k in range(resting):body += slip(k, self.top(k), ((k * 53) % 9) - 4)
        if action:
            for j, k in enumerate(range(n0, n1)):
                land = tc * (j + 1) / max(1, n1 - n0);u = t_in(t, land)
                body += slip(k, lerp(-1000, self.top(k), ease_in(u)), ((k * 53) % 9) - 4 + (0 if u >= 1 else 25 * (1 - u)))
        total = n1 if (action and t >= tc) or (start == 'pile' and not action) else n0
        return body + tag(f'{p["label"]}: {total}', 0, -14, 280, c, c['secondary'])

    def seams(self, p, pose):
        start, end, action, t = pose;k = p['to'] - 1;tc = self.contact_t('pile')
        y = lerp(-1000, self.top(k), ease_in(t_in(t, tc))) if action else self.top(k)
        # Slip k's underside (y) lands on slip k-1's top (top(k-1) - SLIP) or the desk (-40).
        return {'top-slip': ((0, y), (0, self.top(k - 1) - self.SLIP if k else -40))}


register(ReceiptStack(
    name='receipt-stack', description='Receipts drop onto a growing pile with a running count. Bills, subscriptions, hidden costs.',
    params_schema={'type': 'object', 'properties': {'from': {'type': 'integer', 'minimum': 0, 'maximum': 20}, 'to': {'type': 'integer', 'minimum': 1, 'maximum': 24},
                                                    'amount': {'type': 'string', 'maxLength': 8}, 'label': {'type': 'string', 'maxLength': 14}},
                   'required': ['from', 'to', 'amount', 'label'], 'additionalProperties': False},
    defaults={'from': 2, 'to': 14, 'amount': '$20', 'label': 'BILLS'}, states=('few', 'pile'),
    actions={'pile': Action('pile', 'few', 'pile', 54, 'top-slip', 42)},
    bot_slot={'x': 250, 'y': 0, 'scale': .24, 'role': 'buried or reading the top slip'}, tags=('cost', 'bills', 'subscription', 'expense', 'invoice', 'pile'),
    footprint=(-220, -560, 440, 560)))


# 9 Stamp gate ------------------------------------------------------------------

class StampGate(Rig):
    DOC_TOP = -250

    @staticmethod
    def _shade(shape, dx=6, dy=7, o=.18):
        """Soft cut-paper drop shadow: the same shape in ink, offset and faint."""
        return g(shape, dx, dy, opacity=o)

    @staticmethod
    def _rough_rect(w, h, step=9, amp=2.2, seed=0):
        """A rectangle outline with a deterministic rubber-stamp wobble."""
        pts = []
        for side in range(4):
            n = int((w if side % 2 == 0 else h) / step)
            for k in range(n):
                f = k / n;j = amp * math.sin(seed + len(pts) * 2.39) * math.cos(len(pts) * 1.13)
                if side == 0:pts.append((-w / 2 + f * w, -h / 2 + j))
                elif side == 1:pts.append((w / 2 + j, -h / 2 + f * h))
                elif side == 2:pts.append((w / 2 - f * w, h / 2 + j))
                else:pts.append((-w / 2 + j, h / 2 - f * h))
        return 'M' + 'L'.join(f'{x:.1f} {y:.1f}' for x, y in pts) + 'Z'

    def _stamp(self, c, mark, inked):
        """Chunky rubber stamp; local origin at the face centre line, face bottom at y=20."""
        d = c['dark']
        s = rect(-56, 8, 112, 12, mark if inked else c['metal'], 3, d, 3)
        s += rect(-64, -20, 128, 30, c['primary'], 7, d, 3) + g(rect(-56, -15, 70, 6, '#FFFFFF', 3), opacity=.35)
        s += path('M-40 -20V10M40 -20V10', d, 2, extra='opacity=".25"')
        s += rect(-24, -38, 48, 20, c['metal'], 5, d, 3) + path('M-24 -28H24', d, 2, extra='opacity=".3"')
        s += path('M-12 -38C-20 -60 -6 -76 -11 -96L11 -96C6 -76 20 -60 12 -38Z', c['primary'], 3, c['primary'])
        s += path('M-12 -38C-20 -60 -6 -76 -11 -96L11 -96C6 -76 20 -60 12 -38Z', d, 3)
        s += path('M-15 -52H15M-13 -62H13', d, 3) + g(path('M-4 -44C-9 -60 -1 -74 -4 -90', '#FFFFFF', 4), opacity=.35)
        s += f'<circle cx="0" cy="-118" r="27" fill="{c["secondary"]}" stroke="{d}" stroke-width="3"/>'
        s += f'<ellipse cx="-9" cy="-127" rx="9" ry="6" fill="#FFFFFF" opacity=".4"/>'
        return s

    def draw(self, p, pose, c):
        start, end, action, t = pose;tc = self.contact_t('stamp') if action else 1;t = t if action else (1 if start == 'stamped' else 0)
        u = t_in(t, tc);after = t_after(t, tc);ok = p['verdict'] == 'approved'
        stamp_y = lerp(-620, self.DOC_TOP, ease_in(u)) - (120 * ease(after * 2) if after else 0)
        d = c['dark'];mark = c['accent'] if ok else c['pop'];sh = self._shade
        # Floor shadow, desk (top, drawer, legs) and the ink pad.
        body = g(rect(-250, -8, 600, 10, d, 5), opacity=.15)
        legs = rect(-232, -60, 18, 60, c['metal'], 4, d, 3) + rect(92, -60, 18, 60, c['metal'], 4, d, 3) + rect(-214, -36, 306, 8, c['metal'], 3, d, 3)
        body += sh(rect(-232, -60, 18, 60, d) + rect(92, -60, 18, 60, d)) + legs
        body += sh(rect(-248, -78, 374, 20, d, 6)) + rect(-248, -78, 374, 20, c['primary'], 6, d, 3) + g(rect(-240, -74, 200, 4, '#FFFFFF', 2), opacity=.3)
        body += rect(-170, -58, 120, 22, c['primary'], 4, d, 3) + rect(-122, -50, 24, 6, d, 3)
        body += sh(rect(84, -96, 40, 18, d, 4)) + rect(84, -96, 40, 18, c['metal'], 4, d, 3) + rect(88, -101, 32, 7, mark, 3, d, 2)
        # In-tray board with the queue of documents waiting behind the active one.
        body += sh(rect(-224, -272, 308, 196, d, 12)) + rect(-224, -272, 308, 196, c['secondary'], 12, d, 3)
        body += g(rect(-212, -262, 284, 10, '#FFFFFF', 5), opacity=.25)
        for bx in (-210, 70):body += f'<circle cx="{bx}" cy="-258" r="4.5" fill="{c["metal"]}" stroke="{d}" stroke-width="2"/>'
        for k, (dx, dy, a) in enumerate(((-26, -24, -5), (-10, -12, 3))):
            back = card(240, 175, c['light'], .1) + path(f'M24 {16 + k * 4}H{120 + k * 30}', c['metal'], 3)
            body += g(back, -190 + dx, self.DOC_TOP + dy, a)
        doc = card(240, 175, c['light'], .1) + rect(0, 0, 240, 10, mark, 0)
        doc += txt(p['document'], 120, 52, label_size(p['document'], 210, 24), d, 900, 'middle')
        doc += path('M60 66H180', mark, 3) + path('M30 96H210M30 112H190M30 128H150', c['metal'], 3)
        doc += path('M150 150C158 140 164 156 172 146S186 150 200 144', d, 2) + rect(30, 140, 34, 18, 'none', 3, c['metal'], 2)
        body += g(doc, -190, self.DOC_TOP)
        body += sh(rect(-228, -108, 312, 32, d, 6)) + rect(-228, -108, 312, 32, c['secondary'], 6, d, 3)
        body += g(card(44, 22, c['light'], .05) + txt('IN', 22, 17, 15, d, 900, 'middle'), -94, -103)
        if after > 0:
            # Big tilted imprint with rough rubber edges, popping in then settling.
            pop = 1 + .22 * (1 - ease(min(1.0, after * 3)))
            fg = ink(mark, c)
            imp = path(self._rough_rect(164, 62, seed=1), mark, 5, mark, extra='opacity=".94"') + path(self._rough_rect(146, 46, 11, 1.4, 4), fg, 2, extra='opacity=".55"')
            imp += txt(p['stamp'], 0, 11, label_size(p['stamp'], 132, 30), fg, 900, 'middle')
            body += g(imp, -70, self.DOC_TOP + 104, -7, pop, opacity=min(1.0, after * 4))
            if after < .5:
                # Ink splatter and impact ticks around the landing point.
                f = after / .5;o = 1 - f
                for k in range(7):
                    ang = math.radians(196 + k * 25);r = 70 + 40 * ease(f) + (k % 3) * 8
                    body += f'<circle cx="{-70 + r * math.cos(ang):.1f}" cy="{self.DOC_TOP + 4 + r * .55 * math.sin(ang):.1f}" r="{4 + (k % 2) * 3}" fill="{mark}" opacity="{o:.3f}"/>'
                body += path(f'M-150 {self.DOC_TOP - 6}L-172 {self.DOC_TOP - 18}M10 {self.DOC_TOP - 6}L32 {self.DOC_TOP - 18}M-160 {self.DOC_TOP + 8}L-186 {self.DOC_TOP + 8}M20 {self.DOC_TOP + 8}L46 {self.DOC_TOP + 8}', d, 4, extra=f'opacity="{o:.3f}"')
        # The stamp: a soft shadow on the paper tightens as it comes down.
        if u > .35 and after < .5:
            k = (u - .35) / .65;body += f'<ellipse cx="-66" cy="{self.DOC_TOP + 6}" rx="{30 + 34 * k:.1f}" ry="5" fill="{d}" opacity="{.18 * k * (1 - after * 2):.3f}"/>'
        body += g(self._stamp(c, mark, True), -70, stamp_y - 20)
        # Gate: rest fork, post with base, signal light and verdict sign, counterweighted striped arm.
        gate = -80 * ease(after) if ok else 6 * settle(after)
        lit = after > 0;lamp = mark if lit else c['metal']
        body += sh(rect(332, -264, 14, 264, d)) + rect(332, -264, 14, 264, c['metal'], 4, d, 3) + path('M326 -270V-258H352V-270', d, 4)
        body += sh(rect(122, -18, 46, 18, d, 4)) + rect(122, -18, 46, 18, c['metal'], 4, d, 3)
        body += sh(rect(128, -310, 34, 296, d, 6)) + rect(128, -310, 34, 296, c['metal'], 6, d, 3) + g(rect(134, -302, 6, 280, '#FFFFFF', 3), opacity=.3)
        body += rect(122, -320, 46, 14, c['dark'], 4) + path('M128 -300H104V-318', d, 5)
        if lit:body += path('M104 -378V-392M78 -362L68 -370M130 -362L140 -370', lamp, 4, extra=f'opacity="{min(1.0, after * 3):.3f}"')
        bulb = 'M86 -318V-342A18 18 0 0 1 122 -342V-318Z'
        body += sh(path(bulb, d, 0, d)) + rect(80, -322, 48, 10, c['metal'], 4, d, 3) + path(bulb, lamp, 3, lamp) + path(bulb, d, 3)
        body += g(path('M95 -338A9 9 0 0 1 104 -348', '#FFFFFF', 4), opacity=.5)
        body += f'<circle cx="145" cy="-200" r="17" fill="{c["light"]}" stroke="{d}" stroke-width="3"/>'
        glyph = ('M137 -200L143 -193L154 -207' if ok else 'M138 -207L152 -193M152 -207L138 -193') if lit else 'M138 -200H152'
        body += path(glyph, mark if lit else c['metal'], 4)
        arm_col = c['pop'] if not ok else c['accent']
        arm = rect(-40, -18, 34, 36, c['metal'], 5, d, 3) + rect(0, -14, 220, 28, arm_col, 8)
        arm += ''.join(rect(20 + k * 50, -14, 25, 28, c['light']) for k in range(4)) + rect(0, -14, 220, 28, 'none', 8, d, 3)
        arm += f'<circle cx="0" cy="0" r="9" fill="{c["metal"]}" stroke="{d}" stroke-width="3"/>'
        body += g(g(arm, 6, 7, opacity=.15) + arm, 145, -280, gate)
        return body

    def seams(self, p, pose):
        start, end, action, t = pose;tc = self.contact_t('stamp');u = t_in(t if action else 1, tc)
        return {'stamp-document': ((-70, lerp(-620, self.DOC_TOP, ease_in(u)) + 10), (-70, self.DOC_TOP + 10))}


register(StampGate(
    name='stamp-gate', description='A stamp lands on a document; the gate arm lifts (approved) or stays shut (rejected). Approval, policy, permission.',
    params_schema={'type': 'object', 'properties': {'document': {'type': 'string', 'maxLength': 14}, 'stamp': {'type': 'string', 'maxLength': 10}, 'verdict': {'enum': ['approved', 'rejected']}},
                   'required': ['document', 'stamp', 'verdict'], 'additionalProperties': False},
    defaults={'document': 'NEW MODEL', 'stamp': 'APPROVED', 'verdict': 'approved'}, states=('waiting', 'stamped'),
    actions={'stamp': Action('stamp', 'waiting', 'stamped', 42, 'stamp-document', 20)},
    bot_slot={'x': -60, 'y': -640, 'scale': .2, 'role': 'grips the stamp handle'}, tags=('approval', 'policy', 'permission', 'review', 'regulation', 'reject'),
    footprint=(-260, -680, 620, 680)))


# 10 Conveyor -------------------------------------------------------------------

class Conveyor(Rig):
    MOUTH = 150;BELT = -150

    def item_x(self, i, n, t, tc):
        """Items queue left of the mouth; item 0 reaches the mouth at the contact frame."""
        rest = -70 - i * 110;target = self.MOUTH - 50 - i * 110
        x = lerp(rest, target, ease(t_in(t, tc)))
        return x + (200 * ease(t_after(t, tc)) if t > tc else 0)

    def draw(self, p, pose, c):
        start, end, action, t = pose;tc = self.contact_t('process') if action else 1;t = t if action else (1 if start == 'processed' else 0)
        items = p['items'];n = len(items)
        body = rect(-300, self.BELT, 470, 30, c['dark'], 15)
        for k in range(10):
            x = -290 + ((k * 50 + t * 300) % 460);body += path(f'M{x:.1f} {self.BELT + 6}v18', c['metal'], 3)
        for x in (-280, -40, 130):body += f'<circle cx="{x}" cy="{self.BELT + 15}" r="12" fill="{c["metal"]}"/>' + rect(x - 8, self.BELT + 30, 16, -self.BELT - 70, c['metal'], 4)
        cols = [c['primary'], c['accent'], c['secondary'], c['pop'], c['light']]
        for i, label in enumerate(items):
            x = self.item_x(i, n, t, tc)
            if x < self.MOUTH - 50 + 1e-6:body += g(card(100, 80, cols[i % 5], .1) + txt(label, 50, 48, label_size(label, 88, 18), ink(cols[i % 5], c), 900, 'middle'), x - 50, self.BELT - 80)
        body += rect(self.MOUTH, -420, 170, 380, c['primary'], 14) + rect(self.MOUTH - 10, self.BELT - 110, 30, 110, c['dark'], 6)
        body += tag(p['machine'], self.MOUTH + 85, -380, 160, c, c['light']) + f'<circle cx="{self.MOUTH + 85}" cy="-290" r="26" fill="{c["secondary"]}" stroke="{c["dark"]}" stroke-width="3"/>'
        body += path(f'M{self.MOUTH + 85} -290l{18 * math.cos(t * 12):.1f} {18 * math.sin(t * 12):.1f}', c['dark'], 4)
        if t > tc:
            u = ease(t_after(t, tc));body += g(card(150, 90, c['pop'], .1) + txt(p['output'], 75, 54, label_size(p['output'], 136, 22), ink(c['pop'], c), 900, 'middle'), self.MOUTH + 10 - 60 * u, -150 + 40 * u - 30 * settle(t_after(t, tc), 1))
        return body

    def seams(self, p, pose):
        start, end, action, t = pose;tc = self.contact_t('process');x = self.item_x(0, len(p['items']), min(t if action else 1, tc), tc)
        return {'item-mouth': ((x + 50, self.BELT - 40), (self.MOUTH, self.BELT - 40))}


register(Conveyor(
    name='conveyor', description='Labelled inputs ride a belt into a machine that outputs a result. Process, pipeline, automation.',
    params_schema={'type': 'object', 'properties': {'items': {'type': 'array', 'items': {'type': 'string', 'maxLength': 8}, 'minItems': 1, 'maxItems': 4},
                                                    'machine': {'type': 'string', 'maxLength': 12}, 'output': {'type': 'string', 'maxLength': 10}},
                   'required': ['items', 'machine', 'output'], 'additionalProperties': False},
    defaults={'items': ['EMAIL', 'DOCS', 'CHATS'], 'machine': 'AGENT', 'output': 'REPORT'}, states=('idle', 'processed'),
    actions={'process': Action('process', 'idle', 'processed', 54, 'item-mouth', 30)},
    bot_slot={'x': -200, 'y': 0, 'scale': .22, 'role': 'loads the belt'}, tags=('process', 'pipeline', 'automation', 'workflow', 'factory', 'agent'),
    footprint=(-300, -440, 640, 440)))
