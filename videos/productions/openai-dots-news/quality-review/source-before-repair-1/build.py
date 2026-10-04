"""Compile authored Dots capabilities through existing Motif timeline/QA plumbing.

No replan or narration regeneration. Source functions are trusted agent-authored
production adapters, not executable data returned by the planning model.
"""
import difflib,json,math,pathlib,re,shutil,sys
sys.path[:0]=[str(pathlib.Path(__file__).resolve().parent),str(pathlib.Path(__file__).resolve().parents[4]/'scripts')]
from common import DEFS,CREAM,CORAL,card,g,text
import worlds
from motif_quality import ROOT,write,read,sha
from motif_plan_compile import align
from motif_plan import tokens
from motif_script import PIN,write_index
from motif_produce import command,loudness,TARGET_I,PEAK_CEILING

def local_assets(p):
 for d in ('assets/fonts','assets/materials','assets/props','compositions','renders','review'):(p/d).mkdir(parents=True,exist_ok=True)
 for name in ('gsap.min.js','motion-engine.js','motion-primitives.js'):shutil.copy2(ROOT/'videos/motif-calendar-reel/assets'/name,p/'assets'/name)
 shutil.copy2(ROOT/'assets/runtime/motif-frame-sequence.js',p/'assets/motif-frame-sequence.js')
 shutil.copy2(ROOT/'videos/productions/voicestudio-craft-v6/assets/materials/world-paper.webp',p/'assets/materials/world-paper.webp')
 frozen=ROOT/'videos/productions/reference-reconstruction-full-fine-cut';shutil.copy2(frozen/'assets/materials/wall.png',p/'assets/materials/wall.png')
 fonts=pathlib.Path.home()/'.agents/skills/hyperframes-creative/frame-presets/code-editorial/fonts'
 for name in ('Inter-700.woff2','EBGaramond-700.woff2','OFL-inter.txt','OFL-eb-garamond.txt'):shutil.copy2(fonts/name,p/'assets/fonts'/name)
 shutil.copy2(pathlib.Path.home()/'.cache/hyperframes/fonts/inter/900-normal-f82c7af24a98.woff2',p/'assets/fonts/Inter-900.woff2')
 write(p/'style-preset.json',read(ROOT/'assets/styles/reference-expressive-high-energy-v1.json'))
 write(p/'package.json',{'name':p.name,'private':True,'scripts':{k:f'npx --yes hyperframes@{PIN} {v}' for k,v in [('check','check'),('render','render'),('dev','preview')]}})
 shutil.copy2(frozen/'hyperframes.json',p/'hyperframes.json')

def captions(p,plan,words,alignment,duration,voice_duration):
 wanted=tokens(plan['script']);heard=[(tok,w['start'],w['end']) for w in words for tok in tokens(w['text'])];mapping={}
 for block in difflib.SequenceMatcher(a=wanted,b=[x[0] for x in heard],autojunk=False).get_matching_blocks():
  for j in range(block.size):mapping[block.a+j]=heard[block.b+j][1:]
 for item in alignment['merged_token_groups']:
  for i in item['script_indices']:mapping[i]=(item['start'],item['end'])
 groups=[];group=[];cursor=0
 for word in re.findall(r'[^\s—]+',plan['script']):
  ids=list(range(cursor,cursor+len(tokens(word))));cursor+=len(ids)
  if not ids:continue
  group.append((word,ids))
  if len(group)==3 or re.search(r'[.!?,:]$',word):groups.append(group);group=[]
 if group:groups.append(group)
 body='';initial=[];events=[];chunks=[]
 for i,group in enumerate(groups):
  ids=[n for _,ns in group for n in ns]
  if any(n not in mapping for n in ids):raise ValueError('unmeasured caption tokens: '+str(ids))
  start=round(mapping[ids[0]][0]*30)/30;end=round(mapping[ids[-1]][1]*30)/30;label=' '.join(w for w,_ in group)
  width=min(641,max(227,len(label)*20+40));font=min(47,(width-35)/(max(1,len(label))*.52));id_='caption-'+str(i)
  body+=f'<g id="{id_}" class="caption-card">'+g(card(width,95,"#B5573B"),(720-width)/2,1093)+text(label,360,1156,font,CREAM,'middle',700,True)+'</g>'
  initial.append({'target':'#'+id_,'props':{'opacity':0,'svgOrigin':'360 1140'}})
  events.extend([{'time':start,'target':'#'+id_,'action':'CAPTION_REPLACE','params':{}},{'time':start,'target':'#'+id_,'action':'FROM_TO','params':{'from':{'scale':.81,'y':9,'rotation':(-2 if i%2 else 2)},'to':{'scale':1,'y':0,'rotation':0},'duration':min(.15,max(.06,end-start)),'ease':'back.out(2.2)'}}])
  chunks.append({'text':label,'start':start,'end':end,'script_indices':ids})
 for i,c in enumerate(chunks):
  c['end']=min(chunks[i+1]['start'] if i+1<len(chunks) else voice_duration,max(c['end'],c['start']+.12));events.append({'time':c['end'],'target':'#caption-'+str(i),'action':'SET','params':{'props':{'opacity':0}}})
 spec={'schemaVersion':'1.0','compositionId':'captions','durationSec':duration,'fps':30,'initial':initial,'events':sorted(events,key=lambda e:e['time'])}
 literal=json.dumps(spec,separators=(',',':')).replace('</','<\\/')
 (p/'compositions/captions.html').write_text(f'<template><style>#captions-root{{position:absolute;inset:0;width:100%;height:100%}}</style><div id="captions-root" data-composition-id="captions" data-width="1080" data-height="1920" data-duration="{duration}"><svg width="100%" height="100%" viewBox="0 0 720 1280">{body}</svg></div><script>window.MotifEventEngine.compile({literal},"captions");</script></template>')
 write(p/'caption-events.json',chunks);write(p/'caption-engine-events.json',spec)


