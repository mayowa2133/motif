"""Proof sheet for motif_face_acting (DRAFT): each mascot through a face change, frame by frame.

  python3 scripts/proof_face_acting.py OUT.png

Row per mascot: 3 squint frames before the change, the take, the settle, the mark popping and fading.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import motif_face_acting as fa
from motif_bot_kit import dressed_bot
from motif_mascots import ids

FRAMES = (0, 3, 4, 5, 6, 7, 8, 10, 13, 20)
CHANGES = (('neutral', 'shocked'), ('thinking', 'confused'), ('determined', 'proud'), ('happy', 'worried'))


def cell(mascot, before, after, f, change=6):
    track = [before] * change + [after] * 30
    face = track[f];body = dressed_bot(110, 250, .2, face, 'standing', (), 'sunrise', mascot=mascot)
    body = fa.boil_lines(fa.act_face(body, mascot, *fa.face_scale(track, f)), f, f'{mascot}{f}')
    mx, my = fa.head_spot(110, 250, .2, False)
    body += ''.join(fa.emote(k, mx, my, 70, f - s) for s, k in fa.emote_events(track))
    return body


def sheet():
    w, h = 220, 270;rows = []
    for r, m in enumerate(ids()):
        before, after = CHANGES[r % len(CHANGES)]
        for c, f in enumerate(FRAMES):
            rows.append(f'<g transform="translate({c * w} {r * h})"><rect width="{w}" height="{h}" fill="#F4E9D8" stroke="#D8CBB6"/>'
                        f'<text x="8" y="20" font-family="sans-serif" font-size="14" fill="#555">{m} f{f - 6:+d} {before if f < 6 else after}</text>{cell(m, before, after, f)}</g>')
    W, H = w * len(FRAMES), h * len(ids())
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><defs><filter id="grain"><feTurbulence baseFrequency=".9"/></filter></defs>{"".join(rows)}</svg>', W, H


if __name__ == '__main__':
    from playwright.sync_api import sync_playwright
    svg, W, H = sheet()
    with sync_playwright() as p:
        b = p.chromium.launch();pg = b.new_page(viewport={'width': W, 'height': H})
        pg.set_content(f'<body style="margin:0">{svg}</body>');pg.screenshot(path=sys.argv[1]);b.close()
