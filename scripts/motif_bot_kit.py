"""Bot costumes, motion cycles, framing presets and crowds.

Bot keeps its canonical v1 colours and geometry. Costumes are separate
cut-paper pieces drawn in Bot's local 1024 grid (feet at 512, 861; head top at
y 166 between the antennae) and coloured from a scene palette, so the same Bot
reads as chef, builder or presenter and still varies in colour per scene.

  COSTUMES        name -> (behind, front) layers in Bot-local units
  dressed_bot     Bot with a costume, pose, face and optional walk phase
  walk_pose       seeded-free stride cycle (feet and arms) for walk, push, carry
  FRAMING         scale presets: hero, medium, wide, crowd
  crowd           seeded group of small Bots with varied scale, face, pose,
                  costume and facing, depth sorted
"""
import math
import random
from functools import lru_cache

from build_motif_bot import POSES, assemble_pose
from motif_rigs.palettes import palette as get_palette
from motif_ui_components import g

HEAD_PIVOT = (512, 350)
FEET = (512, 861)
FRAMING = {'hero': .55, 'medium': .38, 'wide': .245, 'crowd': .12}
FACES = ('happy', 'excited', 'surprised', 'proud', 'determined', 'neutral', 'thinking')


def _p(d, fill, stroke=None, sw=0, extra=''):
    s = f' stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round"' if stroke else ''
    return f'<path d="{d}" fill="{fill}"{s} {extra}/>'


def _shadowed(d, fill, c):
    """Cut-paper piece: offset shadow then the piece with a thin ink edge."""
    return _p(d, c['dark'], extra='transform="translate(6 9)" opacity=".16"') + _p(d, fill, c['dark'], 5)


# Costume pieces return (behind_body, over_head, over_body). Head pieces turn with the head.
def _hard_hat(c):
    return '', _shadowed('M372 176Q380 70 512 64Q644 70 652 176Z', c['secondary'], c) + _shadowed('M332 170H692Q700 196 680 202H344Q324 196 332 170Z', c['secondary'], c) + _p('M500 70H524V170H500Z', c['light'], extra='opacity=".55"'), ''


def _chef_hat(c):
    puff = 'M402 172Q360 120 400 82Q420 30 470 50Q500 6 548 40Q600 22 622 76Q664 112 622 172Z'
    return '', _shadowed(puff, c['light'], c) + _shadowed('M404 150H620V184H404Z', c['light'], c), ''


def _party_hat(c):
    cone = _shadowed('M430 176L512 20L594 176Z', c['pop'], c)
    stripes = _p('M462 116L560 116', 'none', c['light'], 10) + _p('M446 148L578 148', 'none', c['light'], 10)
    return '', cone + stripes + f'<circle cx="512" cy="20" r="22" fill="{c["secondary"]}" stroke="{c["dark"]}" stroke-width="5"/>', ''


def _beanie(c):
    return '', _shadowed('M382 182Q386 74 512 70Q638 74 642 182Z', c['primary'], c) + _shadowed('M372 160H652V196H372Z', c['secondary'], c) + f'<circle cx="512" cy="62" r="26" fill="{c["light"]}" stroke="{c["dark"]}" stroke-width="5"/>', ''


def _cap(c):
    return '', _shadowed('M388 180Q394 84 512 80Q630 84 636 180Z', c['accent'], c) + _shadowed('M600 168Q700 162 742 184Q700 200 600 194Z', c['accent'], c), ''


def _headset(c):
    band = _p('M318 300Q320 116 512 112Q704 116 706 300', 'none', c['dark'], 18)
    cups = _shadowed('M276 268H332V384H276Z', c['primary'], c) + _shadowed('M692 268H748V384H692Z', c['primary'], c)
    mic = _p('M720 380Q700 470 600 472', 'none', c['dark'], 9) + f'<circle cx="596" cy="472" r="16" fill="{c["pop"]}"/>'
    return '', band + cups + mic, ''


def _glasses(c):
    lens = lambda x: f'<rect x="{x}" y="290" width="104" height="82" rx="26" fill="{c["light"]}" fill-opacity=".14" stroke="{c["pop"]}" stroke-width="12"/>'
    return '', lens(366) + lens(554) + _p('M470 326Q512 306 554 326', 'none', c['pop'], 10), ''


