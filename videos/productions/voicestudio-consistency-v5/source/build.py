"""Rebuild changed art through the existing Motif frame compiler.

Copies frozen hero/caption compositions byte-for-byte; no TTS or audio build.
"""
from pathlib import Path
import importlib.util,sys,json,hashlib,shutil,re
ROOT=Path(__file__).resolve().parents[4];P=Path(__file__).resolve().parents[1];OLD=P.parent/'voicestudio-hero-art-v4'
sys.path.insert(0,str(ROOT/'scripts'))
from motif_ui_production import write_composition,namespace,read,write

def module(name,file):
 spec=importlib.util.spec_from_file_location(name,P/'source'/file);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

def load():
 components=module('motif_art_v4_components','components.py')
 base=module('motif_art_v4_actions','actions_v4.py')
 art=module('motif_consistency_v5_actions','actions.py')
 return components,base,art

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def build():
 comp,base,art=load();plan=read(P/'production-plan.json');engine=read(OLD/'scene-events.json');initial=[];events=[]
 for n,shot in enumerate(plan['shots'],1):
  id_=shot['id'];length=shot['endFrame']-shot['startFrame']
  if n in art.CHANGED:
   local=[{'time':round(f/30,9),'target':'#'+id_+'-world','action':'SET','params':{'props':{'innerHTML':namespace(art.scene(n,f,shot['headline'],shot['seed']),id_)}}} for f in range(1,length)]
   spec=write_composition(P,id_,length/30,art.scene(n,0,shot['headline'],shot['seed']),local,comp.DEFS)
   initial+=spec['initial'];events.extend({**e,'time':round(e['time']+shot['startFrame']/30,9),'composition':id_} for e in local)
  else:
   shutil.copy2(OLD/'compositions'/f'{id_}.html',P/'compositions'/f'{id_}.html')
   initial.extend(i for i in engine['initial'] if i['target']=='#'+id_+'-world');events.extend(e for e in engine['events'] if e['composition']==id_)
   assert all(base.scene(n,f,shot['headline'],shot['seed'])==art.scene(n,f,shot['headline'],shot['seed']) for f in range(length))
 engine.update(initial=initial,events=events);write(P/'scene-events.json',engine)
 registry=read(OLD/'component-registry.json');registry.update(art_revision='consistency-v5',source=['source/components.py','source/actions_v4.py','source/actions.py','source/build.py'],reused_art_provenance='assets/art-v4/provenance.json',changed_shots=list(art.CHANGED));write(P/'component-registry.json',registry)
 native=P/'native-mobile';native.mkdir(exist_ok=True)
 for folder in ('assets','compositions'):shutil.copytree(P/folder,native/folder,dirs_exist_ok=True)
 for name in ('package.json','hyperframes.json'):shutil.copy2(P/name,native/name)
 for file in (native/'compositions').glob('*.html'):file.write_text(file.read_text().replace('data-width="1080"','data-width="360"').replace('data-height="1920"','data-height="640"'))
 (native/'index.html').write_text((P/'index.html').read_text().replace('data-width="1080"','data-width="360"').replace('data-height="1920"','data-height="640"'))
 saved={str(p.relative_to(P)):digest(p) for folder in ['compositions','assets','source'] for p in (P/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
 saved.update({n:digest(P/n) for n in ['index.html','caption-events.json','audio-plan.json','style-preset.json']})
 preserved=['script.txt','production-plan.json','speech-timing.json','caption-events.json','caption-engine-events.json','audio-plan.json','assets/voice/narration-af-nova.wav','assets/voice/review-voice.wav','compositions/captions.html','index.html']
 identical={f:digest(P/f)==digest(OLD/f) for f in preserved};assert all(identical.values())
 write(P/'review-state.json',{'status':'REVIEW_REQUIRED','plan_sha256':digest(P/'production-plan.json'),'voice_sha256':digest(P/'assets/voice/narration-af-nova.wav'),'events_sha256':digest(P/'scene-events.json'),'saved_source_hashes':saved,'changed_shots':list(art.CHANGED),'unchanged_shots':[n for n in range(1,20) if n not in art.CHANGED],'preserved_inputs':identical,'human_review':'required; technical passes do not approve visual craftsmanship','rebuild':'python3 source/build.py'})
 print('Built eleven changed shots; eight untouched, including all five heroes. Frozen script/captions/audio/timing match.')
if __name__=='__main__':build()
