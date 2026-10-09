#!/usr/bin/env python3
"""Scoped concept simplification and bounded per-beat reference evidence."""
import argparse,copy,json,shutil
from pathlib import Path
from jsonschema import Draft202012Validator
from motif_reference import ROOT,read,write,sha,corpus,folder,context,require_calibration,valid_invocation
POLICY='quality/concept-director/PROMPT.md'
CONTACT_CHECKS={'hero-scale','hierarchy','character-role','CONTACT_PROOF_UNREADABLE','ACTOR_AMBIGUITY','UNNECESSARY_VISIBLE_MECHANISM'}

def completed_review(base):
 """A completed review receipt stays historical when artwork later changes.
 Input/schema/response bytes must remain intact; image hashes describe that call.
 Fresh approval still uses valid_invocation and verifies current image bytes.
 """
 base=Path(base);inv=read(base/'concept-critic-invocation.json')
 if inv['exit_code'] or inv.get('saved_response_used') or inv.get('model_fallback_used'):raise ValueError('not completed live review')
 if inv['input_sha256']!=sha(base/'concept-critic-input.txt') or inv['output_schema_sha256']!=sha(base/'concept-critic-output-schema.json'):raise ValueError('historical review input changed')
 record=read(base/'record.json')
 if record.get('response_sha256')!=sha(base/'concept-critic.json') or record.get('invocation_sha256')!=sha(base/'concept-critic-invocation.json'):raise ValueError('historical review receipt changed')
 return inv

def deadlock_history(project,setup_id):
 """Only completed live, distinct reviews count; aborted/copied reviews do not."""
 failures=[];seen=set()
 p=Path(project)
 # archive_review writes completed receipts here; include them in the same
 # history given to the replan director, not only in guard_deadlock.
 records=list((p/'reference-gates').glob('*/record.json'))+list((p/'concept-history').glob('*/record.json'))
 for record in sorted(records):
  if 'aborted' in str(record):continue
  base=record.parent
  try:
   inv=completed_review(base);report=read(base/'concept-critic.json')
  except (ValueError,FileNotFoundError,KeyError):continue
  identity=(inv['input_sha256'],sha(base/'concept-critic.json'))
  if identity in seen:continue
  seen.add(identity)
  failed=[c['check'] for a in report['setup_assessments'] if a['setup_id']==setup_id for c in a['checks'] if c['status']=='FAIL' and c['check'] in CONTACT_CHECKS]
  if failed:failures.append({'record':str(record.resolve()),'record_sha256':sha(record),'failed_checks':failed,'invocation_sha256':sha(base/'concept-critic-invocation.json')})
 counts={c:sum(c in r['failed_checks'] for r in failures) for c in CONTACT_CHECKS}
 return {'setup_id':setup_id,'completed_failures':len(failures),'repeated_checks':[c for c,n in counts.items() if n>=2],'escape_required':any(n>=2 for n in counts.values()),'reviews':failures,'moving_budget_consumed':0}