def _bowtie(c):
    return '', '', _shadowed('M512 528L446 494L446 562Z', c['pop'], c) + _shadowed('M512 528L578 494L578 562Z', c['pop'], c) + f'<circle cx="512" cy="528" r="15" fill="{c["secondary"]}" stroke="{c["dark"]}" stroke-width="5"/>'


def _scarf(c):
    wrap = _shadowed('M420 500Q512 540 604 500L612 540Q512 580 412 540Z', c['primary'], c)
    tail = _shadowed('M560 540L600 650L566 660L536 548Z', c['primary'], c) + _p('M572 600L590 596M580 628L596 624', 'none', c['light'], 6)
    return '', '', wrap + tail


def _apron(c):
    bib = _shadowed('M450 560H574L600 760Q512 786 424 760Z', c['secondary'], c)
    pocket = _p('M472 680H552V730H472Z', 'none', c['dark'], 5) + _p('M450 560L410 520M574 560L614 520', 'none', c['dark'], 6)
    return '', '', bib + pocket


def _cape(c):
    back = _shadowed('M420 520Q300 700 330 880L512 840L694 880Q724 700 604 520Z', c['pop'], c)
    return back, '', _shadowed('M430 506Q512 540 594 506L600 530Q512 566 424 530Z', c['secondary'], c)


def _hi_vis(c):
    vest = _shadowed('M418 540Q512 520 606 540L630 740Q512 776 394 740Z', c['secondary'], c)
    strips = _p('M404 680Q512 706 620 680', 'none', c['light'], 14) + _p('M410 640Q512 664 614 640', 'none', c['light'], 14)
    return '', '', vest + strips


COSTUMES = {
    'none': lambda c: ('', '', ''),
    'hard-hat': _hard_hat, 'chef-hat': _chef_hat, 'party-hat': _party_hat, 'beanie': _beanie, 'cap': _cap,
    'headset': _headset, 'glasses': _glasses, 'bowtie': _bowtie, 'scarf': _scarf, 'apron': _apron,
    'cape': _cape, 'hi-vis': _hi_vis,
}
# Pieces that can be worn together (one head piece, one body piece).
HEAD = ('hard-hat', 'chef-hat', 'party-hat', 'beanie', 'cap', 'headset', 'glasses')
BODY = ('bowtie', 'scarf', 'apron', 'cape', 'hi-vis')


def outfit(names, c):
    names = [names] if isinstance(names, str) else list(names or [])
    behind = head = body = ''
    for name in names:
        if name not in COSTUMES:raise ValueError(f'unknown costume {name}; choose from {sorted(COSTUMES)}')
        b, h, o = COSTUMES[name](c);behind += b;head += h;body += o
    return behind, head, body


# Motion cycles ---------------------------------------------------------------

CYCLES = {'walk': 'walking', 'push': 'pushing', 'carry': 'carrying-object', 'run': 'running'}
PHASES = 8


def walk_pose(phase, cycle='walk'):
    """Pose overrides for a stride phase in [0, 1). Feet alternate, arms swing
    opposite the feet (walk, run); push and carry keep their hands on the load."""
    if cycle not in CYCLES:raise ValueError(f'unknown cycle {cycle}')
    base = dict(POSES[CYCLES[cycle]]);a = 2 * math.pi * (phase % 1.0)
    stride = 120 if cycle == 'run' else 86;lift = 34 if cycle == 'run' else 22
    sx, sy = math.sin(a), math.cos(a)
    lx, rx = 512 - 87 + sx * stride / 2, 512 + 87 - sx * stride / 2
    ly, ry = 861 - max(0.0, sy) * lift, 861 - max(0.0, -sy) * lift
    tilt = base.get('tilt', 0)
    over = {'feet': ((round(lx, 1), round(ly, 1), round(-sx * 14, 1)), (round(rx, 1), round(ry, 1), round(sx * 14, 1))), 'tilt': tilt}
    if cycle in ('walk', 'run'):
        swing = 60 if cycle == 'run' else 44;(_, l_y, lk), (_, r_y, rk) = base['l'], base['r']
        over['l'] = (round(278 - sx * swing * .4, 1), round(676 - sx * swing, 1), lk)
        over['r'] = (round(746 - sx * swing * .4, 1), round(676 + sx * swing, 1), rk)
    return CYCLES[cycle], over


