"""Atelier sound: narration takes, sound design, a small score, mix and measurement.

Narration uses Motif's approved Kokoro voices through the same pinned
HyperFrames TTS tool as Classic, one take per line, cached by content so a
resume never regenerates a take whose text, voice and speed are unchanged.
Line timing is measured from the takes; there is no word-level alignment and
nothing claims one. Sound effects and music are synthesised from seeded code
(no samples, no licences): recipes are named in film.json and placed on the
same moment table the picture uses, so a cue and its action share one number.

Measurements (loudness, true peak, clipping, A/V offset) are technical
evidence. They are never listening approval.
"""
import json
import os
import subprocess
import wave
from pathlib import Path

import numpy as np

from .project import ROOT, sha, sha_value

RATE = 48000
TARGET = {'integrated_lufs': -14.0, 'tolerance_lu': 1.0, 'true_peak_dbtp': -1.0}
GAP_MIN = .08


def _pin():
    from motif_reel import PIN, VOICES
    return PIN, VOICES


# narration --------------------------------------------------------------------

def take(text, voice, speed, cache, python=None):
    """One trimmed TTS take, reused when text/voice/speed/tool are unchanged. Returns (path, reused)."""
    pin, voices = _pin()
    if voice not in voices:raise ValueError(f'voice {voice!r} is not approved (approved: {", ".join(voices)})')
    key = sha_value([text, voice, speed, pin, 'trim40ms'])[:24];folder = Path(cache) / 'voice';folder.mkdir(parents=True, exist_ok=True)
    out = folder / f'{key}.wav'
    if out.is_file():return out, True
    (folder / f'{key}.txt').write_text(text + '\n');raw = folder / f'{key}.raw.wav'
    env = dict(os.environ)
    py = python or (ROOT / '.venv/bin/python')
    if Path(py).exists():env['HYPERFRAMES_PYTHON'] = str(py)
    subprocess.run(['npx', '--yes', f'hyperframes@{pin}', 'tts', f'--text-file={key}.txt', f'--voice={voice}', f'--speed={speed}', f'--output={raw.name}', '--json'],
                   cwd=folder, env=env, check=True, capture_output=True, timeout=900)
    trim = 'silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.04'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(raw), '-af', f'{trim},areverse,{trim},areverse', str(out)], check=True)
    raw.unlink()
    return out, False


def load(path, mono=True):
    """Decode to float at 48 kHz; mono=False keeps every channel (no downmix that could invent or hide overs)."""
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-f', 'f32le', *(['-ac', '1'] if mono else []), '-ar', str(RATE), '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype='<f4').astype(np.float64)


def save(path, data):
    data = np.atleast_2d(data);data = data.T if data.shape[0] in (1, 2) and data.shape[0] < data.shape[1] else data
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(data.shape[1]);w.setsampwidth(2);w.setframerate(RATE)
        w.writeframes((np.clip(data, -1, 1) * 32767).astype('<i2').tobytes())


# sound design -----------------------------------------------------------------

def _band(x, lo, hi):
    spec = np.fft.rfft(x);f = np.fft.rfftfreq(len(x), 1 / RATE)
    mask = 1 / (1 + (lo / np.maximum(f, 1)) ** 4) / (1 + (f / hi) ** 4) if hi else 1 / (1 + (lo / np.maximum(f, 1)) ** 4)
    return np.fft.irfft(spec * mask, len(x))


def _t(length):return np.arange(int(length * RATE)) / RATE


def _env(t, attack, decay):return np.minimum(1, t / max(attack, 1e-4)) * np.exp(-t / max(decay, 1e-4))


def _glide(t, f0, f1, curve=1.0):
    length = t[-1] if len(t) > 1 else 1;freq = f0 + (f1 - f0) * (t / length) ** curve
    return np.sin(2 * np.pi * np.cumsum(freq) / RATE)


def _norm(x, peak=.9):
    m = np.max(np.abs(x)) if len(x) else 0
    return x / m * peak if m > 0 else x


