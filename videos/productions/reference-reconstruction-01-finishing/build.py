#!/usr/bin/env python3
"""Bounded reference production. Original SVG art; unchanged Motif event runtime."""
from pathlib import Path
from html import escape
import json, sys, shutil, re, hashlib, base64
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
from build_motif_bot import assemble_pose, arm, DEFS as BOT_DEFS

P=Path(__file__).resolve().parent
D=164/30
T=50/30
S=88/30
ROUGH='--rough' in sys.argv
INK='#202C32'; PAPER='#F4EBD8'; CORAL='#B5573B'
for folder in ('assets/voice','assets/sfx','assets/materials','compositions','renders','review'):
    (P/folder).mkdir(parents=True,exist_ok=True)
old=ROOT/'videos/productions/little-book-workshop-staging'
for name in ('gsap.min.js','motion-engine.js','motion-primitives.js'):
    shutil.copy2(old/'assets'/name,P/'assets'/name)
for name in ('pop.mp3','click-soft.mp3','whoosh-short.mp3'):
    shutil.copy2(old/'assets/sfx'/name,P/'assets/sfx'/name)

def save(name,obj): (P/name).write_text(json.dumps(obj,indent=2)+'\n')
def text(value,x,y,size=40,color=INK,anchor='start',family='Inter',weight=700,extra=''):
    return f'<text x="{x}" y="{y}" font-family="{family}" font-weight="{weight}" font-size="{size}" fill="{color}" text-anchor="{anchor}" {extra}>{escape(value)}</text>'
def rect(x,y,w,h,color,rx=0,texture=None):
    result=f'<rect x="{x+5}" y="{y+8}" width="{w}" height="{h}" rx="{rx}" fill="#192425" opacity=".21"/><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{color}"/>'
    if texture and not ROUGH: result+=f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="url(#{texture})" opacity=".54"/>'
    return result
def group(id_,body,x=0,y=0,scale=1):
    return f'<g transform="translate({x} {y}) scale({scale})" data-layout-allow-overflow><g id="{id_}" class="motion-asset" data-layout-allow-overflow>{body}</g></g>'
def bot(id_,x,y,scale=.30,pose='standing',face='happy',overrides=None):
    b,_=assemble_pose(pose,face,overrides or {})
    b=re.sub(r'id="([^"]+)"',lambda m:'id="'+id_+'-'+m[1]+'"',b)
    return group(id_,b,x,y,scale)

defs=BOT_DEFS.removeprefix('<defs>').removesuffix('</defs>')
for name in ('paper','card','wood','wall'):
    if not ROUGH:
        defs+=f'<pattern id="{name}Surface" width="2048" height="2048" patternUnits="userSpaceOnUse"><image href="assets/materials/{name}.png" width="2048" height="2048"/></pattern>'
defs+='<clipPath id="wash-opening"><path d="M0 730H1080V1480H0Z"/></clipPath><clipPath id="scan-opening"><path d="M67 388H668V1475H67Z"/></clipPath>'
defs+='<clipPath id="screen-content"><rect x="142" y="473" width="873" height="717" rx="25"/></clipPath>'

assets={}
assets['wash-portal']=rect(162,858,801,590,'#297C9B',12,'cardSurface')+rect(183,898,751,522,'#284348',3,'wallSurface')
assets['wash-portal']+=rect(164,804,830,102,'#22759B',13,'cardSurface')
for i,c in enumerate(('#EDA84C','#EE7651','#EBD65A','#EAAA48','#DF7759','#E5C658','#DA7954')):
    assets['wash-portal']+=f'<circle cx="{229+i*110}" cy="850" r="14" fill="{c}"/>'
assets['wash-portal']+=rect(306,690,550,109,'#246B8B',9,'cardSurface')+text('CLAUDE.md WASH',581,744,49,PAPER,'middle')+text('SELF-SERVICE · AUTOMATIC',581,777,23,PAPER,'middle',weight=700)
assets['wash-portal']+=rect(0,1423,1080,36,'#394448',0,'cardSurface')
assets['wash-roller']=''
for i,color in enumerate(('#DE7854','#E4C05F','#4FA4C3')*3):
    y=i*57
    assets['wash-roller']+=rect(0,y,142,42,color,15,'paperSurface')
    for j in range(16):
        assets['wash-roller']+=f'<path d="M{5+j*8} {y+8}q{(j%3)-1} 15 0 26" stroke="#F5D6A5" stroke-width="2" opacity=".65"/>'
