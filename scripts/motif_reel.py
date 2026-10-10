"""One command from a reel brief to a finished, gated review render.

    python scripts/motif_reel.py run --brief briefs/x.json [--allow-draft] [--render]

Stages (each writes its record into the project; nothing is per-film code):

   1 script      validate the brief, build 3 hook alternates, runtime estimate
   2 plan        library-constrained plan: every shot names a room, rig, insert,
                 Bot costume and headline from the catalogue; unknown IDs fail and
                 missing capabilities become library_request records
   3 structure   plan-level pacing (cuts, headline cadence, runtime); the live
                 Codex structure/direction critics run when available
   4 voice       one TTS take per line (hook, beats, CTA), measured durations
   5 compile     per-shot frame sequences from library data (motif_sets, rigs,
                 inserts, Bot kit), captions, SFX at rig contacts
   6 rough       pacing and empty-field checks on the native compositions
   7 critics     live Codex story/visual critics when available, else recorded
                 as not run
   8 finish      motif_finish pass with per-room lights
   9 gate        technical: provenance + pacing on the finished project
  10 review      optional review render (motif_frame_render); stops at
                 REVIEW_REQUIRED for Mayowa

The narration is the brief's text; timing comes from the measured clip
durations. Word timing inside a clip is proportional to characters, which is
an approximation and is recorded as such.
"""
import argparse
import copy
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
DELIVERY = (1080, 1920)  # delivery size; compositions stay on the 720 x 1280 design grid
MUSIC_VOLUME = .3         # bed level before ducking; fills the pauses like the references
BOIL_STEP = 2           # stop-motion boil: pieces shift every 2 frames (15 fps, animating on twos)
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
    words = re.sub(r'[^\w$%.,\' -]', '', text).upper().replace(', ', ' ').rstrip('.').split()
    while words and words[0] in EDGE_WORDS:words.pop(0)
    out = []
    for w in words:
        if len(' '.join(out + [w])) > limit:break
        out.append(w)
    while len(out) > 1 and out[-1] in EDGE_WORDS:out.pop()
    return ' '.join(out) or text[:limit].upper()


def _number(value):
    m = re.search(r'(\$)?([\d,]+(?:\.\d+)?)\s*([kKmM%x]|\+)?', value or '')
    if not m:return None
    n = float(m.group(2).replace(',', ''));suffix = (m.group(3) or '')
    return {'prefix': m.group(1) or '', 'value': int(n) if n == int(n) else n, 'suffix': suffix}


def _insert_for(fact, text, cat):
    from motif_library import retrieve
    num = _number(fact.get('value'))
    if len(re.findall(r'\d[\d,.]*', fact.get('value') or '')) > 1:num = None  # a range ("1 to 8%") is not one number to count to
    if num and isinstance(num['value'], int):
        unit = re.sub(r'[$\d,.%+]', '', fact.get('value', '')).strip()
        return {'kind': 'counter', 'args': {'start': 0, 'end': num['value'], 'prefix': num['prefix'], 'suffix': num['suffix'], 'label': _short(unit or fact['claim'], 16)}}
    from motif_library import words
    best = [e for e in retrieve(cat, text, 'insert', 3, exclude=('comment_end_card', 'counter', 'progress_bar')) if words(text) & set(e['tags'])]
    # No insert beats a filler one: a full progress bar labelled with a stray word
    # was clutter that fought the rig's own labels (2026-10-09 review, item 5).
    if not best:return None
    kind = best[0]['id']
    args = {'star_badge': {'rating': 5, 'filled': 5}, 'price_tag': {'amount': fact.get('value') or 'FREE'}, 'gauge': {'value': .85, 'label': _short(fact.get('value') or 'MAX', 10)},
            'progress_bar': {'fraction': 1.0, 'label': _short(fact.get('value') or 'DONE', 14)}}.get(kind, {})
    return {'kind': kind, 'args': args}


