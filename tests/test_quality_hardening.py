"""v1.1 focused regressions; live temporal validation is recorded separately."""
import copy,json,math,re,sys,tempfile,unittest,xml.etree.ElementTree as ET
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from motif_quality import ROOT,write,read,sha,state_fingerprint,repair,evaluate,plan_check,normalize_contract,source_freshness
import test_quality_system as v1
from build_quality_fixtures import contract
from motif_quality_frames import ui_frame
from motif_ui_actions import scene
from motif_reaction import matrix,compose,point

def transform(text):
 m=matrix()
 for name,values in re.findall(r'(translate|scale|rotate|matrix)\(([^)]+)\)',text):
  v=list(map(float,re.findall(r'-?\d+(?:\.\d+)?(?:e[+-]?\d+)?',values)))
  if name=='matrix':n=tuple(v)
  elif name=='translate':n=matrix(v[0],v[1] if len(v)>1 else 0)
  elif name=='scale':n=matrix(sx=v[0],sy=v[1] if len(v)>1 else v[0])
  else:n=compose(compose(matrix(v[1],v[2]),matrix(rotation=v[0])),matrix(-v[1],-v[2])) if len(v)>1 else matrix(rotation=v[0])
  m=compose(m,n)
 return m

def xml(body):return ET.fromstring('<svg>'+re.sub(r'\b(data-layout-[a-z-]+)(?=\s|>)',r'\1=""',body)+'</svg>')
def hand_points(body):
 hands={}
 def walk(node,parent):
  m=compose(parent,transform(node.get('transform','')))
  if node.get('data-part') in ('leftHand','rightHand'):hands[node.get('data-part')]=point(m,(0,0))
  for child in node:walk(child,m)
 walk(xml(body),matrix());return hands

def reaction_target(id_,pos):return dict(id=id_,position=pos,relevance=1,amplitude=dict(x=9,y=-6,rotation=4),delay=0)
def ui_contract():
 q=contract();q['performance']=dict(state='focused',target='bot');q['reaction_radius'].update(origin=[165,790],radius=1500);q['reaction_radius']['targets']=[reaction_target('bot',[91,946]),reaction_target('plant',[660,938])];return q