assets['wash-roller']+='<path d="M-3 0V495M147 0V495" stroke="#244952" stroke-width="6" opacity=".35"/>'
assets['document']=rect(0,0,330,465,'#273236',10,'cardSurface')+rect(18,79,294,205,PAPER,6,'paperSurface')+text('CLAUDE',165,160,48,INK,'middle')+text('.md',165,217,46,INK,'middle')
assets['document']+='<path d="M16 456H328V18" fill="none" stroke="#D8DBC5" stroke-width="5"/>'
assets['instruction-slip']=rect(-65,-28,130,57,'#E6BD69',2,'paperSurface')+text('ALWAYS',0,7,24,INK,'middle')
assets['enter-key']=rect(0,0,270,211,'#B7BAAE',25,'paperSurface')+'<path d="M169 39V90H89m0 0 27-22m-27 22 27 22" fill="none" stroke="#263333" stroke-width="13" stroke-linejoin="round"/>'+text('enter',135,171,46,INK,'middle')
assets['scan-gate']=rect(10,763,745,107,'#9AAFB4',9,'cardSurface')
assets['scan-gate']+=rect(18,861,73,614,'#C0CCCA',3,'paperSurface')+rect(672,861,73,614,'#C0CCCA',3,'paperSurface')
for x in (55,708):
    for i in range(10):
        assets['scan-gate']+=f'<circle cx="{x}" cy="{906+i*55}" r="18" fill="{("#E5C963" if i%3==2 else "#5F797B")}"/><circle cx="{x-3}" cy="{903+i*55}" r="9" fill="#D5DDD4" opacity=".28"/>'
assets['scan-gate']+=rect(209,783,343,62,'#254C42',4,'cardSurface')+text('SCANNING',381,828,41,'#9BD8AB','middle')
assets['scan-lens']='<path d="M84 82L153 164" stroke="#715330" stroke-width="34"/><circle r="135" fill="#B2D9CE" fill-opacity=".17" stroke="#263940" stroke-width="15"/><circle r="123" fill="none" stroke="#BECAB6" stroke-width="8"/><path d="M-95-52Q-54-108 30-103" fill="none" stroke="#F5F0DE" stroke-width="8" opacity=".7"/>'
scanner_page_background=rect(0,0,545,1040,PAPER,3,'paperSurface')
assets['scanner-page']=scanner_page_background+text('CLAUDE.md',36,80,44)
for i in range(18):
    assets['scanner-page']+=f'<path d="M35 {145+i*45}H{440-(i%4)*29}" stroke="#A69E88" stroke-width="12" opacity=".6"/>'
assets['scanner-page']+=text('Always double-check your work.',35,265,25,INK,family='JetBrains Mono',weight=400)
assets['scanner-page']+=text('YOU MUST ALWAYS RUN THE TESTS!!',35,475,24,INK,family='JetBrains Mono',weight=400)
assets['scanner-page']+=text('Step 1. Read. Step 2. Plan.',35,682,25,INK,family='JetBrains Mono',weight=400)
assets['scanner-page']+=text('Step 3. Follow this exact order.',35,725,25,INK,family='JetBrains Mono',weight=400)

for name,art in assets.items():
    width,height=(1080,1920)
    # Geometry is in scene coordinates where practical; stable independent groups remain editable.
    (P/'assets'/f'{name}.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}"><defs>{defs.replace("assets/materials/","materials/")}</defs>{art}</svg>')
    save(f'assets/{name}.json',{'id':'reconstruction-'+name,'name':name.replace('-',' ').title(),'category':'prop','subcategory':'reference-reconstruction','concepts':['instruction-cleanup','audit'],'keywords':['paper','cutout',name],'style':'reference-expressive-v1','orientation':'front','dimensions':{'width':1080,'height':1920,'unit':'px'},'artBox':{'x':0,'y':0,'width':1080,'height':1920},'anchors':{'origin':{'x':0,'y':0}},'compatibleCharacters':['motif-bot'],'supportedActions':{'document':['enter','wash','scan'],'wash-roller':['scrub'],'enter-key':['press','release'],'scan-lens':['inspect']}.get(name,['hold']),'sourceType':'manual','source':{'file':str((P/'assets'/f'{name}.svg').relative_to(ROOT)),'reference':'user-supplied reference video; geometry authored independently'},'version':1,'status':'review','license':'project-original','controlledGroups':re.findall(r'id="([^"]+)"',art)})

