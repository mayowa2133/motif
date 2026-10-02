#!/usr/bin/env python3
"""v1.1 isolated painted contact regressions; never a production film."""
import sys,json,shutil,math
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from motif_quality import write,sha,verify_frozen
from motif_ui_production import write_composition,namespace
from motif_quality_frames import ui_frame
from motif_ui_components import bot,g,card,rect,txt,plant,DEFS,INK
from build_quality_fixtures import contract
P=ROOT/'quality/validation/v1.1/temporal'

def frame(number,f,headline,seed,transition=False):
 # Existing canonical geometry and paper components; explicit held-paper anchor.
 u=min(1,f/30);x=400+12*math.sin(f*.05);y=780-75*u
 body=rect(0,0,720,1280,'#BFA783')+rect(0,990,720,290,'#789AA8')
 body+=plant(618,934,f,.75)
 body+=bot(228,969,f,s=.33,jitter=False,contact=(x,y))
 # The same independent paper remains in hand. Intervention label is never painted.
 if number==2 and 31<=f<=33:x+=135;y-=35
 paper=card(190,133)+txt('SOURCE',95,43,24,INK,900,'middle')+rect(25,66,139,9,'#A79C88',3)+rect(25,91,113,9,'#A79C88',3)
 return body+g(paper,x,y-65,a=0)

def build():
 verify_frozen();P.mkdir(parents=True,exist_ok=True)
 if (P/'index.html').exists():raise ValueError('preserve existing hardening fixture')
 base=ROOT/'quality/validation/fixtures'
 for folder in ('assets','compositions','renders'):(P/folder).mkdir(exist_ok=True)
 for folder in ('fonts','materials'):shutil.copytree(base/'assets'/folder,P/'assets'/folder,dirs_exist_ok=True)
 for name in ('gsap.min.js','motion-primitives.js','motion-engine.js','motif-frame-sequence.js'):shutil.copy2(base/'assets'/name,P/'assets'/name)
 for name in ('package.json','hyperframes.json'):shutil.copy2(base/name,P/name)
 shots=[];ranges=[];events=[];initial=[]
 for i,id_ in enumerate(('t01','t02')):
  q=contract();q.update(purpose='Hold and inspect one source paper',hero='source paper',primary_action='Lift source paper and inspect it',before='Paper rests at lower height',after='Source paper is raised and remains held',focal_target='source paper',secondary_motion=[],environment=['wood-colored wall','floor'],exit_overlap=None)
  q['energy']={'dominant_action':'lift and inspect source paper'};q['performance']={'state':'focused','target':'bot'}
  q['reaction_radius'].update(origin=[618,934],radius=200);q['reaction_radius']['targets']=[dict(id='plant',position=[618,934],relevance=1,amplitude=dict(x=3,y=0,rotation=2),delay=0)]
  bodies=[ui_frame(frame,i+1,f,'',5107,q)[0] for f in range(60)]
  local=[{'time':f/30,'target':'#'+id_+'-world','action':'SET','params':{'props':{'innerHTML':namespace(bodies[f],id_)}}} for f in range(1,60)]
  spec=write_composition(P,id_,2,bodies[0],local,DEFS)
  p=P/'compositions'/f'{id_}.html';p.write_text(p.read_text().replace('data-width="1080"','data-width="360"').replace('data-height="1920"','data-height="640"'))
  initial+=spec['initial'];events+=[{**e,'time':e['time']+i*2,'composition':id_} for e in local]
  shots.append({'id':id_,'quality':q,'startFrame':i*60,'endFrame':(i+1)*60})
  ranges.append({'id':id_,'startFrame':i*60,'endFrame':(i+1)*60,'temporal_events':[{'time':i*2+1,'kind':'contact'}]})
 write(P/'production-plan.json',{'quality_mode':'motif-gold-v1','asset_usage':[{'id':'fixture','scope':'production-specific','path':str((ROOT/'scripts/build_quality_hardening_fixtures.py').relative_to(ROOT)),'metadata_path':'quality/validation/v1.1/temporal/provenance.json','agent_assisted':True}],'shots':shots})
 write(P/'scene-events.json',{'fps':30,'durationSec':4,'initial':initial,'events':events})
 write(P/'shot-ranges.json',ranges)
 write(P/'expected.json',{'withheld_from_critics':True,'control':'t01','intermediate_fault':{'shot':'t02','frames':[91,92,93],'gate':'physicality'},'sparse_samples_valid':True,'before_contact_after_local_frames':[25,30,34]})
 write(P/'provenance.json',{'scope':'two isolated 2-second contact fixtures, not a film','canonical':'unchanged Motif Bot v1','sources':{str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'scripts/build_quality_hardening_fixtures.py',ROOT/'scripts/motif_ui_components.py',ROOT/'scripts/motif_quality_frames.py']},'intervention':'withheld expected.json not passed to critics'})
 html=(base/'index.html').read_text();start=html.index('<div class="clip"');end=html.index('<div id="host-captions"')
 mounts=''.join(f'<div class="clip" data-composition-id="{id_}" data-start="{i*2}" data-duration="2" data-composition-src="compositions/{id_}.html" data-track-index="0"></div>' for i,id_ in enumerate(('t01','t02')))
 html=html[:start]+mounts+html[end:];html=html.replace('12.5','4').replace('Recurring bills<br>start piling up','Lift and inspect<br>the source paper')
 (P/'index.html').write_text(html);print(P)
if __name__=='__main__':build()
