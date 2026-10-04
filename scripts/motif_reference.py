#!/usr/bin/env python3
"""Private creative corpus and fresh per-production visual calibration.

External frames never become assets, factual sources, internal gold or render
inputs. Models inspect decoded ordered frames; no playback/listening is claimed.
Existing saved plans remain readable. New ordinary planner calls require this
stage; lack of the registered corpus is an explicit failure, never a fallback.
"""
import argparse,hashlib,json,math,os,shutil,subprocess
from pathlib import Path
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
DEFAULT=Path.home()/'.local/share/motif/reference-corpus/private-seven-v1'
DIMENSIONS={'macro-rhythm','visual-density','interaction','character-performance','ui-physicalization','motion-hierarchy','set-richness','designed-irregularity','effect-character','typographic-rhythm','transition-rhythm'}
CONCEPT={'setup-variety','hero-scale','art-density','set-specificity','intentional-space','distinct-silhouettes','character-role','hierarchy','novelty','COMPOUND_VISUAL_RULE','UNNECESSARY_VISIBLE_MECHANISM','ACTOR_AMBIGUITY','CONTACT_PROOF_UNREADABLE'}
OPENING={'energy','acting','hierarchy','tactility','caption-rhythm','physicality','novelty'}
POLICIES=['scripts/motif_reference.py','quality/reference-director/PROMPT.md','quality/reference-critic/PROMPT.md','quality/reference-critic/policy.json','schemas/reference-calibration.schema.json','schemas/reference-query.schema.json','schemas/reference-gate.schema.json']
POLICIES+=['scripts/motif_concept.py','quality/concept-director/PROMPT.md','schemas/concept-contract.schema.json','schemas/concept-replan.schema.json','schemas/concept-beat-director.schema.json']
POLICIES+=['schemas/reference-structure-critic.schema.json','schemas/reference-visual-critic.schema.json']

def read(p):return json.loads(Path(p).read_text())
def write(p,v):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def policies():return {p:sha(ROOT/p) for p in POLICIES}
def folder(project):return Path(project)/'reference-calibration'
def input_text(project):
 b=read(Path(project)/'brief.json');return b.get('script',b.get('message',''))
def corpus(path=None):
 p=Path(path or os.environ.get('MOTIF_REFERENCE_CORPUS',DEFAULT)).expanduser().resolve();m=read(p/'manifest.json')
 if not m.get('private') or len(m['videos'])!=7 or not m.get('setup_count'):raise ValueError('complete private seven-video corpus required')
 for v in m['videos']:
  source=Path(v['source_path']).resolve()
  if not source.is_relative_to(p) or not source.is_file() or sha(source)!=v['sha256'] or v['status']!='REGISTERED':raise ValueError('reference source missing, changed or unregistered: '+v['id'])
 return p,m

def select_setups(manifest,query,count=5,style_count=2):
 """Relationship coverage and source diversity; no product/topic noun matching."""
 if not 3<=count<=5 or not 0<=style_count<=2:raise ValueError('retrieve 3–5 relevant setups plus up to two style examples')
 wanted={r['verb'] for r in query['relationships']};pool=[{**s,'video_id':v['id']} for v in manifest['videos'] for s in v['setups']];chosen=[];covered=set();used={}
 for _ in range(count):
  candidates=[s for s in pool if s['id'] not in {x['id'] for x in chosen} and set(s['relationships'])&wanted]
  if not candidates:break
  def score(s):
   matches=set(s['relationships'])&wanted
   return (len(matches-covered)*5+len(matches)*2-used.get(s['video_id'],0)*3,-s['duration'],s['id'])
  best=max(candidates,key=score);chosen.append({**best,'retrieval_role':'relationship','matched_relationships':sorted(set(best['relationships'])&wanted)});covered|=set(best['relationships'])&wanted;used[best['video_id']]=used.get(best['video_id'],0)+1
 if len(chosen)<3:raise ValueError('insufficient relationship evidence; revise query or corpus annotations, never substitute topic nouns')
 for _ in range(style_count):
  candidates=[s for s in pool if s['id'] not in {x['id'] for x in chosen}]
  if not candidates:break
  best=max(candidates,key=lambda s:(-used.get(s['video_id'],0),bool(s['physical_interaction']),s['duration'],s['id']))
  chosen.append({**best,'retrieval_role':'broader-style','matched_relationships':[]});used[best['video_id']]=used.get(best['video_id'],0)+1
 return chosen