def headline(value,wide=False):
    cut='M35 279L81 274L110 278L239 273L298 280L428 273L505 278L602 276L715 282L864 275L927 279L1043 274L1040 321L1044 342L1040 376L955 371L881 378L763 373L681 379L563 376L448 378L331 372L246 379L133 373L78 380L39 376L41 332Z'
    grain=f'<path d="{cut}" fill="url(#paperSurface)"/>' if not ROUGH else ''
    size=42 if len(value)>30 else (46 if wide else 57)
    tape='M31 283L54 259L70 280L77 281L112 338L87 360L71 337L66 335Z M969 332L1024 260L1052 282L1034 310L1032 317L996 359L989 345Z'
    return f'<path d="{cut}" transform="translate(4 8)" fill="#263332" opacity=".22"/><path d="{cut}" transform="translate(1 3)" fill="#D8C9AB"/><path d="{cut}" fill="{PAPER}"/>'+grain+f'<path d="{tape}" transform="translate(2 3)" fill="#504836" opacity=".15"/><path d="{tape}" fill="#CDBF87" opacity=".88"/><path d="M41 283L86 346M981 335L1035 277" stroke="#E8DEB8" stroke-width="3" opacity=".4"/>'+text(value,540,341,size,INK,'middle',weight=900)
def base(color):
    return rect(-15,-15,1110,1950,color,0,'wallSurface')
def floor(color):return rect(-10,1490,1100,440,color,0,'woodSurface')

wash=base('#77A498')+floor('#35585A')
for r in range(5):
    for c in range(18):
        x=c*61-12;y=347+r*63
        wash+=f'<rect x="{x}" y="{y}" width="57" height="58" fill="{("#B9D2CF" if (c+r)%3 else "#AFC5C6")}" stroke="#86A9A6" stroke-width="3"/>'
wash+=rect(870,337,184,145,'#477957',1,'paperSurface')+text('OPEN',962,389,30,PAPER,'middle')+text('24/7',962,434,31,PAPER,'middle')
wash+=assets['wash-portal']
# Small Bot pushes from the left; named grip geometry stays canonical.
wash+=bot('wash-bot',-55,1088,.31,'pushing','thinking')
wash+='<path d="M26 1425L112 1279M217 1425L119 1280" stroke="#A28252" stroke-width="15"/>'
wash+=group('roller-left',assets['wash-roller'],245,900)+group('roller-right',assets['wash-roller'],782,900)
wash+=headline('NO MANUAL CLEANUP')

