"""Original music bed for a reel, synthesised in code (no samples, no licences).

Every reference reel runs a light instrumental bed under the voice; Motif's
reels were voice only. bed() writes a deterministic loop for one film: a
four-chord progression in a key and tempo chosen from the film's look and
seed, a plucked arpeggio, a round bass, and a soft kick and shaker. The mix
(motif_frame_render.mix) keeps it about 20 dB under the narration and ducks
it further while the voice speaks.
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


def bed(out, duration, look='paper-craft', seed=0):
    """Write a stereo 48 kHz WAV of `duration` seconds; returns its description."""
    import numpy as np
    tempo_range, mode, bright = FEEL.get(look, FEEL['paper-craft'])
    r = _rng(f'{look}|{seed}');bpm = tempo_range[0] + r % (tempo_range[1] - tempo_range[0] + 1)
    root = 50 + (r >> 8) % 7                        # MIDI D3..G#3
    beat = 60 / bpm;bar = 4 * beat;n = int(duration * RATE) + RATE
    t = np.arange(n) / RATE;left = np.zeros(n);right = np.zeros(n)
    hz = lambda m: 440 * 2 ** ((m - 69) / 12)

    def note(start, length, freq, amp, pan=0.0, decay=3.0, harm=(1, .35, .12)):
        a = int(start * RATE);b = min(n, a + int(length * RATE))
        if a >= n:return
        tt = t[:b - a];env = np.exp(-decay * tt) * np.minimum(1, tt * 200)
        wavef = sum(h * np.sin(2 * np.pi * freq * (k + 1) * tt) for k, h in enumerate(harm)) * env * amp
        left[a:b] += wavef * (1 - pan) / 2 * 2;right[a:b] += wavef * (1 + pan) / 2 * 2

    prog = PROGRESSIONS[mode];bars = int(duration / bar) + 2
    pattern = [0, 1, 2, 1, 2, 1, 0, 2] if (r >> 16) % 2 else [0, 2, 1, 2, 0, 2, 1, 2]
    for i in range(bars):
        chord = prog[i % 4];s = i * bar
        for m in chord:note(s, bar * .98, hz(root + m - 12), .045, 0, .6, (1, .2))           # soft pad
        # 2026-10-10 sound study: the references' beds are bright and light; ours sat almost all
        # below 250 Hz. Bass and kick down, pluck and a bell sparkle up, hats instead of a dull shaker.
        note(s, beat * 1.8, hz(root + chord[0] - 24), .1, 0, 2.2, (1, .5, .2))               # bass on 1
        note(s + 2 * beat, beat * 1.8, hz(root + chord[0] - 24), .08, 0, 2.2, (1, .5, .2))  # and 3
        for k, idx in enumerate(pattern):                                                    # pluck arpeggio in eighths
            note(s + k * beat / 2, beat * .9, hz(root + chord[idx] + 12), .07 * bright + .04, (-.4, .4)[k % 2], 6.0, (1, .5, .3, .15))
        note(s, bar * .5, hz(root + chord[2] + 24), .03 + .02 * bright, (.3, -.3)[i % 2], 4.0, (1, 0, .3))  # bell sparkle on the bar
        for k in range(4):                                                                   # kick on beats, shaker on offbeats
            a = int((s + k * beat) * RATE);b = min(n, a + int(.18 * RATE))
            if a < n:
                kt = t[:b - a];kick = np.sin(2 * np.pi * (50 + 90 * np.exp(-kt * 30)) * kt) * np.exp(-kt * 14) * .11
                left[a:b] += kick;right[a:b] += kick
            a = int((s + k * beat + beat / 2) * RATE);b = min(n, a + int(.05 * RATE))
            if a < n:
                raw = np.random.default_rng(r + i * 4 + k).standard_normal(b - a + 1);hat = np.diff(np.diff(raw, prepend=0))  # crude high-pass: a hat, not a thud
                noise = hat[:b - a] * np.exp(-t[:b - a] * 110) * .03 * (.5 + bright)
                left[a:b] += noise * .8;right[a:b] += noise
    end = int(duration * RATE);fade = int(1.2 * RATE)
    stereo = np.stack([left[:end], right[:end]], 1);stereo[:int(.3 * RATE)] *= np.linspace(0, 1, int(.3 * RATE))[:, None]
    stereo[-fade:] *= np.linspace(1, 0, fade)[:, None]
    stereo /= max(1e-9, np.abs(stereo).max()) / .7
    pcm = (stereo * 32767).astype('<i2')
    out = Path(out);out.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out), 'wb') as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(RATE);w.writeframes(pcm.tobytes())
    return {'file': out.name, 'bpm': bpm, 'root_midi': root, 'mode': mode, 'look': look, 'seed': seed, 'duration': round(duration, 3),
            'method': 'original local synthesis (motif_music.bed); no samples, no external music'}


if __name__ == '__main__':
    import argparse
    a = argparse.ArgumentParser(description=__doc__.split('\n')[0]);a.add_argument('out');a.add_argument('--seconds', type=float, default=20)
    a.add_argument('--look', default='paper-craft');a.add_argument('--seed', type=int, default=0)
    args = a.parse_args();print(json.dumps(bed(args.out, args.seconds, args.look, args.seed)))
