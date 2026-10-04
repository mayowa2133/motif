"""News intake preserves approved copy and the existing pre-animation gates."""
import json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from motif_news import validate_script,voice,build,planner_prompt
class NewsTests(unittest.TestCase):
 def fixture(self):
  b={'script':'A small task finishes.','audience':'workers','style':'reference-expressive-high-energy-v1'}
  p={**b,'beats':[{'id':'task','narration':b['script'],'actions':[{'cue':'task'}]}]}
  return b,p
 def test_script_and_beat_text_cannot_silently_change(self):
  b,p=self.fixture();p['beats'][0]['narration']='A different task finishes.'
  with self.assertRaisesRegex(ValueError,'script changed'):validate_script(p,b)
 def test_audience_cannot_silently_change(self):
  b,p=self.fixture();p['audience']='children'
  with self.assertRaisesRegex(ValueError,'audience/style'):validate_script(p,b)
 def test_voice_and_build_cannot_bypass_structure(self):
  with tempfile.TemporaryDirectory() as d,patch('motif_news.command') as tts,patch('motif_news.runpy.run_path') as code:
   for f in (voice,build):
    with self.assertRaises((ValueError,FileNotFoundError)):f(Path(d))
   tts.assert_not_called();code.assert_not_called()
 def test_typographic_contraction_uses_the_actual_asr_interval(self):
  from motif_plan_compile import align
  p={'beats':[{'id':'name','narration':'They’re called Dots.','actions':[{'cue':'called Dots.'}]}]}
  words=[{'text':w,'start':i*.4+.1,'end':i*.4+.4} for i,w in enumerate(["They're",'called','Dots.'])]
  spans,evidence=align(p,words)
  self.assertEqual(evidence['coverage'],1)
  self.assertEqual(spans[0]['start'],words[0]['start'])
  self.assertEqual(spans[0]['actions'][0]['time'],words[1]['start'])
if __name__=='__main__':unittest.main()
