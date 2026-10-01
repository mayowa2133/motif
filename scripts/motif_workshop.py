"""Bounded book-workshop vocabulary on the unchanged Motif event engine.

Geometry and interaction choreography are agent-authored, not model-generated
code. A live plan chooses this world, actions, language, cues and camera fits.
"""
import re
import xml.etree.ElementTree as ET
from build_motif_bot import assemble_pose
from build_workshop_kit import STRAIGHT

WORKSHOP_BOUNDS = {
 'workshop.project': ((405,925,270,315),(40,755,970,640)),
 'workshop.jobs': ((100,785,880,565),(40,755,970,640)),
 'workshop.assembly': ((380,940,320,360),(115,775,850,620)),
 'workshop.delivery': ((370,1080,350,415),(100,770,880,770)),
}

def local_part(root,assets,asset,part,prefix=''):
    node=ET.parse(root/assets[asset]).getroot()
    node=next(n for n in node.iter() if n.attrib.get('id')==part)
    for n in node.iter():
        n.tag=n.tag.split('}')[-1]
        if 'id' in n.attrib:n.attrib['id']=prefix+n.attrib['id']
    node.attrib.pop('transform',None)
    # Inner IDs are stable finite interaction bindings, never model selectors.
    return ''.join(ET.tostring(n,encoding='unicode') for n in node)

def world(root,assets,fragment,layer):
    body=fragment('workshop-wall')
    # The floor and furniture share the camera. Ground does not detach from
    # moving table feet. Extend only the existing floor's matte fill/grain
    # outside its viewBox to cover the portrait canvas during reframing.
    props='<path d="M-2000 1408 H4000 V5000 H-2000 Z" fill="#9B7764"/><path d="M-2000 1408 H4000 V5000 H-2000 Z" fill="url(#woodFiber)"/>'
    floor=ET.fromstring('<svg>'+fragment('workshop-floor')+'</svg>')
    # Reuse the floor's support shadow; its finite viewBox edge is not a new
    # room boundary. The extended plane uses its unchanged color/wood grain.
    props+=layer('workshop-floor',''.join(ET.tostring(n,encoding='unicode') for n in floor if n.tag=='ellipse'),0,1408)
    for i,x in enumerate((30,335,640)):
        _,pieces=assemble_pose('carrying-object','determined',{'l':(417,800,'grip'),'r':(605,800,'grip')})
        for side in ('left','right'):
            arm=ET.fromstring(pieces[side+'-arm'])
            for j,n in enumerate(arm.findall('path')):n.set('id',f'{side}-arm-line-{j}')
            pieces[side+'-arm']=ET.tostring(arm,encoding='unicode')
        base=''.join(pieces[k] for k in ('left-leg','right-leg','left-foot','right-foot','left-arm','right-arm','body'))
        # Keep the locked full head including antennae. Extract from assembled
        # canonical pose rather than draw a workshop variant.
        whole,_=assemble_pose('carrying-object','determined',{'l':(417,800,'grip'),'r':(605,800,'grip')})
        tree=ET.fromstring('<svg>'+whole+'</svg>')
        canonical=ET.tostring(next(n for n in tree.iter() if n.attrib.get('id')=='head'),encoding='unicode')
        base+=canonical
        base=re.sub(r'id="([^"]+)"',lambda m:f'id="worker-{i}-{m[1]}"',base)
        props+=layer('worker-'+str(i),base,x,740,.4)
        if i==1:carrier=base.replace('worker-1-','carrier-')
    props+=layer('workshop-desk',fragment('desk'),50,1010,1.04)
    props+=layer('carrier-bot',carrier,335,740,.4)
    for asset,part,id_,x,y,s in [('assembly-cradle','cradle','join-cradle',540,1230,.83)]:
        props+=layer(id_,local_part(root,assets,asset,part),x,y,s)
    # One common parent moves the SAME assembled constituents into the receiver.
    props+='<g id="book-carrier" data-layout-allow-overflow>'
    for part in ('pages','cover','binding'):
        props+=f'<g id="job-{part}" data-layout-allow-overflow>'+local_part(root,assets,'project-folio-kit',part)+'</g>'
    props+='</g>'
    # Tool contact plates must occlude the piece they press, not disappear
    # behind it; both tools remain independent reusable layers.
    props+=layer('crease-jig',local_part(root,assets,'hinged-crease-jig','jig'),235,1130,.72)
    props+=layer('page-press',local_part(root,assets,'tabletop-page-press','press'),540,1020,.72)
    for i,x in enumerate((30,335,640)):
        _,pieces=assemble_pose('carrying-object','determined',{'l':(417,800,'grip'),'r':(605,800,'grip')})
        for side in ('left','right'):
            hands=re.sub(r'id="([^"]+)"',lambda m:f'id="worker-{i}-{m[1]}"',pieces[side+'-hand'])
            props+=layer(f'grip-{i}-{side}',hands,x,740,.4)
    props+=layer('receiving-hands',local_part(root,assets,'receiving-hands','hands'),540,1295,.8)
    return body+f'<g id="workshop-camera" class="focus-camera" data-layout-allow-overflow>{props}</g>'

