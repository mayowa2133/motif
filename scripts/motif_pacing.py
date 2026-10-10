"""Reel pacing check, measured from built compositions (not from plan claims).

Rules for the 20 to 32 s paper reel format (see ENERGY_CONTRACT.md, "Reel
pacing"):

  cuts          7 to 15 hard cuts across the film (scaled for other lengths)
  static hold   no run of identical frames longer than 1.2 s
  concurrency   every shot has at least one frame where 2+ pieces move at once
  headline      the headline text changes at least every 3 s of running time

A piece is a depth-0 element of the frame's world markup; it "moves" when its
markup differs from the previous frame. Frames are compared exactly, so the
check is deterministic. Plan-level rules for new reels live in check_plan().
"""
import argparse
import json
import re
from pathlib import Path

from motif_finish import SCRIPT, top_level

FPS = 30
CUTS_PER_SECOND = (7 / 26, 15 / 26)  # 7 to 15 cuts per ~26 s reel
MAX_HOLD = 1.2
MIN_MOVERS = 2
HEADLINE_EVERY = 3.0
TEXT = re.compile(r'<text[^>]*>([^<]+)</text>')


def shots(project):
    index = (Path(project) / 'index.html').read_text();out = []
    for m in re.finditer(r'data-composition-id="([^"]+)" data-composition-src="(compositions/[^"]+)" data-start="([\d.]+)" data-duration="([\d.]+)"', index):
        if m.group(1) != 'captions':out.append({'id': m.group(1), 'file': m.group(2), 'start': float(m.group(3)), 'duration': float(m.group(4))})
    return sorted(out, key=lambda s: s['start'])


def frames(path):
    spec = json.loads(SCRIPT.search(Path(path).read_text()).group(2))
    return [spec['initial'][0]['props']['innerHTML']] + [e['params']['props']['innerHTML'] for e in spec['events']]


def headline(markup):
    """Headline = the largest heavy (font-weight 800+) text in the frame."""
    best = None
    for m in re.finditer(r'<text([^>]*)>([^<]+)</text>', markup):
        attrs = m.group(1);weight = re.search(r'font-weight="(\d+)"', attrs);size = re.search(r'font-size="([\d.]+)"', attrs)
        if not weight or int(weight.group(1)) < 800 or not size:continue
        if best is None or float(size.group(1)) > best[0]:best = (float(size.group(1)), m.group(2).strip())
    return best[1] if best else None


def measure(project):
    film = shots(project);report = {'shots': [], 'cuts': max(0, len(film) - 1)}
    longest_hold, hold_at = 0.0, None;headlines = []
    for shot in film:
        states = frames(Path(project) / shot['file']);run = 1;best_movers = 0
        for i in range(1, len(states)):
            if states[i] == states[i - 1]:
                run += 1
                if run / FPS > longest_hold:longest_hold, hold_at = run / FPS, f'{shot["id"]}@{i}'
            else:
                run = 1
                a = [states[i - 1][s:e] for s, e, *_ in top_level(states[i - 1])];b = [states[i][s:e] for s, e, *_ in top_level(states[i])]
                movers = sum(1 for x, y in zip(a, b) if x != y) + abs(len(a) - len(b))
                best_movers = max(best_movers, movers)
        for i, state in enumerate(states):
            text = headline(state)
            if text and (not headlines or headlines[-1][1] != text):headlines.append((shot['start'] + i / FPS, text))
        report['shots'].append({'id': shot['id'], 'duration': shot['duration'], 'max_concurrent_movers': best_movers})
    duration = film[-1]['start'] + film[-1]['duration'] if film else 0
    gaps = [b[0] - a[0] for a, b in zip(headlines, headlines[1:])] + ([duration - headlines[-1][0]] if headlines else [])
    report.update({'duration': round(duration, 3), 'longest_static_hold': round(longest_hold, 3), 'longest_hold_at': hold_at,
                   'headline_changes': len(headlines), 'longest_headline_hold': round(max(gaps), 3) if gaps else None})
    return report


def check(project):
    r = measure(project);failures = []
    low, high = round(CUTS_PER_SECOND[0] * r['duration']), round(CUTS_PER_SECOND[1] * r['duration'])
    if not low <= r['cuts'] <= high:failures.append(f'cuts {r["cuts"]} outside {low}-{high} for {r["duration"]} s')
    if r['longest_static_hold'] > MAX_HOLD:failures.append(f'static hold {r["longest_static_hold"]} s at {r["longest_hold_at"]} exceeds {MAX_HOLD} s')
    for s in r['shots']:
        if s['max_concurrent_movers'] < MIN_MOVERS:failures.append(f'{s["id"]}: never more than {s["max_concurrent_movers"]} moving piece(s)')
    if r['longest_headline_hold'] is not None and r['longest_headline_hold'] > HEADLINE_EVERY + 1e-6:
        failures.append(f'headline held {r["longest_headline_hold"]} s (limit {HEADLINE_EVERY} s)')
    return {'status': 'FAIL' if failures else 'PASS', 'failures': failures, 'measured': r}


def check_plan(beats, duration, runtime=(20, 32)):
    """Plan-level reel rules, before anything is built.

    beats: [{id, start, end, headline, metaphor, cut_before}] in seconds."""
    failures = []
    for a, b in zip(beats, beats[1:]):
        if a.get('metaphor') != b.get('metaphor') and not b.get('cut_before', False):failures.append(f'{b["id"]}: metaphor changes without a cut')
    changes = [beats[0]['start']] + [b['start'] for a, b in zip(beats, beats[1:]) if a['headline'] != b['headline']] + [duration]
    for x, y in zip(changes, changes[1:]):
        if y - x > HEADLINE_EVERY + 1e-6:failures.append(f'headline held {y - x:.2f} s from {x:.2f} s')
    if not runtime[0] <= duration <= runtime[1]:failures.append(f'runtime {duration:.2f} s outside {runtime[0]:g}-{runtime[1]:g} s')
    return failures


def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n')[0]);p.add_argument('project', type=Path)
    result = check(p.parse_args().project);print(json.dumps(result, indent=2));raise SystemExit(0 if result['status'] == 'PASS' else 1)


if __name__ == '__main__':
    main()
