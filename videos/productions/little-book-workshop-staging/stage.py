"""One scoped staging pass. Reuses accepted pieces, events and soundtrack.

No live replan, new art, new interaction vocabulary, or shared-engine changes.
"""
import copy
import json
import re
import shutil
from pathlib import Path
import xml.etree.ElementTree as ET

HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'little-book-workshop-final'
NS='http://www.w3.org/2000/svg'
ET.register_namespace('',NS)
def tag(name):return '{'+NS+'}'+name

def build():
    html=(SOURCE/'index.html').read_text()
    spec=json.loads((SOURCE/'scene-events.json').read_text())
    svg_match=re.search(r'<svg id="scene".*?</svg>',html,re.S)
    svg=ET.fromstring(svg_match.group().replace(' data-layout-allow-overflow',' data-layout-allow-overflow="true"'))
    ids={n.get('id'):n for n in svg.iter() if n.get('id')}
    camera=ids['workshop-camera']
    parents={child:parent for parent in svg.iter() for child in parent}
    defs=svg.find(tag('defs'))
    bindings=[
      ('cover',['worker-0','grip-0-left','grip-0-right','crease-jig','job-cover'],(-8.75,-582.5,1.25)),
      ('pages',['worker-1','grip-1-left','grip-1-right','page-press','job-pages'],(120,-582.5,1.25)),
      ('binding',['worker-2','grip-2-left','grip-2-right','job-binding'],(-558.5,-135,1.3)),
    ]
    wrappers=[]
    def wrap(node,id_):
        parent=parents[node];index=list(parent).index(node)
        outer=ET.Element(tag('g'),{'id':id_,'data-layout-allow-overflow':'true'})
        parent.remove(node);outer.append(node);parent.insert(index,outer)
        return id_
    # Cut three tabletop segments from the existing desk; no new prop shapes.
    original_table=parents[ids['workshop-desk']]
    for i,(name,elements,matrix) in enumerate(bindings):
        clip_id='station-table-crop-'+str(i)
        clip=ET.SubElement(defs,tag('clipPath'),{'id':clip_id})
        ET.SubElement(clip,tag('rect'),{'x':str(70+305*i),'y':'1070','width':'320','height':'135'})
        table=copy.deepcopy(original_table)
        for n in table.iter():
            if n.get('id'):n.set('id','station-'+str(i)+'-'+n.get('id'))
        crop=ET.Element(tag('g'),{'clip-path':'url(#'+clip_id+')'})
        crop.append(table)
        table_wrapper=ET.Element(tag('g'),{'id':'stage-table-'+str(i),'data-layout-allow-overflow':'true'})
        table_wrapper.append(crop);camera.insert(0,table_wrapper)
        spec['initial'].append({'target':'#stage-table-'+str(i),'props':{'opacity':0,'svgOrigin':'0 0'}})
        wrappers.append(('stage-table-'+str(i),matrix))
        for id_ in elements:
            node=ids[id_] if id_.startswith('job-') else parents[ids[id_]]
            name_=wrap(node,'stage-'+id_)
            spec['initial'].append({'target':'#'+name_,'props':{'x':0,'y':0,'scale':1,'svgOrigin':'0 0'}})
            wrappers.append((name_,matrix))

    # Loose kit at frame one. The bound book has an intentionally different
    # silhouette: aligned, closed and held as a single object at the payoff.
    opening={'job-cover':{'x':485,'y':1070,'rotation':-9},
             'job-pages':{'x':620,'y':1025,'rotation':9},
             'job-binding':{'x':780,'y':1100,'rotation':-12},
             'cover-flap':{'scaleX':-.45},
             'page-0':{'rotation':-14,'x':-28},
             'page-1':{'rotation':14,'x':28},
             'worker-0':{'opacity':0},'worker-2':{'opacity':0},
             'grip-0-left':{'opacity':0},'grip-0-right':{'opacity':0},
             'grip-2-left':{'opacity':0},'grip-2-right':{'opacity':0}}
    for id_,props in opening.items():
        item=next((i for i in spec['initial'] if i['target']=='#'+id_),None)
        if item:item['props'].update(props)
        else:spec['initial'].append({'target':'#'+id_,'props':props})

    events=[]
    trace=json.loads((SOURCE/'action-trace.json').read_text())
    dispatch=trace[0];old_start=dispatch['cue_time'];dispatch_end=dispatch['complete']
    carry_time=round(trace[1]['cue_time']+.58*trace[1]['duration'],3)
    for event in spec['events']:
        e=copy.deepcopy(event)
        if e['target']=='#workshop-camera':continue
        # Start the existing opening/distribution action at .05 seconds.
        if old_start<=e['time']<=dispatch_end and e['target'] not in ('#caption-0',):
            e['time']=round(e['time']-old_start+.05,3)
        # Binding finishes its preparation in its lower station, within the
        # carrying grip, instead of traveling across a now absent long desk.
        if e['target']=='#job-binding' and abs(e['time']-carry_time)<.01:
            e['params']['to'].update(x=910,y=1060,rotation=0)
        if e['target']=='#job-binding' and e['time']<3 and 'to' in e['params']:
            e['params']['to']['rotation']=35
        if e['target']=='#grip-2-left' and abs(e['time']-carry_time)<.01:
            e['params']['to'].update(x=100,y=12)
        if e['target'].startswith('#worker-2-left-arm-line-') and abs(e['time']-carry_time)<.01:
            e['params']['to']['attr']['d']='M396 554 Q456.5 671.0 517.0 812.0'
        events.append(e)
    def emit(t,id_,action,**params):
        events.append({'time':round(t,3),'target':'#'+id_,'action':action,'params':params})
    def tween(t,id_,to,duration):emit(t,id_,'TWEEN',to=to,duration=duration,ease='power2.inOut')
    emit(0,'workshop-camera','SET',props={'x':-351,'y':-690,'scale':1.65})
    tween(1.1,'workshop-camera',{'x':0,'y':0,'scale':1},1.05)
    for id_,(x,y,s) in wrappers:
        tween(2.15,id_,{'x':x,'y':y,'scale':s},1.1)
        tween(9.58,id_,{'x':0,'y':0,'scale':1},1.5)
        if id_.startswith('stage-table-'):
            tween(2.35,id_,{'opacity':1},.35)
            tween(9.58,id_,{'opacity':0},.25)
    for i in (0,2):
        for id_ in (f'worker-{i}',f'grip-{i}-left',f'grip-{i}-right'):
            tween(2.35,id_,{'opacity':1},.3)
            tween(12.89,id_,{'opacity':0},.3)
    tween(2.2,'workshop-desk',{'opacity':0},.3)
    tween(9.58,'workshop-desk',{'opacity':1},.35)
    tween(5.63,'job-pages',{'rotation':0},1.1)
    tween(10.25,'workshop-camera',{'x':-432,'y':-885,'scale':1.8},1.1)
    tween(9.58,'crease-jig',{'opacity':0},.25)
    tween(13.05,'workshop-camera',{'x':-351,'y':-1070,'scale':1.65},.55)
    spec['events']=sorted(events,key=lambda e:e['time'])
    (HERE/'scene-events.json').write_text(json.dumps(spec,indent=2)+'\n')
    html=html[:svg_match.start()]+ET.tostring(svg,encoding='unicode')+html[svg_match.end():]
    literal=json.dumps(spec,separators=(',',':')).replace('</','<\\/')
    html=re.sub(r'(<script id="motif-scene-events" type="application/json">).*?(</script>)',lambda m:m[1]+literal+m[2],html,flags=re.S)
    (HERE/'index.html').write_text(html)
    # Four actual 360x640 renders; no diagnostic crop or enlarged screenshot.
    still=html.replace('width:1080px','width:360px').replace('height:1920px','height:640px')
    still=still.replace('data-width="1080"','data-width="360"').replace('data-height="1920"','data-height="640"')
    still=still.replace('</style>','.caption-card,.headline-card{display:none}</style>')
    (HERE/'mobile-stills').mkdir(exist_ok=True)
    (HERE/'mobile-stills/index.html').write_text(still)
    if not (HERE/'mobile-stills/assets').exists():shutil.copytree(HERE/'assets',HERE/'mobile-stills/assets')
    trace[0].update(cue_time=.05,complete=round(.05+dispatch['duration'],3),timing_note='Picture action starts earlier by explicit staging request; narration is unchanged')
    (HERE/'action-trace.json').write_text(json.dumps(trace,indent=2)+'\n')

if __name__=='__main__':build()
