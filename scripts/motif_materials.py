"""Motif's seeded surface materials: deterministic, original, no image inputs.

Two sets live here.

legacy-v0
    The exact generator behind the 2048 px paper/card/wood/wall overlays first
    written by videos/productions/reference-reconstruction-01-finishing/materials.py
    and later reused as v6's world-paper.webp. Ported verbatim so that the
    shared pipeline no longer depends on a reference-study folder. Pure seeded
    noise and strokes; `--check` proves the committed pixels are reproduced.

motif-v1
    Motif's own material set: matte paper, felt, card, kraft, wood and dark
    card. Every layer is built on a 2048 px torus (spectral noise and
    wrap-around strokes) so the tile repeats without a seam. Each surface is an
    RGBA overlay laid over a flat fill, the same contract as legacy-v0.

Overlays store tone in RGB and strength in alpha. Pixel hashes (not file
bytes) are the identity, so encoder versions cannot break reproducibility.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/materials'
N = 2048


def pixel_sha(image):
    """Identity of decoded RGBA pixels, independent of PNG/WebP encoder bytes."""
    rgba = np.asarray(image.convert('RGBA'))
    # Fully transparent pixels carry no picture; lossless WebP may rewrite their RGB.
    rgba = rgba.copy();rgba[rgba[..., 3] == 0] = 0
    return hashlib.sha256(np.ascontiguousarray(rgba).tobytes()).hexdigest()


# legacy-v0 ------------------------------------------------------------------

LEGACY = ('paper', 'card', 'wood', 'wall')


def legacy(name):
    index = LEGACY.index(name)
    rng = np.random.default_rng(90713 + index)
    rgba = np.zeros((N, N, 4), dtype=np.uint8)
    field = rng.normal(0, 1, (N, N))
    cloud = np.asarray(Image.fromarray(np.uint8(rng.random((5, 5)) * 255)).resize((N, N), Image.Resampling.BICUBIC), dtype=float) - 127.5
    field = field * ({'paper': 1.3, 'card': .8, 'wood': 1.2, 'wall': 1.1}[name]) + cloud * .012
    light = np.where(field > 0, 242, 37).astype(np.uint8)
    rgba[:, :, :3] = light[:, :, None]
    rgba[:, :, 3] = np.clip(np.abs(field) * 2, 0, 9).astype(np.uint8)
    im = Image.fromarray(rgba);draw = ImageDraw.Draw(im)
    if name == 'paper':
        for _ in range(2100):
            x, y = rng.integers(0, N, 2);length = int(rng.integers(2, 9))
            draw.line((int(x), int(y), int(x) + length, int(y) - 1), fill=(110, 89, 68, 9), width=1)
    elif name == 'wood':
        for i in range(100):
            y = int(rng.integers(0, N));x = int(rng.integers(0, N - 250));length = int(rng.integers(80, 400))
            draw.line((x, y, x + length, y + int(rng.integers(-3, 4))), fill=(205, 177, 140, 7), width=1)
    return im


# motif-v1 -------------------------------------------------------------------

def spectral(rng, low, high, aniso=1.0, power=1.0):
    """Periodic band-limited noise in [-1, 1]: tiles seamlessly by construction."""
    f = np.fft.fftfreq(N) * N
    fy, fx = np.meshgrid(f, f, indexing='ij')
    r = np.hypot(fx * aniso, fy)
    band = np.exp(-(r / high) ** 2) * (1 - np.exp(-(r / max(low, 1e-6)) ** 2)) / np.maximum(r, 1) ** (power - 1)
    phase = rng.random((N, N)) * 2 * np.pi
    field = np.real(np.fft.ifft2(band * np.exp(1j * phase)))
    field -= field.mean()
    return field / (np.abs(field).max() + 1e-12)


def strokes(rng, count, length, curl, width, tone, alpha, direction=None, spread=np.pi):
    """Short fibre strokes drawn on a torus so none is cut at a tile edge."""
    layer = Image.new('LA', (N, N), (0, 0));draw = ImageDraw.Draw(layer)
    for _ in range(count):
        x, y = rng.random(2) * N
        angle = (direction if direction is not None else 0) + (rng.random() - .5) * 2 * spread
        steps = max(2, int(rng.integers(length[0], length[1]) / 3))
        pts = []
        for _ in range(steps):
            pts.append((x, y));angle += rng.normal(0, curl);x += 3 * np.cos(angle);y += 3 * np.sin(angle)
        t = int(rng.integers(tone[0], tone[1] + 1));a = int(rng.integers(alpha[0], alpha[1] + 1))
        for dx in (-N, 0, N):
            for dy in (-N, 0, N):
                shifted = [(px + dx, py + dy) for px, py in pts]
                xs = [p[0] for p in shifted];ys = [p[1] for p in shifted]
                if max(xs) < 0 or min(xs) >= N or max(ys) < 0 or min(ys) >= N:continue
                draw.line(shifted, fill=(t, a), width=width)
    return np.asarray(layer, dtype=float)


def flecks(rng, count, radius, tone, alpha):
    layer = Image.new('LA', (N, N), (0, 0));draw = ImageDraw.Draw(layer)
    for _ in range(count):
        x, y = rng.random(2) * N;r = rng.uniform(*radius)
        t = int(rng.integers(tone[0], tone[1] + 1));a = int(rng.integers(alpha[0], alpha[1] + 1))
        for dx in (-N, 0, N):
            for dy in (-N, 0, N):
                draw.ellipse((x + dx - r, y + dy - r, x + dx + r, y + dy + r), fill=(t, a))
    return np.asarray(layer, dtype=float)


def compose(signed, strength, layers=()):
    """Signed tone field -> overlay. Positive lightens, negative darkens."""
    light = np.array([246, 240, 226.]);dark = np.array([42, 34, 28.])
    rgb = np.where(signed[..., None] > 0, light, dark)
    alpha = np.clip(np.abs(signed) * strength, 0, 255)
    for la in layers:
        tone, a = la[..., 0], la[..., 1]
        layer_rgb = np.stack([tone] * 3, -1) * np.array([1, .93, .82])
        out_a = a + alpha * (1 - a / 255)
        mix = np.where(out_a[..., None] > 0, (layer_rgb * a[..., None] + rgb * (alpha * (1 - a / 255))[..., None]) / np.maximum(out_a, 1e-6)[..., None], rgb)
        rgb, alpha = mix, out_a
    return Image.fromarray(np.dstack([np.clip(rgb, 0, 255), np.clip(alpha, 0, 255)]).round().astype(np.uint8), 'RGBA')


def matte_paper(rng):
    mottle = spectral(rng, 2, 9);tooth = spectral(rng, 180, 700);mid = spectral(rng, 30, 90)
    fibres = strokes(rng, 7000, (6, 26), .25, 1, (96, 128), (16, 34))
    return compose(.35 * mottle + .25 * mid + .5 * tooth, 34, [fibres])


def felt(rng):
    mottle = spectral(rng, 3, 14);fuzz = spectral(rng, 250, 900)
    hairs = strokes(rng, 30000, (6, 18), .55, 1, (200, 245), (18, 36))
    dark_hairs = strokes(rng, 16000, (5, 14), .6, 1, (40, 70), (16, 32))
    return compose(.35 * mottle + .6 * fuzz, 40, [dark_hairs, hairs])


def card(rng):
    mottle = spectral(rng, 2, 7);tooth = spectral(rng, 300, 900)
    return compose(.4 * mottle + .4 * tooth, 26, [strokes(rng, 1800, (4, 12), .2, 1, (110, 140), (8, 16))])


def kraft(rng):
    mottle = spectral(rng, 2, 10);mid = spectral(rng, 40, 140);tooth = spectral(rng, 200, 800)
    fibres = strokes(rng, 9000, (10, 40), .18, 1, (70, 100), (14, 30))
    pale = strokes(rng, 3000, (8, 24), .2, 1, (220, 240), (10, 22))
    specks = flecks(rng, 900, (.6, 1.8), (30, 60), (40, 90))
    return compose(.4 * mottle + .3 * mid + .45 * tooth, 40, [fibres, pale, specks])


def wood(rng):
    grain = spectral(rng, 3, 60, aniso=14.0)
    figure = spectral(rng, 1, 6, aniso=4.0);pores = spectral(rng, 200, 800, aniso=6.0)
    lines = strokes(rng, 1400, (120, 520), .015, 1, (60, 90), (10, 24), direction=0.0, spread=.03)
    return compose(.6 * grain + .3 * figure + .25 * pores, 44, [lines])


def dark_card(rng):
    mottle = spectral(rng, 2, 8);tooth = spectral(rng, 250, 900)
    sparkle = flecks(rng, 2600, (.5, 1.2), (200, 240), (16, 40))
    return compose(.4 * mottle + .45 * tooth, 30, [strokes(rng, 2200, (5, 16), .25, 1, (180, 220), (8, 18)), sparkle])


MOTIF_V1 = {
    'matte-paper': (matte_paper, 11001, 'Warm cream matte paper: soft mottling, paper tooth, sparse short fibres.'),
    'felt': (felt, 11002, 'Felt: dense light and dark curled hairs over fuzzy tooth.'),
    'card': (card, 11003, 'Smooth card stock: quiet mottling, fine tooth.'),
    'kraft': (kraft, 11004, 'Kraft: long dark fibres, pale fibres, dark flecks, stronger mottling.'),
    'wood': (wood, 11005, 'Wood veneer: horizontal anisotropic grain, figure and long grain lines.'),
    'dark-card': (dark_card, 11006, 'Dark card: mottling with light fibres and sparse pale flecks for dark surfaces.'),
}


def motif_v1(name):
    fn, seed, _ = MOTIF_V1[name]
    return fn(np.random.default_rng(seed))


SETS = {'legacy-v0': (LEGACY, legacy, 'png'), 'motif-v1': (tuple(MOTIF_V1), motif_v1, 'webp')}


def path_for(set_name, name):
    return OUT / set_name / f'{name}.{SETS[set_name][2]}'


def save(image, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == '.webp':image.save(path, 'WEBP', lossless=True, method=6, exact=False)
    else:image.save(path)


def manifest_path():
    return OUT / 'materials-manifest.json'


def generate(set_name, names=None):
    names, fn, _ = SETS[set_name]
    records = {}
    for name in names:
        image = fn(name);path = path_for(set_name, name)
        # Keep committed bytes when pixels already match (no churn from encoder versions).
        if not (path.is_file() and pixel_sha(Image.open(path)) == pixel_sha(image)):save(image, path)
        records[name] = {'path': str(path.relative_to(ROOT)), 'pixel_sha256': pixel_sha(image), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    return records


def check(set_name, only=None):
    """Regenerate in memory and compare decoded pixels with committed files."""
    names, fn, _ = SETS[set_name];names = [n for n in names if only is None or n in only]
    expected = json.loads(manifest_path().read_text())[set_name]
    problems = []
    for name in names:
        fresh = pixel_sha(fn(name));stored_path = path_for(set_name, name)
        if fresh != expected[name]['pixel_sha256']:problems.append(f'{set_name}/{name}: generator drifted from manifest')
        if not stored_path.is_file():problems.append(f'{set_name}/{name}: missing {stored_path.relative_to(ROOT)}')
        elif pixel_sha(Image.open(stored_path)) != fresh:problems.append(f'{set_name}/{name}: committed pixels differ from generator')
    return problems


def tile_seam_score(image):
    """Ratio of luminance jump across the wrap seam to the jump between interior neighbours.

    About 1 for a seamless tile; well above 1 when edges do not meet."""
    a = np.asarray(image.convert('RGBA'), dtype=float)
    v = a[..., 3] * (a[..., :3].mean(-1) - 128) / 255
    interior = (np.abs(np.diff(v, axis=1)).mean() + np.abs(np.diff(v, axis=0)).mean()) / 2
    seam = (np.abs(v[:, 0] - v[:, -1]).mean() + np.abs(v[0] - v[-1]).mean()) / 2
    return float(seam / max(interior, 1e-9))


def repeat_peak(image, crop=1024):
    """Highest normalised autocorrelation away from zero shift inside one tile.

    A visibly repeating pattern (e.g. a 512 px tile inside 2048) peaks near 1."""
    a = np.asarray(image.convert('RGBA'), dtype=float)[:crop, :crop]
    v = a[..., 3] * (a[..., :3].mean(-1) - 128) / 255
    # High-pass first: smooth mottling correlates broadly but is not repetition.
    spec = np.fft.fft2(v - v.mean());f = np.fft.fftfreq(crop) * crop
    fy, fx = np.meshgrid(f, f, indexing='ij');spec *= 1 - np.exp(-(np.hypot(fx, fy) / 64) ** 2)
    v = np.real(np.fft.ifft2(spec))
    spec = np.fft.fft2(v);ac = np.real(np.fft.ifft2(spec * np.conj(spec)));ac /= ac[0, 0]
    yy, xx = np.meshgrid(np.fft.fftfreq(crop) * crop, np.fft.fftfreq(crop) * crop, indexing='ij')
    ac[np.hypot(yy, xx) < 48] = 0
    return float(ac.max())


def swatch_sheet(out, set_names=('legacy-v0', 'motif-v1')):
    """Review sheet: each overlay on its intended base colour, full tile and 1:1 crop."""
    bases = {'matte-paper': '#E9DCC3', 'felt': '#3F8C84', 'card': '#F1E7D3', 'kraft': '#B98F62', 'wood': '#A4744C', 'dark-card': '#273138',
             'paper': '#E9DCC3', 'wall': '#BDAE8F'}
    rows = [(s, n) for s in set_names for n in SETS[s][0]]
    cell = 360;sheet = Image.new('RGB', (cell * 3 + 40, len(rows) * (cell + 34) + 20), '#FAF7F0');draw = ImageDraw.Draw(sheet)
    for i, (s, n) in enumerate(rows):
        overlay = Image.open(path_for(s, n)).convert('RGBA');y = 20 + i * (cell + 34)
        base = bases.get(n, '#C9B79A')
        draw.text((10, y - 16), f'{s} / {n}  (base {base})', fill='#202C32')
        for k, (img, opacity) in enumerate(((overlay.resize((cell, cell), Image.Resampling.LANCZOS), 1.0), (overlay.crop((0, 0, cell, cell)), 1.0), (overlay.crop((0, 0, cell, cell)), .5))):
            tile = Image.new('RGBA', (cell, cell), base)
            if opacity < 1:img = img.copy();img.putalpha(img.getchannel('A').point(lambda v: int(v * opacity)))
            tile.alpha_composite(img);sheet.paste(tile.convert('RGB'), (10 + k * (cell + 10), y))
    out.parent.mkdir(parents=True, exist_ok=True);sheet.save(out)
    return out


# Surface roles used by the shared pipeline, per set. legacy-v0 stays the default
# until Mayowa approves the motif-v1 swatches; a brief opts in with "material_set".
ROLES = {'wall': {'legacy-v0': 'wall', 'motif-v1': 'matte-paper'}}
DEFAULT_SET = 'legacy-v0'


def install(project, set_name=None):
    """Copy the chosen set's wall surface into a project as assets/materials/wall.png."""
    project = Path(project)
    if set_name is None:
        brief = project / 'brief.json'
        set_name = (json.loads(brief.read_text()).get('material_set') if brief.exists() else None) or DEFAULT_SET
    if set_name not in SETS:raise ValueError('unknown material_set ' + str(set_name))
    source = path_for(set_name, ROLES['wall'][set_name]);dest = project / 'assets/materials/wall.png'
    dest.parent.mkdir(parents=True, exist_ok=True)
    if source.suffix == '.png':
        import shutil
        shutil.copy2(source, dest)
    else:
        with Image.open(source) as image:image.convert('RGBA').save(dest)
    return dest


def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    p.add_argument('--set', choices=sorted(SETS), action='append')
    p.add_argument('--check', action='store_true', help='regenerate in memory and compare with committed pixels')
    p.add_argument('--swatches', type=Path, help='write a review swatch sheet to this PNG')
    a = p.parse_args();sets = a.set or sorted(SETS)
    if a.check:
        problems = [x for s in sets for x in check(s)]
        print('\n'.join(problems) or 'materials reproduce: ' + ', '.join(sets));raise SystemExit(1 if problems else 0)
    if a.swatches:print(swatch_sheet(a.swatches, sets));return
    data = json.loads(manifest_path().read_text()) if manifest_path().exists() else {}
    for s in sets:data[s] = generate(s)
    manifest_path().write_text(json.dumps(data, indent=2) + '\n');print(json.dumps(data, indent=2))


if __name__ == '__main__':
    main()
