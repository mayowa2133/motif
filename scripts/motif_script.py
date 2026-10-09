"""Supplied-script adapter for the existing Motif director/compiler.

Planning is live data-only Codex. Unsupported geometry is an explicit capability
error. Saved-project preview never replans or regenerates narration/assets.
"""
import argparse,difflib,json,math,os,re,shutil,subprocess
from pathlib import Path
from html import escape
from jsonschema import Draft202012Validator
from motif_plan import ROOT,tokens,cue_index
from motif_produce import command,probe,loudness,sha,TARGET_I,PEAK_CEILING
import motif_paper_investigation as paper
PIN='0.8.99'
SCHEMA=ROOT/'schemas/script-production-plan.schema.json'
SCRIPT_ASSETS={'bot':'assets/characters/motif-bot/canonical/v1/motif-bot-v1.json','desk':'assets/scenes/scene-01/furniture/desk.svg','project-folio-kit':'assets/scenes/book-workshop/project-folio-kit.svg','source-chain-paper-set':'','missing-evidence-frame':''}
def read(p):return json.loads(p.read_text())
def write(p,value):p.write_text(json.dumps(value,indent=2)+'\n')
def review(plan,brief):
 if plan.get('style')=='reference-expressive-high-energy-v1':
  from motif_paper_energy import review_energy
  return review_energy(plan,brief)
 errors=[e.message for e in Draft202012Validator(read(SCHEMA)).iter_errors(plan)]
 if errors:return {'pass':False,'issues':errors}
 if plan['script']!=brief['script'] or ' '.join(b['narration'] for b in plan['beats'])!=brief['script']:errors.append('supplied script must be preserved character for character')
 if plan['audience']!=brief['audience']:errors.append('audience changed')
 if plan['style']!=brief['style'] or plan['style']!='reference-expressive-v1':errors.append('explicit registered style selection required')
 if not 1<=len(plan['beats'])<=12:errors.append('require 1–12 beats')
 for asset in plan['assets']:
  if asset['id'] not in SCRIPT_ASSETS or asset['reuse_path']!=SCRIPT_ASSETS.get(asset['id']):errors.append('unsupported asset or registry path: '+asset['id'])
 available={a['id'] for a in plan['assets']}
 if len({b['id'] for b in plan['beats']})!=len(plan['beats']):errors.append('duplicate beat IDs')
 facts=set();trace=[]
 for b in plan['beats']:
  if not re.fullmatch(r'[a-z0-9-]+',b['id']):errors.append('unsafe beat ID')
  if not b['actions']:errors.append('major beat needs physical action')
  if not set(b['needed_assets'])<=available:errors.append('unresolved beat asset request')
  for a in b['actions']:
   try:cue_index(b['narration'],a['cue'])
   except ValueError as e:errors.append(str(e))
   if a['kind'] not in paper.KINDS:errors.append('agent-assisted geometry required for unsupported action: '+a['kind']);continue
   mode,fact,needs,*_=paper.KINDS[a['kind']]
   if not set(needs)<=facts:errors.append('action prerequisites missing: '+a['kind'])
   facts.add(fact);trace.append({'beat':b['id'],'kind':a['kind'],'facts_after':sorted(facts)})
  if len(b['actions'])!=1:errors.append('this finite paper binding supports one meaningful action per beat')
  if not all(b[k].strip() for k in ('subject','action','before_after','focal_detail','consequence','focus_target')):errors.append('incomplete storyboard beat')
  if len(b['headline'])>22:errors.append('headline too long')
 if 'explained' not in facts:errors.append('supported investigation ending not delivered')
 return {'pass':not errors,'issues':errors,'states':trace,'scope':'finite capability/order/script checks; no assertion of audience engagement or factual truth'}

