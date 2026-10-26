"""The host's face acts instead of snapping (DRAFT, brief "host_acting": true).

From JohnHeibel/ClaudeAnimationBase's ANIMATION_GUIDE (MIT; ideas only, no code or art taken):
"faces act, they never snap", painted reaction marks instead of words, and linework that boils.
Motif's hosts swapped one expression for the next between two frames. Here every face change:

  1. squints first (the face squashes over the 3 frames before the change: anticipation),
  2. lands as a take (the new face pops big, dips under, settles: a damped spring over ~10 frames),
  3. on the strong reactions, pops a painted mark beside the head (! ? sweat sparkle vein) that
     springs in, wiggles and fades.

Line boil: the host and the machine are drawn through a small displacement filter whose noise seed
changes every BOIL_STEP frames, so outlines wobble like hand-redrawn cels while the shapes hold.

All of it is closed form in the frame number, so frames still render in any order. Works for every
mascot: it only transforms the face group each mascot already draws (data-part faceState /
face-state) and draws in world space around the host.
"""
import math
import re

SQUINT = (.7, .55, .25)      # squash on the 1st, 2nd, 3rd frame before a change (nearest first)
TAKE_FRAMES = 12
EMOTE_FRAMES = 26
EMOTE_GAP = 36               # frames between two marks on one host
BOIL_STEP = 2
EMOTES = {'surprised': 'bang', 'shocked': 'bang', 'confused': 'question', 'worried': 'sweat',
          'proud': 'sparkle', 'excited': 'sparkle', 'annoyed': 'vein'}
INK = '#2A2730'


def changes(faces):
    """Frames at which the face differs from the frame before."""
    return [f for f in range(1, len(faces)) if faces[f] != faces[f - 1]]