def recipe(name, params, rng):
    """Seeded procedural sound recipes. Every recipe is original code, no recordings."""
    p = params;n = lambda length: rng.standard_normal(int(length * RATE))
    if name == 'pop':
        L = p.get('length', .14);t = _t(L);f = p.get('pitch', 420)
        body = _glide(t, f * 2.2, f * .6, .5) * _env(t, .001, L / 4);snap = _band(n(L), 1500, 9000) * _env(t, .0005, .012)
        return _norm(body * .8 + snap * .9)
    if name == 'thud':
        L = p.get('length', .3);t = _t(L)
        return _norm(_glide(t, p.get('pitch', 95), 38, .6) * _env(t, .002, L / 4) + _band(n(L), 40, 400) * _env(t, .001, .03) * .6)
    if name in ('whoosh', 'swish'):
        L = p.get('length', .45 if name == 'whoosh' else .22);t = _t(L);x = n(L)
        lo, hi = p.get('lo', 300), p.get('hi', 3500);parts = np.array_split(np.arange(len(t)), 12);out = np.zeros(len(t))
        for k, idx in enumerate(parts):
            c = lo + (hi - lo) * (k / 11 if p.get('rise', True) else 1 - k / 11);out[idx] = _band(x, c * .5, c * 1.5)[idx]
        return _norm(out * np.sin(np.pi * t / L) ** 1.6)
    if name == 'tick':
        t = _t(p.get('length', .035));return _norm(_band(n(len(t) / RATE), 2000, 10000) * _env(t, .0003, .004) + np.sin(2 * np.pi * p.get('pitch', 2400) * t) * _env(t, .0003, .01) * .4)
    if name == 'step':
        L = p.get('length', .09);t = _t(L);return _norm(_band(n(L), 80, p.get('bright', 1400)) * _env(t, .002, .018))
    if name == 'boing':
        L = p.get('length', .55);t = _t(L);f = p.get('pitch', 180)
        freq = f * (1 + .6 * np.exp(-t * 7) * np.sin(2 * np.pi * 11 * t)) * (1 + .5 * (1 - t / L))
        return _norm(np.sin(2 * np.pi * np.cumsum(freq) / RATE) * _env(t, .003, L / 2.5))
    if name in ('squeak', 'zip', 'blip', 'stretch'):
        defaults = {'squeak': (1100, 1900, .14), 'zip': (500, 2600, .2), 'blip': (700, 760, .07), 'stretch': (180, 520, .6)}[name]
        f0, f1, L = p.get('from', defaults[0]), p.get('to', defaults[1]), p.get('length', defaults[2]);t = _t(L)
        tone = _glide(t, f0, f1, .7);tone = tone + .3 * np.sign(tone) * np.abs(tone) ** 3 if name != 'blip' else tone
        vib = 1 + (.25 * np.sin(2 * np.pi * 23 * t) if name == 'stretch' else 0)
        return _norm(tone * vib * np.sin(np.pi * np.minimum(1, t / L)) ** .6 * _env(t, .004, L * 2))
    if name in ('hiss', 'sizzle', 'rain', 'wave', 'rumble'):
        L = p.get('length', 1.0);t = _t(L);x = n(L);fade = np.minimum(1, t / p.get('attack', .05)) * np.minimum(1, (L - t) / p.get('release', .2))
        if name == 'hiss':y = _band(x, p.get('lo', 2500), p.get('hi', 12000))
        elif name == 'sizzle':y = _band(x, 1800, 9000) * .35 + _band((rng.random(len(t)) > 1 - p.get('density', .002)) * rng.standard_normal(len(t)), 900, 7000) * 3
        elif name == 'rain':y = _band(x, 600, 9000) * .5 + _band((rng.random(len(t)) > .9985) * rng.standard_normal(len(t)), 2000, 9000) * 2.5
        elif name == 'wave':y = _band(x, 120, 2600) * (.35 + .65 * np.sin(np.pi * t / L) ** 2)
        else:y = _band(x, 20, p.get('hi', 160)) * (.6 + .4 * np.sin(2 * np.pi * .7 * t + 1))
        return _norm(y * fade * p.get('level', 1))
    if name == 'raspberry':
        L = p.get('length', .45);t = _t(L);f = p.get('pitch', 95)
        buzz = np.sign(np.sin(2 * np.pi * np.cumsum(f + 25 * np.sin(2 * np.pi * 7 * t)) / RATE)) * (.6 + .4 * np.sin(2 * np.pi * 31 * t))
        return _norm(_band(buzz + n(L) * .3, 80, 2600) * np.sin(np.pi * t / L) ** .5)
    if name == 'crack':
        L = p.get('length', .18);t = _t(L)
        return _norm(_band(n(L), 700, 11000) * _env(t, .0002, .02) + sum(np.sin(2 * np.pi * f * t) * _env(t, .0005, .04) for f in (1730, 2410, 3150)) * .2)
    if name == 'chime':
        L = p.get('length', 1.6);t = _t(L);f = p.get('pitch', 880)
        return _norm(sum(a * np.sin(2 * np.pi * f * r * t) * _env(t, .002, L / (1 + r)) for r, a in ((1, 1), (2.01, .5), (2.76, .35), (5.4, .15))))
    if name == 'whale':
        L = p.get('length', 2.4);t = _t(L);f0, f1 = p.get('from', 180), p.get('to', 320)
        freq = f0 + (f1 - f0) * np.sin(np.pi * t / L) ** 1.2 + 6 * np.sin(2 * np.pi * 5 * t)
        phase = 2 * np.pi * np.cumsum(freq) / RATE;body = sum(a * np.sin(k * phase) for k, a in ((1, 1), (2, .45), (3, .2), (4, .08)))
        return _norm(body * np.sin(np.pi * t / L) ** 1.5 + _band(n(L), 100, 1200) * .04)
    if name == 'creak':
        L = p.get('length', .6);t = _t(L);rate = 40 + 30 * np.sin(2 * np.pi * 1.3 * t)
        pulses = (np.diff(np.floor(np.cumsum(rate) / RATE), prepend=0) > 0).astype(float)
        return _norm(_band(pulses + n(L) * .02, 300, 2400) * np.sin(np.pi * t / L) ** .8)
    if name == 'thunder':
        L = p.get('length', 2.5);t = _t(L)
        return _norm(_band(n(L), 25, 400) * _env(t, .02, L / 3) * (1 + .5 * np.sin(2 * np.pi * 3 * t)) + _band(n(L), 400, 4000) * _env(t, .001, .08) * .5)
    raise ValueError(f'unknown sound recipe {name!r}')