terminal=base('#202D34')+floor('#46382D')
terminal+='<path d="M132 451Q597 444 1027 454L1046 472L1042 1194Q584 1208 124 1198L116 1176L120 468Z" transform="translate(6 8)" fill="#0E181C" opacity=".3"/><path d="M132 451Q597 444 1027 454L1046 472L1042 1194Q584 1208 124 1198L116 1176L120 468Z" fill="#252827"/>'
terminal+='<path d="M123 454Q580 447 1037 456" stroke="#B0A88F" stroke-width="3"/>'
for i,c in enumerate(('#E77A64','#D5B353','#86AE6F')):terminal+=f'<circle cx="{159+i*32}" cy="483" r="11" fill="{c}"/>'
terminal+=text('claude — /my-app',655,490,24,'#D4CABB','middle',family='JetBrains Mono',weight=400)
terminal+=rect(150,546,866,239,'#252627',10)+'<rect x="150" y="546" width="866" height="239" rx="10" fill="none" stroke="#C98761" stroke-width="4"/>'
terminal+=text('Welcome to Claude Code!',182,611,45,PAPER)
terminal+=text('/help for help, /status for current setup',182,673,27,'#C9C0AE',family='JetBrains Mono',weight=400)+text('cwd: /my-app',182,731,28,'#C9C0AE',family='JetBrains Mono',weight=400)
terminal+=rect(155,936,852,119,'#212726',17)+'<rect x="155" y="936" width="852" height="119" rx="17" fill="none" stroke="#A59E8C" stroke-width="3"/>'
terminal+=text('>',183,1014,45,PAPER,family='JetBrains Mono',weight=400)+text('',263,1014,46,PAPER,family='JetBrains Mono',weight=400,extra='id="command-content"')
terminal+=group('command-caret','<rect width="18" height="49" fill="#F3EADC"/>',263,973)
terminal+=group('terminal-response','<circle cx="176" cy="1100" r="10" fill="#DE7854"/>'+text('Auditing instructions...',199,1112,35,PAPER,family='JetBrains Mono',weight=400))
terminal+=text('? for shortcuts',172,1169,24,'#C6BEAB',family='JetBrains Mono',weight=400)
terminal+=group('enter-key',assets['enter-key'],745,1263)
terminal+=bot('terminal-bot',128,1250,.30,'standing','happy')
# Modest dressing from existing canonical masters; preserve each source.
for name,id_,x,y,scale in [('small-plant','terminal-plant',10,1304,1.45),('coffee-mug','terminal-mug',500,1390,.9)]:
    source=ROOT/'assets/scenes/scene-01/desk-props'/f'{name}.svg'
    raw=source.read_text();raw=re.sub(r'<svg[^>]*>|</svg>|<title>.*?</title>','',raw)
    ids=re.findall(r'id="([^"]+)"',raw)
    for original in ids:
        raw=raw.replace(f'id="{original}"',f'id="{id_}-{original}"').replace(f'url(#{original})',f'url(#{id_}-{original})')
    terminal+=group(id_,raw,x,y,scale)
terminal+=headline('ONE COMMAND IN CLAUDE CODE',True)

scanner=base('#B79D7F')+floor('#6F523B')
scanner+=rect(753,528,296,176,'#273133',6,'cardSurface')+text('PROBLEMS FOUND',902,571,24,'#EBC875','middle')
scanner+=text('0',902,667,98,'#D97354','middle',extra='id="finding-count"')
scanner+=rect(775,891,207,148,'#263D38',5,'cardSurface')+'<rect x="802" y="925" width="55" height="73" fill="#46865A"/><circle cx="913" cy="962" r="31" fill="#46865A"/>'
scanner+='<path d="M771 1379V1483M1030 1379V1483" stroke="#C9AF51" stroke-width="7"/><path d="M771 1389Q900 1435 1030 1389" fill="none" stroke="#BF624D" stroke-width="7"/>'
scanner+='<circle cx="761" cy="1168" r="70" fill="#7B8B8A" stroke="#B7C1B7" stroke-width="12"/><path d="M761 1168L807 1203" stroke="#35494B" stroke-width="22" stroke-linecap="round"/><circle cx="807" cy="1203" r="18" fill="#D27958"/>'
scanner+=headline('IT CHECKS CLAUDE.md, SKILLS, PROMPTS',True)

# One document group persists across wash and scanner shots; no unrelated before/after image swap.
doc=group('wash-document',assets['document'],366,934)
for i in range(7):
    x=(-60 if i%2==0 else 232);y=45+i*48
    slip=assets['instruction-slip'].replace('#E6BD69',('#E6BD69','#D9C2DF','#B6CED0')[i%3])
    doc+=group('slip-'+str(i),slip,366+x,934+y)
wash_effects=''
for i in range(15):
    x=280+(i*73)%540;y=930+(i*83)%440;r=14+(i%4)*6
    wash_effects+=group('foam-'+str(i),f'<circle r="{r}" fill="#E8EEDD" opacity=".93"/><circle cx="{-r*.3}" cy="{-r*.3}" r="{r*.4}" fill="#F5F3DE" opacity=".65"/>',x,y)
wash_effects+=group('spray','<path d="M306 921l-12-27m22 63-40-8M813 939l40-20M799 994l35 8" stroke="#C1E1D1" stroke-width="9" stroke-linecap="round"/>')

scan_doc=scanner_page_background
# Named document-local regions shared by lens and finding geometry.
REGIONS=[{'x':245,'y':258,'boxY':218,'height':65}, {'x':275,'y':468,'boxY':428,'height':65}, {'x':280,'y':688,'boxY':644,'height':96}]
for i,region in enumerate(REGIONS):
    scan_doc+=group('finding-'+str(i),rect(0,0,474,region['height'],'#E5A18B',1,'paperSurface'),28,region['boxY'])