def apply_patch(plan,setup_id,patch,transfer=False):
 """A model patch cannot overwrite unrelated setups/beats/token state changes."""
 Draft202012Validator(read(ROOT/'schemas/concept-replan.schema.json')).validate(patch)
 before=copy.deepcopy(plan);out=copy.deepcopy(plan);setups=out['film_structure']['setups'];old=next(s for s in setups if s['setup_id']==setup_id);index=setups.index(old);beat_ids=old['beat_ids']
 replacements=patch['setups'];beats=patch['beats'];ids=[s['setup_id'] for s in replacements]
 if patch['escape']=='split' and len(replacements)<2:raise ValueError('split escape needs multiple setups')
 if patch['escape']!='split' and len(replacements)!=1:raise ValueError('non-split escape needs one setup')
 if any(s['chapter']!=old['chapter'] for s in replacements):raise ValueError('scoped replan changed chapter')
 if [b['id'] for b in beats]!=beat_ids or [b['narration'] for b in beats]!=[b['narration'] for b in before['beats'] if b['id'] in beat_ids]:raise ValueError('scoped replan changed exact beat narration/order')
 if replacements[-1]['planned_reset_after']!=old['planned_reset_after']:raise ValueError('scoped replan changed outgoing boundary')
 if len(set(ids))!=len(ids) or set(ids)&{s['setup_id'] for s in setups if s['setup_id']!=setup_id}:raise ValueError('setup identity collision')
 if len(replacements)==1 and replacements[0]['visual_rule']==old['visual_rule'] and replacements[0]['relationship_archetype']==old['relationship_archetype']:raise ValueError('deadlock escape cannot retain same physical rule/archetype')
 setups[index:index+1]=replacements
 out['beats']=[next((n for n in beats if n['id']==b['id']),b) for b in out['beats']]
 changes={x['id']:x for x in patch['token_changes']}
 if set(changes)!=set(old['continuity_tokens']):raise ValueError('patch must update only original affected tokens')
 for t in out['film_structure']['continuity_tokens']:
  if t['id'] not in changes:continue
  ch=changes[t['id']];t['story_justification']=ch['story_justification'];usage=[s['setup_id'] for s in setups if t['id'] in s['continuity_tokens']]
  if any(c['setup_id'] not in ids for c in ch['state_changes']):raise ValueError('patch changed token state outside scope')
  t['setups_used']=usage;t['origin_setup']=usage[0]
  state=[c for c in t['state_changes'] if c['setup_id']!=setup_id]+ch['state_changes']
  t['state_changes']=sorted(state,key=lambda c:usage.index(c['setup_id']))
  if before['film_structure']['continuity_tokens'][out['film_structure']['continuity_tokens'].index(t)]['origin_setup']==setup_id:t['state_at_origin']=ch['state_at_origin']
  if usage[-1] in ids:t['final_destination']=ch['final_destination']
 out=refresh_scoped_requirements(before,out,beat_ids,patch,transfer=transfer)
 from motif_structure import check_structure
 check_structure(out)
 Draft202012Validator(read(ROOT/'schemas/script-production-plan.schema.json')).validate(out)
 for s in before['film_structure']['setups']:
  if s['setup_id']!=setup_id and next(x for x in setups if x['setup_id']==s['setup_id'])!=s:raise ValueError('passing setup modified')
 return out

def refresh_scoped_requirements(before,out,beat_ids,patch,transfer=False):
 """Retire old scope's shared prose/resources; never leave two active architectures.
 Assets exclusive to locked beats remain byte-identical. Mixed action bundles are
 narrowed to actual unchanged requirements. New capability IDs come from the live
 patch, not a hand-written substitute storyboard.
 """
 locked=[b for b in out['beats'] if b['id'] not in beat_ids]
 new=[b for b in out['beats'] if b['id'] in beat_ids]
 locked_ids={a for b in locked for a in b['needed_assets']}
 old_ids={a for b in before['beats'] if b['id'] in beat_ids for a in b['needed_assets']}
 wanted={a for b in out['beats'] for a in b['needed_assets']}
 original={a['id']:a for a in before['assets']};usage={a['id']:a for a in before['asset_usage']}
 assets=[];usages=[]
 for aid in sorted(wanted):
  if aid in original and aid not in old_ids-{'agency-props','shared-motif-runtime'}:
   assets.append(copy.deepcopy(original[aid]));usages.append(copy.deepcopy(usage[aid]));continue
  relevant=[b for b in out['beats'] if aid in b['needed_assets']]
  requirements=[{'beat':b['id'],'actions':b['actions']} for b in relevant]
  assets.append({'id':aid,'description':'Active requirements only; superseded scoped apparatus is retired. '+json.dumps(requirements),'reuse_path':original.get(aid,{}).get('reuse_path','') if aid in locked_ids else ''})
  usages.append(copy.deepcopy(usage[aid]) if aid in locked_ids and aid in usage else {'id':aid,'scope':'production-specific','path':'','metadata_path':'','agent_assisted':True})
 out['assets']=assets;out['asset_usage']=usages
 out['rationale']=patch['reason']
 out['metaphor']='Unchanged worlds retain their own setup rules. Replacement relationships: '+' '.join(s['visual_rule'] for s in patch['setups'])
 if transfer:
  out['limitations']=[
   'Exact supplied script and unaffected setup/beat contracts remain unchanged. Superseded requirements and failed reviews are retained as history.',
   'Scoped data requirements do not establish implementation, registered capability, painted quality or human approval. Empty capability paths require explicit project-authored development.',
   'Canonical Motif Bot remains locked. Frozen textual priors supply directing criteria, not factual claims, source pixels or inherited visual approval.',
   'All current setups require fresh own-evidence concept review. Subsequent direction, opening, moving and audio stages retain their admission gates; human moving review remains final.',
   'Concept deadlock and moving repair budgets stay separate. A validated relationship/split escape permits fresh full-project review only.']
  return out
 out['limitations']=[
  'Exact script, source packet and eight unaffected setup/beat contracts are preserved. Only the scoped relationships and their active capability requirements are replaced. Original metadata and failed reports remain archived, not active requirements.',
  'New requirements are live model-authored proposals. Empty capability paths mean agent-assisted development is required; no implementation, registered selector, animation or quality approval is implied.',
  'Canonical Motif Bot v1 stays locked. Exact narration and factual qualifications remain dated to the supplied source packet. Private visual evidence supplies no facts or assets.',
  'This cycle delivers static caption-free native concept/contact proofs only. Moving continuity, full-rate contact, narration/audio and a finished film remain unassessed. No animation or full rough is authorized.',
  'Concept deadlock and moving-repair budgets remain separate. Preserved passing concepts require byte-identical inheritance; replacement setup/contact/hierarchy assessments require fresh independent live review.']
 return out