# score ------------------------------------------------------------------------

def _hz(m):return 440 * 2 ** ((m - 69) / 12)


def _note(instrument, midi, length, vel, rng):
    f = _hz(midi)
    if instrument == 'drum':
        t = _t(.4)
        if midi <= 36:return _glide(t, 120, 42, .5) * _env(t, .001, .09) * vel
        if midi <= 40:return (_band(rng.standard_normal(len(t)), 1200, 8000) * .6 + np.sin(2 * np.pi * 190 * t) * .5) * _env(t, .001, .05) * vel
        return _band(rng.standard_normal(len(t)), 6000, 16000) * _env(t, .0005, .02) * vel
    tail = {'pluck': .25, 'pizz': .12, 'marimba': .5, 'bell': 1.8, 'celesta': 1.0, 'pad': .6, 'bass': .3}[instrument]
    t = _t(length + tail)
    if instrument in ('pluck', 'pizz'):
        d = .35 if instrument == 'pluck' else .12
        y = sum(np.sin(2 * np.pi * f * k * t) / k ** 1.3 * np.exp(-t * k * (1 / d)) for k in range(1, 7))
    elif instrument == 'marimba':y = (np.sin(2 * np.pi * f * t) + .25 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t * 18)) * np.exp(-t * 4.5)
    elif instrument in ('bell', 'celesta'):
        y = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t * r * (1.2 if instrument == 'bell' else 2.5)) for r, a in ((1, 1), (2.0, .4), (3.0, .2), (4.2, .1)))
    elif instrument == 'pad':
        y = sum(sum(np.sin(2 * np.pi * f * k * (1 + dt) * t) / k ** 1.6 for k in range(1, 6)) for dt in (-.004, 0, .005)) / 3
        y *= np.minimum(1, t / .35) * np.clip((length + tail - t) / tail, 0, 1)
    else:y = (np.sin(2 * np.pi * f * t) + .3 * np.sin(4 * np.pi * f * t)) * np.exp(-t * 2.2)
    if instrument not in ('pad',):y *= np.minimum(1, t / .004) * np.clip((length + tail - t) / tail, 0, 1)
    return y * vel