def bob(phase, amount=10):
    """Body rise per stride: highest when the feet pass each other (twice a cycle)."""
    return -abs(math.sin(2 * math.pi * (phase % 1.0))) * amount


def _pose_params(pose, head, cycle, step):
    """The exact pose dict assemble_pose will use, so costumes share its transforms."""
    over = {'head_tilt': head} if head else {}
    if cycle:
        pose, extra = walk_pose(step / PHASES, cycle);over.update(extra)
    return pose, over, {**POSES[pose], **over}


@lru_cache(maxsize=1024)
def _body(pose, face, head, cycle, step):
    pose, over, _ = _pose_params(pose, head, cycle, step)
    body, _ = assemble_pose(pose, face, over or None)
    return body.replace(' id="', ' data-bot-id="').replace('<path ', '<path data-layout-ignore ')


def _like_body(svg, p):
    if p.get('body_y'):svg = f'<g transform="translate(0 {p["body_y"]})">{svg}</g>'
    if p.get('tilt'):svg = f'<g transform="rotate({p["tilt"]} 512 620)">{svg}</g>'
    return svg


def dressed_bot(x, y, s=.245, face='happy', pose='standing', costume=(), palette='sunrise', angle=0, flip=False, cycle=None, phase=0.0, head=0):
    """Bot at feet (x, y). `cycle` + `phase` select a stride frame (8 per cycle)."""
    c = get_palette(palette) if isinstance(palette, str) else palette
    step = int(round((phase % 1.0) * PHASES)) % PHASES if cycle else 0
    body = _body(pose, face, head, cycle, step);_, _, p = _pose_params(pose, head, cycle, step)
    behind, hat, front = outfit(costume, c)
    if hat:hat = f'<g transform="rotate({p.get("head_tilt", 0)} {HEAD_PIVOT[0]} {HEAD_PIVOT[1]})">{hat}</g>'
    piece = (_like_body(behind, p) if behind else '') + body + (_like_body(front + hat, p) if front or hat else '')
    if cycle:y += bob(step / PHASES) * s
    sx = -1 if flip else 1
    return f'<g transform="translate({x:.2f} {y:.2f}) rotate({angle:.2f}) scale({s * sx:.5f} {s:.5f})">{g(piece, -FEET[0], -FEET[1])}</g>'


def framed_bot(preset, x, y, **kw):
    if preset not in FRAMING:raise ValueError(f'unknown framing {preset}; choose from {sorted(FRAMING)}')
    return dressed_bot(x, y, FRAMING[preset], **kw)


# Crowds -----------------------------------------------------------------------

def crowd_layout(count, seed=0, area=(60, 660, 880, 1040), scale=(.08, .13), costumes=HEAD + BODY, poses=('standing', 'celebrating', 'pointing', 'walking', 'presenting'), faces=FACES):
    """Seeded crowd members: varied position, depth scale, face, pose, costume
    and facing. Sorted back to front. Members keep a minimum spacing."""
    rng = random.Random(seed);x0, x1, yb, yf = area;members = []
    tries = 0
    while len(members) < count and tries < count * 200:
        tries += 1;depth = rng.random();x = rng.uniform(x0, x1);y = yb + (yf - yb) * depth
        s = scale[0] + (scale[1] - scale[0]) * depth
        if any(abs(x - m['x']) < 1024 * max(s, m['s']) * .5 and abs(y - m['y']) < 70 for m in members):continue
        wear = [rng.choice(costumes)] if rng.random() < .8 else []
        members.append({'x': round(x, 1), 'y': round(y, 1), 's': round(s, 4), 'face': rng.choice(faces), 'pose': rng.choice(poses),
                        'costume': wear, 'flip': rng.random() < .5, 'angle': round(rng.uniform(-4, 4), 2)})
    if len(members) < count:raise ValueError(f'crowd: only fit {len(members)} of {count} members in {area}')
    return sorted(members, key=lambda m: (m['y'], m['x']))


def crowd(count, seed=0, palette='sunrise', palettes=None, **kw):
    """SVG for a crowd. `palettes` (a list) colours costumes per member for variety."""
    out = []
    for i, m in enumerate(crowd_layout(count, seed, **kw)):
        pal = palettes[i % len(palettes)] if palettes else palette
        out.append(dressed_bot(m['x'], m['y'], m['s'], m['face'], m['pose'], m['costume'], pal, m['angle'], m['flip']))
    return ''.join(out)
