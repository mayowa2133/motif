"""Focused quality regressions. Synthetic critic reports here are UNIT inputs only.
Live painted evidence and actual calls live under quality/validation/fixtures.
"""
import copy,json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from motif_quality import ROOT,write,read,sha,plan_check,apply_bindings,retrieve,evaluate,repair,require_gate,TECHNICAL
from motif_reaction import reaction,matrix,compose,point,grip
from motif_performance import STATES,render,channels
from motif_asset_quality import transition,digest
from build_quality_fixtures import contract
from test_directing_controls import upgraded,compile_saved
from motif_paper_energy import frame_scene
from jsonschema import Draft202012Validator

class QualityTests(unittest.TestCase):
 def test_all_named_states_use_canonical_parts_and_distinct_silhouette(self):
  for state in STATES:
   body=render(state,.3)
   for part in ('head','antennae','leftHand','rightHand','body'):
    self.assertIn('data-part="'+part+'"',body)
  self.assertNotEqual(render('burdened',.7),render('celebrating',.7))
  self.assertLess(channels('burdened',.7)['sy'],channels('celebrating',.7)['sy'])
 def test_selected_radius_is_bounded_distance_and_relevance_weighted(self):
  args=dict(age=.01,origin=[0,0],radius=100,amplitude=dict(x=12,y=8,rotation=6))
  near=reaction(position=[10,0],relevance=1,**args);far=reaction(position=[80,0],relevance=1,**args);weak=reaction(position=[10,0],relevance=.2,**args)
  self.assertGreater(abs(near['x']),abs(far['x']));self.assertGreater(abs(near['x']),abs(weak['x']))
  self.assertEqual(reaction(position=[110,0],relevance=1,**args),dict(x=0,y=0,rotation=0))
  self.assertEqual(reaction(2,[0,0],[0,0],100,1,args['amplitude']),dict(x=0.,y=0.,rotation=0.))
  with self.assertRaises(ValueError):reaction(0,[0,0],[0,0],100,1,dict(x=31,y=0,rotation=0))
 def test_grip_after_main_and_local_reaction_matches_real_anchor(self):
  prop=compose(matrix(140,220,20,.8,.8),matrix(4,-3,5));bot=compose(matrix(70,260,-10,.55,.55),matrix(0,4,-3,1.1,.9));anchor=[18,36]
  hand=grip(prop,anchor,bot);world=point(bot,hand);expected=point(prop,anchor)
  self.assertLess(sum(abs(a-b) for a,b in zip(world,expected)),1e-10)
 def test_operational_performance_changes_compiled_events_without_speech_change(self):
  folder,plan=upgraded('planned-calendar-declined');plan['quality_mode']='motif-gold-v1';plan['asset_usage']=[{'id':'fixture','scope':'reused','path':'fixture','metadata_path':'fixture','agent_assisted':False}]
  for b in plan['beats']:
   q=contract();q['focal_target']=b['focus_target'];q['framing']=b['framing'];q['performance']=dict(state='burdened',target='bot');b['quality']=q
  other=copy.deepcopy(plan);other['beats'][0]['quality']['performance']['state']='celebrating'
  with tempfile.TemporaryDirectory() as d:
   a=Path(d)/'a';b=Path(d)/'b';a.mkdir();b.mkdir();left=compile_saved(folder,plan,a);right=compile_saved(folder,other,b)
   self.assertNotEqual(left['events'],right['events']);self.assertEqual(left['captions'],right['captions'])
   self.assertEqual(read(a/'audio-plan.json'),read(b/'audio-plan.json'))
   frames=lambda s:[e['params']['props']['innerHTML'] for e in s['events'] if e['action']=='SET' and 'innerHTML' in e['params'].get('props',{})]
   self.assertIn('data-performance="burdened"',frames(left)[0]);self.assertIn('data-performance="celebrating"',frames(right)[0])
 def test_reactions_have_separate_transform_channel_and_unsafe_targets_stop(self):
  folder,plan=upgraded('planned-calendar-declined');plan['quality_mode']='motif-gold-v1';plan['asset_usage']=[{'id':'fixture','scope':'reused','path':'fixture','metadata_path':'fixture','agent_assisted':False}]
  for b in plan['beats']:
   q=contract();q.update(focal_target=b['focus_target'],framing=b['framing']);q['performance']=dict(state='focused',target='bot');b['quality']=q
  plan['beats'][0]['quality']['reaction_radius']['targets']=[dict(id='opening',position=[640,782],relevance=1,amplitude=dict(x=3,y=8,rotation=2),delay=0)]
  with tempfile.TemporaryDirectory() as d:
   spec=compile_saved(folder,plan,Path(d));h=(Path(d)/'index.html').read_text()
   self.assertIn('<g id="quality-reaction-opening"',h);self.assertTrue(any(e['target']=='#quality-reaction-opening' for e in spec['events']))
  plan['beats'][0]['quality']['reaction_radius']['targets'][0]['id']='finger'
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaisesRegex(ValueError,'attached'):compile_saved(folder,plan,Path(d))
 def test_high_energy_hook_changes_real_frame_and_preserves_contact(self):
  # Existing finite physical action, no artwork library invention.
  assets={n:'<path d="M0 0L100 0L100 100Z" fill="#eee5d3"/>' for n in ('answer-card','summary-flap','source-leaf','evidence-frame','missing-evidence','context-tab','handoff-envelope','permission-tab','source-token')}
  q=contract();q['performance']=dict(state='burdened',target='bot');q['_cue_time']=0
  a,contacts=frame_scene('catch',.5,1.5,assets,173,q)
  q['performance']['state']='celebrating';b,othercontacts=frame_scene('catch',.5,1.5,assets,173,q)
  self.assertNotEqual(a,b);self.assertTrue(contacts)
  self.assertTrue(all(c['error']<1e-8 for c in contacts+othercontacts))
 def test_actual_hand_geometry_tracks_reacting_prop_with_squashed_performance(self):
  import re,math,xml.etree.ElementTree as ET
  from motif_paper_investigation import ASSET_IDS,fragment
  folder=ROOT/'videos/productions/confidence-isnt-evidence-high-energy'
  assets={n:fragment(str((folder/'assets/props'/f'{n}.svg').relative_to(ROOT))) for n in ASSET_IDS}
  q=contract();q['performance']=dict(state='burdened',target='bot');q['_cue_time']=.2
  q['reaction_radius'].update(origin=[350,700],radius=1000)
  q['reaction_radius']['targets']=[dict(id='answer-card',position=[350,700],relevance=1,amplitude=dict(x=12,y=-8,rotation=5),delay=0)]
  def transform(text):
   result=matrix()
   for name,values in re.findall(r'(translate|scale|rotate)\(([^)]+)\)',text):
    v=list(map(float,re.findall(r'-?\d+(?:\.\d+)?(?:e[+-]?\d+)?',values)))
    if name=='translate':m=matrix(v[0],v[1] if len(v)>1 else 0)
    elif name=='scale':m=matrix(sx=v[0],sy=v[1] if len(v)>1 else v[0])
    else:m=compose(compose(matrix(v[1],v[2]),matrix(rotation=v[0])),matrix(-v[1],-v[2])) if len(v)>1 else matrix(rotation=v[0])
    result=compose(result,m)
   return result
  for t in (.3,.5,.7):
   body,grips=frame_scene('catch',t,1.5,assets,173,q)
   body=re.sub(r'\b(data-layout-[a-z-]+)(?=\s|>)',r'\1=""',body)
   root=ET.fromstring('<svg>'+body+'</svg>');hands={}
   def walk(node,parent):
    m=compose(parent,transform(node.get('transform','')))
    if node.get('data-part') in ('leftHand','rightHand'):hands[node.get('data-part')]=point(m,(0,0))
    for child in node:walk(child,m)
   walk(root,matrix())
   for contact in grips:
    self.assertLess(math.dist(hands['rightHand' if contact['side']=='r' else 'leftHand'],contact['prop_endpoint']),.2)
 def test_performance_binding_changes_native_painted_pixels(self):
  import cairosvg,io
  from PIL import Image,ImageChops
  from build_motif_bot import DEFS
  def paint(state):
   svg='<svg xmlns="http://www.w3.org/2000/svg" width="360" height="640" viewBox="0 0 1080 1920">'+DEFS+'<g transform="translate(30 400)">'+render(state,.7)+'</g></svg>'
   return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode()))).convert('RGB')
  self.assertIsNotNone(ImageChops.difference(paint('burdened'),paint('celebrating')).getbbox())
 def test_embedded_contracts_match_the_shared_source(self):
  expected=read(ROOT/'schemas/shot-contract.schema.json');expected.pop('$schema')
  for name,key in [('production-plan','beats'),('script-production-plan','beats'),('text-directed-production-plan','shots')]:
   schema=read(ROOT/f'schemas/{name}.schema.json')
   self.assertEqual(schema['properties'][key]['items']['properties']['quality'],expected)
 def test_quality_contract_required_in_existing_schemas_and_focal_binding_checked(self):
  _,plan=upgraded('planned-calendar-declined');plan['quality_mode']='motif-gold-v1';plan['asset_usage']=[{'id':'fixture','scope':'reused','path':'fixture','metadata_path':'fixture','agent_assisted':False}]
  self.assertTrue(list(Draft202012Validator(read(ROOT/'schemas/production-plan.schema.json')).iter_errors(plan)))
  for b in plan['beats']:b['quality']=contract()
  with self.assertRaisesRegex(ValueError,'focal_target'):plan_check(plan)
 def test_behavioral_retrieval_is_bounded_and_uses_internal_gold(self):
  gold=retrieve(['burden','ui-contact'],3);self.assertEqual(len(gold),3);self.assertTrue(any(g['id']=='payment-burden' for g in gold))
  self.assertTrue(all(g['clip']['file'].startswith('videos/productions/') for g in gold))
  with self.assertRaises(ValueError):retrieve(['all'],12)
 def test_missing_metadata_and_unreviewed_asset_cannot_promote(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'prop.svg';p.write_text('<svg><g id="paper"/></svg>')
   with self.assertRaisesRegex(ValueError,'metadata'):transition(dict(state='REVIEW',scope='candidate-reusable'),p,'CANONICAL')
   meta=dict(id='prop',state='REVIEW',scope='candidate-reusable',materials=['paper'],layers=['paper'],anchors={'grip':[.5,.5]},interactions=['carry'],provenance='agent-authored fixture',license='original',sha256=digest(p))
   with self.assertRaisesRegex(ValueError,'review'):transition(meta,p,'CANONICAL')
   review=dict(asset_sha256=digest(p),checks={k:'PASS' for k in ('silhouette','mobile','material','layers','anchors','geometry','interaction','alpha','provenance','licensing')},human_approved=True,reviewer='explicit test human',approved_at='2026-10-02')
   self.assertEqual(transition(meta,p,'CANONICAL',review)['state'],'CANONICAL')
   meta['scope']='scene-specific'
   with self.assertRaisesRegex(ValueError,'one-off'):transition(meta,p,'CANONICAL',review)
 def reports(self,p,fail=None):
  # Unit reports aren't used as live validation evidence.
  write(p/'production-plan.json',{'beats':[{'id':'unit','quality':contract()}]});write(p/'scene-events.json',{'events':[]})
  base=p/'quality-review/rough';base.mkdir(parents=True);video=base/'unit-media';video.write_bytes(b'unit-only');image=base/'unit-image';image.write_bytes(b'unit-only');trace=base/'trace.json';write(trace,{})
  e={'video':str(video),'probe':{'sha256':sha(video)},'motion_trace':str(trace),'trace_sha256':sha(trace)}
  write(base/'evidence.json',{'plan_sha256':sha(p/'production-plan.json'),'events_sha256':sha(p/'scene-events.json'),'with_captions':e,'without_captions':e});write(base/'image-inputs.json',[{'file':str(image),'sha256':sha(image)}])
  gates=read(ROOT/'quality/rubric/gates.json')
  for role in ('story','visual'):
   write(base/(role+'-critic.json'),{'role':role,'inspection_scope':'UNIT ONLY','gates':[{'gate':g,'status':'FAIL' if g==fail else 'PASS','evidence':'unit input'} for g in gates[role]],'shot_assessments':[{'shot':'unit','gates':[{'gate':g,'status':'FAIL' if g==fail else 'PASS','evidence':'unit input'} for g in gates[role]]}],'violations':[{'timestamp':0,'shot':'unit','gate':fail,'observation':'unit fail','gold_id':'payment-burden','smallest_correction':'repair cause'}] if fail in gates[role] else [],'sampling_limits':'unit fixture; not live inspection'})
   write(base/(role+'-critic-invocation.json'),{'exit_code':0,'saved_response_used':False,'model_fallback_used':False})
  write(base/'critics-record.json',{'evidence_sha256':sha(base/'evidence.json'),'images_sha256':sha(base/'image-inputs.json'),'gold_ids':['payment-burden'],'report_hashes':{r:sha(base/(r+'-critic.json')) for r in ('story','visual')},'invocation_hashes':{r:sha(base/(r+'-critic-invocation.json')) for r in ('story','visual')}})
  return base
 def test_story_failure_cannot_average_out_with_perfect_art(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);self.reports(p,'cause-effect');r=evaluate(p,'rough');self.assertEqual(r['status'],'REPLAN_REQUIRED');self.assertIn('story: cause-effect',r['blocked'])
 def test_pass_is_not_human_approval_and_changed_media_invalidates_gate(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);base=self.reports(p);r=evaluate(p,'rough');self.assertEqual(r['status'],'FINAL_ART_ALLOWED');self.assertFalse(r['publish']);self.assertEqual(r['human_final_approval'],'REQUIRED')
   (base/'unit-media').write_bytes(b'changed');self.assertNotEqual(evaluate(p,'rough')['status'],'FINAL_ART_ALLOWED')
 def test_missing_gate_and_edited_report_cannot_advance(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);base=self.reports(p);v=read(base/'visual-critic.json');v['gates'].pop();write(base/'visual-critic.json',v)
   self.assertNotEqual(evaluate(p,'rough')['status'],'FINAL_ART_ALLOWED')
 def test_final_gate_requires_complete_technical_evidence_and_prior_rough(self):
  import shutil
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);base=self.reports(p);shutil.copytree(base,p/'quality-review/final')
   with self.assertRaises(FileNotFoundError):require_gate(p,'final')
   t=p/'quality-review/technical.json';write(t,{'status':'PASS','events_sha256':sha(p/'scene-events.json'),'video_sha256':sha(base/'unit-media')})
   with self.assertRaisesRegex(ValueError,'coverage'):require_gate(p,'final')
   source=p/'unit-technical-evidence';source.write_bytes(b'UNIT ONLY')
   write(t,{'status':'PASS','checks':{k:'PASS' for k in TECHNICAL},'events_sha256':sha(p/'scene-events.json'),'video_sha256':sha(base/'unit-media'),'sources':[{'file':str(source),'sha256':sha(source)}]})
   result=require_gate(p,'final');self.assertEqual(result['status'],'AUDIO_FINISH_ALLOWED');self.assertEqual(result['human_final_approval'],'REQUIRED')
   source.write_bytes(b'changed')
   with self.assertRaisesRegex(ValueError,'changed'):require_gate(p,'final')
 def test_repair_budget_two_meaningful_changes_then_human(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);self.reports(p,'energy')
   with self.assertRaisesRegex(ValueError,'unchanged'):repair(p,'pretend correction')
   for i in range(2):
    write(p/'scene-events.json',{'change':i});repair(p,'change actual motion');self.reports(p,'energy')
   self.assertEqual(evaluate(p,'rough')['status'],'HUMAN_REVIEW_REQUIRED')
   with self.assertRaisesRegex(ValueError,'exhausted'):repair(p,'third change')
if __name__=='__main__':unittest.main()
