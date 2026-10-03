#!/usr/bin/env python3
"""Finite production-specific rowhouse choreography. Saved plan/assets/voice only.
No planning, TTS, canonical edits, shared-recipe registration or provider calls.
"""
import sys,json,math,re,shutil,argparse,hashlib
from pathlib import Path
from html import escape
from xml.etree import ElementTree as ET
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2];sys.path.insert(0,str(ROOT/'scripts'))
from motif_performance import render as perform,channels
from motif_reaction import matrix,compose,point,reaction
from build_motif_bot import DEFS as BOT_DEFS
from motif_ui_production import write_composition
from motif_script import write_index
from motif_produce import sha,command,loudness
from motif_quality import read,write,plan_check
INK='#202C32';CREAM='#F4EBD8';EDGE='#DCCDB3';TEAL='#56BFB1';DARK='#254D50';CORAL='#DF806B';GOLD='#EBC46B'
NS='http://www.w3.org/2000/svg';ET.register_namespace('',NS)
PARTS={};CONTACTS=[];BINDINGS=[];STAGE='rough'
def group(b,x=0,y=0,angle=0,s=1,id_=None):return f'<g'+(f' id="{id_}"' if id_ else '')+f' transform="translate({x:.4f} {y:.4f}) rotate({angle:.4f}) scale({s:.5f})">{b}</g>'
def path(d,fill,stroke=None,w=2):return f'<path d="{d}" fill="{fill}"'+(f' stroke="{stroke}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"' if stroke else '')+'/>'
def rect(x,y,w,h,fill,r=0):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}"/>'
def line(d,color=INK,w=3):return path(d,'none',color,w)
def cut(d,color,grain=True):
 return group(path(d,INK),5,8)+group(path(d,EDGE),2,4)+path(d,color)+ (path(d,'url(#cardGrain)') if grain else '')
def progress(u,a,b):
 v=max(0,min(1,(u-a)/(b-a)));return v*v*(3-2*v)
def lerp(a,b,p):return a+(b-a)*p
def clone(b,prefix):return re.sub(r'id="([^"]+)"',lambda m:f'id="{prefix}-{m[1]}"',b)
LOCAL_DEFS='''<pattern id="cardGrain" width="47" height="41" patternUnits="userSpaceOnUse"><path d="M3 6l2 1M22 10l3 -1M37 31l2 0M9 29l3 1" stroke="#766A53" stroke-width=".65" opacity=".13"/><circle cx="34" cy="7" r=".7" fill="#FFF9EA" opacity=".35"/><circle cx="17" cy="20" r=".9" fill="#766A53" opacity=".1"/></pattern><pattern id="wallGrain" width="73" height="69" patternUnits="userSpaceOnUse"><path d="M5 12h3M41 21h4M28 53h3" stroke="#796955" stroke-width=".7" opacity=".13"/><circle cx="53" cy="48" r="1" fill="#F4EBD8" opacity=".25"/></pattern>'''
DEFS=BOT_DEFS.removeprefix('<defs>').removesuffix('</defs>')+LOCAL_DEFS

