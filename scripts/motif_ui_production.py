"""Text-directed UI adapter for Motif's existing planner/event/render pipeline.

Explicit supported recipes, editable component geometry, saved narration/alignment.
Not a general original-video planner. Re-rendering never replans or revoices.
"""
import argparse,difflib,json,math,re,shutil,wave
from pathlib import Path
import numpy as np
from jsonschema import Draft202012Validator
from fontTools.ttLib import TTFont
from motif_ui_components import *
from motif_ui_actions import KINDS,scene
from motif_produce import command,sha,probe,loudness,TARGET_I,PEAK_CEILING
ROOT=Path(__file__).resolve().parents[1]

def read(p):return json.loads(p.read_text())
def write(p,data):p.write_text(json.dumps(data,indent=2)+'\n')
def review(plan,brief):
 errors=[e.message for e in Draft202012Validator(read(ROOT/'schemas/text-directed-production-plan.schema.json')).iter_errors(plan)]
 if errors:return {'pass':False,'issues':errors}
 if plan['script']!=brief['script']:errors.append('supplied script changed')
 if plan['style']!=brief['style']:errors.append('explicit high-energy style changed')
 previous=0;ids=set()
 for shot in plan['shots']:
  if shot['id'] in ids:errors.append('duplicate shot ID')
  ids.add(shot['id'])
  if shot['kind'] not in KINDS:errors.append('unsupported finite UI action: '+shot['kind'])
  if shot['startFrame']!=previous or shot['endFrame']<=previous:errors.append('noncontiguous frame schedule')
  previous=shot['endFrame']
 if previous!=plan['targetFrames']:errors.append('picture length differs from plan')
 from motif_plan import tokens
 if tokens(' '.join(c['text'] for c in plan['captionPhrases']))!=tokens(plan['script']):errors.append('caption phrase words differ from script')
 return {'pass':not errors,'issues':errors,'scope':'finite capabilities, schema, exact script/caption words and contiguous schedule; not subjective approval or product fact check'}

def speech_mapping(script,words):
 from motif_plan import tokens
 wanted=tokens(script);heard=[]
 for w in words:
  for token_ in tokens(w['text']):
   pairs=[(wanted[i],wanted[i+1]) for i in range(len(wanted)-1) if wanted[i]+wanted[i+1]==token_]
   if len(pairs)==1 and len(w.get('centers',[]))>=2:
    split=(w['centers'][0]+w['centers'][-1])/2
    heard.extend([(pairs[0][0],w['start'],split),(pairs[0][1],split,w['end'])])
   else:heard.append((token_,w['start'],w['end']))
 # Homophone correction changes alignment identity only; captions retain supplied words.
 normalized=[('past' if x[0]=='passed' else 'eleven' if x[0]=='11' and 'elevenlabs' in wanted else x[0],x[1],x[2]) for x in heard]
 matcher=difflib.SequenceMatcher(a=wanted,b=[x[0] for x in normalized],autojunk=False)
 mapping={};merged=[]
 for block in matcher.get_matching_blocks():
  for k in range(block.size):mapping[block.a+k]=normalized[block.b+k][1:]
 for tag,ai,aj,bi,bj in matcher.get_opcodes():
  if tag=='equal':continue
  i,j=ai,bi
  while i<aj and j<bj:
   match=next(((a,b) for a in range(1,min(3,aj-i)+1) for b in range(1,min(3,bj-j)+1) if ''.join(wanted[i:i+a])==''.join(x[0] for x in normalized[j:j+b])),None)
   if not match:break
   a,b=match;start,end=normalized[j][1],normalized[j+b-1][2]
   for k in range(a):mapping[i+k]=(start,end)
   merged.append({'script_indices':list(range(i,i+a)),'heard_tokens':[x[0] for x in heard[j:j+b]],'interval':[start,end],'precision':'shared measured compound-word interval'})
   i+=a;j+=b
 measured=len(mapping);estimates=[]
 for i in range(len(wanted)):
  if i in mapping:continue
  before=mapping.get(i-1,(0,0))[1];after=next((mapping[k][0] for k in range(i+1,len(wanted)) if k in mapping),before+.15)
  start=max(0,min(before,after-.07));end=max(start+.04,after)
  mapping[i]=(start,end);estimates.append({'script_index':i,'word':wanted[i],'start':start,'end':end,'method':'estimated onset between adjacent measured DTW anchors; ASR missed this word'})
 return mapping,{'method':'installed Whisper small.en DTW; lexical matches and exact compound concatenation; passed/past homophone and 11/eleven numeral spelling normalization','measured_lexical_coverage':measured/len(wanted),'estimated_boundaries':estimates,'merged_groups':merged,'subjective_listening':'not assessed; exact supplied text verified as TTS input'}

