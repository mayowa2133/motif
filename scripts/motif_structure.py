"""Macro direction inside motif-gold-v1. Data review, never painted approval."""
import hashlib
import json
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
INPUTS = ('docs/MOTIF_STRUCTURAL_GRAMMAR.md', 'quality/structure-critic/PROMPT.md',
          'schemas/film-structure.schema.json', 'schemas/setup-contract.schema.json',
          'schemas/structure-critic.schema.json', 'quality/structure-examples.json',
          'quality/negative/rowhouse.json', 'scripts/motif_structure.py')


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def policy_hashes():
    return {p: sha(ROOT / p) for p in INPUTS}


def narration(plan):
    return plan.get('script', ' '.join(b['narration'] for b in plan.get('beats', [])))


def check_structure(plan):
    """Integrity checks only. Meaning, clutter and rhythm belong to the critic."""
    if plan.get('quality_mode') != 'motif-gold-v1' or 'film_structure' not in plan:
        raise ValueError('film_structure required for new motif-gold-v1 direction/rough')
    f = plan['film_structure']
    Draft202012Validator(read(ROOT / 'schemas/film-structure.schema.json')).validate(f)
    words = narration(plan).split()
    if not words:
        raise ValueError('structure needs narration')
    chapters, setups, tokens = f['rhetorical_chapters'], f['setups'], f['continuity_tokens']
    beats = plan.get('shots', plan.get('beats', []))

    def unique(items, key):
        ids = [x[key] for x in items]
        if len(ids) != len(set(ids)):
            raise ValueError('duplicate ' + key)
        return {x[key]: x for x in items}

    chapter_map = unique(chapters, 'id')
    setup_map = unique(setups, 'setup_id')
    token_map = unique(tokens, 'id')
    beat_map = unique(beats, 'id')

    def span(s):
        start, end = s['start_word'], s['end_word']
        if not 0 <= start < end <= len(words) or s['text'].split() != words[start:end]:
            raise ValueError('narration_span must quote exact half-open word range')
        return start, end

    def partition(items):
        position = 0
        for item in items:
            start, end = span(item['narration_span'])
            if start != position:
                raise ValueError('narration coverage must be contiguous and ordered')
            position = end
        if position != len(words):
            raise ValueError('structure must cover entire narration')

    partition(chapters)
    partition(setups)
    covered = []
    for index, setup in enumerate(setups):
        if setup['chapter'] not in chapter_map:
            raise ValueError('unknown chapter')
        start, end = span(setup['narration_span'])
        lo, hi = span(chapter_map[setup['chapter']]['narration_span'])
        if not lo <= start < end <= hi:
            raise ValueError('setup outside chapter narration')
        if (setup['planned_reset_after']['kind'] == 'end') != (index == len(setups) - 1):
            raise ValueError('end transition belongs only to last setup')
        if len(setup['continuity_tokens']) != len(set(setup['continuity_tokens'])):
            raise ValueError('duplicate setup token')
        for id_ in setup['beat_ids']:
            if id_ not in beat_map:
                raise ValueError('unknown beat in setup: ' + id_)
            art = beat_map[id_].get('quality', {}).get('art_direction', {})
            if art.get('bot_role') != setup['bot_role'] or art.get('environment_mode', 'physical') != setup['environment_mode']:
                raise ValueError('setup role/environment must agree with shot contract')
        if 'shots' not in plan:
            served = ' '.join(beat_map[id_]['narration'] for id_ in setup['beat_ids'])
            if served.split() != words[start:end]:
                raise ValueError('setup narration does not match referenced beats')
        covered.extend(setup['beat_ids'])
    if covered != [b['id'] for b in beats]:
        raise ValueError('each ordered beat must belong to exactly one setup')
    for setup in setups:
        if not set(setup['continuity_tokens']) <= set(token_map):
            raise ValueError('unknown continuity token')
    for token in tokens:
        used = [s['setup_id'] for s in setups if token['id'] in s['continuity_tokens']]
        if not used or token['setups_used'] != used or token['origin_setup'] != used[0]:
            raise ValueError('token lifecycle must match ordered setup usage')
        changes = [c['setup_id'] for c in token['state_changes']]
        if not set(changes) <= set(used) or changes != sorted(changes, key=used.index):
            raise ValueError('token changes must follow usage order')
    return {'status': 'STRUCTURE_REVIEW_REQUIRED', 'setups': len(setups),
            'chapters': len(chapters), 'scope': 'schema/references only; not semantic approval'}