def face_scale(faces, f):
    """(sx, sy) for the face group at frame f: a squint before each change, a take after it."""
    cs = changes(faces)
    after = [c for c in cs if c <= f];before = [c for c in cs if 0 < c - f <= len(SQUINT)]
    if after and f - after[-1] < TAKE_FRAMES:
        a = f - after[-1];k = math.exp(-a / 2.6) * math.cos(a * .85)
        return 1 + .18 * k, 1 + .3 * k
    if before and not (after and f - after[-1] < TAKE_FRAMES // 2):
        k = SQUINT[before[0] - f - 1]
        return 1 + .1 * k, 1 - .55 * k
    return 1.0, 1.0


def pivot(mascot):
    if mascot and mascot != 'bot':
        from motif_mascots import MASCOTS
        m = MASCOTS[mascot];return m.face_at[0], m.face_at[1] + 24 * m.face_scale
    return 512, 362


def act_face(svg, mascot, sx, sy):
    """Squash or stretch the host's face group in place (body untouched)."""
    if sx == 1 and sy == 1:return svg
    px, py = pivot(mascot)
    t = f' transform="translate({px} {py}) scale({sx:.4f} {sy:.4f}) translate({-px} {-py})"'
    return re.sub(r'(<g [^>]*data-part="(?:faceState|face-state)")', lambda m: m[1] + t, svg, count=1)


def emote_events(faces):
    """[(start frame, kind)] for the changes into a strong reaction, at least EMOTE_GAP apart."""
    out = []
    for c in changes(faces):
        kind = EMOTES.get(faces[c])
        if kind and (not out or c - out[-1][0] >= EMOTE_GAP):out.append((c, kind))
    return out


def _paper(d, fill, sw=7):
    return (f'<path d="{d}" fill="{INK}" opacity=".35" transform="translate(5 7)"/>'
            f'<path d="{d}" fill="{fill}" stroke="{INK}" stroke-width="{sw}" stroke-linejoin="round"/>')


def mark(kind):
    """A painted reaction mark, about 200 units tall, centred on (0, 0)."""
    if kind == 'bang':
        return _paper('M-26 -100Q0 -112 26 -100L14 30Q0 38 -14 30Z', '#FFD25A') + _paper('M-20 72A20 20 0 1 0 20 72A20 20 0 1 0 -20 72Z', '#FFD25A')
    if kind == 'question':
        hook = 'M-52 -46Q-50 -108 4 -108Q58 -106 56 -56Q54 -22 18 -6Q4 2 4 26'
        return (f'<path d="{hook}" fill="none" stroke="{INK}" stroke-width="44" stroke-linecap="round" opacity=".35" transform="translate(5 7)"/>'
                f'<path d="{hook}" fill="none" stroke="{INK}" stroke-width="44" stroke-linecap="round"/>'
                f'<path d="{hook}" fill="none" stroke="#8FD3F4" stroke-width="28" stroke-linecap="round"/>'
                + _paper('M-18 74A18 18 0 1 0 18 74A18 18 0 1 0 -18 74Z', '#8FD3F4'))
    if kind == 'sweat':
        return _paper('M0 -90Q44 -20 44 22Q44 66 0 66Q-44 66 -44 22Q-44 -20 0 -90Z', '#8FD3F4') + '<path d="M-18 14Q-16 -8 -4 -24" fill="none" stroke="#FFFFFF" stroke-width="10" stroke-linecap="round"/>'
    if kind == 'sparkle':
        star = lambda x, y, r: f'M{x} {y - r}Q{x + r * .18} {y - r * .18} {x + r} {y}Q{x + r * .18} {y + r * .18} {x} {y + r}Q{x - r * .18} {y + r * .18} {x - r} {y}Q{x - r * .18} {y - r * .18} {x} {y - r}Z'
        return _paper(star(-14, -10, 78), '#FFD25A') + _paper(star(62, 64, 36), '#FFF1B8', 5)
    if kind == 'vein':
        arms = ''.join(f'<g transform="rotate({a})"><path d="M14 -64Q16 -18 64 -14" fill="none" stroke="{INK}" stroke-width="34" stroke-linecap="round"/>'
                       f'<path d="M14 -64Q16 -18 64 -14" fill="none" stroke="#F0645A" stroke-width="20" stroke-linecap="round"/></g>' for a in (0, 90, 180, 270))
        return arms
    raise ValueError(kind)


def emote(kind, x, y, size, age):
    """The mark at world (x, y), `size` world units tall, `age` frames after its change; '' once gone."""
    if age < 0 or age >= EMOTE_FRAMES:return ''
    pop = 1 - math.exp(-age / 2.2) * math.cos(age * .9)
    fade = min(1.0, (EMOTE_FRAMES - age) / 6)
    wig = 9 * math.sin(age * .55) * math.exp(-age / 18)
    drop = 10 * age / EMOTE_FRAMES * size / 60 if kind == 'sweat' else 0
    s = size / 200 * max(0.0, pop)
    return (f'<g opacity="{fade:.3f}" transform="translate({x:.1f} {y + drop:.1f}) rotate({wig:.2f}) scale({s:.4f})">'
            f'{mark(kind)}</g>')


def head_spot(x, y, s, flip):
    """World point beside the top of the host's head (feet at x, y, scale s), on its facing side."""
    side = -1 if flip else 1
    return x + side * 250 * s, y - (861 - 120) * s


def boil_lines(markup, f, key, amount=1.0):
    """Outlines that wobble like redrawn cels: a displacement filter re-seeded every BOIL_STEP frames."""
    seed = (f // BOIL_STEP) * 7 + sum(map(ord, key)) % 97
    fid = 'lb-' + re.sub(r'[^A-Za-z0-9-]', '', key)
    return (f'<filter id="{fid}" x="-5%" y="-5%" width="110%" height="110%">'
            f'<feTurbulence type="fractalNoise" baseFrequency=".045" numOctaves="1" seed="{seed}"/>'
            f'<feDisplacementMap in="SourceGraphic" scale="{2.4 * amount:.2f}" xChannelSelector="R" yChannelSelector="G"/></filter>'
            f'<g filter="url(#{fid})">{markup}</g>')
