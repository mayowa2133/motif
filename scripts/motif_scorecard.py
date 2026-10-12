"""Score a Motif run against the reference reels, line by line, the way a reviewer grades a cut.

    python scripts/motif_scorecard.py RUNS/<slug> [--video path.mp4] [--json]

Each line scores 10 when it sits inside the range measured on the approved references
(Claudex cut 3 grade, 2026-10-11) and falls linearly to 0 at twice its distance from the
range. Story and script cannot be measured here; they stay with the human review and the
lessons gate. The overall score is the mean of the measured lines.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# Measured on references 01 and 05-10 (ffmpeg scdet 12, tblend difference at 270x480 30 fps,
# ebur128) and by eye on reference 09's 12 evenly spaced frames.
REFERENCE = {
    'scene_gap': (1.8, 3.7),        # seconds between scene changes
    'motion': (4.5, 8.2),           # mean frame-to-frame difference
    'loudness': (-15.0, -13.0),     # integrated LUFS
    'product_share': (.5, 1.0),     # claim beats showing the product big (close app-screen)
    'shot_variety': (1.0, 1.0),     # consecutive beats with a different composition
    'host_height': (.14, .3),       # host height as a share of frame height
    'screen_detail': (10, 24),      # UI pieces per product screen (reference 09 by eye: a prompt box ~10, an editor ~20)
}
HOST_UNITS = 670  # host height in frame pixels per unit of scale (BOT_SCALE .42 reads at 22% of 1280)


def score(value, lo, hi):
    if value is None:return None
    if lo <= value <= hi:return 10.0
    span = max(hi - lo, abs(lo) * .25, 1e-6);d = (lo - value) if value < lo else (value - hi)
    return round(max(0.0, 10 * (1 - d / span)), 1)


def _ffmpeg(args):
    return subprocess.run(['ffmpeg', '-nostdin', '-hide_banner', *args], capture_output=True, text=True).stderr


def video_metrics(video):
    """Scene gap, motion and loudness of a rendered reel."""
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(video)], capture_output=True, text=True).stdout.strip())
    cuts = _ffmpeg(['-i', str(video), '-vf', 'scale=270:480,scdet=threshold=12', '-an', '-f', 'null', '-']).count('lavfi.scd.time')
    out = subprocess.run(['ffmpeg', '-nostdin', '-i', str(video), '-vf', 'fps=30,scale=270:480,format=gray,tblend=all_mode=difference,signalstats,metadata=print:key=lavfi.signalstats.YAVG:file=-',
                          '-an', '-f', 'null', '-'], capture_output=True, text=True).stdout
    vals = [float(m) for m in re.findall(r'YAVG=([\d.]+)', out)]
    lufs = re.findall(r'I:\s+(-?[\d.]+) LUFS', _ffmpeg(['-i', str(video), '-af', 'ebur128', '-vn', '-f', 'null', '-']))
    return {'scene_gap': round(dur / (cuts + 1), 2), 'motion': round(sum(vals) / max(1, len(vals)), 2), 'loudness': float(lufs[-1]) if lufs else None}


def plan_metrics(run):
    """Product share, shot variety and host size from the run's plan and set layouts."""
    from motif_reel import composition, framing_of, CLOSE_HOST
    plan = json.loads((run / 'production-plan.json').read_text())
    layouts = json.loads((run / 'set-layouts.json').read_text()) if (run / 'set-layouts.json').exists() else {}
    claims = [b for b in plan['beats'] if b.get('kind') == 'claim']
    def main(b):return next((s for s in b['shots'] if s.get('rig')), None)
    product = sum(1 for b in claims if main(b) and main(b)['rig']['id'] == 'app-screen' and framing_of(main(b)) == 'close')
    keys = [composition(main(b)) if main(b) else None for b in plan['beats']]
    pairs = [(a, b) for a, b in zip(keys, keys[1:]) if a and b]
    heights = []
    for b in claims:
        for s in b['shots']:
            if not s.get('rig'):continue
            lay = layouts.get(b['id']) if isinstance(layouts, dict) else None
            scale = CLOSE_HOST if framing_of(s) == 'close' else ((lay or {}).get('bot') or {}).get('scale')
            if scale:heights.append(scale * HOST_UNITS / 1280)
    from motif_rigs import get as get_rig
    details = []
    for b in plan['beats']:
        s = main(b)
        if s and s['rig']['id'] == 'app-screen':
            rig = get_rig('app-screen');details.append(rig.detail(rig.params(s['rig'].get('params'))))
    return {'product_share': round(product / max(1, len(claims)), 2),
            'screen_detail': round(sum(details) / len(details), 1) if details else None,
            'shot_variety': round(sum(1 for a, b in pairs if a != b) / max(1, len(pairs)), 2),
            'host_height': round(sum(heights) / len(heights), 3) if heights else None}


def scorecard(run, video=None):
    run = Path(run)
    if video is None:
        found = sorted((run.parent / f'{run.name}-finished' / 'renders').glob('*.mp4'))
        video = found[0] if found else None
    values = {**plan_metrics(run), **(video_metrics(video) if video else {})}
    lines = {k: {'value': values.get(k), 'reference': list(REFERENCE[k]), 'score': score(values.get(k), *REFERENCE[k])} for k in REFERENCE}
    scored = [l['score'] for l in lines.values() if l['score'] is not None]
    return {'run': str(run), 'video': str(video) if video else None, 'lines': lines,
            'overall': round(sum(scored) / len(scored), 1) if scored else None,
            'not_measured': ['story', 'script and facts', 'finish by eye', 'host acting']}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('run');ap.add_argument('--video');ap.add_argument('--json', action='store_true')
    a = ap.parse_args(argv)
    card = scorecard(a.run, a.video)
    if a.json:print(json.dumps(card, indent=2));return
    for name, l in card['lines'].items():
        print(f"{name:14} {str(l['value']):>8}  ref {l['reference'][0]}-{l['reference'][1]}  score {l['score']}")
    print(f"overall {card['overall']} / 10 (measured lines only; also judge {', '.join(card['not_measured'])})")


if __name__ == '__main__':
    main()