def artwork():
 """One bounded master with real editable layers; renderer reads these shapes."""
 art={}
 art['rowhouse-facade']=cut('M8 4L369 0Q381 68 375 153L380 444L2 448Q-3 310 0 191Z',CREAM)
 art['rowhouse-facade']+=cut('M31 161Q189 153 343 161L344 388Q193 395 29 388Z',DARK)
 # Three uneven paper sash windows, tactile insets, thick bars.
 for i,(x,w,y) in enumerate([(33,81,31),(148,89,25),(272,76,35)]):
  art['rowhouse-facade']+=group(cut(f'M0 0L{w} -2L{w+1} 105L-2 109Z',EDGE)+rect(9,8,w-17,87,'#64869A',7)+line(f'M{w/2} 9V95M9 48H{w-8}',CREAM,5),x,y)
 art['rowhouse-facade']+=rect(22,415,326,13,EDGE,3)+line('M20 398H352',EDGE,4)
 art['rowhouse-facade']+=rect(78,194,117,24,'#F1DEB7',5)+rect(88,227,94,10,'#819B88',4)
 # Large open room; dry/wet floor will remain an independent layer.
 art['teal-original-roof']=cut('M1 171L217 4Q225 -3 239 11L450 169L445 191L8 188Z',TEAL)
 art['teal-original-roof']+=path('M1 171L217 4L450 169L437 177L217 25L18 180Z','#318E85')
 art['teal-original-roof']+=line('M91 112L361 112M130 81L319 81M50 145L405 145',DARK,3)+line('M153 82L150 110M233 113L231 145M310 146L309 173',DARK,2)
 art['teal-original-roof']+=rect(30,183,25,18,DARK,3)+rect(388,183,25,18,DARK,3)
 art['coral-replacement-roof']=cut('M0 2L174 -2L447 5L452 69L349 72L349 51L309 51L308 72L2 69Z',CORAL)
 art['coral-replacement-roof']+=line('M14 18L432 21M14 49H290M371 51H433','#AD5D4E',4)+path('M310 51H349V75H310Z',DARK)
 art['coral-replacement-roof']+=rect(30,67,25,18,DARK,3)+rect(388,68,25,18,DARK,3)
 art['interior-floor-strip']=cut('M0 0L312 -2L316 30L1 33Z',CREAM)+line('M13 8L299 7',EDGE,4)
 art['upper-window-flap']=cut('M0 0L91 -3L92 78L0 82Z',EDGE)+rect(9,9,72,59,'#64869A',4)+line('M43 9V68M9 36H81',CREAM,5)
 art['left-keyed-roof-slot']=rect(0,0,26,22,INK,5)+rect(6,4,14,8,EDGE,2)
 art['right-keyed-roof-slot']=art['left-keyed-roof-slot']
 art['paper-gold-checkpoint-plate']=cut('M1 119L115 6L137 0L262 122L247 330L7 334Z',GOLD)+line('M16 118L128 19L246 123L244 315L20 319Z','#B58E39',4)
 art['paper-gold-checkpoint-plate']+=group(clone(art['rowhouse-facade'],'relief'),22,119,0,.58)+group(clone(art['teal-original-roof'],'relief'),4,4,0,.58)
 art['paper-gold-checkpoint-tab']=cut('M0 1Q20 -8 51 1L52 47L3 51Z',GOLD)+line('M16 17L8 27L17 37M9 27H39',DARK,4)
 art['paper-gold-rollback-carriage']=cut('M0 0L300 3L306 26L0 29Z',GOLD)+line('M10 14H292','#B58E39',4)
 art['paper-gold-catch-tongue']=cut('M0 0L165 1L176 -24L192 -19L189 19L-1 21Z',GOLD)+line('M10 6H162','#B58E39',3)
 art['paper-gold-history-strip']=''.join(group(cut('M0 3L83 0L88 84L4 90Z',GOLD)+line('M4 3L5 88','#B58E39',3)+path('M4 3L17 17L15 82L5 88Z','#D0A84E'),i*77,0) for i in range(6))
 art['teal-side-gutter']=cut('M0 0L24 -1L25 112Q27 128 48 128L77 125L77 149L42 153Q-1 149 0 111Z',TEAL)+line('M12 10V109Q13 139 44 139H66',DARK,3)
 art['paper-gold-catch-cup']=cut('M0 0L98 -3L87 89L14 93Z',GOLD)+path('M0 0L98 -3L80 18L19 23Z','#B58E39')+line('M21 25L27 81M77 23L72 80','#F8D887',4)
 art['write-latch']=cut('M0 0L34 -2L40 79L4 84Z',INK)+rect(10,10,19,37,TEAL,8)
 art['rain-ribbon-anchor']=cut('M0 0L40 2L42 53L1 55Z',TEAL)+line('M12 18L20 27L30 18',DARK,4)
 art['test-ribbon-guide']=cut('M0 0L288 4L283 36L5 40Z',INK)+rect(20,10,251,10,EDGE,4)
 art['folio-center-hinge']=rect(0,0,16,320,INK,6)+line('M7 18V307','#A79879',2)
 art['wet-test-history-leaf']=cut('M0 2L153 -2L150 206L3 210Z',GOLD)+group(clone(art['rowhouse-facade'],'hist-wet'),18,64,0,.32)+group(clone(art['coral-replacement-roof'],'hist-wet'),4,39,0,.33)+path('M30 155Q75 178 125 155L125 170Q70 198 30 171Z',TEAL)
 art['failed-roof-history-leaf']=cut('M0 1L153 -1L150 206L3 211Z',GOLD)+group(clone(art['coral-replacement-roof'],'hist-failed'),3,37,0,.33)+line('M23 121L128 124',DARK,4)
 art['history-state-original']=cut('M0 1L153 -1L150 206L3 211Z',GOLD)+group(clone(art['rowhouse-facade'],'hist-original'),18,64,0,.32)+group(clone(art['teal-original-roof'],'hist-original'),4,3,0,.33)
 art['history-state-restored']=clone(art['history-state-original'],'restored')
 art['checkpoint-archive-slot']=cut('M0 0L42 -1L39 435L3 443Z',GOLD)+rect(9,8,21,415,DARK,5)
 art['pinboard-seam']=line('M0 0L628 -2',INK,10)+rect(15,-4,7,33,EDGE,1)+rect(604,-4,7,33,EDGE,1)
 art['tabletop']=cut('M0 0L717 -3L720 46L644 47L567 43L490 50L411 44L331 48L251 44L160 50L81 43L0 48Z',CREAM)
 # Composite focus groups contain actual relevant pieces, not empty focus markers.
 art['aligned-roof-profile-pair']=group(clone(art['teal-original-roof'],'pair-before'),0,0,0,.65)+group(clone(art['coral-replacement-roof'],'pair-after'),316,78,0,.65)
 art['leak-droplet-and-floor-contact']=path('M30 0Q5 36 8 48Q23 70 40 49Q52 29 30 0Z',TEAL)+group(clone(art['interior-floor-strip'],'leak-floor'),-80,85,0,.75)
 art['teal-roof-to-gutter-water-path']=group(clone(art['teal-original-roof'],'path-roof'),0,0,0,.65)+group(clone(art['teal-side-gutter'],'path-gutter'),286,126,0,.65)
 art['restored-rowhouse-and-seated-history-spine']=group(clone(art['rowhouse-facade'],'restored-facade'),12,130,0,.65)+group(clone(art['teal-original-roof'],'restored-roof'),-12,12,0,.65)+group(clone(art['paper-gold-history-strip'],'restored-spine'),-12,430,0,.65)
 art['roof-eave-grip']=rect(0,0,25,10,EDGE,2)
 art['house-dry-state']=clone(art['interior-floor-strip'],'dry-state')
 art['house-wet-state']=path('M0 0Q130 30 312 -2L314 30Q135 60 1 33Z',TEAL)
 return art

