"""Bounded full-reference fine cut. Canonical puppet + unchanged Motif event engine.

Only the unfinished shots are authored here. Approved [436,600) is a media clip.
No planner changes, runtime changes, dependency changes, or mascot regeneration.
"""
from pathlib import Path
from html import escape
import base64, hashlib, json, math, re, shutil, sys

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
BASE = P.parent / 'reference-reconstruction-01-finishing'
sys.path.insert(0, str(ROOT / 'scripts'))
from build_motif_bot import assemble_pose, arm, DEFS

D = 1262 / 30
INK = '#202C32'; PAPER = '#F4EBD8'; CORAL = '#B5573B'
TEAL = '#6DABA1'; YELLOW = '#D9B25B'
for folder in ['assets/props', 'assets/materials', 'assets/voice', 'assets/sfx', 'compositions', 'renders', 'review']:
    (P / folder).mkdir(parents=True, exist_ok=True)
for name in ['gsap.min.js', 'motion-engine.js', 'motion-primitives.js']:
    assert hashlib.sha256((P / 'assets' / name).read_bytes()).digest() == hashlib.sha256((BASE / 'assets' / name).read_bytes()).digest()
for name in ['paper', 'wood', 'wall', 'card']:
    dst = P / 'assets/materials' / (name + '.png')
    if not dst.exists(): shutil.copy2(BASE / 'assets/materials' / (name + '.png'), dst)
for name in ['pop.mp3', 'click-soft.mp3', 'whoosh-short.mp3']:
    shutil.copy2(BASE / 'assets/sfx' / name, P / 'assets/sfx' / name)

def save(name, value): (P / name).write_text(json.dumps(value, indent=2) + '\n')
def txt(value, x, y, size=40, color=INK, anchor='start', family='Inter', weight=700, extra=''):
    return f'<text x="{x}" y="{y}" font-family="{family}" font-weight="{weight}" font-size="{size}" fill="{color}" text-anchor="{anchor}" {extra}>{escape(value)}</text>'
def box(x,y,w,h,color=PAPER,rx=3,material=None):
    # Local quiet surfaces and small deterministic cut deviations; no global noise.
    if rx<8 and w>75 and h>60:
        k=min(2.4,min(w,h)*.015)
        path=f'M{x} {y+k}L{x+w*.32} {y}L{x+w*.67} {y+k*.6}L{x+w} {y+k*.25}L{x+w-k*.4} {y+h*.49}L{x+w} {y+h-k*.3}L{x+w*.68} {y+h}L{x+w*.34} {y+h-k*.5}L{x+k*.2} {y+h}L{x} {y+h*.53}Z'
        shape=f'<path d="{path}"'
        shadow=f'{shape} transform="translate(5 8)" fill="{INK}" opacity=".14"/>{shape} transform="translate(2 3)" fill="{INK}" opacity=".09"/>'
        face=f'{shape} fill="{color}"/>'
        texture=f'{shape} fill="url(#{material}Surface)" opacity=".30"/>' if material else ''
        return shadow+face+texture+f'<path d="M{x+k} {y+h-1}L{x+w*.34} {y+h-k*.5-1}L{x+w*.68} {y+h-1}L{x+w-k} {y+h-k*.3-1}" stroke="{INK}" stroke-width="1.2" opacity=".11"/>'
    face=f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}"'
    s=f'<rect x="{x+5}" y="{y+8}" width="{w}" height="{h}" rx="{rx}" fill="{INK}" opacity=".17"/>'+face+f' fill="{color}"/>'
    if material:s+=face+f' fill="url(#{material}Surface)" opacity=".30"/>'
    return s

def grp(id_, body, x=0, y=0, scale=1):
    return f'<g transform="translate({x} {y}) scale({scale})" data-layout-allow-overflow><g id="{id_}" class="motion-asset" data-layout-allow-overflow>{body}</g></g>'
def unique(body, prefix):
    # All canonical definitions are shared; only puppet part IDs are renamed.
    return re.sub(r'id="([^"]+)"', lambda m:f'id="{prefix}-{m[1]}"', body)
def bot(id_,x,y,scale=.30,pose='standing',face='happy',overrides=None,dynamic=False):
    body,parts=assemble_pose(pose,face,overrides or {})
    if dynamic:
        for side in ['left','right']:
            body=body.replace(parts[side+'-arm'],'').replace(parts[side+'-hand'],'')
        body+=f'<g id="{id_}-arms"></g>'
        # Dynamic-arm slot has its own unprefixed ID; canonical part IDs remain unique.
        body=unique(body,id_).replace(f'id="{id_}-{id_}-arms"',f'id="{id_}-arms"')
    else: body=unique(body,id_)
    return grp(id_,body,x,y,scale)
def held_arms(id_,x,y,scale,left,right):
    result=''
    for side,point in [('left',left),('right',right)]:
        if point:
            a,h=arm(side,(point[0]-x)/scale,(point[1]-y)/scale,'grip')
        else: a,h=arm(side,278 if side=='left' else 746,676,'mitten')
        result+=unique(a+h,id_)
    return result
def headline(value):
    path='M35 279L81 274L110 278L239 273L298 280L428 273L505 278L602 276L715 282L864 275L927 279L1043 274L1040 321L1044 342L1040 376L955 371L881 378L763 373L681 379L563 376L448 378L331 372L246 379L133 373L78 380L39 376L41 332Z'
    size=42 if len(value)>30 else 50
    return f'<path d="{path}" transform="translate(4 8)" fill="{INK}" opacity=".2"/><path d="{path}" fill="{PAPER}"/><path d="{path}" fill="url(#paperSurface)"/>'+'<path d="M31 283L54 259L112 338L87 360Z M969 332L1024 260L1052 282L996 359Z" fill="#CDBF87" opacity=".88"/>'+txt(value,540,341,size,INK,'middle',weight=900)
def world(wall,floor):
    return box(-12,-12,1104,1944,wall,0,'wall')+box(-12,1490,1104,440,floor,0,'wood')
def lines(x,y,w,count=9,gap=44,color='#A69E88',sw=11):
    return ''.join(f'<path d="M{x} {y+i*gap}H{x+w-(i%3)*35}" stroke="{color}" stroke-width="{sw}" opacity=".6"/>' for i in range(count))
def paper(w=500,h=690,title='CLAUDE.md'):
    size=min(43,(w-60)/max(1,len(title)*.64))
    return box(0,0,w,h,PAPER,4,'paper')+txt(title,30,72,size)+lines(30,133,w-65,int((h-160)/45),45)
