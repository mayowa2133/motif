"""Build a review pack for an independent jury: someone who did not make the film grades it.

    python scripts/motif_jury.py pack RUNS/<slug> [--video path.mp4] [--out DIR]
    python scripts/motif_jury.py pack path/to/film.mp4 --out DIR

The pack holds what a reviewer needs to look at a film properly instead of watching it once:
a contact sheet (a frame every 0.5 s), filmstrips around the fastest moves and each payoff,
full-resolution stills at key times, the spec numbers, and jury-prompt.md, the brief a fresh
agent session grades from (scores with fixed anchors, then 5 to 10 fixes with timecodes).
See docs/JURY.md. Adapted from the review rubric of the MIT mg-styles-15 repo (2026-10-26).
"""
import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

SHEET_STEP = .5          # seconds between contact-sheet frames
SHEET_COLS = 8
STRIP_FRAMES = 8         # frames per filmstrip, every STRIP_STEP frames at 30 fps
STRIP_STEP = 2
HERO_WINDOW = (.6, .75)  # where the strongest payoff usually lands in a well-built short
DIMENSIONS = {
    'story_concept': 'one object changing; a hook in the first 0.5 s; an unmistakable payoff; the end keeps the hook\'s promise',
    'motion_craft': 'anticipation, overlap, follow-through, arcs; the host acts on the object; no dead or jittery motion',
    'design_type': 'composition and hierarchy on a phone; headline and label setting; palette; nothing cramped or covered',
    'finish': 'paper texture, edges, shadows, grain; no banding, aliasing, clipped words or half-drawn pieces',
    'sound_sync': 'voice clarity, music bed, effects landing on contacts and cuts, mix near -14 LUFS',
    'technical': 'spec, no black or frozen spans, no popping, text inside the phone-safe area',
}


def _run(args):
    return subprocess.run(args, capture_output=True, text=True)


def probe(video):
    out = _run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height,r_frame_rate:format=duration',
                '-of', 'json', str(video)]).stdout
    d = json.loads(out);s = d['streams'][0];num, den = s['r_frame_rate'].split('/')
    return {'duration': round(float(d['format']['duration']), 3), 'width': s['width'], 'height': s['height'], 'fps': round(float(num) / float(den), 3)}


def frame_diffs(video):
    """Mean frame-to-frame difference at 30 fps (the scorecard's motion measure), one value per frame."""
    out = _run(['ffmpeg', '-nostdin', '-i', str(video), '-vf', 'fps=30,scale=270:480,format=gray,tblend=all_mode=difference,signalstats,'
                'metadata=print:key=lavfi.signalstats.YAVG:file=-', '-an', '-f', 'null', '-']).stdout
    return [float(m) for m in re.findall(r'YAVG=([\d.]+)', out)]


def cut_times(video):
    err = _run(['ffmpeg', '-nostdin', '-hide_banner', '-i', str(video), '-vf', 'scale=270:480,scdet=threshold=12', '-an', '-f', 'null', '-']).stderr
    return [float(t) for t in re.findall(r'lavfi\.scd\.time: ?([\d.]+)', err)]


def audio_spec(video):
    err = _run(['ffmpeg', '-nostdin', '-hide_banner', '-i', str(video), '-af', 'ebur128=peak=true', '-vn', '-f', 'null', '-']).stderr
    lufs = re.findall(r'I:\s+(-?[\d.]+) LUFS', err);peak = re.findall(r'Peak:\s+(-?[\d.]+|-inf) dBFS', err)
    return {'loudness_lufs': float(lufs[-1]) if lufs else None, 'true_peak_dbtp': float(peak[-1]) if peak and peak[-1] != '-inf' else None}


def black_spans(video):
    err = _run(['ffmpeg', '-nostdin', '-hide_banner', '-i', str(video), '-vf', 'blackdetect=d=0.1:pix_th=0.10', '-an', '-f', 'null', '-']).stderr
    return [[float(a), float(b)] for a, b in re.findall(r'black_start:([\d.]+) black_end:([\d.]+)', err)]


def longest_static(diffs, still=.3, fps=30):
    """Longest run of nearly identical frames, in seconds, and where it starts."""
    best, run, at = 0, 0, None
    for i, v in enumerate(diffs):
        run = run + 1 if v < still else 0
        if run > best:best, at = run, (i - run + 1) / fps
    return round(best / fps, 2), (round(at, 2) if at is not None else None)


def fastest_moves(diffs, cuts, n=2, fps=30, gap=1.0):
    """Times of the n biggest in-shot moves; cuts and their neighbours are not moves."""
    near_cut = lambda t: any(abs(t - c) < 3 / fps for c in cuts)
    picks = []
    for i in sorted(range(len(diffs)), key=lambda i: -diffs[i]):
        t = (i + 1) / fps
        if near_cut(t) or any(abs(t - p) < gap for p in picks):continue
        picks.append(round(t, 2))
        if len(picks) == n:break
    return sorted(picks)


