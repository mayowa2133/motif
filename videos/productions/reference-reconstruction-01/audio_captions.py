"""Measured local narration and scoped serif paper captions; no source audio."""
from pathlib import Path
from html import escape
import json,subprocess,hashlib
P=Path(__file__).resolve().parent
D=164/30
segments=[('wash',0,1.25),('terminal',50/30,1.5),('scanner',88/30,1.15)]
tracks=[];words=[]
for name,start,speed in segments:
    f=P/'assets/voice'/f'{name}.wav'
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-of','json',str(f)]))
    length=float(probe['format']['duration'])
    tracks.append({'src':str(f.relative_to(P)),'start':start,'duration':length,'volume':1,'kind':'voice','voice':'af_nova','speed':speed})
    for w in json.loads((P/'assets/voice'/name/'transcript.json').read_text()):
        words.append({**w,'id':f'{name}-{w["id"]}','start':round(start+w['start'],6),'end':round(start+w['end'],6)})
for i,(name,start,gain) in enumerate([('whoosh-short',.40,.12),('pop',.63,.16),('click-soft',50/30+.87,.28),('pop',88/30+.93,.13),('pop',88/30+1.63,.13),('pop',88/30+2.16,.13)]):
    f=P/'assets/sfx'/f'{name}.mp3'
    dur=float(json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-of','json',str(f)]))['format']['duration'])
    tracks.append({'src':str(f.relative_to(P)),'start':start,'duration':round(min(dur,D-start),6),'volume':gain,'kind':'sfx'})
(P/'audio-plan.json').write_text(json.dumps({'tracks':tracks,'sourceAudioUsed':False,'music':None},indent=2)+'\n')
(P/'assets/voice/aligned-words.json').write_text(json.dumps(words,indent=2)+'\n')
groups=[(['Clean'],words[0]['start']),(['Clean','your'],words[1]['start']),(['instructions'],words[2]['start']),(['Run'],words[3]['start']),(['Run','prompt'],words[4]['start']),(['Run','prompt','audit'],words[5]['start']),(['Scan'],words[6]['start']),(['Scan','your'],words[7]['start']),(['Scan','your','file'],words[8]['start']),(['for'],words[9]['start']),(['for','three'],words[10]['start']),(['for','three','problems'],words[11]['start'])]
body='';initial=[];events=[]
for i,(phrase,start) in enumerate(groups):
    markup='';x=72
    for n,word in enumerate(phrase):
        width=max(122,len(word)*32+35)
        path=f'M{x} 1492L{x+width-3} 1489L{x+width} 1584L{x+2} 1581Z'
        markup+=f'<path d="{path}" transform="translate(4 7)" fill="#1B2628" opacity=".24"/><path d="{path}" fill="#B5573B"/>'
        markup+=f'<text x="{x+width/2}" y="1562" text-anchor="middle" fill="#FFF0D9" font-family="EB Garamond" font-size="72" font-weight="700">{escape(word)}</text>'
        x+=width+13
    body+=f'<g id="caption-{i}" class="caption-card" data-layout-allow-caption-zone>{markup}</g>'
    initial.append({'target':f'#caption-{i}','props':{'opacity':0}})
    events.append({'time':start,'target':f'#caption-{i}','action':'CAPTION_REPLACE','params':{}})
for t in (50/30,88/30,D-.05):
    for i in range(len(groups)):
        events.append({'time':round(t,6),'target':f'#caption-{i}','action':'SET','params':{'props':{'opacity':0}}})
spec={'schemaVersion':'1.0','compositionId':'caption-track','durationSec':D,'initial':initial,'events':sorted(events,key=lambda x:x['time'])}
(P/'caption-events.json').write_text(json.dumps(spec,indent=2)+'\n')
(P/'compositions/captions.html').write_text(f'<template><style>#captions-root{{position:absolute;inset:0;width:100%;height:100%;pointer-events:none}}</style><div id="captions-root" data-composition-id="caption-track" data-width="1080" data-height="1920" data-duration="{D}"><svg width="100%" height="100%" viewBox="0 0 1080 1920">{body}</svg></div><script>window.MotifEventEngine.compile({json.dumps(spec)},"caption-track");</script></template>')
old=json.loads((P.parents[0]/'little-book-workshop-staging/audio-source-license-manifest.json').read_text())
old['narration'].update({'provider':'local Kokoro ONNX through HyperFrames 0.8.99','voice':'af_nova','speed':'per-segment: 1.25 / 1.5 / 1.15','status':'original brief-length narration; not a cloned voice or source soundtrack','script':['Clean your instructions.','Run prompt audit.','Scan your file for three problems.']})
for key in ('rawFile','rawSha256','scriptFile','alignmentFile'):old['narration'].pop(key,None)
old['narration']['segments']=[{**t,'sha256':hashlib.sha256((P/t['src']).read_bytes()).hexdigest()} for t in tracks if t['kind']=='voice']
old['music']={'included':False,'reason':'No suitable cleared reference-like music in the reused kit; no new provider integration.'}
old['sourceSoundtrack']={'included':False,'comparison':'reference side muted; reconstruction audio only'}
(P/'audio-source-license-manifest.json').write_text(json.dumps(old,indent=2)+'\n')
print('Three measured narration segments and 12 synchronized caption chunks')
