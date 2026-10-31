"""Atelier contracts: schema validation plus the rules a schema cannot express.

Every function returns a list of human-readable errors; an empty list passes.
These checks prove a record is complete and consistent. They never certify
that a premise is good, a shot reads, or a claim is true: those are reviews.
"""
import re
from pathlib import Path

from jsonschema import Draft202012Validator

from .project import ROOT, read

CONTRACTS = ROOT / 'atelier/contracts'
MEDIA = {'.svg', '.png', '.webp', '.jpg', '.jpeg', '.wav', '.woff2', '.ttf', '.otf'}
SOURCE_EXT = MEDIA | {'.js', '.json', '.md', '.txt', '.css'}
SOURCE_MAX_BYTES = 8 * 1024 * 1024
# Linting, not a sandbox: the real boundary is the Chromium page with every
# non-local request aborted and no Python execution of project files.
FORBIDDEN_JS = [(r'\bfetch\s*\(', 'fetch'), (r'XMLHttpRequest', 'XMLHttpRequest'), (r'\bimport\s*\(', 'dynamic import'),
                (r'\beval\s*\(', 'eval'), (r'new\s+Function\b', 'new Function'), (r'WebSocket', 'WebSocket'), (r'\bWorker\s*\(', 'Worker'),
                (r'https?://', 'remote URL'), (r'Math\.random', 'Math.random (use env.rng)'), (r'Date\.now|new\s+Date\s*\(|performance\.now', 'clock'),
                (r'requestAnimationFrame|setTimeout|setInterval', 'timers (render is seek-driven)'), (r'localStorage|indexedDB|document\.cookie', 'storage')]

ROLES = {
    'proof': {'dims': {'action_reads': 'the hardest action reads at phone size: cause, contact and result are visible',
                       'performance': 'poses, timing and reactions sell the action (not a slide across a still)',
                       'feasible_look': 'the representative artwork holds up at 360x640'},
              'mandatory': ['action_reads', 'performance', 'feasible_look']},
    'story': {'dims': {'opening_promise': 'the opening establishes a promise, situation or feeling worth watching',
                       'progression': 'each part develops or complicates it; nothing is a list item',
                       'payoff': 'the ending delivers an intentional result that answers the opening',
                       'cause_before_effect': 'important causes are shown before their consequences',
                       'clarity_normal_speed': 'a first-time viewer follows it at normal speed',
                       'picture_sound_link': 'narration/dialogue and picture tell one story (N/A only for a declared silent film)'},
              'mandatory': ['opening_promise', 'progression', 'payoff', 'cause_before_effect', 'clarity_normal_speed', 'picture_sound_link'],
              'playback_only': ['clarity_normal_speed']},
    'visual': {'dims': {'focal_hierarchy': 'the thing that matters now commands attention',
                        'identity_continuity': 'characters and objects keep identity, scale and materials',
                        'composition': 'staging and framing are intentional for a vertical phone',
                        'readable_action': 'meaningful actions are legible; contacts, grips, landings and releases hold up',
                        'motion_performance': 'timing, anticipation, reactions and stillness serve the story, not busyness',
                        'style_coherence': 'one deliberate visual language throughout',
                        'phone_readability': 'essential meaning survives at phone size',
                        'technical_defects': 'no glitches, popping, tearing, unintended clipping or broken frames'},
               'mandatory': ['focal_hierarchy', 'identity_continuity', 'composition', 'readable_action', 'motion_performance',
                             'style_coherence', 'phone_readability', 'technical_defects']},
    'factual': {'dims': {'claims_match_sources': 'each ledger claim is supported by its cited source',
                         'narration_matches_ledger': 'every consequential spoken or shown claim maps to a ledger entry',
                         'dramatization_labeled': 'exaggeration and invention are identified and do not mislead'},
                'mandatory': ['claims_match_sources', 'narration_matches_ledger', 'dramatization_labeled']},
}
# A dimension listed as playback_only cannot be established from ordered frames. When the reviewer had no moving
# playback, NOT_ASSESSED there is DEFERRED to the person's phone viewing: never PASS, surfaced in the status and
# the delivery record, and any FAIL still blocks. Every other NOT_ASSESSED blocks.
# Only these may be declared NOT_APPLICABLE in direction.applicability, and only for a reason the intent establishes.
DECLARABLE_NA = {'picture_sound_link', 'performance'}


def schema(name):
    return Draft202012Validator(read(CONTRACTS / f'{name}.schema.json'))


def schema_errors(name, value):
    return [f'{name}: {"/".join(map(str, e.absolute_path)) or "<root>"}: {e.message}' for e in schema(name).iter_errors(value)]


def words(text):
    return set(re.findall(r'[a-z]{4,}', text.lower()))


def brief(value):
    return schema_errors('brief', value)


