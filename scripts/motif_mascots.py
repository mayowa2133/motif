"""Motif mascots: more than one character can host a film.

Bot (canonical v1) stays the default. Every other mascot is an original Motif
design drawn on the same skeleton as Bot: the 1024-unit canvas, feet at
motif_bot_kit.FEET, shoulders, hips, the pose table (build_motif_bot.POSES)
with its hand targets, walk/run/push/carry cycles, head tilt and the twelve
expressions. So every pose, cycle, crowd and costume the pipeline asks of Bot
works for any mascot without per-film code; a mascot only supplies its own
head, torso, limbs, feet and extras (ears, tail, glow).

A brief picks one with `"mascot": "<id>"`; `python scripts/motif_reel.py
catalog` lists them. A new mascot is one entry in MASCOTS plus its drawing
functions; tests/test_mascots.py proves it covers every pose and expression.

Origin: authored SVG here; style inputs docs/STYLE_BIBLE.md only. No reference
character was traced or copied. Status: DRAFT until Mayowa approves each one.
"""
import math
from dataclasses import dataclass, field
from functools import lru_cache

from build_motif_bot import HAND_D, POSES

SHOULDERS = {'left': (396, 554), 'right': (628, 554)}
HIPS = {'left': (440, 740), 'right': (584, 740)}
EXPRESSIONS = ('neutral', 'happy', 'excited', 'surprised', 'confused', 'thinking', 'worried', 'determined', 'annoyed', 'proud', 'sleepy', 'shocked')
GRAIN = 'url(#grain)'


def _p(d, fill, stroke=None, sw=0, extra=''):
    return f'<path d="{d}" fill="{fill}"' + (f' stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"' if stroke else '') + f' {extra}/>'


def paper(d, fill, edge):
    """A cut-paper shape: offset edge, fill, grain."""
    return _p(d, edge, extra='transform="translate(4 6)" opacity=".6"') + _p(d, fill) + _p(d, GRAIN, extra='opacity=".45"')


@dataclass(frozen=True)
class Mascot:
    id: str
    name: str
    description: str
    colors: dict
    head: object            # (colors) -> svg drawn in the head group (rotates with head tilt)
    behind: object = None   # (colors, pose dict) -> svg behind the body (tails, capes of their own)
    torso: object = None    # (colors) -> svg
    face_at: tuple = (512, 352)
    face_scale: float = 1.0
    limb_width: float = 46
    tags: tuple = field(default_factory=tuple)


# Faces ----------------------------------------------------------------------------------
# One expression set in Motif's paper style, placed and scaled per mascot.

