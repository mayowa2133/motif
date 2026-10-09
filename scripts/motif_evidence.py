"""Production scope and evidence coverage; extends the existing Gold gate.

This module never renders, watches media, approves artwork or promotes methods.
Historical projects are not rewritten: declare their scope explicitly to resume.
"""
import argparse
import hashlib
import json
import uuid
from pathlib import Path

MODES = ('original-film', 'reference-informed', 'faithful-editable',
         'raster-animatic', 'technical-fixture')
FILM_MODES = MODES[:3]
DIMENSIONS = ('causal-pictures', 'mobile-readability', 'contact',
              'normal-speed-comprehension', 'listening-av')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def declare(project, requested_mode, entrypoint, actual_mode=None):
    project = Path(project)
    actual_mode = actual_mode or requested_mode
    if requested_mode not in MODES or actual_mode not in MODES:
        raise ValueError('explicit supported production mode required')
    if requested_mode != actual_mode:
        raise ValueError('requested production mode cannot be substituted')
    if not entrypoint or not (project / 'brief.json').is_file():
        raise ValueError('entrypoint and saved brief required')
    value = {'version': 1, 'requested_mode': requested_mode,
             'actual_mode': actual_mode, 'entrypoint': entrypoint,
             'brief_sha256': sha(project / 'brief.json'),
             'dimensions': {k: 'UNASSESSED' for k in DIMENSIONS},
             'completion': 'REVIEW_REQUIRED', 'film_approved': False,
             'limitations': ['Frame inspection is not playback or listening.']}
    path = project / 'production-scope.json'
    if path.exists():
        existing = require_scope(project)
        if any(existing[k] != value[k] for k in ('requested_mode', 'actual_mode', 'entrypoint')):
            raise ValueError('existing production scope differs; preserve it')
        return existing
    write(path, value)
    return value


def require_scope(project):
    project = Path(project)
    path = project / 'production-scope.json'
    if not path.is_file():
        raise ValueError('production scope missing; explicitly declare saved project mode')
    value = read(path)
    mode = value.get('requested_mode')
    if value.get('version') != 1 or mode not in MODES or value.get('actual_mode') != mode:
        raise ValueError('invalid or substituted production mode')
    if value.get('brief_sha256') != sha(project / 'brief.json'):
        raise ValueError('production scope brief changed')
    if mode in FILM_MODES:
        plan = read(project / 'production-plan.json')
        if plan.get('quality_mode') != 'motif-gold-v1':
            raise ValueError('film production requires existing Gold quality mode')
    return value


def entry_scope(project, entrypoint, mode='original-film'):
    """New runners declare their documented mode; existing declarations persist."""
    project = Path(project)
    if (project / 'production-scope.json').exists():
        return require_scope(project)
    return declare(project, mode, entrypoint)


def compile_scope(project, plan):
    """Library compilers admit Gold or an explicitly scoped technical fixture."""
    project = Path(project)
    if (project / 'production-scope.json').exists():
        scope=require_scope(project)
        if scope['actual_mode'] in FILM_MODES:
            if plan.get('quality_mode')!='motif-gold-v1' or read(project/'production-plan.json')!=plan:
                raise ValueError('film compiler input differs from saved Gold plan')
        elif scope['actual_mode']!='technical-fixture' and plan.get('quality_mode')!='motif-gold-v1':
            raise ValueError('non-Gold compiler requires explicit technical-fixture scope')
        return scope
    if plan.get('quality_mode') != 'motif-gold-v1':
        raise ValueError('missing compile quality mode; declare technical-fixture for legacy code')


def evidence_inputs(project):
    """Validate declared scope before any new film capture side effects."""
    project = Path(project)
    scope = require_scope(project)
    if scope['actual_mode'] not in FILM_MODES:
        return None
    from motif_causal import validate_map, coverage
    plan = read(project / 'production-plan.json')
    spec = read(project / 'scene-events.json')
    frames = round(spec['durationSec'] * spec['fps'])
    beats = plan.get('beats', plan.get('shots', []))
    script = plan.get('script', ' '.join(b.get('narration', '') for b in beats))
    mapping=read(project / 'causal-map.json')
    result = validate_map(mapping, script, frames)
    required=coverage(read(project / 'critical-intervals.json'), frames, [b['id'] for b in beats])
    from motif_causal import interval
    mapped=set()
    for prop in mapping['propositions']:
        shot=prop['shot_id'];mapped.add(shot)
        if shot not in required or not set(interval(prop['review_interval'],frames)).issubset(required[shot]):
            raise ValueError('critical intervals do not cover frozen causal map: '+shot)
    if mapped!=set(required):raise ValueError('each shot needs an explicit causal evidence route')
    return result


def technical_coverage(name, record):
    """New scoped runs require counted, enabled coverage on source checks."""
    coverage = record.get('coverage', {})
    required, checked = coverage.get('required'), coverage.get('checked')
    if (coverage.get('enabled') is not True or
            type(required) is not int or type(checked) is not int or
            required < 1 or checked < required or not coverage.get('scope')):
        raise ValueError('incomplete enabled technical coverage: ' + name)