def align_voice(project):
 voice=project/'assets/voice/narration-af-nova.wav';prepared=voice.with_name('alignment16.wav');raw=voice.with_name('narration-dtw.json')
 if not raw.exists():
  command(['ffmpeg','-v','error','-y','-i',str(voice),'-ar','16000','-ac','1',str(prepared)],project)
  command(['/opt/homebrew/bin/whisper-cli','-m',str(Path.home()/'.cache/hyperframes/whisper/models/ggml-small.en.bin'),'-f',str(prepared),'-ojf','-of',str(raw.with_suffix('')),'--dtw','small.en','--no-flash-attn','--suppress-nst','-l','en'],project,log=project/'alignment.log')
 words=[]
 for phrase in read(raw)['transcription']:
  for tok in phrase['tokens']:
   text=tok['text']
   if text.startswith('['):continue
   if not text.strip():continue
   if text.strip() in ['.',',',':',';','!','?']:
    if words:words[-1]['text']+=text.strip()
    continue
   if tok['t_dtw']<0:raise ValueError('alignment lacks measured token centers')
   center=tok['t_dtw']/100
   if text.startswith(' ') or not words:words.append({'text':text.strip(),'centers':[center]})
   else:words[-1]['text']+=text;words[-1]['centers'].append(center)
 d=float(probe(voice)['format']['duration'])
 for i,w in enumerate(words):
  w['start']=max(0,(words[i-1]['centers'][-1]+w['centers'][0])/2 if i else w['centers'][0]-.12)
  w['end']=min(d,(w['centers'][-1]+words[i+1]['centers'][0])/2 if i<len(words)-1 else w['centers'][-1]+.12)
 write(project/'speech-timing.json',{'method':'installed Whisper small.en DTW; no flash attention; adjacent token-center midpoints','precision':'automatic approximate word boundaries, not phoneme-perfect','duration':d,'words':words})
 return words,d

def storyboard(project,plan,spans):
 lines=['# '+read(project/'brief.json')['title']+' — proposed storyboard','','Status: REVIEW_REQUIRED','','Rationale: '+plan['rationale'],'','Narration is the supplied script, unchanged. Planning: live Codex; geometry/choreography: agent-assisted finite shared bindings.','']
 for i,b in enumerate(plan['beats']):
  lines+=['## '+b['id'],'',f"Speech window: {spans[i]['start']:.2f}–{spans[i]['end']:.2f} s",'']+[f'- {k}: {b[k]}' for k in ('narration','subject','action','before_after','focal_detail','focus_target','framing','consequence','headline')]+['- Executable action: '+b['actions'][0]['kind'],'- Spoken cue: '+b['actions'][0]['cue'],'- Motion recipes: cursor-drag (matched grip/payload), viewport-change (bounded fit).','']
 (project/'STORYBOARD.md').write_text('\n'.join(lines))

def prepare_local_assets(project):
 for folder in ('assets','assets/fonts','assets/materials','assets/props','compositions','renders','review'): (project/folder).mkdir(parents=True,exist_ok=True)
 for name in ('gsap.min.js','motion-engine.js','motion-primitives.js'):shutil.copy2(ROOT/'videos/motif-calendar-reel/assets'/name,project/'assets'/name)
 frozen=ROOT/'videos/productions/reference-reconstruction-full-fine-cut'
 shutil.copy2(frozen/'assets/materials/wall.png',project/'assets/materials/wall.png')
 # Local rendering dependencies only, never included in a review archive or source package.
 fontroot=Path.home()/'.agents/skills/hyperframes-creative/frame-presets/code-editorial/fonts'
 for name in ('Inter-700.woff2','EBGaramond-700.woff2','OFL-inter.txt','OFL-eb-garamond.txt'):shutil.copy2(fontroot/name,project/'assets/fonts'/name)
 headline=Path.home()/'.cache/hyperframes/fonts/inter/900-normal-f82c7af24a98.woff2'
 shutil.copy2(headline,project/'assets/fonts/Inter-900.woff2')
 style=read(project/'brief.json').get('style','reference-expressive-v1')
 if style not in ('reference-expressive-v1','reference-expressive-high-energy-v1'):raise ValueError('unregistered script style')
 write(project/'style-preset.json',read(ROOT/'assets/styles'/f'{style}.json'))
 write(project/'package.json',{'name':project.name,'private':True,'scripts':{k:f'npx --yes hyperframes@{PIN} {v}' for k,v in [('check','check'),('render','render'),('dev','preview')]}})
 shutil.copy2(frozen/'hyperframes.json',project/'hyperframes.json')
 for name in paper.ASSET_IDS:
  for ext in ('.svg','.json'):
   destination=project/'assets/props'/(name+ext)
   if not destination.exists():shutil.copy2(paper.KIT/(name+ext),destination)

