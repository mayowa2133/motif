"""Script fidelity and capability failures for the shared director adapter."""
import copy,json,sys,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from motif_plan import review_plan
P=R/'videos/productions/confidence-isnt-evidence'
class ScriptInputTests(unittest.TestCase):
 def setUp(self):
  self.plan=json.loads((P/'production-plan.json').read_text());self.brief=json.loads((P/'brief.json').read_text())
 def test_supplied_script_is_not_rewritten(self):
  self.plan['beats'][0]['narration']='A confident answer is always wrong.'
  self.assertFalse(review_plan(self.plan,self.brief)['pass'])
 def test_unknown_actions_cannot_execute(self):
  self.plan['beats'][0]['actions'][0]['kind']='eval-model-code'
  self.assertFalse(review_plan(self.plan,self.brief)['pass'])
 def test_action_requires_physical_predecessor(self):
  self.plan['beats'][0]['actions'],self.plan['beats'][2]['actions']=self.plan['beats'][2]['actions'],self.plan['beats'][0]['actions']
  self.assertFalse(review_plan(self.plan,self.brief)['pass'])
 def test_explicit_style_must_match_input(self):
  self.plan['style']='motif-v1'
  self.assertFalse(review_plan(self.plan,self.brief)['pass'])
 def test_supported_plan_consumed_by_shared_validator(self):
  self.assertTrue(review_plan(self.plan,self.brief)['pass'])
 def test_model_cannot_request_unregistered_file(self):
  self.plan['assets'][0]['reuse_path']='../../private-file'
  self.assertFalse(review_plan(self.plan,self.brief)['pass'])
 def test_framing_controls_change_fit_and_preserve_action(self):
  from motif_paper_investigation import camera
  from motif_framing import contains
  kind=self.plan['beats'][2]['actions'][0]['kind']
  detail=camera(kind,'detail');wide=camera(kind,'establish')
  self.assertNotEqual(detail['camera'],wide['camera'])
  self.assertTrue(contains(detail['safe_area'],detail['projected_critical_bounds'],1))
if __name__=='__main__':unittest.main()
