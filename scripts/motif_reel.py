"""One command from a reel brief to a finished, gated review render.

    python scripts/motif_reel.py run --brief briefs/x.json --local-draft [--allow-draft] [--render]

Stages (each writes its record into the project; nothing is per-film code):

   1 script      validate the brief, build 3 hook alternates, runtime estimate
   2 plan        library-constrained plan: every shot names a room, rig, insert,
                 Bot costume and headline from the catalogue; unknown IDs fail and
                 missing capabilities become library_request records
   3 structure   plan-level pacing only; production requires an existing fresh
                 independent structure review before voice/capture
   4 voice       one TTS take per line (hook, beats, CTA), measured durations
   5 compile     per-shot frame sequences from library data (motif_sets, rigs,
                 inserts, Bot kit), captions, SFX at rig contacts
   6 rough       pacing and empty-field checks on the native compositions
   7 critics     NOT_PERFORMED in explicit local drafts; normal film checks use
                 the existing production evidence gate, never inferred reviews
   8 finish      motif_finish pass with per-room lights
   9 gate        technical: provenance + pacing on the finished project
  10 review      optional review render; local drafts stop at DRAFT_REVIEW_REQUIRED

The deterministic reel planner does not yet author the normal film structure
contract. Normal runs block before voice/capture rather than bypassing that
review. --allow-draft only admits draft library entries; it does not skip gates.

The narration is the brief's text; timing comes from the measured clip
durations. Word timing inside a clip is proportional to characters, which is
an approximation and is recorded as such.
"""
import argparse
import hashlib
import json
import math
import re
import shutil
import subprocess
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FPS = 30
PIN = '0.8.99'
V6 = ROOT / 'videos/productions/voicestudio-craft-v6'
SHOT_MAX = 2.9          # headline must change at least every 3 s
SPEED = 1.2             # Kokoro af_nova reel pace (measured about 3.7 words/s)
TAIL = .7


def read(p):return json.loads(Path(p).read_text())


def write(p, v):
    Path(p).parent.mkdir(parents=True, exist_ok=True);Path(p).write_text(json.dumps(v, indent=2) + '\n')


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


# 2 Plan --------------------------------------------------------------------------------

EDGE_WORDS = {'A', 'AN', 'AND', 'THE', 'IS', 'ARE', 'OF', 'TO', 'IN', 'ON', 'FOR', 'YOUR', 'YOU', 'IT', 'ITS', 'THIS', 'THAT', 'WITH', 'JUST', 'EVEN', 'BUT', 'OR', 'SO', 'AT', 'BY', 'ABOUT', 'ONE', 'EVERY', 'ACROSS', 'INTO', 'FROM', 'HAS', 'HAVE', 'WILL', 'CAN', 'QUIETLY', 'MOST', 'ALREADY'}


def _short(text, limit=26):
    """Headline from a phrase: whole words only, never ending on a filler word."""
    words = re.sub(r'[^\w$%.,\' -]', '', text.replace('\u2212', '-')).upper().replace(', ', ' ').rstrip('.').split()
    while words and words[0] in EDGE_WORDS:words.pop(0)
    out = []
    for w in words:
        if len(' '.join(out + [w])) > limit:break
        out.append(w)
    while len(out) > 1 and out[-1] in EDGE_WORDS:out.pop()
    return ' '.join(out) or text[:limit].upper()


def _number(value):
    m = re.search(r'([+-]?)(\$)?([+-]?)([\d,]+(?:\.\d+)?)\s*([kKmM%x]|\+)?', (value or '').replace('\u2212', '-'))
    if not m:return None
    n = float(m.group(4).replace(',', ''))
    if '-' in (m.group(1), m.group(3)):n = -n
    return {'prefix': m.group(2) or '', 'value': int(n) if n == int(n) else n, 'suffix': m.group(5) or ''}


def _insert_for(fact, text, cat):
    from motif_library import retrieve
    num = _number(fact.get('value'))
    if num and isinstance(num['value'], int):
        unit = re.sub(r'[$\d,.%+\-\u2212]', '', fact.get('value', '')).strip()
        return {'kind': 'counter', 'args': {'start': 0, 'end': num['value'], 'prefix': num['prefix'], 'suffix': num['suffix'], 'label': _short(unit or fact['claim'], 16)}}
    from motif_library import words
    best = [e for e in retrieve(cat, text, 'insert', 3, exclude=('comment_end_card', 'counter')) if words(text) & set(e['tags'])]
    kind = best[0]['id'] if best else 'progress_bar'
    args = {'star_badge': {'rating': 5, 'filled': 5}, 'price_tag': {'amount': fact.get('value') or 'FREE'}, 'gauge': {'value': .85, 'label': _short(fact.get('value') or 'MAX', 10)},
            'progress_bar': {'fraction': 1.0, 'label': _short(fact.get('value') or 'DONE', 14)}}.get(kind, {})
    return {'kind': kind, 'args': args}