def pill(value,x,y,w=250,color=YELLOW,size=31):
    return box(x,y,w,61,color,3,'paper')+txt(value,x+w/2,y+42,size,INK,'middle')
def cloud(x,y):
    return f'<path d="M{x} {y+40}q-35-54 20-67q40-23 67 8q65-22 93 28q18 48-43 57H{x+13}Z" fill="{PAPER}" opacity=".92"/>'

defs=DEFS.removeprefix('<defs>').removesuffix('</defs>')
for name in ['paper','wood','wall','card']:
    defs+=f'<pattern id="{name}Surface" width="2048" height="2048" patternUnits="userSpaceOnUse"><image href="assets/materials/{name}.png" width="2048" height="2048"/></pattern>'

# Minimum shot-required pieces. No speculative library expansion.
assets={}
assets['barbell']='<path d="M-465 0H465" stroke="#A6B9B6" stroke-width="24"/>'
assets['performance-gauge']='<circle r="104" fill="#E1D9BF" stroke="#425952" stroke-width="8"/><path d="M-86 0A86 86 0 0 1 86 0" fill="none" stroke="#79A474" stroke-width="19"/><path d="M0-86A86 86 0 0 1 86 0" fill="none" stroke="#C36949" stroke-width="19"/>'+txt('ANSWERS',0,53,23,INK,'middle')
for x in [-370,370]:
    assets['barbell']+=f'<circle cx="{x+8}" cy="8" r="115" fill="#17262B"/><circle cx="{x}" cy="0" r="115" fill="#263C44" stroke="#95A8A0" stroke-width="8"/><circle cx="{x}" cy="0" r="83" fill="none" stroke="#496069" stroke-width="3"/>'+txt('INSTRUCTIONS',x,7,22,PAPER,'middle')
assets['instruction-note']=box(-80,-36,160,72,YELLOW,2,'paper')+txt('ALWAYS',0,10,25,INK,'middle')
assets['shelf']=box(0,0,930,28,'#5C5144',0,'wood')+''.join(box(30+i*121,-143,92,140,'#243C46',3,'card')+txt('OLD',76+i*121,-70,21,PAPER,'middle')+txt('MODEL',76+i*121,-38,17,PAPER,'middle') for i in range(7))
assets['answer-page']=paper(615,730,'ANSWER')+box(435,570,112,107,PAPER,1)+txt('check',475,707,25)
assets['pencil']='<path d="M-6 0L9-29L27 0V-270H-6Z" fill="#DDB851"/><path d="M-6 0L9 20L27 0" fill="#E9D5AD"/><path d="M4 13L9 20L14 13" fill="#25373D"/>'
assets['race-car']=box(-180,-50,355,100,'#BF6549',32,'card')+'<path d="M-93-48L-55-118H78L133-48Z" fill="#DBBE7D"/>'
for x in [-109,112]: assets['race-car']+=f'<circle cx="{x}" cy="54" r="46" fill="#223037"/><circle cx="{x}" cy="54" r="22" fill="#B7BEB2"/>'
assets['skill-card']=paper(510,595,'prompt-audit')+pill('SOURCE: OFFICIAL SKILLS',22,434,466,TEAL,26)
assets['chalkboard']=box(0,0,820,382,'#806746',5,'wood')+box(18,18,784,343,'#2D5449',3)+txt('A+',90,100,50,PAPER)+txt('B−',660,290,48,PAPER)+txt('F',710,112,44,PAPER)
assets['megaphone']='<path d="M0 0L169-78V82L0 28Z" fill="#E2B744" stroke="#A0803B" stroke-width="5"/><path d="M24 25L32 84H58L50 15" fill="#D1A640"/><ellipse cx="169" cy="2" rx="17" ry="80" fill="#F3DEA4"/>'
assets['step']=box(0,0,164,73,TEAL,1,'paper')+txt('STEP',83,49,31,PAPER,'middle')
assets['permission-gate']=box(0,0,277,226,'#CAD5C6',20,'card')+box(14,16,249,154,'#253C38',15,'card')+pill('NO EDITS YET',24,60,228,CORAL,26)+txt('CLAUDE',139,151,29,PAPER,'middle')+'<path d="M42 223V365M237 223V365" stroke="#CAD5C6" stroke-width="18"/>'
assets['lens']='<path d="M84 82L153 164" stroke="#715330" stroke-width="34"/><circle r="135" fill="#B2D9CE" fill-opacity=".17" stroke="#263940" stroke-width="15"/><circle r="122" fill="none" stroke="#BECAB6" stroke-width="8"/>'
assets['evidence-file']=paper(620,640,'A REAL RUN')+box(65,162,490,241,'#DAB967',1,'paper')+txt('SOURCE EXAMPLE',310,273,41,INK,'middle')+txt('not an independently verified test',310,327,24,INK,'middle')
assets['test-bench']=box(0,0,800,136,'#526970',4,'card')+box(530,-105,267,105,'#C0C8C2',13,'card')+pill('RUN TEST',545,-89,236,INK,34).replace('fill="'+INK+'" text-anchor','fill="'+PAPER+'" text-anchor')
assets['target']='<path d="M-67 203L-108 373M67 203L108 373" stroke="#8E754A" stroke-width="16"/>'
for r,c in [(223,PAPER),(193,'#243C44'),(159,'#4F95AF'),(115,'#D66443'),(70,'#E3B448'),(30,CORAL)]: assets['target']+=f'<circle r="{r}" fill="{c}"/>'
assets['arrow']='<path d="M-285 0H-13" stroke="#525146" stroke-width="10"/><path d="M-24-16L5 0L-24 16" fill="#263E44"/><path d="M-280 0L-313-33H-274L-248 0L-274 33H-313Z" fill="#5EAA9D"/>'
assets['guide']=paper(460,530,'prompt-audit')+pill('COMMAND + GUIDE',24,394,410,TEAL,31)

events=[];initial=[];shots=[];interactions=[];contact_samples=[]
def init(id_,**props): initial.append({'target':'#'+id_,'props':props})
def at(t,id_,**props): events.append({'time':max(0,t),'target':'#'+id_,'action':'SET','params':{'props':props}})
def tween(t,id_,duration,ease='power2.out',**to):
    events.append({'time':t,'target':'#'+id_,'action':'TWEEN','params':{'to':to,'duration':duration,'ease':ease}})