def concepts(value, brief_value, budgets):
    errors = schema_errors('concepts', value)
    if errors:return errors
    premises = value['premises'];ids = [p['id'] for p in premises]
    if len(premises) < budgets['concepts']:errors.append(f'concepts: {budgets["concepts"]} premises required by the exploration budget, got {len(premises)}')
    if len(set(ids)) != len(ids):errors.append('concepts: premise ids must be unique')
    if value['chosen'] not in ids:errors.append('concepts: chosen premise is not one of the premises')
    for i, a in enumerate(premises):
        for b in premises[i + 1:]:
            sa, sb = words(a['central_action'] + ' ' + a['payoff']), words(b['central_action'] + ' ' + b['payoff'])
            if sa and sb and len(sa & sb) / len(sa | sb) > .6:errors.append(f'concepts: {a["id"]} and {b["id"]} are near-duplicates, not different premises')
    declared = brief_value.get('classification', 'unspecified')
    if declared != 'unspecified' and value['classification'] != declared:errors.append(f'concepts: classification {value["classification"]} differs from the brief ({declared})')
    return errors


def direction(value, classification):
    errors = schema_errors('direction', value)
    if errors:return errors
    shots = [s['id'] for s in value['shots']]
    if len(set(shots)) != len(shots):errors.append('direction: shot ids must be unique')
    if value['hardest_shot']['shot'] not in shots:errors.append('direction: hardest_shot names an unknown shot')
    claims = value.get('claims', [])
    if classification in ('factual', 'mixed'):
        if not claims:errors.append('direction: a factual or mixed film needs a claim/source ledger')
        for c in claims:
            if c['kind'] in ('observation', 'inference') and not (c.get('source_url') and c.get('excerpt')):
                errors.append(f'direction: claim {c["id"]} ({c["kind"]}) needs source_url and a source excerpt')
        if classification == 'mixed' and not value.get('dramatization'):errors.append('direction: a mixed film must list its consequential dramatization')
    for dim, reason in value.get('applicability', {}).items():
        if dim not in DECLARABLE_NA:errors.append(f'direction: {dim} cannot be declared not applicable')
    if 'picture_sound_link' in value.get('applicability', {}) and value['audio']['narration'] != 'none':
        errors.append('direction: picture_sound_link is only not applicable to a film declared without narration or dialogue')
    if 'performance' in value.get('applicability', {}) and value['style_sheet']['characters']:
        errors.append('direction: performance is only not applicable to a film without characters')
    for c in value['style_sheet']['characters']:
        if c.get('canonical_asset') and c['new_design']:errors.append(f'direction: {c["id"]} cannot be both a new design and a canonical asset')
    return errors


def resolve_at(film, at, offset=0):
    if isinstance(at, int):return at + offset
    if at not in film['moments']:raise ValueError(f'unknown moment {at!r}')
    return film['moments'][at] + offset


def source_files(source):
    """Static checks on project source before anything executes it."""
    errors = []
    for path in sorted(Path(source).rglob('*')):
        rel = path.relative_to(source).as_posix()
        if path.is_symlink():errors.append(f'source: symlink not allowed: {rel}');continue
        if not path.is_file():continue
        if path.suffix.lower() not in SOURCE_EXT:errors.append(f'source: file type not allowed: {rel}')
        if path.stat().st_size > SOURCE_MAX_BYTES:errors.append(f'source: file too large: {rel}')
        if path.suffix == '.js':
            text = path.read_text(errors='replace')
            for pattern, name in FORBIDDEN_JS:
                if re.search(pattern, text):errors.append(f'source: {rel} uses {name}')
        if path.suffix == '.svg' and re.search(r'<script|(?:href|src)\s*=\s*"https?:', path.read_text(errors='replace')):
            errors.append(f'source: {rel} embeds scripts or remote references')
    return errors


