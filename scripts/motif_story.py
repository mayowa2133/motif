#!/usr/bin/env python3
"""Story pass: check a brief's story plan, and build an animatic before the render.

A brief may carry a `story` block (premises, the changing object, the ending)
and a `story` per beat (purpose, but/therefore link, before -> after, action,
set-up / pay-off tokens). docs/STORY_PASS.md explains how to write them.

    python scripts/motif_story.py check BRIEF
    python scripts/motif_story.py animatic PROJECT      # after `motif_reel.py run --no-finish`

check() only judges briefs that opted in (status NOT_USED otherwise), so the
benchmark briefs keep passing. Its rules come from the story-craft review of
2026-10-12: every beat changes something the viewer can see, beats join with
"but" or "therefore" (never "and then"), the hook's promise is paid off on
screen, and every detail a beat sets up comes back later.
"""
import argparse
import json
import re
import statistics
import subprocess
from pathlib import Path

STOP = set('a an the and or but so to of in on at for with into onto from by is are was were be been it its this that these those your you they their them our we he she his her as than then just one all every each no not more most very can will'.split())


def words(text):
    return {w for w in re.findall(r"[a-z0-9%]+", (text or '').lower()) if w not in STOP and (len(w) > 2 or w.isdigit())}


def _strings(value):
    if isinstance(value, str):yield value
    elif isinstance(value, dict):
        for v in value.values():yield from _strings(v)
    elif isinstance(value, list):
        for v in value:yield from _strings(v)


def on_screen(beat):
    """Words the viewer can read in this beat: headlines, machine labels, screen lines."""
    seen = set()
    for text in [beat.get('headline'), beat.get('payoff_headline'), *_strings((beat.get('visual') or {}).get('params') or {})]:
        seen |= words(text)
    return seen


def sentences(brief):
    hook = brief.get('hook') or {};alts = hook.get('alternates') or []
    text = ' '.join([alts[hook.get('selected') or 0] if alts else ''] + [b['narration'] for b in brief['beats']] + [brief['cta']['narration']])
    return [s for s in re.split(r'(?<=[.!?])\s+', text.strip()) if s]


def check(brief):
    story = brief.get('story')
    if not story:return {'status': 'NOT_USED', 'failures': [], 'warnings': []}
    fail, warn = [], []
    beats = brief['beats'];hook = (brief.get('hook') or {}).get('story');cta = brief['cta'].get('story') or {}
    if story['chosen'] >= len(story['premises']):fail.append(f'story.chosen {story["chosen"]} has no premise')
    if len({p.strip().lower() for p in story['premises']}) < len(story['premises']):fail.append('story.premises repeat each other')
    missing = [b['id'] for b in beats if not b.get('story')]
    if missing:fail.append(f'beats without a story block: {", ".join(missing)}')
    if not hook:fail.append('hook.story is missing: say what the opening promises and what it sets up')
    if missing or not hook:return {'status': 'FAIL', 'failures': fail, 'warnings': warn}
    parts = [b['story'] for b in beats]
    # Every beat is a change the viewer can see.
    for b in beats:
        s = b['story']
        if words(s['before']) == words(s['after']):fail.append(f'{b["id"]}: before and after are the same, so nothing changes')
        if not words(s['after']) & on_screen(b):
            fail.append(f'{b["id"]}: the after state ("{s["after"]}") shares no word with what is on screen (headline, payoff headline, machine labels, screen lines)')
        if (b.get('visual') or {}).get('hold') and s['purpose'] in ('demonstrate', 'resolve'):
            warn.append(f'{b["id"]}: visual.hold keeps the machine still, but the beat is meant to {s["purpose"]}')
    # But / therefore: at least one complication, and not a list of "therefore".
    links = [p['link'] for p in parts[1:]]
    if links and 'but' not in links and not any(p['purpose'] == 'complicate' for p in parts):
        fail.append('no beat complicates anything (no "but" link, no complicate beat): the film is a list, not a story')
    if parts[-1]['purpose'] not in ('reveal', 'resolve'):fail.append(f'{beats[-1]["id"]}: the last beat should reveal or resolve, not {parts[-1]["purpose"]}')
    for k in range(len(parts) - 2):
        if parts[k]['purpose'] == parts[k + 1]['purpose'] == parts[k + 2]['purpose']:
            warn.append(f'{beats[k]["id"]}..{beats[k + 2]["id"]}: three {parts[k]["purpose"]} beats in a row')
    # Set-up / pay-off ledger.
    open_tokens = {t: 'hook' for t in hook.get('sets_up', [])}
    if not open_tokens:fail.append('hook.story.sets_up is empty: the opening must plant something the end pays off')
    hook_tokens = set(open_tokens);paid = set()
    for who, s in [(b['id'], b['story']) for b in beats] + [('cta', cta)]:
        for t in s.get('pays_off', []):
            if t not in open_tokens:fail.append(f'{who}: pays off "{t}", which nothing set up earlier')
            paid.add(t)
        for t in s.get('sets_up', []):open_tokens.setdefault(t, who)
    for t, who in open_tokens.items():
        if t not in paid:fail.append(f'{who}: sets up "{t}", which no later beat pays off')
    end = set(parts[-1].get('pays_off', [])) | set(cta.get('pays_off', []))
    if hook_tokens and not hook_tokens & end:fail.append('the last beat and CTA pay off nothing the hook promised')
    # Narration rhythm and the last line.
    lengths = [len(s.split()) for s in sentences(brief)]
    if len(lengths) >= 4 and (max(lengths) - min(lengths) < 5 or statistics.pstdev(lengths) < 2):
        warn.append(f'flat rhythm: sentence lengths {lengths}; mix short and long lines')
    if not any(s.get('line_job') == 'land' for s in parts + [cta]):warn.append('no line has line_job "land": write the line people would repeat')
    return {'status': 'FAIL' if fail else 'PASS', 'failures': fail, 'warnings': warn}


