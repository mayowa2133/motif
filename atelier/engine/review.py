"""Atelier reviews: evidence packs, hash-bound requests, reviewer backends.

A request binds the brief, direction, source tree, audio and the encoded
render (bytes and a frame fingerprint). Evidence is decoded from the encoded
file, not from the builder's intermediate frames. A response is valid only for
the exact request it names; any change upstream makes it STALE.

Backends:
  codex    the existing Codex CLI (motif_direct.model_call: read-only, data
           only, images attached). Used when the CLI is installed and signed in.
  handoff  the request and a prompt are written to reviews/; an independent
           reviewer (a separate model session or a person) writes the response.
           The orchestrator waits; it never fills in a review itself.

Frames are not playback. Reviewers see ordered frames and dense strips around
key moments, plus audio measurements and timed narration text; they cannot
hear the mix. Requests say so, and responses must disclose their own limits.
"""
import json
import os
from pathlib import Path

from .contracts import ROLES, CONTRACTS
from .playback import extract, sheet, thumb, PREVIEW
from .project import ROOT, read, sha, sha_value, write

SCHEMA_REL = 'atelier/contracts/review.schema.json'
INSTRUCTIONS = (
    'You are an independent reviewer for a short vertical film made in Motif Atelier. You did not make it. '
    'Judge only the rendered evidence listed here against the stated intent: do not read the project source, builder notes or earlier reviews. '
    'Be specific and critical; a polite PASS on weak work defeats the purpose. For every dimension give PASS, FAIL or NOT_ASSESSED with a one-sentence note '
    'citing times or frames. Use NOT_ASSESSED whenever the evidence cannot establish the dimension (for example motion smoothness between sampled frames, or how the mix sounds). '
    'NOT_APPLICABLE is allowed only for the dimensions listed under not_applicable, with that reason. List every problem that should block release as a critical issue '
    'with the smallest fix. Disclose your sampling limits. Do not reward effort, technique or a description of intentions; reward what a first-time phone viewer would see.')


def _rel(path, home):
    return Path(path).resolve().relative_to(home).as_posix()


