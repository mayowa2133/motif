#!/usr/bin/env python3
"""Explicit own-evidence transfer admission; never reference calibration."""
import argparse,hashlib,json,math,shutil
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

def review_setup_ids(plan,stage,ev):
 ids={s['setup_id'] for s in plan['film_structure']['setups']};covered=ev['setup_ids'];reviewed=ev.get('review_setup_ids',covered)
 if not covered or len(covered)!=len(set(covered)) or not set(covered)<=ids or not reviewed or len(reviewed)!=len(set(reviewed)) or not set(reviewed)<=set(covered):raise ValueError('valid declared transfer setup scope required')
 if stage=='concept' and (set(covered)!=ids or set(reviewed)!=ids):raise ValueError('full transfer concept setup coverage required')
 return reviewed

def opening_inputs(project,ev):
 from motif_quality import probe_video
 p=Path(project);plan=read(p/'production-plan.json');info=probe_video(own_file(p,ev['video']));second=probe_video(own_file(p,ev['without_captions']))
 if not 3<=info['duration']<=5.1 or (info['width'],info['height'])!=(360,640):raise ValueError('native3–5s opening required')
 if any(info[k]!=second[k] for k in ('fps','frames','width','height')):raise ValueError('opening caption modes mismatch')
 timing_file=own_file(p,ev['setup_timing']);timing=read(timing_file)
 if ev['source_hashes'].get(str(timing_file))!=sha(timing_file) or timing['plan_sha256']!=sha(p/'production-plan.json'):raise ValueError('opening timing must bind own rendered sources and plan')
 ids={s['setup_id'] for s in plan['film_structure']['setups']};rows=timing['setups']
 if {r['setup_id'] for r in rows}!=ids or len(rows)!=len(ids):raise ValueError('complete own setup timing required')
 cursor=0
 for r in rows:
  if not isinstance(r['start'],(int,float)) or not isinstance(r['end'],(int,float)) or not math.isfinite(r['start']) or not math.isfinite(r['end']) or r['start']!=cursor or not r['end']>r['start']:raise ValueError('setup timing must partition actual choreography')
  cursor=r['end']
 if cursor<info['duration']:raise ValueError('setup timing must cover complete actual opening')
 selected=[r for r in rows if r['start']<info['duration'] and r['end']>0]
 reviewed=review_setup_ids(plan,'opening',ev)
 if set(reviewed)!={r['setup_id'] for r in selected}:raise ValueError('opening scope must exactly match actual reviewed interval')
 return info,selected

def sample_opening(project,ev):
 from motif_quality import evidence
 p=Path(project);info,rows=opening_inputs(p,ev);dest=p/'transfer-review/opening-samples'
 # Called only before a fresh live review. Existing failed receipt is archived first.
 if dest.exists():shutil.rmtree(dest)
 shots=[{'id':r['setup_id'],'start':r['start'],'end':min(r['end'],info['duration']),**({'temporal_events':r['temporal_events']} if r.get('temporal_events') else {})} for r in rows]
 samples={};images=[]
 for mode,field in [('with_captions','video'),('without_captions','without_captions')]:
  samples[mode]=evidence(own_file(p,ev[field]),dest/mode,shots)
  images += [{'file':f,'sha256':sha(f)} for f in samples[mode]['sheets']]
  samples[mode]['motion_observations']=read(samples[mode]['motion_trace'])
 manifest=dest/'sampling.json';write(manifest,{'method':'motif_quality.evidence; actual native decode both modes','video_inputs':{f:ev[f] for f in ('video','without_captions')},'samples':samples,'images':images})
 return {**ev,'images':images,'decoded_opening_samples':samples,'opening_sampling':{'file':str(manifest.resolve()),'sha256':sha(manifest)}}

def evidence_images(project,stage,ev):
 p=Path(project);plan=read(p/'production-plan.json');ids={s['setup_id'] for s in plan['film_structure']['setups']}
 if ev.get('origin')!='project-authored':raise ValueError('own-art origin attestation required')
 review_setup_ids(plan,stage,ev)
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
  opening_inputs(p,ev);sampling=read(own_file(p,ev['opening_sampling']))
  if sampling['method']!='motif_quality.evidence; actual native decode both modes' or sampling['video_inputs']!={f:ev[f] for f in ('video','without_captions')} or sampling['images']!=ev['images']:raise ValueError('opening images must derive from both actual movies')
  if ev.get('decoded_opening_samples')!=sampling['samples']:raise ValueError('opening decoded observation metadata changed')
  if set(sampling['samples'])!={'with_captions','without_captions'}:raise ValueError('both opening modes must be sampled')
  for sample in sampling['samples'].values():
   own_file(p,{'file':sample['motion_trace'],'sha256':sample['trace_sha256']})

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

def concept_families(plan):
 # IDs, palette/layout and free-text visual-rule wording do not reset attempts.
 families={}
 for setup in plan['film_structure']['setups']:
  beats=[b for b in plan['beats'] if b['id'] in setup['beat_ids']]
  key={'narration':[b.get('narration','') for b in beats],'relationship':setup.get('relationship_archetype',''),'bot_role':setup['bot_role']}
  families[setup['setup_id']]=hashlib.sha256(json.dumps(key,sort_keys=True).encode()).hexdigest()
 return families