def compile_script(project,plan,words,voice_duration,duration_range=None):
 from motif_evidence import compile_scope
 compile_scope(project,plan)
 from motif_quality import plan_check,MODE
 if plan.get('quality_mode')==MODE:plan_check(plan)
 if plan.get('style')=='reference-expressive-high-energy-v1':
  from motif_paper_energy import compile_energy
  return compile_energy(project,plan,words,voice_duration)
 from motif_plan_compile import align
 brief=read(project/'brief.json');report=review(plan,brief)
 if not report['pass']:raise ValueError('; '.join(report['issues']))
 if (project/'script.txt').read_text().strip()!=brief['script'] or (project/'assets/voice/narration.txt').read_text().strip()!=brief['script']:raise ValueError('saved narration input differs from supplied script')
 preview_voice=project/'assets/voice/review-voice.wav'
 if not preview_voice.exists():
  command(['ffmpeg','-v','error','-y','-i',str(project/'assets/voice/narration-af-nova.wav'),'-af',f'loudnorm=I={TARGET_I}:TP={PEAK_CEILING-.3}:LRA=11','-ar','24000','-ac','1',str(preview_voice)],project,log=project/'review-level.log')
 # Existing lexical speech/action alignment routine is reused unchanged.
 spans,alignment=align(plan,words)
 for i,s in enumerate(spans):s['end']=spans[i+1]['start'] if i+1<len(spans) else voice_duration+.7
 spans[0]['start']=0.0
 duration=math.ceil((voice_duration+.7)*30)/30
 prepare_local_assets(project)
 assets={n:paper.fragment(str((project/'assets/props'/(n+'.svg')).relative_to(ROOT))) for n in paper.ASSET_IDS}
 frames=[];allinitial=[];allevents=[];bindings=[];actions=[]
 for i,(beat,span) in enumerate(zip(plan['beats'],spans,strict=True)):
  prefix=beat['id'];kind=beat['actions'][0]['kind'];local=span['actions'][0]['time']-span['start'];end=span['end']-span['start']
  markup,initial,events,contacts,cam=paper.build_scene(prefix,kind,local,end,beat['framing'],assets,beat.get('quality') if plan.get('quality_mode')==MODE else None)
  # Every source SVG ID/reference is namespaced across the assembled page.
  defs=paper.BOT_DEFS.removeprefix('<defs>').removesuffix('</defs>')+paper.SCENE_DEFS.removeprefix('<defs>').removesuffix('</defs>')
  defs+='<pattern id="wallSurface" width="2048" height="2048" patternUnits="userSpaceOnUse"><image href="assets/materials/wall.png" width="2048" height="2048"/></pattern><clipPath id="action-safe"><rect x="80" y="400" width="920" height="1110"/></clipPath>'
  defs=re.sub(r'id="([^"]+)"',lambda m:f'id="{prefix}-def-{m[1]}"',defs)
  def namespace(s):return re.sub(r'url\(#([^)]+)\)',lambda m:f'url(#{prefix}-def-{m[1]})',s)
  defs=namespace(defs);markup=namespace(markup)
  for ev in events:
   if 'innerHTML' in ev['params'].get('props',{}):ev['params']['props']['innerHTML']=namespace(ev['params']['props']['innerHTML'])
  spec={'schemaVersion':'1.0','compositionId':prefix,'durationSec':end,'fps':30,'initial':initial,'events':sorted(events,key=lambda e:e['time'])}
  headline=beat['headline']
  if headline:
   # A neutral prompt, not an assertion that the claim is verified.
   head=paper.put(paper.paper(840,122)+paper.txt(headline,420,84,58,paper.INK,'middle',900),120,238)
   markup+=f'<g id="{prefix}-headline">{namespace(head)}</g>'
   spec['initial'].append({'target':'#'+prefix+'-headline','props':{'opacity':0}})
   spec['events'].append({'time':min(.28,end-.1),'target':'#'+prefix+'-headline','action':'TWEEN','params':{'to':{'opacity':1},'duration':.18}})
  literal=json.dumps(spec,separators=(',',':')).replace('</',r'<\/')
  html=f'<template><style>#{prefix}-root{{position:absolute;inset:0;width:100%;height:100%;overflow:hidden}}svg text{{paint-order:stroke fill}}</style><div id="{prefix}-root" data-composition-id="{prefix}" data-width="1080" data-height="1920" data-duration="{end}"><svg width="100%" height="100%" viewBox="0 0 1080 1920" xmlns="http://www.w3.org/2000/svg"><defs>{defs}</defs>{markup}</svg></div><script>window.MotifEventEngine.compile({literal},"{prefix}");</script></template>'
  (project/'compositions'/(prefix+'.html')).write_text(html)
  frames.append({'id':prefix,'start':span['start'],'duration':end,'source':'compositions/'+prefix+'.html'})
  bindings.append({'beat':prefix,'requested_focus':beat['focus_target'],'requested_action':kind,'binding':paper.KINDS[kind][0],'framing':cam,'agent_authored_geometry':True})
  for c in contacts:actions.append({'beat':prefix,'spoken_cue':beat['actions'][0]['cue'],'cue_time':span['actions'][0]['time'],'complete':span['start']+c['complete'],'action':kind,'contact':c['method']})
  for e in spec['events']:allevents.append({**e,'time':round(e['time']+span['start'],6),'composition':prefix})
  allinitial+=spec['initial']
  write(project/'compositions'/(prefix+'.motion.json'),{'duration':end,'assertions':[{'kind':'appearsBy','selector':'#'+prefix+'-bot','bySec':min(.6,end/2)}]})
 # Exact source text, grouped in short chunks and anchored only by actual matched speech.
 heard=[]
 for w in words:
  for token in tokens(w['text']):heard.append((token,w['start'],w['end']))
 wanted=tokens(plan['script']);mapping={}
 for block in difflib.SequenceMatcher(a=wanted,b=[w[0] for w in heard],autojunk=False).get_matching_blocks():
  for j in range(block.size):mapping[block.a+j]=heard[block.b+j]
 # Preserve punctuation and case without coupling it to the geometry code.
 source_words=re.findall(r"[^\s—]+",plan['script']);chunks=[];cursor=0;group=[]
 for word in source_words:
  count=len(tokens(word));indices=list(range(cursor,cursor+count));cursor+=count
  group.append((word,indices))
  if len(group)==4 or re.search(r'[.!?]$',word):
   ids=[j for _,ix in group for j in ix];matched=[mapping[j] for j in ids if j in mapping]
   if not matched:raise ValueError('caption lacks actual speech anchor')
   chunks.append({'text':' '.join(w for w,_ in group),'start':matched[0][1],'end':matched[-1][2],'matched_words':len(matched),'script_indices':ids});group=[]
 if group:
  ids=[j for _,ix in group for j in ix];matched=[mapping[j] for j in ids if j in mapping];chunks.append({'text':' '.join(w for w,_ in group),'start':matched[0][1],'end':matched[-1][2],'matched_words':len(matched),'script_indices':ids})
 capbody='';capinitial=[];capevents=[]
 for i,c in enumerate(chunks):
  c['start']=round(c['start']*30)/30;c['end']=round(c['end']*30)/30
  next_start=round(chunks[i+1]['start']*30)/30 if i+1<len(chunks) else voice_duration
  c['end']=min(max(c['end'],c['start']+.1),next_start)
  w=min(890,max(380,len(c['text'])*27+64));left=(1080-w)/2
  capbody+=f'<g id="caption-{i}" class="caption-card" data-layout-allow-caption-zone><path d="M{left} 1634L{left+w} 1629L{left+w-4} 1750L{left+3} 1754Z" fill="{paper.INK}" opacity=".18" transform="translate(4 7)"/><path d="M{left} 1634L{left+w} 1629L{left+w-4} 1750L{left+3} 1754Z" fill="{paper.CORAL}"/><text x="540" y="1714" text-anchor="middle" fill="{paper.PAPER}" font-family="EB Garamond" font-weight="700" font-size="62">{escape(c["text"])}</text></g>'
  capinitial.append({'target':'#caption-'+str(i),'props':{'opacity':0}})
  capevents.append({'time':c['start'],'target':'#caption-'+str(i),'action':'CAPTION_REPLACE','params':{}})
  capevents.append({'time':c['end'],'target':'#caption-'+str(i),'action':'SET','params':{'props':{'opacity':0}}})
 capspec={'schemaVersion':'1.0','compositionId':'captions','durationSec':duration,'fps':30,'initial':capinitial,'events':sorted(capevents,key=lambda e:e['time'])}
 (project/'compositions/captions.html').write_text(f'<template><style>#captions-root{{position:absolute;inset:0;width:100%;height:100%}}</style><div id="captions-root" data-composition-id="captions" data-width="1080" data-height="1920" data-duration="{duration}"><svg width="100%" height="100%" viewBox="0 0 1080 1920">{capbody}</svg></div><script>window.MotifEventEngine.compile({json.dumps(capspec,separators=(",",":"))},"captions");</script></template>')
 for name,value in [('scene-events.json',{'schemaVersion':'1.0','durationSec':duration,'fps':30,'initial':allinitial,'events':sorted(allevents,key=lambda e:e['time']),'shots':frames}),('execution-bindings.json',bindings),('action-trace.json',actions),('alignment-review.json',alignment),('caption-events.json',chunks),('caption-engine-events.json',capspec),('pre-render-checks.json',report)]:write(project/name,value)
 storyboard(project,plan,spans)
 # Review-level voice calibration only. No music, SFX sourcing or final effects pass.
 preview_voice=project/'assets/voice/review-voice.wav'
 measured=loudness(preview_voice if preview_voice.exists() else project/'assets/voice/narration-af-nova.wav');gain=min(TARGET_I-measured['integrated_lufs'],PEAK_CEILING-measured['true_peak_dbtp']-.15)
 write(project/'audio-plan.json',{'narration':'assets/voice/narration-af-nova.wav','duration':voice_duration,'review_input':str(preview_voice.relative_to(project)) if preview_voice.exists() else 'assets/voice/narration-af-nova.wav','review_input_measurement':measured,'review_gain_db':gain,'target_lufs':TARGET_I,'peak_ceiling':PEAK_CEILING,'music':False,'sfx':False,'subjective_listening':'not assessed'})
 write_index(project,frames,duration,voice_duration,gain)
 write(project/'review-state.json',{'status':'REVIEW_REQUIRED','approval_required_before':'final material and audio polish','plan_sha256':sha(project/'production-plan.json'),'voice_sha256':sha(project/'assets/voice/narration-af-nova.wav'),'events_sha256':sha(project/'scene-events.json'),'caption_events_sha256':sha(project/'caption-events.json'),'bindings_sha256':sha(project/'execution-bindings.json'),'saved_source_hashes':{str(p.relative_to(project)):sha(p) for folder in ('compositions','assets/props') for p in (project/folder).glob('*') if p.is_file()},'finishing_rule':'resume these saved creative decisions; no implicit replan, TTS, or asset generation','duration_seconds':duration,'duration_note':'actual supplied reading; report deviation from suggested duration without padding or post-generation speed-up'})
 return duration

