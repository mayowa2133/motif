"""Finish pass: deterministic, text-safe, opt-in and never in place."""
import json,shutil,sys,tempfile,unittest
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from motif_finish import finish_composition,finish_frame,apply,read,DEFAULT_STYLE,top_level

def frame(i):
 return (f'<rect x="0" y="0" width="720" height="1280" fill="#BDAE8F"/>'
         f'<g opacity="1" transform="translate({100+i} 400) rotate(2) scale(1 1)"><path d="M0 0H200V120H0Z" fill="#F1E7D3"/></g>'
         f'<g opacity="1" transform="translate(40 30) rotate(0) scale(1 1)"><path d="M0 0H640V60H0Z" fill="#F1E7D3"/><text x="320" y="40">HEADLINE</text></g>')

def composition(comp='shot-01',frames=3):
 spec={'schemaVersion':'1.0','compositionId':comp,'fps':30,'durationSec':frames/30,'initial':[{'target':f'#{comp}-world','props':{'innerHTML':frame(0)}}],
       'events':[{'time':(i+1)/30,'target':f'#{comp}-world','action':'SET','params':{'props':{'innerHTML':frame(i+1)}}} for i in range(frames-1)]}
 body=json.dumps(spec,separators=(',',':')).replace('</','<\\/')
 return (f'<template><div id="{comp}-root"><svg width="100%" height="100%" viewBox="0 0 720 1280" xmlns="http://www.w3.org/2000/svg"><defs>'
         f'<pattern id="{comp}-def-worldPaper" width="2048" height="2048" patternUnits="userSpaceOnUse"><image href="assets/materials/world-paper.webp" width="2048" height="2048"/></pattern></defs>'
         f'<g id="{comp}-world" data-layout-allow-overflow>{frame(0)}</g></svg></div>'
         f'<script>window.MotifEventEngine.compileFrames({body},"{comp}");</script></template>')

class FinishTests(unittest.TestCase):
 def setUp(self):self.style=read(DEFAULT_STYLE)
 def test_same_input_gives_same_bytes(self):
  a=finish_composition(composition(),self.style,self.style['lights']['default'])
  self.assertEqual(a,finish_composition(composition(),self.style,self.style['lights']['default']))
 def test_text_pieces_get_shadow_only_and_bare_shapes_are_untouched(self):
  out=finish_frame(frame(0),'s-',self.style);pieces=top_level(out)
  self.assertNotIn('filter',out[pieces[0][0]:pieces[0][1]].split('>')[0])
  self.assertIn('finish-piece-',out[pieces[1][0]:pieces[1][1]].split('>')[0])
  self.assertIn('finish-flat-',out[pieces[2][0]:pieces[2][1]].split('>')[0])
  self.assertIn('>HEADLINE</text>',out)
 def test_jitter_is_stable_for_a_slot_and_small(self):
  a=finish_frame(frame(0),'s-',self.style);b=finish_frame(frame(0),'s-',self.style);self.assertEqual(a,b)
  import re
  x=float(re.findall(r'translate\(([\d.]+) ',a)[0]);self.assertLessEqual(abs(x-100),self.style['micro']['offset_px'])
 def test_every_frame_is_finished_and_overlay_sits_outside_the_swapped_world(self):
  out=finish_composition(composition(frames=4),self.style,self.style['lights']['default'])
  levels=len(self.style['shadows']['blur'])
  self.assertEqual(out.count('url(#shot-01-finish-piece-'),4+1)  # 4 frame states plus the static copy of frame 0
  self.assertEqual(out.count('<filter id="shot-01-finish-piece-'),levels)
  world_end=out.index('<g id="shot-01-finish"');self.assertLess(out.index('<g id="shot-01-world"'),world_end)
  self.assertIn('finish-surface.webp',out);self.assertNotIn('world-paper.webp',out)
 def test_apply_writes_a_copy_and_refuses_to_overwrite(self):
  with tempfile.TemporaryDirectory() as d:
   src=Path(d)/'src';(src/'compositions').mkdir(parents=True);(src/'assets/materials').mkdir(parents=True)
   (src/'compositions/shot-01.html').write_text(composition());(src/'compositions/captions.html').write_text(composition('captions'))
   record=apply(src,Path(d)/'out')
   self.assertEqual(list(record['shots']),['shot-01'])
   self.assertEqual((src/'compositions/shot-01.html').read_text(),composition())
   self.assertEqual((Path(d)/'out/compositions/captions.html').read_text(),composition('captions'))
   with self.assertRaisesRegex(ValueError,'never overwritten'):apply(src,Path(d)/'out')
   from motif_provenance import check
   self.assertEqual(check(Path(d)/'out')['status'],'PASS')

if __name__=='__main__':unittest.main()