def replan(project,original,setup_id,config):
 from motif_direct import model_call
 p=Path(project);old=Path(original);plan=read(old/'production-plan.json');history=deadlock_history(old,setup_id);write(p/'deadlock-history.json',history)
 target=next(s for s in plan['film_structure']['setups'] if s['setup_id']==setup_id)
 refs,images=context(p)
 prompt=(ROOT/POLICY).read_text()+'\nReturn only a replacement patch for the blocked setup. Preserve exact existing beat IDs/narration, chapter, half-open full-script word ranges and final outgoing reset. The unaffected eight setups and their beats are LOCKED. Start with propositions, never the rejected apparatus. No shot list is supplied. No current task deck/coupling or Bot-wing pushing is required. Choose the simplest original readable relationships; prefer clear product agency. Return explicit unsupported capabilities as agent-assisted. Each setup must have one physical rule. Update only the original tokens at replaced setups, preserving token identity.\nFULL ORIGINAL PLAN:'+json.dumps(plan)+'\nBLOCKED SETUP:'+json.dumps(target)+'\nDEADLOCK:'+json.dumps(history)+refs
 patch=model_call(p,'scoped-replan',prompt,'schemas/concept-replan.schema.json',config,images)
 revised=apply_patch(plan,setup_id,patch);write(p/'production-plan.json',revised)
 new_ids=[s['setup_id'] for s in patch['setups']]
 locked=[s['setup_id'] for s in plan['film_structure']['setups'] if s['setup_id']!=setup_id]
 write(p/'concept-scope.json',{'original_project':str(old.resolve()),'original_plan_sha256':sha(old/'production-plan.json'),'replaced_setup':setup_id,'review_setup_ids':new_ids,'preserved_setup_ids':locked,'escape':patch['escape'],'patch_sha256':sha(p/'scoped-replan.json'),'old_concepts_archived_in_place':True})
 return revised

def select_beat_references(manifest,contracts,limit=2):
 """Bounded per-beat semantic matching; no shared setup-wide query substitution."""
 pool=[{**s,'video_id':v['id']} for v in manifest['videos'] for s in v['setups']];rows=[]
 for b in contracts['beats']:
  wanted={r['verb'] for r in b['relationships']};candidates=[s for s in pool if wanted&set(s['relationships'])]
  if not candidates:raise ValueError('missing reference relationship evidence for '+b['beat_id'])
  ranked=sorted(candidates,key=lambda s:(-len(wanted&set(s['relationships'])),s['duration'],s['id']))
  rows.append({'beat_id':b['beat_id'],'physical_rule':b['physical_rule'],'selected':ranked[:limit]})
 return rows

