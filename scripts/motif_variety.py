"""Cross-film similarity check: fails when two reels look too alike.

    python scripts/motif_variety.py PROJECT [PROJECT ...] [--json out.json]

Mayowa (2026-10-09) found the first five benchmark reels "pretty similar".
Per-scene palette rotation could not catch that, because the sameness was
across films. This check compares every pair of reels on what a viewer sees:

  look        headline, captions, camera, transition, hook and CTA treatment
              (share of the six that match)
  palettes    Jaccard overlap of the palettes used
  rooms       Jaccard overlap of the rooms used
  machines    Jaccard overlap of the rigs used
  colour      histogram intersection of hue/value over sampled frames
              (review/rough snapshots), when both projects have them

score = .35 look + .15 palettes + .15 rooms + .20 machines + .15 colour
(weights renormalised when colour is missing). A pair over MAX_SIMILARITY
fails, and so does any pair sharing more than MAX_SHARED_RIGS machines.
Calibration: the first five benchmark reels (one shared look, ten machines)
score 0.70 to 0.82 per pair and all fail.
"""
import argparse
import itertools
import json
from pathlib import Path

WEIGHTS = {'look': .35, 'palettes': .15, 'rooms': .15, 'machines': .20, 'colour': .15}
MAX_SIMILARITY = .5
MAX_SHARED_RIGS = 2
LOOK_FEATURES = ('headline', 'captions', 'camera', 'transition', 'hook', 'cta')
LEGACY_LOOK = {'headline': 'tag', 'captions': 'tiles', 'camera': 'push', 'transition': 'cut', 'hook': 'crowd', 'cta': 'crowd'}


def jaccard(a, b):
    a, b = set(a), set(b);return len(a & b) / len(a | b) if a | b else 0.0


def histogram(pngs, bins=(12, 3)):
    """Normalised hue x value histogram (saturated pixels only; greys go in one extra bin)."""
    from PIL import Image
    import colorsys
    counts = [0] * (bins[0] * bins[1] + 1);total = 0
    for png in pngs:
        im = Image.open(png).convert('RGB').resize((90, 160))
        for r, g, b in im.getdata():
            h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255);total += 1
            if s < .18:counts[-1] += 1;continue
            counts[min(bins[0] - 1, int(h * bins[0])) * bins[1] + min(bins[1] - 1, int(v * bins[1]))] += 1
    return [c / total for c in counts] if total else None


def fingerprint(project):
    """What a viewer sees of one reel, from its production plan and rough snapshots."""
    project = Path(project)
    plan = json.loads((project / 'production-plan.json').read_text())
    from motif_looks import LOOKS
    look = LOOKS.get(plan.get('look')) if plan.get('look') else LEGACY_LOOK
    shots = [s for b in plan['beats'] for s in b['shots']]
    pngs = sorted((project / 'review/rough').glob('*.png')) if (project / 'review/rough').is_dir() else []
    return {'slug': plan['slug'], 'look': plan.get('look', 'legacy'), 'features': {k: look[k] for k in LOOK_FEATURES},
            'palettes': sorted({b['palette'] for b in plan['beats']}), 'rooms': sorted({s['room'] for s in shots}),
            'machines': sorted({s['rig']['id'] for s in shots if s.get('rig')}), 'colour': histogram(pngs) if pngs else None}


def similarity(a, b):
    parts = {'look': sum(a['features'][k] == b['features'][k] for k in LOOK_FEATURES) / len(LOOK_FEATURES),
             'palettes': jaccard(a['palettes'], b['palettes']), 'rooms': jaccard(a['rooms'], b['rooms']), 'machines': jaccard(a['machines'], b['machines'])}
    if a['colour'] and b['colour']:parts['colour'] = sum(min(x, y) for x, y in zip(a['colour'], b['colour']))
    weight = sum(WEIGHTS[k] for k in parts)
    return round(sum(WEIGHTS[k] * v for k, v in parts.items()) / weight, 3), {k: round(v, 3) for k, v in parts.items()}


def check(prints):
    pairs, failures = [], []
    for a, b in itertools.combinations(prints, 2):
        score, parts = similarity(a, b);shared = sorted(set(a['machines']) & set(b['machines']))
        pairs.append({'a': a['slug'], 'b': b['slug'], 'score': score, 'parts': parts, 'shared_machines': shared})
        if score > MAX_SIMILARITY:failures.append(f'{a["slug"]} and {b["slug"]} look too alike ({score} > {MAX_SIMILARITY}: {parts})')
        if len(shared) > MAX_SHARED_RIGS:failures.append(f'{a["slug"]} and {b["slug"]} share {len(shared)} machines ({", ".join(shared)}; limit {MAX_SHARED_RIGS})')
    return {'status': 'FAIL' if failures else 'PASS', 'max_similarity': MAX_SIMILARITY, 'failures': failures, 'pairs': pairs,
            'films': [{k: v for k, v in p.items() if k != 'colour'} for p in prints]}


def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n')[0]);p.add_argument('projects', type=Path, nargs='+');p.add_argument('--json', type=Path)
    a = p.parse_args();result = check([fingerprint(x) for x in a.projects])
    text = json.dumps(result, indent=2)
    if a.json:a.json.write_text(text + '\n')
    print(text);raise SystemExit(0 if result['status'] == 'PASS' else 1)


if __name__ == '__main__':
    main()
