"""Per-film looks: what makes one Motif reel look different from the next.

Mayowa (2026-10-09) watched the first five benchmark reels and found they all
looked "pretty similar". Rotating palettes per scene was not enough, because
every film shared the same headline tag, caption tiles, camera moves, hard
cuts, warm grade, hook and CTA crowd shots and the same ten machines. A look
fixes those choices for a whole film, so variety is structural:

  palettes    a palette family; scenes rotate inside it (neighbours differ)
  rooms       the rooms the planner prefers for this film
  headline    headline treatment (tag, slab, outline, ribbon, bubble)
  captions    caption treatment (tiles, bar, glow, sticker, underline)
  camera      camera grammar (push, punch, snap, float, pan)
  transition  shot transition (cut, wipe, flash, slide, iris)
  hook / cta  opening and closing shot grammar (crowd, big-bot, number, card)
  grade       finish overrides on the approved motif-finish-v1 pass (ambient
              tint, vignette); the materials and paper finish stay as approved

All looks are Motif's own: authored SVG treatments in palette roles. No
reference reel's typography or layout is copied.

choose() takes the brief's `look`, else the first look (in a seeded order) not
used by a recent film, so a batch of new reels spreads across the looks.
"""
import copy
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FINISH_V1 = ROOT / 'assets/styles/motif-finish-v1.json'

LOOKS = {
    'paper-craft': {
        'palettes': ('sunrise', 'citrus', 'berry', 'lagoon'), 'rooms': ('office', 'workshop', 'diner', 'living-room'),
        'headline': 'tag', 'captions': 'tiles', 'camera': 'push', 'transition': 'cut', 'hook': 'crowd', 'cta': 'crowd',
        'transition_colour': '#F4EBD8', 'caption_colours': {'fill': '#CC744F', 'text': '#FFF4DD', 'active': '#FFF4DD'},
        'grade': {}},
    'neon-arcade': {
        'palettes': ('neon-violet', 'neon-teal', 'neon-ember', 'plum-night'), 'rooms': ('arcade', 'server-room', 'night-sky', 'stage', 'rooftop'),
        'headline': 'outline', 'captions': 'glow', 'camera': 'punch', 'transition': 'flash', 'hook': 'number', 'cta': 'big-bot',
        'transition_colour': '#FFF6E8', 'caption_colours': {'fill': '#0E0A1F', 'text': '#FFF6E8', 'active': '#FDE047', 'glow': '#FF4FA3'},
        'grade': {'ambient': {'color': '#2A1A5E', 'opacity': .1}, 'vignette': {'strength': .55, 'radius': .78, 'color': '#05030F'}}},
    'primary-pop': {
        'palettes': ('poppy', 'royal', 'sunflower'), 'rooms': ('street', 'diner', 'stage', 'rooftop', 'arcade'),
        'headline': 'slab', 'captions': 'bar', 'camera': 'snap', 'transition': 'wipe', 'hook': 'big-bot', 'cta': 'card',
        'transition_colour': '#141414', 'caption_colours': {'fill': '#141414', 'text': '#FFF8EC', 'active': '#FFD23F'},
        'grade': {'ambient': {'color': '#000000', 'opacity': .03}, 'vignette': {'strength': .16, 'radius': .8, 'color': '#000000'}}},
    'candy-pastel': {
        'palettes': ('candy', 'lilac', 'peach', 'mint-coral'), 'rooms': ('bakery', 'living-room', 'diner', 'park', 'office'),
        'headline': 'bubble', 'captions': 'sticker', 'camera': 'float', 'transition': 'slide', 'hook': 'crowd', 'cta': 'big-bot',
        'transition_colour': '#FFFDF7', 'caption_colours': {'fill': '#FFFDF7', 'text': '#3A2A4A', 'active': '#FFB255', 'edge': '#3A2A4A'},
        'grade': {'ambient': {'color': '#D98BB5', 'opacity': .06}, 'vignette': {'strength': .2, 'radius': .8, 'color': '#5A3050'}}},
    'great-outdoors': {
        'palettes': ('sky', 'forest', 'meadow', 'cobalt'), 'rooms': ('park', 'beach', 'street', 'night-sky', 'rooftop'),
        'headline': 'ribbon', 'captions': 'underline', 'camera': 'pan', 'transition': 'iris', 'hook': 'number', 'cta': 'crowd',
        'transition_colour': '#1E2B33', 'caption_colours': {'fill': '#1E2B33', 'text': '#FFFFFF', 'active': '#F6E27A'},
        'grade': {'ambient': {'color': '#FFE7A0', 'opacity': .06}, 'vignette': {'strength': .3, 'radius': .78, 'color': '#1C3020'}}},
}

