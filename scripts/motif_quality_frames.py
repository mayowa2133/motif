"""Explicit quality context for existing pure UI frames; no runtime discovery.

ContextVar scopes build-time calls, resets even on error and has no seek history.
Only registered standalone props may react. Screen, token, keyboard and pointer
contacts stay in authored coordinates until those components expose anchors.
"""
from contextvars import ContextVar
import math
from motif_performance import channels,render
from motif_reaction import matrix,compose,reaction
CURRENT=ContextVar('motif_frame_quality',default=None)
UI_REACTIONS={'bot','plant','mug','lamp','clock'}
def response(q,id_,position,t):
    r=q['reaction_radius'];targets=[v for v in r['targets'] if v['id']==id_]
    if len(targets)>1:raise ValueError('duplicate local reaction target: '+id_)
    if not targets:return {'x':0.,'y':0.,'rotation':0.}
    target=targets[0]
    return reaction(t-q.get('_cue_time',0),r['origin'],position,r['radius'],target['relevance'],target['amplitude'],r['duration'],target['delay'])

def prop(id_,body,x,y,f):
    ctx=CURRENT.get()
    if ctx is None:return body
    ctx['used'].add(id_);v=response(ctx['quality'],id_,(x,y),f/30)
    # Rotate around the component's real origin, OUTSIDE its primary placement.
    return f'<g data-quality-reaction="{id_}" transform="translate({v["x"]} {v["y"]}) translate({x} {y}) rotate({v["rotation"]}) translate({-x} {-y})">{body}</g>'

def puppet(x,y,f,s,angle,contact,stretch=1,impact=0):
    ctx=CURRENT.get()
    if ctx is None:return None
    q=ctx['quality'];state=q['performance']['state']
    if state=='absent':return ''
    if q['performance']['target']!='bot':raise ValueError('interactive UI performance target must be bot')
    ctx['used'].add('bot');t=f/30;age=max(0,t-q.get('_cue_time',0));c=channels(state,age)
    # Existing impact/feet placement remains the primary choreography.
    squash=1-.18*impact
    main=compose(compose(matrix(x,y,angle,s/math.sqrt(squash),s*stretch*math.sqrt(squash)),matrix(-512,-861)),matrix())
    v=response(q,'bot',(x,y),t)
    local=compose(compose(matrix(x+v['x'],y+v['y'],v['rotation']),matrix(-x,-y)),main)
    pose=compose(compose(matrix(512,904,c['angle'],1/math.sqrt(c['sy']),math.sqrt(c['sy'])),matrix(-512,-904)),matrix())
    total=compose(local,pose)
    bindings={'r':{'prop_transform':matrix(),'anchor':contact,'puppet_transform':total}} if contact else {}
    body=render(state,age,bindings)
    if contact:ctx['contacts'].append({'frame':f,'side':'r','endpoint':contact,'puppet_transform':total})
    a,b,c_,d,e,h=local
    return f'<g data-quality-bot="bot" transform="matrix({a} {b} {c_} {d} {e} {h})">{body}</g>'

def ui_frame(renderer,number,f,headline,seed,q,transition=False):
    ctx={'quality':q,'frame':f,'used':set(),'contacts':[]};targets={v['id'] for v in q['reaction_radius']['targets']}
    if targets-UI_REACTIONS:raise ValueError('unsafe or unregistered UI reaction targets (anchors unavailable): '+str(sorted(targets-UI_REACTIONS)))
    if q['performance']['state']=='absent' and 'bot' in targets:raise ValueError('absent Bot cannot react')
    token=CURRENT.set(ctx)
    try:body=renderer(number,f,headline,seed,transition)
    finally:CURRENT.reset(token)
    if targets-ctx['used']:raise ValueError('selected UI reaction target not present in this recipe: '+str(sorted(targets-ctx['used'])))
    if q['performance']['state']!='absent' and 'bot' not in ctx['used']:raise ValueError('UI recipe has no registered Bot')
    return body,ctx['contacts']
