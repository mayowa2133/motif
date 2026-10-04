#!/usr/bin/env python3
"""Explicit own-evidence transfer admission; never reference calibration."""
import argparse,json,shutil
from pathlib import Path
from jsonschema import Draft202012Validator
from motif_reference import ROOT,read,write,sha,CONCEPT,OPENING,valid_invocation
MODE='transfer-independent-v1'
POLICY='quality/transfer-review/PROMPT.md'
SCHEMA='schemas/transfer-gate.schema.json'
def enabled(project):return (Path(project)/'transfer-review/required.json').is_file()
def profile(project):
 p=Path(project).resolve();m=p/'transfer-review/required.json';r=read(m)
 if r.get('mode')!=MODE:raise ValueError('unsupported transfer evidence mode')
 if (p/'reference-calibration/required.json').exists() or (p/'reference-calibration/record.json').exists():raise ValueError('transfer cannot mix with private reference calibration')
 for field in ('rubric','learned_metadata','kit_manifest'):
  item=r[field]
  if sha(item['file'])!=item['sha256']:raise ValueError('frozen transfer '+field+' changed')
 manifest=read(r['kit_manifest']['file']);kit=Path(r['kit_manifest']['file']).resolve().parents[1]
 if manifest['package_digest']!=r['kit_digest']:raise ValueError('transfer kit identity changed')
 for rel,digest in manifest['package_files'].items():
  if sha(kit/rel)!=digest:raise ValueError('frozen transfer package changed: '+rel)
 for rel,digest in manifest['repository_dependencies'].items():
  if sha(ROOT/rel)!=digest:raise ValueError('transfer runtime dependency changed: '+rel)
 return r

def binding(project):
 if not enabled(project):return {}
 profile(project);return {'evidence_scope':MODE,'transfer_profile_sha256':sha(Path(project)/'transfer-review/required.json'),'transfer_project_root':str(Path(project).resolve())}
def context(project):
 r=profile(project)
 return '\nEXPLICIT TRANSFER EVIDENCE SCOPE (no reference/gold pixels, no parity claim):'+MODE+'\nFROZEN ACCEPTED-QUALITY RUBRIC:\n'+Path(r['rubric']['file']).read_text()+'\nLEARNED METADATA (relationships, not source shots):'+Path(r['learned_metadata']['file']).read_text()
def enable(project,kit):
 p=Path(project).resolve();kit=Path(kit).resolve();dest=p/'transfer-review/required.json'
 if dest.exists():profile(p);return read(dest)
 if (p/'reference-calibration/required.json').exists() or (p/'reference-calibration/record.json').exists():raise ValueError('archive conflicting calibration separately; do not mix evidence modes')
 manifest=kit/'references/frozen-package.json'
 r={'mode':MODE,'kit_digest':read(manifest)['package_digest'],'rubric':{'file':str(kit/'references/quality.md'),'sha256':sha(kit/'references/quality.md')},'learned_metadata':{'file':str(kit/'references/learned-prior.json'),'sha256':sha(kit/'references/learned-prior.json')},'kit_manifest':{'file':str(manifest),'sha256':sha(manifest)},'scope':'own native art + frozen text only; not source-calibrated review','human_approval':False}
 write(dest,r);profile(p);return r

def own_file(project,item,native=False):
 from PIL import Image
 p=Path(project).resolve();f=Path(item['file']).resolve()
 if not f.is_relative_to(p) or not f.is_file() or sha(f)!=item['sha256']:raise ValueError('only unchanged project-local own evidence permitted')
 if native:
  with Image.open(f) as pic:
   if pic.size!=(360,640):raise ValueError('native360x640 evidence required')
 return f

