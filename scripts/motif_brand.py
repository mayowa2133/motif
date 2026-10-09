"""The real product in the picture: brand marks for the subject of a reel.

The 2026-10-09 review found the benchmark reels never showed the product they
were about (no SQLite, Python or Blender mark anywhere), so "what is this
about" was answered only by the caption. A brief now names its subject with
`brand: {"slug": "sqlite"}` and the compiler puts that mark on the hook hero,
on the rig in every claim beat and on the end card.

Marks come from the vendored simple-icons set in assets/brands/simple-icons
(icon data CC0-1.0; the trademarks belong to their owners and are used only to
identify the product the reel is about). Each mark is one SVG path in a 24 x 24
box plus the brand colour. They are drawn inline as Motif paper pieces (a
cut-paper badge or sticker around the mark), never as a third-party image.
"""
import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / 'assets/brands/simple-icons'


@lru_cache(maxsize=None)
def catalogue():
    return json.loads((FOLDER / 'brands.json').read_text())['brands']


@lru_cache(maxsize=None)
def mark(slug):
    """{'title', 'hex', 'path'} for a vendored brand; KeyError for an unknown slug."""
    if slug not in catalogue():raise KeyError(f'unknown brand {slug}; vendored: {sorted(catalogue())}')
    svg = (FOLDER / f'{slug}.svg').read_text()
    d = re.search(r'<path d="([^"]+)"', svg).group(1)
    return {**catalogue()[slug], 'slug': slug, 'path': d}


def _lum(hex_):
    r, g_, b = (int(hex_[i:i + 2], 16) / 255 for i in (1, 3, 5))
    f = lambda v: v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4
    return .2126 * f(r) + .7152 * f(g_) + .0722 * f(b)


def glyph(slug, size, fill=None):
    """The bare mark, `size` px square, top-left at (0, 0)."""
    m = mark(slug);s = size / 24
    return f'<path d="{m["path"]}" fill="{fill or m["hex"]}" transform="scale({s:.5f})"/>'


def badge(slug, size, c, title=True, angle=0.0):
    """Cut-paper badge: a paper disc with offset shadow, the mark in brand
    colour, and the product name on a tab beneath. Centred on (0, 0)."""
    from motif_ui_components import card, txt
    from motif_rigs.library import label_size
    m = mark(slug);r = size / 2;inner = size * .62
    # A brand colour too dark for a dark scene still sits on light paper.
    out = f'<circle cx="7" cy="10" r="{r:.1f}" fill="#000" opacity=".18"/>'
    out += f'<circle r="{r:.1f}" fill="#FFFDF6" stroke="#202C32" stroke-width="{max(3, size / 60):.1f}"/>'
    out += f'<circle r="{r * .9:.1f}" fill="none" stroke="{m["hex"]}" stroke-width="{max(2, size / 40):.1f}" opacity=".35" stroke-dasharray="{size / 30:.1f} {size / 45:.1f}"/>'
    out += f'<g transform="translate({-inner / 2:.1f} {-inner / 2:.1f})">{glyph(slug, inner)}</g>'
    if title:
        w = max(size * .9, len(m['title']) * size * .1 + 40);h = size * .22
        fs = label_size(m['title'], w - 20, h * .7)
        out += f'<g transform="translate({-w / 2:.1f} {r - h * .35:.1f}) rotate(-2 {w / 2:.1f} {h / 2:.1f})">{card(w, h, c["dark"], .05)}{txt(m["title"], w / 2, h / 2 + fs * .36, fs, c["light"], 900, "middle")}</g>'
    return f'<g transform="rotate({angle:.2f})">{out}</g>'


def sticker(slug, size, angle=-6.0):
    """Small mark on a white die-cut sticker, for pasting onto a rig. Centred."""
    m = mark(slug);pad = size * .16;inner = size - 2 * pad
    out = f'<rect x="{-size / 2 + 4:.1f}" y="{-size / 2 + 6:.1f}" width="{size:.1f}" height="{size:.1f}" rx="{size * .22:.1f}" fill="#000" opacity=".2"/>'
    out += f'<rect x="{-size / 2:.1f}" y="{-size / 2:.1f}" width="{size:.1f}" height="{size:.1f}" rx="{size * .22:.1f}" fill="#FFFFFF" stroke="#202C32" stroke-width="3"/>'
    out += f'<g transform="translate({-inner / 2:.1f} {-inner / 2:.1f})">{glyph(slug, inner)}</g>'
    return f'<g transform="rotate({angle:.2f})">{out}</g>'


def provenance_entries():
    """Registry entries for the vendored marks (see motif_provenance)."""
    from motif_provenance import entry_for
    approval = {'status': 'APPROVED', 'by': 'policy', 'date': '2026-10-09',
                'note': 'Nominative use of the product mark to identify the subject of the reel; icon data CC0 from simple-icons.'}
    out = []
    for slug, info in sorted(catalogue().items()):
        out.append(entry_for(FOLDER / f'{slug}.svg', f'brand/simple-icons/{slug}', 'licensed', 'npm simple-icons@13.21.0 icons/' + slug + '.svg',
                             approval, license='CC0-1.0 icon data; trademark of its owner, nominative use', source_url=info['source'], evidence='assets/brands/simple-icons/LICENSE.md'))
    return out
