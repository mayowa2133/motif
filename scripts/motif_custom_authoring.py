"""Small manual authoring-task records; no automatic custom-code execution.

An explicit capability binding or scoped task feeds shared QA. These records
never certify semantic fulfillment, native editability, film quality or AV.
"""
import math
import copy
from pathlib import Path
from motif_evidence import MODES,read,write,sha
from motif_media_contracts import locked_resource

CAPABILITIES={'waiting-1.0':{'modes':['technical-fixture'],'entrypoint':'motif_waiting'}}
STAGES=('PLAN','BUILD','READY_FOR_SHARED_QA')


def task_path(root):
    path=Path(root)/'custom-authoring-task.json'
    if path.is_symlink() or not path.resolve().is_relative_to(Path(root).resolve()):
        raise ValueError('task bookkeeping must stay inside declared project without a symlink')
    return path


def resolve_requirement(requirement):
    if (not requirement.get('id') or not requirement.get('statement') or
            requirement.get('mode') not in MODES):
        raise ValueError('requirement identity, statement and explicit mode required')
    capability=CAPABILITIES.get(requirement.get('capability'))
    if capability and requirement['mode'] in capability['modes']:
        route={'route':'registered-capability','binding':requirement['capability'],**copy.deepcopy(capability)}
    elif requirement.get('authoring_task'):
        route={'route':'scoped-custom-authoring','task_id':requirement['authoring_task']}
    else:
        raise ValueError('unsupported requirement; declare a scoped custom-authoring task')
    return {'requirement':copy.deepcopy(requirement),**route,'fulfillment':'UNASSESSED','shared_qa_required':True}


def start_task(root,spec):
    root=Path(root);path=task_path(root)
    if path.exists():raise ValueError('task exists; resume without replacing frozen specification')
    resolution=resolve_requirement(spec['requirement'])
    if resolution['route']!='scoped-custom-authoring':raise ValueError('custom task needs explicit task route')
    if not spec.get('inputs') or not spec.get('expected_outputs'):
        raise ValueError('frozen inputs and declared editable outputs required')
    for item in spec['inputs']:locked_resource(root,item)
    names=[item['path'] for item in spec['expected_outputs']]
    if len(set(names))!=len(names):raise ValueError('unique expected output paths required')
    for name in names:
        candidate=Path(name)
        if not candidate.parts or candidate.is_absolute() or '..' in candidate.parts:
            raise ValueError('expected output paths must be project-relative')
        target=(root/candidate).resolve()
        if target==path.resolve():raise ValueError('task bookkeeping cannot be an authored output')
        if not target.is_relative_to(root.resolve()):raise ValueError('output escapes project root')
    write(path,{'version':1,'specification':spec,'resolution':resolution,'stage':'PLAN',
                'history':[],'quality_status':'UNASSESSED','editing_level':'DECLARED_REQUIRES_SHARED_QA'})
    return path


def checkpoint(root,stage,active_seconds,elapsed_seconds,reason):
    """Resume against unchanged inputs; save intervention and output identities."""
    root=Path(root);path=task_path(root);task=read(path)
    if stage not in STAGES or STAGES.index(stage)<STAGES.index(task['stage']):
        raise ValueError('invalid/backward stage; preserve history or start a fresh task')
    unavailable=active_seconds is None and elapsed_seconds is None
    if ((not unavailable and (any(type(v) not in (int,float) or not math.isfinite(v) or v<0 for v in (active_seconds,elapsed_seconds)) or
                              active_seconds>elapsed_seconds)) or not isinstance(reason,str) or not reason.strip()):
        raise ValueError('measured intervention reason and active/elapsed seconds required')
    spec=task['specification']
    for item in spec['inputs']:locked_resource(root,item)
    outputs=[]
    for item in spec['expected_outputs']:
        target=(root/item['path']).resolve()
        if not target.is_relative_to(root.resolve()):raise ValueError('output escapes project root')
        if target==path.resolve() or (target.is_file() and target.samefile(path)):
            raise ValueError('task bookkeeping cannot be an authored output')
        if target.is_file():outputs.append({**item,'sha256':sha(target)})
    if stage=='READY_FOR_SHARED_QA' and len(outputs)!=len(spec['expected_outputs']):
        raise ValueError('declared custom-authoring outputs missing')
    task['stage']=stage
    task['history'].append({'stage':stage,'active_seconds':active_seconds,'elapsed_seconds':elapsed_seconds,
                            'reason':reason,'outputs':outputs,
                            'measurement':'UNAVAILABLE' if unavailable else 'operator-recorded; no inferred efficiency gain'})
    task['quality_status']='UNASSESSED'
    write(path,task)
    return task