scan_doc+=assets['scanner-page'][len(scanner_page_background):]
scan_doc=group('scanner-paper',group('page-scroll',scan_doc,98,514))
scan_effects=assets['scan-gate']
scan_effects+=group('scan-beam',f'<rect width="568" height="24" fill="#75B284" opacity=".65"/><path d="M0 0H568" stroke="#C3E3B3" stroke-width="8"/>',87,877)
for i in range(3):
    body=rect(-31,-3,62,55,'#CF7155',20,'paperSurface')+'<path d="M-29 30V54H29V30Z" fill="#8C9B94"/><path d="M-18 12Q-11-7-6 2" stroke="#F3D1A8" stroke-width="8" stroke-linecap="round"/>'
    scan_effects+=group('alarm-'+str(i),body,137+i*250,700)
scan_effects+=group('scan-lens',assets['scan-lens'],368,979)
_,bot_parts=assemble_pose('standing','thinking',{})
parts=''.join(bot_parts[k] for k in ('left-leg','right-leg','left-foot','right-foot','right-arm','body','head','antennae','face-panel','face-state','right-hand'))
scan_effects+=group('scanner-bot',parts+'<g id="scanner-arm"></g>',496,1095,.32)

world=f'<g id="wash-world" data-layout-allow-overflow>{wash}</g><g id="terminal-world" data-layout-allow-overflow>{terminal}</g><g id="scanner-world" data-layout-allow-overflow>{scanner}</g>'
# Wash rear is rendered first, document then foreground brushes/foam. Scanner paper is masked behind gate.
world+=f'<g id="persistent-document" data-document-identity="claude-md" data-layout-allow-overflow><g id="wash-subject" clip-path="url(#wash-opening)">{doc}</g><g id="scan-subject" clip-path="url(#scan-opening)">{scan_doc}</g></g>'
world+='<g id="wash-contact">'+group('contact-left',assets['wash-roller'],245,900)+group('contact-right',assets['wash-roller'],782,900)+wash_effects+'</g>'
world+=f'<g id="scan-front">{scan_effects}</g>'

events=[]; initial=[]
def init(target,**props):initial.append({'target':'#'+target,'props':props})
def emit(t,target,action='TWEEN',**params):events.append({'time':round(t,6),'target':'#'+target,'action':action,'params':params})
def tween(t,target,duration,**to):emit(t,target,to=to,duration=duration,ease='power2.inOut')
def set_(t,target,**props):emit(t,target,'SET',props=props)
for id_ in ('terminal-world','scanner-world','scan-subject','scan-front'):init(id_,opacity=0)
for id_ in ('wash-world','wash-subject','wash-contact'):init(id_,opacity=1)
init('wash-document',x=-710)
tween(.02,'wash-document',.38,x=0)
for i in range(7):
    init('slip-'+str(i),x=-710,rotation=(-11 if i%2 else 9))
    tween(.02,'slip-'+str(i),.38,x=0)
    at=.40+i*.065
    destx=(-365-(i%3)*55 if i%2==0 else 455+(i%3)*42)
    tween(at,'slip-'+str(i),.43,x=destx,y=-155-(i%4)*85,rotation=(-90 if i%2==0 else 115))
    tween(at+.40,'slip-'+str(i),.17,y=410,opacity=0)
for id_ in ('contact-left','contact-right'):
    init(id_,transformOrigin='50% 50%')
    for k in range(5):
        tween(.37+k*.17,id_,.08,scaleX=.82 if id_.endswith('left') else 1.12,x=12 if k%2 else -12)
        tween(.45+k*.17,id_,.09,scaleX=1,x=0)
for i in range(15):
    init('foam-'+str(i),opacity=0,scale=.35,transformOrigin='50% 50%')
    emit(.36+(i%5)*.07,'foam-'+str(i),'POP_IN',duration=.17,overshoot=1.08)
    tween(.78+(i%5)*.09,'foam-'+str(i),.37,y=-90-(i%3)*45,opacity=0,scale=.7)
