"""Finite plan actions -> approved SVG bindings and the existing Motif event engine."""
import difflib
import json
import re
from html import escape
from pathlib import Path
from build_motif_bot import DEFS as BOT_DEFS, assemble_pose
from build_scene_01 import DEFS
from motif_plan import ROOT, ASSETS, cue_index, narration, tokens
from motif_produce import probe

INK='#202C32'; PAPER='#F4EBD8'; TEAL='#318E85'; CORAL='#C66355'

def fragment(asset):
    raw=(ROOT/ASSETS[asset]).read_text()
    body=raw.split('</defs>',1)[-1]
    body=re.sub(r'^\s*<svg[^>]*>\s*(?:<title>.*?</title>\s*)?', '', body, flags=re.S)
    return body.rsplit('</svg>',1)[0].strip()

def text(value,x,y,size=58,color=INK,anchor='start'):
    return f'<text x="{x}" y="{y}" font-family="MotifSans, Arial, sans-serif" font-size="{size}" font-weight="900" text-anchor="{anchor}" fill="{color}">{escape(value)}</text>'

def layer(id_,body,x=0,y=0,scale=1):
    return f'<g transform="translate({x} {y}) scale({scale})" data-layout-allow-overflow><g id="{id_}" class="motion-asset" data-layout-allow-overflow>{body}</g></g>'

def mark(id_,x,y,passed=False):
    color=TEAL if passed else CORAL
    shape='<path d="M-24 0 l19 20 34 -40"/>' if passed else '<path d="M-21 -21 l42 42 M21 -21 l-42 42"/>'
    return layer(id_,f'<circle r="49" fill="{PAPER}" stroke="{color}" stroke-width="7"/><g fill="none" stroke="{color}" stroke-width="11" stroke-linecap="round" stroke-linejoin="round">{shape}</g>',x,y)

def sign(id_,value,caption=False):
    y=1660 if caption else 72
    width=min(880,max(360, len(value)*29+100)) if caption else 880
    left=(1080-width)/2; right=left+width
    path=f'M{left+10} {y+8} Q540 {y-2} {right-10} {y+8} L{right-15} {y+115} Q540 {y+125} {left+6} {y+111} Z'
    body=f'<path d="{path}" transform="translate(7 10)" fill="{INK}" opacity=".22"/><path d="{path}" fill="{PAPER}" stroke="#DCCDB3" stroke-width="5"/><path d="{path}" fill="url(#paperSpeckle)" opacity=".5"/>'+text(value,540,y+80,56 if caption else 62,anchor='middle')
    return f'<g id="{id_}" class="paper-type {"caption-card" if caption else "headline-card"}" data-layout-allow-overflow>{body}</g>'

def bot(prefix,x,y,scale):
    bodies=[]
    for name,base,face in [('thinking','standing','thinking'),('pointing','pointing','confused'),('presenting','presenting','thinking'),('happy','presenting','happy')]:
        body,_=assemble_pose(base,face,{})
        body=re.sub(r'id="([^"]+)"',lambda m:f'id="{prefix}-{name}-{m[1]}"',body)
        bodies.append(f'<g id="{prefix}-{name}" class="bot-pose">{body}</g>')
    return layer(prefix,''.join(bodies),x,y,scale)

def backdrop(arena=False):
    body=fragment('wall')+layer('floor-static',fragment('floor'),0,1430)
    if arena:
        body+=layer('crowd-static',fragment('crowd'),50,375)+layer('arch-static',fragment('arena-arch'),90,275)
        body+=layer('stage-static',fragment('stage'),90,1320)
    else: body+=layer('desk-static',fragment('desk'),70,1390)
    return body