def write_index(project,frames,duration,voice_duration,gain,width=1080,height=1920):
 hosts=''.join(f'<div id="host-{f["id"]}" class="clip" data-composition-id="{f["id"]}" data-composition-src="{f["source"]}" data-start="{f["start"]}" data-duration="{f["duration"]}" data-track-index="1" data-track-kind="graphics" data-width="{width}" data-height="{height}"></div>' for f in frames)
 hosts+=f'<div id="host-captions" class="clip" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="{duration}" data-track-index="2" data-track-kind="captions" data-width="{width}" data-height="{height}"></div>'
 sfx=''
 audio=read(project/'audio-plan.json') if (project/'audio-plan.json').exists() else {}
 sfx_tracks=[]
 for i,c in enumerate(audio.get('sfx_cues',[])):
  if c['start']>=duration:continue
  track=next((j for j,end in enumerate(sfx_tracks) if end<=c['start']),len(sfx_tracks))
  if track==len(sfx_tracks):sfx_tracks.append(0)
  sfx_tracks[track]=c['start']+c['duration']
  sfx+=f'<audio id="sfx-{i}" src="{c["file"]}" data-start="{c["start"]}" data-duration="{min(c["duration"],duration-c["start"]):.6f}" data-volume="{c["volume"]}" data-track-index="{3+track}" data-track-kind="sfx"></audio>'
 css='@font-face{font-family:Inter;src:url(assets/fonts/Inter-700.woff2);font-weight:700}@font-face{font-family:Inter;src:url(assets/fonts/Inter-900.woff2);font-weight:900}@font-face{font-family:"EB Garamond";src:url(assets/fonts/EBGaramond-700.woff2);font-weight:700}*{box-sizing:border-box}html,body{margin:0;width:100%;height:100%;overflow:hidden;background:#BDAE8F}#root{position:relative;width:100%;height:100%}.clip{position:absolute;inset:0;width:100%;height:100%}'
 voice_file='assets/voice/review-voice.wav' if (project/'assets/voice/review-voice.wav').exists() else 'assets/voice/narration-af-nova.wav'
 html=f'<!doctype html><html lang="en"><head><meta charset="UTF-8"><title>Motif moving preview</title><style>{css}</style><script src="assets/gsap.min.js"></script><script src="assets/motion-primitives.js"></script><script src="assets/motion-engine.js"></script></head><body><div id="root" data-composition-id="main" data-start="0" data-duration="{duration}" data-width="{width}" data-height="{height}">{hosts}<audio id="narration" src="{voice_file}" data-start="0" data-duration="{voice_duration}" data-volume="{10**(gain/20):.7f}" data-track-index="0"></audio>{sfx}</div><script>window.__timelines["main"]=gsap.timeline({{paused:true}});</script></body></html>'
 if (project/'assets/motif-frame-sequence.js').exists():
  html=html.replace('</head>','<script src="assets/motif-frame-sequence.js"></script></head>')
 (project/'index.html').write_text(html)