def initialize(init):
    init('workshop-camera',x=0,y=0,scale=1,svgOrigin='0 0')
    init('book-carrier',x=0,y=0,svgOrigin='540 1090')
    for name in ('pages','cover','binding'):init('job-'+name,x=540,y=1050,scale=.74,svgOrigin='0 0')
    init('cover-flap',svgOrigin='-97 0',scaleX=1)
    init('page-0',rotation=-7,x=-12);init('page-1',rotation=6,x=10)
    init('jig-leaf',svgOrigin='0 0')
    init('receiving-hands',opacity=0)
    init('carrier-bot',opacity=0)
    init('join-cradle',opacity=0)
    init('page-press',opacity=0);init('crease-jig',opacity=0)

def perform(kind,t,end,emit,sfx):
    caps={'workshop.dispatch':2.5,'workshop.work_parallel':5.8,'workshop.assemble':3.3,'workshop.deliver':3.2}
    mins={'workshop.dispatch':1.7,'workshop.work_parallel':3.2,'workshop.assemble':2.2,'workshop.deliver':2.3}
    duration=min(caps[kind],end-t-.18)
    if duration<mins[kind]:raise ValueError(f'{kind} needs {mins[kind]} seconds after its cue; available {duration:.2f}')
    def tween(f,id_,to,span,ease='power2.inOut'):
        emit(t+f*duration,id_,'TWEEN',to=to,duration=span*duration,ease=ease)
        if id_.startswith('grip-') and not (kind=='workshop.deliver' and id_.startswith('grip-1-')):
            _,worker,side=id_.split('-');dx=to.get('x',0);dy=to.get('y',0)
            if kind=='workshop.assemble':dx-=300 if worker=='0' else -300 if worker=='2' else 0
            sx=396 if side=='left' else 628;ex=(417 if side=='left' else 605)+dx;ey=800+dy
            d=f'M{sx} 554 Q{(sx+ex)/2:.1f} {(554+ey)/2-12:.1f} {ex:.1f} {ey:.1f}'
            for j in range(3):emit(t+f*duration,f'worker-{worker}-{side}-arm-line-{j}','TWEEN',to={'attr':{'d':d}},duration=span*duration,ease=ease)
    def set_(f,id_,**props):emit(t+f*duration,id_,'SET',props=props)
    detail={'duration':round(duration,3),'constituent_ids':['job-cover','job-pages','job-binding'],'identity_policy':'same DOM constituents through all phases'}
    if kind=='workshop.dispatch':
        # Leading Bot takes the folio tab; a short pull unfolds then spreads.
        tween(0,'grip-1-right',{'y':-28,'x':-35},.16)
        tween(.16,'cover-flap',{'scaleX':-.72},.29)
        tween(.43,'job-cover',{'x':235,'y':1050,'rotation':-5},.48)
        tween(.43,'job-binding',{'x':940,'y':1050,'rotation':10},.48)
        tween(.60,'crease-jig',{'opacity':1},.2)
        tween(.60,'page-press',{'opacity':1},.2)
        tween(.63,'grip-1-right',{'y':0,'x':0},.28)
        sfx.append((t+.43*duration,'whoosh-short'))
    elif kind=='workshop.work_parallel':
        # Sustained common work window. Cover folds under worker grip; the two
        # press mittens depress the plate; binding is unrolled and carried in.
        tween(0,'grip-0-left',{'y':22,'x':-30},.18)
        tween(.18,'jig-leaf',{'rotation':-54},.27)
        tween(.18,'cover-flap',{'scaleX':1},.30)
        tween(.18,'grip-0-left',{'x':30,'y':16},.30)
        tween(.50,'jig-leaf',{'rotation':0},.22)
        tween(.66,'grip-0-left',{'x':0,'y':0},.24)
        tween(.08,'press-plate',{'y':55},.32)
        for side in ('left','right'):tween(.08,'grip-1-'+side,{'y':38},.32)
        for id_ in ('page-0','page-1'):tween(.20,id_,{'x':0,'rotation':0},.26)
        tween(.54,'press-plate',{'y':-18},.24)
        for side in ('left','right'):tween(.54,'grip-1-'+side,{'y':0},.24)
        tween(.05,'binding-shape',{'attr':{'d':STRAIGHT}},.45)
        tween(.05,'binding-grain',{'attr':{'d':STRAIGHT}},.45)
        tween(.05,'job-binding',{'x':870,'y':1060,'rotation':0},.45)
        tween(.05,'grip-2-left',{'y':12,'x':-16},.45)
        tween(.05,'grip-2-right',{'y':12,'x':-16},.45)
        tween(.58,'job-binding',{'x':735,'y':1110,'rotation':-8},.34)
        tween(.58,'grip-2-left',{'x':-347,'y':58},.34)
        tween(.58,'grip-2-right',{'x':-16,'y':0},.34)
        tween(.78,'job-cover',{'rotation':0},.14)
        detail['simultaneous_job_windows']={
          'fold-cover':[round(t+.18*duration,3),round(t+.48*duration,3)],
          'press-pages':[round(t+.08*duration,3),round(t+.46*duration,3)],
          'unroll-binding':[round(t+.05*duration,3),round(t+.5*duration,3)]}
        detail['three_way_overlap_seconds']=round(.28*duration,3)
        sfx.append((t+.4*duration,'click-soft'))
    elif kind=='workshop.assemble':
        tween(0,'page-press',{'opacity':0},.15)
        tween(0,'join-cradle',{'opacity':1},.15)
        tween(0,'cover-flap',{'scaleX':.06},.24)
        tween(.12,'job-cover',{'x':540,'y':1090,'rotation':0},.40)
        tween(.22,'job-pages',{'x':545,'y':1090},.34)
        tween(.45,'job-binding',{'x':540,'y':1090,'rotation':0},.30)
        tween(.58,'cover-flap',{'scaleX':1},.21)
        # Three Bots contribute to the final joining press rather than react.
        tween(.25,'worker-0',{'x':300},.3);tween(.25,'worker-2',{'x':-300},.3)
        tween(.25,'grip-0-left',{'x':300,'y':0},.3);tween(.25,'grip-2-right',{'x':-300,'y':0},.3)
        tween(.25,'grip-0-right',{'x':505,'y':34},.3)
        tween(.25,'grip-2-left',{'x':-505,'y':34},.3)
        for side in ('left','right'):tween(.75,'grip-1-'+side,{'y':46},.09)
        tween(.75,'book-carrier',{'y':8},.09)
        tween(.87,'book-carrier',{'y':0},.1)
        for side in ('left','right'):tween(.87,'grip-1-'+side,{'y':0},.1)
        sfx.append((t+.84*duration,'click-soft'))
    elif kind=='workshop.deliver':
        set_(0,'worker-1',opacity=0);set_(0,'carrier-bot',opacity=1)
        tween(0,'carrier-bot',{'y':462.5},.5)
        tween(0,'receiving-hands',{'opacity':1,'y':0},.25)
        # Carrier's mittens move with the book until the receiver takes it;
        # the Bot releases while the receiving hands and book leave together.
        for side in ('left','right'):tween(0,'grip-1-'+side,{'y':462.5},.5)
        tween(0,'book-carrier',{'y':185,'scale':1.10},.5)
        for i in (0,2):
            tween(0,'worker-'+str(i),{'x':0},.34)
            for side in ('left','right'):tween(0,f'grip-{i}-{side}',{'x':0,'y':0},.34)
        for side,dx in [('left',-60),('right',60)]:
            tween(.54,'grip-1-'+side,{'y':437.5,'x':dx},.25)
            sx=396 if side=='left' else 628;ex=(417 if side=='left' else 605)+dx;ey=775
            d=f'M{sx} 554 Q{(sx+ex)/2:.1f} {(554+ey)/2-12:.1f} {ex:.1f} {ey:.1f}'
            for j in range(3):tween(.54,f'carrier-{side}-arm-line-{j}',{'attr':{'d':d}},.25)
        tween(.65,'book-carrier',{'y':270},.30)
        tween(.65,'receiving-hands',{'y':85},.30)
        sfx.append((t+.51*duration,'pop'))
    return t+duration,detail