def valid_invocation(base,name):
 r=read(base/(name+'-invocation.json'))
 if r['exit_code'] or r.get('saved_response_used') or r.get('model_fallback_used'):raise ValueError('live independent reference invocation required')
 for key,suffix in [('input_sha256','-input.txt'),('output_schema_sha256','-output-schema.json')]:
  if r[key]!=sha(base/(name+suffix)):raise ValueError('reference invocation input changed')
 for im in r.get('images',[]):
  if not Path(im['file']).is_file() or sha(im['file'])!=im['sha256']:raise ValueError('reference invocation image changed')
 return r

def calibrate(project,config):
 from motif_direct import model_call
 from motif_quality import retrieve,evidence
 p=Path(project).resolve();base=folder(p);text=input_text(p)
 if not text:raise ValueError('exact script or original message required')
 if (base/'record.json').exists():require_calibration(p,required=True);return read(base/'calibration.json')
 if (base/'calibration.json').exists():return accept_calibration(p)
 root,manifest=corpus();base.mkdir(parents=True,exist_ok=True);write(base/'required.json',{'version':'reference-calibration-1.0','required':True,'legacy_saved_productions':'not migrated implicitly'})
 query=model_call(base,'semantic-query','Analyze the exact supplied script/message for semantic relationships before filmmaking. Data only, no tools/web. Return relationship verbs with rationale tied to actual propositions; do not retrieve by product nouns. Do not prescribe shots. INPUT:'+text,'schemas/reference-query.schema.json',config)
 selected=select_setups(manifest,query);images=[];packet=[]
 for s in selected:
  row={k:v for k,v in s.items() if k!='evidence'};row['evidence']={}
  for kind,ev in s['evidence'].items():
   src=Path(ev['file']).resolve()
   if not src.is_relative_to(root) or sha(src)!=ev['sha256']:raise ValueError('private reference evidence changed')
   dest=base/'evidence'/s['id']/src.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest);images.append(dest)
   row['evidence'][kind]={**ev,'file':str(dest.resolve())}
  packet.append(row)
 gold=retrieve([text,*[r['verb'] for r in query['relationships']]],3);gold_packet=[]
 for g in gold:
  still=ROOT/g['still'];images.append(still)
  dst=base/'internal-gold'/g['id'];eg=evidence(ROOT/g['clip']['file'],dst,[{'id':g['id'],'startFrame':g['clip']['frames'][0],'endFrame':g['clip']['frames'][1]}])
  ordered=dst/(g['id']+'-ordered.png');images.append(ordered);gold_packet.append({'id':g['id'],'notes':g['why_passes'],'still':str(still),'ordered':str(ordered),'clip':g['clip']})
 write(base/'retrieval.json',{'corpus_id':manifest['corpus_id'],'corpus_manifest':str(root/'manifest.json'),'corpus_manifest_sha256':sha(root/'manifest.json'),'query':query,'selected':packet,'internal_gold':gold_packet,'copy_policy':'private evidence only, not production assets/facts/templates/runtime files'})
 image_manifest=[{'file':str(x.resolve()),'sha256':sha(x)} for x in images];write(base/'image-inputs.json',image_manifest)
 prompt=(ROOT/'quality/reference-director/PROMPT.md').read_text()+'\nSTRUCTURAL GRAMMAR:\n'+(ROOT/'docs/MOTIF_STRUCTURAL_GRAMMAR.md').read_text()+'\nQUALITY:\n'+(ROOT/'QUALITY_CONTRACT.md').read_text()+'\nEXACT INPUT:'+text+'\nSELECTED EVIDENCE AND IMAGE ORDER:'+json.dumps({'retrieval':read(base/'retrieval.json'),'images':image_manifest})
 result=model_call(base,'calibration',prompt,'schemas/reference-calibration.schema.json',config,images)
 return accept_calibration(p)

