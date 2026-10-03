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
from motif_ui_production import write_composition,namespace
from motif_script import write_index
from motif_produce import sha,command,loudness
from motif_quality import read,write,plan_check
sys.path.insert(0,str(P/'source'))
from timing import resolve as timing_frame,validate as validate_timing
INK='#202C32';CREAM='#F4EBD8';EDGE='#DCCDB3';TEAL='#56BFB1';DARK='#254D50';CORAL='#DF806B';GOLD='#EBC46B'
NS='http://www.w3.org/2000/svg';ET.register_namespace('',NS)
PARTS={};CONTACTS=[];BINDINGS=[];STAGE='rough';ANCHORS={}
def group(b,x=0,y=0,angle=0,s=1,id_=None):return f'<g'+(f' id="{id_}"' if id_ else '')+f' transform="translate({x:.4f} {y:.4f}) rotate({angle:.4f}) scale({s:.5f})">{b}</g>'
def path(d,fill,stroke=None,w=2):return f'<path d="{d}" fill="{fill}"'+(f' stroke="{stroke}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"' if stroke else '')+'/>'
def rect(x,y,w,h,fill,r=0):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}"/>'
def line(d,color=INK,w=3):return path(d,'none',color,w)
def cut(d,color,grain=True):
 return group(path(d,INK),5,8)+group(path(d,EDGE),2,4)+path(d,color)+ (path(d,'url(#cardGrain)') if grain else '')
def progress(u,a,b):
 v=max(0,min(1,(u-a)/(b-a)));return v*v*(3-2*v)
def lerp(a,b,p):return a+(b-a)*p
def clone(b,prefix):
 ids=set(re.findall(r'id="([^"]+)"',b))
 b=re.sub(r'id="([^"]+)"',lambda m:f'id="{prefix}-{m[1]}"',b)
 return re.sub(r'url\(#([^)]+)\)',lambda m:'url(#'+(prefix+'-' if m[1] in ids else '')+m[1]+')',b)
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
 # Separate silhouettes and physical circuits: engage, capture, roll back.
 art['history-engage-control']=cut('M0 0L53 0L53 51L0 51Z',TEAL)+line('M13 31L26 15L39 31M26 15V41',DARK,5)
 art['checkpoint-capture-control']=cut('M0 4L51 0L51 48L0 52Z',GOLD)+rect(12,13,27,25,DARK,3)+rect(18,19,15,13,CREAM,2)
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

 # Exposed, production-local mechanical causes; all broad card geometry.
 art['write-drive-rack']=cut('M0 0L246 0L246 20L232 20L232 31L211 31L211 20L181 20L181 31L160 31L160 20L130 20L130 31L109 31L109 20L79 20L79 31L58 31L58 20L27 20L27 31L7 31L7 20L0 20Z',GOLD)
 art['comparison-drive-rack']=clone(art['write-drive-rack'],'comparison')
 art['discard-trip-latch']=cut('M0 0L65 1L68 23L3 26Z',CORAL)+rect(9,5,15,13,INK,4)
 art['catch-leaf-spring']=line('M0 31L14 5L31 50L48 5L65 50L82 5L99 49L114 7L128 31',GOLD,9)+line('M0 31L14 5L31 50L48 5L65 50L82 5L99 49L114 7L128 31',INK,2)
 art['comparison-leaf-spring']=clone(art['catch-leaf-spring'],'comparison-spring')
 for name in ['capture-pressure-cam','return-drive-flywheel']:
  art[name]=f'<circle cx="40" cy="40" r="38" fill="{EDGE}"/><circle cx="38" cy="36" r="33" fill="{GOLD}"/><circle cx="38" cy="36" r="9" fill="{DARK}"/>'+line('M38 8V24M38 48V64M10 36H26M50 36H66',DARK,5)
 art['checkpoint-drive-latch']=clone(art['discard-trip-latch'],'checkpoint-latch')
 art['checkpoint-dry-floor-cassette']=clone(art['interior-floor-strip'],'dry-cassette')
 art['floor-shuttle']=cut('M0 0L330 -2L329 20L312 20V36H290V20H35V36H15V21L0 22Z',GOLD)
 art['failed-state-bay']=cut('M0 0L138 -3L139 207L2 210Z',GOLD)+rect(8,10,122,185,DARK,8)
 art['live-floor-mounts']=rect(0,0,20,19,EDGE,3)+rect(292,0,20,19,EDGE,3)
 art['return-drive-lever']=cut('M0 0L25 -2L28 111L2 113Z',CORAL)+f'<circle cx="15" cy="17" r="20" fill="{TEAL}"/>'
 art['return-cam-follower']=line('M0 0L48 0L60 -23L76 -23',GOLD,8)
 art['return-cam-apex']=path('M0 40Q21 -12 50 12Q80 40 50 61Z',GOLD,INK,3)
 for name in ['floor-sag-stop','carriage-stop','checkpoint-display-stop','failed-display-stop']:
  art[name]=cut('M0 0L25 0L25 28L0 28Z',EDGE)+rect(6,6,13,15,INK,2)
 art['history-state-proposed']=clone(art['failed-roof-history-leaf'],'proposed')
 art['test-water-slug']=cut('M23 0Q20 14 6 33Q-6 52 10 62Q24 75 43 57Q54 44 40 28Z',TEAL)
 art['test-water-reservoir']=cut('M0 0L81 0L78 16L3 18Z',EDGE)+line('M9 3H71',DARK,5)
 art['test-take-up-cable']=line('M0 0L0 100',TEAL,3)
 art['dry-cassette-latch']=cut('M0 0L34 0L36 20L3 23Z',GOLD)+rect(7,5,21,10,DARK,2)
 for unused in ('aligned-roof-profile-pair','leak-droplet-and-floor-contact','teal-roof-to-gutter-water-path','restored-rowhouse-and-seated-history-spine'):
  del art[unused]
 # Pressure-captured plate uses stamped shutters, not an unexplained second house.
 art['paper-gold-checkpoint-plate']=cut('M1 119L115 6L137 0L262 122L247 330L7 334Z',GOLD)+line('M16 118L128 19L246 123L244 315L20 319Z','#B58E39',4)
 for x in [35,101,171]:art['paper-gold-checkpoint-plate']+=rect(x,135,45,52,DARK,3)
 art['checkpoint-state-stamp']=line('M16 118L128 19L246 123',TEAL,9)+''.join(rect(x+4,139,37,44,CREAM,3) for x in [35,101,171])+line('M25 296L228 296',CREAM,13)
 return art