def run_context(run):
    """Payoff times, beat starts and the story promise from a compiled run, when there is one."""
    ctx = {'payoffs': [], 'shots': [], 'promise': None, 'ending': None, 'title': run.name if run else None}
    if not run:return ctx
    audio = run / 'audio-plan.json'
    if audio.exists():
        cues = json.loads(audio.read_text()).get('sfx_cues', [])
        ctx['payoffs'] = sorted({round(c['start'], 2) for c in cues if c.get('meaning') == 'payoff accent'})
    plan = run / 'production-plan.json'
    if plan.exists():
        p = json.loads(plan.read_text())
        ctx['title'] = p.get('title') or ctx['title']
        story = p.get('story') or {};hook = next((b for b in p.get('beats', []) if b.get('kind') == 'hook'), {})
        ctx['ending'] = story.get('ending');ctx['promise'] = (hook.get('story') or {}).get('promise')
        ctx['beats'] = [{'id': b.get('id'), 'kind': b.get('kind'), 'narration': b.get('narration'), 'headline': b.get('headline')} for b in p.get('beats', [])]
    return ctx


def hero_placement(payoffs, duration):
    """Each payoff as a share of the runtime, and whether any lands in the hero window."""
    shares = [round(t / duration, 2) for t in payoffs if duration]
    return {'payoff_shares': shares, 'window': list(HERO_WINDOW), 'in_window': any(HERO_WINDOW[0] <= s <= HERO_WINDOW[1] for s in shares)}


def _grab(video, times, out_dir, width=None):
    paths = []
    for i, t in enumerate(times):
        p = out_dir / f'{i:03d}.png'
        vf = ['-vf', f'scale={width}:-2'] if width else []
        _run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-ss', f'{t:.3f}', '-i', str(video), '-frames:v', '1', *vf, str(p)])
        paths.append(p if p.exists() else None)
    return paths