def plan_reel(brief, allow_draft=False, avoid_looks=()):
    """Deterministic library-constrained planner (the live-Codex planner, when
    present, must produce the same schema and pass the same validation)."""
    from motif_library import catalog, retrieve
    from motif_reel_script import hook_line
    import motif_looks
    cat = catalog(allow_draft);facts = {f['id']: f for f in brief['facts']};seed = brief.get('seed', 0)
    look_id = motif_looks.choose(brief, avoid_looks);look = motif_looks.get(look_id)
    palettes = motif_looks.palettes(look_id, len(brief['beats']) + 2, seed);used_rigs, rooms = [], []
    hook, _ = hook_line(brief)
    beats = []

    def room_for(text, hint=None):
        if hint:return hint
        ranked = retrieve(cat, text, 'room', 20, exclude=rooms[-1:])
        ranked = [r for r in ranked if r['id'] in look['rooms']] or ranked
        fresh = [r for r in ranked if r['id'] not in rooms]
        return (fresh or ranked)[0]['id'] if (fresh or ranked) else None

    first_fact = facts[brief['beats'][0]['fact']]
    hook_room = room_for(brief['topic'] + ' ' + hook, (brief.get('hook') or {}).get('room'));rooms.append(hook_room)
    hook_insert = _insert_for(first_fact, hook, cat) if _number(first_fact.get('value')) else None
    beats.append({'id': 'hook', 'kind': 'hook', 'narration': hook, 'palette': palettes[0], 'shots': [
        {'id': 'hook', 'role': 'hook', 'headline': (brief.get('hook') or {}).get('headline') or _short(hook, 28), 'headline_b': _short(brief['topic'], 28), 'room': hook_room, 'rig': None,
         'insert': hook_insert, 'bot': {'costume': [], 'face': 'excited', 'pose': 'celebrating'}, 'crowd': 9 if look['hook'] == 'crowd' else 0, 'grammar': 'big-bot' if look['hook'] == 'number' and not hook_insert else look['hook']}]})
    for i, b in enumerate(brief['beats']):
        fact = facts[b['fact']];visual = b.get('visual', {});text = f'{b["narration"]} {fact["claim"]} {fact.get("value", "")}'
        rig_id = visual.get('rig') or (retrieve(cat, text, 'rig', 1, exclude=used_rigs) or retrieve(cat, text, 'rig', 1))[0]['id']
        used_rigs.append(rig_id)
        room = room_for(text, visual.get('room'));rooms.append(room)
        room_costumes = next((e.get('costumes', []) for e in cat if e['kind'] == 'room' and e['id'] == room), [])
        costume = visual.get('costume') or ([room_costumes[i % len(room_costumes)]] if room_costumes else [])
        insert = visual.get('insert') or _insert_for(fact, text, cat)
        setup = b.get('headline') or _short(fact['claim'], 26);payoff = b.get('payoff_headline') or _short(fact.get('value') or b['narration'], 26)
        if payoff == setup:payoff = _short(b['narration'], 26)
        beats.append({'id': b['id'], 'kind': 'claim', 'narration': b['narration'], 'fact': b['fact'], 'palette': visual.get('palette') or palettes[i + 1], 'shots': [
            {'id': f'{b["id"]}-a', 'role': 'setup', 'headline': setup, 'headline_b': _short(b['narration'], 26), 'room': room, 'rig': {'id': rig_id, 'params': visual.get('params', {})}, 'insert': None,
             'bot': {'costume': costume, 'face': 'determined', 'pose': 'walking'}},
            {'id': f'{b["id"]}-b', 'role': 'payoff', 'headline': payoff, 'headline_b': _short(fact['claim'], 26), 'room': room, 'rig': {'id': rig_id, 'params': visual.get('params', {})}, 'insert': insert,
             'bot': {'costume': costume, 'face': 'surprised', 'pose': 'pointing'}}]})
    cta_room = room_for('celebrate launch ' + brief['cta']['narration'], brief['cta'].get('room'))
    beats.append({'id': 'cta', 'kind': 'cta', 'narration': brief['cta']['narration'], 'palette': palettes[-1], 'shots': [
        {'id': 'cta', 'role': 'cta', 'headline': _short(f'COMMENT {brief["cta"]["keyword"]}', 28), 'headline_b': _short(brief['cta']['narration'], 28), 'room': cta_room, 'rig': None,
         'insert': {'kind': 'comment_end_card', 'args': {'keyword': brief['cta']['keyword']}}, 'bot': {'costume': ['party-hat'], 'face': 'excited', 'pose': 'celebrating' if look['cta'] != 'card' else 'pointing'},
         'crowd': 7 if look['cta'] == 'crowd' else 0, 'grammar': look['cta']}]})
    plan = {'schema_version': 'reel-1.0', 'quality_mode': 'motif-gold-v1', 'slug': brief['slug'], 'seed': seed, 'look': look_id, 'library': 'draft' if allow_draft else 'canonical', 'beats': beats, 'library_requests': [], 'warnings': default_label_warnings(beats)}
    return plan


def default_label_warnings(beats):
    """Rig text left at library defaults reads as another film's words: flag it for the brief author."""
    from motif_rigs import all_rigs
    rigs = all_rigs()
    out = []
    for beat in beats:
        for shot in beat['shots'][:1]:
            if not shot['rig']:continue
            rig = rigs.get(shot['rig']['id'])
            if rig is None:continue  # validate_plan records the missing capability.
            props = rig.params_schema['properties']
            text = [k for k, v in props.items() if v.get('type') == 'string' or v.get('items', {}).get('type') == 'string']
            left = [k for k in text if k not in shot['rig'].get('params', {})]
            if left:out.append(f'{beat["id"]}: {rig.name} text params {left} use library defaults {[rig.defaults.get(k) for k in left]}; set visual.params in the brief')
    return out