def prepare(project,config,beat_ids=None):
 from motif_transfer_review import enabled,prepare as transfer_prepare
 if enabled(project):return transfer_prepare(project,config,beat_ids)
 from motif_direct import model_call
 p=Path(project);require_calibration(p,True);plan=read(p/'production-plan.json');scope=read(p/'concept-scope.json') if (p/'concept-scope.json').exists() else None
 beat_ids=beat_ids or [b for s in plan['film_structure']['setups'] if not scope or s['setup_id'] in scope['review_setup_ids'] for b in s['beat_ids']]
 selected=[b for b in plan['beats'] if b['id'] in beat_ids];ref,images=context(p)
 if not (p/'concept-contract.json').exists():
  prompt=(ROOT/POLICY).read_text()+'\nAnalyze these actual beats, not an invented replacement. Identify every planned physical interaction with a unique ID. Describe immediately before/exact contact/immediately after. If there is no physical contact, interactions may be empty but justify visual rule. Do not combine different contacts under one ID. Use existing actor roles; do not rewrite beat actions. Return exactly one contract per supplied beat. Semantic relationship enums are retrieval terms, not templates.\nBEATS:'+json.dumps(selected)+ref
  value=model_call(p,'concept-contract',prompt,'schemas/concept-contract.schema.json',config,images)
 else:value=read(p/'concept-contract.json')
 Draft202012Validator(read(ROOT/'schemas/concept-contract.schema.json')).validate(value)
 if [b['beat_id'] for b in value['beats']]!=beat_ids:raise ValueError('contract beat coverage/order mismatch')
 for b in value['beats']:
  actual=next(x for x in selected if x['id']==b['beat_id'])
  if b['bot_role']!=actual['quality']['art_direction']['bot_role']:raise ValueError('contract cannot change Bot role')
 root,manifest=corpus();rows=select_beat_references(manifest,value);base=folder(p);packets=[];image_map={}
 for row in rows:
  packet={**row,'selected':[]}
  for s in row['selected']:
   item={k:v for k,v in s.items() if k!='evidence'};item['evidence']={}
   for kind,e in s['evidence'].items():
    src=Path(e['file']);dest=base/'beat-evidence'/s['id']/src.name
    if not src.resolve().is_relative_to(root) or sha(src)!=e['sha256']:raise ValueError('private beat evidence changed')
    dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest);item['evidence'][kind]={**e,'file':str(dest.resolve())};image_map[str(dest.resolve())]=sha(dest)
   packet['selected'].append(item)
  packets.append(packet)
 write(base/'beat-retrieval.json',{'plan_sha256':sha(p/'production-plan.json'),'contract_sha256':sha(p/'concept-contract.json'),'corpus_manifest_sha256':sha(root/'manifest.json'),'beats':packets,'images':[{'file':f,'sha256':h} for f,h in image_map.items()],'bounded':{'max_setups_per_beat':2,'max_images_per_beat':6}})
 # The independent Director inspects the real selected strips for beat-specific guidance.
 prompt=(ROOT/POLICY).read_text()+'\nIndependent Reference Director: inspect actual attached per-beat frames. Give bounded original staging/hierarchy/contact principles separately per beat. No new shot list, copied expression or facts. Only cite that beat\'s selected references.\nCONTRACT:'+json.dumps(value)+'\nEVIDENCE:'+json.dumps(read(base/'beat-retrieval.json'))
 result=model_call(base,'beat-director',prompt,'schemas/concept-beat-director.schema.json',config,[Path(f) for f in image_map])
 if [b['beat_id'] for b in result['beats']]!=beat_ids:raise ValueError('Director beat coverage incomplete')
 for b in result['beats']:
  allowed={s['id'] for r in packets if r['beat_id']==b['beat_id'] for s in r['selected']}
  if not b['reference_ids'] or not set(b['reference_ids'])<=allowed:raise ValueError('Director cited another beat\'s evidence')
 write(base/'beat-record.json',{'retrieval_sha256':sha(base/'beat-retrieval.json'),'director_sha256':sha(base/'beat-director.json'),'invocation_sha256':sha(base/'beat-director-invocation.json'),'policy_sha256':sha(ROOT/POLICY)})
 return result

def beat_context(project):
 p=Path(project);base=folder(p)
 if not (base/'beat-record.json').exists():return '',[],[]
 record=read(base/'beat-record.json');r=read(base/'beat-retrieval.json');root,_=corpus()
 expected={'retrieval_sha256':sha(base/'beat-retrieval.json'),'director_sha256':sha(base/'beat-director.json'),'invocation_sha256':sha(base/'beat-director-invocation.json'),'policy_sha256':sha(ROOT/POLICY)}
 if record!=expected or r['plan_sha256']!=sha(p/'production-plan.json') or r['contract_sha256']!=sha(p/'concept-contract.json') or r['corpus_manifest_sha256']!=sha(root/'manifest.json'):raise ValueError('beat reference context stale')
 valid_invocation(base,'beat-director')
 for im in r['images']:
  if sha(im['file'])!=im['sha256']:raise ValueError('beat reference image changed')
 return '\nPER-BEAT CONTRACT/RETRIEVAL/DIRECTOR:'+json.dumps({'contract':read(p/'concept-contract.json'),'retrieval':r,'director':read(base/'beat-director.json')}),[Path(im['file']) for im in r['images']],list({s['id'] for b in r['beats'] for s in b['selected']})