def film(value, direction_value, brief_value, source, complete=True):
    """complete=False checks only what the proof render needs."""
    errors = schema_errors('film', value)
    if errors:return errors
    frames = value['frames'];source = Path(source)
    if not (source / value['entry']).is_file():errors.append(f'film: entry {value["entry"]} missing')
    for name, rel in list(value.get('images', {}).items()) + [(f['family'], f['path']) for f in value.get('fonts', [])]:
        if not (source / rel).is_file():errors.append(f'film: asset {name} -> {rel} missing (an unavailable asset is an authoring task, not a substitution)')
    for name, frame in value['moments'].items():
        if frame >= frames:errors.append(f'film: moment {name} at frame {frame} is past the end ({frames})')
    p = value['proof']
    if not 0 <= p['start'] < p['end'] <= frames or p['end'] - p['start'] < 12:errors.append('film: proof range must be at least 12 frames inside the film')
    if p['shot'] != direction_value['hardest_shot']['shot']:errors.append('film: proof must cover the direction\'s hardest shot')
    if not complete:return errors
    shots = sorted(value['shots'], key=lambda s: s['start']);cursor = 0
    for s in shots:
        if s['start'] != cursor or s['end'] <= s['start']:errors.append(f'film: shots must tile the film without gaps or overlaps (at {s["id"]})')
        cursor = s['end']
    if cursor != frames:errors.append(f'film: shots end at {cursor}, film has {frames} frames')
    planned = {s['id'] for s in direction_value['shots']}
    missing = planned - {s['id'] for s in value['shots']}
    if missing:errors.append(f'film: direction shots not in the film: {sorted(missing)}')
    sound = value['sound'];narrated = direction_value['audio']['narration'] != 'none'
    if narrated and not sound['narration']:errors.append('film: direction declares narration but the film has none')
    if not narrated and sound['narration']:errors.append('film: direction declares no narration but the film has lines')
    ids = [line['id'] for line in sound['narration']]
    if len(set(ids)) != len(ids):errors.append('film: narration ids must be unique')
    try:
        starts = [resolve_at(value, line['at']) for line in sound['narration']]
        if starts != sorted(starts):errors.append('film: narration lines must be in time order')
        for cue in sound['sfx']:
            frame = resolve_at(value, cue['at'], cue.get('offset', 0))
            if not 0 <= frame < frames:errors.append(f'film: sound cue at {cue["at"]} falls outside the film')
            if bool(cue.get('recipe')) == bool(cue.get('file')):errors.append(f'film: sound cue at {cue["at"]} needs exactly one of recipe or file')
    except ValueError as e:errors.append(f'film: {e}')
    claims = {c['id'] for c in direction_value.get('claims', [])}
    for line in sound['narration']:
        for c in line.get('claims', []):
            if c not in claims:errors.append(f'film: line {line["id"]} cites unknown claim {c}')
    spoken = ' '.join(line['text'] for line in sound['narration'])
    for locked in brief_value.get('locked_wording', []):
        if locked not in spoken:errors.append(f'film: locked wording is not spoken verbatim: {locked!r}')
    if sound['music']['kind'] == 'notes' and not sound['music'].get('tracks'):errors.append('film: note music needs tracks')
    return errors


def ledger(value, source_tree):
    """Every source file is identified with origin, rights, version and use; hashes match."""
    errors = schema_errors('asset-ledger', value)
    if errors:return errors
    entries = {a['path']: a for a in value['assets']}
    if len(entries) != len(value['assets']):errors.append('ledger: duplicate paths')
    for rel, digest in source_tree.items():
        if rel == 'asset-ledger.json':continue
        entry = entries.get(rel)
        if not entry:errors.append(f'ledger: {rel} is not recorded (identity, origin, rights, version, use)');continue
        if entry['sha256'] != digest:errors.append(f'ledger: {rel} changed since it was recorded; refresh the ledger and bump its version')
        if entry['origin'] == 'licensed' and 'licen' not in entry['rights'].lower():errors.append(f'ledger: {rel} is licensed but names no licence')
        if entry['origin'] == 'reused-motif-asset' and not entry.get('registry_id'):errors.append(f'ledger: {rel} reuses a Motif asset without its registry id')
    for rel in entries:
        if rel not in source_tree:errors.append(f'ledger: {rel} is recorded but missing from source')
    return errors


def review(value, request, request_sha):
    """Gate one review response. Returns (status, blocking issues, deferred dimensions). Never upgrades a missing assessment."""
    errors = schema_errors('review', value)
    if errors:return 'INVALID', errors, []
    role = request['role'];spec = ROLES[role]
    if value['role'] != role:errors.append(f'review: response role {value["role"]} answers a {role} request')
    if value['request_sha256'] != request_sha:return 'STALE', ['review: response is bound to a different request (changed source, audio, render or direction)'], []
    r = value['reviewer']
    if role != 'proof' and (r['kind'] == 'builder' or r['independence'] == 'builder-self-inspection'):
        errors.append('review: a builder self-description cannot pass a story, visual or factual gate')
    allowed_na = request.get('not_applicable', {})
    blocking, deferred = [], []
    for dim in spec['dims']:
        got = value['dimensions'].get(dim)
        if not got:blocking.append(f'{dim}: NOT_ASSESSED (missing)');continue
        status = got['status']
        if status == 'NOT_APPLICABLE':
            if dim not in allowed_na:blocking.append(f'{dim}: NOT_APPLICABLE was not declared by the project intent before review')
        elif status == 'NOT_ASSESSED' and dim in spec.get('playback_only', ()) and value['reviewer']['playback'] != 'moving':
            deferred.append({'dimension': dim, 'status': 'NOT_ASSESSED', 'deferred_to': 'human phone playback', 'note': got['note']})
        elif status != 'PASS':blocking.append(f'{dim}: {status}: {got["note"]}')
    for issue in value['critical_issues']:blocking.append(f'critical: {issue["where"]}: {issue["problem"]}')
    if role == 'proof' and value.get('verdict') != 'PROCEED':blocking.append(f'proof verdict {value.get("verdict", "missing")}')
    if errors:return 'INVALID', errors, []
    return ('FAIL', blocking, deferred) if blocking else ('PASS', [], deferred)