init('spray',opacity=0);emit(.39,'spray','PULSE',peak=.8,rise=.05,fall=.25)
tween(1.18,'wash-document',.32,x=110,y=25,rotation=3)
tween(.02,'wash-bot',.37,x=69,rotation=8)
tween(.95,'wash-bot',.26,rotation=0)
# Sub-frame epsilon avoids decimal rounding past the frame-50 sample; no frame is retimed.
for id_ in ('wash-world','wash-subject','wash-contact'):set_(T-.00001,id_,opacity=0)
set_(T-.00001,'terminal-world',opacity=1)
init('terminal-response',opacity=0)
# Registry code-terminal-run's deterministic text-at-time row technique, compiled into the unchanged event schema.
command='/prompt-audit'
for i in range(len(command)+1):
    at=T+.06+i*.032
    set_(at,'command-content',textContent=command[:i]);set_(at,'command-caret',x=i*27.6)
for i in range(5):set_(T+i*.17,'command-caret',opacity=1 if i%2==0 else 0)
init('terminal-bot',transformOrigin='50% 90%')
tween(T+.53,'terminal-bot',.20,x=1870,y=-1167,rotation=13)
LAND_Y=(1263-1250)/.30-904
tween(T+.73,'terminal-bot',.14,y=LAND_Y,rotation=0)
tween(T+.87,'enter-key',.10,y=8,scaleY=.95,transformOrigin='50% 100%')
# Soles share the key top plane through compression and initial release.
tween(T+.87,'terminal-bot',.10,y=LAND_Y+(8+211*.05)/.30)
set_(T+.92,'terminal-response',opacity=1)
tween(T+.97,'terminal-bot',.10,y=LAND_Y)
tween(T+.97,'enter-key',.10,y=0,scaleY=1)
tween(T+1.07,'terminal-bot',.12,y=LAND_Y-125,rotation=-5)
set_(T+.97,'command-caret',opacity=0)
set_(S-.00001,'terminal-world',opacity=0)
for id_ in ('scanner-world','scan-subject','scan-front'):set_(S-.00001,id_,opacity=1)
init('scan-beam',y=0)
tween(S+.05,'scan-beam',.32,y=28)
tween(S+.37,'scan-beam',.32,y=0)
for i in range(3):
    init('finding-'+str(i),opacity=0)
    at=S+(.75,1.41,2.06)[i]
    set_(at,'finding-'+str(i),opacity=.84)
    set_(S+(.93,1.63,2.16)[i],'finding-count',textContent=str(i+1))
    init('alarm-'+str(i),opacity=.5)
    emit(at+.12,'alarm-'+str(i),'PULSE',peak=1,rise=.04,fall=.15)
    set_(at+.33,'alarm-'+str(i),opacity=1)
def mix(a,b,q):return a+(b-a)*q
def page_y(sec):
    # Dwell while a line is visible below the scan head; feed it upward after inspection.
    stops=[(0,275),(.28,225),(.76,155),(.90,-65),(1.43,-70),(1.58,-260),(2.06,-280),(2.18,-280),(2.42,-540)]
    for (a,va),(b,vb) in zip(stops,stops[1:]):
        if sec<=b:return mix(va,vb,max(0,(sec-a)/(b-a)))
    return stops[-1][1]
def inspected_region(sec):
    first,second,third=REGIONS
    if sec<=.76:return first['x'],first['y'],0
    if sec<.98:
        q=(sec-.76)/.22;return mix(first['x'],second['x'],q),mix(first['y'],second['y'],q),None
    if sec<=1.43:return second['x'],second['y'],1
    if sec<1.68:
        q=(sec-1.43)/.25;return mix(second['x'],third['x'],q),mix(second['y'],third['y'],q),None
    return third['x'],third['y'],2
