"""Reference ownership, retrieval and blocking gates; no pixel-similarity rules."""
import copy,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from motif_reference import corpus,write,sha,select_setups,reference_failures,stage_status,CONCEPT,OPENING,require_stage,require_calibration
from motif_reference_ingest import ingest
from motif_quality import ROOT

class ReferenceTests(unittest.TestCase):
 def test_registered_sources_survive_without_upload_paths(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);videos=[]
   for i in range(7):
    src=p/f'{i}.mp4';src.write_bytes(bytes([i]));videos.append({'id':str(i),'source_path':str(src),'original_path':'/unavailable/uploads','sha256':sha(src),'status':'REGISTERED'})
   write(p/'manifest.json',{'private':True,'videos':videos,'setup_count':7})
   self.assertEqual(len(corpus(p)[1]['videos']),7)
   (p/'0.mp4').write_bytes(b'changed')
   with self.assertRaisesRegex(ValueError,'changed'):corpus(p)
 def test_incomplete_or_duplicate_corpus_cannot_register(self):
  with self.assertRaisesRegex(ValueError,'seven distinct'):ingest([Path('one.mp4')]*7)
  with tempfile.TemporaryDirectory() as d:
   write(Path(d)/'manifest.json',{'private':True,'videos':[],'setup_count':0})
   with self.assertRaisesRegex(ValueError,'complete'):corpus(d)
 def test_retrieval_matches_relationships_not_topic_words(self):
  sets=[{'id':f's{i}','duration':2,'relationships':['approval'],'physical_interaction':'submit retained key'} for i in range(4)]
  other={'id':'topic-dots','duration':2,'relationships':['price'],'physical_interaction':'price column'}
  m={'videos':[{'id':'a','setups':sets},{'id':'b','setups':[other]}]};q={'relationships':[{'verb':'approval','rationale':'Dots price topic but user approval relationship'}]}
  result=select_setups(m,q,3,0);self.assertNotIn('topic-dots',[s['id'] for s in result])
  with self.assertRaisesRegex(ValueError,'insufficient'):select_setups(m,{'relationships':[{'verb':'restore'}]},3,0)
 def report(self,absent=False):
  mapping=json.loads((ROOT/'quality/reference-critic/policy.json').read_text())['codes'];p={'beats':[{'id':'b','quality':{'performance':{'state':'absent' if absent else 'focused'}}}]}
  r={'reference_assessments':[{'shot':'b','code':c,'status':'NOT_APPLICABLE' if absent and c=='REFERENCE_ACTING_GAP' else 'PASS','reference_id':'ref','evidence':'UNIT'} for c in mapping],'gates':[],'shot_assessments':[],'violations':[]};return p,r
 def test_absent_character_does_not_fail_acting_but_other_na_blocks(self):
  p,r=self.report(True);self.assertEqual(reference_failures(p,r,['ref']),[])
  r['reference_assessments'][0]['status']='NOT_APPLICABLE';self.assertTrue(reference_failures(p,r,['ref']))
  p,r=self.report(False);r['reference_assessments'][2]['status']='NOT_APPLICABLE';self.assertTrue(reference_failures(p,r,['ref']))
 def test_false_pass_and_unretrieved_evidence_cannot_hide_interaction_failure(self):
  p,r=self.report();a=next(a for a in r['reference_assessments'] if a['code']=='REFERENCE_INTERACTION_GAP');a['status']='FAIL'
  self.assertIn('reference failure must block mapped gate: REFERENCE_INTERACTION_GAP',reference_failures(p,r,['ref']))
  r['gates']=[{'gate':'physicality','status':'FAIL'}];r['shot_assessments']=[{'shot':'b','gates':r['gates']}];r['violations']=[{'shot':'b','gate':'physicality','failure_code':a['code']}]
  self.assertNotIn('reference failure must block mapped gate: '+a['code'],reference_failures(p,r,['ref']))
  self.assertTrue(any('unretrieved' in x for x in reference_failures(p,r,['other'])))
 def test_concept_requires_every_check_and_novelty_warning_blocks(self):
  p={'film_structure':{'setups':[{'setup_id':'s','bot_role':'absent'}]}}
  r={'role':'concept','status':'PASS','setup_assessments':[{'setup_id':'s','checks':[{'check':c,'status':'NOT_APPLICABLE' if c=='character-role' else 'PASS','evidence':'intentional pause serves the unresolved question','reference_id':'ref','correction':''} for c in CONCEPT]}],'novelty_warnings':[],'limits':'UNIT'}
  self.assertEqual(stage_status(p,r,'concept',['ref'],['s'])['status'],'PASS')
  r['novelty_warnings']=['Same hero, set and choreography copied'];self.assertEqual(stage_status(p,r,'concept',['ref'],['s'])['status'],'REVISE_ART_DIRECTION')
  r['setup_assessments'][0]['checks'].pop()
  with self.assertRaisesRegex(ValueError,'coverage'):stage_status(p,r,'concept',['ref'],['s'])
 def test_missing_calibration_blocks_ordinary_planner_before_model(self):
  from motif_direct import model_call
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);cli=p/'cli';cli.touch();cli.chmod(0o755);write(p/'brief.json',{'script':'A supplied script.'})
   with patch('motif_reference.corpus',side_effect=ValueError('corpus missing')),patch('motif_direct.subprocess.run') as call:
    with self.assertRaisesRegex(ValueError,'corpus missing'):model_call(p,'initial-plan','plan','schemas/script-production-plan.schema.json',{'cli_path':str(cli)})
    call.assert_not_called()
 def test_required_record_has_no_legacy_saved_response_fallback(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);self.assertIsNone(require_calibration(p));write(p/'reference-calibration/required.json',{'required':True})
   with self.assertRaisesRegex(ValueError,'fresh Reference Calibration'):require_calibration(p)
 def test_opening_pass_cannot_survive_changed_rendered_source(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);b=p/'reference-gates/opening';b.mkdir(parents=True);source=p/'opening.py';source.write_text('original');movie=p/'proof.mp4';movie.write_bytes(b'proof');frame=p/'frame.png';frame.write_bytes(b'frame')
   write(p/'production-plan.json',{'film_structure':{'setups':[{'setup_id':'s','bot_role':'participant'}]}});write(p/'reference-calibration/record.json',{});write(p/'reference-calibration/calibration.json',{'selected_setup_ids':['ref']})
   report={'role':'opening','status':'PASS','setup_assessments':[{'setup_id':'s','checks':[{'check':c,'status':'PASS','evidence':'UNIT','reference_id':'ref','correction':''} for c in OPENING]}],'novelty_warnings':[],'limits':'UNIT'};write(b/'opening-critic.json',report);write(b/'opening-critic-invocation.json',{})
   ev=p/'evidence.json';write(ev,{'setup_ids':['s'],'images':[{'file':str(frame),'sha256':sha(frame)}],'video':{'file':str(movie),'sha256':sha(movie)},'without_captions':{'file':str(movie),'sha256':sha(movie)},'source_hashes':{str(source):sha(source)}})
   write(b/'record.json',{'status':'PASS','plan_sha256':sha(p/'production-plan.json'),'calibration_record_sha256':sha(p/'reference-calibration/record.json'),'evidence_path':str(ev),'evidence_sha256':sha(ev),'response_sha256':sha(b/'opening-critic.json'),'invocation_sha256':sha(b/'opening-critic-invocation.json')})
   with patch('motif_reference.require_calibration',return_value={}),patch('motif_reference.valid_invocation',return_value={}):
    self.assertEqual(require_stage(p,'opening')['status'],'PASS');source.write_text('changed choreography')
    with self.assertRaisesRegex(ValueError,'source changed'):require_stage(p,'opening')
 def test_audio_tail_cannot_generate_nonexistent_source_frames(self):
  import io
  from types import SimpleNamespace
  from motif_reference_ingest import evidence
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);source=p/'source.mp4';source.write_bytes(b'fixture');write(p/'v/setup-indexer-invocation.json',{})
   m={'videos':[{'id':'v','source_path':str(source),'duration':.55}]};index={'videos':[{'id':'v','audio_caption_rhythm':'uninspected','setups':[{'start':0,'end':.55,'action_center':.25}]}],'inspection_scope':'UNIT'}
   process=SimpleNamespace(stdout=io.BytesIO(bytes(360*640*3*12)),wait=lambda:0)
   with patch('motif_reference_ingest.subprocess.check_output',return_value=b'{"streams":[{"nb_frames":"12","duration":"0.4"}]}'),patch('motif_reference_ingest.subprocess.Popen',return_value=process):
    result=evidence(p,m,index)
   setup=result['videos'][0]['setups'][0];self.assertEqual(setup['end_frame'],12);self.assertEqual(setup['end'],.4)
   self.assertTrue(all(n<12 for e in setup['evidence'].values() for n in e['source_frames']))
if __name__=='__main__':unittest.main()