def validated_escape(project,receipt):
 from motif_concept import apply_patch
 p=Path(project);old_file=own_file(p,receipt['old_plan']);patch_file=own_file(p,receipt['patch']);old=read(old_file);patch=read(patch_file);current=read(own_file(p,receipt['new_plan']))
 if receipt['new_plan_sha256']!=receipt['new_plan']['sha256']:raise ValueError('transfer escape target plan changed')
 original=next(s for s in old['film_structure']['setups'] if s['setup_id']==receipt['replaced_setup'])
 replacements=patch['setups']
 # A rule paraphrase or renamed ID is not a substantive escape. Reuse the
 # existing pure scope/partition/narration/token validation, never its private replan flow.
 if patch['escape']!='split' and (len(replacements)!=1 or replacements[0]['relationship_archetype']==original['relationship_archetype']):raise ValueError('transfer escape requires changed relationship, not new wording')
 if patch['escape']=='split' and (len(replacements)<2 or len({s['relationship_archetype'] for s in replacements})<2):raise ValueError('transfer split requires distinct physical relationships')
 if apply_patch(old,receipt['replaced_setup'],patch)!=current:raise ValueError('transfer escape must equal exact validated current plan')
 if receipt['old_family']!=concept_families(old)[receipt['replaced_setup']] or receipt['new_families']!=concept_families(current):raise ValueError('transfer escape family changed')
 # Old plan must be an actual immutable completed own review, not invented history.
 found=False
 for f in list((p/'transfer-concept-history').glob('*/record.json'))+[p/'transfer-gates/concept/record.json']:
  try:completed_review(f.parent);r=read(f)
  except (ValueError,FileNotFoundError,KeyError):continue
  if r.get('plan_sha256')==receipt['old_plan']['sha256'] and r.get('reviewed_plan_sha256')==receipt['old_plan']['sha256']:found=True
 if not found:raise ValueError('transfer escape requires a completed prior own concept review')
 return receipt

def record_escape(project,old_plan,setup_id,patch_path):
 p=Path(project);profile(p);destination=p/'transfer-review/escapes'/sha(p/'production-plan.json');destination.mkdir(parents=True,exist_ok=True)
 target=destination/'new-plan.json'
 if target.exists() and sha(target)!=sha(p/'production-plan.json'):raise ValueError('immutable transfer escape target changed')
 shutil.copy2(p/'production-plan.json',target)
 original=own_file(p,{'file':str(Path(old_plan).resolve()),'sha256':sha(old_plan)});patch_source=own_file(p,{'file':str(Path(patch_path).resolve()),'sha256':sha(patch_path)})
 for source,name in [(original,'old-plan.json'),(patch_source,'patch.json')]:
  snapshot=destination/name
  if snapshot.exists() and sha(snapshot)!=sha(source):raise ValueError('immutable transfer escape source changed')
  if source!=snapshot:shutil.copy2(source,snapshot)
 old_plan=destination/'old-plan.json';patch_path=destination/'patch.json'
 receipt={**binding(p),'new_plan':{'file':str(target.resolve()),'sha256':sha(target)},'replaced_setup':setup_id,'old_plan':{'file':str(Path(old_plan).resolve()),'sha256':sha(old_plan)},'patch':{'file':str(Path(patch_path).resolve()),'sha256':sha(patch_path)},'new_plan_sha256':sha(p/'production-plan.json'),'old_family':concept_families(read(old_plan))[setup_id],'new_families':concept_families(read(p/'production-plan.json')),'scope':'validated data escape only; all setups need fresh concept review; no inherited approval'}
 validated_escape(p,receipt);write(destination/'receipt.json',receipt);return receipt

def guard_transfer_deadlock(project):
 p=Path(project);failures=[];seen=set();current=concept_families(read(p/'production-plan.json'));retired=set()
 for receipt in (p/'transfer-review/escapes').glob('*/receipt.json'):
  retired.add(validated_escape(p,read(receipt))['old_family'])
 records=list((p/'transfer-concept-history').glob('*/record.json'))+[p/'transfer-gates/concept/record.json']
 for f in records:
  try:inv=completed_review(f.parent);report=read(f.parent/'concept-critic.json');record=read(f);plan=read(f.parent/'reviewed-plan.json')
  except (FileNotFoundError,KeyError,ValueError):continue
  if record.get('reviewed_plan_sha256')!=sha(f.parent/'reviewed-plan.json') or record.get('plan_sha256')!=sha(f.parent/'reviewed-plan.json'):raise ValueError('historical transfer plan changed')
  families=concept_families(plan);ident=(inv['input_sha256'],sha(f.parent/'concept-critic.json'))
  if ident in seen:continue
  seen.add(ident)
  for row in report['setup_assessments']:
   for c in row['checks']:
    if c['status']=='FAIL' and c['check'] in ('hero-scale','hierarchy','character-role','CONTACT_PROOF_UNREADABLE','ACTOR_AMBIGUITY','UNNECESSARY_VISIBLE_MECHANISM'):failures.append((families[row['setup_id']],c['check']))
 for family,check in set(failures):
  if failures.count((family,check))<2:continue
  if family in current.values() or family not in retired:raise ValueError('transfer concept deadlock: validated relationship/split escape required, not cosmetic rename')