def validate_plan(plan, allow_draft=False):
    """Every ID must exist in the (approved) catalogue; params must fit the rig schema."""
    from motif_library import catalog, ids
    from motif_rigs import get as get_rig
    from motif_rigs.palettes import PALETTES
    cat = catalog(allow_draft);errors, requests = [], []
    rigs, rooms, costumes, inserts = ids(cat, 'rig'), ids(cat, 'room'), ids(cat, 'costume'), ids(cat, 'insert')
    from motif_looks import LOOKS
    from motif_inserts import validate_insert
    if plan.get('look', 'paper-craft') not in LOOKS:errors.append(f'unknown look {plan.get("look")}')
    for beat in plan['beats']:
        if beat['palette'] not in PALETTES:errors.append(f'{beat["id"]}: unknown palette {beat["palette"]}')
        for shot in beat['shots']:
            where = shot['id']
            if shot['room'] not in rooms:requests.append({'kind': 'room', 'id': shot['room'], 'needed_by': where})
            if shot['rig']:
                if shot['rig']['id'] not in rigs:requests.append({'kind': 'rig', 'id': shot['rig']['id'], 'needed_by': where})
                else:
                    try:get_rig(shot['rig']['id']).params(shot['rig'].get('params'))
                    except Exception as e:errors.append(f'{where}: rig params invalid ({getattr(e, "message", e)})')
            if shot['insert'] and shot['insert']['kind'] not in inserts:requests.append({'kind': 'insert', 'id': shot['insert']['kind'], 'needed_by': where})
            elif shot['insert']:
                try:validate_insert(shot['insert'])
                except ValueError as e:errors.append(f'{where}: insert args invalid ({e})')
            for c in shot['bot'].get('costume', []):
                if c not in costumes:requests.append({'kind': 'costume', 'id': c, 'needed_by': where})
            if not shot.get('headline'):errors.append(f'{where}: headline missing')
    errors += [f'library_request: {r["kind"]} {r["id"]} for {r["needed_by"]} is not in the {"draft" if allow_draft else "approved"} library' for r in requests]
    return errors, requests


# 4 Voice -------------------------------------------------------------------------------

def _wav_duration(path):
    with wave.open(str(path)) as w:return w.getnframes() / w.getframerate()


def _silence(path, seconds, rate=24000):
    with wave.open(str(path), 'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate);w.writeframes(b'\0\0' * round(seconds * rate))


def voice(project, lines, name='af_nova', stub=False, python=None):
    """One take per line, concatenated with fixed gaps. Returns [(id, start, end)]."""
    from motif_reel_script import GAP, WORDS_PER_SECOND, count
    folder = project / 'assets/voice/clauses';folder.mkdir(parents=True, exist_ok=True)
    import os
    env = dict(os.environ)
    if python:env['HYPERFRAMES_PYTHON'] = str(python)
    takes = []
    for i, (id_, text) in enumerate(lines):
        out = folder / f'{i:02d}-{id_}.wav';(folder / f'{i:02d}-{id_}.txt').write_text(text + '\n')
        if stub:_silence(out, count(text) / WORDS_PER_SECOND)
        elif not out.exists():
            subprocess.run(['npx', '--yes', f'hyperframes@{PIN}', 'tts', f'--text-file={out.with_suffix(".txt").name}', f'--voice={name}', f'--speed={SPEED}', f'--output={out.name}', '--json'],
                           cwd=folder, env=env, check=True, capture_output=True, timeout=900)
        takes.append((id_, out))
    gap = folder / 'gap.wav';_silence(gap, GAP)
    listing = folder / 'concat.txt';listing.write_text(''.join(f"file '{p.name}'\nfile 'gap.wav'\n" for _, p in takes[:-1]) + f"file '{takes[-1][1].name}'\n")
    narration = project / 'assets/voice/narration-af-nova.wav'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(listing), '-ar', '24000', '-ac', '1', str(narration)], check=True)
    spans, t = [], 0.0
    for id_, p in takes:
        d = _wav_duration(p);spans.append((id_, round(t, 4), round(t + d, 4)));t += d + GAP
    (project / 'assets/voice/narration.txt').write_text(' '.join(text for _, text in lines) + '\n')
    write(project / 'speech-timing.json', {'method': 'one TTS take per line; spans are measured take durations plus fixed gaps' if not stub else 'STUB: silent takes at the measured speaking rate (no TTS available)',
                                          'voice': name, 'stub': stub, 'gap': GAP, 'spans': [{'id': i, 'start': s, 'end': e} for i, s, e in spans], 'duration': round(t - GAP, 4)})
    return spans, t - GAP


# 5 Compile -----------------------------------------------------------------------------

def schedule(plan, spans, voice_duration):
    """Shot start/duration in seconds (frame-snapped). Claim beats split at the rig contact."""
    timing = {i: (s, e) for i, s, e in spans};shots = [];cursor = 0
    for k, beat in enumerate(plan['beats']):
        start, end = timing[beat['id']]
        nxt = plan['beats'][k + 1]['id'] if k + 1 < len(plan['beats']) else None
        stop = timing[nxt][0] if nxt else voice_duration + TAIL
        stop_f = round(stop * FPS);start_f = cursor;length = stop_f - start_f
        if len(beat['shots']) == 1:parts = [length]
        else:
            first = round(length * .48);parts = [first, length - first]
        for shot, n in zip(beat['shots'], parts):
            if n / FPS > SHOT_MAX:shot['split_headline'] = True
            shots.append({**shot, 'beat': beat['id'], 'palette': beat['palette'], 'start_frame': start_f, 'frames': n});start_f += n
        cursor = stop_f
    return shots


def lights_for(layout):
    """Finish-pass light kit from the room's light colour, placed over the hero."""
    hx, hy, hw, hh = layout['hero']['box'] if layout.get('hero') else (160, 400, 400, 600)
    cx = min(.85, max(.15, (hx + hw / 2) / 720));cy = min(.6, max(.2, (hy + hh * .3) / 1280))
    out = []
    for item in layout['lights']:
        if item['kind'] == 'beam':
            out.append({'kind': 'beam', 'x': cx, 'y': .05, 'to_y': .85, 'top_width': .08, 'bottom_width': .6, 'color': item['colour'], 'strength': .14, 'blend': 'screen'})
        else:
            out.append({'kind': 'lamp', 'x': cx, 'y': cy, 'radius': .85, 'color': item['colour'], 'strength': .5, 'blend': 'soft-light'})
    # Mayowa approved the finish on condition the reels stay colourful: every
    # shot also gets a light tinted by its own palette, so light colour varies per scene.
    if layout.get('palette'):
        from motif_rigs.palettes import palette
        out.append({'kind': 'lamp', 'x': 1 - cx, 'y': .7, 'radius': .6, 'color': palette(layout['palette'])['accent'], 'strength': .28, 'blend': 'soft-light'})
    return out