LAYOUT={'rowhouse-facade':(173,518,1),'teal-original-roof':(138,338,1),'coral-replacement-roof':(190,1117,.78),'interior-floor-strip':(205,853,1),'upper-window-flap':(321,543,1),'paper-gold-checkpoint-plate':(40,630,.44),'checkpoint-archive-slot':(93,540,1),'teal-side-gutter':(565,514,1),'paper-gold-catch-cup':(590,681,1),'paper-gold-checkpoint-tab':(92,815,1),'test-ribbon-guide':(223,310,1),'pinboard-seam':(44,275,1),'tabletop':(0,1009,1),'paper-gold-history-strip':(80,943,1)}
def create_asset():
 asset=P/'assets/props/reversible-rowhouse-folio.svg';art=artwork()
 shown=''.join(f'<g id="{k}" transform="translate({LAYOUT.get(k,(0,0,1))[0]} {LAYOUT.get(k,(0,0,1))[1]}) scale({LAYOUT.get(k,(0,0,1))[2]})"'+(' style="display:none"' if k not in LAYOUT else '')+f'>{v}</g>' for k,v in art.items())
 asset.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="720" height="1280" viewBox="0 0 720 1280"><defs>'+LOCAL_DEFS+'</defs>'+shown+'</svg>\n')
 local={'teal-original-roof':{'eave':[30,183],'right-key':[400,198],'left-key':[42,198]},'coral-replacement-roof':{'right-key':[400,81],'left-key':[42,81],'leak-notch':[329,61]},'paper-gold-checkpoint-tab':{'right-grip':[39,25],'left-grip':[13,25]},'rain-ribbon-anchor':{'grip':[20,29]},'write-latch':{'grip':[23,36],'brake-grip':[11,67]},'interior-floor-strip':{'hinge':[0,16]},'paper-gold-catch-tongue':{'hook':[175,0]},'folio-center-hinge':{'hinge':[8,160]},'failed-roof-history-leaf':{'hinge':[3,105]},'wet-test-history-leaf':{'hinge':[3,105]}}
 local.update({'discard-trip-latch':{'trip':[9,5]},'catch-leaf-spring':{'output':[128,31]},'comparison-drive-rack':{'teal-clevis':[5,15],'coral-clevis':[244,15]},'capture-pressure-cam':{'follower':[38,70]},'paper-gold-checkpoint-plate':{'registration-stop':[128,330]},'checkpoint-dry-floor-cassette':{'left-tab':[0,16],'right-tab':[312,16]},'floor-shuttle':{'wet-saddle':[155,20]},'failed-state-bay':{'roof-seat':[12,45],'floor-seat':[14,158],'hinge':[3,105]},'live-floor-mounts':{'left':[10,8],'right':[302,8]},'return-drive-lever':{'grip':[15,17]},'return-drive-flywheel':{'crank':[38,36]},'return-cam-follower':{'contact':[76,-23]},'return-cam-apex':{'contact':[50,12]},'checkpoint-display-stop':{'contact':[12,12]},'failed-display-stop':{'contact':[12,12]}})
 local.update({'history-engage-control':{'right-grip':[39,25]},'checkpoint-capture-control':{'right-grip':[39,25]},'upper-window-flap':{'water-contact':[45,40]},'interior-floor-strip':{'water-contact':[155,0]},'teal-original-roof':{**local['teal-original-roof'],'rain-contact':[225,12]},'teal-side-gutter':{'water-contact':[12,139]},'paper-gold-catch-cup':{'water-contact':[45,50]}})
 local.update({'rowhouse-facade':{'left-roof-socket':[7,18],'right-roof-socket':[365,18]},'left-keyed-roof-slot':{'socket':[13,12]},'right-keyed-roof-slot':{'socket':[13,12]},'history-state-original':{'left-roof-socket':[18,30],'right-roof-socket':[135,30]},'paper-gold-checkpoint-plate':{**local['paper-gold-checkpoint-plate'],'left-roof-socket':[20,12],'right-roof-socket':[242,12]},'checkpoint-archive-slot':{'plate-stop':[13,85]},'floor-sag-stop':{'contact':[12,12]},'carriage-stop':{'contact':[12,12]},'test-water-slug':{'tip':[23,70]}})
 local['teal-original-roof']['rain-contact']=[329,88]
 local['history-engage-control']['left-grip']=[13,25]
 local.update({'test-water-reservoir':{'delivery-stop':[40,0]},'test-take-up-cable':{'pickup':[0,100]},'write-drive-rack':{'clevis':[205,19]},'paper-gold-history-strip':{'terminal-clevis':[407,13]}})
 local['interior-floor-strip']['wet-support']=[155,46]
 local['dry-cassette-latch']={'lock':[17,12]}
 local['rowhouse-facade'].update({'base-support':[190,448],'archive-seat':[190,448],'left-window-register':[73.5,82.5],'center-window-register':[192.5,76.5],'right-window-register':[310,86.5],'floor-register':[187,335]})
 local['paper-gold-checkpoint-plate'].update({'left-window-register':[57.5,161],'center-window-register':[123.5,161],'right-window-register':[193.5,161],'floor-register':[126,296]})
 local['paper-gold-rollback-carriage']={'left-output':[0,14],'right-output':[300,14]}
 local['left-keyed-roof-slot']['socket']=[0,22];local['right-keyed-roof-slot']['socket']=[0,22]
 local['coral-replacement-roof']['left-key']=[42,78];local['coral-replacement-roof']['right-key']=[400,78]
 local['test-take-up-cable']['pickup']=[0,0]
 local['test-water-reservoir']['outlet']=[40,0]
 meta={'id':'reversible-rowhouse-folio','name':'Reversible rowhouse folio','state':'GENERATED','status':'generated','scope':'scene-specific','category':'production-hero','style':'motif-gold-v1','materials':['fibrous cream card','teal and coral laminated card','paper-gold folds','charcoal card','teal vellum test droplets'],'layers':list(art),'anchors':{'roof-left':[180/720,536/1280],'roof-right':[538/720,536/1280],'archive-tab':[112/720,840/1280],'floor-hinge':[205/720,868/1280],'rain-pull':[600/720,660/1280]},'local_anchors':local,'dimensions':{'width':720,'height':1280},'interactions':[s['action_binding'] for s in read(P/'production-plan.json')['shots']],'provenance':'Original agent-authored SVG for this exact production; no external footage, generated raster or third-party artwork. Canonical Bot is separate and reused unchanged.','license':'project-original','sourceType':'vector','source':{'file':str(asset.relative_to(P)),'builder':'source/build.py:create_asset'},'sha256':sha(asset),'preview':'review/hero-native.png','promotion':'No canonical promotion requested','state_ownership':{'wet-floor':'same interior-floor-strip group retained in failed bay from shot06 onward','dry-floor':'separate checkpoint-dry-floor-cassette captured in shot03'},'focus_bounds':{'rowhouse-facade':[173,518,380,448],'teal-original-roof':[138,338,450,200],'coral-replacement-roof':[138,458,450,90],'interior-floor-strip':[205,853,316,58]},'mechanical_scope':'finite production-specific adapters only; not registered ordinary producer capabilities'}
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
 """Execute the corrected director's exact finite event stages, all world-local."""
 q=shot['quality'];sid=shot['id'];num=int(sid.split('-')[1]);f=index;t=f/30
 mats={};positions={};responded=[]
 def at(landmark):return timing_frame(shot,landmark)
 def phase(a,b):return progress(f,at(a),at(b))
 def anchor(id_,name):
  try:return ANCHORS[id_][name]
  except KeyError:raise ValueError('unsupported anchor: '+id_+'.'+name)
 def put(id_,x,y,s=1,rot=0,body=None,impact=None,sy=None):
  if id_ not in PARTS:raise ValueError('unsupported production-specific part: '+id_)
  raw=PARTS[id_] if body is None else body
  if id_=='paper-gold-checkpoint-plate' and body is None:raw+=PARTS['checkpoint-state-stamp']
  hit=next((z for z in q['reaction_radius']['targets'] if z['id']==id_),None)
  centers={'rowhouse-facade':[190,220],'teal-original-roof':[225,140],'coral-replacement-roof':[225,35],'interior-floor-strip':[155,16],'paper-gold-checkpoint-tab':[25,25],'upper-window-flap':[45,40],'teal-side-gutter':[35,75],'paper-gold-catch-cup':[45,50],'paper-gold-rollback-carriage':[150,14],'failed-state-bay':[70,104]}
  actual_center=point(matrix(x,y,rot,s,s),centers.get(id_,[0,0]))
  r={'x':0,'y':0,'rotation':0}
  if hit and id_!='paper-gold-history-strip':
   rr=q['reaction_radius'];ev=next((e for e in shot['events'] if e['target']==id_ and e['kind'] in ('contact','impact','landing','handoff')),None)
   when=ev['local_frame']/30 if ev else (impact if impact is not None else count*.6/30)
   r=reaction(t-when,rr['origin'],actual_center,rr['radius'],hit['relevance'],hit['amplitude'],rr['duration'],hit['delay']);responded.append(id_)
  m=matrix(x+r['x'],y+r['y'],rot+r['rotation'],s,s if sy is None else sy)
  mats[id_]=m;positions[id_]=list(actual_center)
  return f'<g id="{id_}" transform="matrix('+ ' '.join(f'{v:.6f}' for v in m)+f')">{raw}</g>'
 def puppet(x,y,state,grips=None,age=None):
  if q['performance']['state']=='absent':raise ValueError('absent Bot painted')
  phases=shot['performance_phases']
  active=[p for p in phases if at(p['start'])<=f]
  if not active:raise ValueError('no registered performance phase')
  selected=active[-1];state=selected['state'];age=max(0,(f-at(selected['start']))/30)
  scale=.47;c=channels(state,t if age is None else age)
  primary=compose(matrix(x,y,sx=scale,sy=scale),matrix(-512,-904))
  pose=compose(matrix(512,904,c['angle'],1/math.sqrt(c['sy']),math.sqrt(c['sy'])),matrix(-512,-904));total=compose(primary,pose);bindings={}
  for hand,(id_,anchor) in (grips or {}).items():
   if id_ not in mats:raise ValueError('unpainted grip target: '+id_)
   bindings[hand]={'prop_transform':mats[id_],'anchor':anchor,'puppet_transform':total}
   local=__import__('motif_reaction').grip(mats[id_],anchor,total);actual=point(total,local);wanted=point(mats[id_],anchor)
   CONTACTS.append({'shot':sid,'frame':global_frame,'hand':hand,'prop':id_,'world_anchor':wanted,'world_hand':actual,'error_authoring_px':math.dist(actual,wanted)})
  raw=perform(state,t if age is None else age,bindings)
  return '<g id="bot" data-performance="'+state+'" transform="matrix('+' '.join(f'{v:.6f}' for v in primary)+')">'+raw+'</g>'
 def wet_floor(amount=1):
  sag=14*amount;d=f'M0 0Q128 {sag*1.7} 312 -2L316 30Q128 {33+sag*1.7} 1 33Z'
  # Local clipping exposes wet color from left to right without replacing identity.
  return path(d,CREAM)+f'<clipPath id="wet-mask"><rect width="{316*amount:.4f}" height="72" x="0" y="-4"/></clipPath><g clip-path="url(#wet-mask)">'+path(d,TEAL)+path(d,'url(#cardGrain)')+'</g>'
 def spring(id_,x,y,p):return put(id_,x,y,body=group(PARTS[id_],0,0,0,.65+.35*p))
 def strip(x,y,p,close=0):
  raw=''
  hit=next((z for z in q['reaction_radius']['targets'] if z['id']=='paper-gold-history-strip'),None)
  if hit:responded.append('paper-gold-history-strip')
  for j in range(6):
   a=progress(p, .10*j,.10*j+.35)*(1-close)
   hinge=0
   if hit:
    rr=q['reaction_radius'];event=next((e for e in shot['events'] if e['target']=='paper-gold-history-strip' and e['kind'] in ('contact','landing','impact')),None)
    if event:
     response=reaction(t-event['local_frame']/30,rr['origin'],[x+j*72*a,y],rr['radius'],hit['relevance'],hit['amplitude'],rr['duration'],hit['delay']+j*.025)
     hinge=response['rotation']
   raw+=group(cut('M0 3L76 0L81 84L4 90Z',GOLD)+line('M5 4V85','#B58E39',3),j*72*a,0,(-9 if j%2 else 9)*(1-a)+hinge,max(.025,a))
  # Its segment hinges own motion. Do not apply a global strip collision wiggle.
  return put('paper-gold-history-strip',x,y,body=raw,impact=0)
 def failed_bay(x,y,s=1,roof=True,floor=True):
  raw=PARTS['failed-state-bay']
  if roof:raw+=group(clone(PARTS['coral-replacement-roof'],'archived-coral'),6,39,0,.28)
  if floor:raw+=group(wet_floor(1),10,157,0,.37,id_='interior-floor-strip')
  return put('failed-state-bay',x,y,s,body=raw)
 b=rect(-1000,-1000,2720,3280,'#BBA688')+rect(-1000,-1000,2720,3280,'url(#wallGrain)')+path('M-1000 1022L1720 995V2280H-1000Z','#A99578')
 b+=put('pinboard-seam',44,275)+put('tabletop',0,1009)+'<ellipse cx="368" cy="982" rx="276" ry="21" fill="#202C32" opacity=".12"/>'
 if num==8:b+=put('checkpoint-archive-slot',80,555)
 if num in (1,3,5,6,7):
  b+=put('checkpoint-archive-slot',80,555)
  if num!=3 and num>=5:b+=put('paper-gold-checkpoint-plate',38,605,.43)
  if num==3:
   px=lerp(38,143,phase("checkpoint-capture-control-contact","rowhouse-facade-contact"));py=lerp(605,323,phase("checkpoint-capture-control-contact","rowhouse-facade-contact"));sc=lerp(.43,1.68,phase("checkpoint-capture-control-contact","rowhouse-facade-contact"))
   px=lerp(px,38,phase("paper-gold-checkpoint-plate-impact-plus-1","checkpoint-archive-slot-landing"));py=lerp(py,605,phase("paper-gold-checkpoint-plate-impact-plus-1","checkpoint-archive-slot-landing"));sc=lerp(sc,.43,phase("paper-gold-checkpoint-plate-impact-plus-1","checkpoint-archive-slot-landing"))
   capture=phase("rowhouse-facade-contact","paper-gold-checkpoint-plate-impact")
   body=PARTS['paper-gold-checkpoint-plate']+f'<g opacity="{capture:.6f}">'+PARTS['checkpoint-state-stamp']+'</g>'
   b+=put('paper-gold-checkpoint-plate',px,py,sc,body=body)
  b+=put('rowhouse-facade',173,518)+put('left-keyed-roof-slot',180,514)+put('right-keyed-roof-slot',538,514)
  b+=put('teal-side-gutter',565,514)+put('paper-gold-catch-cup',590,681)
  b+=put('upper-window-flap',442,543,rot=0 if num!=5 else 5*math.exp(-max(0,f-at("upper-window-flap-impact"))/5) if f>=at("upper-window-flap-impact") else 0)
  if num in (1,3):b+=put('interior-floor-strip',205,853)
  if num==7:b+=put('checkpoint-dry-floor-cassette',205,853)
 if num in (1,3,5,6,7):
  if num!=1:b+=put('history-engage-control',84,814,rot=-9)
  if num!=3:b+=put('checkpoint-capture-control',144,814)
  if num in (1,3):b+=put('paper-gold-checkpoint-tab',94,874)
 if num in (5,6,7):
  opening=phase("rain-ribbon-anchor-start","coral-replacement-roof-contact" if num==5 else "teal-original-roof-contact") if num in (5,7) else 0
  gate=rect(28+26*opening,-6,25,12,DARK,2)
  b+=put('test-water-reservoir',427,350,body=PARTS['test-water-reservoir']+gate)
  if num in (5,7):b+=line('M146 321L467 321V350',DARK,4)
 if num==1:
  lift=phase("teal-original-roof-contact","teal-original-roof-stop");descent=phase("teal-original-roof-release","shot-end")
  ox=lerp(138,264,phase("teal-original-roof-contact-plus-15","teal-original-roof-stop"));oy=338-125*lift+112*descent
  rackp=phase("write-latch-release","coral-replacement-roof-stop")
  b+=group(path('M0 0Q123 -29 230 0Q137 60 0 0Z',INK),303,570,0,phase("write-latch-release","teal-original-roof-contact-plus-10"))
  b+=put('write-drive-rack',lerp(450,302,rackp),548)
  b+=put('coral-replacement-roof',lerp(740,315,rackp),452,rot=-2*(1-rackp))
  b+=put('discard-trip-latch',285,575)
  b+=put('teal-original-roof',ox,oy,rot=-3*lift+4*descent)
  b+=put('write-latch',147,761,rot=-27*phase("write-latch-contact","write-latch-release")+9*phase("write-latch-contact-2","coral-replacement-roof-stop"))
  if f>=at("coral-replacement-roof-stop"):b+=rect(174,814,15,12,GOLD,3)
  dormant=PARTS['history-engage-control'].replace(TEAL,'#7B8981') if f<at("history-engage-control-contact") else None
  b+=put('history-engage-control',84,814,rot=-9*phase("history-engage-control-contact","history-engage-control-contact-plus-7"),body=dormant)
  b+=line('M110 839L123 720L294 585',TEAL,6)
  b+=line('M167 806L249 771L275 580L303 560',GOLD,7)
  grips={'r':('write-latch',anchor('write-latch','grip'))} if at("write-latch-contact")<=f<at("write-latch-release") else {'r':('teal-original-roof',anchor('teal-original-roof','eave'))} if at("teal-original-roof-contact")<=f<at("teal-original-roof-release") else {'l':('history-engage-control',anchor('history-engage-control','left-grip'))} if f>=at("history-engage-control-contact") else {}
  if at("write-latch-contact-2")<=f<at("write-latch-release-explicit"):grips['l']=('write-latch',anchor('write-latch','brake-grip'))
  state='focused' if f<at("teal-original-roof-stop") else 'burdened' if f<at("teal-original-roof-release") else 'surprised'
  b+=puppet(185-9*phase("write-latch-contact-2","coral-replacement-roof-stop"),972,state,grips,max(0,(f-at("teal-original-roof-release"))/30) if f>=at("teal-original-roof-release") else None)
 elif num==2:
  catch=phase("teal-original-roof-contact","history-state-original-landing");open_=phase("paper-gold-history-strip-start","paper-gold-history-strip-stop")
  b+=put('rowhouse-facade',175,701,.62,body=clone(PARTS['rowhouse-facade'],'detail-house'))
  b+=put('checkpoint-archive-slot',64,544)
  b+=group(path('M0 0Q123 -29 230 0Q137 60 0 0Z',INK),303,570,0,1-phase("history-state-original-landing","write-drive-rack-contact"))
  b+=put('discard-trip-latch',285,503,rot=10*phase("discard-trip-latch-impact","catch-leaf-spring-release"))
  b+=spring('catch-leaf-spring',124,671,phase("catch-leaf-spring-release","paper-gold-history-strip-start"))
  b+=strip(76,700,open_)
  ox=lerp(264,82,catch);oy=lerp(315+10*phase("local-landmark-0","discard-trip-latch-impact"),459,catch);sc=lerp(1,.64,catch)
  roofmat=matrix(ox,oy,-3+3*catch,sc,sc);anchor=point(roofmat,[30,183])
  # Tongue and eave meet on every owned frame after catch, not just endpoints.
  b+=put('paper-gold-catch-tongue',anchor[0]-175,anchor[1],1)
  b+=put('teal-original-roof',ox,oy,sc,-3+3*catch)
  b+=put('coral-replacement-roof',315,452,1)
  b+=put('write-drive-rack',302,548)
  b+=line('M483 713L507 567',GOLD,7) if f>=at("write-drive-rack-contact") else ''
  b+=put('history-state-original',70,771,.50,body=rect(0,0,300,24,GOLD,7))
  b+=put('history-state-proposed',389,771,.5,body=rect(0,0,300,24,GOLD,7))
 elif num==3:
  rr=phase("teal-original-roof-contact","rowhouse-facade-landing")
  b+=put('teal-original-roof',lerp(82,138,rr),lerp(459,338,rr),lerp(.64,1,rr))
  b+=put('coral-replacement-roof',582,794,.25)
  tabx=144-38*phase("checkpoint-capture-control-contact","paper-gold-checkpoint-plate-impact")+38*phase("paper-gold-checkpoint-plate-impact-plus-1","checkpoint-archive-slot-landing")
  b+=put('checkpoint-capture-control',tabx,814)
  present=phase("checkpoint-capture-control-contact","rowhouse-facade-contact")*(1-phase("paper-gold-checkpoint-plate-impact-plus-1","checkpoint-archive-slot-landing"))
  cx=lerp(40,390,present);cy=lerp(836,950,present)
  b+=put('checkpoint-dry-floor-cassette',cx,cy,.43)
  b+=put('dry-cassette-latch',cx-19,cy-7,.65,rot=65*(1-phase("rowhouse-facade-contact","paper-gold-checkpoint-plate-impact")))
  b+=put('capture-pressure-cam',lerp(95,463,phase("rowhouse-facade-contact","paper-gold-checkpoint-plate-impact")),497,.6,rot=360*phase("rowhouse-facade-contact","paper-gold-checkpoint-plate-impact"))
  b+=put('checkpoint-drive-latch',82,750,.65,rot=12*phase("checkpoint-archive-slot-landing","checkpoint-capture-control-release-plus-1"))
  b+=spring('comparison-leaf-spring',95,925,1-phase("checkpoint-archive-slot-landing","checkpoint-capture-control-release-plus-5"))
  b+=line('M168 839L175 730L208 529',GOLD,5)
  grips={'r':('teal-original-roof',anchor('teal-original-roof','eave'))} if at("teal-original-roof-contact")<=f<at("teal-original-roof-release") else {'r':('checkpoint-capture-control',anchor('checkpoint-capture-control','right-grip'))} if at("checkpoint-capture-control-contact")<=f<at("checkpoint-capture-control-release") else {}
  b+=puppet(185-17*phase("checkpoint-capture-control-contact","paper-gold-checkpoint-plate-impact"),972,'focused',grips)
 elif num==4:
  ex=phase("comparison-drive-rack-start","rowhouse-facade-landing")
  b+=put('paper-gold-checkpoint-plate',33,563,.95)
  move=phase("teal-original-roof-handoff","rowhouse-facade-landing");hx=lerp(173,420,move);hy=518;hs=1
  b+=put('rowhouse-facade',hx,hy,hs)
  b+=put('left-keyed-roof-slot',hx+7*hs,hy-4*hs,hs)+put('right-keyed-roof-slot',hx+365*hs,hy-4*hs,hs)
  b+=put('interior-floor-strip',hx+32*hs,hy+335*hs,hs)
  b+=spring('comparison-leaf-spring',123,916,ex)
  b+=put('comparison-drive-rack',212,829)
  b+=line('M230 839L181 593M432 839L504 611',GOLD,8)
  rack_support=point(mats['comparison-drive-rack'],anchor('comparison-drive-rack','coral-clevis'));house_support=point(mats['rowhouse-facade'],anchor('rowhouse-facade','base-support'))
  b+=line(f'M{rack_support[0]} {rack_support[1]}L{house_support[0]} {house_support[1]}',GOLD,6)
  b+=put('teal-original-roof',lerp(138,-75,phase("teal-original-roof-handoff","paper-gold-checkpoint-plate-landing")),338-12*phase("left-keyed-roof-slot-release","teal-original-roof-handoff")*(1-phase("teal-original-roof-handoff","paper-gold-checkpoint-plate-landing")))
  b+=put('coral-replacement-roof',lerp(589,385,phase("coral-replacement-roof-handoff","rowhouse-facade-landing")),lerp(389,458,phase("coral-replacement-roof-handoff","rowhouse-facade-landing")))
  clevis=point(mats['comparison-drive-rack'],anchor('comparison-drive-rack','teal-clevis'));eave=point(mats['teal-original-roof'],anchor('teal-original-roof','eave'))
  end=[lerp(clevis[0],eave[0],phase("comparison-drive-rack-start","teal-original-roof-contact")),lerp(clevis[1],eave[1],phase("comparison-drive-rack-start","teal-original-roof-contact"))]
  b+=line(f'M{clevis[0]} {clevis[1]}L{end[0]} {end[1]}',GOLD,8)
  b+=group(line('M-12 -6V10H12V-6',DARK,5),end[0],end[1])
  coral_clevis=point(mats['comparison-drive-rack'],anchor('comparison-drive-rack','coral-clevis'));coral_key=point(mats['coral-replacement-roof'],anchor('coral-replacement-roof','left-key'))
  b+=line(f'M{coral_clevis[0]} {coral_clevis[1]}L{coral_key[0]} {coral_key[1]}',GOLD,6)
  b+=strip(70,946,1)
 elif num==5:
  b+=put('coral-replacement-roof',138,458)
  b+=put('test-ribbon-guide',223,301)
  b+=rect(320,340,156,288,'#A6E5D6',10).replace('fill=','opacity=".13" fill=',1)
  b+=put('rain-ribbon-anchor',124,lerp(590,711,phase("rain-ribbon-anchor-start","rain-ribbon-anchor-release")))
  b+=line(f'M146 321V{lerp(590,711,phase("rain-ribbon-anchor-start","rain-ribbon-anchor-release"))+7}',INK,5)
  b+=put('paper-gold-checkpoint-tab',94,874)
  wet=phase("interior-floor-strip-impact","floor-sag-stop-stop")
  b+=put('interior-floor-strip',205,853,body=wet_floor(wet))
  floor_matrix=mats['interior-floor-strip'];saddle=point(floor_matrix,[0,26]);angle=math.degrees(math.atan2(floor_matrix[1],floor_matrix[0]))
  b+=put('floor-shuttle',saddle[0],saddle[1],rot=angle)
  roof_tip=point(mats['coral-replacement-roof'],anchor('coral-replacement-roof','leak-notch'));window_tip=point(mats['upper-window-flap'],anchor('upper-window-flap','water-contact'));floor_tip=point(mats['interior-floor-strip'],anchor('interior-floor-strip','water-contact'))
  if f<at("coral-replacement-roof-contact"):tip=[roof_tip[0],lerp(350,roof_tip[1],phase("rain-ribbon-anchor-start","coral-replacement-roof-contact"))]
  elif f<at("coral-replacement-roof-release"):tip=roof_tip
  elif f<at("upper-window-flap-impact"):tip=[lerp(roof_tip[0],window_tip[0],phase("coral-replacement-roof-release","upper-window-flap-impact")),lerp(roof_tip[1],window_tip[1],phase("coral-replacement-roof-release","upper-window-flap-impact"))]
  else:tip=[lerp(window_tip[0],floor_tip[0],phase("upper-window-flap-impact","interior-floor-strip-impact")),lerp(window_tip[1],floor_tip[1],phase("upper-window-flap-impact","interior-floor-strip-impact"))]
  if f<at("rain-ribbon-anchor-start"):b+=put('test-water-slug',467-23*.91,350-70*.91,.91)
  if f>=at("rain-ribbon-anchor-start"):
   squash=.62 if at("coral-replacement-roof-contact")<=f<at("coral-replacement-roof-release") or at("upper-window-flap-impact")<=f<at("upper-window-flap-impact-plus-2") else .91
   b+=put('test-water-slug',tip[0]-23*.91,tip[1]-70*squash,.91,sy=squash)
   if f in (at("coral-replacement-roof-contact"),at("upper-window-flap-impact"),at("interior-floor-strip-impact")):CONTACTS.append({'shot':sid,'frame':global_frame,'hand':'water-tip','prop':'coral-roof/window/floor','world_anchor':tip,'world_hand':point(mats['test-water-slug'],[23,70]),'error_authoring_px':__import__('math').dist(tip,point(mats['test-water-slug'],[23,70]))})
  b+=put('floor-sag-stop',335,897,.6)
  grips={'r':('rain-ribbon-anchor',anchor('rain-ribbon-anchor','grip'))} if at("rain-ribbon-anchor-contact")<=f<at("rain-ribbon-anchor-release") else {}
  b+=puppet(176-11*phase("rain-ribbon-anchor-start","rain-ribbon-anchor-release"),979,'focused' if f<at("upper-window-flap-impact") else 'worried',grips)
 elif num==6:
  pull=phase("paper-gold-checkpoint-tab-contact","carriage-stop-stop");a=phase("rollback-roof-unlock","coral-replacement-roof-handoff");z=phase("teal-roof-restore-start","rowhouse-facade-landing");wetmove=phase("coral-replacement-roof-handoff","interior-floor-strip-handoff");drymove=phase("checkpoint-dry-floor-cassette-handoff","live-floor-mounts-landing")
  b+=failed_bay(574,752,.82,False,False)
  b+=strip(80,944,1)
  b+=put('paper-gold-rollback-carriage',83-35*pull,791)
  fs=lerp(1,.31,wetmove);fy=lerp(853,881,wetmove)
  b+=put('coral-replacement-roof',lerp(138,581,a),lerp(458,784,a),lerp(1,.26,a),rot=2*a)
  clevis=point(mats['paper-gold-rollback-carriage'],anchor('paper-gold-rollback-carriage','right-output'));key=point(mats['coral-replacement-roof'],anchor('coral-replacement-roof','left-key'))
  b+=line(f'M{clevis[0]} {clevis[1]}L{key[0]} {key[1]}',GOLD,5)
  b+=put('interior-floor-strip',lerp(205,583,wetmove),lerp(853,881,wetmove),lerp(1,.31,wetmove),body=wet_floor(1))
  floor_matrix=mats['interior-floor-strip'];saddle=point(floor_matrix,[0,26]);angle=math.degrees(math.atan2(floor_matrix[1],floor_matrix[0]))
  b+=put('floor-shuttle',saddle[0],saddle[1],fs,rot=angle)
  supported=point(mats['floor-shuttle'],anchor('floor-shuttle','wet-saddle'));wanted=point(floor_matrix,anchor('interior-floor-strip','wet-support'))
  CONTACTS.append({'shot':sid,'frame':global_frame,'hand':'floor-support','prop':'interior-floor-strip','world_anchor':wanted,'world_hand':supported,'error_authoring_px':math.dist(wanted,supported)})
  b+=put('teal-original-roof',lerp(54,138,z),lerp(610,338,z),lerp(.45,1,z),-4*(1-z))
  retained_key=point(mats['teal-original-roof'],anchor('teal-original-roof','eave'));retained_drive=point(mats['paper-gold-rollback-carriage'],anchor('paper-gold-rollback-carriage','left-output'))
  b+=line(f'M{retained_drive[0]} {retained_drive[1]}L{retained_key[0]} {retained_key[1]}',GOLD,5)
  b+=put('checkpoint-dry-floor-cassette',lerp(40,205,drymove),lerp(836,853,drymove),lerp(.43,1,drymove))
  b+=put('live-floor-mounts',205,873)+put('carriage-stop',339,808,.5)
  b+=put('rain-ribbon-anchor',124,lerp(711,590,pull))
  # The rollback take-up cable visibly retrieves the same slug, keeping the wet
  # floor's state intact. It remains stored above the guide through the next cut.
  floor_tip=point(mats['interior-floor-strip'],anchor('interior-floor-strip','water-contact'))
  retrieval=phase("test-water-slug-contact-explicit","interior-floor-strip-handoff-minus-10");tip=[lerp(floor_tip[0],467,retrieval),lerp(floor_tip[1],350,retrieval)]
  secondary=put('test-take-up-cable',tip[0],tip[1],body=line(f'M0 0L{467-tip[0]} {350-tip[1]}',TEAL,3))
  secondary+=put('test-water-slug',tip[0]-23*.91,tip[1]-70*.91,.91)
  b+='<g opacity=".45" data-role="secondary-test-reset">'+secondary+'</g>'
  b+=put('paper-gold-checkpoint-tab',94-36*pull,874)
  b+=line(f'M86 899L{218-35*pull:.3f} 810L{218-35*pull:.3f} 879',GOLD,7)+line('M224 810L260 536',GOLD,6)
  grips={'r':('paper-gold-checkpoint-tab',anchor('paper-gold-checkpoint-tab','right-grip')),'l':('paper-gold-checkpoint-tab',anchor('paper-gold-checkpoint-tab','left-grip'))} if at("paper-gold-checkpoint-tab-contact")<=f<at("paper-gold-checkpoint-tab-release") else {}
  b+=puppet(183-31*pull,979,'burdened' if f<at("paper-gold-checkpoint-tab-release") else 'relieved',grips,max(0,(f-at("paper-gold-checkpoint-tab-release"))/30) if f>=at("paper-gold-checkpoint-tab-release") else None)
 elif num==7:
  b+=put('teal-original-roof',138,338)+failed_bay(574,752,.82)
  b+=put('test-ribbon-guide',223,301)
  b+=rect(320,340,156,288,'#A6E5D6',10).replace('fill=','opacity=".13" fill=',1)
  b+=put('rain-ribbon-anchor',124,lerp(590,711,phase("rain-ribbon-anchor-start","rain-ribbon-anchor-release")))
  b+=line(f'M146 321V{lerp(590,711,phase("rain-ribbon-anchor-start","rain-ribbon-anchor-release"))+7}',INK,5)
  roof_tip=point(mats['teal-original-roof'],anchor('teal-original-roof','rain-contact'))
  gutter_tip=point(mats['teal-side-gutter'],anchor('teal-side-gutter','water-contact'))
  cup_tip=point(mats['paper-gold-catch-cup'],anchor('paper-gold-catch-cup','water-contact'))
  if f<at("teal-original-roof-contact"):tip=[roof_tip[0],lerp(350,roof_tip[1],phase("rain-ribbon-anchor-start","teal-original-roof-contact"))]
  elif f<at("teal-side-gutter-handoff"):tip=[lerp(roof_tip[0],gutter_tip[0],phase("teal-original-roof-contact","teal-side-gutter-handoff")),lerp(roof_tip[1],gutter_tip[1],phase("teal-original-roof-contact","teal-side-gutter-handoff"))]
  else:tip=[lerp(gutter_tip[0],cup_tip[0],phase("teal-side-gutter-handoff","paper-gold-catch-cup-landing")),lerp(gutter_tip[1],cup_tip[1],phase("teal-side-gutter-handoff","paper-gold-catch-cup-landing"))]
  if f<at("rain-ribbon-anchor-start"):b+=put('test-water-slug',467-23*.91,350-70*.91,.91)
  if f>=at("rain-ribbon-anchor-start"):
   b+=put('test-water-slug',tip[0]-23*.91,tip[1]-70*.91,.91)
   if f in (at("teal-original-roof-contact"),at("teal-side-gutter-handoff"),at("paper-gold-catch-cup-landing")):
    CONTACTS.append({'shot':sid,'frame':global_frame,'hand':'water-tip','prop':'teal-roof/gutter/cup','world_anchor':tip,'world_hand':point(mats['test-water-slug'],[23,70]),'error_authoring_px':math.dist(tip,point(mats['test-water-slug'],[23,70]))})
  b+=put('paper-gold-checkpoint-tab',94,874)
  b+=put('return-drive-lever',124,782,.75,rot=15*phase("return-drive-lever-contact","return-drive-flywheel-release"))
  b+=put('return-drive-flywheel',319,922,.6,rot=200*phase("return-drive-flywheel-release","shot-end"))
  b+=line('M138 811L239 960L340 947',GOLD,6)
  grips={'r':('rain-ribbon-anchor',anchor('rain-ribbon-anchor','grip'))} if at("rain-ribbon-anchor-contact")<=f<at("rain-ribbon-anchor-release") else {'l':('return-drive-lever',anchor('return-drive-lever','grip'))} if at("return-drive-lever-contact")<=f<at("return-drive-lever-release") else {}
  b+=puppet(176-8*phase("rain-ribbon-anchor-start","rain-ribbon-anchor-release")-340*phase("offscreen-left-start","local-landmark-94"),979,'focused' if f<at("teal-side-gutter-handoff") else 'relieved',grips,max(0,(f-at("teal-side-gutter-handoff"))/30) if f>=at("teal-side-gutter-handoff") else None)
 elif num==8:
  show=phase("paper-gold-history-strip-start","failed-display-stop-landing");back=phase("return-cam-apex-contact","rowhouse-facade-landing")
  b+=put('rowhouse-facade',173,518)
  b+=put('teal-original-roof',138,338)
  b+=put('checkpoint-dry-floor-cassette',205,853)
  b+=put('teal-side-gutter',565,514)+put('paper-gold-catch-cup',590,681)
  cup_tip=point(mats['paper-gold-catch-cup'],anchor('paper-gold-catch-cup','water-contact'))
  b+=put('test-water-slug',cup_tip[0]-23*.91,cup_tip[1]-70*.91,.91)
  px=lerp(38,-100,phase("paper-gold-history-strip-start","checkpoint-display-stop-landing"));px=lerp(px,97,phase("return-cam-apex-contact","rowhouse-facade-landing"))
  # Only roof profile and floor bar remain visible on the two reduced bays.
  prof=cut('M0 0L203 0L203 338L0 338Z',GOLD)+group(clone(PARTS['teal-original-roof'],'checkpoint-profile'),5,18,0,.40)+rect(14,275,171,26,CREAM,4)
  fold=lerp(1,.10,phase("checkpoint-archive-slot-handoff","rowhouse-facade-landing"))
  b+=put('paper-gold-checkpoint-plate',px,lerp(430,630,phase("checkpoint-archive-slot-handoff","rowhouse-facade-landing")),fold,body=prof,sy=1)
  bx=lerp(574,623,phase("paper-gold-history-strip-start","failed-display-stop-landing"));bx=lerp(bx,99,phase("return-cam-apex-contact","checkpoint-archive-slot-landing"))
  # The same failed roof and wet-floor identities stay owned by this bay.
  raw=cut('M0 0L203 0L203 338L0 338Z',GOLD)+group(clone(PARTS['coral-replacement-roof'],'retained-coral'),5,40,0,.40)+group(wet_floor(1),9,267,0,.54,id_='interior-floor-strip')
  fold=lerp(1,.10,phase("checkpoint-archive-slot-handoff","checkpoint-archive-slot-landing"))
  b+=put('failed-state-bay',bx,lerp(430,630,phase("checkpoint-archive-slot-handoff","checkpoint-archive-slot-landing")),fold,body=raw,sy=1)
  seated=phase("checkpoint-archive-slot-landing","rowhouse-facade-landing");seat=point(mats['rowhouse-facade'],anchor('rowhouse-facade','archive-seat'))
  b+=strip(lerp(80,seat[0],seated),lerp(945,seat[1],seated),1,seated)
  b+=put('return-drive-flywheel',319,922,.6,rot=200+250*phase("paper-gold-history-strip-start","return-cam-follower-stop"))
  b+=put('return-cam-apex',370,920,.7,rot=180*phase("paper-gold-history-strip-start","return-cam-follower-stop"))
  b+=put('return-cam-follower',408,957,.65,rot=7*math.sin(math.pi*phase("paper-gold-history-strip-start","return-cam-follower-stop")))
  b+=put('checkpoint-display-stop',93,780,.45)+put('failed-display-stop',622,780,.45)
  b+=line('M338 944L250 846L93 780M396 940L509 839L622 780',GOLD,5)
 missing={x['id'] for x in q['reaction_radius']['targets']}-set(positions)
 if missing:raise ValueError('unsupported selected response '+sid+': '+str(missing))
 BINDINGS.append({'shot':sid,'frame':global_frame,'actual_part_positions':positions,'reaction_targets_bound':responded,'performance':q['performance']['state']})
 # Accents belong to declared contacts and clear within five frames.
 accents=[e for e in shot['events'] if e['kind'] in ('impact','landing') and 0<=f-e['local_frame']<5]
 for e in accents[:1]:
  pos=positions.get(e['target'],[360,540]);a=1-(f-e['local_frame'])/5
  b+=group(line('M-19 -13L-29 -24M0 -19V-34M18 -14L30 -25',CORAL if num==5 else GOLD,4),pos[0]+28,pos[1],0,a)
 if shot.get('camera'):
  camera=shot['camera'];zoom=1
  if num==4:zoom=lerp(1,camera['wide_scale'],phase(camera['start'],camera['wide']))
  elif num==8:zoom=1-(1-camera['wide_scale'])*phase(camera['start'],camera['wide'])*(1-phase(camera['return_start'],camera['return_end']))
  # One projection affects the entire scene, including tabletop and hardware.
  # Persistent house and roof geometry retain their world size.
  b=rect(0,0,720,1280,'#BBA688')+f'<g transform="translate(360 850) scale({zoom:.6f}) translate(-360 -850)">'+b+'</g>'
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
 for i in range(1,count):ev.append({'time':i/30,'target':'#captions-world','action':'SET','params':{'props':{'innerHTML':namespace(captions_frame(groups,i,fnt),'captions')}}})
 return write_composition(P,'captions',count/30,first,ev,LOCAL_DEFS)