def face(expression, m):
    c = m.colors;ink = c['ink'];x, y = m.face_at;s = m.face_scale;dx = 74 * s;e = expression if expression in EXPRESSIONS else 'neutral'
    out = ''

    def eye(cx, open_=1.0, big=1.0, look=0):
        rx, ry = 20 * s * big, 28 * s * big * open_
        if open_ < .25:return _p(f'M{cx - rx:.1f} {y:.1f}Q{cx:.1f} {y + 9 * s:.1f} {cx + rx:.1f} {y:.1f}', 'none', ink, 8 * s)
        return (f'<ellipse cx="{cx:.1f}" cy="{y:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{ink}"/>'
                f'<circle cx="{cx + rx * .3 + look:.1f}" cy="{y - ry * .38:.1f}" r="{7 * s * big:.1f}" fill="#FFFFFF"/>')

    def arc_eye(cx):
        return _p(f'M{cx - 22 * s:.1f} {y + 6 * s:.1f}Q{cx:.1f} {y - 22 * s:.1f} {cx + 22 * s:.1f} {y + 6 * s:.1f}', 'none', ink, 9 * s)

    def brow(cx, angle, lift=0):
        a = math.radians(angle);hx, hy = 24 * s * math.cos(a), 24 * s * math.sin(a);by = y - 50 * s - lift
        return _p(f'M{cx - hx:.1f} {by - hy:.1f}L{cx + hx:.1f} {by + hy:.1f}', 'none', ink, 9 * s)

    my = y + 62 * s
    if e in ('proud', 'happy') and e == 'proud':out += arc_eye(x - dx) + arc_eye(x + dx)
    elif e == 'sleepy':out += eye(x - dx, .1) + eye(x + dx, .1)
    elif e in ('surprised', 'shocked'):out += eye(x - dx, 1, 1.25 if e == 'shocked' else 1.12) + eye(x + dx, 1, 1.25 if e == 'shocked' else 1.12)
    elif e == 'thinking':out += eye(x - dx, .55) + eye(x + dx, 1, 1, 4 * s) + brow(x + dx, -12, 10)
    elif e == 'excited':out += eye(x - dx, 1, 1.1) + eye(x + dx, 1, 1.1)
    else:out += eye(x - dx) + eye(x + dx)
    if e == 'determined':out += brow(x - dx, 16) + brow(x + dx, -16)
    elif e == 'annoyed':out += brow(x - dx, 10) + brow(x + dx, -10)
    elif e in ('worried', 'confused'):out += brow(x - dx, -14, 6) + brow(x + dx, 14 if e == 'worried' else -6, 6)
    # Mouths.
    if e in ('happy', 'proud'):out += _p(f'M{x - 32 * s:.1f} {my - 6 * s:.1f}Q{x:.1f} {my + 26 * s:.1f} {x + 32 * s:.1f} {my - 6 * s:.1f}', 'none', ink, 9 * s)
    elif e == 'excited':
        d = f'M{x - 40 * s:.1f} {my - 10 * s:.1f}Q{x:.1f} {my - 14 * s:.1f} {x + 40 * s:.1f} {my - 10 * s:.1f}Q{x + 30 * s:.1f} {my + 40 * s:.1f} {x:.1f} {my + 40 * s:.1f}Q{x - 30 * s:.1f} {my + 40 * s:.1f} {x - 40 * s:.1f} {my - 10 * s:.1f}Z'
        out += _p(d, ink) + f'<ellipse cx="{x:.1f}" cy="{my + 26 * s:.1f}" rx="{17 * s:.1f}" ry="{9 * s:.1f}" fill="{c["tongue"]}"/>'
    elif e in ('surprised', 'shocked'):out += f'<ellipse cx="{x:.1f}" cy="{my + 8 * s:.1f}" rx="{15 * s * (1.3 if e == "shocked" else 1):.1f}" ry="{20 * s * (1.3 if e == "shocked" else 1):.1f}" fill="{ink}"/>'
    elif e in ('worried', 'confused'):out += _p(f'M{x - 28 * s:.1f} {my + 8 * s:.1f}Q{x - 10 * s:.1f} {my - 6 * s:.1f} {x + 4 * s:.1f} {my + 6 * s:.1f}T{x + 30 * s:.1f} {my + 2 * s:.1f}', 'none', ink, 8 * s)
    elif e == 'thinking':out += _p(f'M{x + 6 * s:.1f} {my + 4 * s:.1f}L{x + 36 * s:.1f} {my - 2 * s:.1f}', 'none', ink, 8 * s)
    elif e == 'sleepy':out += f'<ellipse cx="{x:.1f}" cy="{my + 4 * s:.1f}" rx="{9 * s:.1f}" ry="{7 * s:.1f}" fill="{ink}"/>'
    else:out += _p(f'M{x - 24 * s:.1f} {my + 2 * s:.1f}L{x + 24 * s:.1f} {my + 2 * s:.1f}', 'none', ink, 9 * s)
    if c.get('blush') and e not in ('annoyed', 'determined'):
        out += ''.join(f'<ellipse cx="{x + k * (dx + 40 * s):.1f}" cy="{y + 40 * s:.1f}" rx="{22 * s:.1f}" ry="{12 * s:.1f}" fill="{c["blush"]}" opacity=".7"/>' for k in (-1, 1))
    return f'<g data-part="face-state" data-state="{e}">{out}</g>'


# Limbs ----------------------------------------------------------------------------------

def arm(m, side, ex, ey, kind):
    c = m.colors;sx, sy = SHOULDERS[side];cx, cy = (sx + ex) / 2, (sy + ey) / 2 - 12
    d = f'M{sx} {sy} Q{cx:.1f} {cy:.1f} {ex:.1f} {ey:.1f}';w = m.limb_width
    line = _p(d, 'none', c['edge'], w + 4, 'transform="translate(4 5)"') + _p(d, 'none', c['limb'], w)
    mirror = 'scale(-1 1)' if side == 'left' else ''
    hd = HAND_D.get(kind, HAND_D['mitten'])
    hand = (f'<g data-part="{side}Hand" transform="translate({ex:.1f} {ey:.1f}) {mirror}">'
            + _p(hd, c['edge'], extra='transform="translate(3 4)" opacity=".62"') + _p(hd, c['hand']) + _p(hd, GRAIN, extra='opacity=".45"') + '</g>')
    return line, hand