FEATURES = ('headline', 'captions', 'camera', 'transition', 'hook', 'cta')


def get(name):
    if name not in LOOKS:raise ValueError(f'unknown look {name}; choose from {sorted(LOOKS)}')
    return LOOKS[name]


def choose(brief, avoid=()):
    if brief.get('look'):get(brief['look']);return brief['look']
    key = int(hashlib.sha256(brief['slug'].encode()).hexdigest()[:8], 16)
    names = sorted(LOOKS);order = [names[(key + i) % len(names)] for i in range(len(names))]
    return next((n for n in order if n not in avoid), order[0])


def palettes(look, count, seed=0):
    """A palette per scene from the look's family; neighbours never repeat."""
    fam = list(get(look)['palettes']);start = seed % len(fam)
    return [fam[(start + i) % len(fam)] for i in range(count)]


def finish_style(look, path):
    """The approved motif-finish-v1 pass with the look's grade overrides, written to `path`."""
    style = json.loads(FINISH_V1.read_text());grade = get(look)['grade']
    for key, value in grade.items():style[key] = {**style.get(key, {}), **value}
    style['id'] = f'motif-finish-v1+{look}';style['look'] = look
    Path(path).write_text(json.dumps(style, indent=2) + '\n')
    return path


# Headline treatments ----------------------------------------------------------------

def _lines(text):
    from motif_reel import _wrap
    return [text] if len(text) <= 16 else _wrap(text)


def headline(style, text, c, f):
    """Headline in the headline band (y 80 to 310) at frame f of its shot."""
    from motif_rigs.library import ink, label_size
    from motif_ui_components import card, g, txt
    from motif_reel import headline_piece
    if style == 'tag':return headline_piece(text, c, f)
    lines = _lines(text);esc = lambda s: s.replace('&', '&amp;').replace('<', '&lt;')
    if style == 'slab':
        size = min(label_size(l, 640, 70) for l in lines);h = 44 + size * 1.04 * len(lines)
        slide = (1 - min(1.0, f / 6)) ** 3 * -760
        back = f'<path d="M-20 {-h / 2 + 12}H740V{h / 2 + 12}H-20Z" fill="{c["primary"]}"/>'
        front = f'<path d="M-20 {-h / 2}H740V{h / 2}H-20Z" fill="{c["dark"]}"/>'
        body = back + front + ''.join(txt(l, 360, -h / 2 + 22 + size * .86 + k * size * 1.04, size, c['light'], 900, 'middle') for k, l in enumerate(lines))
        return g(body, slide, 110 + h / 2, -2.2)
    if style == 'outline':
        size = min(label_size(l, 540, 74) for l in lines);pop = 1.0 if f >= 5 else .6 + .4 * (1 - (1 - f / 5) ** 3)
        y0 = 150;out = ''
        for k, l in enumerate(lines):
            y = y0 + size * .86 + k * size * 1.05 - 40
            shadow = f'<text x="366" y="{y + 7:.1f}" font-family="Inter" font-weight="900" font-size="{size:.1f}" fill="{c["primary"]}" text-anchor="middle" data-layout-allow-overlap>{esc(l)}</text>'
            face = (f'<text x="360" y="{y:.1f}" font-family="Inter" font-weight="900" font-size="{size:.1f}" fill="{c["light"]}" stroke="{c["dark"]}" stroke-width="10" '
                    f'stroke-linejoin="round" paint-order="stroke" text-anchor="middle" data-layout-allow-overlap>{esc(l)}</text>')
            out += shadow + face
        return f'<g transform="translate(360 190) scale({pop:.4f}) translate(-360 -190) rotate({1.5 * math.sin(f * .25):.3f} 360 190)">{out}</g>'
    if style == 'ribbon':
        size = min(label_size(l, 520, 62) for l in lines);h = 36 + size * 1.06 * len(lines);w = min(600, max(len(l) for l in lines) * size * .62 + 80)
        fill = c['pop'];tail = c['dark']
        ends = (f'<path d="M{-w / 2 - 30} {-h / 2 + 18}H{-w / 2 + 10}V{h / 2 + 18}H{-w / 2 - 30}L{-w / 2 - 10} {18}Z" fill="{tail}" opacity=".75"/>'
                f'<path d="M{w / 2 + 30} {-h / 2 + 18}H{w / 2 - 10}V{h / 2 + 18}H{w / 2 + 30}L{w / 2 + 10} {18}Z" fill="{tail}" opacity=".75"/>')
        band = f'<path d="M{-w / 2} {-h / 2}H{w / 2}V{h / 2}H{-w / 2}Z" fill="{fill}" stroke="{c["dark"]}" stroke-width="3"/>'
        body = ends + band + ''.join(txt(l, 0, -h / 2 + 18 + size * .86 + k * size * 1.06, size, ink(fill, c), 900, 'middle') for k, l in enumerate(lines))
        unfurl = min(1.0, f / 7);return g(body, 360, 165 + h / 2, -1.0, 1, .3 + .7 * (1 - (1 - unfurl) ** 3))
    if style == 'bubble':
        size = min(label_size(l, 560, 64) for l in lines);h = 50 + size * 1.06 * len(lines);w = min(650, max(len(l) for l in lines) * size * .62 + 100)
        bounce = 1 + .12 * math.sin(min(1.0, f / 9) * math.pi * 2) * (1 - min(1.0, f / 9))
        shape = (f'<rect x="{-w / 2 + 6}" y="{-h / 2 + 8}" width="{w}" height="{h}" rx="{h / 2}" fill="{c["dark"]}" opacity=".18"/>'
                 f'<rect x="{-w / 2}" y="{-h / 2}" width="{w}" height="{h}" rx="{h / 2}" fill="{c["light"]}" stroke="{c["primary"]}" stroke-width="8"/>'
                 f'<path d="M-20 {h / 2 - 2}L0 {h / 2 + 30}L20 {h / 2 - 2}Z" fill="{c["light"]}" stroke="{c["primary"]}" stroke-width="6" stroke-linejoin="round"/>'
                 f'<rect x="-24" y="{h / 2 - 10}" width="48" height="10" fill="{c["light"]}"/>')
        body = shape + ''.join(txt(l, 0, -h / 2 + 25 + size * .86 + k * size * 1.06, size, c['dark'], 900, 'middle') for k, l in enumerate(lines))
        return g(body, 360, 160 + h / 2, 0, bounce * (min(1.0, .5 + f / 8)))
    raise ValueError(f'unknown headline style {style}')