def render_preview(project):
 from motif_evidence import require_scope
 require_scope(project)
 if read(project/'production-plan.json').get('quality_mode')=='motif-gold-v1':
  from motif_quality import rough,evidence_bundle,critics
  from motif_direct import backend_config
  output=rough(project)
  from motif_evidence import evidence_shots
  shots=evidence_shots(read(project/'quality-bindings.json'),read(project/'production-plan.json'))
  evidence_bundle(project,'rough',output/'captions.mp4',output/'no-captions.mp4',shots)
  critics(project,'rough',backend_config())
  return output/'captions.mp4'
 state=read(project/'review-state.json');spec=read(project/'scene-events.json');audio=read(project/'audio-plan.json')
 for field,path in [('plan_sha256','production-plan.json'),('voice_sha256','assets/voice/narration-af-nova.wav'),('events_sha256','scene-events.json')]:
  if sha(project/path)!=state[field]:raise ValueError('saved review input changed: '+path)
 for path,digest in state.get('saved_source_hashes',{}).items():
  if sha(project/path)!=digest:raise ValueError('saved layout/asset changed: '+path)
 n=1
 while (project/f'renders/preview-{n:02d}.mp4').exists():n+=1
 full=project/f'renders/preview-{n:02d}.mp4'
 render_flags=[]
 check_flags=[]
 if (project/'render-profile.json').exists():
  profile=read(project/'render-profile.json')
  workers=profile.get('workers',1)
  if not isinstance(workers,int) or not 1<=workers<=4:raise ValueError('render worker count must be 1–4')
  render_flags.append(f'--workers={workers}')
  if profile.get('capture')=='screenshot':render_flags.append('--experimental-fast-capture=false')
  timeout=profile.get('check_timeout_ms')
  if timeout is not None:
   if not isinstance(timeout,int) or not 3000<=timeout<=120000:raise ValueError('check timeout must be 3000–120000ms')
   check_flags.extend(['--timeout',str(timeout)])
 command(['npm','run','check','--','--strict','--json',*check_flags],project,log=project/f'review/check-{n:02d}.json')
 command(['npm','run','render','--','-o',str(full),'-q','looks',*render_flags],project,log=project/f'review/render-{n:02d}.log')
 native=project/'native-mobile';native.mkdir(exist_ok=True)
 for folder in ('assets','compositions'):shutil.copytree(project/folder,native/folder,dirs_exist_ok=True)
 for filename in ('package.json','hyperframes.json','audio-plan.json'):shutil.copy2(project/filename,native/filename)
 for child in (native/'compositions').glob('*.html'):
  child.write_text(child.read_text().replace('data-width="1080"','data-width="360"').replace('data-height="1920"','data-height="640"'))
 write_index(native,spec['shots'],spec['durationSec'],audio['duration'],audio['review_gain_db'],360,640)
 phone=project/f'renders/mobile-{n:02d}.mp4'
 command(['npm','run','check','--','--strict','--json',*check_flags],native,log=project/f'review/check-native-{n:02d}.json')
 command(['npm','run','render','--','-o',str(phone),'-q','looks',*render_flags],native,log=project/f'review/render-native-{n:02d}.log')
 delivery_full,delivery_phone,levels=calibrate_encoded_review(project,full,phone)
 write(project/f'review/encoded-{n:02d}.json',{'full':probe(delivery_full),'native':probe(delivery_phone),'loudness':loudness(delivery_full),'review_level_calibration':levels,'subjective_listening':'not assessed','status':'REVIEW_REQUIRED'})
 return full,phone

