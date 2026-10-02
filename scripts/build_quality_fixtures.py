#!/usr/bin/env python3
"""Short copied v6 regressions, never edits approved film or creates a new film."""
import sys,importlib.util,json,shutil,re
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from motif_quality import write,sha,verify_frozen
from motif_ui_production import write_composition,namespace
from motif_performance import render
P=ROOT/'quality/validation/fixtures';G=ROOT/'videos/productions/voicestudio-craft-v6'
def module(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

def contract():
 return dict(purpose='Show a recurring bill becoming a physical burden',hero='hinged pricing placards and accumulating receipts',primary_action='Subscribe, then recurring bills arrive',performance={'state':'burdened','target':'bot'},before='No billing receipts',after='Receipts accumulate and Bot slumps',focal_target='receipt pile',framing='subject',reaction_radius={'origin':[640,782],'radius':200,'duration':.6,'targets':[]},secondary_motion=['receipt flutter','antenna droop'],environment=['tile wall','receipt shelf'],exit_overlap='Receipt settling carries into next beat',energy={'dominant_action':'press subscription control','character_response':'compress, then carry financial burden','local_reaction':'control depresses and receipts collect','residual_motion':'paper settling and antenna droop','next_action_overlap':'later receipts arrive before earlier ones settle'},art_direction={'hero_object':'hinged pricing placards','bot_role':'participant','materials':['printed paper','wood shelf'],'depth_planes':['tile wall','pricing placards','receipts and Bot'],'composition':'Hero occupies action region; evidence visible without captions','intentional_irregularity':'asymmetric placards, layered receipts and varied shelf edges'})

def build():
 verify_frozen();P.mkdir(parents=True,exist_ok=True)
 if (P/'index.html').exists():raise ValueError('fixtures exist; preserve validation run')
 for d in ('source','assets','compositions','renders'): (P/d).mkdir(exist_ok=True)
 for name in ('components.py','actions_v4.py','actions.py'):shutil.copy2(G/'source'/name,P/'source'/name)
 # Minimal unchanged files needed by selected payment action, no full production copy.
 for folder in ('fonts','materials'):
  shutil.copytree(G/'assets'/folder,P/'assets'/folder,dirs_exist_ok=True)
 for name in ('gsap.min.js','motion-engine.js','motion-primitives.js'):shutil.copy2(G/'assets'/name,P/'assets'/name)
 shutil.copy2(ROOT/'assets/runtime/motif-frame-sequence.js',P/'assets/motif-frame-sequence.js')
 for name in ('package.json','hyperframes.json'):shutil.copy2(G/name,P/name)
 C=module('motif_art_v4_components',P/'source/components.py');B=module('motif_art_v4_actions',P/'source/actions_v4.py');A=module('motif_consistency_v5_actions',P/'source/actions.py')
 # Billing artwork is SVG only; the sampled control remains identical to v6.
 origreceipt=A.long_receipt;origbot=A.bot;origworld=A.price_world
 ids=['q01','q02','q03','q04','q05'];length=75;events=[];shots=[];initial=[]
 variants={'q01':'control','q02':'consequence-removed','q03':'tiny-hero','q04':'cheerful-burden','q05':'dead-hold'}
 for i,id_ in enumerate(ids):
  A.long_receipt=origreceipt;A.bot=origbot;A.price_world=origworld
  if id_=='q02':A.long_receipt=lambda *args,**kwargs:''
  if id_=='q03':
   def tiny(f,cancel=False):
    bg=A.backdrop;A.backdrop=lambda *args,**kwargs:''
    try:b=origworld(f,cancel)
    finally:A.backdrop=bg
    return bg(A.COLORS[2],'tiles',f)+A.g(A.g(b,-360,-640),360,640,s=.28)
   A.price_world=tiny
  if id_=='q04':
   def cheerful(x,y,f,**kw):
    if f<44:return origbot(x,y,f,**kw)
    return A.g(A.g(render('celebrating',(f-44)/30),-512,-904),x,y,s=kw.get('s',.29))
   A.bot=cheerful
  frames=[]
  for f in range(length):
   local=20 if id_=='q05' else min(69,10+f)
   frames.append(A.scene(3,local,'Recurring bills start piling up',5107,False))
  local=[{'time':f/30,'target':'#'+id_+'-world','action':'SET','params':{'props':{'innerHTML':namespace(frames[f],id_)}}} for f in range(1,length)]
  spec=write_composition(P,id_,length/30,frames[0],local,C.DEFS)
  file=P/'compositions'/f'{id_}.html';file.write_text(file.read_text().replace('data-width="1080"','data-width="360"').replace('data-height="1920"','data-height="640"'))
  initial+=spec['initial'];events += [{**e,'time':e['time']+i*length/30,'composition':id_} for e in local]
  shots.append({'id':id_,'kind':'reject-free-subscribe','headline':'Recurring bills start piling up','startFrame':i*length,'endFrame':(i+1)*length,'components':['pricing','bot','receipts'],'recipe':'copied validation fixture','seed':5107,'quality':contract()})
 plan={'schema_version':'text-directed-1.0','quality_mode':'motif-gold-v1','family':'interactive-ui-v1','style':'reference-expressive-high-energy-v1','script':'Recurring bills start piling up.','fps':30,'targetFrames':length*5,'seed':5107,'shots':shots,'asset_usage':[{'id':'billing-svg','scope':'production-specific','path':'quality/validation/fixtures/source/actions.py','metadata_path':'quality/validation/fixtures/fixture-provenance.json','agent_assisted':True}],'captionPhrases':[{'startFrame':0,'endFrame':length*5,'text':'Recurring bills start piling up.'}]}
 write(P/'production-plan.json',plan);write(P/'scene-events.json',{'fps':30,'durationSec':length*5/30,'initial':initial,'events':events})
 write(P/'shot-ranges.json',[{'id':s['id'],'startFrame':s['startFrame'],'endFrame':s['endFrame'],'contacts':[(s['startFrame']+24)/30,(s['startFrame']+34)/30]} for s in shots])
 write(P/'expected.json',{'withheld_from_critics':True,'variants':variants,'expected_violations':{'q02':['story','cause-effect'],'q03':['mobile','focal-hierarchy'],'q04':['character-performance'],'q05':['energy']}})
 mounts=''.join(f'<div id="host-{id_}" class="clip" data-composition-id="{id_}" data-start="{i*2.5}" data-duration="2.5" data-composition-src="compositions/{id_}.html" data-track-index="0"></div>' for i,id_ in enumerate(ids))
 html='''<!doctype html><html><head><script src="assets/gsap.min.js"></script><script src="assets/motion-primitives.js"></script><script src="assets/motion-engine.js"></script><script src="assets/motif-frame-sequence.js"></script><meta charset="utf-8"><style>@font-face{font-family:Inter;src:url('assets/fonts/Inter-700.woff2');font-weight:700}@font-face{font-family:Inter;src:url('assets/fonts/Inter-900.woff2');font-weight:900}@font-face{font-family:'EB Garamond';src:url('assets/fonts/EBGaramond-700.woff2');font-weight:700}html,body{margin:0;width:360px;height:640px;overflow:hidden}#root{width:360px;height:640px}.clip{position:absolute;inset:0}#host-captions{position:absolute;top:540px;left:12px;width:336px;text-align:center;background:#eee5d3;color:#211923;padding:8px;font:bold 20px Arial}</style></head><body><div id="root" data-composition-id="main" data-start="0" data-duration="12.5" data-width="360" data-height="640">'''+mounts+'<div id="host-captions" class="clip" data-start="0" data-duration="12.5" data-track-index="1">Recurring bills<br>start piling up</div></div><script>window.__timelines["main"]=gsap.timeline({paused:true});</script></body></html>'
 (P/'index.html').write_text(html)
 write(P/'fixture-provenance.json',{'source_commit':'76f21ba','source':str(G.relative_to(ROOT)),'scope':'copied short regressions; not a new film','source_hashes':{n:sha(G/'source'/n) for n in ('components.py','actions_v4.py','actions.py')},'caption_and_hero_changes':'isolated validation interventions; labels withheld from critic prompt'})
 print(P)
if __name__=='__main__':build()