def sample_task(root, with_captions, without_captions, shots):
    """Attach actual captured roughs to the existing sampler; never approve them.

    The caller authors and captures explicitly. This bridge executes no supplied
    code and grants no structure, direction, painted, final or human gate pass.
    """
    from motif_quality import evidence_bundle, source_freshness
    from motif_evidence import require_capture, require_scope
    root=Path(root).resolve();path=task_path(root);task=read(path)
    if task['stage']!='READY_FOR_SHARED_QA':
        raise ValueError('custom outputs must be ready before shared QA')
    for item in task['specification']['inputs']:locked_resource(root,item)
    current=task['history'][-1]['outputs'] if task['history'] else []
    if len(current)!=len(task['specification']['expected_outputs']):
        raise ValueError('complete output checkpoint required')
    for item in current:locked_resource(root,item)
    scope=require_scope(root)
    if task['specification']['requirement']['mode']!=scope['actual_mode']:
        raise ValueError('custom task mode differs from production scope')
    a,b=Path(with_captions).resolve(),Path(without_captions).resolve()
    if a==b or any(not p.is_relative_to(root) for p in (a,b)):
        raise ValueError('distinct project-local caption and picture outputs required')
    capture=require_capture(root,artifacts=[a,b])
    manifest=evidence_bundle(root,'rough',a,b,shots)
    if source_freshness(root,manifest):raise ValueError('sampled custom sources changed')
    value={'version':1,'status':'SAMPLED_REVIEW_REQUIRED','mode':scope['actual_mode'],
           'task_sha256':sha(path),'capture_record':capture,
           'evidence_sha256':sha(root/'quality-review/rough/evidence.json'),
           'output_checkpoint':current,'film_approved':False,
           'sampled_files':{str(p):sha(p) for k in ('with_captions','without_captions')
                            for p in [*manifest[k]['sheets'],manifest[k]['motion_trace']]},
           'limits':['Shared decoded-frame sampling is not a Gold gate pass.',
                    'Structure/direction, independent critics, technical gates and human playback/listening remain required.']}
    write(root/'custom-shared-qa.json',value)
    return value


def require_sampled_task(root):
    """Fail closed when source, checkpoint, evidence or capture changes."""
    from motif_quality import source_freshness
    from motif_evidence import require_capture, require_scope
    root=Path(root);value=read(root/'custom-shared-qa.json')
    scope=require_scope(root)
    if value.get('mode')!=scope['actual_mode']:
        raise ValueError('custom QA receipt mode differs from production scope')
    if value.get('status')!='SAMPLED_REVIEW_REQUIRED' or value.get('film_approved') is not False:
        raise ValueError('invalid custom QA receipt')
    if value['task_sha256']!=sha(task_path(root)):
        raise ValueError('custom task checkpoint changed')
    task=read(task_path(root))
    if task['specification']['requirement']['mode']!=scope['actual_mode']:
        raise ValueError('custom task mode differs from production scope')
    if task.get('stage')!='READY_FOR_SHARED_QA' or not task.get('history') or value['output_checkpoint']!=task['history'][-1]['outputs']:
        raise ValueError('custom output checkpoint differs from ready task')
    for item in task['specification']['inputs']:locked_resource(root,item)
    for item in value['output_checkpoint']:locked_resource(root,item)
    path=root/'quality-review/rough/evidence.json'
    if value['evidence_sha256']!=sha(path):raise ValueError('custom evidence changed')
    manifest=read(path)
    expected={str(p) for k in ('with_captions','without_captions')
              for p in [*manifest[k]['sheets'],manifest[k]['motion_trace']]}
    if set(value.get('sampled_files',{}))!=expected:
        raise ValueError('custom sampled file coverage incomplete')
    for path,digest in value['sampled_files'].items():
        if not Path(path).resolve().is_relative_to(root.resolve()) or sha(path)!=digest:
            raise ValueError('custom sampled frame/trace changed')
    if source_freshness(root,manifest):raise ValueError('custom render sources changed')
    require_capture(root,value['capture_record'],artifacts=[manifest[k]['video'] for k in ('with_captions','without_captions')])
    return value
