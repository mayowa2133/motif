"""Asset-origin registry, export check and Motif material reproducibility."""
import copy,json,shutil,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import numpy as np
from PIL import Image
from motif_provenance import ROOT,load,check,validate,entry_for,add,sha
import motif_materials as materials

REGISTERED=ROOT/'assets/materials/legacy-v0/wall.png'
STUDY=next(p for p in sorted((ROOT/'references/reconstruction/study').rglob('*')) if p.suffix in ('.png','.jpg','.wav'))

class ProvenanceTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.p=Path(self.tmp.name)
  (self.p/'assets/materials').mkdir(parents=True)
 def test_registered_asset_passes(self):
  shutil.copy2(REGISTERED,self.p/'assets/materials/wall.png')
  r=check(self.p);self.assertEqual(r['status'],'PASS');self.assertEqual(r['files'][0]['origin'],'procedural-seeded')
 def test_lossless_reencode_is_recognised_by_pixels(self):
  Image.open(REGISTERED).save(self.p/'assets/materials/wall.webp','WEBP',lossless=True)
  self.assertEqual(check(self.p)['status'],'PASS')
 def test_unregistered_png_fails(self):
  Image.fromarray(np.full((8,8,3),7,np.uint8)).save(self.p/'assets/materials/new.png')
  r=check(self.p);self.assertEqual(r['status'],'FAIL');self.assertEqual(r['unknown'],['assets/materials/new.png'])
 def test_reference_derived_asset_fails(self):
  shutil.copy2(STUDY,self.p/'assets/materials'/STUDY.name)
  r=check(self.p);self.assertEqual(r['status'],'FAIL');self.assertEqual(len(r['reference_derived']),1)
 def test_derivation_cannot_launder_reference_origin(self):
  data=load();Image.fromarray(np.full((8,8,3),9,np.uint8)).save(self.p/'assets/materials/x.png')
  ref=next(e for e in data['assets'] if e['origin']=='reference-derived')
  add(data,entry_for(self.p/'assets/materials/x.png','test/x','motif-derived','re-encode',{'status':'APPROVED'},derived_from=ref['id']))
  self.assertEqual(check(self.p,registry=data)['reference_derived'],['assets/materials/x.png'])
 def test_per_film_rules_are_limited_to_generated_outputs(self):
  (self.p/'assets/voice').mkdir();(self.p/'assets/voice/take.wav').write_bytes(b'RIFF')
  self.assertEqual(check(self.p)['status'],'FAIL')
  rule={'glob':'assets/voice/*','origin':'motif-tts','generator':'unit tts'}
  self.assertEqual(check(self.p,rules=[rule])['status'],'PASS')
  with self.assertRaisesRegex(ValueError,'per-film'):check(self.p,rules=[{**rule,'origin':'licensed'}])
 def test_registry_entries_are_complete(self):
  data=load();self.assertGreater(len(data['assets']),100)
  bad=copy.deepcopy(data);bad['assets'][0].pop('generator')
  with self.assertRaisesRegex(ValueError,'generator'):validate(bad)
  bad=copy.deepcopy(data);next(e for e in bad['assets'] if e['origin']=='motif-image-gen').pop('prompt')
  with self.assertRaisesRegex(ValueError,'prompt'):validate(bad)
 def test_registered_hashes_match_files_in_repository(self):
  for e in load()['assets']:
   if e.get('path') and (ROOT/e['path']).exists():self.assertEqual(sha(ROOT/e['path']),e['sha256'],e['id'])
 def test_technical_gate_measures_provenance(self):
  from motif_quality import technical
  Image.fromarray(np.full((8,8,3),7,np.uint8)).save(self.p/'assets/materials/new.png')
  (self.p/'scene-events.json').write_text(json.dumps({'fps':30,'durationSec':1}));(self.p/'checks.json').write_text('{}')
  video=self.p/'v.mp4';video.write_bytes(b'x')
  with patch('motif_quality.probe_video',return_value={'frames':30,'fps':30,'width':360,'height':640,'duration':1.0,'sha256':'x'}),patch('motif_evidence.require_scope',return_value={'actual_mode':'technical-fixture'}):
   r=technical(self.p,video,self.p/'checks.json')
  self.assertEqual(r['checks']['provenance'],'FAIL');self.assertEqual(r['provenance_check']['unknown'],['assets/materials/new.png'])

class MaterialTests(unittest.TestCase):
 def test_committed_materials_reproduce_from_seed(self):
  self.assertEqual(materials.check('legacy-v0'),[])
  # Each motif-v1 surface takes several seconds; set MOTIF_FULL_MATERIAL_CHECK=1 to regenerate all six.
  import os
  self.assertEqual(materials.check('motif-v1',None if os.environ.get('MOTIF_FULL_MATERIAL_CHECK') else ['card']),[])
 def test_motif_v1_tiles_without_seams_or_visible_repeats(self):
  for name in materials.MOTIF_V1:
   with Image.open(materials.path_for('motif-v1',name)) as im:
    self.assertLess(materials.tile_seam_score(im),1.3,name)
    self.assertLess(materials.repeat_peak(im),.2,name)
 def test_repeat_detector_flags_a_small_tile(self):
  with Image.open(materials.path_for('motif-v1','card')) as im:tile=im.crop((0,0,512,512))
  big=Image.new('RGBA',(2048,2048))
  for x in range(4):
   for y in range(4):big.paste(tile,(x*512,y*512))
  self.assertGreater(materials.repeat_peak(big),.9)
 def test_materials_are_registered(self):
  ids={e['id'] for e in load()['assets']}
  for s,(names,_,_) in materials.SETS.items():
   for n in names:self.assertIn(f'material/{s}/{n}',ids)

if __name__=='__main__':unittest.main()