LAYOUT={'rowhouse-facade':(173,518,1),'teal-original-roof':(138,338,1),'coral-replacement-roof':(640,454,.72),'interior-floor-strip':(205,853,1),'upper-window-flap':(321,543,1),'paper-gold-checkpoint-plate':(40,630,.44),'checkpoint-archive-slot':(93,540,1),'teal-side-gutter':(565,514,1),'paper-gold-catch-cup':(590,681,1),'paper-gold-checkpoint-tab':(92,815,1),'test-ribbon-guide':(223,310,1),'pinboard-seam':(44,275,1),'tabletop':(0,1009,1),'paper-gold-history-strip':(80,943,1)}
def create_asset():
 asset=P/'assets/props/reversible-rowhouse-folio.svg';art=artwork()
 shown=''.join(f'<g id="{k}" transform="translate({LAYOUT.get(k,(0,0,1))[0]} {LAYOUT.get(k,(0,0,1))[1]}) scale({LAYOUT.get(k,(0,0,1))[2]})"'+(' style="display:none"' if k not in LAYOUT else '')+f'>{v}</g>' for k,v in art.items())
 asset.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="720" height="1280" viewBox="0 0 720 1280"><defs>'+LOCAL_DEFS+'</defs>'+shown+'</svg>\n')
 local={'teal-original-roof':{'eave':[30,183],'right-key':[400,198],'left-key':[42,198]},'coral-replacement-roof':{'right-key':[400,81],'left-key':[42,81],'leak-notch':[329,61]},'paper-gold-checkpoint-tab':{'right-grip':[39,25],'left-grip':[13,25]},'rain-ribbon-anchor':{'grip':[20,29]},'write-latch':{'grip':[23,36]},'interior-floor-strip':{'hinge':[0,16]},'paper-gold-catch-tongue':{'hook':[175,0]},'folio-center-hinge':{'hinge':[8,160]},'failed-roof-history-leaf':{'hinge':[3,105]},'wet-test-history-leaf':{'hinge':[3,105]}}
 meta={'id':'reversible-rowhouse-folio','name':'Reversible rowhouse folio','state':'GENERATED','status':'generated','scope':'scene-specific','category':'production-hero','style':'motif-gold-v1','materials':['fibrous cream card','teal and coral laminated card','paper-gold folds','charcoal card','teal vellum test droplets'],'layers':list(art),'anchors':{'roof-left':[180/720,536/1280],'roof-right':[538/720,536/1280],'archive-tab':[112/720,840/1280],'floor-hinge':[205/720,868/1280],'rain-pull':[600/720,660/1280]},'local_anchors':local,'dimensions':{'width':720,'height':1280},'interactions':[s['action_binding'] for s in read(P/'production-plan.json')['shots']],'provenance':'Original agent-authored SVG for this exact production; no external footage, generated raster or third-party artwork. Canonical Bot is separate and reused unchanged.','license':'project-original','sourceType':'vector','source':{'file':str(asset.relative_to(P)),'builder':'source/build.py:create_asset'},'sha256':sha(asset),'preview':'review/hero-native.png','promotion':'No canonical promotion requested'}
 write(asset.with_suffix('.json'),meta)
 write(P/'assets/props/part-layout.json',LAYOUT)
 return asset