def accept_calibration(project):
 """Resume validation of an already live call; never substitute another answer."""
 p=Path(project);base=folder(p);text=input_text(p);retrieval=read(base/'retrieval.json');result=read(base/'calibration.json')
 valid_invocation(base,'calibration');valid_invocation(base,'semantic-query')
 for im in read(base/'image-inputs.json'):
  if sha(im['file'])!=im['sha256']:raise ValueError('calibration image changed before acceptance')
 root,_=corpus()
 if retrieval['corpus_manifest_sha256']!=sha(root/'manifest.json'):raise ValueError('corpus changed before calibration acceptance')
 if result['input_text']!=text or set(result['selected_setup_ids'])!={x['id'] for x in retrieval['selected']}:raise ValueError('calibration changed input or evidence coverage')
 if {t['dimension'] for t in result['targets']}!=DIMENSIONS or len(result['targets'])!=len(DIMENSIONS):raise ValueError('calibration target coverage incomplete')
 external=set(result['selected_setup_ids']);allowed=external|{g['id'] for g in retrieval['internal_gold']}
 if any(not(set(t['evidence_ids'])&external) or not set(t['evidence_ids'])<=allowed for t in result['targets']):raise ValueError('calibration ungrounded target')
 write(base/'record.json',{'input_sha256':hashlib.sha256(text.encode()).hexdigest(),'calibration_sha256':sha(base/'calibration.json'),'retrieval_sha256':sha(base/'retrieval.json'),'images_sha256':sha(base/'image-inputs.json'),'invocation_sha256':sha(base/'calibration-invocation.json'),'query_invocation_sha256':sha(base/'semantic-query-invocation.json'),'policy_hashes':policies(),'human_approval':False,'scope':'fresh live inspection of selected decoded frames; no MP4 playback/listening'})
 return result

def require_calibration(project,required=False):
 base=folder(project)
 if not (base/'required.json').exists() and not required:return None
 try:
  r=read(base/'record.json');root,m=corpus();retrieval=read(base/'retrieval.json')
  expected={'input_sha256':hashlib.sha256(input_text(project).encode()).hexdigest(),'calibration_sha256':sha(base/'calibration.json'),'retrieval_sha256':sha(base/'retrieval.json'),'images_sha256':sha(base/'image-inputs.json'),'invocation_sha256':sha(base/'calibration-invocation.json'),'query_invocation_sha256':sha(base/'semantic-query-invocation.json'),'policy_hashes':policies()}
  if any(r.get(k)!=v for k,v in expected.items()) or retrieval['corpus_manifest_sha256']!=sha(root/'manifest.json'):raise ValueError('reference calibration stale')
  for im in read(base/'image-inputs.json'):
   if sha(im['file'])!=im['sha256']:raise ValueError('reference calibration image changed')
  valid_invocation(base,'calibration');valid_invocation(base,'semantic-query');return r
 except (FileNotFoundError,KeyError) as e:raise ValueError('fresh Reference Calibration required before planning') from e

def context(project):
 if require_calibration(project) is None:return '',[]
 b=folder(project);r=read(b/'retrieval.json');images=[Path(x['file']) for x in read(b/'image-inputs.json')]
 return '\nPRODUCTION REFERENCE CALIBRATION (creative ambition, never facts/assets/shot templates):'+json.dumps(read(b/'calibration.json'))+'\nSELECTED EXTERNAL SETUPS AND INTERNAL GOLD:'+json.dumps(r)+'\nREFERENCE IMAGE ORDER:'+json.dumps(read(b/'image-inputs.json')),images

def reference_failures(plan,report,ids):
 mapping=read(ROOT/'quality/reference-critic/policy.json')['codes'];shots=plan.get('shots',plan.get('beats',[]));expected={(s['id'],c) for s in shots for c in mapping};ass=report.get('reference_assessments',[]);blocked=[]
 if {(a['shot'],a['code']) for a in ass}!=expected or len(ass)!=len(expected):blocked.append('reference visual coverage incomplete')
 for a in ass:
  if a['reference_id'] not in ids:blocked.append('unretrieved reference: '+a['reference_id'])
  absent=next((s['quality']['performance']['state']=='absent' for s in shots if s['id']==a['shot']),False)
  applicable=a['status']=='NOT_APPLICABLE' and a['code']=='REFERENCE_ACTING_GAP' and absent
  if a['status']!='PASS' and not applicable:blocked.append('reference visual: '+a['shot']+': '+a['code'])
  if a['status']=='FAIL':
   gate=mapping[a['code']]
   global_fail=any(g['gate']==gate and g['status']=='FAIL' for g in report['gates']);shot_fail=any(g['gate']==gate and g['status']=='FAIL' for s in report['shot_assessments'] if s['shot']==a['shot'] for g in s['gates']);violation=any(v['shot']==a['shot'] and v['gate']==gate and v.get('failure_code')==a['code'] for v in report['violations'])
   if not(global_fail and shot_fail and violation):blocked.append('reference failure must block mapped gate: '+a['code'])
 for v in report['violations']:
  code=v.get('failure_code')
  if code in mapping and (v['gate']!=mapping[code] or not any(a['shot']==v['shot'] and a['code']==code and a['status']=='FAIL' for a in ass)):blocked.append('reference violation inconsistent: '+code)
 return blocked

