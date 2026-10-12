"""Original music bed for a reel, synthesised in code (no samples, no licences).

Every reference reel runs a light instrumental bed under the voice; Motif's
reels were voice only. bed() writes a deterministic loop for one film: a
four-chord progression in a key and tempo chosen from the film's look and
seed, a plucked arpeggio, a round bass, and a soft kick and shaker. The mix
(motif_frame_render.mix) keeps it about 20 dB under the narration and ducks
it further while the voice speaks.

Cuts on the beat (2026-10-12 motion study): given the film's cut times, beat_grid() lays the beats so
every cut lands on one and starts a new bar (the chord changes on the cut). Between two cuts the beats
are evenly spaced, so the tempo shifts a little at a cut and holds in between; a cut that would need
more than MAX_SHIFT is left off the grid rather than bend the tempo audibly. The bpm is the one in the
look's range that needs the least bending.
"""
import hashlib
import json
import wave
from pathlib import Path

RATE = 48000
# Look -> (tempo range, scale mode, brightness). Kept small and friendly: the bed
# should sit under a voice, not compete with it.
FEEL = {
    'paper-craft': ((96, 108), 'major', .55), 'neon-arcade': ((112, 124), 'minor', .8),
    'primary-pop': ((108, 120), 'major', .75), 'candy-pastel': ((92, 104), 'major', .5),
    'great-outdoors': ((96, 110), 'major', .6),
}
PROGRESSIONS = {'major': [(0, 4, 7), (7, 11, 14), (9, 12, 16), (5, 9, 12)],      # I V vi IV
                'minor': [(0, 3, 7), (8, 12, 15), (3, 7, 10), (10, 14, 17)]}     # i VI III VII


def _rng(key):
    h = hashlib.sha256(key.encode()).digest();return int.from_bytes(h[:8], 'big')


MAX_SHIFT = .08   # largest tempo change at a cut, as a share of the base beat


def beat_grid(duration, beat, cuts=()):
    """[(time, length, downbeat)] covering duration (+ a bar), with each cut that fits on a downbeat.
    Returns (beats, cuts_on_beat, largest tempo shift)."""
    anchors = [0.0];on = []
    for c in sorted(t for t in cuts if 0 < t < duration):
        n = round((c - anchors[-1]) / beat)
        if n >= 1 and abs((c - anchors[-1]) / n / beat - 1) <= MAX_SHIFT:anchors.append(c);on.append(c)
    beats, shift = [], 0.0
    for a, b in zip(anchors, anchors[1:]):
        n = round((b - a) / beat);step = (b - a) / n;shift = max(shift, abs(step / beat - 1))
        beats += [(a + i * step, step, i % 4 == 0) for i in range(n)]
    a = anchors[-1];i = 0
    while a + i * beat < duration + 4 * beat:beats.append((a + i * beat, beat, i % 4 == 0));i += 1
    return beats, on, shift


def fit_tempo(duration, tempo_range, cuts, default):
    """The bpm in tempo_range (quarter steps) that puts the most cuts on a beat with the least bending."""
    if not cuts:return default
    def cost(bpm):
        _, on, shift = beat_grid(duration, 60 / bpm, cuts);return (len(cuts) - len(on), round(shift, 4), abs(bpm - default))
    return min((tempo_range[0] + q / 4 for q in range(4 * (tempo_range[1] - tempo_range[0]) + 1)), key=cost)


