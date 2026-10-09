"""Rig framework and the first ten rigs: schema, contacts, events, proofs, palettes."""
import json,sys,tempfile,unittest
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from jsonschema import Draft202012Validator,ValidationError
import motif_rigs
from motif_rigs import Rig,Action,rotation,PALETTES
ROOT=Path(__file__).resolve().parents[1]
SCHEMA=json.loads((ROOT/'schemas/rig.schema.json').read_text())

class Dummy(Rig):
 def draw(self,p,pose,c):
  s,e,a,t=pose;y=-300+200*min(1,t/self.contact_t('drop')) if a else -100
  return f'<rect x="-20" y="{y:.2f}" width="40" height="40" fill="{c["primary"]}"/><rect x="-60" y="-60" width="120" height="60" fill="{c["dark"]}"/>'
 def seams(self,p,pose):
  s,e,a,t=pose;y=-300+200*min(1,t/self.contact_t('drop')) if a else -100
  return {'box-table':((0,y+40),(0,-60))}

DUMMY=Dummy(name='dummy-drop',description='A box drops onto a table.',params_schema={'type':'object','properties':{'label':{'type':'string'}},'additionalProperties':False},
            defaults={'label':'X'},states=('up','down'),actions={'drop':Action('drop','up','down',11,'box-table',5)},bot_slot={'x':0,'y':0,'scale':.2,'role':'watches'},tags=('test','drop'))

class RigFrameworkTests(unittest.TestCase):
 def test_dummy_round_trips_and_closes_its_contact(self):
  Draft202012Validator(SCHEMA).validate(DUMMY.manifest())
  self.assertEqual(DUMMY.contact_gap(None,'drop'),0)
  with self.assertRaises(ValidationError):DUMMY.params({'label':3})
  events=DUMMY.events(None,'drop','#s-world',1.0)
  self.assertEqual(len(events),11);self.assertTrue(all(e['action']=='SET' and e['target']=='#s-world' for e in events))
  self.assertAlmostEqual(events[1]['time']-events[0]['time'],1/30,places=5)
 def test_proof_writes_before_contact_after(self):
  with tempfile.TemporaryDirectory() as d:
   rec=DUMMY.proof(d,action='drop')
   for k in ('before','contact','after'):self.assertTrue(Path(rec['stills'][k]).is_file())
   from PIL import Image
   self.assertEqual(Image.open(rec['stills']['contact']).size,(360,640))
 def test_palette_rotation_never_repeats_neighbours_and_covers_all(self):
  order=rotation(16)
  self.assertTrue(all(a!=b for a,b in zip(order,order[1:])))
  self.assertEqual(set(order[:len(PALETTES)]),set(PALETTES))

class LibraryTests(unittest.TestCase):
 def test_ten_rigs_registered_with_valid_manifests(self):
  rigs=motif_rigs.all_rigs();self.assertGreaterEqual(len(rigs),10)
  for rig in rigs.values():Draft202012Validator(SCHEMA).validate(rig.manifest())
 def test_every_action_closes_its_contact_exactly(self):
  for name,rig in motif_rigs.all_rigs().items():
   for action in rig.actions:self.assertAlmostEqual(rig.contact_gap(None,action),0,places=9,msg=f'{name}/{action}')
 def test_contact_is_open_before_the_contact_frame(self):
  for name,rig in motif_rigs.all_rigs().items():
   for action,a in rig.actions.items():
    (x1,y1),(x2,y2)=rig.contacts(None,(action,0.0))[a.contact]
    self.assertGreater(abs(x1-x2)+abs(y1-y2),1,f'{name}/{action} starts already touching')
 def test_every_rig_renders_in_every_palette_and_varies_colour(self):
  for name,rig in motif_rigs.all_rigs().items():
   seen={rig.render(None,rig.states[-1],p) for p in PALETTES}
   self.assertEqual(len(seen),len(PALETTES),name)
 def test_rendering_is_deterministic(self):
  for name,rig in motif_rigs.all_rigs().items():
   a=next(iter(rig.actions));self.assertEqual(rig.frames(None,a),rig.frames(None,a),name)
 def test_every_rig_has_a_design_note(self):
  for name in motif_rigs.all_rigs():self.assertTrue((ROOT/f'docs/rigs/{name}.md').is_file(),name)

if __name__=='__main__':unittest.main()