def calibrate_encoded_review(project,full,phone):
 """Existing combined-mix level constants; picture copied, not rerendered."""
 before=loudness(full);gain=TARGET_I-before['integrated_lufs']
 if before['true_peak_dbtp']+gain>PEAK_CEILING:gain=PEAK_CEILING-before['true_peak_dbtp']-.15
 out=project/'renders/moving-preview.mp4';mobile=project/'renders/mobile.mp4'
 command(['ffmpeg','-v','error','-y','-i',str(full),'-map','0:v:0','-map','0:a:0','-c:v','copy','-af',f'volume={gain:.5f}dB','-c:a','aac','-b:a','192k','-movflags','+faststart',str(out)],project,log=project/'review/review-level-full.log')
 command(['ffmpeg','-v','error','-y','-i',str(phone),'-i',str(out),'-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',str(mobile)],project,log=project/'review/review-level-native.log')
 after=loudness(out)
 if not TARGET_I-.8<=after['integrated_lufs']<=TARGET_I+.8 or after['true_peak_dbtp']>PEAK_CEILING:raise ValueError('encoded review mix misses existing level preset')
 return out,mobile,{'method':'combined encoded linear gain; native uses identical adjusted AAC; original picture streams retained','before':before,'gain_db':gain,'after':after,'scope':'comfortable review levels, not subjective listening approval or final sound design'}