init('scan-lens',opacity=0,x=0,y=0,svgOrigin='0 0')
init('scanner-paper',y=275)
inspection_samples=[]
# Continuous linear lens/page motion; the canonical grip uses the same transformed handle.
for frame in range(76):
    sec=frame/30;py=page_y(sec);rx,ry,active=inspected_region(sec)
    lx,ly=98+rx,514+py+ry
    if sec<.28:
        q=min(1,sec/.28);lx=mix(490,lx,q);ly=mix(1080,ly,q)
    if sec>2.18:
        q=min(1,(sec-2.18)/.22);lx=mix(lx,470,q);ly=mix(ly,1110,q);active=None
    opacity=min(1,sec/.15) if sec<=2.35 else max(0,1-(sec-2.35)/.16)
    props={'x':lx-368,'y':ly-979,'opacity':opacity}
    if frame==0:set_(S-.00001,'scan-lens',**props)
    else:
        emit(S+(frame-1)/30,'scan-lens','TWEEN',to=props,duration=1/30,ease='none')
        emit(S+(frame-1)/30,'scanner-paper','TWEEN',to={'y':py},duration=1/30,ease='none')
    if sec>2.5:la,lh=arm('left',355,660,'mitten')
    else:la,lh=arm('left',(lx+153-496)/.32,(ly+164-1095)/.32,'grip')
    la=la.replace('id="leftArm"','id="scan-canonical-left-arm"');lh=lh.replace('id="leftHand"','id="scan-canonical-left-hand"')
    set_(S+sec-.00001,'scanner-arm',innerHTML=la+lh)
    inspection_samples.append({'localFrame':88+frame,'pageY':py,'activeRegion':active,'regionLocal':[rx,ry],'lensWorld':[lx,ly],'handleWorld':[lx+153,ly+164],'gripWorld':[lx+153,ly+164],'lensOpacity':opacity})
for region,at in zip(REGIONS,(.93,1.63,2.16)):
    top=514+page_y(at)+region['boxY']
    assert top+region['height']<=763 or top>=870,('finding occluded at count',region,top)
save('inspection-coordinates.json',{'pageOrigin':[98,514],'cameraScale':1,'botOrigin':[496,1095],'botScale':.32,'regions':REGIONS,'findingTimes':[S+.75,S+1.41,S+2.06],'countTimes':[S+.93,S+1.63,S+2.16],'samples':inspection_samples,'findingBoxesVisibleAtCount':True})

spec={'schemaVersion':'1.0','compositionId':'story','fps':30,'durationSec':D,'initial':initial,'events':sorted(events,key=lambda e:e['time'])}
save('scene-events.json',spec)
svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 1080 1920" role="img" aria-label="Reference-led document wash, terminal input and scanner"><defs>{defs}</defs>{world}</svg>'
# Existing engine owns all authored motion. Scene and caption tracks remain separately editable in Studio.
font_root=Path('/Users/mayowaadesanya/.agents/skills/hyperframes-creative/frame-presets/code-editorial/fonts')
font_css=''
for family,file,weight in [('Inter','Inter-700.woff2',700),('EB Garamond','EBGaramond-700.woff2',700),('JetBrains Mono','JetBrainsMono-400.woff2',400)]:
    data=base64.b64encode((font_root/file).read_bytes()).decode()
    font_css+=f'@font-face{{font-family:"{family}";src:url(data:font/woff2;base64,{data}) format("woff2");font-weight:{weight};font-style:normal}}'