def _sheet(frames, times, cols, path, title=None):
    from PIL import Image, ImageDraw
    tiles = [Image.open(f).convert('RGB') for f in frames if f]
    if not tiles:return None
    w, h = tiles[0].size;label = 22;head = 36 if title else 0;rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * w, head + rows * (h + label)), 'white');draw = ImageDraw.Draw(sheet)
    if title:draw.text((8, 10), title, fill='black')
    for i, (tile, t) in enumerate(zip(tiles, [t for f, t in zip(frames, times) if f])):
        x, y = (i % cols) * w, head + (i // cols) * (h + label)
        sheet.paste(tile, (x, y + label));draw.text((x + 6, y + 4), f'{int(t // 60)}:{t % 60:05.2f}', fill='black')
    sheet.save(path);return path


def pack(target, video=None, out=None):
    target = Path(target)
    run = target if target.is_dir() else None
    if video is None:
        if run is None:video = target
        else:
            found = sorted((run.parent / f'{run.name}-finished' / 'renders').glob('*.mp4'))
            if not found:raise SystemExit(f'no render for {run}; pass --video')
            video = found[0]
    video = Path(video);out = Path(out) if out else ((run / 'review' / 'jury') if run else video.with_suffix('') .parent / f'{video.stem}-jury')
    out.mkdir(parents=True, exist_ok=True)
    meta = probe(video);dur = meta['duration'];diffs = frame_diffs(video);cuts = cut_times(video);ctx = run_context(run)
    static_s, static_at = longest_static(diffs)
    spec = {**meta, **audio_spec(video), 'black_spans': black_spans(video), 'longest_static_s': static_s, 'longest_static_at': static_at,
            'cuts': len(cuts), 'mean_scene_s': round(dur / (len(cuts) + 1), 2), 'motion': round(sum(diffs) / max(1, len(diffs)), 2)}
    moves = fastest_moves(diffs, cuts)
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        times = [round(i * SHEET_STEP, 2) for i in range(int(dur / SHEET_STEP) + 1) if i * SHEET_STEP < dur - .02]
        (tmp / 'sheet').mkdir();_sheet(_grab(video, times, tmp / 'sheet', 216), times, SHEET_COLS, out / 'contact-sheet.png', f'every {SHEET_STEP} s')
        strips = []
        for kind, centres in (('move', moves), ('payoff', ctx['payoffs'])):
            for c in centres:
                ts = [round(max(0, min(dur - .04, c + (k - STRIP_FRAMES // 2) * STRIP_STEP / 30)), 3) for k in range(STRIP_FRAMES)]
                d = tmp / f'{kind}-{c}';d.mkdir()
                name = f'strip-{kind}-{c:05.2f}s.png'
                if _sheet(_grab(video, ts, d, 270), ts, STRIP_FRAMES, out / name, f'{kind} at {c:.2f} s, every {STRIP_STEP} frames'):strips.append(name)
    keys = sorted({round(min(dur - .25, t), 2) for t in [.05, *ctx['payoffs'], *[dur * k / 6 for k in range(1, 6)], dur - .25]})
    stills = []
    for t, p in zip(keys, _grab(video, keys, out)):
        if p:name = f'still-{t:05.2f}s.png';p.rename(out / name);stills.append(name)
    hero = hero_placement(ctx['payoffs'], dur)
    report = {'video': str(video), 'run': str(run) if run else None, 'spec': spec, 'fastest_moves': moves, 'hero': hero,
              'contact_sheet': 'contact-sheet.png', 'filmstrips': strips, 'stills': stills, 'dimensions': DIMENSIONS}
    (out / 'pack.json').write_text(json.dumps(report, indent=2))
    (out / 'jury-prompt.md').write_text(prompt(report, ctx))
    return report


def prompt(report, ctx):
    s = report['spec'];hero = report['hero']
    dims = '\n'.join(f'   - {k}: {v}' for k, v in DIMENSIONS.items())
    beats = '\n'.join(f"   - {b['kind']}: \"{b.get('headline') or ''}\" / {b.get('narration') or ''}" for b in ctx.get('beats', []))
    story = ''
    if ctx.get('promise') or ctx.get('ending'):story = f"The hook promises: {ctx.get('promise')}\nThe ending should show: {ctx.get('ending')}\n"
    hero_line = (f"Payoffs land at {', '.join(f'{x:.0%}' for x in hero['payoff_shares'])} of the runtime"
                 f" ({'one is' if hero['in_window'] else 'none is'} in the usual hero window, {HERO_WINDOW[0]:.0%} to {HERO_WINDOW[1]:.0%}).") if hero['payoff_shares'] else 'No payoff times known (bare video).'
    return f"""# Jury: {ctx.get('title') or Path(report['video']).stem}

You are a senior jury member for short-form explainer reels (think: the editor of a motion-design
showcase, and the lead of a top faceless explainer account). You did NOT make this film. Judge it
harshly and precisely; kindness is useless, specificity is everything. The bar is the reference
reels Motif is measured against: flat 2D paper-style explainers watched on a phone, 9:16.

Film: {report['video']}
{story}{('Beats (headline / narration):' + chr(10) + beats + chr(10)) if beats else ''}
## What is in this folder

- contact-sheet.png: a frame every {SHEET_STEP} s with timecodes.
- {', '.join(report['filmstrips']) or 'no filmstrips'}: {STRIP_FRAMES} frames, {STRIP_STEP} frames apart, around the fastest in-shot moves and each payoff.
- {len(report['stills'])} full-resolution stills: look at edges, type, labels, texture and clipping at 100 %.
- pack.json: the measured numbers below.

Spec: {s['width']}x{s['height']}, {s['fps']} fps, {s['duration']} s; {s['loudness_lufs']} LUFS (target -14 +-1), true peak
{s['true_peak_dbtp']} dBTP (ceiling -1); {s['cuts']} cuts, one every {s['mean_scene_s']} s (references 1.8 to 3.7);
motion {s['motion']} (references 4.5 to 8.2); longest frozen span {s['longest_static_s']} s at {s['longest_static_at']} s;
black spans {s['black_spans'] or 'none'}. {hero_line}

Watch the film itself too, with sound, once at full speed and once scrubbing, if you can play video.

## Score

Score 1 to 10 on each dimension (5 = competent student work; 6 = decent template level; 7 = solid
professional; 8 = the reference reels; 9 = the best explainer account you know; 10 = best in the
world). Most first cuts deserve 5 to 7. Do not inflate; a score above 7 names the frame that earns it.
{dims}

## Fixes

Give 5 to 10 fixes ordered by impact on a viewer scrolling on a phone. Each: timecode(s), what is
wrong (observable), why it matters, and a concrete how-to (numbers: frames, px, seconds, which
beat field or rig param to change). Prefer a few big upgrades over nitpicks; at least one fix must
raise the wow, not only polish. Motif films are briefs, not code: say the fix as a brief change
(headline, act, rig, params, hold, room, palette, story) or name the library piece that is missing.

Flag as critical: anything that reads as generic or AI-template, a claim the picture does not
demonstrate, a metaphor that repeats, text under the phone UI, and any spec failure.

## Return

Write `jury.json` next to this file:
{{"reviewer": "...", "scores": {{{', '.join(f'"{k}": 0' for k in DIMENSIONS)}}}, "overall": 0,
 "critical": ["..."], "fixes": [{{"at": "0:12.5", "what": "...", "why": "...", "how": "..."}}], "strengths": ["..."]}}
"""


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('pack', help='build the review pack and jury prompt');p.add_argument('target');p.add_argument('--video');p.add_argument('--out')
    a = ap.parse_args(argv)
    r = pack(a.target, a.video, a.out)
    s = r['spec']
    print(f"pack: {Path(r['video']).name} {s['duration']} s, {s['loudness_lufs']} LUFS, peak {s['true_peak_dbtp']} dBTP, "
          f"{len(r['filmstrips'])} filmstrips, {len(r['stills'])} stills")
    print(f"next: give jury-prompt.md and the pack folder to a fresh agent session that did not make the film")


if __name__ == '__main__':
    main()