def plan_script(brief_path):
 from motif_direct import backend_config,model_call
 brief=read(brief_path)
 if not re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*',brief['slug']):raise ValueError('unsafe slug')
 if not brief.get('script','').strip() or brief['style'] not in ('reference-expressive-v1','reference-expressive-high-energy-v1'):raise ValueError('supplied script and explicit style required')
 project=ROOT/'videos/productions'/brief['slug']
 if project.exists():raise ValueError('output exists; use saved project preview or a fresh slug')
 project.mkdir();(project/'assets/voice').mkdir(parents=True);write(project/'brief.json',brief);(project/'script.txt').write_text(brief['script']+'\n');(project/'assets/voice/narration.txt').write_text(brief['script']+'\n')
 from motif_evidence import entry_scope
 entry_scope(project, 'motif_script.plan_script')
 config=backend_config();write(project/'backend.json',config)
 prompt='Plan an original paper-world explanation from supplied script. Data only: no tools, code or files. Preserve script and audience EXACTLY. Beat narration joined with single spaces MUST equal script. Choose operative action kinds and focus/framing. Use physical before/after, readable focal detail and consequence; never certify truth by confidence, source existence or a checkmark. Existing finite capabilities: '+json.dumps({k:{'state_after':v[1],'requires':v[2]} for k,v in paper.KINDS.items()})+'. Available asset IDs and reuse paths: '+json.dumps(SCRIPT_ASSETS)+'. Unsupported requests are allowed in creative data but will stop compilation as explicit agent-assisted development needs. The current paper art specifically illustrates a fictional WILL summary versus MAY original and an unresolved evidence gap. It is not a general-purpose artwork generator; reject mismatched content rather than repainting keywords into this story. No hardcoded title/keyword lookup. No real studies or claims; sample documents only. No sales CTA. Reference-expressive-v1 opt-in. Brief: '+json.dumps(brief)
 if brief['style']=='reference-expressive-high-energy-v1':
  from motif_paper_energy import STAGES
  prompt+='\nACTIVE PRESET OVERRIDES: '+json.dumps(read(ROOT/'assets/styles/reference-expressive-high-energy-v1.json'))+'\nUse these high-energy action bindings instead: '+json.dumps(STAGES)+'. One dominant focal idea supports overlapping reactions, living motion, caption hits and transitions. Do not apply quiet one-action-then-hold rules. No parked multi-second diagrams.'
 from motif_quality import planning_context,direction_review
 prompt+=planning_context(brief['script'],project)
 plan=model_call(project,'initial-plan',prompt,'schemas/script-production-plan.schema.json',config)
 if plan.get('quality_mode')!='motif-gold-v1':raise ValueError('new script plans require motif-gold-v1')
 write(project/'production-plan.json',plan)
 from motif_structure import structure_review
 # Macro replanning precedes narration and does not spend a moving-repair pass.
 for attempt in range(2):
  try:
   structure_review(project,plan,config)
   break
  except ValueError:
   record=project/'quality-structure-record.json'
   if not record.exists() or read(record)['status']!='REPLAN_REQUIRED':raise
   archive=project/'planning-attempts'/str(attempt);archive.mkdir(parents=True)
   write(archive/'plan.json',plan)
   for artifact in project.glob('quality-structure*'):
    if artifact.is_file():shutil.copyfile(artifact,archive/artifact.name)
   if attempt==1:raise
   failures=read(project/'quality-structure.json')
   plan=model_call(project,'structure-replanned',prompt+'\nOne bounded macro replan. Preserve the exact script/audience. Rebuild setup boundaries rather than polishing the old architecture. Prior plan: '+json.dumps(plan)+'\nIndependent structure review: '+json.dumps(failures),'schemas/script-production-plan.schema.json',config)
   write(project/'production-plan.json',plan)
 direction_review(project,plan,config)
 (project/'STORYBOARD_INITIAL.md').write_text(json.dumps(plan,indent=2)+'\n')
 r=review(plan,brief);write(project/'pre-render-checks.json',r)
 if not r['pass']:raise ValueError('; '.join(r['issues']))
 env=os.environ.copy();env.setdefault('HYPERFRAMES_PYTHON',str(Path.home()/'.cache/motif-kokoro-venv/bin/python'))
 command(['npx','--yes',f'hyperframes@{PIN}','tts','--text-file=assets/voice/narration.txt','--voice=af_nova',f'--speed={brief.get("voice_speed",1)}','--output=assets/voice/narration-af-nova.wav','--json'],project,env,project/'tts.log')
 words,d=align_voice(project);compile_script(project,plan,words,d)
 if plan.get('quality_mode')=='motif-gold-v1':render_preview(project)
 return project
