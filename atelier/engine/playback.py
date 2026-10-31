"""Deterministic playback: saved film source -> frames -> encoded video.

The same pattern as Classic's motif_frame_render (Chromium draws each frame,
frames pipe to ffmpeg), with an Atelier film contract instead of Classic
compositions. No model is called while rendering. The page is served only the
film's own source folder and the Atelier runtime; every other request is
aborted and fails the render. Frames are rendered in independent seekable
segments (one Chromium per worker) and concatenated, so a frame never depends
on the one before it.

Execution boundary, stated plainly: project JavaScript runs inside a headless
Chromium page with network access limited to the local file server and a
per-frame timeout. That is browser isolation plus request interception, not an
operating-system sandbox. Python never imports or executes project files.
"""
import base64
import functools
import http.server
import io
import json
import mimetypes
import os
import subprocess
import threading
import time
from glob import glob
from pathlib import Path

RUNTIME = Path(__file__).resolve().parent / 'runtime'
PREVIEW = (360, 640)
DELIVERY = (1080, 1920)
FRAME_TIMEOUT_MS = 20000
BOOT_TIMEOUT_MS = 60000
THUMB = (27, 48)


def chromium():
    """MOTIF_CHROMIUM, else the pre-installed Playwright Chromium (either archive layout)."""
    override = os.environ.get('MOTIF_CHROMIUM')
    if override:return override
    found = sorted(glob('/opt/pw-browsers/chromium-*/chrome-linux*/chrome'))
    return found[-1] if found else None


class _Handler(http.server.BaseHTTPRequestHandler):
    """GET only; serves the film source folder, the runtime and the timing document."""
    def log_message(self, *args):pass

    def do_GET(self):
        path = self.path.split('?', 1)[0].lstrip('/')
        if path == '':body, kind = (RUNTIME / 'player.html').read_bytes(), 'text/html'
        elif path == '__atelier/timing.json':body, kind = self.server.timing, 'application/json'
        else:
            base, rel = (RUNTIME, path[len('__atelier/'):]) if path.startswith('__atelier/') else (self.server.source, path)
            target = (base / rel).resolve()
            if not target.is_relative_to(base) or not target.is_file() or any(p.is_symlink() for p in [base / rel, *(base / rel).parents] if p.is_relative_to(base)):
                self.send_error(404);return
            body = target.read_bytes();kind = mimetypes.guess_type(target.name)[0] or 'application/octet-stream'
        self.send_response(200);self.send_header('Content-Type', kind);self.send_header('Content-Length', str(len(body)));self.end_headers();self.wfile.write(body)


class Server:
    def __init__(self, source, timing):
        self.httpd = http.server.ThreadingHTTPServer(('127.0.0.1', 0), _Handler)
        self.httpd.source = Path(source).resolve();self.httpd.timing = json.dumps(timing).encode()
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()
        self.base = f'http://127.0.0.1:{self.httpd.server_address[1]}/'

    def close(self):self.httpd.shutdown();self.httpd.server_close()


class RenderError(RuntimeError):
    pass


def _encoder(out, size, fps, crf):
    return subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'image2pipe', '-framerate', str(fps), '-i', '-',
                             '-vf', f'scale={size[0]}:{size[1]}:flags=lanczos,format=yuv420p', '-c:v', 'libx264', '-preset', 'medium',
                             '-crf', str(crf), '-g', str(fps * 2), '-r', str(fps), str(out)], stdin=subprocess.PIPE, stderr=subprocess.PIPE)