def evidence(project, video, film, role, out, frames=None):
    """Decode ordered frames and dense strips from the encoded preview. Returns evidence entries and a fingerprint."""
    fps = film['fps'];a, b = frames or (0, film['frames']);out = Path(out);home = project.root
    shots = sorted(film['shots'], key=lambda s: s['start'])
    shot_of = lambda n: next((s['id'] for s in shots if s['start'] <= n < s['end']), '?')
    step = 2 if role == 'proof' else max(1, fps // 2)
    order = list(range(a, b, step));images = extract(video, [n - a for n in order])
    entries = [{'path': _rel(sheet(images, [f'{n / fps:5.2f}s f{n} {shot_of(n)}' for n in order], out / 'ordered-frames.png', cols=8 if role == 'proof' else 10, width=135), home),
                'what': f'ordered frames every {step} frames ({step / fps:.2f}s), in playback order, labelled time / frame / shot'}]
    keys = film.get('key_moments') or list(film['moments'])
    if role == 'proof':keys = [k for k in keys if a <= film['moments'][k] < b]
    picks = sorted({min(max(s['start'] + (s['end'] - s['start']) // 2, a), b - 1) for s in shots if s['end'] > a and s['start'] < b})
    for name in keys:
        m = film['moments'][name];strip = [n for n in range(m - 8, m + 9, 2) if a <= n < b]
        if not strip:continue
        imgs = extract(video, [n - a for n in strip])
        entries.append({'path': _rel(sheet(imgs, [f'f{n}{" *" if n == m else ""}' for n in strip], out / f'strip-{name}.png', cols=len(strip), width=150), home),
                        'what': f'dense strip around moment "{name}" (frame {m}, {m / fps:.2f}s): every 2nd frame from -8 to +8'})
    full = extract(video, [n - a for n in picks])
    for n, img in zip(picks, full):
        path = out / f'phone-f{n:05d}.png';img.save(path)
        entries.append({'path': _rel(path, home), 'what': f'full preview frame at phone size 360x640, shot {shot_of(n)} midpoint ({n / fps:.2f}s)'})
    for e in entries:e['sha256'] = sha(home / e['path'])
    sample = sorted(set(order[::max(1, len(order) // 12)] + [film['moments'][k] for k in keys if a <= film['moments'][k] < b]))
    finger = {str(n): thumb(img) for n, img in zip(sample, extract(video, [n - a for n in sample]))}
    return entries, finger


def intent(project, role, film):
    brief = read(project.dir / 'brief.json');direction = read(project.dir / 'direction.json');concepts = read(project.dir / 'concepts.json')
    chosen = next(p for p in concepts['premises'] if p['id'] == concepts['chosen'])
    value = {'idea': brief['idea'], 'audience': brief.get('audience'), 'classification': concepts['classification'], 'intended_effect': brief.get('intended_effect'),
             'premise': {k: chosen[k] for k in ('title', 'opening_image', 'audience_hook', 'central_action', 'complication', 'payoff')},
             'logline': direction['logline'], 'opening_promise': direction['opening_promise'], 'ending': direction['ending'],
             'style': direction['style_sheet']['look'], 'audio_intent': direction['audio'],
             'shot_plan': [{k: s[k] for k in ('id', 'purpose', 'sees') if k in s} | {'frames': next(([f['start'], f['end']] for f in film['shots'] if f['id'] == s['id']), None)} for s in direction['shots']]}
    if role == 'proof':value['hardest_shot'] = direction['hardest_shot']
    if role == 'factual':value['claims'] = direction.get('claims', []);value['dramatization'] = direction.get('dramatization', [])
    return value


def request(project, role, binding, entries, film, extra=None):
    """Write reviews/<role>-request.json (+ prompt). Returns (request, sha)."""
    direction = read(project.dir / 'direction.json');spec = ROLES[role]
    value = {'schema': 'motif-atelier-review-request/1', 'role': role, 'project': project.slug, 'project_id': project.state['project_id'], 'approach_id': direction['approach_id'],
             'dimensions': spec['dims'], 'mandatory': spec['mandatory'],
             'not_applicable': {k: v for k, v in direction.get('applicability', {}).items() if k in spec['dims']},
             'intent': intent(project, role, film), 'binding': binding, 'evidence': entries, 'evidence_root': str(project.root),
             'playback_available': False,
             'limits': 'Ordered decoded frames and dense strips only; no moving playback and no listening. Motion between samples and the sound of the mix cannot be judged from this evidence.',
             'instructions': INSTRUCTIONS, 'response_path': f'reviews/{role}.json', 'response_schema': SCHEMA_REL, **(extra or {})}
    path = project.dir / f'reviews/{role}-request.json';write(path, value);digest = sha(path)
    (project.dir / f'reviews/{role}-request.md').write_text(prompt(project, value, digest))
    return value, digest


def prompt(project, value, digest):
    lines = [f'# {value["role"].title()} review request: {value["project"]}', '', value['instructions'], '',
             f'Write your response as JSON to `{project.dir / value["response_path"]}`, valid against `{ROOT / SCHEMA_REL}`, with',
             f'`"request_sha256": "{digest}"` and `"role": "{value["role"]}"`. Set `reviewer` honestly (kind, id, independence, playback: "ordered-frames").', '',
             '## Intent', '```json', json.dumps(value['intent'], indent=1), '```', '', '## Dimensions (all mandatory)']
    lines += [f'- `{k}`: {v}' for k, v in value['dimensions'].items()]
    if value['not_applicable']:lines += ['', '## Declared not applicable (before production)'] + [f'- `{k}`: {v}' for k, v in value['not_applicable'].items()]
    lines += ['', '## Evidence (open every image)'] + [f'- `{Path(value["evidence_root"]) / e["path"]}`: {e["what"]}' for e in value['evidence']]
    for key in ('audio', 'narration'):
        if key in value:lines += ['', f'## {key.title()}', '```json', json.dumps(value[key], indent=1), '```']
    lines += ['', f'Limits: {value["limits"]}', '']
    return '\n'.join(lines)


def response(project, role):
    path = project.dir / f'reviews/{role}.json'
    return read(path) if path.is_file() else None


def archive(project, role, reason):
    path = project.dir / f'reviews/{role}.json'
    if path.is_file():
        old = read(path);dest = project.dir / f'reviews/history/{role}-{old.get("request_sha256", "unbound")[:12]}.json'
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists():path.replace(dest)
        else:path.unlink()
        project.event('review-archived', role=role, reason=reason, kept=dest.name)


# codex backend ----------------------------------------------------------------

def codex_available():
    try:
        from motif_direct import resolve_codex_cli
        resolve_codex_cli();return True
    except Exception:
        return False


def wire_schema(role):
    """Strict structured-output form: every dimension an explicit required property."""
    dim = {'type': 'object', 'additionalProperties': False, 'required': ['status', 'note', 'evidence'],
           'properties': {'status': {'enum': ['PASS', 'FAIL', 'NOT_ASSESSED', 'NOT_APPLICABLE']}, 'note': {'type': 'string'}, 'evidence': {'type': 'string'}}}
    issue = {'type': 'object', 'additionalProperties': False, 'required': ['dimension', 'where', 'problem', 'smallest_fix'],
             'properties': {k: {'type': 'string'} for k in ('dimension', 'where', 'problem', 'smallest_fix')}}
    dims = {'type': 'object', 'additionalProperties': False, 'required': list(ROLES[role]['dims']), 'properties': {k: dim for k in ROLES[role]['dims']}}
    props = {'dimensions': dims, 'critical_issues': {'type': 'array', 'items': issue}, 'sampling_limits': {'type': 'string'}, 'summary': {'type': 'string'},
             'verdict': {'enum': ['PROCEED', 'REPAIR', 'CHANGE_CONCEPT']}}
    return {'$schema': 'https://json-schema.org/draft/2020-12/schema', 'type': 'object', 'additionalProperties': False, 'required': list(props), 'properties': props}


def codex_review(project, role, value, digest, out_dir):
    """One live, read-only Codex call with the evidence images. Raises on any backend failure (never a PASS)."""
    from motif_direct import backend_config, model_call
    out_dir = Path(out_dir);out_dir.mkdir(parents=True, exist_ok=True)
    schema_path = out_dir / f'{role}-wire.schema.json';write(schema_path, wire_schema(role))
    images = [Path(value['evidence_root']) / e['path'] for e in value['evidence'] if e['path'].endswith('.png')]
    config = backend_config()
    got = model_call(out_dir, f'atelier-{role}', prompt(project, value, digest), os.path.relpath(schema_path, ROOT), config, images)
    project.state['reviewer_calls'] += 1;project.save()
    result = {'request_sha256': digest, 'role': role, 'reviewer': {'kind': 'model', 'id': f'codex-exec {config.get("model") or "default model"}',
              'independence': 'different-provider', 'playback': 'ordered-frames', 'inputs_viewed': [e['path'] for e in value['evidence']], 'tools': 'none (data-only call)'},
              **{k: got[k] for k in ('dimensions', 'critical_issues', 'sampling_limits', 'summary')}}
    if role == 'proof':result['verdict'] = got['verdict']
    write(project.dir / f'reviews/{role}.json', result)
    return result
