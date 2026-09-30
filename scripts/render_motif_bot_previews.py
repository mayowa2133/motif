#!/usr/bin/env python3
"""Render review sheets for the generated mascot SVG package.

Requires Pillow and CairoSVG; see scripts/requirements-preview.txt.
"""

from __future__ import annotations

import io
from pathlib import Path

import cairosvg
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'assets/characters/motif-bot/canonical/v1'
OUT = ROOT / 'previews'
PROOFS = OUT / 'motif-bot-a-v1/proofs'


def font(size: int, bold: bool = False):
    path = '/System/Library/Fonts/HelveticaNeue.ttc'
    try:
        return ImageFont.truetype(path, size, index=1 if bold else 0)
    except OSError:
        return ImageFont.load_default()


def render_svg(path: Path, size: int = 520) -> Image.Image:
    data = cairosvg.svg2png(url=str(path), output_width=size, output_height=size)
    return Image.open(io.BytesIO(data)).convert('RGBA')


def sheet(title: str, entries: list[tuple[str, Path]], cols: int, tile: tuple[int, int], filename: str) -> None:
    rows = (len(entries) + cols - 1) // cols
    tw, th = tile
    margin = 30
    head = 128
    canvas = Image.new('RGB', (cols * tw + (cols + 1) * margin, rows * th + (rows + 1) * margin + head), '#E4EBE0')
    d = ImageDraw.Draw(canvas)
    d.rectangle((0, 0, canvas.width, head), fill='#254D50')
    d.text((margin + 10, 27), title, font=font(48, True), fill='#F4EBD8')
    d.text((margin + 10, 87), 'Motif Bot A · minimal paper puppet · canonical v1', font=font(20), fill='#A6E5D6')
    for idx, (label, path) in enumerate(entries):
        col, row = idx % cols, idx // cols
        x = margin + col * (tw + margin)
        y = head + margin + row * (th + margin)
        d.rounded_rectangle((x, y, x + tw, y + th), radius=20, fill='#F4EBD8', outline='#C4D1C8', width=2)
        d.text((x + 22, y + 17), label.replace('-', ' ').title(), font=font(24, True), fill='#202C32')
        art = render_svg(path, min(tw - 20, th - 58))
        art.thumbnail((tw - 15, th - 53), Image.Resampling.LANCZOS)
        d.rounded_rectangle((x + 8, y + 48, x + tw - 8, y + th - 8), radius=13, fill='#CBD7D0')
        bg = Image.new('RGBA', art.size, '#CBD7D0')
        bg.alpha_composite(art)
        px = x + (tw - art.width) // 2
        py = y + 48 + (th - 52 - art.height) // 2
        canvas.paste(bg.convert('RGB'), (px, py))
    OUT.mkdir(exist_ok=True)
    canvas.save(OUT / filename, optimize=True)
    print(OUT / filename)


def main() -> None:
    views = ['front', 'front-three-quarter-left', 'front-three-quarter-right', 'left-side', 'right-side', 'back']
    sheet('TURNAROUND', [(x, BASE / 'views' / f'{x}.svg') for x in views], 3, (460, 520), 'mascot-turnaround.png')
    expressions = ['neutral', 'happy', 'excited', 'surprised', 'confused', 'thinking', 'worried', 'determined', 'annoyed', 'proud', 'sleepy', 'shocked']
    sheet('EXPRESSIONS', [(x, PROOFS / 'expressions' / f'{x}.svg') for x in expressions], 4, (330, 390), 'mascot-expressions.png')
    poses = ['standing', 'sitting', 'walking', 'running', 'pointing', 'typing', 'holding-object', 'carrying-object', 'inspecting', 'celebrating', 'falling', 'pushing', 'pulling', 'presenting', 'thinking', 'magnifying-glass']
    pose_art = lambda x: PROOFS / ('pose-demos' if (PROOFS / 'pose-demos' / f'{x}.svg').exists() else 'poses') / f'{x}.svg'
    sheet('POSE PROOFS', [(x, pose_art(x)) for x in poses], 4, (330, 390), 'mascot-poses.png')
    representative = ['standing', 'running', 'pointing', 'holding-object', 'typing', 'falling']
    sheet('REPRESENTATIVE POSES', [(x, pose_art(x)) for x in representative], 3, (460, 520), 'mascot-representative-poses.png')
    front = render_svg(BASE / 'motif-bot-front-neutral-v1.svg', 1024)
    front.save(OUT / 'motif-bot-front-neutral-v1.png')
    small = Image.new('RGB', (900, 360), '#CBD7D0')
    draw = ImageDraw.Draw(small)
    for i, size in enumerate((96, 144, 288)):
        art = render_svg(BASE / 'motif-bot-front-neutral-v1.svg', size)
        x = 30 + i * 280 + (280 - size) // 2
        y = 42 + (288 - size) // 2
        field = Image.new('RGBA', art.size, '#CBD7D0')
        field.alpha_composite(art)
        small.paste(field.convert('RGB'), (x, y))
        draw.text((30 + i * 280, 326), f'{size}px full character', font=font(16), fill='#202C32')
    small.save(OUT / 'mascot-small-size.png')


if __name__ == '__main__':
    main()
