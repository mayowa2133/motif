#!/usr/bin/env python3
"""Saved native stills/compiled events for v1.1 hooks, never a new film."""
import sys,copy,shutil,re,math,io
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(ROOT/'tests'))
from motif_quality import read,write,verify_frozen,sha
from motif_quality_frames import ui_frame
from motif_ui_actions import scene
from motif_ui_components import DEFS
from motif_plan_compile import compile_plan
from motif_paper_investigation import build_scene,ASSET_IDS,BOT_DEFS,SCENE_DEFS,fragment
from test_quality_hardening import ui_contract,hand_points,xml,reaction_target,transform
from build_quality_fixtures import contract
from motif_reaction import point,compose,matrix
import cairosvg
P=ROOT/'quality/validation/v1.1/bindings'
def save(name,body,defs,viewbox):
 markup=f'<svg xmlns="http://www.w3.org/2000/svg" width="360" height="640" viewBox="{viewbox}"><defs>{defs}</defs>{body}</svg>'
 markup=re.sub(r'\b(data-layout-[a-z-]+)(?=\s|>)',r'\1=""',markup)
 (P/(name+'.svg')).write_text(markup)
 cairosvg.svg2png(bytestring=markup.encode(),url=str(ROOT/'quality/validation/v1.1/temporal/index.html'),write_to=str(P/(name+'.png')))
def build():
 verify_frozen();P.mkdir(parents=True,exist_ok=True);checks={}
 q=ui_contract();q['_cue_time']=.2
 for state in ('focused','burdened','absent'):
  variant=copy.deepcopy(q);variant['performance']['state']=state
  if state=='absent':variant['performance']['target']='';variant['art_direction']['bot_role']='absent';variant['reaction_radius']['targets']=[reaction_target('plant',[660,938])]
  body,contacts=ui_frame(scene,14,8,'Compare both players',5107,variant)
  save('ui-'+state,body,DEFS,'0 0 720 1280')
  checks['ui-'+state]={'contacts':len(contacts),'hand_error_native_pixels':math.dist(hand_points(body)['rightHand'],(165,790))*.5 if contacts else None,'svg_sha256':sha(P/('ui-'+state+'.svg'))}
 assets={n:fragment(str((ROOT/'assets/scenes/paper-investigation'/(n+'.svg')).relative_to(ROOT))) for n in ASSET_IDS}
 q=ui_contract();q['reaction_radius'].update(origin=[320,1050],radius=1000);q['reaction_radius']['targets']=[reaction_target('claim',[320,1050]),reaction_target('bot',[55,895])]
 markup,initial,events,contacts,cam=build_scene('calm','snap-open-then-buckle-sample-answer',.1,3,'subject',assets,q)
 t=.3;values={e['target']:e['params']['props']['innerHTML'] for e in events if abs(e['time']-t)<1e-6 and 'innerHTML' in e['params']['props']}
 paper=xml(values['#calm-claim']);m=compose(transform(paper[0].get('transform')),transform(paper[0][0].get('transform')));hands=hand_points(values['#calm-bot'])
 checks['calm']={'left_error_authoring_pixels':math.dist(hands['leftHand'],point(m,(20,345))),'right_error_authoring_pixels':math.dist(hands['rightHand'],point(m,(90,330)))}
 save('calm-contact',values['#calm-claim']+values['#calm-bot'],BOT_DEFS.removeprefix('<defs>').removesuffix('</defs>')+SCENE_DEFS.removeprefix('<defs>').removesuffix('</defs>'),'0 0 1080 1920')
 folder=ROOT/'videos/productions/little-book-workshop';plan=read(folder/'production-plan.json');plan['quality_mode']='motif-gold-v1';plan['asset_usage']=[{'id':'copied-workshop','scope':'reused','path':'assets/scenes/book-workshop/project-folio-kit.svg','metadata_path':'assets/scenes/book-workshop/project-folio-kit.json','agent_assisted':False}]
 for b in plan['beats']:
  q=contract();q.update(focal_target=b['focus_target'],framing=b['framing']);q['performance']={'state':'focused','target':'carrier-bot' if any(a['kind']=='workshop.deliver' for a in b['actions']) else 'worker-1'};q['reaction_radius'].update(origin=[540,1090],radius=600);q['reaction_radius']['targets']=[reaction_target('workshop-interaction',[540,1090])];b['quality']=q
 dest=P/'workshop';dest.mkdir(exist_ok=True)
 shutil.copytree(folder/'assets',dest/'assets',dirs_exist_ok=True)
 for name in ('package.json','hyperframes.json'):shutil.copy2(folder/name,dest/name)
 write(dest/'production-plan.json',plan);words=read(folder/'assets/voice/transcript.json');voice=read(folder/'audio-plan.json')['tracks'][0]['duration'];compile_plan(dest,plan,words,voice,[1,60])
 p=dest/'index.html';h=p.read_text().replace('data-width="1080"','data-width="360"').replace('data-height="1920"','data-height="640"').replace('width:1080px','width:360px').replace('height:1920px','height:640px');h=re.sub(r'<audio\b.*?</audio>','',h);p.write_text(h)
 actions=read(dest/'action-trace.json');delivery=next(a for a in actions if a['kind']=='workshop.deliver');write(dest/'snapshot-times.json',{'times':[delivery['cue_time']+.1,delivery['cue_time']+delivery['duration']*.5],'scope':'two native stills from copied approved workflow; no video encode'})
 checks['workshop']={'same_book_constituents':delivery['constituent_ids'],'reaction_target':'workshop-interaction','performance_channels':'head/face/antenna only','separate_unsafe_grip_reactions':'rejected','operative_events_sha256':sha(dest/'scene-events.json')}
 write(P/'results.json',checks);print(P)
if __name__=='__main__':build()