def load_parts():
 root=ET.fromstring((P/'assets/props/reversible-rowhouse-folio.svg').read_text());parts={}
 for el in root:
  if el.tag.endswith('g'):parts[el.attrib['id']]=''.join(ET.tostring(ch,encoding='unicode') for ch in el)
 return parts

def droplet(x,y,size=1,color=TEAL):return group(cut('M19 0Q16 12 5 28Q-6 44 5 54Q20 68 34 53Q47 39 36 25Z',color),x,y,0,size)
def frame(shot,index,count,global_frame):
 q=shot['quality'];u=index/max(1,count-1);t=index/30;sid=shot['id'];number=int(sid.split('-')[1]);n=count/30
 positions={};transforms={};responded=[];events=[]
 main_event=.58*n
 def place(id_,x,y,s=1,angle=0,body=None,age=None):
  if id_ not in PARTS and body is None:raise ValueError('unregistered part '+id_)
  raw=PARTS[id_] if body is None else body
  actual=(x,y);m=matrix(x,y,angle,s,s)
  hit=next((z for z in q['reaction_radius']['targets'] if z['id']==id_),None)
  if hit:
   rr=q['reaction_radius'];r=reaction(t-(main_event if age is None else age),rr['origin'],actual,rr['radius'],hit['relevance'],hit['amplitude'],rr['duration'],hit['delay']);m=compose(matrix(r['x'],r['y'],r['rotation']),m);responded.append(id_)
  transforms[id_]=m;positions[id_]=actual
  return f'<g id="{id_}" transform="matrix('+ ' '.join(f'{v:.6f}' for v in m)+f')">{raw}</g>'
 def bot(x,y,s,state,targets=None,performance_age=None):
  if q['performance']['state']=='absent':raise ValueError('Bot attempted in absent shot')
  c=channels(state,t if performance_age is None else performance_age);primary=compose(matrix(x,y,sx=s,sy=s),matrix(-512,-904))
  pose=compose(matrix(512,904,c['angle'],1/math.sqrt(c['sy']),math.sqrt(c['sy'])),matrix(-512,-904));total=compose(primary,pose)
  bindings={}
  for hand,(id_,anchor) in (targets or {}).items():
   if id_ not in transforms:raise ValueError('contact prop not painted '+id_)
   bindings[hand]={'prop_transform':transforms[id_],'anchor':anchor,'puppet_transform':total}
   local=__import__('motif_reaction').grip(transforms[id_],anchor,total);actual=point(total,local);wanted=point(transforms[id_],anchor)
   CONTACTS.append({'shot':sid,'frame':global_frame,'hand':hand,'prop':id_,'world_anchor':wanted,'world_hand':actual,'error_authoring_px':math.dist(actual,wanted)})
  b=perform(state,t if performance_age is None else performance_age,bindings)
  return f'<g id="bot" data-performance="{state}" transform="matrix('+ ' '.join(f'{v:.6f}' for v in primary)+f')">{b}</g>'
 b=rect(0,0,720,1280,'#BBA688')+rect(0,0,720,1280,'url(#wallGrain)')
 b+=path('M0 1012L720 1005V1280H0Z','#A99578')+place('pinboard-seam',44,275)+place('tabletop',0,1009)
 b+='<ellipse cx="368" cy="982" rx="276" ry="21" fill="#202C32" opacity=".12"/>'
 # Persistent table seam, archive and live cutaway hero.
 if number in (1,3,5,6,7):
  hx,hy=173,518;facade=PARTS['rowhouse-facade']
  b+=place('checkpoint-archive-slot',93,540)
  if number>=3:b+=place('paper-gold-checkpoint-plate',44,612,.46)
  b+=place('rowhouse-facade',hx,hy)
  b+=place('left-keyed-roof-slot',180,514)+place('right-keyed-roof-slot',538,514)
  b+=place('teal-side-gutter',565,514)+place('paper-gold-catch-cup',590,681)
  wet=number==6 or (number==5 and u>.59)
  sag=(progress(u,.59,.82) if number==5 else 1-progress(u,.48,.72) if number==6 else 0)*25
  floor=path(f'M0 0Q145 {sag} 312 -2L316 30Q145 {33+sag} 1 33Z',TEAL if wet and sag>3 else CREAM)+path(f'M0 0Q145 {sag} 312 -2L316 30Q145 {33+sag} 1 33Z','url(#cardGrain)')
  if number==6 and .48<u<.72:
   p=progress(u,.48,.72);floor=group(floor,0,16,0,max(.08,abs(math.cos(p*math.pi))))
  b+=place('interior-floor-strip',205,853,body=floor)
  b+=place('upper-window-flap',321,543)
 if number==1:
  lift=progress(u,.18,.40);fall=progress(u,.62,.85)
  ox=138+126*progress(u,.36,.62);oy=338-125*lift+62*fall
  mouth=progress(u,.30,.50)
  b+=group(path('M0 0Q123 -29 230 0Q137 60 0 0Z',INK),303,329,0,mouth)
  roof=place('teal-original-roof',ox,oy,1,-3*lift+5*fall)
  replacement=place('coral-replacement-roof',lerp(750,309,progress(u,.48,.85)),452,1,-3*(1-progress(u,.48,.85)))
  latch=place('write-latch',152,752,1,lerp(0,-27,progress(u,.08,.17)))
  tongue=place('paper-gold-catch-tongue',lerp(-220,ox-155,progress(u,.86,1)),oy+192,1)
  hands={'r':('write-latch',[23,36])} if u<.18 else {'r':('teal-original-roof',[30,183])} if u<.76 else {}
  b+=latch+roof+replacement+tongue
  b+=bot(128-13*progress(u,.62,.85),969,.52,'focused' if u<.65 else 'surprised',hands,t if u<.65 else max(0,t-.65*n))
 elif number==2:
  spread=progress(u,.1,.70);settle=progress(u,.52,.78)
  # Tight detail is achieved by scaling real parts, not a container-only crop.
  b+=place('rowhouse-facade',175,701,.88,body=clone(PARTS['rowhouse-facade'],'close'))
  b+=place('checkpoint-archive-slot',64,544)
  b+=place('paper-gold-history-strip',76,700,1,body=group(PARTS['paper-gold-history-strip'],0,0,0,max(.02,spread)))
  b+=place('paper-gold-catch-tongue',lerp(-102,82,progress(u,0,.34)),642,1)
  b+=place('teal-original-roof',lerp(264,82,settle),lerp(275,459,settle),.64,lerp(2,-4,settle))
  b+=place('coral-replacement-roof',lerp(580,401,spread),538,.64,4)
  b+=path('M284 659L284 699M495 597L495 699',GOLD,GOLD,7)
 elif number==3:
  restore=progress(u,0,.25);capture=progress(u,.27,.68);store=progress(u,.69,.96)
  b+=place('teal-original-roof',lerp(83,138,restore),lerp(459,338,restore),lerp(.64,1,restore),lerp(-4,0,restore))
  b+=place('coral-replacement-roof',586,799,.30)
  # A full silhouette relief physically sweeps across, then parks in archive.
  px=lerp(-268,174,capture);px=lerp(px,43,store);ps=lerp(1.49,.46,store)
  plate=place('paper-gold-checkpoint-plate',px,lerp(370,612,store),ps)
  tab=place('paper-gold-checkpoint-tab',lerp(94,54,capture)+38*store,813)
  b+=plate+tab+bot(120-20*capture+19*store,970,.5,'focused',{'r':('paper-gold-checkpoint-tab',[39,25])})
 elif number==4:
  p=progress(u,.08,.63);rx=lerp(210,402,p);lx=lerp(145,34,p)
  b+=place('paper-gold-checkpoint-plate',27,596,.50)
  b+=place('folio-center-hinge',350,545)
  b+=place('rowhouse-facade',rx,553,.66,3*p)
  b+=group(clone(PARTS['rowhouse-facade'],'before-leaf'),lx+20,553,-3*p,.66)
  b+=place('teal-original-roof',lx,436,.69,-3*p)
  b+=place('coral-replacement-roof',rx-18,lerp(348,518,progress(u,.20,.59)),.69,3*p)
  b+=place('right-keyed-roof-slot',rx+248,559,.66)
  b+=place('paper-gold-history-strip',42,864,1)
  b+=f'<g id="aligned-roof-profile-pair">'+line('M68 561L664 561',GOLD,3)+'</g>'
 elif number in (5,7):
  b+=place('test-ribbon-guide',223,301)
  b+=rect(257,340,205,290,'#A6E5D6',10).replace('fill=', 'opacity=".15" fill=',1)
  good=number==7
  b+=place('teal-original-roof',138,338) if good else place('coral-replacement-roof',138,458)
  b+=place('paper-gold-checkpoint-tab',94,813)
  if good:
   b+=place('coral-replacement-roof',54,810,.25)
  ribbon=progress(u,.04,.77)
  py=lerp(590,711,ribbon)
  pull=place('rain-ribbon-anchor',124,py,1)
  b+=line(f'M146 320V{py+5}',INK,5)+pull
  for j in range(3):
   v=progress(u,.10+j*.095,.51+j*.095)
   if good:
    if v<.52:x,y=320+30*j,lerp(348,427,v/.52)
    elif v<.78:x,y=lerp(340+30*j,580,(v-.52)/.26),lerp(427,547,(v-.52)/.26)
    else:x,y=610,lerp(547,730,(v-.78)/.22)
   else:
    if v<.48:x,y=360+20*j,lerp(330,451,v/.48)
    elif v<.64:x,y=lerp(360+20*j,459,(v-.48)/.16),459
    else:x,y=459,lerp(490,842,(v-.64)/.36)
   if v>0:b+=droplet(x,y,.67+(.08*j))
  if not good:
   b+=bot(103-18*ribbon,979,.52,'focused' if u<.49 else 'worried',{'r':('rain-ribbon-anchor',[20,29])} if u<.83 else {'r':('paper-gold-checkpoint-tab',[39,25])})
   if u>.59:b+=f'<g id="leak-droplet-and-floor-contact">'+path(f'M280 846Q330 {846+25*progress(u,.59,.82)} 493 846',TEAL,TEAL,9)+'</g>'
  else:
   b+=f'<g id="teal-roof-to-gutter-water-path">'+line('M589 594Q594 645 619 670',TEAL,6)+'</g>'
   if u>.65:b+=rect(604,737,53,20,TEAL,8)
 elif number==6:
  pull=progress(u,.14,.83);a=progress(u,.2,.54);z=progress(u,.43,.82)
  b+=place('paper-gold-history-strip',80,936,1)
  b+=place('paper-gold-rollback-carriage',83,795,1,body=group(PARTS['paper-gold-rollback-carriage'],0,0,0,1+.14*pull))
  b+=place('coral-replacement-roof',lerp(138,570,a),lerp(458,800,a),lerp(1,.3,a),12*a)
  b+=place('teal-original-roof',lerp(54,138,z),lerp(610,338,z),lerp(.45,1,z),-7*(1-z))
  b+=place('paper-gold-checkpoint-tab',94-43*pull,814)
  b+=bot(116-40*pull,978,.50,'burdened' if u<.85 else 'relieved',{'r':('paper-gold-checkpoint-tab',[39,25]),'l':('paper-gold-checkpoint-tab',[13,25])} if u<.88 else {},max(0,t-.85*n) if u>=.85 else t)
  # Linkages make one pull visibly act on roof exchange and floor reversal.
  b+=line(f'M89 840L202 828L214 886',GOLD,7)
 elif number==8:
  unfold=progress(u,0,.27);back1=progress(u,.35,.65);back2=progress(u,.62,.84)
  b+=place('rowhouse-facade',173,518)+place('teal-original-roof',138,338)+place('interior-floor-strip',205,853)
  b+=place('teal-side-gutter',565,514)+place('paper-gold-catch-cup',590,681)+rect(604,737,53,20,TEAL,8)
  b+=place('paper-gold-history-strip',lerp(210,80,unfold),935,1)
  b+=place('history-state-original',55,741,.9,-7*unfold)
  # Two physical failed parts on one pivot/base, hence exactly three state bays.
  fscale=max(.025,1-back1);b+=place('failed-roof-history-leaf',lerp(220,45,back1),757,.94*fscale,8*(1-back1))
  b+=place('wet-test-history-leaf',lerp(302,45,back1),777,.94*fscale,-4*(1-back1))
  b+=place('history-state-restored',lerp(486,168,back2),741,.9*max(.025,1-back2),7*(1-back2))
  b+=place('paper-gold-checkpoint-tab',92-19*back2,818)
  b+=f'<g id="restored-rowhouse-and-seated-history-spine">'+line('M156 996L568 996',GOLD,11)+'</g>'
 # Every requested response target must have an actual painted registration.
 missing=set(z['id'] for z in q['reaction_radius']['targets'])-set(positions)
 if missing:raise ValueError('unsupported reaction target in '+sid+': '+str(missing))
 BINDINGS.append({'shot':sid,'frame':global_frame,'actual_part_positions':positions,'reaction_targets_bound':responded,'performance':q['performance']['state']})
 # Event-specific short cut-paper accent near actual change; no unrelated confetti.
 age=u-.61
 if 0<age<.09:
  at={'x':455 if number==5 else 360,'y':868 if number==5 else 491}
  b+=group(line('M-21 -17L-34 -27M0 -24V-38M21 -18L34 -29',CORAL if number==5 else GOLD,5),at['x'],at['y'],0,1-age/.09)
 return b