# Animatic -------------------------------------------------------------------------------

def animatic(project, out=None, width=360):
    """Two stills per shot (just after the cut, just before the next) timed to the real voice."""
    from motif_frame_render import FPS, clips, mix
    from motif_frame_snapshot import sheet, snapshot
    project = Path(project);out = Path(out) if out else project / 'review/animatic.mp4';out.parent.mkdir(parents=True, exist_ok=True)
    shots = [c for c in clips(project) if c['id'] != 'captions'];size = (width, round(width * 16 / 9))
    requests = []
    for c in shots:
        n = max(1, round(c['duration'] * FPS));requests += [(c['id'], min(n - 1, round(n * .15))), (c['id'], max(0, n - 6))]
    pngs = snapshot(project, requests, project / 'review/animatic', size)
    concat = project / 'review/animatic/concat.txt';lines = []
    for k, c in enumerate(shots):
        for j in range(2):lines += [f"file '{pngs[2 * k + j].resolve()}'", f'duration {c["duration"] / 2:.3f}']
    lines.append(f"file '{pngs[-1].resolve()}'");concat.write_text('\n'.join(lines) + '\n')
    silent = out.with_suffix('.silent.mp4');duration = shots[-1]['start'] + shots[-1]['duration']
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(concat), '-vf', f'fps={FPS},format=yuv420p', '-c:v', 'libx264', '-crf', '23', str(silent)], check=True)
    mix(project, silent, out, duration)
    brief = json.loads((project / 'brief.json').read_text()) if (project / 'brief.json').exists() else {}
    stories = {b['id']: b.get('story') or {} for b in brief.get('beats', [])}
    def label(shot_id):
        beat = next((b for b in stories if shot_id.startswith(b)), None);s = stories.get(beat) or {}
        return f'{shot_id}  {s.get("link", "")} {s.get("purpose", "")}: {s.get("after", "")}'.strip()
    sheet([(label(c['id']), pngs[2 * k:2 * k + 2]) for k, c in enumerate(shots)], project / 'review/storyboard.png', width=240)
    return {'animatic': str(out), 'storyboard': str(project / 'review/storyboard.png'), 'shots': len(shots), 'duration': round(duration, 2)}


def main():
    a = argparse.ArgumentParser(description=__doc__.split('\n')[0]);sub = a.add_subparsers(dest='cmd', required=True)
    c = sub.add_parser('check');c.add_argument('brief', type=Path)
    m = sub.add_parser('animatic');m.add_argument('project', type=Path);m.add_argument('--out', type=Path)
    args = a.parse_args()
    if args.cmd == 'check':
        report = check(json.loads(args.brief.read_text()));print(json.dumps(report, indent=2));raise SystemExit(1 if report['status'] == 'FAIL' else 0)
    print(json.dumps(animatic(args.project, args.out), indent=2))


if __name__ == '__main__':
    main()