def technical_binding(name, record, events_sha256, video_sha256):
    technical_coverage(name, record)
    if (record.get('events_sha256') != events_sha256 or record.get('video_sha256') != video_sha256 or
            not record.get('file') or sha(record['file']) != record.get('sha256')):
        raise ValueError('technical source binding incomplete: '+name)
    source=read(record['file'])
    if source.get('check') != name:
        raise ValueError('technical source describes a different check: '+name)
    for key in ('status','coverage','events_sha256','video_sha256','observation'):
        if source.get(key)!=record.get(key):
            raise ValueError('technical source result differs: '+name+': '+key)


def capture_inputs(project):
    project=Path(project)
    names=['production-scope.json','production-plan.json','scene-events.json']
    if (project/'render-config.json').exists():names.append('render-config.json')
    resources={}
    if (project/'resource-manifest.json').exists():
        from motif_media_contracts import locked_resource
        names.append('resource-manifest.json')
        for record in read(project/'resource-manifest.json')['resources']:
            resources['resource:'+record['path']]=sha(locked_resource(project,record))
    scope=require_scope(project)
    if scope['actual_mode'] in FILM_MODES:
        evidence_inputs(project)
        names+=['causal-map.json','critical-intervals.json']
    return {**{name:sha(project/name) for name in names},**resources}


def freeze_capture(project):
    """Called before capture commands; a failed attempt remains in the archive."""
    project=Path(project)
    name='capture-scopes/'+uuid.uuid4().hex+'.json'
    value={'version':1,'status':'STARTED','inputs':capture_inputs(project),'artifacts':{}}
    write(project/name,value)
    write(project/'capture-scope.json',{'record':name,'sha256':sha(project/name)})
    return name


def seal_capture(project, name, artifacts):
    project=Path(project)
    path=project/name
    value=read(path)
    if value['status']!='STARTED' or value['inputs']!=capture_inputs(project):
        raise ValueError('capture inputs changed during capture')
    value['artifacts']={str(Path(p).resolve()):sha(p) for p in artifacts}
    if not value['artifacts']:raise ValueError('captured artifacts required')
    value['status']='CAPTURED'
    write(path,value)
    write(project/'capture-scope.json',{'record':name,'sha256':sha(path)})
    return {'record':name,'sha256':sha(path)}


def require_capture(project, record=None, artifacts=()):
    project=Path(project)
    record=record or read(project/'capture-scope.json')
    name=record.get('record','')
    if not isinstance(name,str) or not __import__('re').fullmatch(r'capture-scopes/[0-9a-f]{32}\.json',name):
        raise ValueError('invalid local capture record path')
    path=project/name
    if sha(path)!=record.get('sha256'):raise ValueError('capture record changed')
    value=read(path)
    if value.get('status')!='CAPTURED' or value.get('inputs')!=capture_inputs(project):
        raise ValueError('scope/map/interval/plan/events changed since frozen capture')
    for artifact in artifacts:
        if value['artifacts'].get(str(Path(artifact).resolve()))!=sha(artifact):
            raise ValueError('artifact not bound to this capture')
    return record


def evidence_shots(bindings, plan):
    """Paper spans and UI frame schedules share one sampler input contract."""
    planned={s['id']:s for s in plan.get('shots',[])}
    result=[]
    for shot in bindings['shots']:
        if 'span' in shot:
            span=shot['span']
            result.append({'id':shot['id'],'start':span['start'],'end':span['end'],
                           'contacts':[a['time'] for a in span['actions']]})
        else:
            saved=planned[shot['id']]
            result.append({'id':shot['id'],'startFrame':saved['startFrame'],
                           'endFrame':saved['endFrame'],'contacts':[]})
    return result


def completion(project, artifact):
    """Record encoded readiness honestly; human evaluation remains separate."""
    project = Path(project)
    value = require_scope(project)
    artifact = Path(artifact).resolve()
    if not artifact.is_file():
        raise ValueError('completion artifact missing')
    result = {'version': 1, 'mode': value['actual_mode'],
              'scope_sha256': sha(project / 'production-scope.json'),
              'artifact': str(artifact), 'artifact_sha256': sha(artifact),
              'status': 'ENCODED_REVIEW_REQUIRED', 'film_approved': False,
              'dimensions': {k: 'UNASSESSED' for k in DIMENSIONS},
              'next': 'Evaluate frozen artifact with independent picture and playback reviews.'}
    if value['actual_mode'] not in FILM_MODES:
        result['status'] = 'SCOPED_OUTPUT_ONLY'
    write(project / 'completion-evidence.json', result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['declare', 'check', 'completion', 'freeze-capture', 'seal-capture'])
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--mode', choices=MODES)
    parser.add_argument('--artifact', type=Path)
    parser.add_argument('--artifacts', type=Path, nargs='+')
    parser.add_argument('--capture-record')
    args = parser.parse_args()
    if args.action == 'declare':
        result = declare(args.project, args.mode, 'explicit-saved-project')
    elif args.action == 'check':
        result = require_scope(args.project)
    elif args.action == 'freeze-capture':
        result = {'record':freeze_capture(args.project)}
    elif args.action == 'seal-capture':
        result = seal_capture(args.project,args.capture_record,args.artifacts or [])
    else:
        result = completion(args.project, args.artifact)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
