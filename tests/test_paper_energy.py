"""Seek determinism and composed contact checks for opt-in paper motion."""
import json,math,re,sys,unittest,xml.etree.ElementTree as ET
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from motif_paper_energy import living,frame_scene,review_energy
from motif_paper_investigation import ASSET_IDS,fragment
P=R/'videos/productions/confidence-isnt-evidence-high-energy'
class EnergyTests(unittest.TestCase):
 def test_living_hold_is_repeatable_stepped_and_independent(self):
  self.assertEqual([living(i,173) for i in range(12)],[living(i,173) for i in range(12)])
  self.assertEqual(living(3,173),living(5,173))
  self.assertNotEqual(living(3,173),living(3,204))
  self.assertTrue(all(abs(living(i,173,2))<=2 for i in range(300)))
 def test_reversed_seek_returns_identical_markup(self):
  a={n:fragment(str((P/'assets/props'/f'{n}.svg').relative_to(R))) for n in ASSET_IDS}
  first=frame_scene('patch',.8,2.94,a,390)
  frame_scene('patch',2.3,2.94,a,390)
  self.assertEqual(first,frame_scene('patch',.8,2.94,a,390))
 def test_canonical_hand_transform_meets_composed_prop_endpoint(self):
  a={n:fragment(str((P/'assets/props'/f'{n}.svg').relative_to(R))) for n in ASSET_IDS}
  for t in (.2,.37,.6,.8):
   body,grips=frame_scene('catch',t,1.02,a,204)
   xml=re.sub(r'\b(data-layout-[a-z-]+)(?=\s|>)',r'\1=""',body)
   root=ET.fromstring('<svg>'+xml+'</svg>');puppet=root[-1]
   tx,ty,angle,scale=map(float,re.findall(r'-?\d+(?:\.\d+)?',puppet.attrib['transform'])[:4])
   hand=next(x for x in puppet.iter() if x.get('data-part')=='rightHand')
   hx,hy=map(float,re.findall(r'-?\d+(?:\.\d+)?',hand.attrib['transform'])[:2])
   theta=math.radians(angle);dx=(hx-512)*scale;dy=(hy-620)*scale
   actual=(tx+dx*math.cos(theta)-dy*math.sin(theta),ty+dx*math.sin(theta)+dy*math.cos(theta))
   target=next(x['prop_endpoint'] for x in grips if x['side']=='r')
   self.assertLess(math.dist(actual,target),.12)
 def test_unknown_energy_actions_and_rewritten_script_fail(self):
  plan=json.loads((P/'production-plan.json').read_text());brief=json.loads((P/'brief.json').read_text())
  self.assertTrue(review_energy(plan,brief)['pass'])
  plan['beats'][0]['actions'][0]['kind']='execute-model-code'
  self.assertFalse(review_energy(plan,brief)['pass'])
  plan['script']='Finding a source proves the claim.'
  self.assertFalse(review_energy(plan,brief)['pass'])
if __name__=='__main__':unittest.main()