headline_font=json.loads((P/'assets/materials/headline-font-data.json').read_text())
font_css+=f'@font-face{{font-family:"Inter";src:url(data:font/woff2;base64,{headline_font["data"]}) format("woff2");font-weight:900;font-style:normal}}'
story=f'''<template><style>{font_css}#story-root{{position:absolute;inset:0;width:100%;height:100%;overflow:hidden}}svg text{{paint-order:stroke fill}} .motion-asset{{transform-box:fill-box}}</style><div id="story-root" data-composition-id="story" data-width="1080" data-height="1920" data-duration="{D}">{svg}</div><script>window.MotifEventEngine.compile({json.dumps(spec)},'story');</script></template>'''
(P/'compositions/story.html').write_text(story)
save('style-preset.json',{'id':'reference-expressive-v1','scope':'this production only','sourceHierarchy':['actual reference picture','canonical Motif Bot identity','existing Motif implementation'],'headline':'newly authored taped paper strip','caption':'coral content-sized EB Garamond 700 paper chunks','palette':{'wash':'#77A498','terminal':'#202D34','scanner':'#B79D7F','caption':'#B5573B'},'materials':['paper','dark-card','wood','wall','roller-fibers','foam'],'timing':'source frames; no retiming','character':'unchanged canonical v1','implementation':'unchanged Motif event engine; scoped authored interactions','defaultStyleModified':False})
save('reconstruction-timeline.json',{'source':str(Path('/Users/mayowaadesanya/Downloads/igexport-Dd15NcHvlNl.mp4')),'sourceInFrame':436,'sourceOutFrameExclusive':600,'fps':30,'frameCount':164,'duration':D,'shots':[{'id':'wash','sourceFrames':[436,486],'localFrames':[0,50],'focus':'document and roller contact','occupancy':'89% width / 39% height','rules':['spring-pop-entrance']},{'id':'terminal','sourceFrames':[486,524],'localFrames':[50,88],'focus':'typed command and Enter contact','occupancy':'88% width / 40% height','rules':['press-release-spring']},{'id':'scanner','sourceFrames':[524,600],'localFrames':[88,164],'focus':'moving page, beam, lens, findings','occupancy':'72% width / 51% height','rules':['spring-pop-entrance']}],'interactions':[{'kind':'document.wash','start':0,'end':T,'contact':.4,'consequence':'seven attached slips peel from document; labeled document remains'},{'kind':'terminal.submit','start':T,'end':S,'contact':T+.87,'response':T+.92,'consequence':'command typed, contact, depression, illustrative response, release'},{'kind':'document.inspect','start':S,'end':D,'findings':[S+.75,S+1.41,S+2.06],'consequence':'highlight and count follow scan progress'}],'provenance':'agent-authored geometry and choreography, not autonomous planner output'})
save('package.json',{'name':'reference-reconstruction-01-finishing','private':True,'scripts':{k:f'npx --yes hyperframes@0.8.99 {v}' for k,v in [('check','check'),('render','render'),('dev','preview')]}})
shutil.copy2(old/'hyperframes.json',P/'hyperframes.json')

def render_index(captions='',audio='',native=False):
    w,h=(360,640) if native else (1080,1920)
    # At native mobile size the complete authored canvas scales once, not each asset/camera.
    css=f'#stage{{position:absolute;inset:0;width:100%;height:100%;overflow:hidden}} #canvas{{position:absolute;width:1080px;height:1920px;transform:scale({w/1080});transform-origin:0 0}}'
    return f'''<!doctype html><html><head><meta charset="utf-8"><title>Motif reconstruction study</title><style>html,body{{margin:0;background:{INK};width:100%;height:100%;overflow:hidden}}{css}</style><script src="assets/gsap.min.js"></script><script src="assets/motion-primitives.js"></script><script src="assets/motion-engine.js"></script></head><body><div id="stage" data-composition-id="main" data-width="{w}" data-height="{h}" data-fps="30" data-duration="{D}"><div id="canvas"><div id="story-host" class="clip" data-composition-id="story" data-composition-src="compositions/story.html" data-track-kind="graphics" data-track-index="1" data-start="0" data-duration="{D}" data-width="1080" data-height="1920"></div>{captions}</div>{audio}</div><script>window.__timelines['main']=gsap.timeline({{paused:true}});</script></body></html>'''
if (P/'compositions/captions.html').exists():
    captions=f'<div id="captions-host" class="clip" data-composition-id="caption-track" data-composition-src="compositions/captions.html" data-track-kind="captions" data-track-index="2" data-start="0" data-duration="{D}" data-width="1080" data-height="1920"></div>'
else: captions=''
audio=''
if (P/'audio-plan.json').exists():
    for i,a in enumerate(json.loads((P/'audio-plan.json').read_text())['tracks']):
        audio+=f'<audio id="audio-{i}" class="clip" src="{a["src"]}" data-start="{a["start"]}" data-duration="{a["duration"]}" data-volume="{a["volume"]}" data-track-index="{3+i}"></audio>'
(P/'index.html').write_text(render_index(captions,audio))
mobile=P/'native-mobile'
mobile.mkdir(exist_ok=True)
for name in ('assets','compositions'):
    if not (mobile/name).exists(): (mobile/name).symlink_to('../'+name,target_is_directory=True)
shutil.copy2(P/'package.json',mobile/'package.json')
shutil.copy2(P/'hyperframes.json',mobile/'hyperframes.json')
(mobile/'index.html').write_text(render_index(captions,audio,True))
print('Built', 'rough' if ROUGH else 'finished', '164-frame passage')