def _worker(base, size, frames, out, fps, crf, stills, blocked, errors, keep):
    from playwright.sync_api import sync_playwright
    encoder = _encoder(out, size, fps, crf) if out else None
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=chromium())
            try:
                page = browser.new_page(viewport={'width': size[0], 'height': size[1]}, device_scale_factor=1)
                def route(r):
                    if r.request.url.startswith(base):r.continue_()
                    else:blocked.append(r.request.url);r.abort()
                page.route('**/*', route)
                page.on('pageerror', lambda e: errors.append(f'page error: {e}'))
                page.on('console', lambda m: errors.append(f'console {m.type}: {m.text}') if m.type == 'error' else None)
                page.set_default_timeout(FRAME_TIMEOUT_MS)
                page.goto(f'{base}?w={size[0]}&h={size[1]}', wait_until='load', timeout=BOOT_TIMEOUT_MS)
                page.wait_for_function('window.__atelierReady === true || window.__atelierError !== undefined', timeout=BOOT_TIMEOUT_MS)
                boot_error = page.evaluate('window.__atelierError || null')
                if boot_error:raise RenderError(f'film failed to boot: {boot_error}')
                cdp = page.context.new_cdp_session(page)
                for n in frames:
                    # Runtime.evaluate's own timeout terminates a runaway script; page.evaluate would wait forever.
                    # The pixels come from the canvas buffer in the same call, so a capture can never show a stale composited frame.
                    got = cdp.send('Runtime.evaluate', {'expression': f'Atelier.seek({n}) && document.getElementById("film").toDataURL("image/png")',
                                                        'timeout': FRAME_TIMEOUT_MS, 'returnByValue': True})
                    if 'exceptionDetails' in got:
                        detail = got['exceptionDetails'];text = (detail.get('exception') or {}).get('description') or detail.get('text', '')
                        raise RenderError(f'frame {n}: ' + ('timed out after %d ms (execution terminated)' % FRAME_TIMEOUT_MS if 'terminated' in text.lower() else text))
                    png = base64.b64decode(got['result']['value'].split(',', 1)[1])
                    if encoder:encoder.stdin.write(png)
                    if n in stills:keep[n] = png
                    if errors or blocked:raise RenderError('; '.join(errors + [f'blocked request {u}' for u in blocked]))
            finally:browser.close()
    finally:
        if encoder:
            encoder.stdin.close();code = encoder.wait()
            if code:errors.append('encoder failed: ' + encoder.stderr.read().decode(errors='replace')[-400:])


def render(source, film, timing, out, size, frames=None, workers=3, crf=18, stills=()):
    """Render frames [a, b) of the saved film to an H.264 file. Returns a record with timings and stills."""
    a, b = frames or (0, film['frames']);fps = film['fps'];out = Path(out);out.parent.mkdir(parents=True, exist_ok=True)
    count = b - a;workers = max(1, min(workers, count // 30 or 1))
    chunks = [(a + count * k // workers, a + count * (k + 1) // workers) for k in range(workers)]
    server = Server(source, timing);blocked, errors, keep, threads, parts = [], [], {}, [], []
    started = time.time()
    try:
        for k, (x, y) in enumerate(chunks):
            part = out.with_name(f'.{out.stem}.part{k}.mp4');parts.append(part)
            t = threading.Thread(target=lambda x=x, y=y, part=part: _safe(_worker, errors, server.base, size, range(x, y), part, fps, crf, set(stills), blocked, errors, keep))
            t.start();threads.append(t)
        for t in threads:t.join()
    finally:server.close()
    if errors or blocked:
        for part in parts:part.unlink(missing_ok=True)
        raise RenderError('; '.join(dict.fromkeys(errors + [f'blocked request {u}' for u in blocked]))[:2000])
    listing = out.with_name(f'.{out.stem}.parts.txt');listing.write_text(''.join(f"file '{p.name}'\n" for p in parts))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(listing), '-c', 'copy', str(out)], check=True)
    listing.unlink()
    for part in parts:part.unlink()
    return {'file': str(out), 'frames': count, 'range': [a, b], 'size': list(size), 'fps': fps, 'workers': workers,
            'seconds': round(time.time() - started, 1), 'blocked_requests': 0, 'stills': keep}


def _safe(fn, errors, *args):
    try:fn(*args)
    except Exception as e:errors.append(f'{type(e).__name__}: {e}')


def mux(video, audio, out, subtitles=None, language='eng', duration=None):
    """Picture + finished audio (+ optional soft captions) into one MP4, cut to the film's exact duration.

    Not -shortest: a caption track ends with its last cue and would trim the picture.
    AAC at 256 kbps: the native encoder at 192 kbps overshot sharp synthetic transients by
    about 3.8 dB (measured: master -1.87 dBTP became +1.89 dBTP), 256 kbps kept -1.87.
    """
    args = ['ffmpeg', '-v', 'error', '-y', '-i', str(video), '-i', str(audio)]
    if subtitles:args += ['-i', str(subtitles)]
    args += ['-map', '0:v', '-map', '1:a'] + (['-map', '2:s', '-c:s', 'mov_text', f'-metadata:s:s:0', f'language={language}'] if subtitles else [])
    args += ['-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-ac', '2', *(['-t', f'{duration:.6f}'] if duration else []), '-movflags', '+faststart', str(out)]
    subprocess.run(args, check=True)
    return out


def probe(path):
    data = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-count_frames', '-show_entries',
                                      'format=duration:stream=index,codec_type,codec_name,width,height,r_frame_rate,nb_read_frames,pix_fmt,sample_rate,channels,duration',
                                      '-of', 'json', str(path)], capture_output=True, text=True, check=True).stdout)
    streams = data['streams'];v = next((s for s in streams if s['codec_type'] == 'video'), None)
    a = next((s for s in streams if s['codec_type'] == 'audio'), None);sub = [s for s in streams if s['codec_type'] == 'subtitle']
    num, den = map(int, v['r_frame_rate'].split('/')) if v else (0, 1)
    return {'duration': float(data['format']['duration']), 'video': v and {'codec': v['codec_name'], 'width': v['width'], 'height': v['height'], 'fps': num / den,
            'frames': int(v.get('nb_read_frames', 0)), 'pix_fmt': v.get('pix_fmt'), 'duration': float(v.get('duration', 0))},
            'audio': a and {'codec': a['codec_name'], 'sample_rate': int(a['sample_rate']), 'channels': a['channels'], 'duration': float(a.get('duration', 0))},
            'subtitles': [s['codec_name'] for s in sub]}