def bed(out, duration, look='paper-craft', seed=0, cuts=()):
    """Write a stereo 48 kHz WAV of `duration` seconds; returns its description. cuts (seconds) are
    put on the beat where they fit (see beat_grid)."""
    import numpy as np
    tempo_range, mode, bright = FEEL.get(look, FEEL['paper-craft'])
    r = _rng(f'{look}|{seed}');bpm = fit_tempo(duration, tempo_range, list(cuts), tempo_range[0] + r % (tempo_range[1] - tempo_range[0] + 1))
    root = 50 + (r >> 8) % 7                        # MIDI D3..G#3
    beat = 60 / bpm;n = int(duration * RATE) + RATE
    t = np.arange(n) / RATE;left = np.zeros(n);right = np.zeros(n)
    hz = lambda m: 440 * 2 ** ((m - 69) / 12)

    def note(start, length, freq, amp, pan=0.0, decay=3.0, harm=(1, .35, .12)):
        a = int(start * RATE);b = min(n, a + int(length * RATE))
        if a >= n:return
        tt = t[:b - a];env = np.exp(-decay * tt) * np.minimum(1, tt * 200)
        wavef = sum(h * np.sin(2 * np.pi * freq * (k + 1) * tt) for k, h in enumerate(harm)) * env * amp
        left[a:b] += wavef * (1 - pan) / 2 * 2;right[a:b] += wavef * (1 + pan) / 2 * 2

    prog = PROGRESSIONS[mode];grid, on, shift = beat_grid(duration, beat, cuts)
    pattern = [0, 1, 2, 1, 2, 1, 0, 2] if (r >> 16) % 2 else [0, 2, 1, 2, 0, 2, 1, 2]
    i = -1;k = 0
    for j, (s, step, down) in enumerate(grid):
        if down:i += 1;k = 0                                                                 # a new bar: on a cut or every 4 beats
        chord = prog[i % 4]
        if down:
            bar = next((g[0] for g in grid[j + 1:] if g[2]), s + 4 * step) - s
            for m in chord:note(s, bar * .98, hz(root + m - 12), .045, 0, .6, (1, .2))       # soft pad
            # 2026-10-10 sound study: the references' beds are bright and light; ours sat almost all
            # below 250 Hz. Bass and kick down, pluck and a bell sparkle up, hats instead of a dull shaker.
            note(s, bar * .5, hz(root + chord[2] + 24), .03 + .02 * bright, (.3, -.3)[i % 2], 4.0, (1, 0, .3))  # bell sparkle on the bar
        if k in (0, 2):note(s, step * 1.8, hz(root + chord[0] - 24), .1 if k == 0 else .08, 0, 2.2, (1, .5, .2))  # bass on 1 and 3
        for h in range(2):                                                                   # pluck arpeggio in eighths
            idx = pattern[(k * 2 + h) % 8];note(s + h * step / 2, step * .9, hz(root + chord[idx] + 12), .07 * bright + .04, (-.4, .4)[h], 6.0, (1, .5, .3, .15))
        a = int(s * RATE);b = min(n, a + int(.18 * RATE))                                  # kick on beats, hat on offbeats
        if a < n:
            kt = t[:b - a];kick = np.sin(2 * np.pi * (50 + 90 * np.exp(-kt * 30)) * kt) * np.exp(-kt * 14) * .11
            left[a:b] += kick;right[a:b] += kick
        a = int((s + step / 2) * RATE);b = min(n, a + int(.05 * RATE))
        if a < n:
            raw = np.random.default_rng(r + j).standard_normal(b - a + 1);hat = np.diff(np.diff(raw, prepend=0))  # crude high-pass: a hat, not a thud
            noise = hat[:b - a] * np.exp(-t[:b - a] * 110) * .03 * (.5 + bright)
            left[a:b] += noise * .8;right[a:b] += noise
        k += 1
    end = int(duration * RATE);fade = int(1.2 * RATE)
    stereo = np.stack([left[:end], right[:end]], 1);stereo[:int(.3 * RATE)] *= np.linspace(0, 1, int(.3 * RATE))[:, None]
    stereo[-fade:] *= np.linspace(1, 0, fade)[:, None]
    stereo /= max(1e-9, np.abs(stereo).max()) / .7
    pcm = (stereo * 32767).astype('<i2')
    out = Path(out);out.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out), 'wb') as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(RATE);w.writeframes(pcm.tobytes())
    return {'file': out.name, 'bpm': bpm, 'root_midi': root, 'mode': mode, 'look': look, 'seed': seed, 'duration': round(duration, 3),
            'cuts': len(list(cuts)), 'cuts_on_beat': len(on), 'tempo_shift_max': round(shift, 3),
            'method': 'original local synthesis (motif_music.bed); no samples, no external music'}

if __name__ == '__main__':
    import argparse
    a = argparse.ArgumentParser(description=__doc__.split('\n')[0]);a.add_argument('out');a.add_argument('--seconds', type=float, default=20)
    a.add_argument('--look', default='paper-craft');a.add_argument('--seed', type=int, default=0);a.add_argument('--cuts', type=float, nargs='*', default=[])
    args = a.parse_args();print(json.dumps(bed(args.out, args.seconds, args.look, args.seed, args.cuts)))