# Caption treatments -----------------------------------------------------------------

def captions(style, groups, f, fonts, colours):
    """Caption band markup (y >= 1090) for frame f. fonts: {'serif': TTFont, 'sans': TTFont}."""
    from motif_ui_production import captions_frame, font_width
    if style == 'tiles':return f'<g transform="translate(0 150)">{captions_frame(groups, f, fonts["serif"])}</g>'
    t = f / 30;c = next((c for c in groups if c['start'] <= t < c['end']), None)
    if c is None:return ''
    visible = [w for w in c['words'] if t + .0001 >= w['start']]
    if not visible:return ''
    words = [w['text'].upper() if style in ('bar', 'glow', 'underline') else w['text'] for w in c['words']]
    size = 50;gap = 16 if style != 'sticker' else 12
    widths = [font_width(fonts['sans'], w, size) for w in words];full = sum(widths) + gap * (len(words) - 1)
    pad = {'bar': 0, 'glow': 34, 'sticker': 26, 'underline': 0}[style]
    if full + pad * (len(words) if style == 'sticker' else 1) > 640:
        k = 640 / (full + pad * (len(words) if style == 'sticker' else 1));size *= k;widths = [w * k for w in widths];full = sum(widths) + gap * (len(words) - 1)
    n = len(visible);active = n - 1;y = 1200;out = ''
    esc = lambda s: s.replace('&', '&amp;').replace('<', '&lt;')
    word = lambda s, x, col, extra='': f'<text x="{x:.1f}" y="{y + size * .36:.1f}" font-family="Inter" font-weight="900" font-size="{size:.1f}" fill="{col}" text-anchor="middle" {extra} data-layout-allow-overlap>{esc(s)}</text>'
    if style == 'sticker':full += pad * len(words)
    x = (720 - full) / 2
    if style == 'bar':
        out += f'<rect x="0" y="{y - 52}" width="720" height="104" fill="{colours["fill"]}" opacity=".92"/>'
    if style == 'glow':
        out += f'<rect x="{x - pad / 2:.1f}" y="{y - 46}" width="{full + pad:.1f}" height="92" rx="46" fill="{colours["fill"]}" opacity=".88"/>'
    for i in range(n):
        w = widths[i] + (pad if style == 'sticker' else 0);cx = x + w / 2;age = (t - visible[i]['start']) * 30;pop = min(1.0, .7 + .3 * age / 4)
        col = colours['active'] if i == active else colours['text']
        if style == 'sticker':
            fill = colours['active'] if i == active else colours['fill'];rot = (-3, 2, -1.5, 3)[i % 4]
            out += (f'<g transform="translate({cx:.1f} {y}) rotate({rot}) scale({pop:.3f}) translate({-cx:.1f} {-y})">'
                    f'<rect x="{cx - w / 2:.1f}" y="{y - 40}" width="{w:.1f}" height="80" rx="22" fill="{fill}" stroke="{colours["edge"]}" stroke-width="4"/>{word(words[i], cx, colours["text"])}</g>')
        elif style == 'underline':
            stroke = f'stroke="{colours["fill"]}" stroke-width="10" stroke-linejoin="round" paint-order="stroke"'
            if i == active:out += f'<rect x="{x:.1f}" y="{y + size * .48:.1f}" width="{widths[i] * min(1.0, age / 5):.1f}" height="10" rx="5" fill="{colours["active"]}"/>'
            out += word(words[i], cx, colours['text'], stroke)
        elif style == 'glow':
            if i == active:out += word(words[i], cx, 'none', f'stroke="{colours["glow"]}" stroke-width="14" opacity=".45"')
            out += f'<g transform="translate({cx:.1f} {y}) scale({pop:.3f}) translate({-cx:.1f} {-y})">{word(words[i], cx, col)}</g>'
        else:
            out += word(words[i], cx, col)
        x += w + gap
    return out


