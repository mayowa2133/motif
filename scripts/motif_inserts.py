"""Data-bound counters and inserts in Motif's cut-paper style.

All take explicit frame/progress inputs and palette roles (motif_rigs.palettes),
so they vary in colour with the scene. Coordinates are local; place with g().

  counter_values  monotonic integer roll from A to B that lands exactly on B
  counter         rolling digits on a paper tag
  star_badge, price_tag, gauge, progress_bar
  comment_end_card  the "comment KEYWORD" call to action
  screenshot_card   an image taped into a paper card; refuses an image without
                    a cited source and registers it for the provenance check
"""
import json
import math
from pathlib import Path

from motif_rigs.base import ease
from motif_rigs.library import ink, label_size
from motif_rigs.palettes import palette as get_palette
from motif_ui_components import card, g, path, rect, txt


def counter_values(start, end, frames, settle_at=.8):
    """Integer value per frame: eased, monotonic, exactly `end` from settle_at on."""
    if frames < 2:return [end]
    out = []
    for i in range(frames):
        u = min(1.0, i / max(1, (frames - 1) * settle_at))
        out.append(round(start + (end - start) * ease(u)))
    step = 1 if end >= start else -1
    for i in range(1, frames):  # enforce monotonic after rounding
        if (out[i] - out[i - 1]) * step < 0:out[i] = out[i - 1]
    out[-1] = end
    return out


def _lum(hex_):
    r, g_, b = (int(hex_[i:i + 2], 16) / 255 for i in (1, 3, 5))
    f = lambda v: v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4
    return .2126 * f(r) + .7152 * f(g_) + .0722 * f(b)


def contrast(a, b):
    la, lb = sorted((_lum(a), _lum(b)), reverse=True);return (la + .05) / (lb + .05)


def readable(on, c, roles=('secondary', 'pop', 'accent', 'primary', 'light'), minimum=4.5):
    """First palette role that reads on `on` (WCAG 4.5:1), so digits keep a palette colour."""
    return next((c[r] for r in roles if contrast(c[r], on) >= minimum), c['light'])


def fmt(value, prefix='', suffix='', commas=True):
    return f'{prefix}{value:,}{suffix}' if commas else f'{prefix}{value}{suffix}'


def counter(value, c, prefix='', suffix='', label=None, w=260, roll=0.0):
    """Paper counter tag. `roll` in [0, 1) slides the last digit for a mechanical tick."""
    c = get_palette(c) if isinstance(c, str) else c;text = fmt(value, prefix, suffix);h = 96
    size = label_size(text, w - 30, 54)
    body = card(w, h, c['light'], .08) + rect(12, 12, w - 24, h - 24, c['dark'], 10)
    body += txt(text, w / 2, h / 2 + size * .36 - roll * 8, size, readable(c['dark'], c), 900, 'middle')
    if label:body += g(card(w * .7, 34, c['accent'], .06) + txt(label, w * .35, 24, label_size(label, w * .6, 18), ink(c['accent'], c), 800, 'middle'), w * .15, h - 8)
    return body


def star_badge(c, rating=5, filled=5, s=1.0):
    c = get_palette(c) if isinstance(c, str) else c;body = ''
    for k in range(rating):
        fill = c['secondary'] if k < filled else c['light']
        body += g(path('M0 -22L6 -7L22 -6L10 4L14 20L0 11L-14 20L-10 4L-22 -6L-6 -7Z', c['dark'], 2, fill), k * 48, 0)
    return g(g(card(rating * 48 + 20, 64, c['primary'], .08), -32, -32) + body, s=s)


def price_tag(amount, c, strike=None, angle=-8):
    c = get_palette(c) if isinstance(c, str) else c
    body = path('M0 0L150 0L190 40L150 80L0 80Z', c['dark'], 0, c['dark'], 'transform="translate(4 6)" opacity=".18"') + path('M0 0L150 0L190 40L150 80L0 80Z', c['secondary'], 2, c['secondary'])
    body += f'<circle cx="160" cy="40" r="8" fill="{c["light"]}"/>'
    if strike:body += txt(amount, 75, 68, label_size(amount, 130, 32), ink(c['secondary'], c), 900, 'middle') + txt(strike, 75, 28, 18, ink(c['secondary'], c), 800, 'middle') + path('M50 22H100', c['pop'], 4)
    else:body += txt(amount, 75, 52, label_size(amount, 130, 36), ink(c['secondary'], c), 900, 'middle')
    return g(body, a=angle)


