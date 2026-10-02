"""Finite paper interactions requested by an original live script plan.

Agent-authored geometry/choreography. No model code executes. Asset text is
illustrative, editable production data. Existing canonical puppet is imported.
"""
import json, math, re, xml.etree.ElementTree as ET
from html import escape
from pathlib import Path
from build_motif_bot import DEFS as BOT_DEFS, assemble_pose, arm
from build_scene_01 import DEFS as SCENE_DEFS
from motif_framing import union, contains, project_box
ROOT=Path(__file__).resolve().parents[1]
KIT=ROOT/'assets/scenes/paper-investigation'
INK='#202C32'; PAPER='#F4EBD8'; EDGE='#DCCDB3'; TEAL='#318E85'; CORAL='#B5573B'; GOLD='#D9B25B'
SAFE=(80,400,920,1110)
KINDS={
 'snap-open-then-buckle-sample-answer':('fold-catch','caught',(),(260,960,710,520),(90,925,910,610),2.0),
 'trace-claim-connector-through-folio':('trace','traced',('caught',),(340,650,640,730),(85,650,915,790),3.4),
 'lift-summary-window-to-compare-source':('compare','compared',('traced',),(320,610,650,690),(140,580,840,830),3.2),
 'expose-and-preserve-evidence-gap':('gap','gap-open',('compared',),(295,690,650,650),(140,650,850,760),4.0),
 'place-cautious-decision-bookmark':('decision','review-needed',('gap-open',),(310,760,650,570),(170,730,820,700),1.15),
 'arrange-exploded-support-chain-for-understanding':('explain','explained',('review-needed',),(245,495,700,945),(90,480,910,1010),3.6),
}
ASSET_IDS=('answer-card','source-leaf','summary-flap','evidence-frame','connector-strip','blank-scrap','decision-bookmark')
def txt(s,x,y,size=48,color=INK,anchor='start',weight=700):
 return f'<text x="{x}" y="{y}" font-family="Inter" font-weight="{weight}" font-size="{size}" text-anchor="{anchor}" fill="{color}">{escape(s)}</text>'
def paper(w,h,color=PAPER):
 d=f'M2 5 L{w*.31} 0 L{w*.64} 3 L{w-2} 1 L{w} {h*.46} L{w-3} {h-1} L{w*.59} {h+2} L{w*.25} {h-2} L0 {h} L3 {h*.51}Z'
 return f'<path d="{d}" transform="translate(6 9)" fill="{INK}" opacity=".16"/><path d="{d}" fill="{color}"/><path d="{d}" fill="url(#paperSpeckle)" opacity=".45"/><path d="M3 {h-2}L{w*.25} {h-4}L{w*.59} {h}L{w-3} {h-3}" stroke="{EDGE}" stroke-width="3"/>'
