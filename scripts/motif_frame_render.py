"""Fast review render for Motif frame-sequence projects.

HyperFrames renders finished compositions very slowly in the cloud container
(a full v7 render ran for over an hour without finishing). Every Motif
composition is a frame sequence (one SET of the world markup per frame), so a
review render can draw each frame directly: one Chromium page per shot, swap
the world markup per frame, screenshot, and pipe the frames to ffmpeg. The
captions composition is layered on top. Audio is narration plus the planned
SFX cues, mixed to -16 LUFS with a -1.5 dBTP ceiling.

This is a review renderer: the pinned HyperFrames renderer stays the delivery
path wherever it runs at a usable speed.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from motif_finish import SCRIPT, top_level
from motif_frame_snapshot import FONT_STYLE, _QuietHandler, _chromium

FPS = 30


def clips(project):
    index = (Path(project) / 'index.html').read_text();out = []
    for m in re.finditer(r'data-composition-id="([^"]+)" data-composition-src="(compositions/[^"]+)" data-start="([\d.]+)" data-duration="([\d.]+)"', index):
        out.append({'id': m.group(1), 'src': m.group(2), 'start': float(m.group(3)), 'duration': float(m.group(4))})
    return out


def states(html):
    spec = json.loads(SCRIPT.search(html).group(2));comp = SCRIPT.search(html).group(4)
    frames = [spec['initial'][0]['props']['innerHTML']] + [e['params']['props']['innerHTML'] for e in spec['events']]
    start = html.index(f'<g id="{comp}-world"');end = top_level(html[start:])[0][1] + start
    svg_start = html.index('<svg', html.index('<template>'))
    shell = html[svg_start:html.index('>', start) + 1] + html[end - 4:html.rindex('</svg>') + 6]
    return comp, shell, frames


def render(project, out, size=(720, 1280), audio=True, workers=None):
    """Shots render in parallel, one Chromium per worker, each to its own cached segment.

    Every frame is drawn from data alone, so a shot whose markup did not change since
    the last render is reused, and only the changed shots are drawn again.
    """
    project, out = Path(project), Path(out);out.parent.mkdir(parents=True, exist_ok=True)
    index = (project / 'index.html').read_text();fonts = FONT_STYLE.search(index);fonts = fonts.group(1).split('*{')[0] if fonts else ''
    shots = [c for c in clips(project) if c['id'] != 'captions'];cap = next((c for c in clips(project) if c['id'] == 'captions'), None)
    total = round((shots[-1]['start'] + shots[-1]['duration']) * FPS)
    cap_comp, cap_shell, cap_frames = states((project / cap['src']).read_text()) if cap else (None, '', [])
    cache = project / '.render-cache';cache.mkdir(exist_ok=True);jobs = []
    for shot in shots:
        html = (project / shot['src']).read_text();first = round(shot['start'] * FPS);count = min(round(shot['duration'] * FPS), total - first)
        caps = [cap_frames[min(first + f, len(cap_frames) - 1)] for f in range(count)] if cap_frames else []
        key = hashlib.sha256(json.dumps([html, cap_shell, caps, fonts, list(size), count]).encode()).hexdigest()[:20]
        jobs.append({'src': shot['src'], 'count': count, 'caps': caps, 'segment': str(cache / f'{key}.mp4')})
    todo = [j for j in jobs if not Path(j['segment']).exists()]
    workers = max(1, min(workers or min(4, os.cpu_count() or 1), len(todo) or 1));bins = [[] for _ in range(workers)]
    for job in sorted(todo, key=lambda j: -j['count']):min(bins, key=lambda b: sum(j['count'] for j in b)).append(job)
    common = (str(project), fonts, cap_comp, cap_shell, list(size))
    if workers == 1:_render_shots(common, todo)
    else:
        with ProcessPoolExecutor(workers) as pool:list(pool.map(_render_shots, [common] * workers, bins))
    for job in jobs:
        frames = int(subprocess.run(['ffprobe', '-v', 'error', '-count_packets', '-select_streams', 'v:0', '-show_entries', 'stream=nb_read_packets', '-of', 'csv=p=0', job['segment']], capture_output=True, text=True).stdout.strip() or 0)
        if frames != job['count']:Path(job['segment']).unlink(missing_ok=True);raise RuntimeError(f'{job["src"]}: {frames} frames rendered, {job["count"]} planned')
    used = {Path(j['segment']).name for j in jobs}
    for old in cache.glob('*.mp4'):
        if old.name not in used:old.unlink()
    listing = cache / 'concat.txt';listing.write_text(''.join(f"file '{j['segment']}'\n" for j in jobs))
    silent = out.with_suffix('.silent.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(listing), '-c', 'copy', str(silent)], check=True)
    written = sum(j['count'] for j in jobs)
    if not audio:silent.replace(out);return {'frames': written, 'file': str(out), 'shots_drawn': len(todo), 'shots': len(jobs)}
    return {'frames': written, 'file': str(mix(project, silent, out, written / FPS)), 'shots_drawn': len(todo), 'shots': len(jobs)}


def _render_shots(common, jobs):
    """One worker: one Chromium page, each shot piped straight to its own segment."""
    if not jobs:return
    from playwright.sync_api import sync_playwright
    import functools, http.server, threading
    project, fonts, cap_comp, cap_shell, size = common;project = Path(project)
    handler = functools.partial(_QuietHandler, directory=str(project));server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start();base = f'http://127.0.0.1:{server.server_address[1]}/'
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=_chromium());page = browser.new_page(viewport={'width': size[0], 'height': size[1]})
            for job in jobs:
                comp, shell, frames = states((project / job['src']).read_text())
                tmp = project / f'.render-{comp}.html';part = Path(job['segment']).with_suffix('.part.mp4')
                layer = 'position:absolute;inset:0;width:100%;height:100%'
                tmp.write_text(f'<!doctype html><html><head><meta charset="utf-8"><style>{fonts} html,body{{margin:0;background:#000;width:{size[0]}px;height:{size[1]}px;overflow:hidden;position:relative}} svg{{{layer}}}</style></head>'
                               f'<body>{shell}{cap_shell}</body></html>')
                ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'image2pipe', '-framerate', str(FPS), '-i', '-', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'medium', str(part)], stdin=subprocess.PIPE)
                try:
                    page.goto(base + tmp.name, wait_until='load', timeout=300000)
                    page.evaluate("Promise.all(['700 40px Inter','900 40px Inter','700 40px \"EB Garamond\"'].map(f => document.fonts.load(f).catch(() => null))).then(() => document.fonts.ready)")
                    for f in range(job['count']):
                        page.evaluate('([a, b, ca, cb]) => { document.getElementById(a).innerHTML = b; if (ca) document.getElementById(ca).innerHTML = cb; }',
                                      [f'{comp}-world', frames[min(f, len(frames) - 1)], f'{cap_comp}-world' if cap_comp else None, job['caps'][f] if job['caps'] else ''])
                        ff.stdin.write(page.screenshot(type='png'))
                finally:
                    tmp.unlink();ff.stdin.close();ff.wait()
                part.replace(job['segment'])
            browser.close()
    finally:server.shutdown()


# 2026-10-10 sound study against the references: they master near -14 LUFS (ours -16.7), the
# voice carries ~8 dB more 2-4 kHz presence and less 100-250 Hz boom, and the bed fills the
# pauses between lines instead of dropping out.
LOUDNESS = -13  # single-pass loudnorm lands about 1 LU low: measures -14 like the references
VOICE_EQ = 'highpass=f=90,equalizer=f=200:t=o:w=1:g=-3,equalizer=f=3200:t=o:w=1.2:g=5,highshelf=f=7000:g=2'
MUSIC_EQ = 'equalizer=f=90:t=o:w=1.5:g=-5,highshelf=f=3000:g=4,lowpass=f=12000'


def mix(project, silent, out, duration):
    """Narration + SFX cues, loudness-normalised on the combined mix."""
    plan = json.loads((project / 'audio-plan.json').read_text()) if (project / 'audio-plan.json').exists() else {}
    index = (project / 'index.html').read_text()
    voice = re.search(r'<audio id="narration" src="([^"]+)"[^>]*data-volume="([\d.]+)"', index)
    inputs = ['-i', str(silent), '-i', str(project / (voice.group(1) if voice else plan['narration']))];filters = [f'[1:a]aresample=48000,{VOICE_EQ},asplit=2[v0][vkey]'];labels = ['[v0]']
    cues = [c for c in plan.get('sfx_cues', []) if c['start'] < duration]
    for k, cue in enumerate(cues):
        inputs += ['-i', str(project / cue['file'])];delay = int(cue['start'] * 1000)
        filters.append(f'[{k + 2}:a]aresample=48000,volume={cue["volume"]},adelay={delay}|{delay}[s{k}]');labels.append(f'[s{k}]')
    music = plan.get('music')
    if music and (project / music['file']).exists():
        # Music bed, ducked under the voice with a sidechain compressor keyed on the narration.
        inputs += ['-i', str(project / music['file'])];k = len(cues) + 2
        filters.append(f'[{k}:a]aresample=48000,{MUSIC_EQ},volume={music.get("volume", .22)}[m0]')
        filters.append('[m0][vkey]sidechaincompress=threshold=0.02:ratio=4:attack=15:release=350[mus]');labels.append('[mus]')
    else:filters[0] = f'[1:a]aresample=48000,{VOICE_EQ}[v0]'
    filters.append(f'{"".join(labels)}amix=inputs={len(labels)}:normalize=0,apad,atrim=0:{duration:.3f},loudnorm=I={LOUDNESS}:TP=-1:LRA=9[a]')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *inputs, '-filter_complex', ';'.join(filters), '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-movflags', '+faststart', str(out)], check=True)
    silent.unlink()
    return out


def main():
    a = argparse.ArgumentParser(description=__doc__.split('\n')[0]);a.add_argument('project', type=Path);a.add_argument('out', type=Path)
    a.add_argument('--width', type=int, default=720);a.add_argument('--no-audio', action='store_true');a.add_argument('--workers', type=int)
    args = a.parse_args();print(json.dumps(render(args.project, args.out, (args.width, round(args.width * 16 / 9)), not args.no_audio, args.workers)))


if __name__ == '__main__':
    main()