def prepare(project,config,beat_ids=None):
 from motif_direct import model_call
 from motif_structure import require_structure
 p=Path(project);profile(p);require_structure(p);plan=read(p/'production-plan.json')
 beat_ids=beat_ids or [b for s in plan['film_structure']['setups'] for b in s['beat_ids']];selected=[b for b in plan['beats'] if b['id'] in beat_ids]
 policy=(ROOT/'quality/concept-director/PROMPT.md').read_text()
 policy=policy.replace('Retrieve bounded actual connection/contact, transfer/input or continuing-process evidence for each critical beat, using semantic relationships, not topic nouns. Transfer principles, never reference assets, plots or characters.', 'Use only the frozen learned relationship metadata and quality rubric as directing priors; no original reference pixels or source shots are available in this mode.')
 prompt=policy+'\nTRANSFER-INDEPENDENT CONTRACT PREPARATION: do not retrieve original shots or reference pixels. Identify every planned physical interaction and BEFORE/CONTACT/AFTER from the actual beats; do not invent a replacement scene or change Bot role. This is a data contract, not visual approval.\nBEATS:'+json.dumps(selected)+context(p)
 base=p/'transfer-review';base.mkdir(exist_ok=True)
 value=model_call(base,'concept-contract',prompt,'schemas/concept-contract.schema.json',{**config,**binding(p)},())
 Draft202012Validator(read(ROOT/'schemas/concept-contract.schema.json')).validate(value)
 if [b['beat_id'] for b in value['beats']]!=beat_ids:raise ValueError('transfer contract beat coverage mismatch')
 for b in value['beats']:
  actual=next(x for x in selected if x['id']==b['beat_id'])
  if b['bot_role']!=actual['quality']['art_direction']['bot_role']:raise ValueError('transfer contract changed Bot role')
 write(p/'concept-contract.json',value)
 write(base/'contract-record.json',{**binding(p),'plan_sha256':sha(p/'production-plan.json'),'contract_sha256':sha(p/'concept-contract.json'),'invocation_sha256':sha(base/'concept-contract-invocation.json')})
 return value

def verify_contract(project):
 p=Path(project);r=read(p/'transfer-review/contract-record.json')
 if any(r.get(k)!=v for k,v in binding(p).items()) or r['plan_sha256']!=sha(p/'production-plan.json') or r['contract_sha256']!=sha(p/'concept-contract.json') or r['invocation_sha256']!=sha(p/'transfer-review/concept-contract-invocation.json'):raise ValueError('fresh transfer contract required')
 inv=valid_invocation(p/'transfer-review','concept-contract')
 if inv.get('images',[]) or any(inv.get('configuration',{}).get(k)!=v for k,v in binding(p).items()):raise ValueError('transfer contract invocation scope/evidence mismatch')

def evidence_images(project,stage,ev):
 p=Path(project);plan=read(p/'production-plan.json');ids={s['setup_id'] for s in plan['film_structure']['setups']}
 if ev.get('origin')!='project-authored':raise ValueError('own-art origin attestation required')
 if set(ev['setup_ids'])!=ids or len(ev['setup_ids'])!=len(ids) or ev.get('review_setup_ids',ev['setup_ids'])!=ev['setup_ids']:raise ValueError('full transfer setup coverage required')
 if not ev.get('source_hashes'):raise ValueError('own rendered source fingerprint required')
 for file,digest in ev['source_hashes'].items():own_file(p,{'file':file,'sha256':digest})
 images=[own_file(p,i) for i in ev['images']]
 if not images:raise ValueError('actual own stage images required')
 if stage=='concept':
  from motif_concept import validate_contact_proofs
  verify_contract(p);validate_contact_proofs(p,ev)
  if ev.get('caption_free') is not True:raise ValueError('caption-free concept proofs required')
  previews=ev.get('previews',[])
  if {x['setup_id'] for x in previews}!=ids or len(previews)!=len(ids):raise ValueError('one native preview per setup required')
  images += [own_file(p,i,True) for i in previews]
  images += [own_file(p,i,True) for row in ev['contact_proofs'] for i in row['frames'].values()]
 elif stage=='opening':
  from motif_quality import probe_video
  info=probe_video(own_file(p,ev['video']))
  if not 3<=info['duration']<=5.1 or (info['width'],info['height'])!=(360,640):raise ValueError('native3–5s opening required')
  second=probe_video(own_file(p,ev['without_captions']))
  if any(info[k]!=second[k] for k in ('fps','frames','width','height')):raise ValueError('opening caption modes mismatch')
 else:raise ValueError('unsupported transfer stage')
 return list(dict.fromkeys(images))