def make_assets():
 bodies={
 'answer-card':paper(540,380)+txt('SAMPLE · ANSWER',34,62,36)+txt('IT WILL',32,166,92,weight=900)+txt('WORK.',32,265,96,weight=900)+f'<path d="M35 317Q270 324 495 317" stroke="{TEAL}" stroke-width="17" stroke-linecap="round"/>',
 'summary-flap':paper(540,195,GOLD)+txt('SAMPLE · SUMMARY',28,45,34)+txt('WILL',28,153,118,weight=900)+f'<path d="M386 110H494M470 85L498 110L470 135" stroke="{INK}" stroke-width="10" fill="none"/>',
 'source-leaf':paper(540,380)+txt('SAMPLE · ORIGINAL',28,51,34)+txt('MAY',28,175,122,TEAL,weight=900)+txt('in some cases',28,239,51)+f'<path d="M28 279H480M28 309H405M28 339H446" stroke="#ADAB94" stroke-width="9"/>',
 'connector-strip':paper(74,230,TEAL)+f'<path d="M36 15V211" stroke="{PAPER}" stroke-width="6" stroke-dasharray="15 15"/>',
 'blank-scrap':paper(222,180,EDGE)+f'<path d="M33 57H179M33 98H148M33 139H167" stroke="#A79D88" stroke-width="8"/>',
 'decision-bookmark':paper(260,148,CORAL)+txt('NEEDS',130,63,48,PAPER,'middle',900)+txt('REVIEW',130,121,48,PAPER,'middle',900),
 'evidence-frame':f'<path d="M0 0H540V290H0Z M36 42V248H504V42Z" fill="{INK}" opacity=".12" transform="translate(6 8)" fill-rule="evenodd"/><path d="M0 0H540V290H0Z M36 42V248H504V42Z" fill="{PAPER}" fill-rule="evenodd"/>'+txt('SUPPORT',270,34,31,INK,'middle')+f'<path d="M93 128H199 M341 128H447" stroke="{TEAL}" stroke-width="28" stroke-linecap="square"/><path d="M221 87V172 M319 87V172" stroke="{CORAL}" stroke-width="6" stroke-dasharray="12 10"/>'+txt('?',270,149,76,CORAL,'middle'),
 }
 sizes={'answer-card':(550,394),'summary-flap':(550,210),'source-leaf':(550,394),'connector-strip':(85,244),'blank-scrap':(232,194),'decision-bookmark':(270,164),'evidence-frame':(550,304)}
 for name,body in bodies.items():
  w,h=sizes[name];defs=SCENE_DEFS.removeprefix('<defs>').removesuffix('</defs>')
  (KIT/(name+'.svg')).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="Illustrative paper investigation {name}"><title>{name}</title><defs>{defs}</defs>{body}</svg>')
  (KIT/(name+'.json')).write_text(json.dumps({'id':name,'status':'moving-preview; review required','method':'agent-authored editable SVG','style':'reference-expressive-v1','viewBox':[0,0,w,h],'meaning':'illustrative sample; no real source or product claim','layers':'paper edge, contact shadow, quiet surface, editable text or route geometry','shadow':'down-right','production':'confidence-isnt-evidence'},indent=2)+'\n')
 return bodies

def fragment(path):
 s=(ROOT/path).read_text();s=s.split('</defs>',1)[-1].rsplit('</svg>',1)[0];s=re.sub(r'^\s*<svg[^>]*>\s*(?:<title>.*?</title>\s*)?','',s,flags=re.S);return s

def unique(body,prefix): return re.sub(r'id="([^"]+)"',lambda m:f'id="{prefix}-{m[1]}"',body)
def put(body,x,y,scale=1,rotation=0,scale_y=1): return f'<g transform="translate({x:.3f} {y:.3f}) rotate({rotation:.3f}) scale({scale:.5f} {scale*scale_y:.5f})">{body}</g>'
def point(x,y,px,py,angle=0,scale=1):
 a=math.radians(angle); return (x+scale*(px*math.cos(a)-py*math.sin(a)),y+scale*(px*math.sin(a)+py*math.cos(a)))
def camera(kind, framing):
 _,_,_,box,critical,_=KINDS[kind];sx,sy,sw,sh=SAFE
 if framing=='establish': box=union(box,critical)
 padding={'establish':1.03,'subject':1.18,'detail':1.02}[framing]
 scale=min(sw/(box[2]*padding),sh/(box[3]*padding),sw/(critical[2]+24),sh/(critical[3]+24),2)
 x=sx+sw/2-(box[0]+box[2]/2)*scale; y=sy+sh/2-(box[1]+box[3]/2)*scale
 x=max(sx-critical[0]*scale,min(x,sx+sw-(critical[0]+critical[2])*scale));y=max(sy-critical[1]*scale,min(y,sy+sh-(critical[1]+critical[3])*scale))
 cam={'x':round(x,3),'y':round(y,3),'scale':round(scale,6),'svgOrigin':'0 0'}
 assert contains(SAFE,project_box(critical,cam),1)
 return {'camera':cam,'target_bounds':box,'critical_bounds':critical,'projected_critical_bounds':project_box(critical,cam),'framing':framing,'safe_area':SAFE}

