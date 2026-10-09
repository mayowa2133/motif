"""How much a rendered reel moves, measured from the pixels.

The 2026-10-09 review measured the PR #14 benchmark reels at about half the
reference reels' movement: median share of pixels changing between frames of
2 to 7%, against 7.5 to 15% for the references. measure() samples the video
at 15 fps in greyscale at 180 x 320 and reports, per sampled pair, the share
of pixels whose value changes by more than 12 levels. Hard cuts are excluded
(a cut changes everything and would inflate the number).

Gate: median moving share >= FLOOR and no static hold longer than 0.6 s.
This is a floor against a reel that settles and waits; it does not score
whether the movement is good, which only a person watching can judge.
"""
import argparse
import json
import subprocess

FLOOR = .06
STATIC_MAX = .6
W, H, RATE = 180, 320, 15


def measure(path, floor=FLOOR):
    import numpy as np
    raw = subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', str(path), '-vf', f'fps={RATE},scale={W}:{H},format=gray', '-f', 'rawvideo', '-'], capture_output=True, check=True).stdout
    frames = np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(np.int16)
    diff = np.abs(np.diff(frames, axis=0))
    moving = (diff > 12).mean(axis=(1, 2));mean = diff.mean(axis=(1, 2))
    cuts = moving > .6
    kept = moving[~cuts]
    run = best = 0
    for m in kept:
        run = run + 1 if m < .002 else 0;best = max(best, run)
    median = float(np.median(kept)) if len(kept) else 0.0
    longest = best / RATE
    status = 'PASS' if median >= floor and longest <= STATIC_MAX else 'FAIL'
    return {'file': str(path), 'status': status, 'median_moving_share': round(median, 4), 'mean_abs_change': round(float(np.median(mean[~cuts])), 3) if len(kept) else 0,
            'floor': floor, 'longest_static_s': round(longest, 2), 'static_max_s': STATIC_MAX, 'cuts_excluded': int(cuts.sum()), 'samples': int(len(moving))}


def main():
    a = argparse.ArgumentParser(description=__doc__.split('\n')[0]);a.add_argument('videos', nargs='+');a.add_argument('--floor', type=float, default=FLOOR)
    args = a.parse_args();out = [measure(v, args.floor) for v in args.videos];print(json.dumps(out, indent=2))
    raise SystemExit(0 if all(o['status'] == 'PASS' for o in out) else 1)


if __name__ == '__main__':
    main()