def headline_piece(text, c, t_in):
    """Taped cream headline in the headline band; Inter 900, fitted to width."""
    from motif_rigs.library import label_size
    from motif_ui_components import card, g, txt
    lines = [text] if len(text) <= 16 else _wrap(text)
    size = min(label_size(l, 600, 64) for l in lines);h = 40 + size * 1.08 * len(lines);w = min(660, max(len(l) for l in lines) * size * .62 + 70)
    body = card(w, h, c['light'], .1)
    for k, l in enumerate(lines):body += txt(l, w / 2, 26 + size * .86 + k * size * 1.08, size, c['dark'], 900, 'middle')
    tape = card(80, 26, c['secondary'], .04)
    pop = .82 + .18 * min(1.0, t_in / 6) if t_in < 6 else 1.0
    return g(g(body + g(tape, w / 2 - 40, -12, -4), -w / 2, -h / 2), 360, 150 + h / 2, -1.2, pop)


def _wrap(text):
    words = text.split();best = None
    for k in range(1, len(words)):
        a, b = ' '.join(words[:k]), ' '.join(words[k:]);score = max(len(a), len(b))
        if best is None or score < best[0]:best = (score, [a, b])
    return best[1] if best else [text]


def insert_piece(insert, c_name, u, frame):
    """Insert at progress u in [0, 1] of its shot."""
    import motif_inserts as ins
    from motif_ui_components import g
    a = insert.get('args', {});kind = insert['kind']
    pop = min(1.0, frame / 7);scale = .7 + .3 * (1 - (1 - pop) ** 3)
    if kind == 'counter':
        values = ins.counter_values(a.get('start', 0), a['end'], 40);v = values[min(len(values) - 1, int(u * 60))]
        body = ins.counter(v, c_name, a.get('prefix', ''), a.get('suffix', ''), a.get('label'), w=300, roll=(frame % 4) / 4 if v != a['end'] else 0)
        return g(body, 360 - 150 * scale, 330, 2, scale)
    if kind == 'comment_end_card':return g(ins.comment_end_card(a['keyword'], c_name), 80, 330, -1.5, scale)
    if kind == 'star_badge':return g(ins.star_badge(c_name, a.get('rating', 5), min(a.get('filled', 5), int(u * 8) + 1), 1.2), 230, 380, 0, scale)
    if kind == 'price_tag':return g(ins.price_tag(a['amount'], c_name, a.get('strike')), 470, 330, -6 + 3 * math.sin(frame * .2), scale)
    if kind == 'gauge':return g(ins.gauge(min(a.get('value', .8), u * 1.4), c_name, a.get('label', '')), 540, 420, 0, scale)
    if kind == 'progress_bar':return g(ins.progress_bar(min(a.get('fraction', 1.0), u * 1.5), c_name, label=a.get('label', '')), 150, 390, -1, scale)
    raise ValueError(f'unsupported insert {kind}')


def camera(markup, zoom, cx, cy, dx=0.0, dy=0.0):
    """Per-piece camera so each top-level piece still moves independently."""
    if abs(zoom - 1) < 1e-6 and abs(dx) < 1e-6 and abs(dy) < 1e-6:return markup
    return f'<g transform="translate({cx + dx:.2f} {cy + dy:.2f}) scale({zoom:.5f}) translate({-cx:.2f} {-cy:.2f})">{markup}</g>'


