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

    def draw(self, p, pose, c):
        start, end, action, t = pose;tc = self.contact_t('stack') if action else 0
        n0, n1 = p['count_from'], p['count_to'];resting = n1 if (start == 'tall' and not action) else n0
        body = rect(-220, -40, 440, 40, c['floor'], 6) + rect(-230, -46, 460, 14, c['secondary'], 6)  # buffet counter
        def plate(y, k, wob=0):
            return g(path('M-110 0Q-118 -16 -96 -20H96Q118 -16 110 0Q100 8 0 8Q-100 8 -110 0Z', c['dark'], 0, c['dark'], 'transform="translate(3 5)" opacity=".2"')
                     + path('M-110 0Q-118 -16 -96 -20H96Q118 -16 110 0Q100 8 0 8Q-100 8 -110 0Z', c['light'], 2, c['light'])
                     + path('M-80 -10H80', [c['primary'], c['accent'], c['pop']][k % 3], 4), 0, y, wob)
        lean = settle(t_after(t, tc), 3) if action else 0
        for k in range(resting):body += plate(self.plate_y(k), k, lean * k / max(1, resting))
        if action:
            # Plates n0 .. n1-1 drop in turn; the last lands exactly at the contact frame.
            for j, k in enumerate(range(n0, n1)):
                land = tc * (j + 1) / max(1, n1 - n0);u = t_in(t, land)
                y = lerp(-900, self.plate_y(k), ease_in(u))
                body += plate(y, k, lean * k / max(1, n1) if u >= 1 else 4 * (1 - u))
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

    def draw(self, p, pose, c):
        start, end, action, t = pose;tc = self.contact_t('press') if action else 0
        u = t_in(t, tc) if action else (1 if start == 'crushed' else 0);squash = ease(t_after(t, tc)) if action else (1 if start == 'crushed' else 0)
        plate_y = lerp(-600, self.OBJ_TOP, ease_in(u)) + 90 * squash
        body = rect(-250, -40, 500, 40, c['dark'], 6) + rect(-230, -640, 40, 600, c['metal'], 6) + rect(190, -640, 40, 600, c['metal'], 6) + rect(-250, -690, 500, 60, c['primary'], 10)
        body += rect(-12, -630, 24, plate_y + 630 - 40, c['metal'], 4)
        h = (-self.OBJ_TOP - 40) * (1 - .45 * squash);w = 200 * (1 + .35 * squash)
        body += g(card(w, h, c['secondary'], .1) + txt(p['object'], w / 2, h / 2 + 8, label_size(p['object'], w - 20, 26), ink(c['secondary'], c), 900, 'middle'), -w / 2, -40 - h)
        body += g(card(300, 40, c['accent'], .08), -150, plate_y - 40)
        for k in range(3 if squash > .05 else 0):
            a = -30 + k * 30;r = 130 + 40 * squash
            body += path(f'M{r * math.sin(math.radians(a)) * 1.3:.1f} {-60 - k * 15}l{20 * (1 if a >= 0 else -1)} {-6}', c['pop'], 6)
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
        return self.pan_bottom(side, (1 if side > 0 else -1) * self.TILT)

    def draw(self, p, pose, c):
        start, end, action, t = pose;tc = self.contact_t('tip') if action else 1;t = t if action else (1 if start == 'tipped' else 0)
        a = self.angle(p, t, tc);px, py = self.PIVOT
        body = rect(-150, -40, 300, 40, c['dark'], 8) + rect(-18, py, 36, -py - 40, c['metal'], 6) + path(f'M-60 {py + 10}L0 {py - 30}L60 {py + 10}Z', c['primary'], 2, c['primary'])
        if p['left_weight'] != p['right_weight']:
            sx, sy = self.stop_top(p);body += rect(sx - 40, sy, 80, -40 - sy, c['secondary'], 6)
        body += g(rect(-self.ARM - 20, -10, 2 * self.ARM + 40, 20, c['primary'], 8), px, py, a)
        swing = settle(t_after(t, tc), 4)
        for side, label, weight in ((-1, p['left_label'], p['left_weight']), (1, p['right_label'], p['right_weight'])):
            bx, by = self.pan_bottom(side, a);top = by - self.HANG
            body += path(f'M{bx} {top}L{bx - 60} {by - 20}M{bx} {top}L{bx + 60} {by - 20}', c['metal'], 3)
            body += path(f'M{bx - 85} {by - 22}Q{bx} {by + 10} {bx + 85} {by - 22}Z', c['secondary'], 2, c['secondary'])
            for k in range(weight):body += g(card(44, 34, c['accent'] if side < 0 else c['pop'], .1), bx - 66 + (k % 3) * 44, by - 56 - (k // 3) * 34, swing)
            body += tag(label, bx, by + 40, 170, c, c['light'])
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

    def draw(self, p, pose, c):
        start, end, action, t = pose;tc = self.contact_t('heat') if action else 1;t = t if action else (1 if start == 'hot' else 0)
        y = lerp(self.level(p['from']), self.level(p['to']), ease(t_in(t, tc)))
        body = rect(-70, -660, 140, 620, c['light'], 70, c['dark'], 4) + f'<circle cx="0" cy="-110" r="80" fill="{c["pop"]}" stroke="{c["dark"]}" stroke-width="4"/>'
        body += rect(-30, y, 60, -110 - y, c['pop'], 20)
        for k in range(0, 101, 20):
            ty = self.level(k);body += path(f'M40 {ty}H70', c['dark'], 3) + txt(str(k), 82, ty + 8, 22, c['dark'], 800)
        ty = self.level(p['to']);body += path(f'M-90 {ty}H90', c['accent'], 5) + tag(p['target'], -190, ty, 160, c, c['secondary'])
        stars = p['stars'];after = t_after(t, tc)
        for k in range(stars):
            u = max(0.0, min(1.0, after * stars - k));s = ease(u) * (1 + settle(u, .3))
            if s > 0:body += g(path('M0 -30L9 -9L30 0L9 9L0 30L-9 9L-30 0L-9 -9Z', c['secondary'], 2, c['secondary']), 150 + (k % 2) * 60, -560 + k * 70, a=20 * k, s=s)
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

    def draw(self, p, pose, c):
        start, end, action, t = pose;tc = self.contact_t('stamp') if action else 1;t = t if action else (1 if start == 'stamped' else 0)
        u = t_in(t, tc);after = t_after(t, tc);ok = p['verdict'] == 'approved'
        stamp_y = lerp(-620, self.DOC_TOP, ease_in(u)) - (120 * ease(after * 2) if after else 0)
        body = rect(-260, -40, 520, 40, c['dark'], 6) + rect(-220, -250, 300, 210, c['secondary'], 10)
        body += g(card(240, 150, c['light'], .1) + txt(p['document'], 120, 52, label_size(p['document'], 210, 24), c['dark'], 900, 'middle') + path('M30 90H210M30 112H170', c['metal'], 3), -190, self.DOC_TOP)
        if after > 0:
            mark = c['accent'] if ok else c['pop']
            body += g(rect(-70, -26, 140, 52, 'none', 8, mark, 6) + txt(p['stamp'], 0, 10, label_size(p['stamp'], 120, 26), mark, 900, 'middle'), -70, self.DOC_TOP + 80, -8, opacity=min(1.0, after * 4))
        body += g(rect(-60, -10, 120, 30, c['primary'], 6) + rect(-14, -110, 28, 100, c['metal'], 4) + f'<circle cx="0" cy="-120" r="30" fill="{c["primary"]}"/>', -70, stamp_y - 20)
        gate = -80 * ease(after) if ok else 6 * settle(after)
        body += rect(130, -300, 30, 260, c['metal'], 6) + g(rect(0, -14, 220, 28, c['pop'] if not ok else c['accent'], 8) + ''.join(rect(20 + k * 50, -14, 25, 28, c['light']) for k in range(4)), 145, -280, gate)
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