def score(music, duration, seed):
    """film.json music: {"kind": "notes", "tempo": bpm, "tracks": [{"instrument", "notes": [[beat, midi, beats, vel]]}]}"""
    out = np.zeros((int(duration * RATE) + RATE, 2))
    if music.get('kind') != 'notes':return out[:int(duration * RATE)]
    beat = 60 / music['tempo']
    for k, track in enumerate(music['tracks']):
        rng = np.random.default_rng(seed + 101 * k);gain = 10 ** (track.get('gain_db', 0) / 20);pan = track.get('pan', 0)
        for start, midi, length, vel in track['notes']:
            y = _note(track['instrument'], midi, length * beat, vel, rng) * gain;a = int(start * beat * RATE);b = min(len(out), a + len(y))
            if a >= len(out):continue
            out[a:b, 0] += y[:b - a] * (1 - pan) / 2 * 1.4;out[a:b, 1] += y[:b - a] * (1 + pan) / 2 * 1.4
    return out[:int(duration * RATE)]


# timing, stems, mix -----------------------------------------------------------

def plan(film, cache, python=None):
    """Voice every line (cached), place lines, check slots. Returns (timing, errors, takes)."""
    from .contracts import resolve_at
    sound = film['sound'];fps = film['fps'];duration = film['frames'] / fps;voice = sound.get('voice');speed = sound.get('speed', 1.0)
    lines, errors, takes = {}, [], []
    for i, line in enumerate(sound['narration']):
        path, reused = take(line['text'], voice, speed, cache, python);length = len(load(path)) / RATE
        start = resolve_at(film, line['at']) / fps;end = start + length
        lines[line['id']] = {'start': round(start, 4), 'end': round(end, 4), 'text': line['text']}
        takes.append({'id': line['id'], 'file': str(path), 'sha256': sha(path), 'seconds': round(length, 3), 'reused_from_cache': reused, 'voice': voice, 'speed': speed})
        if end > duration - .05:errors.append(f'line {line["id"]} ends at {end:.2f}s, after the picture ({duration:.2f}s); re-time the picture or rewrite the line')
        if line.get('ends_before') is not None:
            limit = resolve_at(film, line['ends_before']) / fps
            if end > limit:errors.append(f'line {line["id"]} must end before {line["ends_before"]} ({limit:.2f}s) but runs to {end:.2f}s; re-time the picture or rewrite the line (voice speed is not changed to fit)')
    ordered = list(lines.items())
    for (a, x), (b, y) in zip(ordered, ordered[1:]):
        if y['start'] < x['end'] + GAP_MIN:errors.append(f'line {b} starts at {y["start"]:.2f}s before line {a} ends ({x["end"]:.2f}s)')
    timing = {'method': 'line-level: measured duration of one TTS take per line, placed at the authored frame; no word-level alignment',
              'voice': voice, 'speed': speed, 'duration': duration, 'lines': lines}
    return timing, errors, takes


def stems(film, timing, takes, source, out_dir, seed=0):
    """Write voice/sfx/music stems (48 kHz stereo) and the cue sheet."""
    from .contracts import resolve_at
    from .project import inside
    fps = film['fps'];n = int(film['frames'] / fps * RATE);out_dir = Path(out_dir)
    voice = np.zeros(n);files = {t['id']: t['file'] for t in takes}
    for line_id, line in timing['lines'].items():
        y = load(files[line_id]);a = int(line['start'] * RATE);voice[a:a + len(y)] += y[:max(0, n - a)]
    sfx = np.zeros((n, 2));cues = []
    for k, cue in enumerate(film['sound']['sfx']):
        frame = resolve_at(film, cue['at'], cue.get('offset', 0));start = frame / fps
        if cue.get('recipe'):y = recipe(cue['recipe'], cue.get('params', {}), np.random.default_rng(cue.get('seed', seed * 1000 + k)))
        else:y = load(inside(source, cue['file']))
        y = y * 10 ** (cue.get('gain_db', -6) / 20);a = int(start * RATE);b = min(n, a + len(y));pan = cue.get('pan', 0)
        sfx[a:b, 0] += y[:b - a] * (1 - pan) / 2 * 1.4;sfx[a:b, 1] += y[:b - a] * (1 + pan) / 2 * 1.4
        cues.append({'at': cue['at'], 'frame': frame, 'time': round(start, 4), 'sound': cue.get('recipe') or cue.get('file')})
    music = film['sound']['music'];bed = score(music, n / RATE, seed)[:n] * 10 ** (music.get('gain_db', -18) / 20)
    if len(bed) < n:bed = np.vstack([bed, np.zeros((n - len(bed), 2))])
    env = _envelope(voice);duck = 10 ** (-music.get('duck_db', 8) * np.clip(env / .02, 0, 1) / 20)
    bed = bed * duck[:, None]
    files = {'voice': out_dir / 'voice.wav', 'sfx': out_dir / 'sfx.wav', 'music': out_dir / 'music.wav'}
    save(files['voice'], np.stack([voice, voice], 1));save(files['sfx'], sfx);save(files['music'], bed)
    pre = np.stack([voice, voice], 1) + sfx + bed
    save(out_dir / 'premix.wav', pre / max(1, np.max(np.abs(pre)) / .98))
    return {k: str(v) for k, v in files.items()}, cues