class HardeningTests(unittest.TestCase):
 def reviewed(self,p):
  base=v1.QualityTests().reports(p);(p/'assets').mkdir();(p/'assets/prop.svg').write_text('<svg/>')
  m=read(base/'evidence.json');m['state_fingerprint']=state_fingerprint(p);m['render_source_hashes']=m['state_fingerprint']['render']['sources'];write(base/'evidence.json',m)
  record=read(base/'critics-record.json');record['evidence_sha256']=sha(base/'evidence.json');write(base/'critics-record.json',record);return base
 def test_art_only_repair_and_unchanged_rejection(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);self.reviewed(p)
   with self.assertRaisesRegex(ValueError,'unchanged'):repair(p,'pretend')
   (p/'assets/prop.svg').write_text('<svg><rect width="10"/></svg>')
   items=repair(p,'make hero silhouette readable');self.assertEqual(len(items),1);self.assertEqual(items[0]['changed'],{'semantic':False,'render':True});self.assertTrue((p/'quality-review/rough-before-repair-1/evidence.json').exists())
 def test_source_edits_additions_deletions_block_old_gate(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);base=self.reviewed(p);self.assertEqual(evaluate(p,'rough')['status'],'FINAL_ART_ALLOWED');m=read(base/'evidence.json')
   (p/'assets/new.css').write_text('svg{opacity:.5}')
   self.assertTrue(source_freshness(p,m));self.assertEqual(evaluate(p,'rough')['status'],'REPAIR_REQUIRED')
   (p/'assets/new.css').unlink();(p/'assets/prop.svg').unlink();self.assertTrue(source_freshness(p,m))
 def test_story_repair_archives_direction_but_art_does_not(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);self.reviewed(p);write(p/'quality-direction.json',{'pass':True});write(p/'quality-direction-record.json',{'plan_sha256':sha(p/'production-plan.json')})
   (p/'assets/prop.svg').write_text('<svg><circle/></svg>');repair(p,'art');self.assertTrue((p/'quality-direction.json').exists())
   self.reviewed_again(p)
   plan=read(p/'production-plan.json');plan['beats'][0]['quality']['after']='Visible changed consequence';write(p/'production-plan.json',plan);repair(p,'story');self.assertFalse((p/'quality-direction-record.json').exists());self.assertTrue((p/'quality-review/direction-before-repair-2/quality-direction-record.json').exists())
 def reviewed_again(self,p):
  import shutil
  shutil.copytree(p/'quality-review/rough-before-repair-1',p/'quality-review/rough')
  m=read(p/'quality-review/rough/evidence.json');m['state_fingerprint']=state_fingerprint(p);write(p/'quality-review/rough/evidence.json',m)
 def test_optional_energy_minimal_and_bot_absent(self):
  q=contract();q['energy']={'dominant_action':'Pause to compare the exposed discrepancy'};q['exit_overlap']=None;q['performance']={'state':'absent','target':''};q['art_direction'].update(bot_role='absent',environment_mode='minimal-isolated',environment_justification='Isolate the discrepancy so the viewer can compare it');q['environment']=[]
  plan={'quality_mode':'motif-gold-v1','asset_usage':[{'id':'fixture','scope':'reused'}],'shots':[{'id':'unit','quality':q}]}
  self.assertEqual(plan_check(plan)['shots'],1);self.assertIsNone(normalize_contract(q)['energy']['character_response'])
  q['art_direction']['environment_justification']=None
  with self.assertRaisesRegex(ValueError,'justification'):plan_check(plan)
  q['art_direction']['environment_mode']='physical'
  with self.assertRaisesRegex(ValueError,'meaningful cues'):plan_check(plan)
  q['environment']=['wall','floor'];q['energy']['residual_motion']='none'
  with self.assertRaisesRegex(ValueError,'dummy'):plan_check(plan)
 def test_ui_contact_reaction_pixels_determinism_and_unsafe_target(self):
  import cairosvg,io
  from PIL import Image,ImageChops
  from motif_ui_components import DEFS
  q=ui_contract();q['_cue_time']=.2
  a,contacts=ui_frame(scene,14,8,'Compare both players',5107,q)
  self.assertTrue(contacts);self.assertLess(math.dist(hand_points(a)['rightHand'],(165,790)),.2)
  self.assertIn('data-quality-reaction="plant"',a);self.assertEqual(a,ui_frame(scene,14,8,'Compare both players',5107,q)[0])
  other=copy.deepcopy(q);other['performance']['state']='burdened';b,_=ui_frame(scene,14,8,'Compare both players',5107,other);self.assertNotEqual(a,b);self.assertLess(math.dist(hand_points(b)['rightHand'],(165,790)),.2)
  def paint(body):return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=('<svg xmlns="http://www.w3.org/2000/svg" width="360" height="640" viewBox="0 0 720 1280"><defs>'+DEFS+'</defs>'+ET.tostring(xml(body),encoding='unicode')+'</svg>').encode(),url=str(ROOT/'quality/validation/fixtures/index.html')))).convert('RGB')
  self.assertIsNotNone(ImageChops.difference(paint(a),paint(b)).getbbox())
  other['reaction_radius']['targets'][0]['id']='token'
  with self.assertRaisesRegex(ValueError,'unsafe'):ui_frame(scene,14,8,'',5107,other)
 def test_ui_absent_has_no_fake_performance(self):
  q=ui_contract();q['performance']={'state':'absent','target':''};q['art_direction']['bot_role']='absent';q['reaction_radius']['targets']=[reaction_target('plant',[660,938])]
  body,contacts=ui_frame(scene,14,8,'Compare both players',5107,q);self.assertNotIn('data-part="head"',body);self.assertFalse(contacts)
 def test_calm_paper_contacts_under_reacting_carried_prop(self):
  from motif_paper_investigation import build_scene,ASSET_IDS
  assets={n:'<rect width="550" height="400" fill="#eee5d3"/>' for n in ASSET_IDS}
  q=ui_contract();q['reaction_radius']['targets']=[reaction_target('claim',[320,1050]),reaction_target('bot',[55,895])];q['reaction_radius']['origin']=[320,1050]
  kind='snap-open-then-buckle-sample-answer'
  markup,initial,events,contacts,cam=build_scene('fixture',kind,.1,3,'subject',assets,q)
  # The source frame's actual paper placement and actual canonical hand transform.
  for t in (.1,.2,.3):
   frame=[e for e in events if abs(e['time']-t)<1e-6 and 'innerHTML' in e['params']['props']]
   values={e['target']:e['params']['props']['innerHTML'] for e in frame}
   if not values:continue
   hands=hand_points(values['#fixture-bot'])
   prop=xml(values['#fixture-claim']);outer=transform(prop[0].get('transform'));inner=transform(prop[0][0].get('transform'));painted=compose(outer,inner)
   self.assertLess(math.dist(hands['leftHand'],point(painted,(20,345))),.2)
   self.assertLess(math.dist(hands['rightHand'],point(painted,(90,330))),.2)
  q['reaction_radius']['targets'][0]['id']='thread'
  with self.assertRaisesRegex(ValueError,'unsafe'):build_scene('fixture',kind,.1,3,'subject',assets,q)
 def test_dense_native_windows_cover_intermediate_frames_in_order(self):
  p=ROOT/'quality/validation/v1.1/temporal/quality-review/rough/evidence.json';manifest=read(p)
  for mode in ('with_captions','without_captions'):
   window=next(w for w in manifest[mode]['temporal_windows'] if w['shot']=='t02')
   self.assertEqual(window['frames'],list(range(84,97)));self.assertTrue(window['consecutive']);self.assertEqual(window['contact_frame'],90)
   self.assertTrue({91,92,93}<=set(window['frames']));self.assertEqual(len(window['strips_in_order']),4)
   # Frozen evidence records the original capture directory. Resolve its exact
   # relative paths against this checkout without rewriting the evidence.
   recorded_root=Path(manifest[mode]['motion_trace']).parent
   local_root=p.parent/('evidence-captions' if mode=='with_captions' else 'evidence-no-captions')
   for value in window['strips_in_order']:
    self.assertTrue((local_root/Path(value).relative_to(recorded_root)).is_file())
  # The three broken frames are absent from the unchanged eight sparse samples.
  self.assertFalse({91,92,93}&{60+round(59*i/7) for i in range(8)})
 def test_ordinary_ui_compiler_consumes_fields_into_events(self):
  from unittest.mock import patch
  import shutil
  from motif_ui_production import compile_ui,SOUND_MAP
  plan=read(ROOT/'videos/productions/voicestudio-text-directed-film/production-plan.json');plan.update(script='Compare both players.',targetFrames=60,quality_mode='motif-gold-v1',asset_usage=[{'id':'fixture','scope':'reused','path':'fixture','metadata_path':'fixture','agent_assisted':False}])
  shot=plan['shots'][0];shot.update(id='unit',kind='dual-player',startFrame=0,endFrame=60,headline='Compare both players',quality=ui_contract());plan['shots']=[shot];plan['captionPhrases']=[{'startFrame':0,'endFrame':60,'text':plan['script']}]
  words=[{'text':w,'start':i*.4,'end':(i+1)*.4,'centers':[i*.4+.2]} for i,w in enumerate(('Compare','both','players'))]
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)
   for name in ('assets/voice','assets/fonts','assets/materials','compositions','review'):(p/name).mkdir(parents=True,exist_ok=True)
   (p/'assets/voice/narration-af-nova.wav').write_bytes(b'UNIT audio boundary only');(p/'script.txt').write_text(plan['script']);(p/'assets/voice/narration.txt').write_text(plan['script']);write(p/'brief.json',{'script':plan['script'],'style':plan['style']});write(p/'production-plan.json',plan);write(p/'style-preset.json',{})
   shutil.copy2(ROOT/'quality/validation/fixtures/assets/fonts/EBGaramond-700.woff2',p/'assets/fonts/EBGaramond-700.woff2');shutil.copy2(ROOT/'quality/validation/fixtures/assets/materials/world-paper.webp',p/'assets/materials/world-paper.webp')
   # Audio/assets are unrelated to this binding test; render frame generation is real.
   ledger=[{'id':name,'file':'unit-audio','duration':.1} for name in {name for items in SOUND_MAP.values() for _,name in items}]
   with patch('motif_script.prepare_local_assets'),patch('motif_ui_production.command'),patch('motif_ui_production.make_sounds',return_value=ledger):
    a=compile_ui(p,plan,words,1.2);plan['shots'][0]['quality']['performance']['state']='worried';write(p/'production-plan.json',plan);b=compile_ui(p,plan,words,1.2)
   self.assertNotEqual(a['events'],b['events']);self.assertIn('data-performance=',a['events'][0]['params']['props']['innerHTML']);self.assertTrue((p/'quality-bindings.json').exists())
 def test_workshop_local_wrapper_keeps_prop_and_grip_common_transform(self):
  from motif_plan_compile import compile_plan
  folder=ROOT/'videos/productions/little-book-workshop';plan=read(folder/'production-plan.json');plan['quality_mode']='motif-gold-v1';plan['asset_usage']=[{'id':'fixture','scope':'reused'}]
  for b in plan['beats']:
   q=contract();q.update(focal_target=b['focus_target'],framing=b['framing']);q['performance']=dict(state='focused',target='carrier-bot' if any(a['kind']=='workshop.deliver' for a in b['actions']) else 'worker-1');q['reaction_radius']['targets']=[reaction_target('workshop-interaction',[540,1090])];q['reaction_radius'].update(origin=[540,1090],radius=600);b['quality']=q
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);words=read(folder/'assets/voice/transcript.json');voice=read(folder/'audio-plan.json')['tracks'][0]['duration'];compile_plan(p,plan,words,voice,[1,60]);h=(p/'index.html').read_text();svg=re.search(r'<svg\b.*?</svg>',h,re.S)[0];tree=xml(re.sub(r'^<svg[^>]*>|</svg>$','',svg));wrapper=next(n for n in tree.iter() if n.get('id')=='quality-reaction-workshop-interaction');ids={n.get('id') for n in wrapper.iter()};self.assertTrue({'book-carrier','grip-1-left','grip-1-right','carrier-bot'}<=ids)
   spec=read(p/'scene-events.json');self.assertTrue(any(e['target']=='#worker-1-head' and 'innerHTML' in e['params'].get('props',{}) for e in spec['events']));self.assertTrue(any(e['target']=='#quality-reaction-workshop-interaction' for e in spec['events']))
   # Every common outer affine conserves the existing contact, independent of seek.
   self.assertNotIn('grip-1-left', {e['target'].removeprefix('#') for e in spec['events'] if e['target'].startswith('#quality-reaction-')})
   other=copy.deepcopy(plan);other['beats'][0]['quality']['performance']['state']='worried';compile_plan(p,other,words,voice,[1,60]);self.assertNotEqual(spec,read(p/'scene-events.json'))
   other['beats'][0]['quality']['reaction_radius']['targets'][0]['id']='job-pages'
   with self.assertRaisesRegex(ValueError,'attached'):compile_plan(p,other,words,voice,[1,60])
if __name__=='__main__':unittest.main()