def reveal(t,id_,duration=.18):
    init(id_,opacity=0,y=16)
    at(t,id_,opacity=1)
    tween(t,id_,duration,y=0)
def shot(id_,start,end,wall,floor,title,body):
    shots.append({'id':id_,'frames':[start,end],'duration':(end-start)/30,'headline':title,'editable':True})
    init('shot-'+id_,opacity=1 if start==0 else 0)
    if start: at(start/30-.00001,'shot-'+id_,opacity=1)
    if end<1262: at(end/30-.00001,'shot-'+id_,opacity=0)
    return grp('shot-'+id_,world(wall,floor)+body+headline(title)+box(185,65,710,66,INK,3)+txt('REFERENCE STUDY · MOTIF FINE CUT',540,110,25,PAPER,'middle'))
def contact(kind,frame,consequence,**extra): interactions.append({'kind':kind,'contactFrame':frame,'consequence':consequence,**extra})

worlds=''
# 01: grip remains exactly on the bar while weight/strain drives the gauge.
b=''
for i in range(10):
    x=i*117-18
    b+=f'<path d="M{x} 0L{x+60} 102L{x+116} 0Z" fill="{[CORAL,PAPER,INK][i%3]}"/>'
b+=pill('CLAUDE GYM',62,420,368,'#CD7252',39)+pill('OPUS 5.5',359,1430,362,YELLOW,36)
b+=grp('gym-dial',assets['performance-gauge'],833,650,1.2)
b+=grp('gym-gauge','',833,650)
# Keep the pivot in local geometry. Finite endpoint sets avoid the rough's
# global SVG pivot + fill-box transform moving the needle out of the dial.
for f in range(110):
    q=max(0,min(1,(f/30-.9)/1.7));angle=math.radians(117*(1-(1-q)**3))
    px=-89*math.cos(angle)+56*math.sin(angle);py=-89*math.sin(angle)-56*math.cos(angle)
    at(f/30,'gym-gauge',innerHTML=f'<path d="M0 0L{px:.3f} {py:.3f}" stroke="#283A3C" stroke-width="9" stroke-linecap="round"/><circle r="15" fill="#283A3C"/>')
