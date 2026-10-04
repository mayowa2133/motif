"""Protocol tests with synthetic images and mocked responses, never creative approval."""
import sys,json,tempfile,unittest
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
  self.plan={'film_structure':{'setups':[{'setup_id':'u','beat_ids':['b'],'bot_role':'participant'}]},'beats':[{'id':'b','quality':{'art_direction':{'bot_role':'participant'}}}]};write(self.p/'production-plan.json',self.plan)
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
 def test_deadlock_counts_completed_current_and_archived_without_current_pixels(self):
  for j in range(2):
   base=self.p/('transfer-concept-history/first' if j==0 else 'transfer-gates/concept');base.mkdir(parents=True)
   self.fake_call(base,'concept-critic','different'+str(j),tr.SCHEMA,{**tr.binding(self.p)},())
   write(base/'concept-critic.json',self.report(fail='hero-scale'))
   write(base/'record.json',{'response_sha256':sha(base/'concept-critic.json'),'invocation_sha256':sha(base/'concept-critic-invocation.json')})
  with self.assertRaisesRegex(ValueError,'deadlock'):tr.guard_transfer_deadlock(self.p)
if __name__=='__main__':unittest.main()
