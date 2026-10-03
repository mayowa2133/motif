"""Structure integrity, ordinary producer boundaries and blocking hierarchy."""
import copy,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from motif_quality import ROOT,read,write,sha,direction_review,rough,hierarchy_failures,repair
from motif_structure import check_structure,report_status,require_structure,policy_hashes,structure_review
P=ROOT/'quality/validation/structure-v1/fixtures-clean'

def plan(name='e'):return read(P/name/'production-plan.json')
def report(p):
 codes=read(ROOT/'schemas/structure-critic.schema.json')['properties']['checks']['items']['properties']['check']['enum']
 return {'role':'structure','inspection_scope':'UNIT ONLY','checks':[{'check':c,'status':'PASS','evidence':'unit decision'} for c in codes],'setup_assessments':[{'setup_id':s['setup_id'],'status':'PASS','evidence':'unit decision'} for s in p['film_structure']['setups']],'violations':[],'limits':'UNIT ONLY, not live evidence'}

class StructureTests(unittest.TestCase):
 def test_many_beats_one_setup_and_absent_bot_are_valid(self):
  self.assertEqual(check_structure(plan())['setups'],1)
  self.assertEqual(check_structure(plan('i'))['setups'],1)
 def test_setup_schema_embedded_consistently_in_existing_plan_schemas(self):
  film=read(ROOT/'schemas/film-structure.schema.json');film.pop('$schema');setup=read(ROOT/'schemas/setup-contract.schema.json');setup.pop('$schema')
  self.assertEqual(film['properties']['setups']['items'],setup)
  for n in ['production-plan','script-production-plan','text-directed-production-plan']:
   stored=read(ROOT/f'schemas/{n}.schema.json')['properties']['film_structure']
   self.assertEqual(stored.get('anyOf',[stored])[0],film)
 def test_narration_coverage_and_quotes_are_checked(self):
  p=plan();p['film_structure']['setups'][0]['narration_span']['text']='unrelated words'
  with self.assertRaisesRegex(ValueError,'quote'):check_structure(p)
  p=plan('g');p['film_structure']['setups'][1]['narration_span']['start_word']+=1
  with self.assertRaises(ValueError):check_structure(p)
 def test_setup_refs_role_and_duplicate_assignment_block(self):
  p=plan();p['film_structure']['setups'][0]['beat_ids'][0]='missing'
  with self.assertRaisesRegex(ValueError,'unknown beat'):check_structure(p)
  p=plan();p['film_structure']['setups'][0]['bot_role']='absent'
  with self.assertRaisesRegex(ValueError,'role'):check_structure(p)
  p=plan();p['film_structure']['setups'][0]['beat_ids'].append('b1')
  with self.assertRaises(ValueError):check_structure(p)
 def test_token_lifecycle_is_not_just_a_list_of_ids(self):
  p=plan('g');check_structure(p);p['film_structure']['continuity_tokens'][0]['origin_setup']='s2'
  with self.assertRaisesRegex(ValueError,'lifecycle'):check_structure(p)
 def test_missing_check_or_setup_cannot_pass(self):
  p=plan();r=report(p);r['checks'].pop()
  with self.assertRaisesRegex(ValueError,'coverage'):report_status(p,r)
  r=report(p);r['setup_assessments']=[]
  with self.assertRaisesRegex(ValueError,'coverage'):report_status(p,r)
 def test_not_assessed_requires_replan_and_fail_needs_correction(self):
  p=plan();r=report(p);r['checks'][0]['status']='NOT_ASSESSED';self.assertEqual(report_status(p,r),'REPLAN_REQUIRED')
  r['checks'][0]['status']='FAIL'
  with self.assertRaisesRegex(ValueError,'correction'):report_status(p,r)
 def test_ordinary_direction_and_rough_require_structure_before_io(self):
  with tempfile.TemporaryDirectory() as d:
   project=Path(d);p=plan();write(project/'production-plan.json',p)
   with patch('motif_direct.model_call') as model,patch('motif_quality.cmd') as renderer:
    with self.assertRaisesRegex(ValueError,'fresh structure'):direction_review(project,p,{})
    with self.assertRaisesRegex(ValueError,'fresh structure'):rough(project)
    model.assert_not_called();renderer.assert_not_called()
 def test_live_record_freshness_plan_policy_and_response(self):
  with tempfile.TemporaryDirectory() as d:
   project=Path(d);p=plan();write(project/'production-plan.json',p)
   def call(folder,name,prompt,schema,config):
    write(folder/(name+'.json'),report(p));(folder/(name+'-input.txt')).write_text(prompt);write(folder/(name+'-output-schema.json'),{})
    write(folder/(name+'-invocation.json'),{'exit_code':0,'saved_response_used':False,'model_fallback_used':False,'input_sha256':sha(folder/(name+'-input.txt')),'output_schema_sha256':sha(folder/(name+'-output-schema.json'))});return report(p)
   with patch('motif_direct.model_call',side_effect=call):structure_review(project,p,{})
   require_structure(project)
   with patch('motif_structure.policy_hashes',return_value={}):
    with self.assertRaisesRegex(ValueError,'stale'):require_structure(project)
   p['beats'][0]['quality']['before']='Changed intent';write(project/'production-plan.json',p)
   with self.assertRaisesRegex(ValueError,'stale'):require_structure(project)
 def test_false_pass_report_cannot_ignore_hierarchy_failure(self):
  p=plan('i');mapping=read(ROOT/'quality/rubric/hierarchy.json')['codes'];r={'gates':[],'shot_assessments':[],'violations':[],'hierarchy_assessments':[{'shot':'b1','code':c,'status':'PASS','evidence':'unit'} for c in mapping]}
  self.assertEqual(hierarchy_failures(p,r),[])
  r['hierarchy_assessments'][0]['status']='FAIL'
  self.assertTrue(any('mapped gate' in v for v in hierarchy_failures(p,r)))
  r['hierarchy_assessments']=[];self.assertIn('visual hierarchy coverage incomplete',hierarchy_failures(p,r))
 def test_story_change_archives_structure_with_direction(self):
  from test_quality_system import QualityTests
  with tempfile.TemporaryDirectory() as d:
   project=Path(d);QualityTests().reports(project,'energy')
   write(project/'quality-structure-record.json',{'status':'PASS','unit':True})
   write(project/'quality-structure.json',{'unit':True})
   p=read(project/'production-plan.json');p['beats'][0]['quality']['after']='Meaningfully changed result';write(project/'production-plan.json',p)
   repair(project,'Change story consequence')
   archive=project/'quality-review/direction-before-repair-1'
   self.assertTrue((archive/'quality-structure-record.json').exists())
   self.assertFalse((project/'quality-structure-record.json').exists())
 def test_caption_dependence_in_moving_gate_requires_replan(self):
  from test_quality_system import QualityTests
  from motif_quality import evaluate
  with tempfile.TemporaryDirectory() as d:
   project=Path(d);base=QualityTests().reports(project)
   p=plan('i');p['beats'][0]['id']='unit';p['film_structure']['setups'][0]['beat_ids']=['unit'];write(project/'production-plan.json',p)
   evidence=read(base/'evidence.json');evidence['plan_sha256']=sha(project/'production-plan.json');write(base/'evidence.json',evidence)
   visual=read(base/'visual-critic.json');mapping=read(ROOT/'quality/rubric/hierarchy.json')['codes']
   visual['hierarchy_assessments']=[{'shot':'unit','code':c,'status':'FAIL' if c=='CAPTION_CARRIES_STORY' else 'PASS','evidence':'UNIT ONLY'} for c in mapping]
   for g in visual['gates']+visual['shot_assessments'][0]['gates']:
    if g['gate']=='mobile':g['status']='FAIL'
   visual['violations']=[{'timestamp':0,'shot':'unit','gate':'mobile','failure_code':'CAPTION_CARRIES_STORY','observation':'UNIT ONLY','gold_id':'payment-burden','smallest_correction':'Replan the visible action'}];write(base/'visual-critic.json',visual)
   record=read(base/'critics-record.json');record['evidence_sha256']=sha(base/'evidence.json');record['report_hashes']['visual']=sha(base/'visual-critic.json');record['hierarchy_policy_sha256']=sha(ROOT/'quality/rubric/hierarchy.json');write(base/'critics-record.json',record)
   with patch('motif_structure.require_structure',return_value={'status':'PASS'}):
    result=evaluate(project,'rough')
   self.assertEqual(result['status'],'REPLAN_REQUIRED')
   self.assertFalse(result['publish'])
 def test_planner_context_and_wire_schema_require_structure(self):
  from motif_direct import planning_prompt
  prompt=planning_prompt({'message':'Choose a result','intended_duration_seconds':20})
  self.assertIn('FILM STRUCTURE FIRST',prompt);self.assertIn('same visual rule',prompt)
  # model_call's existing planner flattening includes every property, including film_structure.
  for n in ['production-plan','script-production-plan']:
   self.assertIn('film_structure',read(ROOT/f'schemas/{n}.schema.json')['properties'])
if __name__=='__main__':unittest.main()