def captions(plan,words):
 font=P/'assets/fonts/EBGaramond-700.woff2'
 from fontTools.ttLib import TTFont
 from motif_ui_production import captions_frame
 timing=read(P/'alignment-review.json')['aligned_words'];tokens=[];cursor=0
 for word in re.findall(r'\S+',plan['script']):
  tokens.append({'text':word,'start':round(timing[cursor][1]*30)/30,'end':timing[cursor][2],'script_indices':[cursor]});cursor+=1
 groups=[];batch=[]
 for w in tokens:
  batch.append(w)
  if len(batch)==4 or re.search(r'[.!?]$',w['text']):groups.append({'text':' '.join(x['text'] for x in batch),'words':batch,'start':batch[0]['start']});batch=[]
 if batch:groups.append({'text':' '.join(x['text'] for x in batch),'words':batch,'start':batch[0]['start']})
 for i,g in enumerate(groups):g['end']=groups[i+1]['start'] if i+1<len(groups) else plan['targetFrames']/30
 write(P/'caption-events.json',groups)
 fnt=TTFont(font);count=plan['targetFrames'];first=captions_frame(groups,0,fnt);ev=[]
 for i in range(1,count):ev.append({'time':i/30,'target':'#captions-world','action':'SET','params':{'props':{'innerHTML':captions_frame(groups,i,fnt)}}})
 return write_composition(P,'captions',count/30,first,ev,LOCAL_DEFS)

