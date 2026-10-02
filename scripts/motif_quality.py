#!/usr/bin/env python3
"""Existing Motif quality gate. Critics inspect painted evidence; no averaging."""
import argparse,copy,hashlib,json,math,re,shutil,subprocess
from pathlib import Path
from jsonschema import Draft202012Validator
from motif_reaction import reaction
from motif_performance import render,STATES
ROOT=Path(__file__).resolve().parents[1]
MODE='motif-gold-v1'
def read(p):return json.loads(Path(p).read_text())
def write(p,v):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(v,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def cmd(args,cwd=None):
    p=subprocess.run([str(x) for x in args],cwd=cwd,text=True,capture_output=True)
    if p.returncode:raise ValueError('command failed: '+str(args[:3])+'\n'+p.stderr[-2000:])
    return p.stdout

def verify_frozen():
    hashes=read(ROOT/'quality/gold/frozen-manifest.json')['sha256']
    changed=[p for p,h in hashes.items() if not (ROOT/p).exists() or sha(ROOT/p)!=h]
    if changed:raise ValueError('frozen benchmark/canonical changed: '+str(changed[:5]))
    return {'files_verified':len(hashes),'unchanged':True}

def retrieve(tags,count=3):
    if not 2<=count<=4:raise ValueError('retrieve 2–4 examples')
    examples=read(ROOT/'quality/gold/index.json')['examples'];terms=set(re.findall(r'[a-z][a-z-]*',' '.join(tags).lower()))
    ranked=sorted(examples,key=lambda e:(-len(terms&set(e['tags'])),e['id']))[:count]
    return [{**e,'why_passes':(ROOT/e['note']).read_text()} for e in ranked]

def planning_context(text):
    examples=retrieve([text,'performance','physical-ui'])
    return '\n\nMANDATORY QUALITY MODE: set quality_mode to motif-gold-v1. Record asset_usage scopes (reused, production-specific, candidate-reusable, canonical-promoted), paths, metadata paths and explicit agent_assisted additions. Each beat/shot must have quality matching schemas/shot-contract.schema.json. All fields enter the pre-animation direction critic. Focus/framing and performance/reaction channels compile only through registered capabilities. Do not invent selectors. Calendar/arena and high-energy paper support named performance; other attached frame renderers need an anchor-aware hook and stop explicitly when unsupported. An absent Bot is valid only if absent in art direction. The director may request agent-assisted additions rather than force inappropriate reuse. No final artwork before moving rough critics pass.\n'+(ROOT/'QUALITY_CONTRACT.md').read_text()+'\n'+(ROOT/'ENERGY_CONTRACT.md').read_text()+'\nREGISTERED QUALITY BINDINGS: '+json.dumps(read(ROOT/'quality/bindings.json'))+'\nSHOT CONTRACT: '+json.dumps(read(ROOT/'schemas/shot-contract.schema.json'))+'\nRETRIEVED BEHAVIORAL EXAMPLES (not plot/pixel templates): '+json.dumps(examples)

def plan_check(plan):
    if plan.get('quality_mode')!=MODE:raise ValueError('explicit motif-gold-v1 plan required')
    if not plan.get('asset_usage'):raise ValueError('asset_usage must distinguish reuse, one-offs, candidates and promoted assets')
    for asset in plan['asset_usage']:
        if asset['scope']=='canonical-promoted':
            from motif_asset_quality import transition
            path=ROOT/asset['path'];meta=read(ROOT/asset['metadata_path'])
            if meta.get('state')!='CANONICAL':raise ValueError('unreviewed canonical asset: '+asset['id'])
            transition({**meta,'state':'REVIEW','scope':'candidate-reusable'},path,'CANONICAL',meta.get('promotion_review'))
    key='shots' if 'shots' in plan else 'beats';schema=read(ROOT/'schemas/shot-contract.schema.json')
    for beat in plan[key]:
        q=beat.get('quality');Draft202012Validator(schema).validate(q)
        if 'focus_target' in beat and q['focal_target']!=beat['focus_target']:raise ValueError('quality focal_target must bind existing focus_target')
        if 'framing' in beat and q['framing']!=beat['framing']:raise ValueError('quality framing must bind existing framing')
        if q['performance']['state']=='absent':
            if q['performance']['target'] or q['art_direction']['bot_role']!='absent':raise ValueError('absent Bot requires no target and absent role')
        elif not q['performance']['target'] or q['art_direction']['bot_role']=='absent':raise ValueError('participating Bot needs target and role')
    return {'status':'DIRECTION_REVIEW_REQUIRED','shots':len(plan[key]),'scope':'schema and binding consistency; no painted approval'}

def direction_review(project,plan,config):
    """Before animation: independent data critic, never called visual review."""
    from motif_direct import model_call
    plan_check(plan)
    prompt='Review shot contracts before animation. This is DATA ONLY, not visual QA. Identify weak subject/action/before/after/consequence, hero/material/depth/composition choices, unsupported interactions, ignored energy intentions. Art direction must be specific to this script. Return all planning-review schema fields. No tools.\n'+planning_context(json.dumps(plan))+'\nPLAN:'+json.dumps(plan)
    result=model_call(project,'quality-direction',prompt,'schemas/planning-review.schema.json',config)
    write(project/'quality-direction-record.json',{'plan_sha256':sha(project/'production-plan.json'),'response_sha256':sha(project/'quality-direction.json'),'invocation_sha256':sha(project/'quality-direction-invocation.json')})
    if not result['pass']:raise ValueError('pre-animation direction failed: '+json.dumps(result['issues']))
    return result

def group_wrap(html,id_,wrapper):
    """Insert a transform channel OUTSIDE an existing SVG group, retaining IDs."""
    m=re.search(r'<g\b[^>]*\bid="'+re.escape(id_)+r'"[^>]*>',html)
    if not m:raise ValueError('unregistered reaction target: '+id_)
    depth=1;end=None
    for tag in re.finditer(r'</?g\b[^>]*>',html[m.end():]):
        depth+=-1 if tag[0].startswith('</') else (0 if tag[0].endswith('/>') else 1)
        if depth==0:end=m.end()+tag.end();break
    if end is None:raise ValueError('unbalanced target group')
    return html[:m.start()]+f'<g id="{wrapper}" class="quality-reaction">'+html[m.start():end]+'</g>'+html[end:]

def apply_bindings(project,plan,spans):
    """Decorator for the existing static calendar/arena compiler and event engine."""
    if plan.get('quality_mode')!=MODE:return
    plan_check(plan)
    if plan.get('environment') not in ('calendar','arena'):
        raise ValueError('agent-assisted anchor-aware quality binding required for this renderer; fields cannot be silently ignored')
    spec=read(project/'scene-events.json');html=(project/'index.html').read_text();wrapped=set();trace=[]
    spans=copy.deepcopy(spans)
    for i,span in enumerate(spans):span['end']=spans[i+1]['start'] if i+1<len(spans) else spec['durationSec']
    prefixes=['bot'] if plan['environment']=='calendar' else ['pair-bot','close-A-bot','close-B-bot','review-bot']
    # Only groups deliberately registered by the static compiler can react. No DOM proximity enrollment.
    targets={'bot','opening','existing','proposed','committed','decision','decision-result','finger'} if plan['environment']=='calendar' else {'pair-bot','close-A-bot','close-B-bot','review-bot','receiver','pair-A','pair-B','close-A','close-B','review-A','review-B'}
    # Human finger has contacts; moving it without recomputing contacts is explicitly forbidden.
    targets.discard('finger')
    for b,s in zip(plan['beats'],spans,strict=True):
        q=b['quality'];start=s['start'];end=s['end'];cue=s['actions'][0]['time'] if s['actions'] else start
        state=q['performance']['state'];prefix=q['performance']['target']
        if state!='absent':
            if prefix not in prefixes:raise ValueError('unregistered performance target: '+prefix)
            for n in range(math.ceil(start*30),math.ceil(end*30)):
                t=n/30;body=render(state,max(0,t-cue))
                for face in ('thinking','pointing','presenting','happy'):
                    spec['events'].append({'time':t,'target':'#'+prefix+'-'+face,'action':'SET','params':{'props':{'innerHTML':body}}})
        r=q['reaction_radius']
        for target in r['targets']:
            id_=target['id'];wrapper='quality-reaction-'+id_
            if id_ not in targets:raise ValueError('unregistered or attached reaction target: '+id_)
            if id_ not in wrapped:html=group_wrap(html,id_,wrapper);wrapped.add(id_)
            # Never overlap two active reactions on one local transform: resolve explicitly.
            interval=[cue+target['delay'],cue+target['delay']+r['duration']]
            if any(x['id']==id_ and max(x['interval'][0],interval[0])<min(x['interval'][1],interval[1]) for x in trace):raise ValueError('overlapping reaction channel; explicit composition required')
            trace.append({'id':id_,'interval':interval,'origin':r['origin'],'selected_target':target,'beat':b['id']})
            for n in range(math.floor(cue*30),math.ceil(interval[1]*30)+1):
                t=n/30;v=reaction(t-cue,r['origin'],target['position'],r['radius'],target['relevance'],target['amplitude'],r['duration'],target['delay'])
                spec['events'].append({'time':t,'target':'#'+wrapper,'action':'SET','params':{'props':{**v,'svgOrigin':'0 0'}}})
    spec['events'].sort(key=lambda e:e['time']);write(project/'scene-events.json',spec)
    literal=json.dumps(spec,separators=(',',':')).replace('</','<\\/')
    html=re.sub(r'(<script id="motif-scene-events" type="application/json">).*?(</script>)',lambda m:m[1]+literal+m[2],html,flags=re.S)
    (project/'index.html').write_text(html)
    write(project/'quality-bindings.json',{'mode':MODE,'shots':[{'id':b['id'],'contract':b['quality'],'span':s} for b,s in zip(plan['beats'],spans)],'reactions':trace,'critic_consumers':['direction','story','visual']})

def reject_unbound(plan):
    if plan.get('quality_mode')==MODE:
        plan_check(plan)
        raise ValueError('agent-assisted anchor-aware quality hook required for attached/frame renderer; no ignored performance/reaction fields')

def probe_video(path):
    data=json.loads(cmd(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',path]));s=next(x for x in data['streams'] if x['codec_type']=='video')
    a,b=map(int,s['r_frame_rate'].split('/'))
    return {'width':s['width'],'height':s['height'],'fps':a/b,'frames':int(s['nb_read_frames']),'duration':int(s['nb_read_frames'])/(a/b),'sha256':sha(path)}

def rough(project):
    """Native moving rough, actual captions removed, using existing pinned render."""
    plan=read(project/'production-plan.json');plan_check(plan)
    if not (project/'quality-direction.json').exists() or not read(project/'quality-direction.json')['pass']:raise ValueError('pre-animation art/direction review required')
    direction=read(project/'quality-direction-record.json')
    if direction['plan_sha256']!=sha(project/'production-plan.json') or direction['response_sha256']!=sha(project/'quality-direction.json'):raise ValueError('pre-animation direction review is stale')
    output=project/'quality-review/rough';output.mkdir(parents=True,exist_ok=True)
    for mode in ('captions','no-captions'):
        dest=output/mode
        if dest.exists():raise ValueError('rough exists; archive this attempt before repair')
        dest.mkdir()
        for folder in ('assets','compositions'):
            if (project/folder).exists():shutil.copytree(project/folder,dest/folder)
        for name in ('package.json','hyperframes.json','index.html'):shutil.copy2(project/name,dest/name)
        for p in [dest/'index.html',*list((dest/'compositions').glob('*.html'))]:
            h=p.read_text().replace('data-width="1080"','data-width="360"').replace('data-height="1920"','data-height="640"').replace('width:1080px','width:360px').replace('height:1920px','height:640px')
            if mode=='no-captions':h=h.replace('</head>','<style>.caption-card,#host-captions,[data-composition-id="captions"]{display:none!important}</style></head>')
            p.write_text(h)
        # Strict native checks are separate evidence, not creative pass.
        for name,args in [('check',['npm','run','check']),('render',['npm','run','render','--','-o',str(output/(mode+'.mp4')),'--skill=general-video','-q','delivery'])]:
            log=subprocess.run(args,cwd=dest,text=True,capture_output=True);(dest/(name+'.log')).write_text(log.stdout+log.stderr)
            if log.returncode:raise ValueError('native '+name+' failed: '+str(dest/(name+'.log')))
    write(output/'render-record.json',{'scope':'moving rough only; not finished art/audio','plan_sha256':sha(project/'production-plan.json'),'events_sha256':sha(project/'scene-events.json'),'with_captions':probe_video(output/'captions.mp4'),'without_captions':probe_video(output/'no-captions.mp4')})
    return output

def evidence(video,out,shots):
    """Decode actual native media; full-rate motion observations plus ordered sheets."""
    from PIL import Image,ImageDraw
    import numpy as np
    info=probe_video(video)
    if (info['width'],info['height'])!=(360,640):raise ValueError('critic requires native 360×640 media')
    out.mkdir(parents=True,exist_ok=False)
    cmd(['ffmpeg','-v','error','-i',video,'-fps_mode','passthrough',out/'f-%05d.png'])
    files=sorted(out.glob('f-*.png'));images=[];trace=[];prev=None;unchanged=0;longest=0
    for i,p in enumerate(files):
        with Image.open(p) as im:crop=np.asarray(im.convert('RGB'))[140:510].astype('int16')
        mad=None if prev is None else float(np.abs(crop-prev).mean());prev=crop
        unchanged=unchanged+1 if mad is not None and mad<.025 else 0;longest=max(longest,unchanged)
        trace.append({'frame':i,'time':round(i/info['fps'],4),'action_region_pixel_delta':mad})
    for shot in shots:
        start=max(0,int(shot.get('startFrame',round(shot.get('start',0)*info['fps']))));end=min(len(files),int(shot.get('endFrame',round(shot.get('end',info['duration'])*info['fps']))))
        if end<=start:raise ValueError('invalid shot evidence range')
        # Eight evenly-spaced images plus declared contacts, shown at native pixel dimensions.
        indices=set(round(start+(end-start-1)*i/7) for i in range(8))
        indices.update(int(t*info['fps']) for t in shot.get('contacts',[]) if start<=int(t*info['fps'])<end)
        indices=sorted(indices);sheet=Image.new('RGB',(360*4,668*math.ceil(len(indices)/4)), '#eee5d5');d=ImageDraw.Draw(sheet)
        for k,i in enumerate(indices):
            with Image.open(files[i]) as im:sheet.paste(im.convert('RGB'),((k%4)*360,(k//4)*668+28))
            d.text(((k%4)*360+5,(k//4)*668+5),f'{shot["id"]} · frame {i} · {i/info["fps"]:.3f}s',fill='#202c32')
        path=out/(shot['id']+'-ordered.png');sheet.save(path);images.append(path)
        # Individual native frames avoid losing silhouette detail in a large sheet.
        for index in sorted({indices[0],indices[len(indices)//2],indices[-1]}):
            path=out/(shot['id']+f'-native-{index:05d}.png');shutil.copyfile(files[index],path);images.append(path)
    write(out/'motion-trace.json',{'scope':'full-rate painted action-region changes; not semantic motion grading','region':[0,140,360,510],'longest_nearly_unchanged_seconds':longest/info['fps'],'frames':trace})
    # Keep review sheets and motion trace; no duplicate 30fps PNG archive.
    for p in files:p.unlink()
    return {'video':str(Path(video).resolve()),'probe':info,'sheets':[str(p) for p in images],'motion_trace':str(out/'motion-trace.json'),'trace_sha256':sha(out/'motion-trace.json')}

def evidence_bundle(project,phase,with_captions,without_captions,shots,delivery_picture=None):
    if phase=='final' and delivery_picture is None:raise ValueError('final QA requires the matching delivery picture before audio finishing')
    base=project/'quality-review'/phase;base.mkdir(parents=True,exist_ok=True)
    a=evidence(with_captions,base/'evidence-captions',shots);b=evidence(without_captions,base/'evidence-no-captions',shots)
    if any(a['probe'][k]!=b['probe'][k] for k in ('fps','frames','duration')):raise ValueError('caption modes have different timing')
    source_files=[project/'index.html',*list((project/'compositions').rglob('*.html')),*[p for p in (project/'assets').rglob('*') if p.is_file()]]
    source_hashes={str(p.resolve()):sha(p) for p in source_files if p.exists()}
    manifest={'render_source_hashes':source_hashes,'phase':phase,'inspection':'ordered decoded native frames + full-rate pixel motion traces; CLI does not accept video','plan_sha256':sha(project/'production-plan.json'),'events_sha256':sha(project/'scene-events.json'),'with_captions':a,'without_captions':b,'shots':shots}
    if delivery_picture:
        delivery=probe_video(delivery_picture)
        if any(delivery[k]!=a['probe'][k] for k in ('fps','frames','duration')):raise ValueError('delivery and native preview timings differ')
        manifest['delivery_picture']={'file':str(delivery_picture.resolve()),'probe':delivery}
    write(base/'evidence.json',manifest);return manifest

def critics(project,phase,config):
    from motif_direct import model_call
    base=project/'quality-review'/phase;manifest=read(base/'evidence.json');plan=read(project/'production-plan.json')
    if manifest['plan_sha256']!=sha(project/'production-plan.json') or manifest['events_sha256']!=sha(project/'scene-events.json'):raise ValueError('stale visual evidence')
    gold=retrieve([json.dumps(plan),'physical-ui','performance'])
    images=[]
    for mode in ('with_captions','without_captions'):
        e=manifest[mode]
        if sha(e['video'])!=e['probe']['sha256']:raise ValueError('preview changed after sampling')
        images += [Path(p) for p in e['sheets']]
    # Gold stills plus ordered motion samples retrieved from their stable clip ranges.
    gold_evidence=[]
    for g in gold:
        dest=base/('gold-'+g['id']);clip=ROOT/g['clip']['file']
        if sha(clip)!=g['clip']['sha256']:raise ValueError('gold clip changed')
        if dest.exists():
            eg={'video':str(clip.resolve()),'probe':probe_video(clip),'sheets':[str(p) for p in sorted(dest.glob('*.png'))],'motion_trace':str(dest/'motion-trace.json'),'trace_sha256':sha(dest/'motion-trace.json')}
            if not eg['sheets']:raise ValueError('incomplete gold sample')
        else:eg=evidence(clip,dest,[{'id':g['id'],'startFrame':g['clip']['frames'][0],'endFrame':g['clip']['frames'][1]}])
        images += [Path(p) for p in eg['sheets']];gold_evidence.append({'id':g['id'],'notes':g['why_passes'],'evidence':eg})
    image_manifest=[{'file':str(p.resolve()),'sha256':sha(p)} for p in images];write(base/'image-inputs.json',image_manifest)
    observations=[]
    for mode in ('with_captions','without_captions'):
        trace=read(manifest[mode]['motion_trace'])
        observations.append({'mode':mode,'scope':trace['scope'],'region':trace['region'],'longest_nearly_unchanged_seconds':trace['longest_nearly_unchanged_seconds'],'timed_pixel_deltas':trace['frames'][::3]})
    common='Assess EVERY listed shot separately in shot_assessments, using its declared before/after and performance as intended meaning, and the actual images as truth. Do not let failures in one shot hide another. Compare posture against the requested role, not just the presence of Bot. If review_unit is independent-variants, assess within each clip; no continuity/progression is expected between variant boundaries. For an ordinary production, also assess the complete film progression. '+ 'No tools or web. Assess only contract violations, not arbitrary improvements. This is rendered evidence, NOT plan self-grading. The CLI receives images, not MP4 playback: inspect the ordered decoded native frame sequences and full-rate motion observations. Do not claim you watched/listened to the videos. If samples cannot establish a gate, mark NOT_ASSESSED. Gold is behavioral, never pixel matching or copying plot. Inspect both caption modes. Every FAIL must include timestamp, shot, gate, observation, relevant retrieved gold ID, smallest correction. Character performance may be NOT_APPLICABLE only when Bot is explicitly absent. No averaged score, particle quotas or global-jitter mandates. Return schema JSON.\n'+(ROOT/'QUALITY_CONTRACT.md').read_text()+'\n'+(ROOT/'ENERGY_CONTRACT.md').read_text()+'\nPLAN: '+json.dumps(plan)+'\nEVIDENCE and IMAGE ORDER: '+json.dumps(manifest)+'\nATTACHED IMAGES IN ORDER: '+json.dumps(image_manifest)+'\nPAINTED MOTION OBSERVATIONS (pixel delta is not semantic motion): '+json.dumps(observations)+'\nRETRIEVED GOLD: '+json.dumps(gold_evidence)
    results={}
    for role in ('story','visual'):
        prompt=(ROOT/f'quality/{"story-critic" if role=="story" else "visual-critic"}/PROMPT.md').read_text()+'\n'+common
        results[role]=model_call(base,role+'-critic',prompt,'schemas/'+role+'-critic.schema.json',config,images=images)
    write(base/'critics-record.json',{'evidence_sha256':sha(base/'evidence.json'),'images_sha256':sha(base/'image-inputs.json'),'gold_ids':[g['id'] for g in gold],'invocations':['story-critic-invocation.json','visual-critic-invocation.json'],'report_hashes':{role:sha(base/(role+'-critic.json')) for role in ('story','visual')},'invocation_hashes':{role:sha(base/(role+'-critic-invocation.json')) for role in ('story','visual')},'scope':manifest['inspection']})
    return evaluate(project,phase)

def evaluate(project,phase,check_current_events=True):
    base=project/'quality-review'/phase;manifest=read(base/'evidence.json');record=read(base/'critics-record.json');blocked=[]
    if record['evidence_sha256']!=sha(base/'evidence.json') or record['images_sha256']!=sha(base/'image-inputs.json'):blocked.append('critic input manifest changed')
    for image in read(base/'image-inputs.json'):
        if sha(image['file'])!=image['sha256']:blocked.append('critic frame changed')
    for mode in ('with_captions','without_captions'):
        e=manifest[mode]
        if sha(e['video'])!=e['probe']['sha256']:blocked.append('moving preview changed')
        if sha(e['motion_trace'])!=e['trace_sha256']:blocked.append('motion evidence changed')
    if manifest['plan_sha256']!=sha(project/'production-plan.json') or (check_current_events and manifest['events_sha256']!=sha(project/'scene-events.json')):blocked.append('plan/events changed; resample and re-critique')
    if 'delivery_picture' in manifest and sha(manifest['delivery_picture']['file'])!=manifest['delivery_picture']['probe']['sha256']:blocked.append('delivery picture changed')
    if check_current_events:
        for path,h in manifest.get('render_source_hashes',{}).items():
            if not Path(path).exists() or sha(path)!=h:blocked.append('render source changed: '+path)
    reports={};story_bad=False
    for role in ('story','visual'):
        r=read(base/(role+'-critic.json'));Draft202012Validator(read(ROOT/f'schemas/{role}-critic.schema.json')).validate(r);reports[role]=r
        if record.get('report_hashes',{}).get(role)!=sha(base/(role+'-critic.json')) or record.get('invocation_hashes',{}).get(role)!=sha(base/(role+'-critic-invocation.json')):blocked.append('critic report/invocation changed')
        invocation=read(base/(role+'-critic-invocation.json'))
        if invocation['exit_code']!=0 or invocation.get('saved_response_used') or invocation.get('model_fallback_used'):blocked.append('no valid live '+role+' invocation')
        expected=set(read(ROOT/'quality/rubric/gates.json')[role]);seen={g['gate'] for g in r['gates']}
        if expected!=seen or len(r['gates'])!=len(expected):blocked.append(role+' gate coverage incomplete')
        shots=read(project/'production-plan.json').get('beats',read(project/'production-plan.json').get('shots',[]));expected_shots={b['id'] for b in shots}
        assessments=r['shot_assessments']
        if {a['shot'] for a in assessments}!=expected_shots or len(assessments)!=len(expected_shots):blocked.append(role+' shot coverage incomplete')
        for assessment in assessments:
            if {g['gate'] for g in assessment['gates']}!=expected or len(assessment['gates'])!=len(expected):blocked.append(role+' incomplete shot gates: '+assessment['shot'])
            for g in assessment['gates']:
                absent=next((b['quality']['performance']['state']=='absent' for b in shots if b['id']==assessment['shot']),False)
                applicable=g['status']=='NOT_APPLICABLE' and g['gate']=='character-performance' and absent
                if g['status']!='PASS' and not applicable:blocked.append(role+': '+assessment['shot']+': '+g['gate']);story_bad|=role=='story'
                if g['status']=='FAIL' and not any(v['shot']==assessment['shot'] and v['gate']==g['gate'] for v in r['violations']):blocked.append('shot failure missing correction: '+assessment['shot']+': '+g['gate'])
        for g in r['gates']:
            allowed=g['status']=='NOT_APPLICABLE' and g['gate']=='character-performance' and all(b['quality']['performance']['state']=='absent' for b in read(project/'production-plan.json').get('beats',read(project/'production-plan.json').get('shots',[])))
            if g['status']!='PASS' and not allowed:blocked.append(role+': '+g['gate']);story_bad|=role=='story'
        for g in r['gates']:
            if g['status']=='FAIL' and not any(v['gate']==g['gate'] for v in r['violations']):blocked.append('failure missing correction: '+g['gate'])
        if any(v['gold_id'] not in record['gold_ids'] for v in r['violations']):blocked.append('violation references unretrieved gold')
    repairs=read(project/'quality-review/repairs.json') if (project/'quality-review/repairs.json').exists() else []
    status=('HUMAN_REVIEW_REQUIRED' if len(repairs)>=2 else 'REPLAN_REQUIRED' if story_bad else 'REPAIR_REQUIRED') if blocked else ('FINAL_ART_ALLOWED' if phase=='rough' else 'AUDIO_FINISH_ALLOWED')
    result={'phase':phase,'status':status,'blocked':blocked,'meaningful_repairs':len(repairs),'human_final_approval':'REQUIRED','publish':False,'report_hashes':{r:sha(base/(r+'-critic.json')) for r in reports},'evidence_sha256':sha(base/'evidence.json')}
    write(base/'gate.json',result);return result

def repair(project,note):
    p=project/'quality-review/repairs.json';items=read(p) if p.exists() else []
    if len(items)>=2:raise ValueError('two meaningful repair passes exhausted; human review required')
    current={'plan':sha(project/'production-plan.json'),'events':sha(project/'scene-events.json')}
    gates=list((project/'quality-review').glob('*/evidence.json'))
    if not gates:raise ValueError('repair needs prior moving evidence')
    previous=read(max(gates,key=lambda p:p.stat().st_mtime))
    if current=={'plan':previous['plan_sha256'],'events':previous['events_sha256']}:raise ValueError('unchanged plan/events is not a meaningful repair')
    if not note.strip():raise ValueError('repair must describe correction')
    items.append({'pass':len(items)+1,'correction':note,'hashes':current});write(p,items)
    for phase in ('rough','final'):
        d=project/'quality-review'/phase
        if d.exists():d.rename(project/'quality-review'/f'{phase}-before-repair-{len(items)}')
    return items

def require_gate(project,phase):
    result=evaluate(project,phase)
    wanted='FINAL_ART_ALLOWED' if phase=='rough' else 'AUDIO_FINISH_ALLOWED'
    if result['status']!=wanted:raise ValueError('quality gate blocks advancement: '+result['status']+' '+str(result['blocked']))
    if phase=='final':
        from motif_asset_quality import validate,CHECKS
        plan=read(project/'production-plan.json')
        for asset in plan.get('asset_usage',[]):
            if asset['scope']=='reused':continue
            path=ROOT/asset['path'];meta=read(ROOT/asset['metadata_path'])
            reviewed=meta.get('quality_review',meta.get('promotion_review',{}))
            if validate(meta,path) or meta.get('state') not in ('REVIEW','CANONICAL') or reviewed.get('asset_sha256')!=sha(path) or set(reviewed.get('checks',{}))!=set(CHECKS) or any(v!='PASS' for v in reviewed.get('checks',{}).values()):raise ValueError('new asset review incomplete: '+asset['id'])
        rough_result=evaluate(project,'rough',check_current_events=False)
        if rough_result['status']!='FINAL_ART_ALLOWED':raise ValueError('approved rough story required before final QA')
        technical=read(project/'quality-review/technical.json')
        if set(technical.get('checks',{}))!=set(TECHNICAL) or any(v!='PASS' for k,v in technical.get('checks',{}).items() if k not in ('loudness','true-peak')) or not technical.get('sources'):raise ValueError('technical gate coverage incomplete')
        if technical.get('status') not in ('PASS','PICTURE_PASS_AUDIO_PENDING') or technical.get('events_sha256')!=sha(project/'scene-events.json') or technical.get('video_sha256')!=manifest_hash(project,'final'):raise ValueError('separate current technical report required')
        for record in technical.get('sources',[]):
            if sha(record['file'])!=record['sha256']:raise ValueError('technical evidence changed')
    return result

def manifest_hash(project,phase):
    return read(project/'quality-review'/phase/'evidence.json')['with_captions']['probe']['sha256']

TECHNICAL=('frame-count','fps','dimensions','duration','assets','clipping','contrast','caption-overflow','safe-areas','runtime','tts-alignment','loudness','true-peak','provenance','licensing','anchors','generation-artifacts','reproducibility')
def technical(project,video,checks):
    """Normalize existing technical evidence, measure encoded media independently.

    Source reports for qualitative/license/alignment checks must be supplied;
    unavailable checks remain NOT_ASSESSED and block. No manufactured PASS.
    """
    from motif_produce import loudness,TARGET_I,PEAK_CEILING
    spec=read(project/'scene-events.json');info=probe_video(video);statuses={k:'NOT_ASSESSED' for k in TECHNICAL};sources=[]
    fps=spec['fps'];duration=spec['durationSec'];expected=round(duration*fps)
    statuses.update({'frame-count':'PASS' if info['frames']==expected else 'FAIL','fps':'PASS' if info['fps']==fps else 'FAIL','dimensions':'PASS' if (info['width'],info['height'])==(360,640) else 'FAIL','duration':'PASS' if abs(info['duration']-duration)<1/fps else 'FAIL'})
    try:
        audio=loudness(video);statuses['loudness']='PASS' if abs(audio['integrated_lufs']-TARGET_I)<=.8 else 'FAIL';statuses['true-peak']='PASS' if audio['true_peak_dbtp']<=PEAK_CEILING else 'FAIL'
    except (ValueError,RuntimeError,KeyError,StopIteration):audio={'status':'NOT_ASSESSED'}
    supplied=read(checks)
    for name,record in supplied.items():
        if name not in TECHNICAL or name in ('frame-count','fps','dimensions','duration','loudness','true-peak'):raise ValueError('not a supplemental technical check: '+name)
        path=Path(record['file']).resolve()
        if not path.is_file() or sha(path)!=record['sha256'] or record.get('events_sha256')!=sha(project/'scene-events.json') or record.get('video_sha256')!=sha(video):raise ValueError('stale supplemental technical evidence: '+name)
        if record.get('status') not in ('PASS','FAIL','NOT_ASSESSED') or not record.get('observation'):raise ValueError('technical result requires status and measured observation')
        statuses[name]=record['status'];sources.append({'file':str(path),'sha256':sha(path),'check':name})
    sources.append({'file':str(checks.resolve()),'sha256':sha(checks)})
    status='PASS' if all(v=='PASS' for v in statuses.values()) else 'PICTURE_PASS_AUDIO_PENDING' if all(v=='PASS' for k,v in statuses.items() if k not in ('loudness','true-peak')) else 'BLOCKED'
    result={'status':status,'checks':statuses,'probe':info,'audio':audio,'sources':sources,'events_sha256':sha(project/'scene-events.json'),'video_sha256':sha(video),'human_listening':'REQUIRED; measurement is not listening approval'}
    write(project/'quality-review/technical.json',result);return result

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['retrieve','verify-frozen','plan-check','direction','rough','sample','critique','gate','repair','technical','asset-transition']);p.add_argument('--project',type=Path);p.add_argument('--phase',choices=['rough','final'],default='rough');p.add_argument('--tags',nargs='*',default=[]);p.add_argument('--with-captions',type=Path);p.add_argument('--without-captions',type=Path);p.add_argument('--shots',type=Path);p.add_argument('--note',default='');p.add_argument('--asset',type=Path);p.add_argument('--metadata',type=Path);p.add_argument('--review',type=Path);p.add_argument('--state',choices=['REVIEW','CANONICAL']);p.add_argument('--output',type=Path);p.add_argument('--checks',type=Path);p.add_argument('--delivery-picture',type=Path);a=p.parse_args()
    if a.action=='retrieve':value=retrieve(a.tags)
    elif a.action=='verify-frozen':value=verify_frozen()
    elif a.action=='asset-transition':
        from motif_asset_quality import transition
        value=transition(read(a.metadata),a.asset,a.state,read(a.review) if a.review else None)
        if not a.output:raise ValueError('explicit metadata output path required')
        write(a.output,value)
    else:
        project=a.project.resolve();plan=read(project/'production-plan.json')
        if a.action=='plan-check':value=plan_check(plan)
        elif a.action=='direction':
            from motif_direct import backend_config
            value=direction_review(project,plan,backend_config())
        elif a.action=='rough':value=str(rough(project))
        elif a.action=='sample':value=evidence_bundle(project,a.phase,a.with_captions,a.without_captions,read(a.shots),a.delivery_picture)
        elif a.action=='critique':
            from motif_direct import backend_config
            value=critics(project,a.phase,backend_config())
        elif a.action=='gate':value=require_gate(project,a.phase)
        elif a.action=='technical':value=technical(project,a.with_captions,a.checks)
        else:value=repair(project,a.note)
    print(json.dumps(value,indent=2))
if __name__=='__main__':main()