def gauge(value, c, label='', w=240):
    """Semicircle gauge; value in [0, 1] sets the needle (left = 0, right = 1)."""
    c = get_palette(c) if isinstance(c, str) else c;r = w / 2 - 14
    body = path(f'M{-r} 0A{r} {r} 0 0 1 {r} 0Z', c['dark'], 3, c['light'])
    for k, col in enumerate((c['accent'], c['secondary'], c['pop'])):
        a0, a1 = math.pi * (1 - k / 3), math.pi * (1 - (k + 1) / 3)
        body += path(f'M{r * .78 * math.cos(a0):.1f} {-r * .78 * math.sin(a0):.1f}A{r * .78} {r * .78} 0 0 1 {r * .78 * math.cos(a1):.1f} {-r * .78 * math.sin(a1):.1f}', col, 16)
    a = math.pi * (1 - max(0.0, min(1.0, value)))
    body += path(f'M0 0L{r * .7 * math.cos(a):.2f} {-r * .7 * math.sin(a):.2f}', c['dark'], 7) + f'<circle r="12" fill="{c["dark"]}"/>'
    if label:body += txt(label, 0, 36, label_size(label, w, 22), c['dark'], 800, 'middle')
    return body


def progress_bar(fraction, c, w=420, label=''):
    c = get_palette(c) if isinstance(c, str) else c;fraction = max(0.0, min(1.0, fraction))
    body = card(w, 54, c['light'], .08) + rect(10, 10, w - 20, 34, c['dark'], 17) + rect(14, 14, max(0, (w - 28) * fraction), 26, c['primary'], 13)
    if label:  # on its own tag above the bar, so it never straddles fill and track
        lw = min(w, 30 + len(label) * 13);body += g(card(lw, 40, c['accent'], .06) + txt(label, lw / 2, 28, label_size(label, lw - 20, 22), ink(c['accent'], c), 800, 'middle'), 0, -46)
    return body


def comment_end_card(keyword, c, prompt='Comment', w=560):
    """End card: 'Comment KEYWORD' in a speech box. The keyword is the CTA word."""
    c = get_palette(c) if isinstance(c, str) else c;h = 220
    body = path(f'M0 0H{w}V{h - 40}H{w * .32}L{w * .2} {h + 10}L{w * .22} {h - 40}H0Z', c['dark'], 0, c['dark'], 'transform="translate(6 10)" opacity=".2"')
    body += path(f'M0 0H{w}V{h - 40}H{w * .32}L{w * .2} {h + 10}L{w * .22} {h - 40}H0Z', c['light'], 3, c['light'])
    body += txt(prompt, w / 2, 62, 34, c['dark'], 800, 'middle')
    kw_w = w * .78;body += g(card(kw_w, 84, c['pop'], .08) + txt(keyword.upper(), kw_w / 2, 58, label_size(keyword, kw_w - 30, 52), ink(c['pop'], c), 900, 'middle'), (w - kw_w) / 2, 84)
    return body


def screenshot_card(image_href, c, source_url, w=420, h=300, project=None, sha256=None, licence='nominative'):
    """A real product screenshot taped into a paper card. Requires a cited source
    URL; when `project` is given, records a per-film provenance rule for it."""
    if not source_url or not str(source_url).startswith(('http://', 'https://')):
        raise ValueError('screenshot card needs the source URL the plan cites')
    c = get_palette(c) if isinstance(c, str) else c
    if project is not None:
        record = Path(project) / 'asset-provenance.json';data = json.loads(record.read_text()) if record.exists() else {'rules': []}
        rel = image_href.lstrip('/')
        rule = {'glob': rel, 'origin': 'licensed', 'generator': f'screenshot of {source_url} ({licence}); sha256 {sha256 or "unrecorded"}', 'source_url': source_url, 'licence': licence}
        if rule not in data['rules']:data['rules'].append(rule);record.write_text(json.dumps(data, indent=2) + '\n')
    body = card(w + 30, h + 30, c['light'], .08) + f'<image href="{image_href}" x="15" y="15" width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice"/>'
    for x, a in ((-10, -18), (w - 40, 14)):body += g(card(70, 24, c['secondary'], .04), x, -8, a)
    return body
