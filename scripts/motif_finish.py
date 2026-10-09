"""Finish pass: paper texture, light and cut-paper edges over built compositions.

Runs after a project's compositions exist and before encoding. It never edits
the source project: `apply` writes a finished copy. Everything is driven by a
style preset (assets/styles/motif-finish-v1.json) and is deterministic: no
clocks, no randomness outside fixed seeds, no new dependencies.

Per shot composition (an <svg> whose world group's innerHTML is swapped per
frame by motif-frame-sequence.js) the pass adds:

  surface grain   the shared worldPaper pattern is pointed at a registered
                  Motif material and stacked `surface_gain` times. Every piece
                  that already fills with worldPaper keeps its own transform,
                  so its grain moves with it.
  overlay grain   one more registered material over the whole frame (multiply),
                  for flat fills that carry no texture of their own.
  light kit       lamp pools, window shafts and volumetric beams per shot,
                  composited with screen/soft-light blends.
  vignette        radial darkening toward the frame edge.
  cut edges       each top-level piece gets a seeded turbulence displacement
                  (rough fibre edge) and a down-right drop shadow whose blur
                  grows with stacking depth; a stable per-piece micro rotation
                  and offset from its stacking index.

Text is never displaced (pieces holding text get the shadow-only filter). An
optional headline band can be masked out of the light layers; by default the
whole frame is lit, which keeps headline contrast above 7:1 on v6 (13.7:1 as
shipped, 10.2 to 10.9:1 finished). Captions live in their own composition,
which is left untouched.
"""
import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STYLE = ROOT / 'assets/styles/motif-finish-v1.json'
SCRIPT = re.compile(r'(window\.MotifEventEngine\.compileFrames\()(.*)(,"([^"]+)"\);</script>)', re.S)


def read(path):
    return json.loads(Path(path).read_text())


def unit(seed, *keys):
    """Stable value in [0, 1) from a seed and keys."""
    h = hashlib.sha256(json.dumps([seed, *keys]).encode()).digest()
    return int.from_bytes(h[:8], 'big') / 2 ** 64


# Piece-level edits --------------------------------------------------------

TAG = re.compile(r'<(/?)([a-zA-Z][\w:-]*)([^>]*?)(/?)>')


def top_level(markup):
    """(start, end, name, attrs_span) of each depth-0 element in a fragment."""
    out, depth, start, name, attrs = [], 0, None, None, None
    for m in TAG.finditer(markup):
        closing, tag, self_closing = m.group(1), m.group(2), m.group(4)
        if not closing:
            if depth == 0:start, name, attrs = m.start(), tag, (m.start(3), m.end(3))
            if self_closing:
                if depth == 0:out.append((start, m.end(), name, attrs))
            else:depth += 1
        else:
            depth -= 1
            if depth == 0:out.append((start, m.end(), name, attrs))
    return out


ROTATE = re.compile(r'rotate\((-?[\d.]+)\)')
TRANSLATE = re.compile(r'translate\((-?[\d.]+)[ ,](-?[\d.]+)\)')