# Camera, transitions -----------------------------------------------------------------

def camera(style, role, u, f, n):
    """(zoom, dx, dy) for frame f (u = f / (n - 1)) of a shot with this role."""
    from motif_rigs.base import ease
    if style == 'push':
        return ({'setup': 1.0 + .04 * u, 'payoff': 1.12 + .05 * ease(u)}.get(role, 1.0 + .06 * u), 0, 0)
    if style == 'punch':
        if role == 'payoff':return (1.14 + .2 * math.exp(-f / 4), 0, 0)
        if role == 'hook':return (1.16 - .14 * ease(u), 0, 0)
        return (1.0 + .03 * u + .1 * math.exp(-f / 3), 0, 0)
    if style == 'snap':
        return (1.0 + .2 * (1 - ease(min(1.0, f / 6))) + (.06 if role == 'payoff' else 0), 0, 0)
    if style == 'float':
        return (1.06 + .02 * math.sin(f * .07), 14 * math.sin(f * .05), 9 * math.cos(f * .06))
    if style == 'pan':
        direction = -1 if role == 'payoff' else 1
        return (1.08 + (.03 * ease(u) if role == 'payoff' else 0), direction * (20 - 40 * ease(u)), 0)
    raise ValueError(f'unknown camera {style}')


def transition_in(style, f, colour):
    """Overlay drawn on the first frames of a shot (a depth-0 piece)."""
    from motif_rigs.base import ease
    if style == 'wipe' and f < 5:
        # A slanted band sweeps off to the right; the frame is never fully covered (v4 review:
        # a full-cover wipe gave ~0.4 s of near-black at every cut).
        x = -200 + 1100 * ease(f / 5);return f'<path d="M{x - 60:.1f} 0H{x + 240:.1f}L{x + 120:.1f} 1280H{x - 180:.1f}Z" fill="{colour}"/>'
    if style == 'flash' and f < 5:
        return f'<rect width="720" height="1280" fill="{colour}" opacity="{.85 * (1 - f / 5):.3f}"/>'
    if style == 'iris' and f < 8:
        r = 20 + 880 * ease(f / 8);return f'<path d="M0 0H720V1280H0Z M360 {640 - r:.1f}A{r:.1f} {r:.1f} 0 1 0 360 {640 + r:.1f}A{r:.1f} {r:.1f} 0 1 0 360 {640 - r:.1f}Z" fill="{colour}" fill-rule="evenodd"/>'
    return ''


def transition_out(style, f, n, colour):
    """Overlay drawn on the last frames of a shot."""
    from motif_rigs.base import ease_in
    left = n - 1 - f
    if style == 'wipe' and left < 3:
        x = -300 + 500 * ease_in((3 - left) / 3);return f'<path d="M{x - 60:.1f} 0H{x + 240:.1f}L{x + 120:.1f} 1280H{x - 180:.1f}Z" fill="{colour}"/>'
    if style == 'iris' and left < 6:
        r = 900 - 880 * ease_in((6 - left) / 6);return f'<path d="M0 0H720V1280H0Z M360 {640 - r:.1f}A{r:.1f} {r:.1f} 0 1 0 360 {640 + r:.1f}A{r:.1f} {r:.1f} 0 1 0 360 {640 - r:.1f}Z" fill="{colour}" fill-rule="evenodd"/>'
    return ''


def slide_offset(style, f):
    """Slide transition: the new shot rises into place over its first frames."""
    from motif_rigs.base import ease
    return 320 * (1 - ease(f / 8)) if style == 'slide' and f < 8 else 0.0


def fingerprint_of(look):
    l = get(look);return {k: l[k] for k in FEATURES} | {'palettes': list(l['palettes'])}


def describe():
    return {name: copy.deepcopy(l) for name, l in LOOKS.items()}