def build_scene(prefix,kind,action_time,end,framing,assets):
 """Build-time finite SVG states compiled as SET/TWEEN through Motif's engine."""
 mode,_,_,_,_,dur=KINDS[kind];dur=min(dur,end-action_time-.12)
 if dur<=.7: raise ValueError('speech leaves insufficient physical-action time: '+kind)
 events=[]; initial=[]; parts=[];contacts=[]
 def init(id_,**props):initial.append({'target':'#'+prefix+'-'+id_,'props':props})
 def at(t,id_,**props):events.append({'time':round(t,6),'target':'#'+prefix+'-'+id_,'action':'SET','params':{'props':props}})
 def layer(id_,body):parts.append(f'<g id="{prefix}-{id_}" data-layout-allow-overflow>{body}</g>')
 def tween(t,id_,duration,**props):events.append({'time':round(t,6),'target':'#'+prefix+'-'+id_,'action':'TWEEN','params':{'to':props,'duration':duration,'ease':'power2.out'}})
 # Standing miniature Bot on the existing desk; all dynamic grips use canonical arms/hands.
 bx,by,bs=(55,895,.57) if mode in ('fold-catch','trace') else (60,942,.52)
 if mode=='explain':bx,by,bs=(35,998,.48)
 body,items=assemble_pose('standing','thinking',{})
 for side in ('left','right'): body=body.replace(items[side+'-arm'],'').replace(items[side+'-hand'],'')
 botbody=put(unique(body,prefix+'-bot'),bx,by,bs)
 layer('bot',botbody);layer('arms','')
 def arms(left,right):
  value=''
  for side,p in [('left',left),('right',right)]:
   if p is None:p=(bx+(278 if side=='left' else 746)*bs,by+676*bs)
   a,h=arm(side,(p[0]-bx)/bs,(p[1]-by)/bs,'grip' if side=='right' else 'open')
   value+=unique(a+h,prefix+'-arm')
  return put(value,bx,by,bs)
 def frame(t,poses,left=None,right=None):
  for name,value in poses.items():
   asset,x,y,s,a,*extra=value
   at(t,name,innerHTML=put(assets[asset],x,y,s,a,extra[0] if extra else 1))
  at(t,'arms',innerHTML=arms(left,right))
 def track(states):
  frame(0,*states(0))
  for f in range(math.ceil(dur*30)+1):
   q=min(1,f/(dur*30));t=action_time+min(f/30,dur)
   frame(t,*states(q))
  contacts.append({'action':kind,'start':action_time,'complete':action_time+dur,'method':'canonical arm endpoints and carried prop share authored finite poses at 30 fps'})
 # Existing desk and folio cover are actual library fragments, without label substitution.
 desk=put(fragment('assets/scenes/scene-01/furniture/desk.svg'),70,1430,1)
 folioxml=ET.parse(ROOT/'assets/scenes/book-workshop/project-folio-kit.svg').getroot()
 cover=ET.tostring(next(x for x in folioxml if x.get('id')=='cover'),encoding='unicode').replace('ns0:','').replace(':ns0','')
 cover=unique(cover,prefix+'-folio')
 if mode=='fold-catch':
  layer('claim','');layer('base',put(paper(390,36,TEAL),475,1398));init('base',svgOrigin='670 1416')
  tween(action_time+.6,'base',.24,scaleY=.25,rotation=8)
  def states(q):
   if q<.3: p=q/.3; u=1-(1-p)**3;x=470;y=1340-300*u;a=0;s=.95;sy=.22+.78*u
   else:p=min(1,(q-.3)/.55);u=1-(1-p)**3;x=470-50*u;y=1040+10*u;a=13*u;s=.95;sy=1
   l=point(x,y,20,345*sy,a,s);r=point(x,y,90,330*sy,a,s)
   return ({'claim':('answer-card',x,y,s,a,sy)},l,r)
  track(states)
 elif mode=='trace':
  layer('claim',put(assets['answer-card'],330,685,.78,0));layer('folio',put(cover,365,1088,1.30))
  layer('source','');layer('thread','');init('folio',svgOrigin='700 1270')
  tween(action_time+.28,'folio',.7,rotation=-10,y=70)
  def states(q):
   u=1-(1-q)**3;x=455;y=1290-260*u
   source=put(assets['source-leaf'],x,y,.84)
   # Continuous strip has a fixed anchor on the SAME claim and moving source end.
   thread=f'<path d="M742 966Q986 1030 913 {y+220:.2f}" stroke="{TEAL}" stroke-width="28" fill="none"/><path d="M742 966Q986 1030 913 {y+220:.2f}" stroke="{PAPER}" stroke-width="5" stroke-dasharray="12 12" fill="none"/>'
   at(action_time+q*dur,'thread',innerHTML=thread)
   return ({'source':('source-leaf',x,y,.84,0)},None,(x+8,y+240))
  track(states)
 elif mode=='compare':
  layer('source',put(assets['source-leaf'],340,895,1.05));layer('summary','');layer('hinge',f'<path d="M350 894H878" stroke="{EDGE}" stroke-width="13" stroke-dasharray="18 12"/>')
  # Summary peels upward while the original MAY remains attached at its lower hinge.
  def states(q):
   u=1-(1-q)**3;x=340;y=940-292*u;a=-3*u
   return ({'summary':('summary-flap',x,y,1.05,a)},None,point(x,y,18,170,a,1.05))
  track(states)
 elif mode=='gap':
  layer('source',put(assets['source-leaf'],335,650,.98));layer('frame',put(assets['evidence-frame'],335,1090,.98));layer('scrap','');layer('tab',put(assets['connector-strip'],565,1009,.50))
  # Gap exposes tabletop, not a white filled panel. The unattached scrap is removed.
  def states(q):
   u=1-(1-q)**3;x=495+292*u;y=1040-320*u;a=12*u
   return ({'scrap':('blank-scrap',x,y,.72,a)},None,point(x,y,15,110,a,.72))
  track(states)
 elif mode=='decision':
  layer('source',put(assets['source-leaf'],335,650,.98));layer('frame',put(assets['evidence-frame'],335,1090,.98));layer('scrap',put(assets['blank-scrap'],787,720,.72,12));layer('tab',put(assets['connector-strip'],565,1009,.50));layer('bookmark','')
  def states(q):
   u=1-(1-q)**3;x=286+494*u;y=895+385*u
   return ({'bookmark':('decision-bookmark',x,y,.75,0)},None,(x+4,y+95))
  track(states)
 else:
  layer('claim','');layer('summary','');layer('source','');layer('frame','');layer('bookmark','');layer('thread','')
  def states(q):
   u=1-(1-q)**3
   poses={'claim':('answer-card',450-122*u,565-40*u,.72,0),'summary':('summary-flap',420-58*u,940-140*u,.82,0),'source':('source-leaf',390-14*u,1190-206*u,.78,0),'frame':('evidence-frame',370+58*u,1260+65*u,.64,0),'bookmark':('decision-bookmark',780+15*u,1280+74*u,.64,0)}
   # Final explicit provenance to source, but no connection across the lower evidence gap.
   thread=f'<path d="M{780-122*u:.2f} {809-40*u:.2f}Q970 855 {832-14*u:.2f} {1240-206*u:.2f}" stroke="{TEAL}" stroke-width="17" fill="none"/>'
   at(action_time+q*dur,'thread',innerHTML=thread)
   right=(poses['source'][1]+10,poses['source'][2]+220*.78)
   left=(poses['frame'][1]+199*.64,poses['frame'][2]+128*.64)
   return poses,left,right
  track(states)
 # Put desk behind the Bot and held papers; no extra environment generation.
 backdrop=f'<rect width="1080" height="1920" fill="#BDAE8F"/><rect width="1080" height="1920" fill="url(#wallSurface)" opacity=".25"/>'
 content=desk+''.join(p for p in parts if not p.startswith(f'<g id="{prefix}-arms"'))+next(p for p in parts if p.startswith(f'<g id="{prefix}-arms"'))
 cam=camera(kind,framing);init('camera',**cam['camera'])
 markup=backdrop+f'<g clip-path="url(#action-safe)"><g id="{prefix}-camera" data-layout-allow-overflow>{content}</g></g>'
 return markup,initial,events,contacts,cam