def planning_context():
    return ('\nFILM STRUCTURE FIRST: derive rhetorical propositions and semantic verbs; '
            'group adjacent propositions by the same visual rule BEFORE choosing beats. '
            'Return film_structure with half-open zero-based whitespace word spans and '
            'ordered beat_ids. Setup IDs are not shot IDs: multiple beats may develop one setup. '
            'Reuse capabilities, not plots. If finite bindings cannot execute the required '
            'worlds, report explicit agent-assisted development; do not collapse them into '
            'one inappropriate metaphor. No shot/duration/reaction quotas.\n' +
            (ROOT / 'docs/MOTIF_STRUCTURAL_GRAMMAR.md').read_text() +
            '\nSTRUCTURE SCHEMA: ' + json.dumps(read(ROOT / 'schemas/film-structure.schema.json')))


def critic_prompt(plan):
    return ((ROOT / 'quality/structure-critic/PROMPT.md').read_text() +
            '\nGRAMMAR:\n' + (ROOT / 'docs/MOTIF_STRUCTURAL_GRAMMAR.md').read_text() +
            '\nINTERNAL BEHAVIORAL EXAMPLES: ' + json.dumps(read(ROOT / 'quality/structure-examples.json')) +
            '\nNEGATIVE BEHAVIOR (not gold art): ' + json.dumps(read(ROOT / 'quality/negative/rowhouse.json')['behavior']) +
            '\nPLAN: ' + json.dumps(plan))


def report_status(plan, report):
    Draft202012Validator(read(ROOT / 'schemas/structure-critic.schema.json')).validate(report)
    codes = set(read(ROOT / 'schemas/structure-critic.schema.json')['properties']['checks']['items']['properties']['check']['enum'])
    checks = report['checks']
    setups = {s['setup_id'] for s in plan['film_structure']['setups']}
    if {c['check'] for c in checks} != codes or len(checks) != len(codes):
        raise ValueError('structure check coverage incomplete')
    assessments = report['setup_assessments']
    if {a['setup_id'] for a in assessments} != setups or len(assessments) != len(setups):
        raise ValueError('structure setup coverage incomplete')
    violations = report['violations']
    failed = {c['check'] for c in checks if c['status'] == 'FAIL'}
    if failed != {v['code'] for v in violations}:
        raise ValueError('structure failure/correction coverage inconsistent')
    for v in violations:
        if not set(v['setup_ids']) <= setups:
            raise ValueError('unknown violation setup')
    for a in assessments:
        implicated = any(a['setup_id'] in v['setup_ids'] for v in violations)
        if (a['status'] == 'FAIL') != implicated:
            raise ValueError('setup failure/correction coverage inconsistent')
    return 'PASS' if all(c['status'] == 'PASS' for c in checks + assessments) else 'REPLAN_REQUIRED'


def structure_review(project, plan, config):
    from motif_direct import model_call
    from motif_quality import write
    project = Path(project)
    check_structure(plan)
    if plan != read(project / 'production-plan.json'):
        raise ValueError('save exact plan before structure review')
    report = model_call(project, 'quality-structure', critic_prompt(plan), 'schemas/structure-critic.schema.json', config)
    status = report_status(plan, report)
    write(project / 'quality-structure-record.json', {
        'status': status, 'plan_sha256': sha(project / 'production-plan.json'),
        'response_sha256': sha(project / 'quality-structure.json'),
        'invocation_sha256': sha(project / 'quality-structure-invocation.json'),
        'policy_hashes': policy_hashes(), 'scope': 'data only; no painted approval'})
    if status != 'PASS':
        raise ValueError('structure REPLAN_REQUIRED: ' + json.dumps(report['violations']))
    return report


def require_structure(project):
    """Fresh live independent assessment; a PASS flag alone is insufficient."""
    project = Path(project)
    plan = read(project / 'production-plan.json')
    check_structure(plan)
    try:
        record = read(project / 'quality-structure-record.json')
        report = read(project / 'quality-structure.json')
        invocation = read(project / 'quality-structure-invocation.json')
        if record['plan_sha256'] != sha(project / 'production-plan.json') or record['response_sha256'] != sha(project / 'quality-structure.json') or record['invocation_sha256'] != sha(project / 'quality-structure-invocation.json') or record['policy_hashes'] != policy_hashes():
            raise ValueError('structure review stale')
        for key, suffix in [('input_sha256', '-input.txt'), ('output_schema_sha256', '-output-schema.json')]:
            if invocation[key] != sha(project / ('quality-structure' + suffix)):
                raise ValueError('structure invocation inputs changed')
        if invocation['exit_code'] or invocation.get('saved_response_used') or invocation.get('model_fallback_used'):
            raise ValueError('structure needs a live independent invocation')
        if record['status'] != 'PASS' or report_status(plan, report) != 'PASS':
            raise ValueError('structure REPLAN_REQUIRED')
    except (FileNotFoundError, KeyError) as error:
        raise ValueError('fresh structure review required before direction/rough') from error
    return record