def plan_reel(brief, allow_draft=False, avoid_looks=()):
    """Deterministic library-constrained planner (the live-Codex planner, when
    present, must produce the same schema and pass the same validation)."""
    from motif_library import catalog, retrieve
    from motif_reel_script import hook_line
    import motif_looks
    from motif_semantics import rig_text, relation_of, rigs_for
    cat = catalog(allow_draft);facts = {f['id']: f for f in brief['facts']};seed = brief.get('seed', 0)
    brand = (brief.get('brand') or {}).get('slug')
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
        relation = relation_of(b, fact)
        # The machine must show the claim's relation (motif_semantics); retrieval only ranks among those.
        allowed = set(rigs_for(relation)) if relation else None
        pool = [e for e in retrieve(cat, text, 'rig', 50) if allowed is None or e['id'] in allowed]
        rig_id = visual.get('rig') or next((e['id'] for e in pool if e['id'] not in used_rigs), pool[0]['id'] if pool else None) \
            or (retrieve(cat, text, 'rig', 1, exclude=used_rigs) or retrieve(cat, text, 'rig', 1))[0]['id']
        used_rigs.append(rig_id)
        params = dict(visual.get('params', {}))
        from motif_rigs import get as _get_rig
        if brand and 'logo' in _get_rig(rig_id).params_schema['properties'] and 'logo' not in params:params['logo'] = brand
        room = room_for(text, visual.get('room'));rooms.append(room)
        room_costumes = next((e.get('costumes', []) for e in cat if e['kind'] == 'room' and e['id'] == room), [])
        costume = visual.get('costume') or ([room_costumes[i % len(room_costumes)]] if room_costumes else [])
        insert = visual.get('insert') or _insert_for(fact, text, cat)
        # The machine already prints the number: a second counter would only collide with it.
        num = _number(fact.get('value'))
        if not visual.get('insert') and num and any(str(num['value']) in t.replace(',', '') for t in rig_text(params, rig_id)):insert = None
        setup = b.get('headline') or _short(fact['claim'], 26);payoff = b.get('payoff_headline') or _short(fact.get('value') or b['narration'], 26)
        if payoff == setup:payoff = _short(b['narration'], 26)
        beats.append({'id': b['id'], 'kind': 'claim', 'relation': relation, 'narration': b['narration'], 'fact': b['fact'], 'palette': visual.get('palette') or palettes[i + 1], 'shots': [
            {'id': f'{b["id"]}-a', 'role': 'setup', 'headline': setup, 'headline_b': _short(b['narration'], 26), 'room': room, 'rig': {'id': rig_id, 'params': params, **({'hold': True} if visual.get('hold') else {})}, 'insert': None,
             'bot': {'costume': costume, 'face': 'determined', 'pose': 'walking'}},
            {'id': f'{b["id"]}-b', 'role': 'payoff', 'headline': payoff, 'headline_b': _short(fact['claim'], 26), 'room': room, 'rig': {'id': rig_id, 'params': params, **({'hold': True} if visual.get('hold') else {})}, 'insert': insert,
             'bot': {'costume': costume, 'face': 'surprised', 'pose': 'pointing'}}]})
    # Hero-first opening (review item 5, round 2): the hook shows the first claim's machine
    # already in action with the product mark, the way the references open on the metaphor.
    # The first claim beat then replays it from the start with its own setup.
    first_claim = beats[1]['shots'][0]
    if (brief.get('hook') or {}).get('hero', True):
        beats[0]['shots'][0].update({'rig': copy.deepcopy(first_claim['rig']), 'insert': None, 'crowd': 0, 'grammar': 'hero'})
    cta_room = room_for('celebrate launch ' + brief['cta']['narration'], brief['cta'].get('room'))
    beats.append({'id': 'cta', 'kind': 'cta', 'narration': brief['cta']['narration'], 'palette': palettes[-1], 'shots': [
        {'id': 'cta', 'role': 'cta', 'headline': _short(f'COMMENT {brief["cta"]["keyword"]}', 28), 'headline_b': _short(re.sub(r'[,.?!]?\s*comment\s+\S+\s*$', '', brief['cta']['narration'], flags=re.I), 28), 'room': cta_room, 'rig': None,
         'insert': {'kind': 'comment_end_card', 'args': {'keyword': brief['cta']['keyword']}}, 'bot': {'costume': ['party-hat'], 'face': 'excited', 'pose': 'celebrating' if look['cta'] != 'card' else 'pointing'},
         'crowd': 7 if look['cta'] == 'crowd' else 0, 'grammar': look['cta']}]})
    plan = {'schema_version': 'reel-1.1', 'quality_mode': 'motif-gold-v1', 'slug': brief['slug'], 'seed': seed, 'look': look_id, 'brand': brand, 'library': 'draft' if allow_draft else 'canonical', 'beats': beats, 'library_requests': [], 'warnings': default_label_warnings(beats)}
    return plan