def build(create=False):
 global PARTS,CONTACTS,BINDINGS
 plan=read(P/'production-plan.json');plan_check(plan)
 if create:create_asset()
 PARTS=load_parts();CONTACTS=[];BINDINGS=[];all_events=[];initial=[];frames=[];evidence_shots=[]
 for shot in plan['shots']:
  start,end=shot['startFrame'],shot['endFrame'];count=end-start;id_=shot['id']
  sequence=[frame(shot,i,count,start+i) for i in range(count)]
  events=[{'time':i/30,'target':'#'+id_+'-world','action':'SET','params':{'props':{'innerHTML':sequence[i]}}} for i in range(1,count)]
  spec=write_composition(P,id_,count/30,sequence[0],events,DEFS)
  frames.append({'id':id_,'start':start/30,'duration':count/30,'source':'compositions/'+id_+'.html'})
  initial+=spec['initial'];all_events +=[{**e,'time':round(e['time']+start/30,6),'composition':id_} for e in events]
  contacts=[{'time':(start+round((count-1)*p))/30,'kind':kind} for p,kind in [( .58,'contact'),(.8,'landing')]]
  evidence_shots.append({'id':id_,'startFrame':start,'endFrame':end,'temporal_events':contacts})
  write(P/'review'/(id_+'-before.svg'),{'note':'preview source is frame output, not evidence; actual MP4 will be sampled'} ) if False else None
  for suffix,i in [('before',0),('mid',count//2),('after',count-1)]:
   (P/'review'/(id_+'-'+suffix+'.svg')).write_text('<svg xmlns="http://www.w3.org/2000/svg" width="360" height="640" viewBox="0 0 720 1280"><defs>'+DEFS+'</defs>'+sequence[i]+'</svg>')
   if suffix=='mid':
    import cairosvg;cairosvg.svg2png(url=str(P/'review'/(id_+'-'+suffix+'.svg')),write_to=str(P/'review'/(id_+'-'+suffix+'.png')))
 capspec=captions(plan,None)
 write(P/'scene-events.json',{'schemaVersion':'1.0','fps':30,'durationSec':plan['targetFrames']/30,'initial':initial,'events':sorted(all_events,key=lambda e:e['time']),'shots':frames})
 write(P/'evidence-shots.json',evidence_shots)
 write(P/'quality-bindings.json',{'scope':'production-specific finite adapter; shared performance, inverse grip and selected reaction functions','contract':read(P/'execution-contract.json'),'shots':[{**s,'compiled_frame_count':s['endFrame']-s['startFrame']} for s in plan['shots']],'sampled_bindings':BINDINGS[::30]})
 write(P/'review/contact-audit.json',{'samples':len(CONTACTS),'maximum_error_authoring_px':max([x['error_authoring_px'] for x in CONTACTS] or [0]),'scope':'inverse transform solver mathematical residual; temporal strips verify actual painted continuity','frames':CONTACTS})
 voice=P/'assets/voice/narration-af-nova.wav';d=read(P/'speech-timing.json')['duration']
 # Review-level normalization is existing rough workflow; SFX/final mix gated later.
 review=voice.with_name('review-voice.wav')
 if not review.exists():command(['ffmpeg','-v','error','-y','-i',str(voice),'-af','loudnorm=I=-16:TP=-1.8:LRA=11','-ar','24000','-ac','1',str(review)],P)
 write(P/'audio-plan.json',{'narration':'assets/voice/narration-af-nova.wav','review_input':'assets/voice/review-voice.wav','duration':d,'review_gain_db':0,'music':False,'sfx':False,'subjective_listening':'human required','voice_speed':.85})
 write_index(P,frames,plan['targetFrames']/30,d,0)
 write(P/'pre-render-checks.json',{'status':'DATA_CHECKS_ONLY','plan':plan_check(plan),'exact_script':read(P/'brief.json')['script']==plan['script'],'alignment':'alignment-review.json','contacts':'review/contact-audit.json','unsupported_policy':'fail on unregistered part/reaction or absent Bot','scope':'not creative or painted approval'})
 print('Built',len(frames),'shots',plan['targetFrames'],'frames',flush=True)
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--create-asset',action='store_true');args=a.parse_args();build(args.create_asset)