def status(plan,report,stage,setup_ids):
 Draft202012Validator(read(ROOT/SCHEMA)).validate(report)
 expected=CONCEPT if stage=='concept' else OPENING;rows=report['setup_assessments'];setups={s['setup_id']:s for s in plan['film_structure']['setups']};blocked=[]
 if report['role']!=stage or {a['setup_id'] for a in rows}!=set(setup_ids) or len(rows)!=len(setup_ids):raise ValueError('transfer setup coverage incomplete')
 for row in rows:
  if {c['check'] for c in row['checks']}!=expected or len(row['checks'])!=len(expected):raise ValueError('transfer check coverage incomplete')
  for c in row['checks']:
   if c['basis_id'] not in ('transfer-rubric','learned-prior'):raise ValueError('unknown transfer textual basis')
   applicable=c['status']=='NOT_APPLICABLE' and c['check'] in ('acting','character-role') and setups[row['setup_id']]['bot_role']=='absent'
   if c['status']!='PASS' and not applicable:blocked.append(row['setup_id']+': '+c['check'])
   if c['status']=='FAIL' and not c['correction'].strip():raise ValueError('transfer failure missing correction')
 if report['novelty_warnings']:blocked+=report['novelty_warnings']
 if report['status']!='PASS':blocked.append('global '+stage+' '+report['status'])
 return {'status':'PASS' if not blocked else 'REVISE_ART_DIRECTION' if stage=='concept' else 'REWORK_OPENING','blocked':blocked}

def policies():return {f:sha(ROOT/f) for f in (POLICY,SCHEMA,'scripts/motif_transfer_review.py','scripts/motif_concept.py','scripts/motif_reference.py')}
def completed_review(base,stage='concept'):
 name=stage+'-critic'
 base=Path(base);r=read(base/'record.json');inv=read(base/(name+'-invocation.json'))
 if inv['exit_code'] or inv.get('saved_response_used') or inv.get('model_fallback_used'):raise ValueError('completed live transfer review required')
 if r['response_sha256']!=sha(base/(name+'.json')) or r['invocation_sha256']!=sha(base/(name+'-invocation.json')) or inv['input_sha256']!=sha(base/(name+'-input.txt')) or inv['output_schema_sha256']!=sha(base/(name+'-output-schema.json')):raise ValueError('historical transfer receipt changed')
 return inv

def guard_transfer_deadlock(project):
 p=Path(project);failures=[];seen=set()
 records=list((p/'transfer-concept-history').glob('*/record.json'))+[p/'transfer-gates/concept/record.json']
 for f in records:
  try:inv=completed_review(f.parent);report=read(f.parent/'concept-critic.json')
  except (FileNotFoundError,KeyError,ValueError):continue
  ident=(inv['input_sha256'],sha(f.parent/'concept-critic.json'))
  if ident in seen:continue
  seen.add(ident)
  for row in report['setup_assessments']:
   for c in row['checks']:
    if c['status']=='FAIL' and c['check'] in ('hero-scale','hierarchy','character-role','CONTACT_PROOF_UNREADABLE','ACTOR_AMBIGUITY','UNNECESSARY_VISIBLE_MECHANISM'):failures.append((row['setup_id'],c['check']))
 if any(failures.count(x)>=2 for x in failures):raise ValueError('transfer concept deadlock: simplify/split/change relationship')