def default_label_warnings(beats):
    """Rig text left at library defaults reads as another film's words: flag it for the brief author."""
    from motif_rigs import get as get_rig
    out = []
    for beat in beats:
        for shot in beat['shots'][:1]:
            if not shot['rig']:continue
            rig = get_rig(shot['rig']['id']);props = rig.params_schema['properties']
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
    from motif_semantics import RIG_RELATIONS, fits, rigs_for
    if plan.get('look', 'paper-craft') not in LOOKS:errors.append(f'unknown look {plan.get("look")}')
    if plan.get('brand'):
        from motif_brand import catalogue
        if plan['brand'] not in catalogue():errors.append(f'unknown brand {plan["brand"]}; vendor it in assets/brands first')
    for beat in plan['beats']:
        if beat.get('kind') != 'claim':continue
        rig = beat['shots'][0]['rig']['id'] if beat['shots'][0].get('rig') else None
        if not beat.get('relation'):errors.append(f'{beat["id"]}: claim has no relation; declare one in the brief')
        elif rig and rig in RIG_RELATIONS and not fits(rig, beat['relation']):
            errors.append(f'{beat["id"]}: metaphor mismatch: {rig} shows {RIG_RELATIONS[rig]}, the claim is {beat["relation"]} (fits: {rigs_for(beat["relation"])})')
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
        if not stub:
            # TTS pads each take with ~0.25 s of silence at both ends, which left 0.6 s holes between
            # lines; the references' delivery never stops (2026-10-10 sound study). Trim to 40 ms.
            tight = out.with_name(out.stem + '.tight.wav')
            trim = 'silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.04'
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(out), '-af', f'{trim},areverse,{trim},areverse', str(tight)], check=True)
            out = tight
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


def boil(markup, f, key, amount=1.0):
    """Stop-motion life for a cut-paper piece: a small seeded offset and turn that
    changes every BOIL_STEP frames, so nothing on screen is ever perfectly still
    (the hand-animated feel of the references; 2026-10-09 review found the reels
    moved about half as much)."""
    step = f // BOIL_STEP;h = int(hashlib.sha256(f'{key}|{step}'.encode()).hexdigest()[:8], 16)
    dx = ((h & 255) / 255 - .5) * 2.4 * amount;dy = (((h >> 8) & 255) / 255 - .5) * 2.4 * amount;a = (((h >> 16) & 255) / 255 - .5) * 1.0 * amount
    return f'<g transform="translate({dx:.2f} {dy:.2f}) rotate({a:.2f} 360 640)">{markup}</g>'


def entrance(f, delay, frames=9):
    """(scale, dy, opacity) for a piece popping in: rises 60 px and overshoots slightly."""
    from motif_rigs.base import ease
    u = max(0.0, min(1.0, (f - delay) / frames))
    if u >= 1:return 1.0, 0.0, 1.0
    over = 1 + .08 * math.sin(u * math.pi)
    return (.86 + .14 * ease(u)) * over, 60 * (1 - ease(u)), min(1.0, u * 2.5)


def poof(x, y, f, c, size=1.0, frames=12):
    """A cut-paper smoke puff at (x, y): puffs swell outward and fade over `frames`.
    The references mark an in-place change (an object swapped, a state flipped)
    with a puff like this instead of cutting away."""
    if f >= frames:return ''
    from motif_rigs.base import ease
    u = f / frames;grow = ease(min(1.0, u * 1.6));fade = 1 if u < .45 else max(0.0, 1 - (u - .45) / .55);out = ''
    for k in range(7):
        a = k * 2 * math.pi / 7 + .4;d = (18 + 62 * grow) * size;r = (16 + 30 * grow) * size * (1 - .25 * (k % 2))
        out += f'<circle cx="{x + d * math.cos(a):.1f}" cy="{y + d * math.sin(a) * .8:.1f}" r="{r:.1f}" fill="{c["light"]}" stroke="{c["dark"]}" stroke-width="3"/>'
    out += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{(26 + 34 * grow) * size:.1f}" fill="{c["light"]}"/>'
    for k in range(6):
        a = k * math.pi / 3 + .2;r0 = (60 + 70 * grow) * size;r1 = r0 + 22 * size
        out += f'<path d="M{x + r0 * math.cos(a):.1f} {y + r0 * math.sin(a):.1f}L{x + r1 * math.cos(a):.1f} {y + r1 * math.sin(a):.1f}" stroke="{c["dark"]}" stroke-width="4" stroke-linecap="round"/>'
    return f'<g opacity="{fade:.3f}">{out}</g>'