def calendar_world(plan):
    labels=plan['calendar']
    decision='DECLINE' if any(a['kind']=='calendar.decline' for b in plan['beats'] for a in b['actions']) else 'APPROVE'
    board=fragment('calendar-board')
    body=layer('calendar-board',board,120,315)
    body+=layer('existing',fragment('appointment')+text(labels['existing_title'],74,88,54),380,625,.85)
    body+=layer('committed',fragment('appointment')+text(labels['proposed_title'],74,88,54),590,975,.85)
    body+=layer('proposed',fragment('proposal')+text(labels['proposed_title'],74,89,52,TEAL),590,975,.85)
    body+=layer('opening','<path d="M471 941 h-22 q-10 0 -10 11 v173 q0 11 10 11 h22 M940 941 h23 q10 0 10 11 v173 q0 11 -10 11 h-23" fill="none" stroke="#318E85" stroke-width="12" stroke-linecap="round"/>')
    body+=bot('bot',120,1135,.38)
    tab=fragment('decision-tab').replace('APPROVE',decision)
    body+=layer('decision',tab,613,1238)
    body+=mark('decision-result',678,1320,decision=='APPROVE')
    body+=layer('finger',fragment('human-hand'),690,1160)
    return backdrop()+f'<g id="world-camera" data-layout-allow-overflow>{body}</g>'

def sheet(prefix,letter,x,y,scale):
    ink='#64869A' if letter=='A' else CORAL
    body=fragment('answer-sheet')+text(letter,112,113,80,ink)
    body+=layer(prefix+'-stencil',fragment('stencil'),50,415)
    # Both pass and fail geometry exist, but a validated action chooses one.
    ends='<circle cx="143" cy="552" r="28"/><circle cx="616" cy="552" r="28"/>'
    for result,path in [('fail','M192 552 H325 M452 552 H565'),('pass','M192 552 H565')]:
        color=CORAL if result=='fail' else TEAL
        body+=layer(prefix+'-'+result,f'<g fill="{PAPER}" stroke="{color}" stroke-width="15">{ends}</g><path d="{path}" fill="none" stroke="{color}" stroke-width="28" stroke-linecap="round"/>')
        body+=mark(prefix+'-'+result+'-mark',384,552,result=='pass')
    return layer(prefix,body,x,y,scale)

def arena_world(plan):
    body=backdrop(True)
    pair=sheet('pair-A','A',110,570,.48)+sheet('pair-B','B',605,570,.48)+bot('pair-bot',365,1100,.34)
    close_a=sheet('close-A','A',160,390,1)+bot('close-A-bot',70,1230,.26)
    close_b=sheet('close-B','B',160,390,1)+bot('close-B-bot',70,1230,.26)
    review=sheet('review-A','A',160,600,.40)+sheet('review-B','B',510,600,.40)+bot('review-bot',85,1130,.34)
    # Existing fingertip, acting as a separately attributed receiving person.
    review+=layer('receiver',fragment('human-hand'),680,850,.9)
    review+=layer('winner',text('SELECTED',540,1180,65,TEAL,anchor='middle'))
    return body+''.join(layer('shot-'+name,value) for name,value in [('arena-pair',pair),('arena-a',close_a),('arena-b',close_b),('arena-review',review)])