def stage_status(plan,report,stage,ids,setup_ids):
 Draft202012Validator(read(ROOT/'schemas/reference-gate.schema.json')).validate(report)
 expected=CONCEPT if stage=='concept' else OPENING;ass=report['setup_assessments'];setups={s['setup_id']:s for s in plan['film_structure']['setups']}
 if report['role']!=stage or {a['setup_id'] for a in ass}!=set(setup_ids) or len(ass)!=len(setup_ids):raise ValueError('reference '+stage+' setup coverage incomplete')
 blocked=[]
 for a in ass:
  if {c['check'] for c in a['checks']}!=expected or len(a['checks'])!=len(expected):raise ValueError('reference '+stage+' check coverage incomplete')
  for c in a['checks']:
   if c['reference_id'] not in ids:raise ValueError('unretrieved stage reference')
   applicable=c['status']=='NOT_APPLICABLE' and c['check'] in ('acting','character-role') and setups[a['setup_id']]['bot_role']=='absent'
   if c['status']!='PASS' and not applicable:blocked.append(a['setup_id']+': '+c['check'])
   if c['status']=='FAIL' and not c['correction'].strip():raise ValueError('stage failure missing correction')
 if report['novelty_warnings']:blocked+=report['novelty_warnings']
 if report['status']!='PASS':blocked.append('global '+stage+' '+report['status'])
 return {'status':'PASS' if not blocked else 'REVISE_ART_DIRECTION' if stage=='concept' else 'REWORK_OPENING','blocked':blocked}

def stage_review(project,stage,evidence_path,config):
 from motif_direct import model_call
 p=Path(project);require_calibration(p,required=True);plan=read(p/'production-plan.json');ev=read(evidence_path);ref,images=context(p);base=p/'reference-gates'/stage;base.mkdir(parents=True,exist_ok=True)
 if stage=='concept':
  from motif_concept import prepare,validate_contact_proofs,beat_context,guard_deadlock,archive_review
  guard_deadlock(p,ev)
  if not (folder(p)/'beat-record.json').exists():prepare(p,config)
  validate_contact_proofs(p,ev)
  extra,beat_images,_=beat_context(p);ref+=extra;images+=beat_images
  archive_review(p)
 for item in ev['images']:
  if sha(item['file'])!=item['sha256']:raise ValueError('stage image evidence changed')
 images=[Path(x['file']) for x in ev['images']]+[Path(im['file']) for row in ev.get('contact_proofs',[]) for im in row['frames'].values()]+images
 if not ev['images']:raise ValueError('actual stage images required')
 if stage=='concept':
  if ev.get('caption_free') is not True:raise ValueError('caption-free concept previews required')
  previews=ev.get('previews',[])
  if {x['setup_id'] for x in previews}!=set(ev['setup_ids']) or len(previews)!=len(ev['setup_ids']):raise ValueError('one actual preview per concept setup required')
  for item in previews:
   if sha(item['file'])!=item['sha256']:raise ValueError('concept preview changed')
 if stage=='opening':
  from motif_quality import probe_video
  video=ev['video']
  probe=probe_video(video['file'])
  if sha(video['file'])!=video['sha256'] or not 3<=probe['duration']<=5.1 or (probe['width'],probe['height'])!=(360,640):raise ValueError('actual native 3–5 second opening motion proof required')
  if not ev.get('source_hashes'):raise ValueError('opening rendered source fingerprint required')
  second=ev.get('without_captions')
  if not second or sha(second['file'])!=second['sha256']:raise ValueError('actual caption-free opening proof required')
 prompt=(ROOT/'quality/reference-critic/PROMPT.md').read_text()+f'\nYou are the independent {stage} Art/Reference Critic. This is an INTERNAL prebuild gate, not human approval. Return role {stage}. Assess exactly STAGE EVIDENCE review_setup_ids (or setup_ids when no scoped list) and exactly these checks:'+json.dumps(sorted(CONCEPT if stage=='concept' else OPENING))+'. Review only review_setup_ids when provided; other setups are inherited unchanged and not granted new approval. Concept: judge representative rough silhouette/scale/interaction composition, not finished texture or animation. Opening: inspect actual ordered full-rate and overview evidence, both caption modes; never claim playback/listening. Purposeful dramatic minimalism may pass; absent characters may be NOT_APPLICABLE only for acting/character-role.\nPLAN:'+json.dumps(plan)+'\nSTAGE EVIDENCE IMAGE ORDER (first attachments):'+json.dumps(ev)+ref
 name=stage+'-critic';report=model_call(base,name,prompt,'schemas/reference-gate.schema.json',config,images)
 selected=read(folder(p)/'calibration.json')['selected_setup_ids'];setup_ids=ev.get('review_setup_ids',ev['setup_ids'])
 if stage=='concept':
  from motif_concept import beat_context
  _,_,beat_ids=beat_context(p);selected+=beat_ids
 status=stage_status(plan,report,stage,selected,setup_ids)
 if stage=='concept' and set(ev['setup_ids'])!={s['setup_id'] for s in plan['film_structure']['setups']}:raise ValueError('every planned setup needs a concept preview')
 write(base/'record.json',{**status,'plan_sha256':sha(p/'production-plan.json'),'calibration_record_sha256':sha(folder(p)/'record.json'),'evidence_path':str(Path(evidence_path).resolve()),'evidence_sha256':sha(evidence_path),'response_sha256':sha(base/(name+'.json')),'invocation_sha256':sha(base/(name+'-invocation.json')),'human_approval':False})
 if status['status']!='PASS':raise ValueError(stage+' '+status['status']+': '+json.dumps(status['blocked']))
 return report