def pop_in(markup, f, delay, anchor):
    s, dy, o = entrance(f, delay)
    if s == 1 and dy == 0 and o == 1:return markup
    ax, ay = anchor
    return f'<g opacity="{o:.3f}" transform="translate({ax:.1f} {ay + dy:.1f}) scale({s:.4f}) translate({-ax:.1f} {-ay:.1f})">{markup}</g>'


def bot_motion(role, u, f, n, tc, side, entering=True):
    """Bot acting synced to the machine: (pose, face, dx, dy, squash, cycle).
    setup: walks in from its side, then works the machine (pointing/presenting)
    and recoils at the contact; payoff: reacts to the result and keeps moving."""
    from motif_rigs.base import ease
    if role == 'setup':
        walk = min(1.0, u / .25) if entering else 1.0  # a short step in: Bot is in frame at the cut
        if walk < 1:return 'standing', 'determined', side * 80 * (1 - ease(walk)), 0.0, 1.0, 'walk'
        at = u / max(1e-6, tc * .92) if tc else 1.0
        if at < .92:  # works the machine: alternating gestures, bobbing and leaning, never a held pose
            return ('pointing' if (f // 16) % 2 == 0 else 'presenting'), 'determined', 6 * math.sin(f * .17), -9 * abs(math.sin(f * .3)), 1.0, None
        hit = max(0.0, min(1.0, (at - .92) / .3))
        return 'presenting', 'surprised', 0.0, -26 * math.sin(hit * math.pi), 1 - .1 * math.sin(hit * math.pi), None
    if role == 'payoff':
        hop = max(0.0, math.sin(min(1.0, u / .3) * math.pi)) * 40 + abs(math.sin(f * .26)) * 10 * (u > .3)
        return ('celebrating' if (f // 7) % 2 else 'presenting') if u > .2 else 'standing', 'excited', 7 * math.sin(f * .2) * (u > .3), -hop, 1.0, None
    return 'celebrating', 'excited', 0.0, -abs(math.sin(f * .2)) * 20, 1.0, None


def shot_frames(shot, layout, seed, look='paper-craft', brand=None, prev=None, continued=False):
    """World markup for every frame of one shot.

    prev: (role, frames) of the shot this one continues (same beat, same set). The
    references hold the set across a beat and only cut between beats, so a
    continuing shot has no transition, nothing pops in again and the camera eases
    on from where the previous shot left it. continued: the next shot continues
    this one, so no outgoing transition. A new scene is complete on its first
    frame (2026-10-10 transitions study)."""
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
    main_x = layout['bot']['x'] if rig else {'big-bot': 360, 'card': 150, 'number': 560}.get(grammar, 360)
    members = crowd_layout(shot.get('crowd', 0) + 4, seed, area=(40, 680, 760, 1050), scale=(.1, .16)) if shot.get('crowd') else []
    # Crowd members keep clear of the main Bot (the review found overlapping Bots) and of the brand badge.
    members = [m for m in members if abs(m['x'] - main_x) > 150][:shot.get('crowd', 0)]
    headlines = [shot['headline']] + ([shot.get('headline_b')] if shot.get('split_headline') and shot.get('headline_b') else [])
    # The product mark floats in Bot's lane above its head: it never covers the rig's own labels.
    if rig:
        bot = layout['bot'];half = 235 * bot['scale']
        sticker_at = (min(720 - 56, max(56, bot['x'])), max(370, bot['y'] - 4.2 * half - 60))
    else:sticker_at = None
    poof_at = None
    # A held beat keeps its machine in the start state (Codex's v11 critique: Python's lock opened
    # while the narration was still explaining the restriction). A later beat performs the change.
    hold = bool(rig and shot['rig'].get('hold'))
    if rig and prev and not hold:
        # The payoff opens on the change itself: a puff where the machine made contact.
        h = layout['hero'];(lx, ly), _ = rig.contacts(h.get('values'), (action, tc))[rig.actions[action].contact]
        poof_at = (h['x'] + lx * h['scale'], h['y'] + ly * h['scale'])
    frames = []
    for f in range(n):
        u = f / max(1, n - 1);pieces = []
        zoom, dx, dy = motif_looks.camera(L['camera'], shot['role'], u, f, n)
        if prev:
            pz, pdx, pdy = motif_looks.camera(L['camera'], prev[0], 1.0, prev[1] - 1, prev[1]);k = ease(min(1.0, f / 10))
            zoom, dx, dy = pz + (zoom - pz) * k, pdx + (dx - pdx) * k, pdy + (dy - pdy) * k
        else:dy += motif_looks.slide_offset(L['transition'], f)
        cam = lambda markup: camera(markup, zoom, cx, cy, dx, dy)
        if dy > 0:pieces.append(f'<rect width="720" height="1280" fill="{L["transition_colour"]}"/>')
        pieces.append(cam(room['draw'](c)))
        for k, item in enumerate(layout.get('dressing', [])):
            if item['layer'] == 'back':
                # Round 8 (2026-10-10): the references' frames never settle, so every prop keeps a slow
                # life of its own: hanging and sky pieces swing and drift, floor pieces rock on their base.
                mount = PROPS[item['prop']].mount;air = mount in ('ceiling', 'sky')
                sway = (2.4 if air else 1.1) * math.sin(f * (.09 if air else .075) + item['x'] * .01 + k)
                pivot_y = item['y'] if mount == 'floor' else item['box'][1];drift = 12 * math.sin(f * .025 + k) if mount == 'sky' else 0
                body = f'<g transform="translate({drift:.2f} 0) rotate({sway:.2f} {item["x"]:.1f} {pivot_y:.1f})">{place(PROPS[item["prop"]].render(c), item["x"], item["y"], item["scale"])}</g>'
                pieces.append(cam(boil(body, f, f'{shot["id"]}-d{k}', .8)))
        if rig:
            if shot['role'] == 'setup':t = tc * ease(min(1.0, u / .92))
            elif shot['role'] == 'hook':t = min(1.0, .35 * tc + ease(min(1.0, u / .6)))  # already moving at frame 0
            else:t = tc + (1 - tc) * min(1.0, u / .55)
            if hold:t = 0.0
            h = layout['hero'];breathe = 1 + (.018 if shot['role'] == 'payoff' else .01) * math.sin(f * .21)
            hero = place(rig.render(h['values'] or None, (action, t), shot['palette']), h['x'], h['y'], h['scale'] * breathe)
            rock = .7 * math.sin(f * .13) + (1.6 * math.sin(f * .9) * (math.sin(f * .11) > .3) if hold else 0)  # a held machine strains against itself
            hero = f'<g transform="rotate({rock:.3f} {h["x"]:.1f} {h["y"]:.1f})">{hero}</g>'  # the machine rocks on its base
            if brand and shot['role'] != 'hook':
                from motif_brand import sticker
                # The product's mark on the machine: the frame names its subject without the caption.
                wob = 3 * math.sin(f * .3)
                mark = f'<g transform="translate({sticker_at[0]:.1f} {sticker_at[1]:.1f})">{sticker(brand, 92, -8 + wob)}</g>'
                hero += mark if prev else pop_in(mark, f, 2, sticker_at)
            hero_at = len(pieces);pieces.append(cam(boil(hero, f, f'{shot["id"]}-hero', .6)))
            if prev and shot['role'] == 'payoff' and poof_at:pieces.append(cam(poof(*poof_at, f, c, h['scale'] * 1.1)))
        b = layout['bot'];bot = shot['bot']
        if rig:
            side = b.get('side', -1 if b['x'] < 360 else 1)
            pose, face, bdx, bdy, squash, cycle = bot_motion(shot['role'], u, f, n, tc, side, entering=not prev)
            face = bot['face'] if shot['role'] == 'payoff' and face == 'excited' and bot.get('face') else face
            body = dressed_bot(b['x'] + bdx, b['y'] + bdy, b['scale'], face, pose, bot['costume'], shot['palette'], flip=side > 0, cycle=cycle, phase=f / 10, head=round(4 * math.sin(f * .3)))
            if squash != 1:body = f'<g transform="translate({b["x"]:.1f} {b["y"]:.1f}) scale({2 - squash:.3f} {squash:.3f}) translate({-b["x"]:.1f} {-b["y"]:.1f})">{body}</g>'
            if b.get('behind'):pieces.insert(hero_at, cam(body))  # squeezed onto a wide machine: peeks from behind it
            else:pieces.append(cam(body))
        elif grammar == 'big-bot':
            hop = abs(math.sin(f * .18)) * 18;tilt = 4 * math.sin(f * .15)
            pieces.append(cam(dressed_bot(360 if not brand else 540, 1050 - hop, .5 if not brand else .42, bot['face'], bot['pose'], bot['costume'], shot['palette'], angle=tilt)))
        elif grammar in ('number', 'card'):
            hop = abs(math.sin(f * .22)) * 16
            pieces.append(cam(dressed_bot(150 if grammar == 'card' else 560, 1030 - hop, .38, bot['face'], 'pointing', bot['costume'], shot['palette'], flip=grammar == 'number')))
        else:
            hop = abs(math.sin(f * .22)) * 26
            pieces.append(cam(dressed_bot(360, 1010 - hop, .38, bot['face'], bot['pose'], bot['costume'], shot['palette'])))
        for k, m in enumerate(members):
            bounce = abs(math.sin(f * .25 + k)) * 14
            pieces.append(cam(pop_in(dressed_bot(m['x'], m['y'] - bounce, m['s'], m['face'], 'celebrating' if (f // 8 + k) % 2 else m['pose'], m['costume'], shot['palette'], m['angle'], m['flip']), f, 3 + k, (m['x'], m['y']))))
        for k, item in enumerate(layout.get('dressing', [])):
            if item['layer'] == 'front':pieces.append(cam(boil(place(PROPS[item['prop']].render(c), item['x'], item['y'], item['scale']), f, f'{shot["id"]}-f{k}', .8)))
        if brand and shot['role'] in ('hook', 'cta'):
            from motif_brand import badge
            # Hook: the product is the first thing on screen (visible at frame 0, then settles).
            big = shot['role'] == 'hook' and not shot.get('insert') and not rig;size = 300 if big else 190
            if shot['role'] == 'hook' and rig:bx, by = min(600, max(120, sticker_at[0])), max(400, sticker_at[1] - 20);size = 150  # over Bot's lane, clear of the machine
            elif big:bx, by = (300, 600) if grammar == 'big-bot' else (360, 560)
            elif shot['role'] == 'hook':bx, by = 170, 840
            elif grammar == 'card':bx, by = 580, 820
            else:bx, by = 170, 720
            s_ = 1.0 if f > 10 else .9 + .1 * ease(f / 10) + .06 * math.sin(f / 10 * math.pi)
            spin = 4 * math.sin(f * .12)
            pieces.append(cam(boil(f'<g transform="translate({bx} {by + 6 * math.sin(f * .15):.1f}) scale({s_:.4f})">{badge(brand, size, c, angle=spin)}</g>', f, f'{shot["id"]}-brand', .5)))
        if shot.get('insert') and (shot['role'] != 'payoff' or u > .25):
            start = .25 if shot['role'] == 'payoff' else 0;local = (u - start) / (1 - start)
            piece = insert_piece(shot['insert'], shot['palette'], local, int(local * (n - 1)))
            if grammar == 'number' and shot['role'] == 'hook':piece = f'<g transform="translate(360 560) scale(1.45) translate(-360 -400)">{piece}</g>'
            elif grammar == 'card' and shot['role'] == 'cta':piece = f'<g transform="translate(420 520) scale(1.25) translate(-360 -420)">{piece}</g>'
            pieces.append(piece)
        text = headlines[min(len(headlines) - 1, int(u * len(headlines)))]
        # After a cut the headline is already mostly in (the references' title is on screen at the cut);
        # a continuing shot's new headline gets its full entrance.
        pieces.append(motif_looks.headline(L['headline'], text, c, f if prev else f + 3))
        overlay = ('' if prev else motif_looks.transition_in(L['transition'], f, L['transition_colour'])) + ('' if continued else motif_looks.transition_out(L['transition'], f, n, L['transition_colour']))
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
        {'glob': 'assets/sfx/*', 'origin': 'procedural-seeded', 'generator': 'motif_ui_production.make_sounds (seeded filtered noise and resonators)'},
        {'glob': 'assets/music/*', 'origin': 'procedural-seeded', 'generator': 'motif_music.bed (synthesised chords, bass, arpeggio and drums; no samples)'}]})


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
        i = shots.index(shot);same = lambda a, b: a['beat'] == b['beat'] and a['room'] == b['room'] and a.get('rig') == b.get('rig')
        prev = (shots[i - 1]['role'], shots[i - 1]['frames']) if i and same(shots[i - 1], shot) else None
        continued = i + 1 < len(shots) and same(shots[i + 1], shot)
        frames = shot_frames(shot, layout, seed + shot['start_frame'], plan.get('look', 'paper-craft'), plan.get('brand'), prev, continued)
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
    music = False
    if plan.get('music', True):
        # An original bed under the voice (the references all run music; review item 6).
        from motif_music import bed
        music = bed(project / 'assets/music/bed.wav', duration, plan.get('look', 'paper-craft'), plan.get('seed', 0))
        music.update({'file': 'assets/music/bed.wav', 'volume': MUSIC_VOLUME})
    write(project / 'audio-plan.json', {'duration': voice_duration, 'narration': 'assets/voice/narration-af-nova.wav', 'sfx_cues': cues, 'music': music, 'subjective_listening': 'not assessed'})
    write_index(project, frames_index, duration, voice_duration, 0)
    write(project / 'shots.json', [{k: v for k, v in s.items()} for s in shots])
    write(project / 'set-layouts.json', {f'{k[0]}': v for k, v in layouts.items()})
    write(project / 'finish-lights.json', lights)
    write(project / 'caption-events.json', groups)
    return {'duration': duration, 'shots': len(shots), 'frames_index': frames_index}


# Pipeline ------------------------------------------------------------------------------

def codex_available():
    return shutil.which('codex') is not None


def run(brief_path, out_root=None, allow_draft=False, stub_voice=False, render=False, python=None, finish=True, avoid_looks=()):
    from motif_evidence import declare
    from motif_pacing import check as pacing, check_plan
    from motif_provenance import check as provenance
    from motif_reel_script import script_record, validate
    import motif_sets as ms
    brief = read(brief_path);record = {'brief': str(brief_path), 'stages': []}
    stage = lambda name, status, **kw: record['stages'].append({'stage': name, 'status': status, **kw})
    errors = validate(brief)
    if errors:raise ValueError('script: ' + '; '.join(errors))
    root = Path(out_root) if out_root else ROOT / 'videos/productions';project = root / brief['slug']
    if project.exists():raise FileExistsError(f'{project} exists; choose a fresh slug')
    project.mkdir(parents=True);write(project / 'brief.json', brief)
    script = script_record(brief);write(project / 'reel-script.json', script);stage('script', 'PASS', hook=script['hook'], hook_alternates=script['hook_alternates'])
    plan = plan_reel(brief, allow_draft, avoid_looks);errs, requests = validate_plan(plan, allow_draft)
    if requests:write(project / 'library-requests.json', requests)
    if errs:stage('plan', 'FAIL', errors=errs);write(project / 'reel-record.json', record);raise ValueError('plan: ' + '; '.join(errs))
    write(project / 'production-plan.json', plan);declare(project, 'original-film', 'motif_reel.run');stage('plan', 'PASS', look=plan['look'], shots=sum(len(b['shots']) for b in plan['beats']), warnings=plan['warnings'])
    from motif_semantics import sound_off
    meaning = sound_off(plan, brief);write(project / 'sound-off.json', meaning)
    stage('sound-off', meaning['status'], failures=meaning['failures'])
    if meaning['status'] != 'PASS':write(project / 'reel-record.json', record);raise ValueError('sound-off: ' + '; '.join(meaning['failures']))
    prepare(project, brief)
    spans, voice_duration = voice(project, [(b['id'], b['narration']) for b in plan['beats']], brief.get('voice', 'af_nova'), stub_voice, python)
    stage('voice', 'STUB' if stub_voice else 'PASS', duration=round(voice_duration, 3))
    timing = {i: (s, e) for i, s, e in spans}
    beats_t = []
    for s in schedule(json.loads(json.dumps(plan)), spans, voice_duration):
        a, n = s['start_frame'] / FPS, s['frames'] / FPS;metaphor = s['rig']['id'] if s['rig'] else s['role']
        heads = [s['headline'], s.get('headline_b')] if s.get('split_headline') else [s['headline']]
        for k, h in enumerate(heads):beats_t.append({'id': f'{s["id"]}.{k}', 'start': round(a + n * k / len(heads), 3), 'end': round(a + n * (k + 1) / len(heads), 3), 'headline': h, 'metaphor': metaphor, 'cut_before': True})
    measured = validate(brief, measured=voice_duration + TAIL)
    if measured:stage('voice-runtime', 'FAIL', errors=measured);write(project / 'reel-record.json', record);raise ValueError('voice: ' + '; '.join(measured))
    structure = check_plan(beats_t, beats_t[-1]['end'])
    stage('structure', 'FAIL' if structure else 'PASS', failures=structure, critics='live Codex structure/direction critics ' + ('run separately' if codex_available() else 'not available in this environment; not run'))
    if structure:write(project / 'reel-record.json', record);raise ValueError('structure: ' + '; '.join(structure))
    compiled = compile_reel(project, plan, spans, voice_duration, brief.get('seed', 0));stage('compile', 'PASS', duration=round(compiled['duration'], 3), shots=compiled['shots'])
    rough = pacing(project)
    from motif_frame_snapshot import at_times, snapshot
    mids = [f['start'] + f['duration'] * .7 for f in compiled['frames_index']]
    pngs = snapshot(project, at_times(project, mids), project / 'review/rough', size=(360, 640))
    empty = ms.check_frames(pngs)
    stage('rough', 'PASS' if rough['status'] == 'PASS' and empty['status'] == 'PASS' else 'FAIL', pacing=rough, empty_field=empty)
    stage('critics', 'NOT_RUN', reason='live Codex story/visual critics need the Codex CLI' if not codex_available() else 'run motif_concept critics on review/rough')
    final = project
    if finish:
        final = project.with_name(project.name + '-finished')
        from motif_finish import apply
        from motif_looks import finish_style
        style = finish_style(plan['look'], project / 'finish-style.json')
        apply(project, final, style_path=style, lights_path=project / 'finish-lights.json');stage('finish', 'PASS', project=str(final), style=f'motif-finish-v1+{plan["look"]}')
    origin = provenance(final);gate = pacing(final)
    stage('gate', 'PASS' if origin['status'] == 'PASS' and gate['status'] == 'PASS' else 'FAIL', provenance={k: origin[k] for k in ('status', 'checked', 'unknown', 'reference_derived', 'rejected')}, pacing=gate['status'])
    if render:
        from motif_frame_render import render as frame_render
        out = final / 'renders/review.mp4';result = frame_render(final, out, DELIVERY)
        from motif_motion import measure
        motion = measure(out);write(final / 'motion.json', motion)
        stage('render', 'PASS', file=str(out), frames=result['frames'], size=list(DELIVERY))
        stage('motion', motion['status'], **{k: motion[k] for k in ('median_moving_share', 'floor', 'longest_static_s')})
    stage('review', 'REVIEW_REQUIRED', note='Mayowa reviews on phone; technical passes do not approve the film')
    write(project / 'reel-record.json', record)
    if final != project:write(final / 'reel-record.json', record)
    return record


def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n')[0]);sub = p.add_subparsers(dest='cmd', required=True)
    r = sub.add_parser('run');r.add_argument('--brief', type=Path, required=True);r.add_argument('--out', type=Path)
    r.add_argument('--allow-draft', action='store_true', help='use DRAFT library entries (review renders before approval)')
    r.add_argument('--stub-voice', action='store_true');r.add_argument('--render', action='store_true');r.add_argument('--no-finish', action='store_true')
    r.add_argument('--tts-python', type=Path, help='Python with kokoro-onnx for hyperframes tts')
    pl = sub.add_parser('plan');pl.add_argument('--brief', type=Path, required=True);pl.add_argument('--allow-draft', action='store_true')
    a = p.parse_args()
    if a.cmd == 'plan':
        plan = plan_reel(read(a.brief), a.allow_draft);errs, _ = validate_plan(plan, a.allow_draft);print(json.dumps({'plan': plan, 'errors': errs}, indent=2));raise SystemExit(1 if errs else 0)
    record = run(a.brief, a.out, a.allow_draft, a.stub_voice, a.render, a.tts_python, not a.no_finish)
    print(json.dumps(record['stages'], indent=2))


if __name__ == '__main__':
    main()