def leg(m, side, fx, fy, rot):
    c = m.colors;hx, hy = HIPS[side]
    line = _p(f'M{hx} {hy} Q{(hx + fx) / 2:.1f} {(hy + fy - 36) / 2:.1f} {fx:.1f} {fy - 35:.1f}', 'none', c['limb'], m.limb_width - 4)
    foot = 'M-66 -14 Q-62 -40 -30 -42 L28 -42 Q60 -38 66 -10 L68 20 Q68 40 48 42 L-54 42 Q-72 40 -72 20 Z'
    shoe = f'<g data-part="{side}Foot" transform="translate({fx:.1f} {fy:.1f}) rotate({rot:.1f})">' + paper(foot, c['foot'], c['edge']) + '</g>'
    return line, shoe


def assemble(m, pose='standing', expression=None, overrides=None):
    """A full mascot at one pose, on the Bot skeleton. Returns SVG in 1024-unit space."""
    p = dict(POSES[pose])
    if overrides:p.update(overrides)
    feet = p.get('feet', ((425, 861, 0), (599, 861, 0)))
    larm, lhand = arm(m, 'left', *p['l'][:2], p['l'][2]);rarm, rhand = arm(m, 'right', *p['r'][:2], p['r'][2])
    lleg, lfoot = leg(m, 'left', *feet[0]);rleg, rfoot = leg(m, 'right', *feet[1])
    tilt = p.get('head_tilt', 0);expr = expression or p.get('face', 'neutral')
    head = f'<g data-part="head" transform="rotate({tilt} 512 350)">{m.head(m.colors)}{face(expr, m)}</g>'
    behind = m.behind(m.colors, p) if m.behind else ''
    body = behind + lleg + rleg + lfoot + rfoot + larm + rarm + (m.torso(m.colors) if m.torso else '') + head + lhand + rhand
    if p.get('body_y'):body = f'<g transform="translate(0 {p["body_y"]})">{body}</g>'
    if p.get('tilt'):body = f'<g transform="rotate({p["tilt"]} 512 620)">{body}</g>'
    return body


# Kit: a paper fox ---------------------------------------------------------------------

def _kit_head(c):
    ears = ''
    for k in (-1, 1):
        outer = f'M{512 + k * 110} 240L{512 + k * 190} 92L{512 + k * 230} 270Z';inner = f'M{512 + k * 140} 238L{512 + k * 188} 136L{512 + k * 208} 252Z'
        ears += paper(outer, c['fur'], c['edge']) + _p(inner, c['cream'])
    head = 'M512 196C640 196 734 262 742 352C748 420 690 470 610 498L512 520L414 498C334 470 276 420 282 352C290 262 384 196 512 196Z'
    muzzle = 'M392 392C430 380 470 400 512 432C554 400 594 380 632 392C640 450 590 506 512 516C434 506 384 450 392 392Z'
    cheeks = ''.join(_p(f'M{512 + k * 226} 372L{512 + k * 260} 420L{512 + k * 200} 428Z', c['cream']) for k in (-1, 1))
    return ears + paper(head, c['fur'], c['edge']) + _p(muzzle, c['cream']) + cheeks + f'<ellipse cx="512" cy="418" rx="20" ry="14" fill="{c["ink"]}"/>'


def _kit_torso(c):
    body = 'M424 520Q512 498 600 520Q632 640 610 760Q512 784 414 760Q392 640 424 520Z'
    return paper(body, c['fur'], c['edge']) + _p('M466 548Q512 536 558 548Q574 650 556 744Q512 756 468 744Q450 650 466 548Z', c['cream'])


def _kit_tail(c, p):
    sway = -10 if p.get('tilt', 0) > 0 else 6
    tail = f'M600 720C700 700 790 640 820 {540 + sway}C850 {460 + sway} 820 {400 + sway} 770 {390 + sway}C780 {470 + sway} 740 600 590 660Z'
    tip = f'M820 {540 + sway}C850 {460 + sway} 820 {400 + sway} 770 {390 + sway}C778 {440 + sway} 790 {480 + sway} 812 {520 + sway}Z'
    return paper(tail, c['fur'], c['edge']) + _p(tip, c['cream'])


# Memo: a sticky note ------------------------------------------------------------------

def _memo_head(c):
    note = 'M298 176L726 166L734 492L640 520L306 512Z'
    curl = 'M640 520L734 492Q690 500 676 470Q656 498 640 520Z'
    lines = ''.join(_p(f'M{336} {y}L{700} {y - 4}', 'none', c['rule'], 4, 'opacity=".55"') for y in (300, 450))
    return (paper(note, c['note'], c['edge']) + _p('M298 176L726 166L728 222L300 230Z', c['strip'], extra='opacity=".85"') + lines
            + _p(curl, c['curl']) + _p('M640 520L676 470', 'none', c['edge'], 3))