def align(plan, words):
    wanted=tokens(narration(plan))
    heard=[]
    for w in words:
        for word in tokens(w['text']): heard.append((word,w['start'],w['end']))
    # Only lexical matches from actual speech are usable anchors. Unmatched words are not interpolated.
    matcher=difflib.SequenceMatcher(a=wanted,b=[w[0] for w in heard],autojunk=False)
    mapping={}
    for block in matcher.get_matching_blocks():
        for i in range(block.size): mapping[block.a+i]=heard[block.b+i]
    merged=[]
    # Whisper may merge adjacent words (e.g. 'a cross' -> 'across', 'B takes' -> 'Btakes').
    # Recover only exact concatenations; all recovered words share the measured
    # token interval. Never interpolate a fictional within-token word boundary.
    for tag,ai,aj,bi,bj in matcher.get_opcodes():
        if tag=='equal': continue
        i,j=ai,bi
        while i<aj and j<bj:
            match=None
            for a_count in range(1,min(3,aj-i)+1):
                for b_count in range(1,min(3,bj-j)+1):
                    if ''.join(wanted[i:i+a_count])==''.join(h[0] for h in heard[j:j+b_count]):
                        match=(a_count,b_count);break
                if match: break
            if not match: break
            a_count,b_count=match
            for k in range(a_count): mapping[i+k]=(wanted[i+k],heard[j][1],heard[j+b_count-1][2])
            merged.append({'script_indices':list(range(i,i+a_count)),'script_words':wanted[i:i+a_count],'heard_tokens':[h[0] for h in heard[j:j+b_count]],'start':heard[j][1],'end':heard[j+b_count-1][2],'precision':'shared measured ASR token interval'})
            i+=a_count;j+=b_count
    coverage=len(mapping)/len(wanted)
    if coverage < .90: raise ValueError(f'alignment coverage {coverage:.1%} below 90%; revise or inspect speech')
    spans=[]; offset=0
    for b in plan['beats']:
        count=len(tokens(b['narration']))
        if offset not in mapping: raise ValueError('unmatched beat-start word: '+b['id'])
        cues=[]
        for a in b['actions']:
            i=offset+cue_index(b['narration'],a['cue'])
            if i not in mapping: raise ValueError('unmatched action cue: '+a['cue'])
            cues.append({'action':a,'time':round(mapping[i][1],3),'script_word_index':i,'heard_word':mapping[i][0]})
        spans.append({'id':b['id'],'start':round(mapping[offset][1],3),'actions':cues})
        offset+=count
    return spans,{'coverage':coverage,'merged_token_groups':merged,'script_words':wanted,'matched_script_indices':sorted(mapping),'beat_anchors':spans}