def build(create=False):
 global PARTS,CONTACTS,BINDINGS,ANCHORS
 plan=read(P/'production-plan.json');plan_check(plan);validate_timing(plan)
 if not (P/'quality-direction.json').exists() or not read(P/'quality-direction.json')['pass']:
  raise ValueError('Pre-animation direction blocks this production; inspect quality-direction.json. No replan or regeneration occurred.')
 if create:create_asset()
 direction=read(P/'quality-direction-record.json')
 if direction['plan_sha256']!=sha(P/'production-plan.json') or direction['response_sha256']!=sha(P/'quality-direction.json'):
  raise ValueError('pre-animation direction review is stale')
 registry=read(P/'source/registered-bindings.json')
 if registry['adapter_sha256']!=sha(P/'source/build.py') or registry['asset_sha256']!=sha(P/'assets/props/reversible-rowhouse-folio.svg') or registry['timing_sha256']!=sha(P/'source/timing.py'):
  raise ValueError('production capability registration is stale')
 shared=read(ROOT/'quality/bindings.json')
 if registry.get('channel_capability')!='high-energy paper' or shared['performance']['high-energy paper']!=['bot'] or 'actual persistent prop names' not in shared['reaction']['high-energy paper']:
  raise ValueError('registered high-energy paper channels unavailable')
 for i,shot in enumerate(plan['shots']):
  binding=registry['action_bindings'].get(shot['action_binding'],{})
  if binding.get('shot_id')!=shot['id'] or binding.get('events_source')!='production-plan.json' or binding.get('events_pointer')!=f'/shots/{i}/events' or 'exact_events' in binding:
   raise ValueError('action binding does not reference the authoritative shot events')
  if binding.get('framing')!=shot['quality']['framing'] or binding.get('focal_target')!=shot['quality']['focal_target']:
   raise ValueError('unsupported framing/focus for this finite action; explicit development required')
 ANCHORS=read(P/'assets/props/reversible-rowhouse-folio.json')['local_anchors']
 for shot in plan['shots']:
  for event in shot['events']:
   for ref in event.get('anchor_refs',[]):
    if ref['part'] not in registry['persistent_parts'] or ref['anchor'] not in ANCHORS.get(ref['part'],{}):
     raise ValueError('unregistered event contact anchor: '+ref['part']+'.'+ref['anchor'])
 PARTS=load_parts();CONTACTS=[];BINDINGS=[];all_events=[];initial=[];frames=[];evidence_shots=[]
 for shot in plan['shots']:
  start,end=shot['startFrame'],shot['endFrame'];count=end-start;id_=shot['id']
  sequence=[frame(shot,i,count,start+i) for i in range(count)]
  events=[{'time':i/30,'target':'#'+id_+'-world','action':'SET','params':{'props':{'innerHTML':namespace(sequence[i],id_)}}} for i in range(1,count)]
  spec=write_composition(P,id_,count/30,sequence[0],events,DEFS)
  frames.append({'id':id_,'start':start/30,'duration':count/30,'source':'compositions/'+id_+'.html'})
  initial+=spec['initial'];all_events +=[{**e,'time':round(e['time']+start/30,6),'composition':id_} for e in events]
  contacts=[{'time':(start+e['local_frame'])/30,'kind':e['kind']} for e in shot['events'] if e['kind'] in ('contact','landing','handoff','impact')]
  evidence_shots.append({'id':id_,'startFrame':start,'endFrame':end,'temporal_events':contacts})
  write(P/'review'/(id_+'-before.svg'),{'note':'preview source is frame output, not evidence; actual MP4 will be sampled'} ) if False else None
  for suffix,i in [('before',0),('mid',count//2),('after',count-1)]:
   (P/'review'/(id_+'-'+suffix+'.svg')).write_text('<svg xmlns="http://www.w3.org/2000/svg" width="360" height="640" viewBox="0 0 720 1280"><defs>'+DEFS+'</defs>'+sequence[i]+'</svg>')
   if suffix=='mid':
    import cairosvg;cairosvg.svg2png(url=str(P/'review'/(id_+'-'+suffix+'.svg')),write_to=str(P/'review'/(id_+'-'+suffix+'.png')))
 capspec=captions(plan,None)
 write(P/'scene-events.json',{'schemaVersion':'1.0','fps':30,'durationSec':plan['targetFrames']/30,'initial':initial,'events':sorted(all_events,key=lambda e:e['time']),'shots':frames})
 write(P/'evidence-shots.json',evidence_shots)
 write(P/'quality-bindings.json',{'scope':'production-specific finite adapter; shared performance, inverse grip and selected reaction functions','contract':{'source':'production-plan.json','bindings':'production-specific finite part transforms and exact local-frame events','scopes':{'candidate-reusable':[],'canonical-promoted':[]}},'shots':[{**s,'compiled_frame_count':s['endFrame']-s['startFrame']} for s in plan['shots']],'sampled_bindings':BINDINGS[::30]})
 write(P/'review/contact-audit.json',{'samples':len(CONTACTS),'maximum_error_authoring_px':max([x['error_authoring_px'] for x in CONTACTS] or [0]),'scope':'inverse transform solver mathematical residual; temporal strips verify actual painted continuity','frames':CONTACTS})
 voice=P/'assets/voice/narration-af-nova.wav';d=read(P/'speech-timing.json')['duration']
 # Review-level normalization is existing rough workflow; SFX/final mix gated later.
 review=voice.with_name('review-voice.wav')
 if not review.exists():command(['ffmpeg','-v','error','-y','-i',str(voice),'-af','loudnorm=I=-16:TP=-1.8:LRA=11','-ar','24000','-ac','1',str(review)],P)
 write(P/'audio-plan.json',{'narration':'assets/voice/narration-af-nova.wav','review_input':'assets/voice/review-voice.wav','duration':d,'review_gain_db':0,'music':False,'sfx':False,'subjective_listening':'human required','voice_speed':.85})
 write_index(P,frames,plan['targetFrames']/30,d,0)
 write(P/'pre-render-checks.json',{'status':'DATA_CHECKS_ONLY','plan':plan_check(plan),'exact_script':read(P/'brief.json')['script']==plan['script'],'alignment':'alignment-review.json','contacts':'review/contact-audit.json','unsupported_policy':'fail on unregistered part/reaction or absent Bot','scope':'not creative or painted approval'})
 inputs=['production-plan.json','source/build.py','source/timing.py','source/registered-bindings.json','assets/props/reversible-rowhouse-folio.svg','assets/props/reversible-rowhouse-folio.json','alignment-review.json']
 outputs=['index.html','scene-events.json','quality-bindings.json','evidence-shots.json','caption-events.json']+[str(f.relative_to(P)) for f in sorted((P/'compositions').glob('*.html'))]
 write(P/'compile-record.json',{'inputs':{n:sha(P/n) for n in inputs},'outputs':{n:sha(P/n) for n in outputs},'frames':plan['targetFrames'],'scope':'current compiled source; not rendered quality approval'})
 print('Built',len(frames),'shots',plan['targetFrames'],'frames',flush=True)
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--create-asset',action='store_true');args=a.parse_args();build(args.create_asset)
