"""Regression checks for the text-directed adapter's actual input edge cases."""
import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from motif_ui_production import review,speech_mapping
from motif_ui_actions import scene
class UiInputTests(unittest.TestCase):
 def test_missing_article_and_compound_use_distinct_measured_anchors(self):
  mapping,r=speech_mapping('A solo dev just',[
   {'text':'SoloDev','start':.18,'end':.59,'centers':[.30,.50]},
   {'text':'just','start':.59,'end':.86,'centers':[.68]}])
  self.assertEqual([x['word'] for x in r['estimated_boundaries']],['a'])
  self.assertLess(mapping[0][0],mapping[1][0]);self.assertLess(mapping[1][0],mapping[2][0])
  self.assertEqual(mapping[2][0],.40)
 def test_reject_unregistered_binding_and_injected_id(self):
  p=json.loads((ROOT/'videos/productions/voicestudio-text-directed-film/production-plan.json').read_text());b={'script':p['script'],'style':p['style']}
  self.assertTrue(review(p,b)['pass'])
  p['shots'][0]['kind']='execute-arbitrary-code';self.assertFalse(review(p,b)['pass'])
  p['shots'][0]['kind']='record-and-complete';p['shots'][0]['id']='x\" onclick=bad'
  self.assertFalse(review(p,b)['pass'])
 def test_local_ui_state_is_seek_safe(self):
  expected=scene(17,26,'OFFLINE',5107)
  for f in [38,0,12,25,10]:scene(17,f,'OFFLINE',5107)
  self.assertEqual(expected,scene(17,26,'OFFLINE',5107))
if __name__=='__main__':unittest.main()
