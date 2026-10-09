"""Fast still frames from Motif frame-sequence compositions.

Builds one standalone page per requested frame (the composition's SVG with that
frame's world markup) inside the project, so relative asset paths resolve, and
screenshots it with headless Chromium. Used for review sheets; final films still
render through the pinned HyperFrames renderer.
"""
import argparse
import json
import re
from pathlib import Path

from motif_finish import SCRIPT, top_level

FONT_STYLE = re.compile(r'<style>(@font-face.*?)</style>', re.S)


def frame_markup(html, frame):
    script = SCRIPT.search(html);spec = json.loads(script.group(2));comp = script.group(4)
    states = [spec['initial'][0]['props']['innerHTML']] + [e['params']['props']['innerHTML'] for e in spec['events']]
    start = html.index(f'<g id="{comp}-world"')
    end = top_level(html[start:])[0][1] + start  # the world group's own closing tag
    open_end = html.index('>', start) + 1
    svg_start = html.index('<svg', html.index('<template>'))
    head = html[svg_start:open_end];tail = html[end - 4:html.rindex('</svg>') + 6]
    return head + states[max(0, min(len(states) - 1, frame))] + tail, len(states)


def snapshot(project, requests, out, size=(1080, 1920)):
    """requests: [(composition stem, frame index)]. Returns written PNG paths."""
    from playwright.sync_api import sync_playwright
    project, out = Path(project), Path(out);out.mkdir(parents=True, exist_ok=True)
    index = (project / 'index.html').read_text() if (project / 'index.html').exists() else ''
    fonts = FONT_STYLE.search(index);fonts = fonts.group(1).split('*{')[0] if fonts else ''
    paths = []
    # Serve the project over HTTP: compositions reference assets by root-absolute URLs (/assets/...).
    import functools, http.server, threading
    handler = functools.partial(_QuietHandler, directory=str(project))
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f'http://127.0.0.1:{server.server_address[1]}/'
    try:
        return _capture(project, requests, out, size, fonts, base, paths)
    finally:server.shutdown()


def _capture(project, requests, out, size, fonts, base, paths):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=_chromium());page = browser.new_page(viewport={'width': size[0], 'height': size[1]})
        for stem, frame in requests:
            svg, _ = frame_markup((project / 'compositions' / f'{stem}.html').read_text(), frame)
            tmp = project / f'.snapshot-{stem}-{frame}.html'
            tmp.write_text(f'<!doctype html><html><head><meta charset="utf-8"><style>{fonts} html,body{{margin:0;background:#000}} svg{{display:block;width:{size[0]}px;height:{size[1]}px}}</style></head><body>{svg}</body></html>')
            try:
                page.goto(base + tmp.name, wait_until='load', timeout=120000);page.evaluate('document.fonts.ready')
                path = out / f'{stem}-f{frame:04d}.png';page.screenshot(path=str(path));paths.append(path)
            finally:tmp.unlink()
        browser.close()
    return paths


import http.server as _http


class _QuietHandler(_http.SimpleHTTPRequestHandler):
    def log_message(self, *args):pass


def sheet(rows, out, width=360):
    """Contact sheet: rows of (label, [png paths]) at phone-preview width."""
    from PIL import Image, ImageDraw
    height = int(width * 16 / 9);cols = max(len(r[1]) for r in rows)
    image = Image.new('RGB', (cols * (width + 8) + 8, len(rows) * (height + 30) + 8), '#FAF7F0');draw = ImageDraw.Draw(image)
    for r, (label, paths) in enumerate(rows):
        draw.text((8, 8 + r * (height + 30)), label, fill='#202C32')
        for c, path in enumerate(paths):
            with Image.open(path) as frame:image.paste(frame.convert('RGB').resize((width, height), Image.Resampling.LANCZOS), (8 + c * (width + 8), 24 + r * (height + 30)))
    Path(out).parent.mkdir(parents=True, exist_ok=True);image.save(out);return out


def _chromium():
    found = sorted(Path('/opt/pw-browsers').glob('chromium-*/chrome-linux/chrome'))
    return str(found[-1]) if found else None


def at_times(project, times):
    """Map timeline seconds to (composition, frame) using index.html clip starts."""
    index = (Path(project) / 'index.html').read_text();clips = []
    for m in re.finditer(r'data-composition-id="([^"]+)" data-composition-src="compositions/[^"]+" data-start="([\d.]+)" data-duration="([\d.]+)"', index):
        clips.append((m.group(1), float(m.group(2)), float(m.group(3))))
    out = []
    for t in times:
        comp, start, _ = next(c for c in clips if c[1] <= t < c[1] + c[2] and c[0] != 'captions')
        out.append((comp, int(round((t - start) * 30))))
    return out


def main():
    a = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    a.add_argument('project', type=Path);a.add_argument('out', type=Path);a.add_argument('--at', required=True, help='comma-separated seconds')
    args = a.parse_args()
    for p in snapshot(args.project, at_times(args.project, [float(x) for x in args.at.split(',')]), args.out):print(p)


if __name__ == '__main__':
    main()