def caption_schedule(plan,mapping):
 from motif_plan import tokens
 cursor=0;groups=[]
 for phrase in plan['captionPhrases']:
  words=[]
  for text in phrase['text'].split():
   count=len(tokens(text));indices=list(range(cursor,cursor+count));cursor+=count
   start=min(mapping[i][0] for i in indices);end=max(mapping[i][1] for i in indices)
   words.append({'text':text,'start':round(start*30)/30,'end':end,'script_indices':indices})
  # Compound recognizer intervals may coincide; use disclosed approximate separation
  # within that measured interval so each displayed word has a distinct entrance.
  for i in range(1,len(words)):
   if words[i]['start']<=words[i-1]['start']:words[i]['start']=min(words[i]['end']-.04,words[i-1]['start']+.10)
  groups.append({'text':phrase['text'],'sourceRhythmFrames':[phrase['startFrame'],phrase['endFrame']],'start':words[0]['start'],'words':words})
 for i,c in enumerate(groups):c['end']=groups[i+1]['start'] if i+1<len(groups) else plan['targetFrames']/30
 return groups

def font_width(font,text,size):
 cmap=font.getBestCmap();metrics=font['hmtx'].metrics;upem=font['head'].unitsPerEm
 return sum(metrics[cmap.get(ord(c),'.notdef')][0] for c in text)/upem*size

def captions_frame(groups,f,font):
 t=f/30;c=next((c for c in groups if c['start']<=t<c['end']),None)
 if c is None:return ''
 visible=[w for w in c['words'] if t+.0001>=w['start']]
 if not visible:return ''
 size=51;full=sum(font_width(font,w['text'],size)+18 for w in c['words'])+6*(len(c['words'])-1)
 if full>650:size*=650/full
 widths=[font_width(font,w['text'],size)+18 for w in visible];x=(720-sum(widths)-6*(len(widths)-1))/2;b=''
 for i,(w,width) in enumerate(zip(visible,widths)):
  age=(t-w['start'])*30;scale=.82+.18*spring(age/6);angle=([-1.7,1.0,-.65,1.45][i%4])
  tile=card(width,65,"#CC744F",.07)+txt(w['text'],width/2,48,size,'#FFF4DD',700,'middle',True)
  b+=g(g(tile,-width/2,-32),x+width/2,1040,angle,scale)
  x+=width+6
 return b

SOUND_MAP={
 1:[(33,'star'),(44,'pop'),(61,'paper')],2:[(28,'key1'),(49,'star')],3:[(15,'reject'),(34,'key2'),(46,'paper'),(57,'paper')],
 4:[(10,'paper'),(16,'key1'),(22,'key2'),(28,'key3')],5:[(4,'cloth'),(18,'washer'),(63,'pop')],6:[(8,'spring')],7:[(21,'pop'),(31,'paper'),(45,'key1')],
 8:[(3,'paper'),(16,'flutter'),(30,'cloth')],9:[(8,'key1'),(18,'key2'),(27,'key3'),(35,'key1'),(44,'key2'),(49,'star')],
 10:[(10,'flutter'),(23,'paper'),(34,'paper'),(43,'star')],11:[(7,'key1'),(18,'key2'),(28,'key3')],12:[(13,'paper'),(19,'key1'),(27,'key2'),(35,'key3'),(43,'paper')],
 13:[(14,'key1'),(29,'key2'),(40,'star')],14:[(1,'key1'),(9,'spring')],15:[(12,'key1'),(27,'key2'),(40,'star')],16:[(18,'key2'),(25,'pop')],
 17:[(12,'key1'),(23,'key2'),(36,'star')],18:[(14,'reject'),(47,'whoosh')],19:[(28,'key1'),(30,'key2'),(32,'key3'),(34,'key1'),(36,'key2'),(38,'star')]}