def shot_frames(shot, layout, seed, look='paper-craft'):
    """World markup for every frame of one shot."""
    import motif_sets as ms
    from motif_bot_kit import crowd_layout, dressed_bot
    from motif_props import PROPS
    from motif_rigs import get as get_rig
    from motif_rigs.base import ease, place
    from motif_rigs.palettes import palette
    import motif_looks
    L = motif_looks.get(look);grammar = shot.get('grammar', 'crowd')
    c = palette(shot['palette']);n = shot['frames'];room = ms.ROOMS[shot['room']]
    rig = get_rig(shot['rig']['id']) if shot['rig'] else None
    action = next(iter(rig.actions)) if rig else None;tc = rig.contact_t(action) if rig else 0
    hb = layout['hero']['box'] if layout.get('hero') else (160, 500, 400, 540)
    cx, cy = hb[0] + hb[2] / 2, hb[1] + hb[3] * .55
    members = crowd_layout(shot.get('crowd', 0), seed, area=(40, 680, 760, 1050), scale=(.1, .16)) if shot.get('crowd') else []
    headlines = [shot['headline']] + ([shot.get('headline_b')] if shot.get('split_headline') and shot.get('headline_b') else [])
    frames = []
    for f in range(n):
        u = f / max(1, n - 1);pieces = []
        zoom, dx, dy = motif_looks.camera(L['camera'], shot['role'], u, f, n);dy += motif_looks.slide_offset(L['transition'], f)
        cam = lambda markup: camera(markup, zoom, cx, cy, dx, dy)
        if dy > 0:pieces.append(f'<rect width="720" height="1280" fill="{L["transition_colour"]}"/>')
        pieces.append(cam(room['draw'](c)))
        for item in layout.get('dressing', []):
            if item['layer'] == 'back':
                sway = 1.2 * math.sin(f * .09 + item['x'] * .01) if PROPS[item['prop']].mount in ('ceiling', 'sky') else 0
                pieces.append(cam(f'<g transform="rotate({sway:.2f} {item["x"]:.1f} {item["box"][1]:.1f})">{place(PROPS[item["prop"]].render(c), item["x"], item["y"], item["scale"])}</g>'))
        if rig:
            if shot['role'] == 'setup':t = tc * ease(min(1.0, u / .92))
            else:t = tc + (1 - tc) * min(1.0, u / .55)
            h = layout['hero'];pieces.append(cam(place(rig.render(h['values'] or None, (action, t), shot['palette']), h['x'], h['y'], h['scale'])))
        b = layout['bot'];bot = shot['bot']
        if shot['role'] == 'setup':
            enter = min(1.0, u / .5);side = -1 if b['x'] < 360 else 1
            bx = b['x'] + side * 160 * (1 - ease(enter));walking = enter < 1
            pieces.append(cam(dressed_bot(bx, b['y'], b['scale'], 'determined', 'standing', bot['costume'], shot['palette'], flip=side > 0, cycle='walk' if walking else None, phase=f / 10)))
        elif shot['role'] == 'payoff':
            hop = max(0.0, math.sin(min(1.0, u / .35) * math.pi)) * 30
            pieces.append(cam(dressed_bot(b['x'], b['y'] - hop, b['scale'], bot['face'], bot['pose'] if u > .2 else 'standing', bot['costume'], shot['palette'], head=round(3 * math.sin(f * .3)))))
        elif grammar == 'big-bot':
            hop = abs(math.sin(f * .18)) * 18;tilt = 4 * math.sin(f * .15)
            pieces.append(cam(dressed_bot(360, 1050 - hop, .55, bot['face'], bot['pose'], bot['costume'], shot['palette'], angle=tilt)))
        elif grammar in ('number', 'card'):
            hop = abs(math.sin(f * .22)) * 16
            pieces.append(cam(dressed_bot(150 if grammar == 'card' else 560, 1030 - hop, .34, bot['face'], 'pointing', bot['costume'], shot['palette'], flip=grammar == 'number')))
        else:
            hop = abs(math.sin(f * .22)) * 26
            pieces.append(cam(dressed_bot(360, 1010 - hop, .3, bot['face'], bot['pose'], bot['costume'], shot['palette'])))
        for k, m in enumerate(members):
            bounce = abs(math.sin(f * .25 + k)) * 14
            pieces.append(cam(dressed_bot(m['x'], m['y'] - bounce, m['s'], m['face'], 'celebrating' if (f // 8 + k) % 2 else m['pose'], m['costume'], shot['palette'], m['angle'], m['flip'])))
        for item in layout.get('dressing', []):
            if item['layer'] == 'front':pieces.append(cam(place(PROPS[item['prop']].render(c), item['x'], item['y'], item['scale'])))
        if shot.get('insert') and (shot['role'] != 'payoff' or u > .25):
            start = .25 if shot['role'] == 'payoff' else 0;local = (u - start) / (1 - start)
            piece = insert_piece(shot['insert'], shot['palette'], local, int(local * (n - 1)))
            if grammar == 'number' and shot['role'] == 'hook':piece = f'<g transform="translate(360 560) scale(1.45) translate(-360 -400)">{piece}</g>'
            elif grammar == 'card' and shot['role'] == 'cta':piece = f'<g transform="translate(420 520) scale(1.25) translate(-360 -420)">{piece}</g>'
            pieces.append(piece)
        text = headlines[min(len(headlines) - 1, int(u * len(headlines)))]
        pieces.append(motif_looks.headline(L['headline'], text, c, f))
        overlay = motif_looks.transition_in(L['transition'], f, L['transition_colour']) + motif_looks.transition_out(L['transition'], f, n, L['transition_colour'])
        if overlay:pieces.append(overlay)
        frames.append(''.join(pieces))
    return frames


SOUND = {'overflow-vehicle': 'spring', 'plate-stack': 'paper', 'hydraulic-press': 'reject', 'race-track': 'star', 'balance-scale': 'cloth',
         'stacked-meter': 'pop', 'thermometer': 'star', 'receipt-stack': 'paper', 'stamp-gate': 'reject', 'conveyor': 'key1'}


def prepare(project, brief):
    for folder in ('assets/fonts', 'assets/materials', 'assets/voice', 'compositions', 'review'):(project / folder).mkdir(parents=True, exist_ok=True)
    for name in ('gsap.min.js', 'motion-engine.js', 'motion-primitives.js'):shutil.copy2(ROOT / 'videos/motif-calendar-reel/assets' / name, project / 'assets' / name)
    shutil.copy2(ROOT / 'assets/runtime/motif-frame-sequence.js', project / 'assets/motif-frame-sequence.js')
    for name in ('Inter-700.woff2', 'EBGaramond-700.woff2', 'OFL-inter.txt', 'OFL-eb-garamond.txt'):shutil.copy2(V6 / 'assets/fonts' / name, project / 'assets/fonts' / name)
    # v6's Inter 900 is subset to its own headline glyphs; reels need the full Latin set.
    shutil.copy2(ROOT / 'assets/fonts/Inter-900-latin.woff2', project / 'assets/fonts/Inter-900.woff2')
    from motif_materials import install
    install(project)
    surface = project / 'assets/materials/world-paper.webp'
    if not surface.exists():shutil.copy2(V6 / 'assets/materials/world-paper.webp', surface)
    shutil.copy2(V6 / 'hyperframes.json', project / 'hyperframes.json')
    write(project / 'package.json', {'name': project.name, 'private': True, 'scripts': {k: f'npx --yes hyperframes@{PIN} {v}' for k, v in (('check', 'check'), ('render', 'render'), ('dev', 'preview'))}})
    write(project / 'asset-provenance.json', {'rules': [
        {'glob': 'assets/voice/*', 'origin': 'motif-tts', 'generator': f'hyperframes {PIN} tts, voice {brief.get("voice", "af_nova")}, one take per line of the brief'},
        {'glob': 'assets/voice/clauses/*', 'origin': 'motif-tts', 'generator': f'hyperframes {PIN} tts clause takes and generated silence'},
        {'glob': 'assets/sfx/*', 'origin': 'procedural-seeded', 'generator': 'motif_ui_production.make_sounds (seeded filtered noise and resonators)'}]})


def caption_groups(lines, spans):
    """Caption chunks of up to four words; word times proportional to characters inside each measured take."""
    timing = {i: (s, e) for i, s, e in spans};groups = []
    for id_, text in lines:
        start, end = timing[id_];words = text.split();total = sum(len(w) + 1 for w in words);t = start;chunk = []
        for w in words:
            d = (end - start) * (len(w) + 1) / total;chunk.append({'text': w, 'start': round(t * FPS) / FPS, 'end': t + d});t += d
            if len(chunk) == 4 or re.search(r'[.!?,]$', w):groups.append(chunk);chunk = []
        if chunk:groups.append(chunk)
    out = [{'text': ' '.join(w['text'] for w in g), 'start': g[0]['start'], 'words': g} for g in groups]
    for i, g in enumerate(out):g['end'] = out[i + 1]['start'] if i + 1 < len(out) else spans[-1][2] + TAIL
    return out


def compile_reel(project, plan, spans, voice_duration, seed=0):
    import motif_sets as ms
    from fontTools.ttLib import TTFont
    from motif_rigs import get as get_rig
    from motif_script import write_index
    from motif_ui_components import DEFS
    from motif_ui_production import captions_frame, make_sounds, namespace, write_composition
    shots = schedule(plan, spans, voice_duration);frames_index, cues, layouts, lights = [], [], {}, {}
    ledger = {x['id']: x for x in make_sounds(project)}
    by_beat = {}
    for shot in shots:
        key = (shot['beat'], shot['room'])
        if key not in layouts:
            if shot['rig']:
                layouts[key] = ms.solve_checked(shot['room'], shot['rig']['id'], shot['rig'].get('params'), shot['palette'], seed, len(layouts), shot['bot']['costume'])
            else:
                layouts[key] = {'room': shot['room'], 'palette': shot['palette'], 'dressing': [], 'lights': ms.ROOMS[shot['room']]['lights'], 'bot': {'x': 360, 'y': 1010, 'scale': .3, 'costume': shot['bot']['costume']}}
                try:
                    probe = ms.solve(shot['room'], 'conveyor', None, shot['palette'], seed, len(layouts))
                    layouts[key]['dressing'] = [d for d in probe['dressing'] if d['role'] != 'overlap']
                except ValueError:pass
        layout = layouts[key];by_beat.setdefault(shot['beat'], []).append(shot['id'])
        frames = shot_frames(shot, layout, seed + shot['start_frame'], plan.get('look', 'paper-craft'))
        dur = shot['frames'] / FPS
        events = [{'time': round(f / FPS, 9), 'target': f'#{shot["id"]}-world', 'action': 'SET', 'params': {'props': {'innerHTML': namespace(body, shot['id'])}}} for f, body in enumerate(frames) if f]
        write_composition(project, shot['id'], dur, frames[0], events, DEFS)
        start = shot['start_frame'] / FPS
        frames_index.append({'id': shot['id'], 'start': start, 'duration': dur, 'source': f'compositions/{shot["id"]}.html'})
        lights[shot['id']] = lights_for(layout)
        if shot['rig'] and shot['role'] == 'setup':
            rig = get_rig(shot['rig']['id']);item = ledger[SOUND.get(rig.name, 'pop')]
            cues.append({'shot': shot['id'], 'start': round(start + dur * .92, 3), 'file': item['file'], 'duration': item['duration'], 'volume': .38, 'meaning': f'{rig.name} contact'})
        if shot['role'] in ('payoff', 'hook', 'cta'):
            item = ledger['whoosh' if shot['role'] != 'payoff' else 'star'];cues.append({'shot': shot['id'], 'start': round(start + (.02 if shot['role'] != 'payoff' else dur * .3), 3), 'file': item['file'], 'duration': item['duration'], 'volume': .26, 'meaning': f'{shot["role"]} accent'})
    duration = frames_index[-1]['start'] + frames_index[-1]['duration']
    lines = [(b['id'], b['narration']) for b in plan['beats']];groups = caption_groups(lines, spans)
    import motif_looks
    look = motif_looks.get(plan.get('look', 'paper-craft'))
    fonts = {'serif': TTFont(project / 'assets/fonts/EBGaramond-700.woff2'), 'sans': TTFont(project / 'assets/fonts/Inter-900.woff2')}
    cap = lambda f: motif_looks.captions(look['captions'], groups, f, fonts, look['caption_colours'])
    total = round(duration * FPS)
    capevents = [{'time': round(f / FPS, 9), 'target': '#captions-world', 'action': 'SET', 'params': {'props': {'innerHTML': namespace(cap(f), 'captions')}}} for f in range(1, total)]
    write_composition(project, 'captions', duration, cap(0), capevents, DEFS)
    write(project / 'audio-plan.json', {'duration': voice_duration, 'narration': 'assets/voice/narration-af-nova.wav', 'sfx_cues': cues, 'music': False, 'subjective_listening': 'not assessed'})
    write_index(project, frames_index, duration, voice_duration, 0)
    write(project / 'shots.json', [{k: v for k, v in s.items()} for s in shots])
    write(project / 'set-layouts.json', {f'{k[0]}': v for k, v in layouts.items()})
    write(project / 'finish-lights.json', lights)
    write(project / 'caption-events.json', groups)
    return {'duration': duration, 'shots': len(shots), 'frames_index': frames_index}


# Pipeline ------------------------------------------------------------------------------

def codex_available():
    return shutil.which('codex') is not None


class ReelFailure(ValueError):
    """An unsuccessful stage with a saved, non-approval receipt."""


def bind_capture_sources(project):
    """Bind actual composition states and local resources via existing capture APIs."""
    from motif_finish import SCRIPT
    from motif_frame_render import clips
    initial, events, shots = [], [], []
    for clip in clips(project):
        spec = json.loads(SCRIPT.search((project / clip['src']).read_text()).group(2))
        initial.extend(spec['initial'])
        events.extend({**e, 'time': round(clip['start'] + e['time'], 9)} for e in spec['events'])
        if clip['id'] != 'captions':
            shots.append({'id': clip['id'], 'startFrame': round(clip['start'] * FPS),
                          'endFrame': round((clip['start'] + clip['duration']) * FPS)})
    write(project / 'scene-events.json', {'schemaVersion': '1.0', 'fps': FPS,
          'durationSec': max(s['endFrame'] for s in shots) / FPS,
          'initial': initial, 'events': sorted(events, key=lambda e: e['time']), 'shots': shots})
    paths = [project / 'index.html', *sorted((project / 'compositions').glob('*.html')),
             *(p for p in sorted((project / 'assets').rglob('*')) if p.is_file())]
    write(project / 'resource-manifest.json', {'resources': [
          {'path': p.relative_to(project).as_posix(), 'sha256': sha(p)} for p in paths]})


def check_production(project, phase='rough'):
    """Use the existing gates on an already-authored production, without critics."""
    from motif_evidence import evidence_inputs, require_capture, require_scope, FILM_MODES
    from motif_quality import require_gate
    from motif_structure import require_structure
    project = Path(project)
    if require_scope(project)['actual_mode'] not in FILM_MODES:
        raise ValueError('production check requires an explicitly declared film project')
    require_structure(project)
    evidence_inputs(project)
    require_capture(project)
    return require_gate(project, phase)


def run(brief_path, out_root=None, allow_draft=False, stub_voice=False, render=False, python=None, finish=True, avoid_looks=(), local_draft=False):
    from motif_evidence import declare, evidence_inputs, freeze_capture, seal_capture
    from motif_pacing import check as pacing, check_plan
    from motif_provenance import check as provenance
    from motif_reel_script import script_record, validate
    import motif_sets as ms
    brief = read(brief_path)
    root = Path(out_root) if out_root else ROOT / 'videos/productions'
    # A malformed slug must never redirect receipt writes outside the output root.
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{2,60}', str(brief.get('slug', ''))):
        raise ValueError('script: a valid local slug is required before creating a project')
    project = root / brief['slug']
    if project.exists():raise FileExistsError(f'{project} exists; choose a fresh slug')
    project.mkdir(parents=True);write(project / 'brief.json', brief)
    record = {'brief': str(brief_path), 'mode': 'experimental-local-draft' if local_draft else 'original-film',
              'film_approved': False, 'status': 'IN_PROGRESS', 'stages': []}
    final = project;current = 'script'
    def stage(name, status, **kw):
        record['stages'].append({'stage': name, 'status': status, **kw})
    def require_pass(name, passed):
        if not passed:raise ReelFailure(f'{name} failed; advancement blocked')
    try:
        errors = validate(brief)
        if errors:raise ReelFailure('script: ' + '; '.join(errors))
        script = script_record(brief);write(project / 'reel-script.json', script)
        stage('script', 'PASS', hook=script['hook'], hook_alternates=script['hook_alternates'])
        current = 'plan'
        plan = plan_reel(brief, allow_draft, avoid_looks);errs, requests = validate_plan(plan, allow_draft)
        if requests:write(project / 'library-requests.json', requests)
        if errs:stage('plan', 'FAIL', errors=errs);raise ReelFailure('plan: ' + '; '.join(errs))
        write(project / 'production-plan.json', plan)
        declare(project, 'technical-fixture' if local_draft else 'original-film', 'motif_reel.run')
        stage('plan', 'PASS', look=plan['look'], shots=sum(len(b['shots']) for b in plan['beats']), warnings=plan['warnings'])
        current = 'production-boundary'
        if not local_draft:
            from motif_structure import require_structure
            # The deterministic reel plan cannot invent authored structure or a live review.
            require_structure(project)
            stage('production-boundary', 'PASS', scope='existing structure review; other film gates still required')
        else:
            stage('production-boundary', 'SCOPED_OUTPUT_ONLY', scope='experimental local draft; not original-film production')
            stage('critics', 'NOT_PERFORMED', reason='explicit local draft; no model CLI invoked',
                  reviews={k: 'NOT_PERFORMED' for k in ('structure', 'direction', 'story', 'visual')})
        current = 'voice'
        prepare(project, brief)
        spans, voice_duration = voice(project, [(b['id'], b['narration']) for b in plan['beats']], brief.get('voice', 'af_nova'), stub_voice, python)
        stage('voice', 'STUB' if stub_voice else 'PASS', duration=round(voice_duration, 3))
        current = 'structure'
        beats_t = []
        for s in schedule(json.loads(json.dumps(plan)), spans, voice_duration):
            a, n = s['start_frame'] / FPS, s['frames'] / FPS;metaphor = s['rig']['id'] if s['rig'] else s['role']
            heads = [s['headline'], s.get('headline_b')] if s.get('split_headline') else [s['headline']]
            for k, h in enumerate(heads):beats_t.append({'id': f'{s["id"]}.{k}', 'start': round(a + n * k / len(heads), 3), 'end': round(a + n * (k + 1) / len(heads), 3), 'headline': h, 'metaphor': metaphor, 'cut_before': True})
        measured = validate(brief, measured=voice_duration + TAIL)
        if measured:raise ReelFailure('voice runtime: ' + '; '.join(measured))
        structure = check_plan(beats_t, beats_t[-1]['end'])
        stage('structure', 'FAIL' if structure else 'PASS', failures=structure, scope='pacing data only; no independent structure approval')
        require_pass('structure', not structure)
        current = 'compile'
        compiled = compile_reel(project, plan, spans, voice_duration, brief.get('seed', 0))
        stage('compile', 'PASS', duration=round(compiled['duration'], 3), shots=compiled['shots'])
        current = 'capture'
        bind_capture_sources(project)
        evidence_inputs(project)  # Film scopes require authored causal maps before capture.
        capture = freeze_capture(project)
        current = 'rough'
        rough = pacing(project)
        if rough['status'] != 'PASS':stage('rough', 'FAIL', pacing=rough)
        require_pass('rough pacing', rough['status'] == 'PASS')
        from motif_frame_snapshot import at_times, snapshot
        mids = [f['start'] + f['duration'] * .7 for f in compiled['frames_index']]
        pngs = snapshot(project, at_times(project, mids), project / 'review/rough', size=(360, 640))
        seal_capture(project, capture, pngs)
        empty = ms.check_frames(pngs)
        stage('rough', 'PASS' if empty['status'] == 'PASS' else 'FAIL', pacing=rough, empty_field=empty)
        require_pass('rough', empty['status'] == 'PASS')
        current = 'critics'
        if not local_draft:
            check_production(project, 'rough')
            stage('critics', 'PASS', scope='existing fresh production gate; no new invocation')
        current = 'finish'
        if finish:
            from motif_finish import apply
            from motif_looks import finish_style
            style = finish_style(plan['look'], project / 'finish-style.json')
            finished = project.with_name(project.name + '-finished')
            apply(project, finished, style_path=style, lights_path=project / 'finish-lights.json')
            final = finished
            stage('finish', 'PASS', project=str(final), style=f'motif-finish-v1+{plan["look"]}')
            bind_capture_sources(final)
        current = 'gate'
        origin = provenance(final);gate = pacing(final)
        passed = origin['status'] == 'PASS' and gate['status'] == 'PASS'
        stage('gate', 'PASS' if passed else 'FAIL', scope='asset provenance and pacing only',
              provenance={k: origin[k] for k in ('status', 'checked', 'unknown', 'reference_derived', 'rejected')}, pacing=gate)
        require_pass('gate', passed)
        if not local_draft:check_production(final, 'final')
        if render:
            current = 'render'
            evidence_inputs(final)
            capture = freeze_capture(final)
            from motif_frame_render import render as frame_render
            out = final / 'renders/review.mp4';result = frame_render(final, out)
            seal_capture(final, capture, [out])
            stage('render', 'PASS', file=str(out), frames=result['frames'])
        record['status'] = 'DRAFT_REVIEW_REQUIRED' if local_draft else 'REVIEW_REQUIRED'
        stage('review', record['status'], note='No film approval; playback/listening and creative reviews remain required')
        return record
    except Exception as error:
        record['status'] = 'BLOCKED';record['failure'] = {'stage': current, 'type': type(error).__name__, 'message': str(error)}
        if not record['stages'] or record['stages'][-1]['stage'] != current or record['stages'][-1]['status'] != 'FAIL':
            stage(current, 'FAIL', error=str(error))
        raise ReelFailure(f'{current}: {error}; receipt: {project / "reel-record.json"}') from error
    finally:
        write(project / 'reel-record.json', record)
        if final != project:write(final / 'reel-record.json', record)


def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n')[0]);sub = p.add_subparsers(dest='cmd', required=True)
    r = sub.add_parser('run');r.add_argument('--brief', type=Path, required=True);r.add_argument('--out', type=Path)
    r.add_argument('--allow-draft', action='store_true', help='use DRAFT library entries (review renders before approval)')
    r.add_argument('--stub-voice', action='store_true');r.add_argument('--render', action='store_true');r.add_argument('--no-finish', action='store_true')
    r.add_argument('--local-draft', action='store_true', help='experimental technical-fixture output; creative reviews NOT_PERFORMED, no model CLI')
    r.add_argument('--tts-python', type=Path, help='Python with kokoro-onnx for hyperframes tts')
    pl = sub.add_parser('plan');pl.add_argument('--brief', type=Path, required=True);pl.add_argument('--allow-draft', action='store_true')
    pc = sub.add_parser('check-production');pc.add_argument('project', type=Path);pc.add_argument('--phase', choices=('rough', 'final'), default='rough')
    a = p.parse_args()
    if a.cmd == 'check-production':
        try:print(json.dumps(check_production(a.project, a.phase), indent=2))
        except (ValueError, FileNotFoundError) as e:p.exit(1, f'Production blocked: {e}\n')
        return
    if a.cmd == 'plan':
        plan = plan_reel(read(a.brief), a.allow_draft);errs, _ = validate_plan(plan, a.allow_draft);print(json.dumps({'plan': plan, 'errors': errs}, indent=2));raise SystemExit(1 if errs else 0)
    try:record = run(a.brief, a.out, a.allow_draft, a.stub_voice, a.render, a.tts_python, not a.no_finish, local_draft=a.local_draft)
    except (ValueError, FileNotFoundError, FileExistsError) as e:p.exit(1, f'Reel blocked: {e}\n')
    print(json.dumps(record['stages'], indent=2))


if __name__ == '__main__':
    main()
