"""Render every benchmark brief and build one contact sheet for scoring.

    python scripts/motif_benchmark.py --out DIR [--allow-draft] [--tts-python PY] [--only slug,...]

Each brief runs through motif_reel.run (no per-film code) with a review render.
The sheet shows four moments per reel. Scores go in quality/scorecard.md.
Each film gets a look not used by the films before it (unless its brief names
one), and the batch must pass the cross-film similarity check (motif_variety).
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRIEFS = ROOT / 'quality/benchmark-briefs'


def main():
    from motif_frame_snapshot import at_times, sheet, snapshot
    from motif_reel import run
    p = argparse.ArgumentParser(description=__doc__.split('\n')[0]);p.add_argument('--out', type=Path, required=True)
    p.add_argument('--allow-draft', action='store_true');p.add_argument('--tts-python', type=Path);p.add_argument('--only');p.add_argument('--no-render', action='store_true')
    a = p.parse_args();only = set(a.only.split(',')) if a.only else None;rows, summary, looks, projects = [], [], [], []
    for brief in sorted(BRIEFS.glob('*.json')):
        slug = json.loads(brief.read_text())['slug']
        if only and slug not in only:continue
        record = run(brief, a.out, a.allow_draft, False, not a.no_render, a.tts_python, avoid_looks=tuple(looks))
        looks.append(next(s['look'] for s in record['stages'] if s['stage'] == 'plan'));projects.append(a.out / slug)
        final = a.out / f'{slug}-finished';duration = next(s['duration'] for s in record['stages'] if s['stage'] == 'compile')
        stills = snapshot(final, at_times(final, [duration * k for k in (.04, .3, .6, .93)]), a.out / 'sheet' / slug, size=(360, 640))
        rows.append((slug, stills));summary.append({'slug': slug, 'stages': {s['stage']: s['status'] for s in record['stages']}})
    sheet(rows, a.out / 'benchmark-sheet.png', width=240)
    if len(projects) > 1:
        from motif_variety import check, fingerprint
        variety = check([fingerprint(x) for x in projects]);(a.out / 'variety.json').write_text(json.dumps(variety, indent=2) + '\n')
        summary.append({'variety': variety['status'], 'failures': variety['failures'], 'max_pair': max(x['score'] for x in variety['pairs'])})
    (a.out / 'benchmark-summary.json').write_text(json.dumps(summary, indent=2) + '\n');print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
