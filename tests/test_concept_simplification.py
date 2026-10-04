"""Semantic gate coverage, locked scope, native contact proofs and deadlock budget."""
import copy,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from motif_concept import select_beat_references,validate_contact_proofs,guard_deadlock,deadlock_history,apply_patch
from motif_reference import ROOT,read,write,sha
from motif_structure import report_status

class ConceptTests(unittest.TestCase):
 def test_per_beat_retrieval_does_not_reuse_topic_or_other_beat(self):
  manifest={'videos':[{'id':'v','setups':[{'id':'connect','relationships':['interface-interaction'],'duration':1},{'id':'pass','relationships':['handoff'],'duration':2},{'id':'dots','relationships':['price'],'duration':1}]}]}
  contract={'beats':[{'beat_id':'a','physical_rule':'engage','relationships':[{'verb':'interface-interaction'}]},{'beat_id':'b','physical_rule':'transfer','relationships':[{'verb':'handoff'}]}]}
  result=select_beat_references(manifest,contract)
  self.assertEqual([[s['id'] for s in r['selected']] for r in result],[['connect'],['pass']])
 def proof(self,p):
  write(p/'concept-contract.json',{'beats':[{'beat_id':'b','interactions':[{'id':'contact'}]}]});states={}
  for state in ['before','contact','after']:
   f=p/(state+'.png');Image.new('RGB',(360,640),'teal').save(f);states[state]={'file':str(f),'sha256':sha(f)}
  return {'setup_ids':['s'],'contact_proofs':[{'beat_id':'b','interaction_id':'contact','frames':states}]}
 def test_missing_contact_wrong_size_or_diagnostic_cannot_pass(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);e=self.proof(p);self.assertTrue(validate_contact_proofs(p,e))
   e['contact_proofs'][0]['frames']['contact']['diagnostic']=True
   with self.assertRaisesRegex(ValueError,'clean'):validate_contact_proofs(p,e)
   e=self.proof(p);f=Path(e['contact_proofs'][0]['frames']['contact']['file']);Image.new('RGB',(720,1280)).save(f);e['contact_proofs'][0]['frames']['contact']['sha256']=sha(f)
   with self.assertRaisesRegex(ValueError,'native'):validate_contact_proofs(p,e)
   e['contact_proofs']=[]
   with self.assertRaisesRegex(ValueError,'coverage'):validate_contact_proofs(p,e)
 def test_all_three_new_semantic_checks_are_required_and_block(self):
  from test_structure import plan,report
  p=plan();r=report(p)
  for code in ['COMPOUND_VISUAL_RULE','UNNECESSARY_VISIBLE_MECHANISM','ACTOR_AMBIGUITY']:
   c=next(c for c in r['checks'] if c['check']==code);c['status']='FAIL';sid=p['film_structure']['setups'][0]['setup_id'];r['setup_assessments'][0]['status']='FAIL'
   r['violations']=[{'code':code,'setup_ids':[sid],'observation':'UNIT only: separate mechanism','smallest_structural_correction':'Split physical rules'}]
   self.assertEqual(report_status(p,r),'REPLAN_REQUIRED');r=report(p)
 def test_deadlock_uses_completed_same_problem_not_moving_budget(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)
   for n in range(2):
    b=p/'concept-history'/str(n);write(b/'record.json',{})
    write(b/'concept-critic.json',{'setup_assessments':[{'setup_id':'s','checks':[{'check':'hierarchy','status':'FAIL'}]}]})
   with patch('motif_concept.completed_review',return_value={}):
    with self.assertRaisesRegex(ValueError,'CONCEPT_DEADLOCK'):guard_deadlock(p,{'setup_ids':['s']})
    guard_deadlock(p,{'setup_ids':['new-family']})
 def test_aborted_or_duplicate_reviews_do_not_consume_deadlock(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)
   for name in ['concept','copy','concept-aborted-pose-check']:
    b=p/'reference-gates'/name;write(b/'record.json',{});write(b/'concept-critic-invocation.json',{});write(b/'concept-critic.json',{'setup_assessments':[{'setup_id':'s','checks':[{'check':'hierarchy','status':'FAIL'}]}]})
   with patch('motif_concept.completed_review',return_value={'input_sha256':'same'}):
    result=deadlock_history(p,'s');self.assertEqual(result['completed_failures'],1);self.assertFalse(result['escape_required']);self.assertEqual(result['moving_budget_consumed'],0)
 def test_replan_history_counts_archived_completed_receipts_once(self):
  import shutil
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)
   def receipt(base,label):
    base.mkdir(parents=True);(base/'concept-critic-input.txt').write_text(label)
    write(base/'concept-critic-output-schema.json',{})
    write(base/'concept-critic.json',{'setup_assessments':[{'setup_id':'s','checks':[{'check':'CONTACT_PROOF_UNREADABLE','status':'FAIL'}]}]})
    write(base/'concept-critic-invocation.json',{'exit_code':0,'input_sha256':sha(base/'concept-critic-input.txt'),'output_schema_sha256':sha(base/'concept-critic-output-schema.json')})
    write(base/'record.json',{'response_sha256':sha(base/'concept-critic.json'),'invocation_sha256':sha(base/'concept-critic-invocation.json')})
   receipt(p/'concept-history/first','distinct first live input')
   receipt(p/'reference-gates/concept','distinct second live input')
   shutil.copytree(p/'reference-gates/concept',p/'concept-history/duplicate')
   result=deadlock_history(p,'s')
   self.assertEqual(result['completed_failures'],2);self.assertTrue(result['escape_required'])
   self.assertEqual(result['repeated_checks'],['CONTACT_PROOF_UNREADABLE'])
   with self.assertRaisesRegex(ValueError,'CONCEPT_DEADLOCK'):guard_deadlock(p,{'setup_ids':['s']})
 def original_patch(self):
  p=read(ROOT/'videos/productions/openai-dots-reference-calibrated/production-plan.json');s=copy.deepcopy(p['film_structure']['setups'][1]);s['visual_rule']='One new engagement rule';s['relationship_archetype']='connection';tokens=[{'id':t['id'],'state_at_origin':t['state_at_origin'],'story_justification':t['story_justification'],'state_changes':[c for c in t['state_changes'] if c['setup_id']==s['setup_id']],'final_destination':t['final_destination']} for t in p['film_structure']['continuity_tokens'] if t['id'] in s['continuity_tokens']]
  return p,{'reason':'UNIT only','escape':'simplify','setups':[s],'beats':copy.deepcopy(p['beats'][1:4]),'token_changes':tokens}
 def test_patch_preserves_other_eight_setups_and_exact_script(self):
  p,patch_=self.original_patch();q=apply_patch(p,'s02-connected-work',patch_)
  self.assertEqual(q['script'],p['script']);self.assertEqual(q['film_structure']['setups'][2:],p['film_structure']['setups'][2:]);self.assertEqual(q['beats'][4:],p['beats'][4:])
  patch_['beats'][0]['narration']='Changed'
  with self.assertRaisesRegex(ValueError,'narration'):apply_patch(p,'s02-connected-work',patch_)
 def test_scoped_merge_retires_superseded_shared_architecture(self):
  p,v=self.original_patch()
  for b in v['beats']:b['needed_assets']=['agency-props','agent-assisted:new-aperture']
  q=apply_patch(p,'s02-connected-work',v)
  ids={a['id'] for a in q['assets']}
  self.assertNotIn('connected-work-contact-map',ids);self.assertNotIn('connected-work-props',ids);self.assertIn('agent-assisted:new-aperture',ids)
  active=q['rationale']+q['metaphor']+' '.join(q['limitations'])+json.dumps(q['assets'])
  self.assertNotIn('Bot palm contact',active);self.assertNotIn('dock, seat, develop',active)
  self.assertEqual(q['beats'][4:],p['beats'][4:])
 def test_cosmetic_escape_and_fake_split_rejected(self):
  p,v=self.original_patch();v['setups'][0]=copy.deepcopy(p['film_structure']['setups'][1])
  with self.assertRaisesRegex(ValueError,'retain same'):apply_patch(p,'s02-connected-work',v)
  v['escape']='split'
  with self.assertRaisesRegex(ValueError,'multiple'):apply_patch(p,'s02-connected-work',v)
if __name__=='__main__':unittest.main()