def _memo_torso(c):
    pad = 'M426 534H598Q612 534 612 548V754Q612 768 598 768H426Q412 768 412 754V548Q412 534 426 534Z'
    out = paper(pad, c['pad'], c['edge'])
    out += ''.join(_p(f'M432 {y}H592', 'none', c['rule'], 4, 'opacity=".6"') for y in (600, 640, 680, 720))
    out += ''.join(f'<circle cx="{x}" cy="540" r="11" fill="none" stroke="{c["ink"]}" stroke-width="6"/>' for x in (448, 484, 520, 556, 592))
    return out


# Lumo: a light bulb -------------------------------------------------------------------

def _lumo_head(c):
    glow = f'<circle cx="512" cy="322" r="236" fill="{c["glow"]}" opacity=".35"/>'
    bulb = 'M512 132C622 132 704 214 704 318C704 392 664 432 632 466C612 488 604 504 604 520H420C420 504 412 488 392 466C360 432 320 392 320 318C320 214 402 132 512 132Z'
    shine = _p('M398 250Q414 196 470 176', 'none', '#FFFFFF', 16, 'opacity=".75"')
    base = ''.join(paper(f'M{424 + k * 6} {520 + k * 18}H{600 - k * 6}V{536 + k * 18}H{424 + k * 6}Z', c['metal'], c['edge']) for k in range(3))
    return glow + paper(bulb, c['bulb'], c['edge']) + shine + base


def _lumo_torso(c):
    body = 'M430 566Q512 548 594 566Q622 660 606 762Q512 782 418 762Q402 660 430 566Z'
    bolt = 'M522 600L478 676H514L496 740L552 652H514Z'
    return paper(body, c['suit'], c['edge']) + _p(bolt, c['glow'], c['ink'], 5)


MASCOTS = {
    'kit': Mascot('kit', 'Kit', 'A cut-paper fox with a bushy white-tipped tail: curious, quick, good for discovery, research and how-to films.',
                  {'fur': '#E8743B', 'cream': '#FFF1DC', 'edge': '#B9562A', 'limb': '#5A3A2E', 'hand': '#5A3A2E', 'foot': '#5A3A2E', 'ink': '#2A1C18', 'tongue': '#F07C8A', 'blush': '#F7A98C'},
                  _kit_head, _kit_tail, _kit_torso, face_at=(512, 346), face_scale=.9, tags=('fox', 'animal', 'curious', 'research', 'learning')),
    'memo': Mascot('memo', 'Memo', 'A sticky note with a spiral-pad body and ink-line limbs: notes, productivity, writing and knowledge films.',
                   {'note': '#FFE27A', 'strip': '#F5C84C', 'curl': '#F1D06A', 'rule': '#C9A848', 'pad': '#A8D8F0', 'edge': '#C9B05A', 'limb': '#2C2C3A', 'hand': '#FFE27A', 'foot': '#2C2C3A', 'ink': '#2C2C3A', 'tongue': '#F07C8A', 'blush': '#F7A0A0'},
                   _memo_head, None, _memo_torso, face_at=(512, 360), face_scale=1.0, limb_width=30, tags=('note', 'paper', 'writing', 'productivity', 'knowledge')),
    'lumo': Mascot('lumo', 'Lumo', 'A glowing light bulb with a teal suit and a spark emblem: ideas, inventions, tips and explainers.',
                   {'bulb': '#FFF6CF', 'glow': '#FFD25A', 'metal': '#A9B4BC', 'suit': '#3BB3A6', 'edge': '#B8A86A', 'limb': '#257A70', 'hand': '#FFF6CF', 'foot': '#257A70', 'ink': '#2B3138', 'tongue': '#F07C8A', 'blush': '#FFB4A0'},
                   _lumo_head, None, _lumo_torso, face_at=(512, 316), face_scale=1.0, tags=('idea', 'light', 'tip', 'explainer', 'invention')),
}


def ids():
    return ('bot',) + tuple(MASCOTS)


@lru_cache(maxsize=2048)
def body(mascot, pose, expression, head, cycle, step):
    """Like motif_bot_kit._body for any non-Bot mascot (same pose and cycle arguments)."""
    from motif_bot_kit import _pose_params
    pose, over, _ = _pose_params(pose, head, cycle, step)
    return assemble(MASCOTS[mascot], pose, expression, over or None).replace('<path ', '<path data-layout-ignore ')


def catalog():
    from motif_bot_kit import FACES
    out = [{'id': 'bot', 'name': 'Bot', 'status': 'CANONICAL', 'description': 'Motif Bot v1, the default host: cream paper robot with a dark face panel and teal accents.'}]
    for m in MASCOTS.values():out.append({'id': m.id, 'name': m.name, 'status': 'DRAFT', 'description': m.description, 'tags': list(m.tags)})
    return {'mascots': out, 'poses': sorted(POSES), 'expressions': list(FACES)}