def temporal(setup,ctx,d):
 c=lambda b,n=0:worlds.cue(ctx,b,n)
 if setup=='s01':return [('landing',c('b01')+.4)]
 if setup=='s02':return [('contact',c('b03')+.3+i*.25) for i in range(3)]+[('landing',c('b04')+.4)]
 if setup=='s03':
  begin=max(.1,c('b05')-.8);remaining=max(1,d-begin-.45);return [('contact',begin+remaining*(i+1)/3) for i in range(3)]
 if setup=='s04':return [('contact',c('b06')+.35),('landing',c('b07')+.15),('landing',c('b07',1)+.05)]
 if setup=='s05':return [('impact',c('b08'))]
 if setup=='s06':return [('landing',c('b09')+.05),('contact',c('b09',1)+.1)]
 if setup=='s07':return [('landing',c('b10')+.15),('landing',c('b11')+.2)]
 if setup=='s08':return [('contact',min(d-.2,c('b12')+.45))]
 return []


def compile(p):
 p=pathlib.Path(p).resolve();plan=read(p/'production-plan.json');worlds.validate_bindings(plan);local_assets(p)
 from motif_news import require_direction,validate_script
 require_direction(p);validate_script(plan,read(p/'brief.json'))
 speech=read(p/'speech-timing.json');voice_duration=speech['duration'];words=speech['words']
 spans,alignment=align(plan,words);spans[0]['start']=0;duration=math.ceil((voice_duration+.6)*30)/30
 for i,s in enumerate(spans):s['end']=spans[i+1]['start'] if i+1<len(spans) else duration
 by_id={s['id']:s for s in spans};beats={b['id']:b for b in plan['beats']};frames=[];events=[];initial=[];review=[];bindings=[];motion=[]
 voice=p/'assets/voice/review-voice.wav'
 if not voice.exists():command(['ffmpeg','-v','error','-y','-i',str(p/'assets/voice/narration-af-nova.wav'),'-af',f'loudnorm=I={TARGET_I}:TP={PEAK_CEILING-.8}:LRA=11','-ar','24000','-ac','1',str(voice)],p,log=p/'review/voice-level.log')
 for setup in plan['film_structure']['setups']:
  id_=setup['setup_id'];begin=by_id[setup['beat_ids'][0]]['start'];end=by_id[setup['beat_ids'][-1]]['end'];d=end-begin
  ctx={b:{'start':by_id[b]['start']-begin,'end':by_id[b]['end']-begin,'cues':[a['time']-begin for a in by_id[b]['actions']],'quality':beats[b]['quality']} for b in setup['beat_ids']}
  def ns(body):
   body=re.sub(r'id="([^"]+)"',lambda m:f'id="{id_}-{m[1]}"',body)
   return re.sub(r'url\(#([^)]+)\)',lambda m:f'url(#{id_}-{m[1]})',body)
  first=ns(worlds.frame(id_,0,d,ctx));local=[]
  for f in range(1,math.ceil(d*30-1e-6)):
   t=min(f/30,d);body=ns(worlds.frame(id_,t,d,ctx))
   local.append({'time':round(t,6),'target':'#'+id_+'-world','action':'SET','params':{'props':{'innerHTML':body}}})
  spec={'schemaVersion':'1.0','compositionId':id_,'durationSec':d,'fps':30,'initial':[{'target':'#'+id_+'-world','props':{'innerHTML':first}}],'events':local}
  literal=json.dumps(spec,separators=(',',':')).replace('</','<\\/')
  (p/'compositions'/f'{id_}.html').write_text(f'<template><style>#{id_}-root{{position:absolute;inset:0;width:100%;height:100%;overflow:hidden}}</style><div id="{id_}-root" data-composition-id="{id_}" data-width="1080" data-height="1920" data-duration="{d:.6f}"><svg width="100%" height="100%" viewBox="0 0 720 1280"><defs>{ns(DEFS)}</defs><g id="{id_}-world" data-layout-allow-overflow>{first}</g></svg></div><script>window.MotifEventEngine.compileFrames({literal},"{id_}");</script></template>')
  frame={'id':id_,'start':begin,'duration':d,'source':f'compositions/{id_}.html'};frames.append(frame);initial+=spec['initial'];events += [{**e,'time':round(e['time']+begin,6),'composition':id_} for e in local]
  contacts=temporal(id_,ctx,d)
  for b in setup['beat_ids']:
   span=by_id[b];quality=beats[b]['quality'];temporal_events=[{'kind':kind,'time':round(begin+t,6)} for kind,t in contacts if span['start']<=begin+t<span['end']]
   review.append({'id':b,'start':span['start'],'end':span['end'],'temporal_events':temporal_events})
   bindings.append({'id':b,'contract':quality,'span':span,'setup':id_,'requested_actions':beats[b]['actions'],'executed_adapter':id_,'focus':quality['focal_target'],'framing':quality['framing'],'performance':'source/common.py canonical state channel' if quality['performance']['state']!='absent' else 'explicitly absent','reaction':'Numeric selected Bot response plus authored contact-specific local responses; empty target arrays do not enroll extras','status':'Executed provisional; moving approval required'})
  sidecar={'setup':id_,'start':begin,'duration':d,'rule':setup['visual_rule'],'recipes':['cursor-drag: matched payload/contact transforms','press-release-spring: caused local material settle','viewport-change: token close view in same setup'],'temporal_events':[{'kind':k,'time':begin+t} for k,t in contacts],'exit':setup['planned_reset_after']}
  write(p/'compositions'/f'{id_}.motion.json',sidecar);motion.append(sidecar)
 captions(p,plan,words,alignment,duration,voice_duration)
 spec={'schemaVersion':'1.0','durationSec':duration,'fps':30,'initial':initial,'events':events,'shots':frames,'review_shots':review}
 write(p/'scene-events.json',spec);write(p/'alignment-review.json',alignment);write(p/'quality-bindings.json',{'mode':'motif-gold-v1','shots':bindings,'hook':'provisional requested Dots bindings with explicit focus, role and contact channels','critic_consumers':['direction','story','visual']});write(p/'execution-bindings.json',bindings);write(p/'animation-map.json',motion)
 write(p/'audio-plan.json',{'narration':'assets/voice/narration-af-nova.wav','review_input':'assets/voice/review-voice.wav','duration':voice_duration,'review_gain_db':0,'music':False,'sfx':False,'phase':'rough; audio finishing blocked until final painted gates','review_input_measurement':loudness(voice),'subjective_listening':'not assessed'})
 write_index(p,frames,duration,voice_duration,0)
 lines=['# Original Dots storyboard','','Live planner: initial-plan.json. Pre-animation clarifications: planning-corrections.json. No external reference footage or prescribed initial shots.','']
 for setup in plan['film_structure']['setups']:
  lines+=['## Frame '+setup['setup_id'],'','status: animated',f'src: compositions/{setup["setup_id"]}.html','Rule: '+setup['visual_rule'],'Motion: cursor-drag / press-release-spring / viewport-change; pure-time Motif event compiler.','']
  for b in setup['beat_ids']:lines += [f'### {b} ({by_id[b]["start"]:.2f}–{by_id[b]["end"]:.2f}s)','',beats[b]['narration'],'',beats[b]['action'],'',beats[b]['consequence'],'']
 (p/'STORYBOARD.md').write_text('\n'.join(lines)+'\n')
 write(p/'build-record.json',{'duration':duration,'voice_duration':voice_duration,'setups':len(frames),'beats':len(spans),'source_sha256':{str(x.relative_to(p)):sha(x) for x in (p/'source').glob('*.py')},'plan_sha256':sha(p/'production-plan.json'),'events_sha256':sha(p/'scene-events.json'),'generation':'Live model data plan; agent-assisted finite artwork/choreography; shared Motif runtime, alignment, quality gates','art_phase':'provisional rough','human_approved':False})
 print('Compiled',duration,'seconds,',len(frames),'setups,',len(events),'frame events',flush=True)