def finish_frame(markup, prefix, style):
    """Edge roughening, depth shadows and micro jitter for one frame's pieces.

    Only transformed <g> pieces are touched; backgrounds, text and bare paths
    stay exact. Jitter is keyed by stacking index, so it is stable across
    frames while a piece holds its slot."""
    edges = style['edges'];micro = style['micro']
    pieces = [p for p in top_level(markup) if p[2] == 'g' and 'transform=' in markup[p[3][0]:p[3][1]]]
    levels = len(style['shadows']['blur'])
    pieces_out, cursor = [], 0
    for index, (start, end, _, (a0, a1)) in enumerate(pieces):
        attrs = markup[a0:a1]
        if 'filter=' in attrs or 'data-finish-skip' in attrs or style.get('piece_filters') is False:continue
        depth = min(levels - 1, index * levels // max(len(pieces), 1))
        jr = (unit(micro['seed'], 'r', index) - .5) * 2 * micro['rotate_deg']
        jx = (unit(micro['seed'], 'x', index) - .5) * 2 * micro['offset_px']
        jy = (unit(micro['seed'], 'y', index) - .5) * 2 * micro['offset_px']
        new = attrs
        t = TRANSLATE.search(new)
        if t:new = new[:t.start()] + f'translate({float(t.group(1)) + jx:.3f} {float(t.group(2)) + jy:.3f})' + new[t.end():]
        r = ROTATE.search(new)
        if r:new = new[:r.start()] + f'rotate({float(r.group(1)) + jr:.3f})' + new[r.end():]
        # Pieces carrying text keep exact glyph edges: shadow only, no displacement.
        kind = 'flat' if '<text' in markup[a1:end] else 'piece'
        new += f' filter="url(#{prefix}finish-{kind}-{depth})"'
        pieces_out.append(markup[cursor:a0] + new);cursor = a1
    return ''.join(pieces_out) + markup[cursor:] if pieces_out else markup


# Static layers ------------------------------------------------------------

def defs(prefix, style, width, height):
    e = style['edges'];s = style['shadows'];m = style['materials'];v = style['vignette']
    out = []
    for level, (blur, opacity) in enumerate(zip(s['blur'], s['opacity'])):
        scale = 1 + level * .5
        out.append(
            f'<filter id="{prefix}finish-piece-{level}" x="-8%" y="-8%" width="120%" height="124%" color-interpolation-filters="sRGB">'
            f'<feTurbulence type="fractalNoise" baseFrequency="{e["frequency"]}" numOctaves="2" seed="{e["seed"]}" result="n"/>'
            f'<feDisplacementMap in="SourceGraphic" in2="n" scale="{e["roughness"]}" xChannelSelector="R" yChannelSelector="G" result="rough"/>'
            f'<feDropShadow in="rough" dx="{s["dx"] * scale:.2f}" dy="{s["dy"] * scale:.2f}" stdDeviation="{blur}" flood-color="{s["color"]}" flood-opacity="{opacity}"/>'
            '</filter>')
        out.append(
            f'<filter id="{prefix}finish-flat-{level}" x="-8%" y="-8%" width="120%" height="124%" color-interpolation-filters="sRGB">'
            f'<feDropShadow dx="{s["dx"] * scale:.2f}" dy="{s["dy"] * scale:.2f}" stdDeviation="{blur}" flood-color="{s["color"]}" flood-opacity="{opacity}"/>'
            '</filter>')
    out.append(f'<pattern id="{prefix}finish-overlay" width="1024" height="1024" patternUnits="userSpaceOnUse"><image href="assets/materials/finish-overlay.webp" width="1024" height="1024"/></pattern>')
    out.append(f'<radialGradient id="{prefix}finish-vignette" cx="50%" cy="48%" r="{v["radius"] * 100:.0f}%"><stop offset="55%" stop-color="#000" stop-opacity="0"/><stop offset="100%" stop-color="{v["color"]}" stop-opacity="{v["strength"]}"/></radialGradient>')
    band = style.get('headline_band') or [0, 0]
    # Soft-edged hole over the headline band; fades back in over 4% of frame height.
    fade = .04 * height if band[1] > band[0] else 0;y0, y1 = band[0] * height, band[1] * height
    out.append(f'<linearGradient id="{prefix}finish-band" x1="0" y1="0" x2="0" y2="{height}" gradientUnits="userSpaceOnUse">'
               f'<stop offset="0" stop-color="#fff"/><stop offset="{max(0, y0 - fade) / height:.4f}" stop-color="#fff"/><stop offset="{y0 / height:.4f}" stop-color="#000"/>'
               f'<stop offset="{y1 / height:.4f}" stop-color="#000"/><stop offset="{min(height, y1 + fade) / height:.4f}" stop-color="#fff"/><stop offset="1" stop-color="#fff"/></linearGradient>')
    out.append(f'<mask id="{prefix}finish-mask" maskUnits="userSpaceOnUse" x="0" y="0" width="{width}" height="{height}"><rect width="{width}" height="{height}" fill="url(#{prefix}finish-band)"/></mask>')
    out.append(f'<filter id="{prefix}finish-soft" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="{width * .012:.1f}"/></filter>')
    return ''.join(out)


def light(prefix, n, item, width, height):
    kind = item['kind'];x, y = item['x'] * width, item['y'] * height;color = item.get('color', '#FFE7B3');k = item.get('strength', .3)
    gid = f'{prefix}finish-light-{n}'
    if kind == 'lamp':
        r = item.get('radius', .45) * width
        return (f'<radialGradient id="{gid}" cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="{color}" stop-opacity="{k}"/><stop offset=".55" stop-color="{color}" stop-opacity="{k * .35:.3f}"/><stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient>',
                f'<rect width="{width}" height="{height}" fill="url(#{gid})" style="mix-blend-mode:{item.get("blend", "soft-light")}"/>')
    if kind == 'beam':
        top = item.get('top_width', .06) * width;bottom = item.get('bottom_width', .5) * width;to_y = item.get('to_y', 1) * height
        pts = f'{x - top / 2:.1f},{y:.1f} {x + top / 2:.1f},{y:.1f} {x + bottom / 2:.1f},{to_y:.1f} {x - bottom / 2:.1f},{to_y:.1f}'
        return (f'<linearGradient id="{gid}" x1="0" y1="{y:.1f}" x2="0" y2="{to_y:.1f}" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="{color}" stop-opacity="{k}"/><stop offset="1" stop-color="{color}" stop-opacity="0"/></linearGradient>',
                f'<polygon points="{pts}" fill="url(#{gid})" filter="url(#{prefix}finish-soft)" style="mix-blend-mode:{item.get("blend", "screen")}"/>')
    if kind == 'window':
        angle = item.get('angle', 24);w = item.get('width', .5) * width;h = item.get('height', .6) * height;bars = item.get('bars', 3)
        shafts = ''.join(f'<rect x="{x + i * w / bars:.1f}" y="{y:.1f}" width="{w / bars * .72:.1f}" height="{h:.1f}"/>' for i in range(bars))
        return (f'<linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{color}" stop-opacity="{k}"/><stop offset="1" stop-color="{color}" stop-opacity="0"/></linearGradient>',
                f'<g fill="url(#{gid})" transform="skewX({-angle}) translate({y * .4:.1f} 0)" filter="url(#{prefix}finish-soft)" style="mix-blend-mode:{item.get("blend", "soft-light")}">{shafts}</g>')
    raise ValueError('unknown light kind ' + kind)


def overlay(prefix, style, lights, width, height):
    gradients, shapes = [], []
    for n, item in enumerate(lights):
        g, s = light(prefix, n, item, width, height);gradients.append(g);shapes.append(s)
    m = style['materials']
    # The mask sits on each layer, not the group: a masked group is isolated and its blend modes would not reach the scene.
    mask = f' mask="url(#{prefix}finish-mask)"'
    shapes = [x.replace(' style=', mask + ' style=', 1) for x in shapes]
    return (f'<defs>{"".join(gradients)}</defs><g id="{prefix}finish" pointer-events="none">'
            f'<rect width="{width}" height="{height}" fill="url(#{prefix}finish-overlay)" opacity="{m["overlay_opacity"]}"{mask} style="mix-blend-mode:multiply"/>'
            f'<rect width="{width}" height="{height}" fill="{style["ambient"]["color"]}" opacity="{style["ambient"]["opacity"]}"{mask} style="mix-blend-mode:multiply"/>'
            + ''.join(shapes) +
            f'<rect width="{width}" height="{height}" fill="url(#{prefix}finish-vignette)"{mask}/></g>')


# Composition rewrite ------------------------------------------------------

def finish_composition(html, style, lights):
    vb = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', html)
    width, height = float(vb.group(1)), float(vb.group(2))
    script = SCRIPT.search(html)
    if not script:raise ValueError('not a Motif frame-sequence composition')
    comp = script.group(4);prefix = comp + '-'
    spec = json.loads(script.group(2))
    layers = style.get('layers', {})
    if not layers.get('pieces', True):style = {**style, 'piece_filters': False}
    for state in spec['initial']:state['props']['innerHTML'] = finish_frame(state['props']['innerHTML'], prefix, style)
    for event in spec['events']:event['params']['props']['innerHTML'] = finish_frame(event['params']['props']['innerHTML'], prefix, style)
    body = json.dumps(spec, separators=(',', ':'), ensure_ascii=False).replace('</', '<\\/')
    html = html[:script.start(2)] + body + html[script.end(2):]
    # Initial static markup duplicates frame 0; keep it consistent with the finished frames.
    start = html.find(f'<g id="{prefix}world"')
    if start >= 0:
        end = top_level(html[start:])[0][1] + start
        html = html[:html.index('>', start) + 1] + spec['initial'][0]['props']['innerHTML'] + html[end - 4:]
    gain = style['materials']['surface_gain']
    paper = re.compile(rf'<pattern id="{re.escape(prefix)}def-worldPaper"[^>]*>(<image[^>]*/>)+</pattern>')
    # One image reference (the renderer inlines each one); strength comes from an alpha gain filter.
    tile = (f'<filter id="{prefix}finish-gain" x="0" y="0" width="1" height="1"><feComponentTransfer><feFuncA type="linear" slope="{gain}"/></feComponentTransfer></filter>'
            f'<image href="assets/materials/finish-surface.webp" width="1024" height="1024" filter="url(#{prefix}finish-gain)"/>')
    html = paper.sub(f'<pattern id="{prefix}def-worldPaper" width="1024" height="1024" patternUnits="userSpaceOnUse">{tile}</pattern>', html)
    html = html.replace('</defs>', defs(prefix, style, width, height) + '</defs>', 1)
    if not layers.get('overlay', True):return html
    end = html.rindex('</svg>')
    return html[:end] + overlay(prefix, style, lights, width, height) + html[end:]


def material_path(ref):
    from motif_materials import path_for
    set_name, name = ref.split('/', 1)
    return path_for(set_name, name)


def apply(project, out, style_path=DEFAULT_STYLE, lights_path=None):
    """Copy `project` to `out` and finish every shot composition there."""
    project, out = Path(project), Path(out)
    if out.exists():raise ValueError(f'{out} exists; finished output is never overwritten')
    style = read(style_path);lights = read(lights_path) if lights_path else {}
    shutil.copytree(project, out, ignore=shutil.ignore_patterns('renders', 'native-mobile', 'snapshots', 'quality-review', 'review'))
    for role in ('surface', 'overlay'):
        shutil.copy2(material_path(style['materials'][role]), out / f'assets/materials/finish-{role}.webp')
    record = {'style': style['id'], 'style_sha256': hashlib.sha256(Path(style_path).read_bytes()).hexdigest(), 'source': str(project), 'shots': {}}
    for comp in sorted((out / 'compositions').glob('*.html')):
        html = comp.read_text()
        if not SCRIPT.search(html) or comp.stem in style.get('skip_compositions', []):continue
        shot_lights = lights.get(comp.stem, lights.get('default', style['lights']['default']))
        comp.write_text(finish_composition(html, style, shot_lights))
        record['shots'][comp.stem] = {'lights': shot_lights, 'sha256': hashlib.sha256(comp.read_bytes()).hexdigest()}
    (out / 'finish-record.json').write_text(json.dumps(record, indent=2) + '\n')
    return record


def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    p.add_argument('project', type=Path);p.add_argument('out', type=Path)
    p.add_argument('--style', type=Path, default=DEFAULT_STYLE);p.add_argument('--lights', type=Path, help='JSON {shot-id|default: [light, ...]}')
    a = p.parse_args();record = apply(a.project, a.out, a.style, a.lights)
    print(f'finished {len(record["shots"])} compositions -> {a.out}')


if __name__ == '__main__':
    main()