def _envelope(x, win=.05):
    w = int(win * RATE);power = np.convolve(x * x, np.ones(w) / w, 'same');env = np.sqrt(power)
    out = np.empty_like(env);g = 0.0;att, rel = np.exp(-1 / (.03 * RATE / 64)), np.exp(-1 / (.35 * RATE / 64))
    for i in range(0, len(env), 64):                     # block-rate attack/release smoothing
        v = env[i];g = att * g + (1 - att) * v if v > g else rel * g + (1 - rel) * v;out[i:i + 64] = g
    return out


def loudness(path):
    from motif_produce import loudness as measure
    return measure(Path(path))


def master(premix, out, target=TARGET):
    """Measured gain into a look-ahead limiter, repeated until the integrated level converges on the target.

    The limiter ceiling sits 1 dB under the true-peak target so the AAC encode keeps headroom.
    """
    ceiling = 10 ** ((target['true_peak_dbtp'] - 1.0) / 20);gain = target['integrated_lufs'] - loudness(premix)['integrated_lufs']
    for _ in range(4):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(premix), '-af', f'volume={gain:.3f}dB,alimiter=limit={ceiling:.4f}:attack=3:release=60:level=false',
                        '-ar', str(RATE), '-c:a', 'pcm_s24le', str(out)], check=True)
        miss = target['integrated_lufs'] - loudness(out)['integrated_lufs']
        if abs(miss) <= .3:break
        gain += miss
    return out


def clipped_samples(path):
    data = load(path, mono=False);return int(np.sum(np.abs(data) >= .9999))


def av_offset_ms(stem, delivered):
    """Cross-correlate the sound-design stem with the delivered audio; 0 ms means cues sit where they were placed."""
    a, b = load(stem), load(delivered);n = min(len(a), len(b))
    if n == 0 or np.max(np.abs(a[:n])) < 1e-4:return None
    hop = 48;a, b = np.abs(a[:n:hop]), np.abs(b[:n:hop]);a -= a.mean();b -= b.mean()
    lag = int(.25 * RATE / hop);corr = [float(np.dot(a[max(0, -k):len(a) - max(0, k)], b[max(0, k):len(b) - max(0, -k)])) for k in range(-lag, lag + 1)]
    return round((int(np.argmax(corr)) - lag) * hop / RATE * 1000, 1)


def captions(timing, out, width=34):
    """WebVTT from measured line spans (line-level timing; not word-aligned)."""
    def stamp(s):return f'{int(s // 3600):02d}:{int(s % 3600 // 60):02d}:{s % 60:06.3f}'
    blocks = ['WEBVTT', '', 'NOTE line starts and ends are measured from TTS takes; a line split across cards divides its span by length (approximate); no word-level alignment', '']
    for k, (line_id, line) in enumerate(timing['lines'].items(), 1):
        words, rows, row = line['text'].split(), [], ''
        for w in words:
            if row and len(row) + 1 + len(w) > width:rows.append(row);row = w
            else:row = f'{row} {w}'.strip()
        rows.append(row)
        chunks = [rows[i:i + 2] for i in range(0, len(rows), 2)];span = (line['end'] - line['start']) / len(chunks)
        for j, chunk in enumerate(chunks):
            blocks += [f'{line_id}-{j + 1}', f'{stamp(line["start"] + j * span)} --> {stamp(line["start"] + (j + 1) * span)}', *chunk, '']
    Path(out).write_text('\n'.join(blocks))
    return out
