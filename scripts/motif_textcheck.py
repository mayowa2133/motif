"""Text check: every word a finished Motif project draws, traced to the 1080 x 1920 screen.

    python scripts/motif_textcheck.py RUNS/<slug>-finished [--every 6] [--json]

Samples the timeline (every 6th frame plus the first and last frame of each shot), stacks
that moment's shot and caption compositions in headless Chromium and reads the screen box
of every visible SVG <text>. It flags:

  cut off       a word runs past the frame edge
  overlap       two different strings cover each other (over a quarter of the smaller box)
  phone UI      a string sits under Instagram's own interface: the caption, username and
                buttons at the bottom (y > 1500) or the like/comment/share rail on the right
                (x > 940). Motif reels are posted as Reels, so text there gets covered.

A reviewer reading contact sheets misses these at thumbnail size. The safe zone is the
one the /animate skill's review uses (top 240, bottom 420, right 140 at 1080 x 1920);
the approved references keep their captions just above it (about y 1485).
"""
import argparse
import json
import re
from pathlib import Path

W, H = 1080, 1920
SAFE = {'top': 240, 'bottom': 420, 'right': 140}
FPS = 30

COLLECT = """(safe) => {
  const vis = (el) => { let a = 1;
    for (let e = el; e && e.nodeType === 1; e = e.parentElement) {
      const cs = getComputedStyle(e); if (cs.display === 'none' || cs.visibility === 'hidden') return 0;
      a *= parseFloat(cs.opacity || '1'); const o = e.getAttribute('opacity'); if (o !== null) a *= parseFloat(o); }
    return a; };
  const out = [];
  document.querySelectorAll('text').forEach((t) => {
    const s = (t.textContent || '').trim(); if (!s || vis(t) < 0.05) return;
    const fill = t.getAttribute('fill'); if (fill === 'none' && !t.getAttribute('stroke')) return;
    const r = t.getBoundingClientRect(); if (r.width < 2 || r.height < 2) return;
    // Hidden behind an opaque card of its own layer (a stack window's lines under the front window): not seen.
    const layer = t.closest('[data-layer]'), pts = [[.5, .5], [.2, .5], [.8, .5], [.35, .3], [.65, .7]];
    const seen = pts.some(([fx, fy]) => { const x = r.left + fx * r.width, y = r.top + fy * r.height;
      if (x < 0 || y < 0 || x >= innerWidth || y >= innerHeight) return true;
      const top = document.elementsFromPoint(x, y).find((e) => layer.contains(e) && e !== layer && e.tagName !== 'svg' && e.tagName !== 'g');
      return !top || top === t || t.contains(top); });
    if (!seen) return;
    out.push({s, layer: t.closest('[data-layer]').dataset.layer, x0: r.left, y0: r.top, x1: r.right, y1: r.bottom});
  });
  return out; }"""


OVERLAY = """([safe, boxes]) => {
  const add = (x, y, w, h, css) => { const d = document.createElement('div'); d.style.cssText = `position:absolute;left:${x}px;top:${y}px;width:${w}px;height:${h}px;${css}`; document.body.appendChild(d); };
  add(0, 0, innerWidth, safe.top, 'background:rgba(255,40,40,.16);outline:4px dashed #FF2A2A;outline-offset:-4px'); add(0, innerHeight - safe.bottom, innerWidth, safe.bottom, 'background:rgba(255,40,40,.16);outline:4px dashed #FF2A2A;outline-offset:-4px');
  add(innerWidth - safe.right, safe.top, safe.right, innerHeight - safe.top - safe.bottom, 'background:rgba(255,40,40,.16);outline:4px dashed #FF2A2A;outline-offset:-4px');
  boxes.forEach((b) => add(b.x0, b.y0, b.x1 - b.x0, b.y1 - b.y0, 'outline:2px solid #00E5FF'));
}"""


def clips(project):
    index = (Path(project) / 'index.html').read_text()
    return [(m.group(1), float(m.group(2)), float(m.group(3))) for m in re.finditer(
        r'data-composition-id="([^"]+)" data-composition-src="compositions/[^"]+" data-start="([\d.]+)" data-duration="([\d.]+)"', index)]


def sample_times(project, every=6):
    shots = [c for c in clips(project) if c[0] != 'captions']
    end = max(s + d for _, s, d in shots);frames = set(range(0, int(end * FPS), every))
    for _, s, d in shots:frames |= {int(round(s * FPS)), int(round((s + d) * FPS)) - 1}
    return sorted(f / FPS for f in frames if f / FPS < end)


def _area(b):return max(0.0, b['x1'] - b['x0']) * max(0.0, b['y1'] - b['y0'])


def _inter(a, b):
    return max(0.0, min(a['x1'], b['x1']) - max(a['x0'], b['x0'])) * max(0.0, min(a['y1'], b['y1']) - max(a['y0'], b['y0']))