def stage_review(project,stage,evidence_path,config):
 from motif_direct import model_call
 from motif_structure import require_structure
 from motif_concept import guard_deadlock
 p=Path(project);profile(p);require_structure(p);ev=read(evidence_path);base=p/'transfer-gates'/stage;base.mkdir(parents=True,exist_ok=True)
 images=evidence_images(p,stage,ev)
 if stage=='concept':
  guard_deadlock(p,ev) # Original history plus transfer history below.
  guard_transfer_deadlock(p)
 if (base/'record.json').exists():
  completed_review(base,stage)
  dest=p/('transfer-'+stage+'-history')/sha(base/(stage+'-critic-invocation.json'))[:16];shutil.copytree(base,dest,dirs_exist_ok=True)
 prompt=(ROOT/POLICY).read_text()+context(p)+'\nReturn evidence_scope '+MODE+' and role '+stage+'. Assess exactly checks:'+json.dumps(sorted(CONCEPT if stage=='concept' else OPENING))+'\nPLAN:'+json.dumps(read(p/'production-plan.json'))+'\nOWN EVIDENCE/IMAGE ORDER:'+json.dumps(ev)
 name=stage+'-critic';report=model_call(base,name,prompt,SCHEMA,{**config,**binding(p)},images)
 result=status(read(p/'production-plan.json'),report,stage,ev['setup_ids'])
 write(base/'record.json',{**result,**binding(p),'plan_sha256':sha(p/'production-plan.json'),'evidence_path':str(Path(evidence_path).resolve()),'evidence_sha256':sha(evidence_path),'image_inputs':[{'file':str(f),'sha256':sha(f)} for f in images],'response_sha256':sha(base/(name+'.json')),'invocation_sha256':sha(base/(name+'-invocation.json')),'policy_hashes':policies(),'human_approval':False,'source_calibration':False})
 if result['status']!='PASS':raise ValueError('transfer '+stage+' blocked: '+json.dumps(result['blocked']))
 return report

def require_stage(project,stage):
 p=Path(project);profile(p);base=p/'transfer-gates'/stage;name=stage+'-critic'
 try:
  r=read(base/'record.json');ev=read(r['evidence_path'])
  if any(r.get(k)!=v for k,v in binding(p).items()) or r['policy_hashes']!=policies() or r['plan_sha256']!=sha(p/'production-plan.json') or r['evidence_sha256']!=sha(r['evidence_path']) or r['response_sha256']!=sha(base/(name+'.json')) or r['invocation_sha256']!=sha(base/(name+'-invocation.json')):raise ValueError('transfer stage stale')
  images=evidence_images(p,stage,ev);inv=valid_invocation(base,name)
  expected=[{'file':str(f),'sha256':sha(f)} for f in images]
  if any(inv.get('configuration',{}).get(k)!=v for k,v in binding(p).items()) or r['image_inputs']!=expected or inv.get('images')!=expected:raise ValueError('transfer invocation attached non-permitted evidence')
  if r['status']!='PASS' or status(read(p/'production-plan.json'),read(base/(name+'.json')),stage,ev['setup_ids'])['status']!='PASS':raise ValueError('transfer gate blocked')
  return r
 except (FileNotFoundError,KeyError) as error:raise ValueError('fresh own-evidence transfer '+stage+' review required') from error

def main():
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('action',choices=['enable','prepare','concept','opening','verify']);a.add_argument('--project',type=Path,required=True);a.add_argument('--kit',type=Path);a.add_argument('--evidence',type=Path);a.add_argument('--stage',choices=['concept','opening'],default='concept');v=a.parse_args()
 from motif_direct import backend_config
 result=enable(v.project,v.kit) if v.action=='enable' else require_stage(v.project,v.stage) if v.action=='verify' else prepare(v.project,backend_config()) if v.action=='prepare' else stage_review(v.project,v.action,v.evidence,backend_config())
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
