"""Reel pacing check measured from built compositions."""
import json,sys,tempfile,unittest
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from motif_pacing import check,check_plan
REPO=Path(__file__).resolve().parents[1]

def state(i,moving=True,headline='HEADLINE'):
 x=i if moving else 0
 return f'<g transform="translate({x} 0)"><rect width="10" height="10"/></g><g transform="translate(0 {x})"><rect width="10" height="10"/></g><text font-weight="900" font-size="32">{headline}</text>'

def project(d,shots):
 """shots: list of frame-state lists."""
 d=Path(d);(d/'compositions').mkdir();hosts=[];t=0
 for n,states in enumerate(shots):
  comp=f'shot-{n+1:02d}';dur=len(states)/30
  spec={'schemaVersion':'1.0','fps':30,'durationSec':dur,'initial':[{'target':f'#{comp}-world','props':{'innerHTML':states[0]}}],'events':[{'time':(i+1)/30,'target':f'#{comp}-world','action':'SET','params':{'props':{'innerHTML':s}}} for i,s in enumerate(states[1:])]}
  (d/f'compositions/{comp}.html').write_text(f'<template><svg viewBox="0 0 720 1280"><g id="{comp}-world"></g></svg><script>window.MotifEventEngine.compileFrames({json.dumps(spec)},"{comp}");</script></template>')
  hosts.append(f'<div data-composition-id="{comp}" data-composition-src="compositions/{comp}.html" data-start="{t}" data-duration="{dur}"></div>');t+=dur
 (d/'index.html').write_text(''.join(hosts));return d

class PacingTests(unittest.TestCase):
 def test_v6_passes(self):
  r=check(REPO/'videos/productions/voicestudio-craft-v6');self.assertEqual(r['status'],'PASS',r['failures'])
 def test_three_second_static_hold_fails(self):
  with tempfile.TemporaryDirectory() as d:
   shots=[[state(i,headline=f'H{n}') for i in range(60)] for n in range(10)]
   shots[4]=[state(0,moving=False,headline='H4')]*90+[state(i,headline='H4b') for i in range(1,4)]
   r=check(project(d,shots));self.assertEqual(r['status'],'FAIL')
   self.assertTrue(any('static hold 3.0' in f for f in r['failures']),r['failures'])
 def test_single_mover_and_long_headline_and_few_cuts_fail(self):
  with tempfile.TemporaryDirectory() as d:
   one=lambda i:f'<g transform="translate({i} 0)"><rect/></g><g><rect/></g><text font-weight="900" font-size="32">SAME</text>'
   r=check(project(d,[[one(i) for i in range(300)],[one(i) for i in range(300)]]))
   text=' '.join(r['failures'])
   self.assertIn('cuts 1 outside',text);self.assertIn('moving piece',text);self.assertIn('headline held',text)
 def test_plan_rules(self):
  beats=[{'id':'a','start':0,'end':2.5,'headline':'A','metaphor':'bus'},{'id':'b','start':2.5,'end':5,'headline':'B','metaphor':'scale','cut_before':False}]
  self.assertTrue(any('without a cut' in f for f in check_plan(beats,22)))
  self.assertTrue(any('headline held' in f for f in check_plan(beats,22)))
  self.assertTrue(any('runtime' in f for f in check_plan(beats,5)))

if __name__=='__main__':unittest.main()
