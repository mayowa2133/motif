"""Protocol tests with synthetic images and mocked responses, never creative approval."""
import sys,json,tempfile,unittest,copy
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from PIL import Image
import motif_transfer_review as tr
import motif_reference as mr
from motif_reference import write,sha,ROOT
class TransferReviewTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.p=self.root/'own';self.p.mkdir();self.kit=self.root/'kit';(self.kit/'references').mkdir(parents=True)
  for name,value in [('quality.md','human quality rubric'),('learned-prior.json','{"relationship":"contact/consequence"}')]: (self.kit/'references'/name).write_text(value)
  files={str(f.relative_to(self.kit)):sha(f) for f in self.kit.rglob('*') if f.is_file()}
  write(self.kit/'references/frozen-package.json',{'package_digest':'synthetic-test-kit','package_files':files,'repository_dependencies':{}})
  tr.enable(self.p,self.kit)
  self.plan={'film_structure':{'setups':[{'setup_id':'u','beat_ids':['b'],'bot_role':'participant','relationship_archetype':'retain','visual_rule':'hold token'}]},'beats':[{'id':'b','quality':{'art_direction':{'bot_role':'participant'}}}]};write(self.p/'production-plan.json',self.plan)
  self.contract={'version':'hero-succession-v1','beats':[{'beat_id':'b','interactions':[{'id':'touch'}]}]};write(self.p/'concept-contract.json',self.contract)
  source=self.p/'source.py';source.write_text('# synthetic own fixture')
  frames={}
  for name in ['before','contact','after']:
   f=self.p/(name+'.png');Image.new('RGB',(360,640),'white').save(f);frames[name]={'file':str(f),'sha256':sha(f)}
  self.ev={'origin':'project-authored','setup_ids':['u'],'images':[frames['contact']],'source_hashes':{str(source):sha(source)},'caption_free':True,'previews':[{'setup_id':'u',**frames['contact']}],'contact_proofs':[{'beat_id':'b','interaction_id':'touch','frames':frames}]};self.ep=self.p/'concept-evidence.json';write(self.ep,self.ev)
 def tearDown(self):self.temp.cleanup()
 def report(self,transfer=True,fail=None):
  return {**({'evidence_scope':tr.MODE} if transfer else {}),'role':'concept','status':'FAIL' if fail else 'PASS','setup_assessments':[{'setup_id':'u','checks':[{'check':c,'status':'FAIL' if c==fail else 'PASS','evidence':'synthetic test only',('basis_id' if transfer else 'reference_id'):'transfer-rubric' if transfer else 'fixture-ref','correction':'simplify' if c==fail else ''} for c in sorted(mr.CONCEPT)]}],'novelty_warnings':[],'limits':'mocked unit response, not artistic evidence'}
 def fake_call(self,base,name,prompt,schema,config,images=()):
  base=Path(base);base.mkdir(parents=True,exist_ok=True);(base/(name+'-input.txt')).write_text(prompt);(base/(name+'-output-schema.json')).write_text('{}')
  report=self.report();write(base/(name+'.json'),report);write(base/(name+'-invocation.json'),{'exit_code':0,'saved_response_used':False,'model_fallback_used':False,'input_sha256':sha(base/(name+'-input.txt')),'output_schema_sha256':sha(base/(name+'-output-schema.json')),'images':[{'file':str(Path(f).resolve()),'sha256':sha(f)} for f in images],'configuration':config});return report
 def test_own_only_review_and_receipt(self):
  with patch('motif_structure.require_structure',return_value={}),patch.object(tr,'verify_contract'),patch('motif_direct.model_call',side_effect=self.fake_call) as call:
   tr.stage_review(self.p,'concept',self.ep,{})
   attachments=call.call_args.args[-1];self.assertTrue(attachments);self.assertTrue(all(f.is_relative_to(self.p.resolve()) for f in attachments))
   self.assertFalse((self.p/'reference-calibration').exists());self.assertFalse((self.p/'reference-gates').exists())
   record=tr.require_stage(self.p,'concept');self.assertEqual(record['evidence_scope'],tr.MODE);self.assertFalse(record['human_approval']);self.assertFalse(record['source_calibration'])
   self.ev['contact_proofs'][0]['frames']['contact']['diagnostic']=True;write(self.ep,self.ev)
   with self.assertRaises(ValueError):tr.require_stage(self.p,'concept')
 def test_data_contract_uses_no_images_and_binds_scope(self):
  contract={'version':'hero-succession-v1','beats':[{'beat_id':'b','story_subject':'own fixture','causal_actor':'agent','bot_role':'participant','physical_rule':'one handoff','hero':'token','prune_inactive':[],'relationships':[{'verb':'handoff','rationale':'own change'}],'interactions':[{k:('touch' if k=='id' else 'own '+k) for k in ['id','actor','surface','support','ownership_before','ownership_after','before','contact','after','blocked_state']}]}]}
  def call(base,name,prompt,schema,config,images=()):
   self.assertEqual(tuple(images),());self.fake_call(base,name,prompt,schema,config,images);write(Path(base)/(name+'.json'),contract);return contract
  with patch('motif_structure.require_structure',return_value={}),patch('motif_direct.model_call',side_effect=call):
   tr.prepare(self.p,{});tr.verify_contract(self.p)
   inv=self.p/'transfer-review/concept-contract-invocation.json';value=mr.read(inv);value['images']=[self.ev['images'][0]];write(inv,value)
   record=self.p/'transfer-review/contract-record.json';r=mr.read(record);r['invocation_sha256']=sha(inv);write(record,r)
   with self.assertRaisesRegex(ValueError,'scope/evidence'):tr.verify_contract(self.p)
 def test_moving_critics_attach_only_own_frames_default_still_attaches_gold(self):
  import motif_quality as q
  def fixture(project):
   base=project/'quality-review/rough';base.mkdir(parents=True);write(project/'production-plan.json',self.plan);write(project/'scene-events.json',[])
   modes={}
   for mode in ('with_captions','without_captions'):
    video=project/(mode+'.test-media');video.write_text('synthetic media, probe mocked');image=project/(mode+'.png');Image.new('RGB',(360,640),'white').save(image)
    trace=project/(mode+'.json');write(trace,{'scope':'synthetic','region':[0,0,360,640],'longest_nearly_unchanged_seconds':0,'frames':[]})
    modes[mode]={'video':str(video),'probe':{'sha256':sha(video)},'sheets':[str(image)],'motion_trace':str(trace)}
   write(base/'evidence.json',{'plan_sha256':sha(project/'production-plan.json'),'events_sha256':sha(project/'scene-events.json'),'inspection':'synthetic test only',**modes});return base
  base=fixture(self.p)
  with patch.object(q,'source_freshness',return_value=[]),patch.object(q,'retrieve',side_effect=AssertionError('no old gold retrieval')),patch.object(q,'evaluate',return_value={}),patch('motif_direct.model_call',side_effect=self.fake_call) as call:
   q.critics(self.p,'rough',{})
   for c in call.call_args_list:
    self.assertTrue(all(f.resolve().is_relative_to(self.p.resolve()) for f in c.kwargs['images']));self.assertIn('NOT retrieved clip pixels',c.args[2])
   r=mr.read(base/'critics-record.json');self.assertEqual(r['basis_ids'],['transfer-rubric','learned-prior']);self.assertFalse(r['source_calibration'])
  legacy=self.root/'legacy-moving';legacy.mkdir();fixture(legacy);clip=self.root/'old.test-media';clip.write_text('mock gold');image=self.root/'old.png';Image.new('RGB',(360,640),'white').save(image)
  gold={'id':'old-gold','why_passes':'synthetic default gold','clip':{'file':str(clip),'sha256':sha(clip),'frames':[0,2]}}
  with patch.object(q,'source_freshness',return_value=[]),patch.object(q,'retrieve',return_value=[gold]),patch.object(q,'evidence',return_value={'sheets':[str(image)]}),patch.object(q,'evaluate',return_value={}),patch('motif_direct.model_call',side_effect=self.fake_call) as call:
   q.critics(legacy,'rough',{})
   self.assertTrue(all(image in c.kwargs['images'] for c in call.call_args_list));self.assertNotIn('evidence_scope',mr.read(legacy/'quality-review/rough/critics-record.json'))
 def test_external_symlink_stale_and_non_native_rejected(self):
  outside=self.root/'external.png';Image.new('RGB',(360,640),'white').save(outside)
  with self.assertRaises(ValueError):tr.own_file(self.p,{'file':str(outside),'sha256':sha(outside)})
  link=self.p/'alias.png';link.symlink_to(outside)
  with self.assertRaises(ValueError):tr.own_file(self.p,{'file':str(link),'sha256':sha(link)})
  inside=self.p/'small.png';Image.new('RGB',(100,100),'white').save(inside)
  with self.assertRaises(ValueError):tr.own_file(self.p,{'file':str(inside),'sha256':sha(inside)},True)
  with self.assertRaises(ValueError):tr.own_file(self.p,{'file':str(inside),'sha256':'old'})
 def test_no_missing_or_inapplicable_checks_pass(self):
  r=self.report(fail='CONTACT_PROOF_UNREADABLE');self.assertNotEqual(tr.status(self.plan,r,'concept',['u'])['status'],'PASS')
  r=self.report();r['setup_assessments'][0]['checks'].pop()
  with self.assertRaises(ValueError):tr.status(self.plan,r,'concept',['u'])
  r=self.report();r['setup_assessments'][0]['checks'][0]['status']='NOT_ASSESSED';self.assertNotEqual(tr.status(self.plan,r,'concept',['u'])['status'],'PASS')
  r=self.report();c=next(c for c in r['setup_assessments'][0]['checks'] if c['check']=='CONTACT_PROOF_UNREADABLE');c['status']='NOT_APPLICABLE';self.assertNotEqual(tr.status(self.plan,r,'concept',['u'])['status'],'PASS')
 def test_rubric_and_conflicting_calibration_rejected(self):
  (self.kit/'references/quality.md').write_text('changed')
  with self.assertRaises(ValueError):tr.profile(self.p)
  # New synthetic profile for the conflict test.
  (self.kit/'references/quality.md').write_text('human quality rubric');write(self.p/'reference-calibration/required.json',{})
  with self.assertRaises(ValueError):tr.profile(self.p)
 def test_explicit_dispatch_and_default_calibrated_route(self):
  import motif_concept
  with patch.object(tr,'prepare',return_value='own') as own,patch('motif_concept.require_calibration') as old:
   self.assertEqual(motif_concept.prepare(self.p,{}),'own');old.assert_not_called()
  legacy=self.root/'legacy';legacy.mkdir()
  with patch.object(tr,'stage_review') as own,patch('motif_reference.require_calibration',side_effect=RuntimeError('original calibrated gate')) as old:
   with self.assertRaisesRegex(RuntimeError,'original calibrated'):mr.stage_review(legacy,'concept',legacy/'evidence.json',{})
   old.assert_called_once_with(legacy,required=True);own.assert_not_called()
  # Existing status criteria still require external reference IDs, never textual basis IDs.
  result=mr.stage_status(self.plan,self.report(False),'concept',['fixture-ref'],['u']);self.assertEqual(result['status'],'PASS')
  with self.assertRaises(ValueError):mr.stage_status(self.plan,self.report(False),'concept',['transfer-rubric'],['u'])
 def test_opening_scope_does_not_require_unseen_later_setups(self):
  self.plan['film_structure']['setups'].append({'setup_id':'later','beat_ids':['later-beat'],'bot_role':'absent'});write(self.p/'production-plan.json',self.plan)
  ev={**self.ev,'video':{'file':str(self.p/'own.mp4'),'sha256':''},'without_captions':{'file':str(self.p/'own-clean.mp4'),'sha256':''}}
  for field in ('video','without_captions'):
   Path(ev[field]['file']).write_text('synthetic video, mock probe');ev[field]['sha256']=sha(ev[field]['file'])
  timing=self.p/'setup-timing.json';write(timing,{'plan_sha256':sha(self.p/'production-plan.json'),'setups':[{'setup_id':'u','start':0,'end':4},{'setup_id':'later','start':4,'end':8}]});ev['setup_timing']={'file':str(timing.resolve()),'sha256':sha(timing)};ev['source_hashes'][str(timing.resolve())]=sha(timing)
  def sample(video,out,shots):
   out.mkdir(parents=True);f=out/'decoded.png';Image.new('RGB',(360,640),'black').save(f);trace=out/'motion-trace.json';write(trace,{'frames':[0,1]})
   return {'sheets':[str(f.resolve())],'motion_trace':str(trace.resolve()),'trace_sha256':sha(trace)}
  with patch('motif_quality.probe_video',return_value={'duration':4,'width':360,'height':640,'fps':30,'frames':120}),patch('motif_quality.evidence',side_effect=sample) as sampler:
   with self.assertRaises(KeyError):tr.evidence_images(self.p,'opening',ev) # Arbitrary still alone is not temporal evidence.
   sampled=tr.sample_opening(self.p,ev);self.assertEqual(sampler.call_count,2);self.assertTrue(tr.evidence_images(self.p,'opening',sampled))
   unrelated={**sampled,'images':ev['images']}
   with self.assertRaisesRegex(ValueError,'derive from both'):tr.evidence_images(self.p,'opening',unrelated)
   with self.assertRaisesRegex(ValueError,'reviewed interval'):tr.opening_inputs(self.p,{**ev,'setup_ids':['later']})
  self.assertEqual(tr.review_setup_ids(self.plan,'opening',ev),['u'])
  report=self.report();report['role']='opening';report['setup_assessments'][0]['checks']=[{'check':c,'status':'PASS','basis_id':'transfer-rubric','evidence':'synthetic','correction':''} for c in sorted(mr.OPENING)]
  self.assertEqual(tr.status(self.plan,report,'opening',['u'])['status'],'PASS')
  with self.assertRaisesRegex(ValueError,'concept setup coverage'):tr.review_setup_ids(self.plan,'concept',ev)
  for bad in (['unknown'],['u','u'],[]):
   with self.assertRaises(ValueError):tr.review_setup_ids(self.plan,'opening',{**ev,'setup_ids':bad})
  with self.assertRaises(ValueError):tr.review_setup_ids(self.plan,'opening',{**ev,'review_setup_ids':['later']})
 def test_deadlock_counts_completed_current_and_archived_without_current_pixels(self):
  for j in range(2):
   base=self.p/('transfer-concept-history/first' if j==0 else 'transfer-gates/concept');base.mkdir(parents=True)
   self.fake_call(base,'concept-critic','different'+str(j),tr.SCHEMA,{**tr.binding(self.p)},())
   write(base/'concept-critic.json',self.report(fail='hero-scale'))
   write(base/'reviewed-plan.json',self.plan)
   write(base/'record.json',{'response_sha256':sha(base/'concept-critic.json'),'invocation_sha256':sha(base/'concept-critic-invocation.json'),'plan_sha256':sha(base/'reviewed-plan.json'),'reviewed_plan_sha256':sha(base/'reviewed-plan.json')})
  with self.assertRaisesRegex(ValueError,'deadlock'):tr.guard_transfer_deadlock(self.p)
  # Renaming setup/beat/interaction IDs or rewording the physical rule does not reset.
  self.plan['film_structure']['setups'][0]['setup_id']='renamed';self.plan['film_structure']['setups'][0]['visual_rule']='same mechanism paraphrased';write(self.p/'production-plan.json',self.plan)
  with self.assertRaisesRegex(ValueError,'deadlock'):tr.guard_transfer_deadlock(self.p)
  old=self.p/'transfer-concept-history/first/reviewed-plan.json';patchfile=self.p/'split-patch.json';write(patchfile,{'escape':'split','setups':[{'relationship_archetype':'retain'},{'relationship_archetype':'handoff'}]})
  self.plan['film_structure']['setups']=[{'setup_id':'split-a','beat_ids':['b'],'bot_role':'participant','relationship_archetype':'compare','visual_rule':'new'},{'setup_id':'split-b','beat_ids':['c'],'bot_role':'absent','relationship_archetype':'handoff','visual_rule':'other'}];write(self.p/'production-plan.json',self.plan)
  with self.assertRaisesRegex(ValueError,'deadlock'):tr.guard_transfer_deadlock(self.p) # Changed names/rules without validated escape insufficient.
  value=mr.read(patchfile);value['fixture_result']=copy.deepcopy(self.plan);write(patchfile,value)
  with patch('motif_concept.apply_patch',side_effect=lambda old,sid,v,**kwargs:v['fixture_result']) as validation:
   tr.record_escape(self.p,old,'u',patchfile);tr.guard_transfer_deadlock(self.p);validation.assert_called();self.assertTrue(old.exists())
   # A later real-family failure/escape must not resurrect already escaped history.
   prior_new=None
   for j in range(2):
    base=self.p/'transfer-concept-history'/('second'+str(j));self.fake_call(base,'concept-critic','second-family'+str(j),tr.SCHEMA,tr.binding(self.p),());r=self.report(fail='hero-scale');r['setup_assessments'][0]['setup_id']='split-a';write(base/'concept-critic.json',r);write(base/'reviewed-plan.json',self.plan);write(base/'record.json',{'response_sha256':sha(base/'concept-critic.json'),'invocation_sha256':sha(base/'concept-critic-invocation.json'),'plan_sha256':sha(base/'reviewed-plan.json'),'reviewed_plan_sha256':sha(base/'reviewed-plan.json')});prior_new=base/'reviewed-plan.json'
   with self.assertRaisesRegex(ValueError,'deadlock'):tr.guard_transfer_deadlock(self.p)
   self.plan['film_structure']['setups'][0]['relationship_archetype']='transform';write(self.p/'production-plan.json',self.plan);second=self.p/'second-patch.json';write(second,{'escape':'change-archetype','setups':[{'relationship_archetype':'transform'}],'fixture_result':copy.deepcopy(self.plan)})
   tr.record_escape(self.p,prior_new,'split-a',second);tr.guard_transfer_deadlock(self.p);self.assertEqual(len(list((self.p/'transfer-review/escapes').glob('*/receipt.json'))),2)
   # Mutable user patch/prior current paths can change; immutable snapshots remain valid.
   write(patchfile,{'now':'changed own input'});tr.guard_transfer_deadlock(self.p)
  self.plan['film_structure']['setups'][0]['visual_rule']='cosmetic attempt';write(self.p/'production-plan.json',self.plan)
  write(patchfile,{'escape':'simplify','setups':[{'relationship_archetype':'retain'}]})
  with self.assertRaisesRegex(ValueError,'changed relationship'):tr.record_escape(self.p,old,'u',patchfile)
 def test_transfer_planning_direction_structure_use_no_old_context(self):
  import motif_quality as q, motif_structure as st, motif_news as news
  old_read=st.read
  def no_legacy(path):
   if 'rowhouse' in str(path) or 'structure-examples' in str(path):raise AssertionError('forbidden old example')
   return old_read(path)
  brief={'script':'A small task finishes.','audience':'workers','style':'reference-expressive-high-energy-v1'}
  with patch.object(q,'retrieve',side_effect=AssertionError('forbidden gold')),patch.object(st,'read',side_effect=no_legacy):
   self.assertIn('LEARNED METADATA',q.planning_context('own',self.p));self.assertNotIn('House +',q.planning_context('own',self.p));st.critic_prompt(self.plan,self.p)
   # Actual news planner caller propagates profile scope to planning context.
   with patch.object(news,'ROOT',self.root),patch.object(news,'read',return_value={}):self.assertIn('LEARNED METADATA',news.planner_prompt(brief,{},self.p))
   write(self.p/'transfer-gates/concept/record.json',{})
   def direction_call(*args,**kwargs):self.fake_call(*args,**kwargs);return {'pass':True,'issues':[]}
   with patch.object(q,'plan_check'),patch.object(st,'require_structure',return_value={}),patch.object(mr,'require_stage',return_value={}),patch('motif_direct.model_call',side_effect=direction_call):q.direction_review(self.p,self.plan,{})
 def test_opening_samples_are_decoded_from_both_own_movies(self):
  import motif_quality as q
  ev={**self.ev};ev['source_hashes']=dict(self.ev['source_hashes'])
  for field,color in [('video','red'),('without_captions','blue')]:
   movie=self.p/(field+'.mp4');q.cmd(['ffmpeg','-v','error','-f','lavfi','-i','color=c='+color+':s=360x640:r=4:d=3','-c:v','libx264','-pix_fmt','yuv420p',movie]);ev[field]={'file':str(movie.resolve()),'sha256':sha(movie)}
  timing=self.p/'setup-timing.json';write(timing,{'plan_sha256':sha(self.p/'production-plan.json'),'setups':[{'setup_id':'u','start':0,'end':3}]});ev['setup_timing']={'file':str(timing.resolve()),'sha256':sha(timing)};ev['source_hashes'][str(timing.resolve())]=sha(timing)
  sampled=tr.sample_opening(self.p,ev);tr.evidence_images(self.p,'opening',sampled)
  for mode,channel in [('with_captions',0),('without_captions',2)]:
   entry=sampled['decoded_opening_samples'][mode];native=next(f for f in entry['sheets'] if '-native-' in f)
   with Image.open(native) as image:pixel=image.convert('RGB').getpixel((180,320))
   self.assertGreater(pixel[channel],200);self.assertEqual(len(entry['motion_observations']['frames']),12)
  # Test fixture is synthetic media, not a story, live critic or creative PASS.
 def test_real_unmocked_transfer_escape_preserves_validation_without_old_limits(self):
  from motif_concept import apply_patch
  from test_structure import plan as fixture_plan
  plan=fixture_plan();plan.update({'schema_version':'script-1.0','audience':'synthetic reviewer','style':'reference-expressive-high-energy-v1','rationale':'protocol fixture','metaphor':'own paper change','ending_action':'release','limitations':[],'assets':[{'id':'planning-paper','description':'synthetic own asset','reuse_path':''}]})
  required=mr.read(ROOT/'schemas/script-production-plan.schema.json')['properties']['beats']['items']['required']
  for b in plan['beats']:
   for name in required:
    if name not in b:b[name]='synthetic own '+name
   b.update({'needed_assets':['planning-paper'],'actions':[{'kind':'own-action','cue':b['narration'].split()[0],'requires':[],'produces':[]}],'framing':'subject'})
  original=plan['film_structure']['setups'][0];replacement=copy.deepcopy(original);replacement['relationship_archetype']='transform';replacement['visual_rule']='Own material changes state'
  patch_value={'reason':'synthetic changed relationship','escape':'change-archetype','setups':[replacement],'beats':copy.deepcopy(plan['beats']),'token_changes':[]}
  old=self.p/'transfer-concept-history/real';self.fake_call(old,'concept-critic','own complete real-validation fixture',tr.SCHEMA,tr.binding(self.p),());report=self.report(fail='hero-scale');report['setup_assessments'][0]['setup_id']=original['setup_id'];write(old/'concept-critic.json',report);write(old/'reviewed-plan.json',plan);write(old/'record.json',{'response_sha256':sha(old/'concept-critic.json'),'invocation_sha256':sha(old/'concept-critic-invocation.json'),'plan_sha256':sha(old/'reviewed-plan.json'),'reviewed_plan_sha256':sha(old/'reviewed-plan.json')})
  output=apply_patch(plan,original['setup_id'],patch_value,transfer=True);write(self.p/'production-plan.json',output);patchfile=self.p/'real-patch.json';write(patchfile,patch_value)
  tr.record_escape(self.p,old/'reviewed-plan.json',original['setup_id'],patchfile);tr.guard_transfer_deadlock(self.p)
  limits=' '.join(output['limitations']);self.assertNotIn('eight unaffected',limits);self.assertNotIn('Private visual evidence',limits);self.assertNotIn('No animation or full rough is authorized',limits);self.assertIn('fresh own-evidence concept review',limits)
  # Default scope retains its existing static-only constraints; transfer didn't weaken pure validation.
  self.assertIn('No animation or full rough is authorized',' '.join(apply_patch(plan,original['setup_id'],patch_value)['limitations']))
  bad=copy.deepcopy(patch_value);bad['beats'][0]['narration']='Changed copy'
  with self.assertRaisesRegex(ValueError,'narration'):apply_patch(plan,original['setup_id'],bad,transfer=True)
 def test_opening_timing_must_cover_entire_video_and_be_finite(self):
  import motif_quality as q
  ev={**self.ev};ev['source_hashes']=dict(self.ev['source_hashes'])
  for field in ('video','without_captions'):
   f=self.p/(field+'.test');f.write_text('synthetic probe fixture');ev[field]={'file':str(f),'sha256':sha(f)}
  timing=self.p/'timing.json'
  for end in (1,float('inf'),float('nan')):
   write(timing,{'plan_sha256':sha(self.p/'production-plan.json'),'setups':[{'setup_id':'u','start':0,'end':end}]});ev['setup_timing']={'file':str(timing.resolve()),'sha256':sha(timing)};ev['source_hashes'][str(timing.resolve())]=sha(timing)
   with patch.object(q,'probe_video',return_value={'duration':4,'width':360,'height':640,'fps':30,'frames':120}),self.assertRaises(ValueError):tr.opening_inputs(self.p,ev)
 def test_voice_build_require_fresh_transfer_concept_and_direction_binding(self):
  import motif_news as news
  concept=self.p/'transfer-gates/concept/record.json';write(concept,{'fresh':'initial'});write(self.p/'quality-direction.json',{'pass':True});write(self.p/'quality-direction-invocation.json',{})
  record={**tr.binding(self.p),'plan_sha256':sha(self.p/'production-plan.json'),'response_sha256':sha(self.p/'quality-direction.json'),'invocation_sha256':sha(self.p/'quality-direction-invocation.json'),'transfer_concept_gate_sha256':sha(concept)};write(self.p/'quality-direction-record.json',record)
  with patch.object(news,'require_structure'),patch.object(mr,'require_stage',return_value={}) as stage:
   news.require_direction(self.p);stage.assert_called_with(self.p,'concept')
   write(concept,{'fresh':'replaced'})
   with patch.object(news,'command') as tts,patch.object(news.runpy,'run_path') as build:
    for action in (news.voice,news.build):
     with self.assertRaisesRegex(ValueError,'transfer/concept evidence stale'):action(self.p)
    tts.assert_not_called();build.assert_not_called()
   record['transfer_concept_gate_sha256']=sha(concept);record['transfer_profile_sha256']='changed';write(self.p/'quality-direction-record.json',record)
   with self.assertRaisesRegex(ValueError,'transfer/concept evidence stale'):news.require_direction(self.p)
 def test_transfer_news_plan_stops_before_concept_direction(self):
  import motif_news as news
  production=self.root/'videos/productions';production.mkdir(parents=True);project=production/'new';tr.enable(project,self.kit)
  brief={'slug':'new','script':'A small task finishes.','audience':'workers','style':'reference-expressive-high-energy-v1'};source={'as_of':'2026-10-04','sources':['owned brief'],'visual_fact_rules':['no new claims']};bp=self.root/'brief.json';sp=self.root/'sources.json';write(bp,brief);write(sp,source)
  with patch.object(news,'ROOT',self.root),patch.object(news,'backend_config',return_value={}),patch.object(news,'planner_prompt',return_value='own prompt'),patch.object(news,'model_call',return_value=self.plan),patch.object(news,'validate_script'),patch.object(news,'structure_review'),patch.object(news,'direction_review') as direction:
   self.assertEqual(news.plan_news(bp,sp),project);direction.assert_not_called();self.assertTrue((project/'production-plan.json').exists())
if __name__=='__main__':unittest.main()