def make_sounds(project):
 folder=project/'assets/sfx';folder.mkdir(exist_ok=True);sr=24000;ledger=[]
 durations={'paper':.23,'flutter':.37,'cloth':.48,'key1':.08,'key2':.07,'key3':.09,'pop':.13,'spring':.19,'star':.24,'reject':.14,'washer':2.08,'whoosh':.39}
 for i,(name,duration) in enumerate(durations.items()):
  n=round(duration*sr);t=np.arange(n)/sr;rng=np.random.default_rng(7301+i);noise=rng.normal(0,1,n)
  low=np.convolve(noise,np.ones(27)/27,'same');mid=np.convolve(noise,np.ones(6)/6,'same')-low
  env=(1-np.exp(-t*900))*np.exp(-t*(22 if name.startswith('key') else 12))
  signal=low*.9+mid*.7
  if name in ('paper','flutter','cloth'):env=np.sin(np.pi*t/duration)**1.1*(.5+.5*np.sin(t*37+i)**6);signal=low*1.7+mid*.48
  if name.startswith('key'):signal+=np.sin(t*2*np.pi*(170+i*19))*.12
  if name in ('pop','spring','reject'):signal+=np.sin(2*np.pi*(250*t-220*t*t))*.32
  if name=='star':
   signal=low*.4+sum(np.sin(t*2*np.pi*hz)*.16 for hz in (330,495,660));env=np.exp(-t*20)*np.minimum(1,t*400)
  if name=='washer':env=(.30+.70*np.sin(t*2*np.pi*17)**12)*np.minimum(1,t*12)*np.minimum(1,(duration-t)*12);signal=low*2+np.sin(t*2*np.pi*91)*.04
  if name=='whoosh':env=np.sin(np.pi*t/duration)**1.4;signal=low*2+mid*.65
  y=signal*env;y/=max(1,np.max(np.abs(y)));y*=.32 if name.startswith('key') else .17 if name=='washer' else .35
  file=folder/(name+'.wav')
  with wave.open(str(file),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes((y*32767).astype('<i2').tobytes())
  ledger.append({'id':name,'file':str(file.relative_to(project)),'duration':duration,'source':'original deterministic filtered-noise and resonator construction','seed':7301+i,'external_recording':False,'sha256':sha(file)})
 return ledger

def namespace(markup,prefix):
 markup=re.sub(r'id="([^"]+)"',lambda m:f'id="{prefix}-def-{m[1]}"',markup)
 return re.sub(r'url\(#([^)]+)\)',lambda m:f'url(#{prefix}-def-{m[1]})',markup)
def write_composition(project,id_,duration,first,events,defs=''):
 spec={'schemaVersion':'1.0','compositionId':id_,'fps':30,'durationSec':duration,'initial':[{'target':'#'+id_+'-world','props':{'innerHTML':namespace(first,id_)}}],'events':events}
 literal=json.dumps(spec,separators=(',',':')).replace('</',r'<\/')
 html=f'<template><style>#{id_}-root{{position:absolute;inset:0;width:100%;height:100%;overflow:hidden}}</style><div id="{id_}-root" data-composition-id="{id_}" data-width="1080" data-height="1920" data-duration="{duration:.9f}"><svg width="100%" height="100%" viewBox="0 0 720 1280" xmlns="http://www.w3.org/2000/svg"><defs>{namespace(defs,id_)}</defs><g id="{id_}-world" data-layout-allow-overflow>{namespace(first,id_)}</g></svg></div><script>window.MotifEventEngine.compileFrames({literal},"{id_}");</script></template>'
 (project/'compositions'/f'{id_}.html').write_text(html);return spec

def compile_ui(project,plan,words,voice_duration):
 from motif_quality import plan_check,MODE
 from motif_quality_frames import ui_frame
 quality_mode=plan.get('quality_mode')==MODE
 if quality_mode:plan_check(plan)
 from motif_script import prepare_local_assets,write_index
 report=review(plan,read(project/'brief.json'))
 if not report['pass']:raise ValueError('; '.join(report['issues']))
 for file in ('script.txt','assets/voice/narration.txt'):
  if (project/file).read_text().strip()!=plan['script']:raise ValueError('saved narration input changed')
 duration=plan['targetFrames']/30
 if voice_duration>duration:raise ValueError(f'coherent narration {voice_duration:.6f} exceeds picture {duration:.6f}; regenerate cadence, never truncate speech')
 prepare_local_assets(project)
 shutil.copy2(ROOT/'assets/runtime/motif-frame-sequence.js',project/'assets/motif-frame-sequence.js')
 preset=read(project/'style-preset.json')
 preset['projectOverrides']=read(project/'brief.json').get('style_overrides',{})
 write(project/'style-preset.json',preset)
 surface=project/'assets/materials/world-paper.webp'
 if not surface.exists():
  from PIL import Image
  Image.open(project/'assets/materials/wall.png').save(surface,'WEBP',lossless=True,method=6)
 mapping,alignment=speech_mapping(plan['script'],words);groups=caption_schedule(plan,mapping)
 # Explicit production-scoped artwork revision. The coding agent authors these
 # fixed sources; plans cannot supply runtime code or arbitrary import paths.
 scene_renderer=scene;scene_defs=DEFS;caption_renderer=captions_frame
 revision=read(project/'brief.json').get('art_revision')
 if revision in ('art-performance-v3','hero-art-v4'):
  if quality_mode:raise ValueError('production-scoped art revision needs its own anchor-aware quality adapter; use registered interactive-ui-v1 components')
  import importlib.util,sys
  modules=[]
  prefix='motif_art_v4' if revision=='hero-art-v4' else 'motif_art_v3'
  for module_name,filename in [(prefix+'_components','components.py'),(prefix+'_actions','actions.py')]:
   spec=importlib.util.spec_from_file_location(module_name,project/'source'/filename)
   module=importlib.util.module_from_spec(spec);sys.modules[module_name]=module;spec.loader.exec_module(module);modules.append(module)
  scene_renderer=modules[1].scene;scene_defs=modules[0].DEFS
  caption_renderer=modules[0].caption_frame
 voice=project/'assets/voice/review-voice.wav'
 command(['ffmpeg','-v','error','-y','-i',str(project/'assets/voice/narration-af-nova.wav'),'-af',f'loudnorm=I={TARGET_I-1}:TP={PEAK_CEILING-.9}:LRA=11','-ar','24000','-ac','1',str(voice)],ROOT,log=project/'review/voice-level.log')
 ledger=make_sounds(project);cues=[];frames=[];events=[];initial=[];directions=[]
 for shot in plan['shots']:
  number=KINDS.index(shot['kind'])+1;end=(shot['endFrame']-shot['startFrame'])/30;id_=shot['id'];local=[]
  def paint(f):
   if not quality_mode:return scene_renderer(number,f,shot['headline'],shot['seed'])
   return ui_frame(scene_renderer,number,f,shot['headline'],shot['seed'],shot['quality'])[0]
  first=paint(0)
  for f in range(1,shot['endFrame']-shot['startFrame']):
   body=paint(f)
   local.append({'time':round(f/30,9),'target':'#'+id_+'-world','action':'SET','params':{'props':{'innerHTML':namespace(body,id_)}}})
  spec=write_composition(project,id_,end,first,local,scene_defs)
  frames.append({'id':id_,'start':shot['startFrame']/30,'duration':end,'source':'compositions/'+id_+'.html'})
  events.extend({**e,'time':round(e['time']+shot['startFrame']/30,9),'composition':id_} for e in local);initial+=spec['initial']
  for offset,name in SOUND_MAP[number]:
   item=next(x for x in ledger if x['id']==name);cues.append({'shot':id_,'start':(shot['startFrame']+offset)/30,'file':item['file'],'duration':item['duration'],'volume':.34 if name=='washer' else .36 if name.startswith('key') else .40,'meaning':name+' at specified physical interaction'})
  directions.append({**shot,'concurrent_layers':'pure frame-indexed waveforms, spinners, independent component motion and connected actor response','source_of_decisions':'supplied detailed text; coding-agent implementation','transition':'lateral push from absolute925 to937' if number==18 else 'settled continuation at937' if number==19 else 'hard cut'})
 font=TTFont(project/'assets/fonts/EBGaramond-700.woff2');capevents=[]
 for f in range(1,plan['targetFrames']):capevents.append({'time':round(f/30,9),'target':'#captions-world','action':'SET','params':{'props':{'innerHTML':namespace(caption_renderer(groups,f,font),'captions')}}})
 capspec=write_composition(project,'captions',duration,caption_renderer(groups,0,font),capevents,scene_defs)
 audio={'duration':voice_duration,'narration':'assets/voice/narration-af-nova.wav','review_input':'assets/voice/review-voice.wav','review_gain_db':0,'target_lufs':TARGET_I,'peak_ceiling':PEAK_CEILING,'sfx_cues':cues,'music':False,'subjective_listening':'not assessed'}
 engine={'schemaVersion':'1.0','durationSec':duration,'fps':30,'initial':initial,'events':events,'shots':frames}
 for name,data in [('scene-events.json',engine),('caption-events.json',groups),('caption-engine-events.json',capspec),('alignment-review.json',alignment),('shot-direction.json',directions),('execution-bindings.json',directions),('audio-plan.json',audio),('pre-render-checks.json',report),('sfx-source-manifest.json',{'assets':ledger,'music':'none; no cleared bed selected'})]:write(project/name,data)
 write_index(project,frames,duration,voice_duration,0)
 if quality_mode:write(project/'quality-bindings.json',{'mode':MODE,'renderer':'interactive-ui-v1','shots':[{'id':s['id'],'contract':s['quality']} for s in plan['shots']],'contacts':'explicit world anchors resolved after primary, reaction and performance transforms','limitations':'standalone plant/mug/lamp/clock and Bot reactions; attached screen/token/keyboard targets rejected'})
 sources={str(p.relative_to(project)):sha(p) for folder in ['compositions','assets'] for p in (project/folder).rglob('*') if p.is_file()}
 sources.update({n:sha(project/n) for n in ['index.html','caption-events.json','audio-plan.json','style-preset.json']})
 sources.update({str(p.relative_to(project)):sha(p) for p in (project/'source').glob('*.py')})
 write(project/'review-state.json',{'status':'REVIEW_REQUIRED','plan_sha256':sha(project/'production-plan.json'),'voice_sha256':sha(project/'assets/voice/narration-af-nova.wav'),'events_sha256':sha(project/'scene-events.json'),'saved_source_hashes':sources,'human_review':'required; technical passes do not approve creative results'})
 (project/'STORYBOARD.md').write_text('# VoiceStudio text-directed film\n\nStatus: REVIEW_REQUIRED\n\nThe supplied recipes drive nineteen supported UI actions; all geometry/choreography is agent-assisted.\n\n'+ '\n\n'.join(f'## {s["id"]}: {s["headline"]}\n\nFrames [{s["startFrame"]},{s["endFrame"]}); action `{s["kind"]}`.\n\n{s["recipe"]}' for s in plan['shots']))
 registry={'family':'interactive-ui-v1','scope':'finite text-directed UI study; new narrative decisions or geometry need explicit development','actions':list(KINDS),'components':sorted({c for s in plan['shots'] for c in s['components']}),'source':['scripts/motif_ui_components.py','scripts/motif_ui_actions.py'],'character':'existing locked canonical Motif Bot v1','seed':plan['seed'],'render_contract':'frame-baked SET events through existing MotifEventEngine, GSAP and pinned HyperFrames'}
 if revision in ('art-performance-v3','hero-art-v4'):
  registry.update(source=['source/components.py','source/actions.py'],art_revision=revision,art_provenance='assets/art-v4/provenance.json' if revision=='hero-art-v4' else 'assets/art-v3/provenance.json')
 write(project/'component-registry.json',registry)
 return engine

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--project',type=Path,required=True);parser.add_argument('--compile',action='store_true');parser.add_argument('--render',action='store_true');args=parser.parse_args();p=args.project.resolve()
 from motif_script import align_voice,render_preview
 if args.compile:
  if (p/'speech-timing.json').exists():speech=read(p/'speech-timing.json');words,d=speech['words'],speech['duration']
  else:words,d=align_voice(p)
  compile_ui(p,read(p/'production-plan.json'),words,d)
 if args.render:render_preview(p)
 print('REVIEW_REQUIRED '+str(p))
if __name__=='__main__':main()