def classify(boxes, safe=SAFE):
    """Issues in one frame's text boxes: [(kind, label)]."""
    issues = []
    zones = [{'x0': 0, 'y0': H - safe['bottom'], 'x1': W, 'y1': H}, {'x0': W - safe['right'], 'y0': safe['top'], 'x1': W, 'y1': H - safe['bottom']}]
    for b in boxes:
        label = b['s'][:40]
        if len(b['s']) > 1 and (b['x0'] < -3 or b['y0'] < -3 or b['x1'] > W + 3 or b['y1'] > H + 3):issues.append(('cut off by the frame edge', label, b['layer']))
        elif sum(_inter(b, z) for z in zones) > _area(b) / 3:issues.append(('under the phone UI', label, b['layer']))
    for i, a in enumerate(boxes):
        for b in boxes[i + 1:]:
            if a['s'] == b['s'] or a['s'] in b['s'] or b['s'] in a['s']:continue
            if _inter(a, b) > .25 * min(_area(a), _area(b)):issues.append(('overlaps other text', f'"{a["s"][:24]}" x "{b["s"][:24]}"', f'{a["layer"]}/{b["layer"]}'))
    return issues


def check(project, every=6, shots_dir=None):
    from motif_frame_snapshot import FONT_STYLE, _QuietHandler, _chromium, frame_markup
    import functools, http.server, threading
    from playwright.sync_api import sync_playwright
    project = Path(project);shots = [c for c in clips(project) if c[0] != 'captions']
    index = (project / 'index.html').read_text();fonts = FONT_STYLE.search(index);fonts = fonts.group(1).split('*{')[0] if fonts else ''
    html = {}
    def comp(stem):
        if stem not in html:html[stem] = (project / 'compositions' / f'{stem}.html').read_text()
        return html[stem]
    has_captions = (project / 'compositions/captions.html').exists()
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(_QuietHandler, directory=str(project)))
    threading.Thread(target=server.serve_forever, daemon=True).start();base = f'http://127.0.0.1:{server.server_address[1]}/'
    issues, frames = {}, 0
    tmp = project / '.textcheck.html'
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=_chromium());page = browser.new_page(viewport={'width': W, 'height': H})
            for t in sample_times(project, every):
                stem, start, _ = next(c for c in shots if c[1] <= t < c[1] + c[2])
                layers = [('shot', frame_markup(comp(stem), int(round((t - start) * FPS)))[0])]
                if has_captions:layers.append(('captions', frame_markup(comp('captions'), int(round(t * FPS)))[0]))
                body = ''.join(f'<div data-layer="{n}" style="position:absolute;inset:0">{svg}</div>' for n, svg in layers)
                tmp.write_text(f'<!doctype html><html><head><meta charset="utf-8"><style>{fonts} html,body{{margin:0}} svg{{display:block;width:{W}px;height:{H}px}}</style></head><body>{body}</body></html>')
                page.goto(base + tmp.name, wait_until='load', timeout=120000)
                page.evaluate("Promise.all(['700 40px Inter','900 40px Inter','700 40px \"EB Garamond\"'].map(f => document.fonts.load(f).catch(() => null))).then(() => document.fonts.ready)")
                frames += 1
                boxes = page.evaluate(COLLECT, SAFE);fresh = False
                for kind, label, layer in classify(boxes):
                    fresh |= (kind, label) not in issues
                    v = issues.setdefault((kind, label), {'kind': kind, 'text': label, 'layer': layer, 't0': round(t, 2), 't1': round(t, 2), 'frames': 0})
                    v['t1'] = round(t, 2);v['frames'] += 1
                if shots_dir and fresh:
                    # The phone UI in red and every traced word boxed, for the frames that raise a new issue.
                    page.evaluate(OVERLAY, [SAFE, boxes]);Path(shots_dir).mkdir(parents=True, exist_ok=True)
                    page.screenshot(path=str(Path(shots_dir) / f't{t:06.2f}.png'))
            browser.close()
    finally:
        server.shutdown();tmp.unlink(missing_ok=True)
    found = list(issues.values());count = lambda k: sum(1 for i in found if i['kind'] == k)
    hard = count('cut off by the frame edge') + count('overlaps other text')
    return {'frames': frames, 'safe_zone': SAFE, 'issues': found, 'cut_off': count('cut off by the frame edge'),
            'overlap': count('overlaps other text'), 'phone_ui': count('under the phone UI'),
            'status': 'FAIL' if hard else ('WARN' if count('under the phone UI') else 'PASS')}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('project');ap.add_argument('--every', type=int, default=6);ap.add_argument('--json', action='store_true')
    ap.add_argument('--shots', help='write a screenshot of each frame that raises a new issue here')
    a = ap.parse_args(argv);r = check(a.project, a.every, a.shots)
    if a.json:print(json.dumps(r, indent=2));return
    for i in sorted(r['issues'], key=lambda i: (i['kind'], i['t0'])):
        print(f"{i['kind']:26} {i['layer']:16} {i['t0']:6.2f}-{i['t1']:<6.2f}s ({i['frames']:3} frames)  {i['text']}")
    print(f"text: {r['status']} ({r['frames']} frames; {r['cut_off']} cut off, {r['overlap']} overlapping, {r['phone_ui']} under the phone UI)")


if __name__ == '__main__':
    main()