def require_stage(project,stage):
 if require_calibration(project) is None:return None
 p=Path(project);base=p/'reference-gates'/stage;name=stage+'-critic'
 try:
  r=read(base/'record.json');ev=read(r['evidence_path']);report=read(base/(name+'.json'));plan=read(p/'production-plan.json')
  if r['plan_sha256']!=sha(p/'production-plan.json') or r['calibration_record_sha256']!=sha(folder(p)/'record.json') or r['evidence_sha256']!=sha(r['evidence_path']) or r['response_sha256']!=sha(base/(name+'.json')) or r['invocation_sha256']!=sha(base/(name+'-invocation.json')):raise ValueError(stage+' gate stale')
  valid_invocation(base,name)
  for im in ev['images']:
   if sha(im['file'])!=im['sha256']:raise ValueError(stage+' preview changed')
  for im in ev.get('previews',[]):
   if sha(im['file'])!=im['sha256']:raise ValueError('concept preview changed')
  if stage=='opening' and sha(ev['video']['file'])!=ev['video']['sha256']:raise ValueError('opening movie changed')
  if stage=='opening' and sha(ev['without_captions']['file'])!=ev['without_captions']['sha256']:raise ValueError('caption-free opening movie changed')
  for source,digest in ev.get('source_hashes',{}).items():
   source=Path(source).resolve()
   if not source.is_relative_to(p.resolve()) or sha(source)!=digest:raise ValueError(stage+' source changed')
  if stage=='opening' and not ev.get('source_hashes'):raise ValueError('opening rendered source fingerprint required')
  selected=read(folder(p)/'calibration.json')['selected_setup_ids']
  if stage=='concept':
   from motif_concept import validate_contact_proofs,beat_context
   validate_contact_proofs(p,ev);_,_,beat_ids=beat_context(p);selected+=beat_ids
  result=stage_status(plan,report,stage,selected,ev.get('review_setup_ids',ev['setup_ids']))
  if result['status']!='PASS' or r['status']!='PASS':raise ValueError(stage+' gate blocked')
  if stage=='concept' and set(ev['setup_ids'])!={s['setup_id'] for s in plan['film_structure']['setups']}:raise ValueError('concept coverage incomplete')
  return r
 except (FileNotFoundError,KeyError) as e:raise ValueError('fresh '+stage+' reference gate required') from e

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['verify','calibrate','concept','opening']);p.add_argument('--project',type=Path);p.add_argument('--evidence',type=Path);p.add_argument('--corpus',type=Path);a=p.parse_args()
 if a.action=='verify':
  path,m=corpus(a.corpus);result={'corpus':str(path),'videos':len(m['videos']),'setups':m['setup_count'],'source_integrity':'PASS','private':True}
 else:
  from motif_direct import backend_config
  result=calibrate(a.project,backend_config()) if a.action=='calibrate' else stage_review(a.project,a.action,a.evidence,backend_config())
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