b+=box(340,1276,389,37,'#846C50',2,'wood')+box(375,1313,321,108,'#5C5143',2,'wood')
b+=bot('gym-bot',310,860,.46,face='thinking',dynamic=True)
bar=assets['barbell']
# Instruction slips cover the weights intentionally; the underlying plate labels
# are omitted so the small stamped words remain readable.
bar=re.sub(r'<text[^>]*>INSTRUCTIONS</text>','',bar)
for i in range(6):
    x=-370 if i%2==0 else 370;y=-68+(i//2)*67
    bar+=grp('gym-note-'+str(i),assets['instruction-note'],x,y,.78)
    init('gym-note-'+str(i),opacity=0,y=-390)
    at(.65+i*.25,'gym-note-'+str(i),opacity=1)
    tween(.65+i*.25,'gym-note-'+str(i),.24,y=0,rotation=0)
b+=grp('gym-bar',bar,540,1100)
for f in range(110):
    sec=f/30
    if sec<.55: by=1100-210*math.sin(sec/.55*math.pi/2)
    elif sec<1.5: by=890+20*math.sin(sec*15)
    else: by=min(1195,890+(sec-1.5)*155)+9*math.sin(sec*26)
    if f==0: at(0,'gym-bar',y=by-1100)
    else: tween((f-1)/30,'gym-bar',1/30,ease='none',y=by-1100)
    at(sec,'gym-bot-arms',innerHTML=held_arms('gym-bot',310,860,.46,(407,by),(662,by)))
    contact_samples.append({'shot':'gym','frame':f,'grips':[[407,by],[662,by]],'barY':by})
worlds+=shot('gym',0,110,'#B99A80','#81664E','MAKE OPUS 5.5 SMARTER AND CHEAPER',b)
contact('barbell.strain',46,'attached notes add burden; bar drops while gauge enters red')

# 02: burden lands on the same archive document; physical chain beneath it.
b=grp('archive-shelf',assets['shelf'],70,624)
page=paper(593,682)
labels=[('THINK STEP','BY STEP'),('DOUBLE-CHECK','EVERYTHING'),('VERIFY','TWICE'),('OLD','MODEL'),('ALWAYS',''),('NEVER','')]
placements=[(137,250,-9),(285,310,8),(422,366,-7),(181,423,11),(331,477,-12),(427,543,7)]
for i,(label,(x,y,angle)) in enumerate(zip(labels,placements)):
    n=box(-100,-48,200,105,['#D8B263','#B7C3B9','#A894BA'][i%3],2,'paper')+txt(label[0],0,-15,20,INK,'middle')+txt(label[1],0,34,20,INK,'middle')
    id_='archive-note-'+str(i);page+=grp(id_,f'<g transform="rotate({angle})">{n}</g>',x,y)
    init(id_,y=-470,opacity=0)
    landing=110/30+.25+i*.29
    at(landing,id_,opacity=1);tween(landing,id_,.30,y=0)
    tween(landing+.29,'archive-page',.13,y=(i+1)*7)
b+=grp('archive-page',page,150,713)
b+='<path d="M256 1420q-63-53 0-79q65 49 0 79q-51 51 0 75q53-49 0-75" stroke="#6A7976" stroke-width="14" fill="none"/>'
b+=bot('archive-bot',715,1105,.31,face='thinking')
worlds+=shot('archive',110,206,'#A48C48','#5B503B','WORKAROUNDS FOR RETIRED MODELS',b)
contact('notes.burden',143,'old instruction slips land on and weigh down the file')

# 03: pencil reaches checkbox before the check appears; duplicate answer follows.
b=grp('answer-main',assets['answer-page'],290,590)
b+=bot('answer-bot',-4,1020,.35,face='thinking',dynamic=True)
b+=grp('answer-pencil',assets['pencil'],769,1178)
b+=grp('answer-check','<path d="M744 1218L768 1240L812 1179" stroke="#42825F" stroke-width="19" fill="none"/>')
b+=grp('answer-copy',assets['answer-page'],480,570,.78)
init('answer-check',opacity=0);init('answer-copy',opacity=0,x=-80,rotation=4)
for f in range(51):
    sec=f/30
    # Tip is (9,20) in pencil coordinates. World path finishes inside the box.
    px=769+min(0,(sec-.45)*350);py=1178+min(0,(sec-.45)*200)
    at(206/30+sec,'answer-pencil',x=px-769,y=py-1178)
    at(206/30+sec,'answer-bot-arms',innerHTML=held_arms('answer-bot',-4,1020,.35,None,(px+12,py-76)))
at(206/30+.50,'answer-check',opacity=1)
at(206/30+.86,'answer-copy',opacity=1);tween(206/30+.86,'answer-copy',.35,x=0,rotation=9)
worlds+=shot('answer',206,257,'#365E61','#203F41','“VERIFY TWICE BEFORE RESPONDING”',b)
contact('pencil.check',221,'tip reaches checkbox; check then duplicate sheet appears')

# 04: wheels stay on the track; burdened car travels less distance.
b=box(-5,672,1090,770,'#A55D3C',0,'card')
for y in [736,887,1038,1189,1340]: b+=f'<path d="M0 {y}H1080" stroke="{PAPER}" stroke-width="5" stroke-dasharray="75 50"/>'
b+='<path d="M755 670V1442" stroke="#DCE0CF" stroke-width="10" stroke-dasharray="12 13"/>'
for i in range(12):
    for j in range(4):b+=box(i*92,400+j*40,73,22,['#EFCB8B','#758D87',CORAL][(i+j)%3],0)
car_top=bot('race-loaded-bot',-151,-336,.30,face='thinking')+assets['race-car'].replace('#BF6549','#4F8974')
for i in range(3): car_top+=grp('race-load-'+str(i),assets['instruction-note'],-112,-230+i*59,.62)
car_top+=pill('OLD INSTRUCTIONS',-185,137,373,YELLOW,25)
car_bottom=bot('race-free-bot',-151,-336,.30)+assets['race-car']+pill('LIGHTER FILE',-185,137,373,PAPER,29)
b+=grp('race-loaded',car_top,285,875)+grp('race-free',car_bottom,285,1245)
tween(257/30+.3,'race-loaded',3.1,x=235,ease='power1.inOut')
tween(257/30+.3,'race-free',2.5,x=505,ease='power1.inOut')
b+=pill('FINISH',816,565,230,PAPER,36)
b+=grp('race-gauge',assets['performance-gauge'],933,461,.66)
b+=grp('race-gauge-needle','<path d="M0 0L-70-38" stroke="#283A3C" stroke-width="8"/><circle r="12" fill="#283A3C"/>',933,461,.66)
for f in range(113):
    q=max(0,min(1,(f/30-.8)/1.6));a=math.radians(114*(1-(1-q)**3))
    px=-70*math.cos(a)+38*math.sin(a);py=-70*math.sin(a)-38*math.cos(a)
    at((257+f)/30,'race-gauge-needle',innerHTML=f'<path d="M0 0L{px:.3f} {py:.3f}" stroke="#283A3C" stroke-width="8"/><circle r="12" fill="#283A3C"/>')
worlds+=shot('race',257,370,'#819E9D','#546447','IT OVER-CHECKS AND OVER-PLANS',b)
contact('race.load',267,'attached instruction burden lags; free car crosses the finish first')

# 05: portrait-free credits, followed by the focal skill document.
b=cloud(39,512)+cloud(856,549)
names=[('Lance Martin',['updated it for','Opus 5.5']),('CJ Avilla',['added','prompt-audit']),('Boris Cherny',['created','Claude Code'])]
for i,(name,sub) in enumerate(names):
    x=43+i*342
    c=box(0,0,308,223,PAPER,2,'paper')+txt(name,154,66,32,INK,'middle')+txt(sub[0],154,118,25,INK,'middle')+txt(sub[1],154,158,29,CORAL,'middle')+txt('SOURCE VIDEO CREDIT',154,202,17,INK,'middle')
    b+=grp('contributor-'+str(i),c,x,420);reveal(370/30+.03+i*.05,'contributor-'+str(i))
card=box(0,0,620,710,PAPER,3,'paper')+txt('prompt-audit',310,112,64,INK,'middle',family='EB Garamond')+lines(45,182,530,7,48)+pill('SKILL / COMMAND',59,584,502,TEAL,34)
b+=grp('skills-command',card,230,722)
b+=bot('skills-bot-left',-9,1184,.29)+bot('skills-bot-right',765,1191,.28)
init('skills-command',opacity=0,y=140)
at(370/30+.30,'skills-command',opacity=1);tween(370/30+.30,'skills-command',.42,y=0)
worlds+=shot('skills',370,436,'#8C7E9F','#5A5769',"SOURCE-CREDITED SKILLS",b)
contact('skills.arrival',390,'contributor credits settle before the command document arrives')

# [436,600) is intentionally absent here: reused approved video, not reconstructed.
shots.extend([{'id':id_,'frames':[a,z],'duration':(z-a)/30,'editable':'preserved original project','reuse':'approved movie'} for id_,a,z in [('wash',436,486),('terminal',486,524),('scanner',524,600)]])

# 09: marker circle singles out the supplied classroom quote.
b=grp('class-board',assets['chalkboard'],126,968)
b+=box(122,619,849,247,PAPER,2,'paper')+txt('Always double-check',545,711,58,INK,'middle')+txt('your work.',545,784,59,INK,'middle')
b+=grp('class-circle','<ellipse cx="544" cy="741" rx="425" ry="115" fill="none" stroke="#BA5543" stroke-width="9"/>')
b+=(box(57,500,106,61,CORAL,3,'paper')+txt('1',110,542,58,PAPER,'middle'))+bot('class-bot',133,1058,.30,'magnifying-glass','thinking')
init('class-circle',opacity=0,scale=.88,svgOrigin='544 741');at(600/30+.42,'class-circle',opacity=1);tween(600/30+.42,'class-circle',.16,scale=1)
worlds+=shot('classroom',600,650,'#AA847E','#746357','1. DOUBLE-CHECK RITUALS',b)
contact('quote.inspect',613,'duplicate-check instruction is isolated by a marker circle')

# 10: held megaphone points at capital letters; waves cause phrase to expand.
b=''
for i,(words,y) in enumerate([('YOU MUST',593),('ALWAYS RUN',706),('THE TESTS!!',819)]):
    id_='shout-words-'+str(i)
    b+=grp(id_,txt(words,0,0,81,PAPER,'middle'),590,y)
    init(id_,opacity=0,y=32)
    at(650/30+.24+i*.24,id_,opacity=1);tween(650/30+.24+i*.24,id_,.16,y=0)

b+=bot('shout-bot',85,1070,.35,face='thinking',dynamic=True)
b+=grp('shout-megaphone',assets['megaphone'],358,1182)
b+=grp('shout-waves','<path d="M574 1110Q629 1180 574 1250M616 1069Q710 1180 616 1294" stroke="#D7B450" stroke-width="11" fill="none"/>')
at(650/30,'shout-bot-arms',innerHTML=held_arms('shout-bot',85,1070,.35,None,(400,1240)))
init('shout-waves',opacity=0);at(650/30+.23,'shout-waves',opacity=1);tween(650/30+.23,'shout-waves',.37,scale=1.1,svgOrigin='526 1182')
worlds+=shot('shout',650,691,'#273C53','#202D43','2. SHOUTING IN CAPS',b)
contact('megaphone.amplify',657,'held mouthpiece projects waves toward the capital instruction')

# 11: soles reach the independent platform; unnecessary stairs collapse behind.
b=pill('CAUTION',759,416,240,YELLOW,32)+txt('STEP-BY-STEP',879,500,22,INK,'middle')
b+=box(842,648,214,29,'#916F48',1,'wood')+'<path d="M864 680L897 723M1032 680L1001 723" stroke="#735838" stroke-width="10"/>'
colors=['#DA9150','#D8B64F','#5F9E75','#5AA5B0','#637FB1','#927CA8']
for i in range(9):
    step=assets['step'].replace(TEAL,colors[i%6]);id_='stair-'+str(i)
    b+=grp(id_,step,65+i*101,1360-i*89)
    init(id_,opacity=0);at(691/30+i*.08,id_,opacity=1)
    # Bot reaches the upper platform then failure cascades top → bottom.
    tween(691/30+1.85+(8-i)*.04,id_,.34,rotation=26+4*(i%3),y=140+i*17,x=-48)
b+=bot('stair-bot',-75,1050,.30,pose='standing')
bx=-75;by=1050
for f in range(76):
    sec=f/30
    if sec<.32: x=bx;y=1360-.30*904
    elif sec<1.82:
        q=min(8,(sec-.32)/.1875);within=q-int(q)
        x=bx+q*101
        y=1360-q*89-.30*904-39*math.sin(within*math.pi)
    else:
        x=bx+808
        y=648-.30*904
    at(691/30+sec,'stair-bot',x=(x-bx)/.30,y=(y-by)/.30,rotation=0)
    if f in [21,32,43,54,75]:contact_samples.append({'shot':'stairs','frame':691+f,'soleY':y+.30*904,'support':'step or independent upper platform','phase':'climb / platform hold'})
b+='<path d="M0 1452H1080" stroke="#252F34" stroke-width="35"/><path d="M0 1452H1080" stroke="#E5BA58" stroke-width="35" stroke-dasharray="28 30"/>'
worlds+=shot('stairs',691,767,'#B5A455','#756546','3. STEP-BY-STEP SCRIPTS',b)
contact('stairs.collapse',747,'staircase falls after the climb; bot remains supported by independent upper platform')

# 12: lens reviews changes but permission gate stays locked; no fictitious approval.
b=grp('proposal-page',paper(690,680),327,562)
proposal=['− Always double-check your work.','− YOU MUST ALWAYS RUN THE TESTS!!','− Step 1. Read the file. Step 2. Plan.','+ Run the tests before you commit.']
for i,line in enumerate(proposal):
    id_='proposal-row-'+str(i);y=745+i*118
    b+=grp(id_,box(357,y,632,75,'#D38871' if i<3 else '#A5C8A0',2)+txt(line,375,y+49,24,INK,family='JetBrains Mono',weight=400))
    reveal(767/30+.34+i*.33,id_)
b+=pill('Apply? y/n',719,1177,279,PAPER,31)
b+=grp('permission-gate',assets['permission-gate'],39,1093)
b+=bot('permission-bot',282,1150,.31,'standing','thinking',dynamic=True)
b+='<path d="M317 1418Q590 1490 925 1403" stroke="#AD6650" stroke-width="10" fill="none"/><path d="M927 1357V1477" stroke="#DAB857" stroke-width="13"/>'
b+=grp('permission-lens',assets['lens'],526,810,.65)
for f in range(94):
    sec=f/30;lx=526+min(sec,1.8)*58;ly=810+min(sec,1.8)*161
    at(767/30+sec,'permission-lens',x=(lx-526)/.65,y=(ly-810)/.65)
    at(767/30+sec,'permission-bot-arms',innerHTML=held_arms('permission-bot',282,1150,.31,None,(lx+153*.65,ly+164*.65)))
worlds+=shot('permission',767,861,'#88A284','#48634E','NOTHING CHANGES WITHOUT YOUR OK',b)
contact('proposal.inspect',778,'highlighted proposal appears; NO EDITS YET and Apply? y/n remain pending',approval='not given')

# 13: brief evidence intro, preserving the short source beat.
b=grp('real-run-file',assets['evidence-file'],119,603,1.16)+bot('real-run-bot',716,1162,.31)
init('real-run-file',opacity=0,y=125);at(861/30,'real-run-file',opacity=1);tween(861/30,'real-run-file',.24,y=0)
worlds+=shot('real-run',861,887,'#796078','#5D4350','A REAL RUN',b)

# 14: recreate supplied post as an attributed quotation, not a fake screenshot.
b=box(62,510,949,617,PAPER,3,'paper')+txt('Dan McAteer',104,593,56)+txt('@daniel_mac8',106,645,32,CORAL)
post=['“~70 ways to improve”','skills · CLAUDE.md · AGENTS.md']
for i,line in enumerate(post):b+=txt(line,104,769+i*90,49 if i==0 else 36,INK,family='EB Garamond' if i==0 else 'Inter')
b+=txt('Opus 5.5 / prompt audit',104,970,35)+txt('RETYPED SOURCE EXCERPT · SEP 2026',104,1068,25)
b+=box(626,1197,405,272,INK,10,'card')+txt('> prompt-audit',649,1270,27,PAPER,family='JetBrains Mono',weight=400)+txt('auditing files…',649,1340,25,TEAL,family='JetBrains Mono',weight=400)
b+=bot('post-bot',167,1137,.35)
worlds+=shot('post',887,923,'#8CABB2','#4D6C70','DAN McATEER, DEVELOPER',b)

# 15: findings attach to each of the three files, then reported counter increments.
b=box(322,443,436,179,INK,7,'card')+txt('FIXES FOUND · SOURCE CLAIM',540,486,23,YELLOW,'middle')+txt('0',540,587,88,'#D77E59','middle',extra='id="files-count"')
for i,label in enumerate(['skills/','CLAUDE.md','AGENTS.md']):
    b+=grp('file-'+str(i),paper(282,494,label),41+i*355,909)
    for j in range(4):
        id_=f'file-finding-{i}-{j}'
        art=box(-31,-45,65,83,CORAL,1,'paper')+txt('!',0,12,45,PAPER,'middle')
        b+=grp(id_,art,101+i*355+j*42,1090+(j%2)*28)
        init(id_,opacity=0,y=-181,rotation=-11+9*j)
        at(923/30+.19+(i*4+j)*.078,id_,opacity=1)
        tween(923/30+.19+(i*4+j)*.078,id_,.16,y=0)
b+=bot('files-bot',476,695,.26)
for f,n in [(941,'24'),(950,'46'),(960,'70')]: at(f/30,'files-count',textContent=n)
worlds+=shot('files',923,985,'#B4AE97','#726A4D','SKILLS, CLAUDE.md AND AGENTS.md',b)
contact('findings.accumulate',941,'findings land on three named files before source-reported counter reaches 70',claim='unverified source quotation')

# 16: visible supplied article title/byline/date, precise quoted findings.
b=box(96,486,683,791,PAPER,3,'paper')+txt('RETYPED SOURCE EXCERPT',128,555,29)+txt('Claude Platform',128,613,28,CORAL)
for i,line in enumerate(['Reducing cost and','improving performance','with Claude Platform']):b+=txt(line,128,703+i*62,45,INK,family='EB Garamond')
b+=txt('Lance Martin · Anthropic',128,937,29)+txt('September 8, 2026',128,986,28)

b+=grp('paper-results',box(122,1010,630,130,'#DAC883',2,'paper')+txt('“costs … an additional 9%”',145,1062,39,INK,family='EB Garamond')+txt('“around 2 percentage points”',145,1110,36,INK,family='EB Garamond'))
reveal(985/30+1.1,'paper-results')
b+=grp('test-bench',assets['test-bench'],205,1393)
b+=bot('test-bot',480,1130,.30,face='thinking',dynamic=True)
for i,c in enumerate(['#B0C9C5','#D6908B','#D4C073']):b+=box(788+i*76,903,61,160,c,8)+box(800+i*76,865,35,41,PAPER,0)
b+=grp('test-handle','<path d="M874 1358L783 1243" stroke="#BCC5BF" stroke-width="28"/><circle cx="783" cy="1243" r="29" fill="#D16449"/>')
for f in range(91):
    sec=f/30
    angle=(-32*min(1,(sec-.65)/.16) if .65<=sec<.81 else -32*(1-min(1,(sec-.81)/.25)) if .81<=sec<1.06 else 0)
    theta=math.radians(angle)
    hx=874-91*math.cos(theta)+115*math.sin(theta)
    hy=1358-91*math.sin(theta)-115*math.cos(theta)
    at(985/30+sec,'test-handle',innerHTML=f'<path d="M874 1358L{hx:.3f} {hy:.3f}" stroke="#BCC5BF" stroke-width="28"/><circle cx="{hx:.3f}" cy="{hy:.3f}" r="29" fill="#D16449"/>')
    at(985/30+sec,'test-bot-arms',innerHTML=held_arms('test-bot',480,1130,.30,None,(hx,hy)))
b+=grp('test-status',pill('SOURCE RESULTS',773,673,271,TEAL,26));reveal(985/30+1.05,'test-status')
worlds+=shot('research',985,1076,'#789AA7','#415D66','A SOURCE-CITED TEST',b)
contact('bench.run',1010,'lever depresses before source-quoted result strip appears')

# 17: cost index uses a common baseline; AFTER is 91% of BEFORE.
b=''
for r in range(8):
    for c in range(6): b+=box(c*196-(96 if r%2 else 0),480+r*114,182,103,'#84918E',1,'wall')
b+=box(240,771,211,640,CORAL,1,'card')+box(674,828.6,211,582.4,TEAL,1,'card')
b+='<path d="M202 1411H924" stroke="#203037" stroke-width="6"/>'
b+=txt('100',345,945,74,PAPER,'middle')+txt('91',780,1003,74,PAPER,'middle')
b+='<path d="M927 773H948V830H927" stroke="#F4EBD8" stroke-width="7" fill="none"/>'+txt('−9%',919,715,43,PAPER,'middle')
b+=pill('BEFORE',208,1422,279,YELLOW,34)+pill('AFTER',641,1422,279,YELLOW,34)
b+=txt('≈9% lower cost',542,445,55,PAPER,'middle')+txt('source claim · illustrative cost index',540,500,28,PAPER,'middle')
monster='<path d="M-74 0Q-102-70-66-113L-84-164L-27-149Q26-164 47-140L89-163L77-104Q111-63 70 0Z" fill="#80984F" stroke="#405D47" stroke-width="7"/><circle cx="-32" cy="-91" r="16" fill="#E9D4AD"/><circle cx="38" cy="-91" r="16" fill="#E9D4AD"/><circle cx="-32" cy="-90" r="7" fill="#294346"/><circle cx="38" cy="-90" r="7" fill="#294346"/><path d="M-29-49Q3-26 38-51" stroke="#294346" stroke-width="10" fill="none"/>'
b+=grp('cost-creature',monster,348,763)
b+=grp('cost-burp',pill('BURP!',33,685,180,PAPER,35));reveal(1076/30+.37,'cost-burp')
tween(1076/30+.27,'cost-creature',.13,scaleY=1.11,svgOrigin='0 0');tween(1076/30+.40,'cost-creature',.20,scaleY=1)
b+=bot('cost-bot',483,1201,.24)
worlds+=shot('cost',1076,1121,'#889495','#795E45','FEWER TOOL CALLS, SMALLER BILL',b)

# 18: arrows physically enter target; each consequence appears after the hit.
b=cloud(38,528)+cloud(319,439)+cloud(91,711)+grp('accuracy-target',assets['target'],738,922)
b+=pill('ABOUT 2 POINTS',53,411,447,PAPER,39)+txt('source-reported accuracy gain',76,512,30,PAPER)
b+=bot('accuracy-before-bot',-21,1134,.31,face='thinking')+bot('accuracy-after-bot',354,1134,.31)
b+=pill('OPUS 5.5',27,1390,244,CORAL,27)+pill('OPUS 5.5',426,1390,244,CORAL,27)
b+=grp('accuracy-bullseye',pill('BULLSEYE!',742,585,302,YELLOW,43));init('accuracy-bullseye',opacity=0)
for i,(dy,landing) in enumerate([(-132,.55),(66,1.13),(0,1.79)]):
    id_='target-arrow-'+str(i);b+=grp(id_,assets['arrow'],738,922+dy)
    init(id_,opacity=0,x=-720,y=130)
    at(1121/30+landing-.27,id_,opacity=1)
    tween(1121/30+landing-.27,id_,.27,x=0,y=0,ease='power1.in')
    contact('arrow.hit',round(1121+landing*30),'arrow head lands on target; earlier arrows remain embedded',targetWorld=[738,922+dy])
at(1121/30+1.86,'accuracy-bullseye',opacity=1)
worlds+=shot('accuracy',1121,1196,'#819563','#536549','ABOUT 2 POINTS MORE ACCURATE',b)

# 19: same guide sheet fans out; framing stays close and short.
guide_back=box(0,0,460,530,PAPER,3,'paper')+lines(30,120,360,8,43)
b=grp('guide-back',guide_back,216,797)+grp('guide-front',assets['guide'],216,797)+bot('guide-bot',706,1129,.34,'holding-object')
init('guide-back',rotation=0,svgOrigin='230 410');tween(1196/30+.16,'guide-back',.38,rotation=-14,x=-55)
tween(1196/30+.16,'guide-front',.38,rotation=8,x=21)
worlds+=shot('guide',1196,1227,'#B58C66','#756A51','GET THE COMMAND AND THE GUIDE',b)

# 20: visibly typed AUDIT, rather than claiming a real comment was submitted.
b=box(40,625,1000,693,PAPER,17,'paper')+txt('Comments',87,724,56)+txt('Illustrative comment interface',87,802,29)
b+=box(84,956,912,171,'#E0E2D8',29)+txt('AUDIT',135,1062,67,INK,extra='id="comment-value"')
b+=pill('Send',784,1181,207,TEAL,39)+bot('comment-bot',101,682,.29)
at(1227/30,'comment-value',textContent='')
for i in range(1,6):at(1227/30+.12+i*.08,'comment-value',textContent='AUDIT'[:i])
worlds+=shot('comment',1227,1262,'#3D3240','#443B35','COMMENT AUDIT',b)
contact('comment.type',1242,'AUDIT text enters illustrative comment field; no submission depicted')

# Stage geometry and motion remain separate from caption track.
spec={'schemaVersion':'1.0','compositionId':'rough-story','fps':30,'durationSec':D,'initial':initial,'events':sorted(events,key=lambda e:e['time'])}
save('scene-events.json',spec)
fonts=''
fontroot=Path('/Users/mayowaadesanya/.agents/skills/hyperframes-creative/frame-presets/code-editorial/fonts')
for family,file,weight in [('Inter','Inter-700.woff2',700),('EB Garamond','EBGaramond-700.woff2',700),('JetBrains Mono','JetBrainsMono-400.woff2',400)]:
    data=base64.b64encode((fontroot/file).read_bytes()).decode()
    fonts+=f'@font-face{{font-family:"{family}";src:url(data:font/woff2;base64,{data});font-weight:{weight};font-style:normal}}'
head=json.loads((BASE/'assets/materials/headline-font-data.json').read_text())['data']
fonts+=f'@font-face{{font-family:Inter;src:url(data:font/woff2;base64,{head});font-weight:900;font-style:normal}}'
svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 1080 1920"><defs>{defs}</defs>{worlds}</svg>'
(P/'compositions/story.html').write_text(f'<template><style>{fonts}#rough-story-root{{position:absolute;inset:0;overflow:hidden}}.motion-asset{{transform-box:fill-box}}</style><div id="rough-story-root" data-composition-id="rough-story" data-width="1080" data-height="1920" data-duration="{D}">{svg}</div><script>window.MotifEventEngine.compile({json.dumps(spec)},"rough-story");</script></template>')

# Captions follow word timestamps measured from the final generated narration.
# Approved captions remain inside the locked movie; this track has no entries there.
caps='';capinit=[];capevents=[]
voice=json.loads((P/'narration-script.json').read_text())
save('voice-plan.json',voice)
alignment=json.loads((P/'caption-alignment.json').read_text()) if (P/'caption-alignment.json').exists() else {'chunks':[]}
for i,c in enumerate(alignment['chunks']):
    chunk=c['text'];start=c['start'];end=c['end']
    assert end<=436/30+.000001 or start>=600/30-.000001
    w=min(980,max(210,c.get('width',86+len(chunk)*32)));x=(1080-w)/2;id_=f'fine-caption-{i}'
    art=box(x,1570,w,110,CORAL,2,'paper')+txt(chunk,540,1647,67,PAPER,'middle',family='EB Garamond')
    caps+=grp(id_,art);capinit.append({'target':'#'+id_,'props':{'opacity':0}})
    for time,opacity in [(max(0,start-.00001),1),(end-.00001,0)]:
        capevents.append({'time':time,'target':'#'+id_,'action':'SET','params':{'props':{'opacity':opacity}}})
cs={'schemaVersion':'1.0','compositionId':'rough-captions','durationSec':D,'initial':capinit,'events':sorted(capevents,key=lambda e:e['time'])}
save('caption-events.json',cs)
(P/'compositions/captions.html').write_text(f'<template><style>{fonts}#rough-caption-root{{position:absolute;inset:0;overflow:hidden}}</style><div id="rough-caption-root" data-composition-id="rough-captions" data-width="1080" data-height="1920" data-duration="{D}"><svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 1080 1920">{caps}</svg></div><script>window.MotifEventEngine.compile({json.dumps(cs)},"rough-captions");</script></template>')

def index(native=False):
    w,h=(360,640) if native else (1080,1920)
    audio=""
    if (P/"audio-plan.json").exists():
        for i,t in enumerate(json.loads((P/"audio-plan.json").read_text())["tracks"]):
            audio+=f'<audio id="rough-audio-{i}" class="clip" src="{t["src"]}" data-start="{t["start"]}" data-duration="{t["duration"]}" data-volume="{t["volume"]}" data-track-index="{4+i}"></audio>'
    return f'''<!doctype html><html><head><meta charset="utf-8"><title>Motif full reconstruction fine cut</title><style>html,body{{margin:0;width:100%;height:100%;overflow:hidden;background:{INK}}}#stage{{position:absolute;inset:0;overflow:hidden}}#canvas{{position:absolute;width:1080px;height:1920px;transform:scale({w/1080});transform-origin:0 0}}#locked-passage{{position:absolute;inset:0;width:1080px;height:1920px;object-fit:fill}}</style><script src="assets/gsap.min.js"></script><script src="assets/motion-primitives.js"></script><script src="assets/motion-engine.js"></script></head><body><div id="stage" data-composition-id="main" data-width="{w}" data-height="{h}" data-fps="30" data-duration="{D}"><div id="canvas"><div id="rough-story-host" class="clip" data-composition-id="rough-story" data-composition-src="compositions/story.html" data-track-kind="graphics" data-track-index="1" data-start="0" data-duration="{D}" data-width="1080" data-height="1920"></div><div id="rough-captions-host" class="clip" data-composition-id="rough-captions" data-composition-src="compositions/captions.html" data-track-kind="captions" data-track-index="2" data-start="0" data-duration="{D}" data-width="1080" data-height="1920"></div><video id="locked-passage" class="clip" src="assets/baseline/{'mobile' if native else 'final'}.mp4" data-start="{436/30}" data-duration="{164/30}" data-track-index="3" muted playsinline></video></div>{audio}</div><script>window.__timelines['main']=gsap.timeline({{paused:true}});</script></body></html>'''
(P/'index.html').write_text(index())
m=P/'native-mobile';m.mkdir(exist_ok=True)
for n in ['assets','compositions']:
    if not (m/n).exists():(m/n).symlink_to('../'+n,target_is_directory=True)
for n in ['package.json','hyperframes.json']:shutil.copy2(P/n,m/n)
(m/'index.html').write_text(index(True))

bounds={'barbell':(-489,-119,982,242),'performance-gauge':(-108,-108,216,216),'instruction-note':(-80,-36,165,80),'shelf':(0,-143,935,179),'answer-page':(0,0,620,738),'pencil':(-6,-270,33,290),'race-car':(-180,-118,360,218),'skill-card':(0,0,515,603),'chalkboard':(0,0,825,390),'megaphone':(0,-83,193,171),'step':(0,0,169,81),'permission-gate':(0,0,282,374),'lens':(-143,-143,314,324),'evidence-file':(0,0,625,648),'test-bench':(0,-105,805,249),'target':(-223,-223,446,604),'arrow':(-313,-33,318,66),'guide':(0,0,465,538)}
grips={'barbell':{'leftGrip':(-133,0),'rightGrip':(122,0)},'megaphone':{'grip':(42,58)},'lens':{'grip':(153,164)},'pencil':{'grip':(12,-76)},'performance-gauge':{'pivot':(0,0)},'target':{'center':(0,0)}}
actions={'barbell':['lift','strain'],'performance-gauge':['indicate'],'instruction-note':['attach','burden'],'pencil':['mark'],'race-car':['race'],'megaphone':['amplify'],'step':['climb','collapse'],'permission-gate':['await-permission'],'lens':['inspect'],'test-bench':['run-test'],'target':['receive-hit'],'arrow':['fly','embed'],'guide':['fan']}
for name,art in assets.items():
    x,y,w,h=bounds[name]
    propdefs=''
    for material in ['paper','wood','wall','card']:
        if f'url(#{material}Surface)' in art:
            propdefs+=f'<pattern id="{material}Surface" width="2048" height="2048" patternUnits="userSpaceOnUse"><image href="../materials/{material}.png" width="2048" height="2048"/></pattern>'
    source=P/'assets/props'/f'{name}.svg'
    source.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="{x} {y} {w} {h}"><defs>{propdefs}</defs>{art}</svg>')
    anchors={key:{'x':(point[0]-x)/w,'y':(point[1]-y)/h} for key,point in grips.get(name,{}).items()}
    save(f'assets/props/{name}.json',{'id':'reconstruction-rough-'+name,'name':name.replace('-',' ').title(),'category':'prop','subcategory':'reference-reconstruction','concepts':['instruction-audit','reference-study'],'keywords':['paper','cutout',name],'style':'reference-expressive-v1','orientation':'front','dimensions':{'width':w,'height':h,'unit':'px'},'artBox':{'x':x,'y':y,'width':w,'height':h},'anchors':anchors,'compatibleCharacters':['motif-bot'],'supportedActions':actions.get(name,['hold','reveal']),'sourceType':'vector','source':{'file':str(source.relative_to(ROOT)),'generator':str((P/'build.py').relative_to(ROOT)),'reference':'Agent-authored geometry for a mapped source shot; no source prop pixels.'},'preview':str(source.relative_to(ROOT)),'license':'project-original','status':'review','presentationStatus':'fine-cut','version':1})
save('reconstruction-timeline.json',{'source':'/Users/mayowaadesanya/Downloads/igexport-Dd15NcHvlNl.mp4','duration':D,'frames':1262,'fps':30,'retiming':False,'provenance':'Codex-assisted, reference-led production using Motif','shots':sorted(shots,key=lambda s:s['frames'][0]),'interactions':interactions,'approvedReuse':[436,600]})
save('contact-coordinates.json',{'samples':contact_samples,'method':'Precomputed world coordinates; canonical hands use inverse placement transforms. Gauge and lever endpoints are finite geometry sets about fixed pivots.','limitations':'World-coordinate contact records, sampled encoded-frame review; no automatic pixel-contact assertion for every rendered pose.'})
save('style-preset.json',{'id':'reference-expressive-v1','scope':'reconstruction only','canonicalMascot':'locked v1, imported generator functions only','surfaces':'quiet existing paper, wall, wood, card materials','headlines':'editable taped paper; genuine Inter 900','captions':'editable coral paper, EB Garamond 700','newShotStatus':'fine cut; local quiet surfaces, contact shadows, cut edges','defaultStyleModified':False})
print(f'Built {len(shots)} source shots / {len(assets)} required pieces / {len(events)} finite events; baseline reused unchanged.')

save('cost-scale.json',{'baselineY':1411,'before':{'index':100,'x':240,'topY':771,'height':640},'after':{'index':91,'x':674,'topY':828.6,'height':582.4},'ratio':582.4/640,'qualification':'illustrative index encoding the source claim; no verified cost measurement'})