def compile_plan(project, plan, words, voice_duration, duration_range):
    spans,alignment=align(plan,words)
    events=[]; initial=[]; actions=[]; sfx=[]; label_timing=[]
    def init(id_,**props): initial.append({'target':'#'+id_,'props':props})
    def emit(t,id_,action,**params): events.append({'time':round(t,3),'target':'#'+id_,'action':action,'params':params})
    def pop(t,id_,dur=.32): emit(t,id_,'FROM_TO',**{'from':{'opacity':0,'scale':.92},'to':{'opacity':1,'scale':1},'duration':dur,'ease':'power3.out'})
    def hide(t,id_,dur=.25): emit(t,id_,'TWEEN',to={'opacity':0},duration=dur)
    def pose(t,result):
        prefixes=['bot'] if plan['environment']=='calendar' else ['pair-bot','close-A-bot','close-B-bot','review-bot']
        for prefix in prefixes:
            for face in ('thinking','pointing','presenting','happy'): emit(t,prefix+'-'+face,'SET',props={'opacity':int(face==result)})
    if plan['environment']=='calendar':
        for id_ in ('proposed','committed','opening','decision','decision-result','finger'): init(id_,opacity=0)
        init('world-camera',scale=1)
        pop(.18,'opening'); bot_prefixes=['bot']
    else:
        bot_prefixes=['pair-bot','close-A-bot','close-B-bot','review-bot']
        for shot in ('arena-pair','arena-a','arena-b','arena-review'): init('shot-'+shot,opacity=0)
        init('receiver',opacity=0); init('winner',opacity=0)
        for prefix in ('pair-A','pair-B','close-A','close-B','review-A','review-B'):
            for part in ('stencil','pass','fail','pass-mark','fail-mark'): init(prefix+'-'+part,opacity=0)
    for prefix in bot_prefixes:
        for face in ('thinking','pointing','presenting','happy'): init(prefix+'-'+face,opacity=int(face=='thinking'))
    previous_shot=None
    for i,(beat,span) in enumerate(zip(plan['beats'],spans,strict=True)):
        start=span['start']; end=spans[i+1]['start'] if i+1<len(spans) else voice_duration+1.2
        init('caption-'+str(i),opacity=0); emit(start,'caption-'+str(i),'CAPTION_REPLACE')
        if beat['headline']:
            init('headline-'+str(i),opacity=0)
            for j in range(i):
                if plan['beats'][j]['headline']: emit(start,'headline-'+str(j),'SET',props={'opacity':0})
            # Headline reveal is scheduled after this beat's physical evidence below.
        if plan['environment']=='calendar':
            emit(start,'world-camera','TWEEN',to={'scale':1.08 if beat['shot']=='calendar-detail' else 1},duration=.4)
        elif beat['shot']!=previous_shot:
            if previous_shot: emit(start,'shot-'+previous_shot,'SCENE_CUT',hide='#shot-'+previous_shot,show='#shot-'+beat['shot'])
            else: emit(0,'shot-'+beat['shot'],'SET',props={'opacity':1})
        previous_shot=beat['shot']
        for entry in span['actions']:
            a=entry['action']; t=entry['time']; kind=a['kind']; complete=t
            if kind=='bot.pose':
                pose(t,a['result'])
                actions.append({'beat':beat['id'],'kind':kind,'subject':a['subject'],'cue':a['cue'],'cue_time':t,'complete':t,'result':a['result'],'requires':a['requires']})
                continue
            if kind=='calendar.propose':
                emit(t,'proposed','FROM_TO',**{'from':{'opacity':0,'y':-110},'to':{'opacity':1,'y':0},'duration':.55})
                complete=t+.55; sfx.append((t,'pop'))
            elif kind in ('calendar.approve','calendar.decline'):
                approach=max(start,t-.55); pop(approach,'decision',.25)
                emit(approach,'finger','FROM_TO',**{'from':{'x':350,'opacity':0},'to':{'x':0,'opacity':1},'duration':t-approach or .01})
                emit(t,'finger','TWEEN',to={'y':35},duration=.18)
                emit(t,'decision','TWEEN',to={'y':12,'scale':.96},duration=.18)
                pop(t+.23,'decision-result',.16)
                emit(t+.36,'finger','TWEEN',to={'x':350,'opacity':0},duration=.42)
                emit(t+.36,'decision','TWEEN',to={'y':0,'scale':1},duration=.3)
                if kind=='calendar.decline': hide(t+.78,'proposed',.35); hide(t+.78,'opening',.35)
                complete=t+1.13 if kind.endswith('decline') else t+.78
                sfx.append((t+.18,'click-soft'))
            elif kind=='calendar.commit':
                hide(t,'proposed',.25); pop(t+.32,'committed',.5); complete=t+.82; sfx.append((t+.32,'pop'))
            elif kind=='arena.check':
                candidate=a['subject']; result=a['result']
                prefixes=['pair-'+candidate,'close-'+candidate,'review-'+candidate]
                for prefix in prefixes:
                    emit(t,prefix+'-stencil','FROM_TO',**{'from':{'y':-150,'opacity':0},'to':{'y':0,'opacity':1},'duration':.38})
                    pop(t+.40,prefix+'-'+result,.25)
                    pop(t+.94,prefix+'-'+result+'-mark',.2)
                complete=t+1.14; sfx.append((t+.94,'click-soft'))
            elif kind=='arena.select':
                pop(t,'winner'); complete=t+.32; sfx.append((t,'pop'))
            elif kind=='arena.handoff':
                pop(max(start,t-.4),'receiver',.35)
                emit(t,'review-A','TWEEN',to={'x':370,'y':225,'rotation':-6},duration=.75)
                emit(t,'review-B','TWEEN',to={'x':80,'y':225,'rotation':6},duration=.75)
                emit(t+.8,'receiver','TWEEN',to={'x':-30},duration=.2)
                complete=t+1; sfx.append((t,'whoosh-short'))
            if complete>end-.08: raise ValueError(f"duration conflict: {beat['id']} {kind} completes {complete:.2f} after next beat {end:.2f}; place cue earlier or revise narration")
            actions.append({'beat':beat['id'],'kind':kind,'subject':a['subject'],'cue':a['cue'],'cue_time':t,'complete':round(complete,3),'result':a['result'],'requires':a['requires']})
        evidence=[a['complete'] for a in actions if a['beat']==beat['id'] and a['kind']!='bot.pose']
        headline_time=round(max(evidence)+.12,3) if evidence else start
        if beat['headline']:
            if headline_time+.25 > end: raise ValueError('headline lacks evidence dwell: '+beat['id'])
            pop(headline_time,'headline-'+str(i),.25)
        label_timing.append({'beat':beat['id'],'caption':beat['caption'],'caption_start':start,'beat_end':end,'shot':beat['shot'],'headline':beat['headline'],'headline_start':headline_time if beat['headline'] else None})
    duration=round(max(voice_duration+1.2,max(a['complete'] for a in actions)+.8),2)
    if not duration_range[0]<=duration<=duration_range[1]: raise ValueError(f'duration conflict: actual {duration}s outside intended range {duration_range}; plan must be revised, not speech rushed')
    spec={'schemaVersion':'1.0','compositionId':'main','fps':30,'durationSec':duration,'initial':initial,'events':sorted(events,key=lambda e:e['time']), 'captions':[{'text':b['caption'],'start':s['start'],'end':spans[i+1]['start'] if i+1<len(spans) else voice_duration} for i,(b,s) in enumerate(zip(plan['beats'],spans))]}
    media=[{'id':'narration','file':'assets/voice/narration-af-nova.wav','start':0,'duration':voice_duration,'volume':1,'lane':0,'group':'voice'}]
    for i,(start,name) in enumerate(sfx):
        media.append({'id':'sfx-'+str(i),'file':f'assets/sfx/{name}.mp3','start':round(start,3),'duration':round(min(.7,duration-start,float(probe(ROOT/f'videos/motif-calendar-reel/assets/sfx/{name}.mp3')['format']['duration'])),3),'volume':.16 if name=='whoosh-short' else .20,'lane':1,'group':'effects'})
    for name,value in [('scene-events.json',spec),('alignment-review.json',alignment),('action-trace.json',actions),('audio-plan.json',{'tracks':media}),('label-timing.json',label_timing)]: (project/name).write_text(json.dumps(value,indent=2)+'\n')
    world=calendar_world(plan) if plan['environment']=='calendar' else arena_world(plan)
    captions=''.join(sign('caption-'+str(i),b['caption'],True) for i,b in enumerate(plan['beats']))
    headlines=''.join(sign('headline-'+str(i),b['headline']) for i,b in enumerate(plan['beats']) if b['headline'])
    audio='\n'.join(f'<audio id="{m["id"]}" src="{m["file"]}" data-start="{m["start"]}" data-duration="{m["duration"]}" data-volume="{m["volume"]}" data-track-index="{m["lane"]}" data-audio-group="{m["group"]}"></audio>' for m in media)
    literal=json.dumps(spec,separators=(',',':')).replace('</','<\\/')
    html=f'''<!doctype html><html lang="en" data-resolution="portrait"><head><meta charset="UTF-8"><title>{escape(plan['message'])}</title>
<script src="assets/gsap.min.js"></script><script src="assets/motion-primitives.js"></script><script src="assets/motion-engine.js"></script>
<style>@font-face{{font-family:MotifSans;src:url('assets/MotifSans.ttf')}}
*{{box-sizing:border-box}}html,body{{margin:0;width:1080px;height:1920px;overflow:hidden;background:#B99476}}#root{{width:100%;height:100%}}#scene{{width:1080px;height:1920px;display:block;overflow:hidden}}
.motion-asset,.bot-pose,.paper-type{{transform-box:fill-box;transform-origin:center}}#world-camera{{transform-box:view-box;transform-origin:540px 900px}}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{duration}" data-width="1080" data-height="1920">
<svg id="scene" class="clip" data-start="0" data-duration="{duration}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1920" aria-label="{escape(plan['message'])}"><defs>{DEFS}{BOT_DEFS}</defs>{world}{headlines}{captions}</svg>{audio}</div>
<script id="motif-scene-events" type="application/json">{literal}</script><script>window.__timelines = window.__timelines || {{}}; window.MotifEventEngine.compile(JSON.parse(document.getElementById('motif-scene-events').textContent),'main');</script></body></html>'''
    (project/'index.html').write_text(html)
    return duration