def validate_contact_proofs(project,evidence):
 """Integrity/native coverage only: the independent critic decides readability."""
 from PIL import Image
 p=Path(project);contract=read(p/'concept-contract.json');expected={(b['beat_id'],i['id']) for b in contract['beats'] for i in b['interactions']};proofs=evidence.get('contact_proofs',[])
 if len(proofs)!=len(expected) or {(r['beat_id'],r['interaction_id']) for r in proofs}!=expected:raise ValueError('BEFORE/CONTACT/AFTER interaction coverage incomplete')
 for row in proofs:
  if set(row['frames'])!={'before','contact','after'}:raise ValueError('three clean contact states required')
  for im in row['frames'].values():
   if im.get('diagnostic') or sha(im['file'])!=im['sha256']:raise ValueError('clean unchanged contact proof required')
   with Image.open(im['file']) as pic:
    if pic.size!=(360,640):raise ValueError('native 360x640 contact proof required')
 scope=read(p/'concept-scope.json') if (p/'concept-scope.json').exists() else None
 if scope:
  if evidence.get('review_setup_ids')!=scope['review_setup_ids']:raise ValueError('scoped review coverage changed')
  old=Path(scope['original_project']);oldplan=read(old/'production-plan.json');newplan=read(p/'production-plan.json');old_ev=read(old/'concept-evidence.json');old_report=read(old/'reference-gates/concept/concept-critic.json')
  if sha(old/'production-plan.json')!=scope['original_plan_sha256']:raise ValueError('preserved original plan changed')
  for sid in scope['preserved_setup_ids']:
   if next(s for s in oldplan['film_structure']['setups'] if s['setup_id']==sid)!=next(s for s in newplan['film_structure']['setups'] if s['setup_id']==sid):raise ValueError('passing setup changed')
   original=next(s for s in oldplan['film_structure']['setups'] if s['setup_id']==sid)
   for bid in original['beat_ids']:
    if next(b for b in oldplan['beats'] if b['id']==bid)!=next(b for b in newplan['beats'] if b['id']==bid):raise ValueError('passing beat changed')
   assessment=[a for a in old_report['setup_assessments'] if a['setup_id']==sid]
   if len(assessment)!=1:raise ValueError('preserved assessment missing')
   if any(c['status']=='FAIL' or c['status']=='NOT_ASSESSED' for a in old_report['setup_assessments'] if a['setup_id']==sid for c in a['checks']):raise ValueError('inherited setup not passing')
   original=next(x for x in old_ev['previews'] if x['setup_id']==sid);current=next(x for x in evidence['previews'] if x['setup_id']==sid)
   if sha(original['file'])!=original['sha256'] or current['sha256']!=original['sha256'] or sha(current['file'])!=original['sha256']:raise ValueError('passing preview changed')
 elif set(evidence.get('review_setup_ids',evidence['setup_ids']))!=set(evidence['setup_ids']):raise ValueError('unscoped concept must review every setup')
 return True

def archive_review(project):
 p=Path(project);base=p/'reference-gates/concept'
 if not (base/'record.json').exists():return
 completed_review(base)
 dest=p/'concept-history'/sha(base/'concept-critic-invocation.json')[:16]
 if not dest.exists():shutil.copytree(base,dest)

def guard_deadlock(project,evidence):
 p=Path(project);history=p/'concept-history';failed={}
 for record in history.glob('*/record.json'):
  base=record.parent
  try:completed_review(base);report=read(base/'concept-critic.json')
  except (FileNotFoundError,ValueError,KeyError):continue
  for row in report['setup_assessments']:
   for check in row['checks']:
    if check['status']=='FAIL' and check['check'] in CONTACT_CHECKS:
     key=(row['setup_id'],check['check']);failed[key]=failed.get(key,0)+1
 current=p/'reference-gates/concept/record.json'
 if current.exists():
  try:
   completed_review(current.parent);report=read(current.parent/'concept-critic.json')
   if not (history/sha(current.parent/'concept-critic-invocation.json')[:16]).exists():
    for row in report['setup_assessments']:
     for check in row['checks']:
      if check['status']=='FAIL' and check['check'] in CONTACT_CHECKS:
       key=(row['setup_id'],check['check']);failed[key]=failed.get(key,0)+1
  except (ValueError,FileNotFoundError,KeyError):pass
 # A scoped replan produces a new immutable patch/family and new review IDs.
 if any(n>=2 and sid in evidence.get('review_setup_ids',evidence['setup_ids']) for (sid,_),n in failed.items()):
  raise ValueError('CONCEPT_DEADLOCK: two completed same-family failures; simplify, change archetype or split via a fresh scoped replan, never cosmetic polish')

def main():
 from motif_direct import backend_config
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('action',choices=['replan','prepare']);a.add_argument('--project',type=Path,required=True);a.add_argument('--original',type=Path);a.add_argument('--setup');args=a.parse_args()
 result=replan(args.project,args.original,args.setup,backend_config()) if args.action=='replan' else prepare(args.project,backend_config());print(json.dumps(result,indent=2))
if __name__=='__main__':main()