def extract(video, frames, size=None):
    """Decode exact frame indices from an encoded file (evidence comes from the delivered bytes)."""
    from PIL import Image
    expr = '+'.join(f'eq(n\\,{n})' for n in frames)
    scale = f',scale={size[0]}:{size[1]}:flags=area' if size else ''
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(video), '-vf', f'select={expr}{scale}', '-fps_mode', 'passthrough', '-f', 'image2pipe', '-c:v', 'png', '-'],
                         capture_output=True, check=True).stdout
    images, i = [], 0
    while i < len(raw):                       # walk PNG chunks; stop at each IEND
        j = i + 8
        while True:
            length = int.from_bytes(raw[j:j + 4], 'big');kind = raw[j + 4:j + 8];j += 12 + length
            if kind == b'IEND':break
        images.append(Image.open(io.BytesIO(raw[i:j])).convert('RGB'));i = j
    if len(images) != len(frames):raise RenderError(f'decoded {len(images)} of {len(frames)} requested frames')
    return images


def thumb(image):
    from PIL import Image
    return image.convert('L').resize(THUMB, Image.Resampling.BOX).tobytes().hex()


def thumb_distance(a, b):
    x, y = bytes.fromhex(a), bytes.fromhex(b)
    diffs = [abs(p - q) for p, q in zip(x, y)]
    return {'mean': round(sum(diffs) / len(diffs), 3), 'max': max(diffs)}


def fingerprint(video, frames):
    return {str(n): thumb(img) for n, img in zip(frames, extract(video, frames))}


def sheet(images, labels, out, cols=6, width=180):
    from PIL import Image, ImageDraw
    height = width * 16 // 9;rows = (len(images) + cols - 1) // cols
    canvas = Image.new('RGB', (cols * (width + 6) + 6, rows * (height + 22) + 6), '#f4f1ea');draw = ImageDraw.Draw(canvas)
    for k, (img, label) in enumerate(zip(images, labels)):
        x, y = 6 + (k % cols) * (width + 6), 6 + (k // cols) * (height + 22)
        canvas.paste(img.resize((width, height)), (x, y + 16));draw.text((x, y + 2), label, fill='#222')
    Path(out).parent.mkdir(parents=True, exist_ok=True);canvas.save(out)
    return out