def stage_review(project,stage,evidence_path,config):
 from motif_direct import model_call
 from motif_structure import require_structure
 from motif_concept import guard_deadlock
 p=Path(project);profile(p);require_structure(p);ev=read(evidence_path);base=p/'transfer-gates'/stage;base.mkdir(parents=True,exist_ok=True)
 if stage=='concept':
  guard_deadlock(p,ev) # Original history plus transfer history below.
  guard_transfer_deadlock(p)
 if (base/'record.json').exists():
  completed_review(base,stage)
  dest=p/('transfer-'+stage+'-history')/sha(base/(stage+'-critic-invocation.json'))[:16];shutil.copytree(base,dest,dirs_exist_ok=True)
 if stage=='opening':
  ev=sample_opening(p,ev);evidence_path=base/'opening-evidence.json';write(evidence_path,ev)
 images=evidence_images(p,stage,ev)
 prompt=(ROOT/POLICY).read_text()+context(p)+'\nReturn evidence_scope '+MODE+' and role '+stage+'. Assess exactly checks:'+json.dumps(sorted(CONCEPT if stage=='concept' else OPENING))+'\nAssess exactly these declared stage setup IDs (unseen later setups receive no opening approval):'+json.dumps(review_setup_ids(read(p/'production-plan.json'),stage,ev))+'\nPLAN:'+json.dumps(read(p/'production-plan.json'))+'\nOWN EVIDENCE/IMAGE ORDER:'+json.dumps(ev)
 name=stage+'-critic';report=model_call(base,name,prompt,SCHEMA,{**config,**binding(p)},images)
 result=status(read(p/'production-plan.json'),report,stage,review_setup_ids(read(p/'production-plan.json'),stage,ev))
 shutil.copy2(p/'production-plan.json',base/'reviewed-plan.json')
 write(base/'record.json',{**result,**binding(p),'plan_sha256':sha(p/'production-plan.json'),'reviewed_plan_sha256':sha(base/'reviewed-plan.json'),'evidence_path':str(Path(evidence_path).resolve()),'evidence_sha256':sha(evidence_path),'image_inputs':[{'file':str(f),'sha256':sha(f)} for f in images],'response_sha256':sha(base/(name+'.json')),'invocation_sha256':sha(base/(name+'-invocation.json')),'policy_hashes':policies(),'human_approval':False,'source_calibration':False})
 if result['status']!='PASS':raise ValueError('transfer '+stage+' blocked: '+json.dumps(result['blocked']))
 return report

def require_stage(project,stage):
 p=Path(project);profile(p);base=p/'transfer-gates'/stage;name=stage+'-critic'
 try:
  r=read(base/'record.json');ev=read(r['evidence_path'])
  if any(r.get(k)!=v for k,v in binding(p).items()) or r['policy_hashes']!=policies() or r['plan_sha256']!=sha(p/'production-plan.json') or r['reviewed_plan_sha256']!=sha(base/'reviewed-plan.json') or r['reviewed_plan_sha256']!=r['plan_sha256'] or r['evidence_sha256']!=sha(r['evidence_path']) or r['response_sha256']!=sha(base/(name+'.json')) or r['invocation_sha256']!=sha(base/(name+'-invocation.json')):raise ValueError('transfer stage stale')
  images=evidence_images(p,stage,ev);inv=valid_invocation(base,name)
  expected=[{'file':str(f),'sha256':sha(f)} for f in images]
  if any(inv.get('configuration',{}).get(k)!=v for k,v in binding(p).items()) or r['image_inputs']!=expected or inv.get('images')!=expected:raise ValueError('transfer invocation attached non-permitted evidence')
  if r['status']!='PASS' or status(read(p/'production-plan.json'),read(base/(name+'.json')),stage,review_setup_ids(read(p/'production-plan.json'),stage,ev))['status']!='PASS':raise ValueError('transfer gate blocked')
  return r
 except (FileNotFoundError,KeyError) as error:raise ValueError('fresh own-evidence transfer '+stage+' review required') from error

def main():
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('action',choices=['enable','prepare','concept','opening','verify','escape']);a.add_argument('--project',type=Path,required=True);a.add_argument('--kit',type=Path);a.add_argument('--old-plan',type=Path);a.add_argument('--patch',type=Path);a.add_argument('--setup');a.add_argument('--evidence',type=Path);a.add_argument('--stage',choices=['concept','opening'],default='concept');v=a.parse_args()
 from motif_direct import backend_config
 result=record_escape(v.project,v.old_plan,v.setup,v.patch) if v.action=='escape' else enable(v.project,v.kit) if v.action=='enable' else require_stage(v.project,v.stage) if v.action=='verify' else prepare(v.project,backend_config()) if v.action=='prepare' else stage_review(v.project,v.action,v.evidence,backend_config())
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
