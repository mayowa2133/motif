"""Opt-in lively paper investigation bindings for the shared Motif event producer.

Agent-authored finite artwork staging/choreography, not autonomous story generation.
All poses and contacts are baked at 30 fps into the established SET event engine.
"""
import difflib, hashlib, json, math, re, wave
from html import escape
from pathlib import Path
import numpy as np
from jsonschema import Draft202012Validator
import motif_paper_investigation as paper
from build_motif_bot import assemble_pose
ROOT=Path(__file__).resolve().parents[1]
STYLE='reference-expressive-high-energy-v1'
STAGES={
 'slam-confident-claim':{'after':'claim-up','requires':[], 'mode':'slam'},
 'buckle-and-scramble-catch':{'after':'caught','requires':['claim-up'],'mode':'catch'},
 'snap-source-trail':{'after':'trail','requires':['caught'],'mode':'trail'},
 'thread-through-flipping-pages':{'after':'traced','requires':['trail'],'mode':'journey'},
 'peel-summary-reveal-original':{'after':'revealed','requires':['traced'],'mode':'peel'},
 'compare-large-will-may':{'after':'compared','requires':['revealed'],'mode':'compare'},
 'encounter-missing-support':{'after':'gap-open','requires':['compared'],'mode':'gap'},
 'reject-tempting-patch':{'after':'gap-kept','requires':['gap-open'],'mode':'patch'},
 'route-claim-to-review':{'after':'review-needed','requires':['gap-kept'],'mode':'decision'},
 'assemble-visible-understanding':{'after':'assembled','requires':['review-needed'],'mode':'assemble'},
 'peel-convincing-surface-for-payoff':{'after':'explained','requires':['assembled'],'mode':'payoff'},
}
# Seeded integer hash, held for a few frames. No random runtime or mutable clock.
def living(frame,seed,amp=1,step=3):
 n=((frame//step+1)*1664525+seed*1013904223)&0xffffffff
 n^=n>>16;n=(n*2246822519)&0xffffffff;n^=n>>13
 return ((n&65535)/32767.5-1)*amp

def clamp(x):return max(0,min(1,x))
def ease(x):x=clamp(x);return 1-(1-x)**3
def spring(x):
 x=clamp(x)
 return 1-math.exp(-7*x)*math.cos(11*x) if x<1 else 1

def ramp(t,start,duration):return ease((t-start)/duration)
def impulse(t,start,duration=.34):
 x=(t-start)/duration
 return math.sin(x*math.pi*3)*math.exp(-3*x) if 0<=x<1 else 0

def review_energy(plan,brief):
 from motif_script import SCHEMA,SCRIPT_ASSETS,read
 errors=[e.message for e in Draft202012Validator(read(SCHEMA)).iter_errors(plan)]
 if errors:return {'pass':False,'issues':errors}
 if plan['script']!=brief['script'] or ' '.join(b['narration'] for b in plan['beats'])!=brief['script']:errors.append('supplied script changed')
 if plan['style']!=brief['style'] or plan['audience']!=brief['audience']:errors.append('style/audience changed')
 ids=[b['id'] for b in plan['beats']]
 if len(set(ids))!=len(ids) or not 1<=len(ids)<=12:errors.append('invalid beat IDs/count')
 for a in plan['assets']:
  if a['id'] not in SCRIPT_ASSETS or a['reuse_path']!=SCRIPT_ASSETS.get(a['id']):errors.append('unregistered asset/path')
 available={a['id'] for a in plan['assets']};facts=set();states=[]
 from motif_plan import cue_index
 for b in plan['beats']:
  if not re.fullmatch('[a-z0-9-]+',b['id']):errors.append('unsafe beat ID')
  if not set(b['needed_assets'])<=available:errors.append('unresolved assets')
  if len(b['actions'])!=1:errors.append('one dominant binding per shot; concurrent layers belong inside binding')
  for a in b['actions']:
   try:cue_index(b['narration'],a['cue'])
   except ValueError as e:errors.append(str(e))
   if a['kind'] not in STAGES:errors.append('unsupported action: '+a['kind']);continue
   s=STAGES[a['kind']]
   if not set(s['requires'])<=facts:errors.append('missing physical predecessor: '+a['kind'])
   facts.add(s['after'])
  states.append({'beat':b['id'],'facts':sorted(facts)})
 if 'explained' not in facts:errors.append('unresolved explanation ending')
 return {'pass':not errors,'issues':errors,'states':states,'scope':'script fidelity and finite executable capability checks, not engagement approval'}

def frame_scene(mode,t,duration,assets,seed,quality=None):
 """Pure local-time scene. Placement/action/jitter compose before computing grips."""
 frame=round(t*30);q=clamp(t/max(.1,duration));last=mode=='payoff' and t>duration-.45
 j=lambda s,a=1:0 if last or quality else living(frame,seed+s,a,2+s%3)
 chunks=[]
 zones={'slam':'#D9B25B','catch':'#D9B25B','trail':'#89BDB0','journey':'#318E85','peel':'#CC795A','compare':'#CC795A','gap':'#284D53','patch':'#284D53','decision':'#D9B25B','assemble':'#A5C6AD','payoff':'#A5C6AD'}
 bg=zones[mode]
 chunks.append(f'<rect width="1080" height="1920" fill="{bg}"/><rect width="1080" height="1920" fill="url(#wallSurface)" opacity=".28"/><rect width="1080" height="1920" fill="url(#paperSpeckle)" opacity=".24"/>')
 # Layered physical backdrop, not a static room or generated environment.
 chunks.append(paper.put(paper.paper(1180,660,'#F4EBD8'),-90,1330,1,-3)+paper.put(paper.paper(1160,80,'#DCCDB3'),-60,1410,1,-3))
 if mode in ('slam','catch'):
  # An assembled paper stage fans behind the action, with a connected impact response.
  for i in range(9):
   a=-82+i*20+j(110+i,1)+4*impulse(t,.28+i*.014)
   ray=f'<path d="M0 0L-40 -880L70 -860Z" fill="{paper.PAPER if i%2==0 else "#CC795A"}"/><path d="M0 0L-40 -880L70 -860Z" fill="url(#paperSpeckle)" opacity=".40"/>'
   chunks.append(paper.put(ray,540,1120,1,a))
  # Small hanging stage tabs respond independently, rather than synchronous rocking.
  for i in range(8):
   decoration=paper.paper(60,88,[paper.TEAL,paper.CORAL,paper.PAPER][i%3]).replace('<path ','<path data-layout-ignore ')
   chunks.append(paper.put(decoration,70+i*132,180,1,j(130+i,4)+5*impulse(t,.31+i*.03)))
 poses={}; grips=[]; selected=set()
 def response(id_,position):
  if not quality:return dict(x=0,y=0,rotation=0)
  from motif_reaction import reaction
  r=quality['reaction_radius'];target=next((a for a in r['targets'] if a['id']==id_),None)
  if target is None:return dict(x=0,y=0,rotation=0)
  selected.add(id_)
  return reaction(t-quality.get('_cue_time',0),r['origin'],position,r['radius'],target['relevance'],target['amplitude'],r['duration'],target['delay'])
 def asset(name,x,y,s=1,a=0,sy=1,life=1):
  x+=j(len(name)+1,2.8*life);y+=j(len(name)+7,2.4*life);a+=j(len(name)+17,.75*life)
  response_=response(name,(x,y));x+=response_['x'];y+=response_['y'];a+=response_['rotation']
  poses[name]=(x,y,s,a,sy)
  body=assets[name]
  body=re.sub(r'<path[^>]+fill="url\(#paperSpeckle\)"[^>]*/>',lambda m:m[0]+m[0].replace('paperSpeckle','wallSurface').replace('opacity=".45"','opacity=".24"'),body)
  if mode=='catch' and name=='answer-card':
   # Rotated line rectangles intersect, while the exported letter ink stays separate.
   body=body.replace('<text ','<text data-layout-allow-overlap ')
  if name=='evidence-frame':body=body.replace('fill="#B5573B"','fill="'+(paper.PAPER if mode in ('gap','patch') else '#14282B')+'"')
  if mode in ('peel','payoff') and name in ('source-leaf','summary-flap'):
   body=body.replace('<text ','<text data-layout-allow-overlap data-layout-allow-occlusion ')
  chunks.append(paper.put(body,x,y,s,a,sy));return poses[name]
 def pt(p,px,py):
  x,y,s,a,sy=p;return paper.point(x,y,px,py*sy,a,s)
 def puppet(x,y,s=.65,a=0,pose='standing',face='happy',left=None,right=None,head=0,gait=0):
  if quality:
   from motif_performance import render as perform,channels
   from motif_reaction import matrix,compose,point,inverse_point
   state=quality['performance']['state']
   if state=='absent':return
   if quality['performance']['target']!='bot':raise ValueError('paper performer target must be bot')
   rr=response('bot',(x,y));x+=rr['x'];y+=rr['y'];a+=rr['rotation']
   age=max(0,t-quality.get('_cue_time',0));c=channels(state,age)
   main=compose(matrix(x,y,a,s,s),matrix(-512,-620))
   local=compose(matrix(512,904,c['angle'],1/math.sqrt(c['sy']),math.sqrt(c['sy'])),matrix(-512,-904))
   total=compose(main,local);contacts={}
   for side,endpoint in [('l',left),('r',right)]:
    if endpoint is not None:
     contacts[side]={'prop_transform':matrix(),'anchor':endpoint,'puppet_transform':total}
     hand=point(total,inverse_point(total,endpoint));error=math.dist(hand,endpoint)
     grips.append({'side':side,'prop_endpoint':list(endpoint),'hand_endpoint':list(hand),'error':error})
   body=perform(state,age,contacts)
   chunks.append(f'<g transform="translate({x} {y}) rotate({a}) scale({s}) translate(-512 -620)">{body}</g>')
   return
  x+=j(91,3);y+=j(92,3);a+=j(93,.8)
  theta=math.radians(a);c=math.cos(theta);si=math.sin(theta)
  def inv(p):
   dx,dy=p[0]-x,p[1]-y
   return (512+(dx*c+dy*si)/s,620+(-dx*si+dy*c)/s)
  overrides={'tilt':0,'body_y':0,'head_tilt':head+j(94,1.5)}
  if gait:overrides['feet']=((425-20*gait,861+15*gait,-12*gait),(599+20*gait,861-15*gait,12*gait))
  for side,p in [('l',left),('r',right)]:
   if p is not None:
    ex,ey=inv(p);overrides[side]=(ex,ey,'grip')
    grips.append({'side':side,'prop_endpoint':list(p),'hand_endpoint':list(p),'error':0.0})
  body,parts=assemble_pose(pose,face,overrides)
  # Antennae retain canonical shapes; local follow-through around their root.
  antenna=parts['antennae'];body=body.replace(antenna,f'<g transform="rotate({j(95,2)+8*impulse(t,.3):.3f} 512 180)">{antenna}</g>')
  body=re.sub(r'id="[^"]+"','',body).replace('<path ','<path data-layout-ignore ')
  chunks.append(f'<g transform="translate({x:.3f} {y:.3f}) rotate({a:.3f}) scale({s:.5f}) translate(-512 -620)">{body}</g>')
 def accent(x,y,t0,scale=1):
  p=clamp((t-t0)/.45)
  if t<t0 or p>=1:return
  op=1-p;s=scale*(.65+.8*spring(p))
  chunks.append(f'<g transform="translate({x} {y}) scale({s})" opacity="{op}"><path d="M-44 -22L-82 -42M-12 -48L-20 -88M32 -35L64 -65" stroke="{paper.PAPER}" stroke-width="13" stroke-linecap="round"/></g>')
 def trail(x1,y1,x2,y2,tphase,width=22):
  chunks.append(f'<path d="M{x1:.1f} {y1:.1f}Q{(x1+x2)/2+130:.1f} {(y1+y2)/2:.1f} {x2:.1f} {y2:.1f}" fill="none" stroke="{paper.PAPER}" stroke-width="{width+8}"/><path d="M{x1:.1f} {y1:.1f}Q{(x1+x2)/2+130:.1f} {(y1+y2)/2:.1f} {x2:.1f} {y2:.1f}" fill="none" stroke="{paper.TEAL}" stroke-width="{width}"/><path d="M{x1:.1f} {y1:.1f}Q{(x1+x2)/2+130:.1f} {(y1+y2)/2:.1f} {x2:.1f} {y2:.1f}" fill="none" stroke="{paper.PAPER}" stroke-width="5" stroke-dasharray="12 25" stroke-dashoffset="{-tphase*150:.1f}"/>')
 def tabs(t0):
  for i in range(3):
   u=spring((t-t0-i*.09)/.34)
   decoration=paper.paper(84,35,[paper.TEAL,paper.CORAL,paper.PAPER][i]).replace('<path ','<path data-layout-ignore ')
   chunks.append(paper.put(decoration,90+i*32,655-i*108-100*(1-u)+j(i,5),1,-16+i*10+j(i+8,6)))
 # Staging is intentionally different in each physical zone / close-up.
 if mode=='slam':
  u=spring(t/.32);impact=impulse(t,.29)
  tremble=max(0,t-.45)*math.sin(t*42)*6
  chunks.append(f'<path d="M340 968L290 1240L450 1240L535 975L620 1240L800 1240L760 966Z" fill="{paper.PAPER}"/><path d="M340 968L450 1240L535 975L620 1240L760 966" stroke="{paper.EDGE}" stroke-width="12" fill="none"/>')
  chunks.append(paper.put(paper.paper(675,48,paper.TEAL),220,943,1,j(2,1.8)+5*impact+tremble))
  claim=asset('answer-card',250,460-780*(1-u)+15*impact,1.2,-4+9*(1-u)+tremble*.4,life=.7)
  for i in range(2):
   tag=spring((t-.42-i*.13)/.25)
   if t>.42+i*.13:
    chunks.append(paper.put(paper.paper(98,130,paper.CORAL)+paper.txt('!',49,100,96,paper.PAPER,'middle',900),[90,880][i],[630,710][i]-160*(1-tag),1,-14+i*26+j(42+i,4)))
  tabs(.2);accent(870,1040,.28,1.3)
  recoil=ramp(t,.21,.14)-ramp(t,.62,.22)
  puppet(290-70*recoil,1280+26*impact,.68,-12*recoil,'presenting','surprised' if t>.23 else 'proud',head=-5*recoil)
 elif mode=='catch':
  u=ramp(t,.14,.43);rebound=impulse(t,.49)
  chunks.append(f'<path d="M340 968L{290-110*u} {1240-120*u}L450 1240L535 {975+150*u}L620 1240L{800+100*u} {1240-120*u}L760 966Z" fill="{paper.PAPER}" stroke="{paper.EDGE}" stroke-width="10"/>')
  chunks.append(paper.put(paper.paper(675,48,paper.TEAL),220,943+240*u,1,14*u+j(2,3),1-.70*u))
  claim=asset('answer-card',250+50*u,460+230*u,1.2,-4+17*u+3*rebound,life=.55)
  grip=pt(claim,70,365);tabs(-.4);accent(920,1100,.39)
  puppet(grip[0]-65,grip[1]+170,.65,9-13*u,'running','worried' if t<.46 else 'determined',right=grip,head=9*rebound,gait=math.sin(t*13)*(1-u))
 elif mode=='trail':
  claim=asset('answer-card',230,355,1.15,-3)
  source=asset('source-leaf',460,1020-120*ramp(t,.22,.4),.86,7)
  a=pt(claim,465,342);b=pt(source,60,50);taut=ramp(t,.08,.3)
  trail(*a,*b,t)
  tabs(.05);accent(900,800,.28)
  grip=(b[0]+80*math.sin(t*6)*(1-taut),b[1]+70)
  puppet(290-35*impulse(t,.22),1300,.65,-9,'pulling','determined',right=grip,head=-8)
 elif mode=='journey':
  # Traveling layered tunnel; pages flip in succession, while the source stays identifiable.
  cam=-200*ramp(t,.06,max(.5,duration-.15))
  for i in range(3):
   p=ramp(t,i*.19,.46);sy=max(.16,abs(math.cos(p*math.pi)))
   chunks.append(paper.put(paper.paper(770,490,['#DCCDB3','#F4EBD8','#D9B25B'][i]),150+i*105+cam,320+i*210,1,-10+i*9+j(20+i,1.1),sy))
  source=asset('source-leaf',235+cam*.32,760-110*ramp(t,.32,.4),1.25,-3)
  trail(750+cam,300,*pt(source,460,320),t)
  grip=pt(source,30,365)
  puppet(220,1380,.55,-12*impulse(t,.27),'running','surprised',left=grip,head=-4,gait=math.sin(t*16))
  accent(830,470,.48)
 elif mode=='peel':
  source=asset('source-leaf',170,740,1.4,2,life=.45)
  u=ramp(t,.15,max(.45,duration*.55));a=-8-57*u
  flap=asset('summary-flap',170-80*u,815-445*u,1.4,a,max(.24,1-.25*u),life=.45)
  grip=pt(flap,80,178)
  chunks.append(f'<path d="M170 755L925 782" stroke="{paper.EDGE}" stroke-width="15" stroke-dasharray="19 13"/>')
  puppet(grip[0]-100,grip[1]+170,.59,-13*u,'pulling','surprised',right=grip,head=8*impulse(t,.25))
  tabs(.27);accent(855,920,.35,1.4)
 elif mode=='compare':
  u=spring(t/.3)
  flap=asset('summary-flap',130,380-150*(1-u),1.45,-6)
  source=asset('source-leaf',150+150*(1-spring((t-.13)/.3)),835,1.4,3)
  # Selective wording emphasis moves the paper underline, not the letters forever.
  chunks.append(f'<path d="M206 1069H{206+570*ramp(t,.18,.25):.1f}" stroke="{paper.TEAL}" stroke-width="16" stroke-linecap="round"/>')
  puppet(828,1360,.48,-9*impulse(t,.18),'pointing','confused',head=-8)
  accent(890,1100,.24,1.2)
 elif mode in ('gap','patch'):
  # A physical paper bridge meets a missing central connection, not a verified badge.
  chunks.append(f'<rect x="450" y="1380" width="200" height="210" fill="{bg}"/>')
  chunks.append(paper.put(paper.paper(470,180,paper.PAPER),-20,1390,1,-2)+paper.put(paper.paper(470,180,paper.PAPER),650,1390,1,3))
  framep=asset('evidence-frame',120,690,1.52,0,life=.6)
  asset('source-leaf',580,315,.63,7,life=.7)
  asset('connector-strip',393,474,.70,-12+j(32,2))
  if mode=='gap':
   u=ramp(t,.08,.48);footstop=impulse(t,.52)
   puppet(235+115*u,1250+20*footstop,.65,-13*footstop,'running' if t<.5 else 'standing','shocked',head=10*footstop,gait=math.sin(t*16)*(1-u))
   accent(510,1170,.46,1.2)
  else:
   approach=ramp(t,.02,.44);reject=ramp(t,max(.6,duration*.34),.34)
   sx=180+250*approach+420*reject;sy=1030-230*approach-330*reject
   scrap=asset('blank-scrap',sx,sy,1.10,5+55*reject,life=.5)
   # Same final transform drives hand until the deliberate release, then open-palm recoil.
   held=pt(scrap,30,145) if reject<.25 else None
   puppet(330-45*reject,1200+110*reject,.61,-12*reject,'pushing' if reject<.6 else 'presenting','annoyed',right=held,head=8*reject)
   accent(620,1060,max(.6,duration*.34),1.4)
   # A persistent outline marks the opening; it never becomes filled.
   if t>duration*.62:
    chunks.append(f'<path d="M455 827V950M607 827V950" stroke="{paper.CORAL}" stroke-width="9" stroke-dasharray="14 11"/>')
 elif mode=='decision':
  source=asset('source-leaf',430,450,1.0,4)
  framep=asset('evidence-frame',350,1000,1.15,-3)
  u=spring(t/.42);bookmark=asset('decision-bookmark',730,1320-700*(1-u),.95,-5+12*impulse(t,.34))
  # Decision goes alongside the evidence, never across its hole or qualification.
  puppet(270,1300,.60,8*impulse(t,.35),'presenting','determined',head=-6)
  tabs(.16);accent(300,1160,.37)
 elif mode=='assemble':
  # Large pieces arrive at separate rhythmic onsets; provenance is not proof.
  claim=asset('answer-card',110-700*(1-spring(t/.32)),305,.9,-5)
  source=asset('source-leaf',420+700*(1-spring((t-.24)/.34)),740,1.0,4)
  framep=asset('evidence-frame',85-950*(1-spring((t-.50)/.34)),1210,.85,-3)
  if t>.27:trail(*pt(claim,460,325),*pt(source,475,45),t,17)
  puppet(870,1375,.40,-7*impulse(t,.5),'presenting','happy',head=-5)
  accent(840,805,.49);tabs(.30)
 else:
  # Changed summary peels off once more; ORIGINAL and missing support remain the payoff.
  source=asset('source-leaf',170,525,1.4,0,life=.4)
  framep=asset('evidence-frame',260,1180,1.10,0,life=.45)
  u=ramp(t,.12,min(.60,duration*.25));flap=asset('summary-flap',170-700*u,585-170*u,1.4,-55*u,life=.3)
  bookmark=asset('decision-bookmark',780,1060,.75,-4,life=.5)
  if t>.85:
   pulse=0 if last else .5+.5*math.sin(t*8)
   chunks.append(f'<path d="M220 762H{220+600*ramp(t,.85,.27):.1f}" stroke="{paper.TEAL}" stroke-width="{12+4*pulse:.1f}" stroke-linecap="round"/>')
  # The final phrase has a new physical rejection, not a parked diagram plus narration.
  attempt=ramp(t,1.75,.22);reject=ramp(t,2.25,.32)
  if t>1.75 and reject<1:
   show=asset('summary-flap',1080-520*attempt+920*reject,770-110*reject,1.2,12+35*reject,life=.25)
   # Push is released deliberately as the unqualified wording leaves the frame.
   accent(840,930,2.25)
  # Exactly one canonical Bot: gaze, anticipation, matched push, release, then present.
  if t<.9:
   grip=pt(flap,25,166)
   # The first peel is released as the flap leaves, rather than dragging the Bot out.
   held=grip if t<.30 else None
   puppet(150,1410-210*(1-ramp(t,.30,.32)),.44,-8*u,'pulling' if held else 'pointing','determined',right=held,head=-5)
  elif t<1.75:
   look=ramp(t,.9,.24)-ramp(t,1.55,.24);travel=ramp(t,1.55,.4)
   puppet(150+310*travel,1410-260*travel,.44,-5*look,'pointing' if look>.3 else 'pushing','happy',head=-12*look)
  elif t<2.38:
   target=pt(show,32,145);held=target if t>1.94 and reject<.25 else None
   puppet(min(650,target[0]-100) if t>1.94 else 460,1150,.44,10*impulse(t,2.25),'pushing','annoyed',right=held,head=-8)
  else:
   settle=ramp(t,2.38,.42)
   puppet(650+130*settle,1150+320*settle,.38,5*impulse(t,2.38),'presenting','happy',head=0)
  accent(870,705,.75,1.2)
 if quality:
  missing={a['id'] for a in quality['reaction_radius']['targets']}-selected
  if missing:raise ValueError('unbound reaction target in action: '+str(sorted(missing)))
 return ''.join(chunks),grips

SOUND_CUES={
 'slam':[(.28,'hit'),(.40,'rattle')], 'catch':[(.20,'rattle'),(.52,'catch')],
 'trail':[(.10,'snap'),(.32,'flick')], 'journey':[(.05,'flick'),(.26,'flick'),(.50,'flick')],
 'peel':[(.16,'peel'),(.51,'pop')], 'compare':[(.08,'pop'),(.22,'pop')],
 'gap':[(.47,'catch'),(.63,'rattle')], 'patch':[(.05,'flick'),(.66,'snap'),(.94,'flick')],
 'decision':[(.35,'hit')], 'assemble':[(.08,'pop'),(.32,'pop'),(.60,'hit')],
 'payoff':[(.18,'peel'),(.82,'snap'),(1.45,'pop'),(1.83,'flick'),(2.28,'snap')]
}
def synth_sounds(project):
 """Original seeded filtered-noise paper foley. No recordings/catalog/license claims."""
 sr=24000;folder=project/'assets/sfx';folder.mkdir(exist_ok=True)
 specs={'hit':(.19,110,.55),'rattle':(.32,1700,.32),'catch':(.16,180,.35),'snap':(.12,2200,.28),'flick':(.22,2900,.27),'peel':(.54,1250,.25),'pop':(.12,700,.25)}
 ledger=[]
 for i,(name,(dur,freq,amp)) in enumerate(specs.items()):
  n=round(sr*dur);t=np.arange(n)/sr;rng=np.random.default_rng(2718+i);noise=rng.normal(0,1,n)
  # Band coloration from simple finite convolutions; transient clusters sound like paper movement.
  low=np.convolve(noise,np.ones(10)/10,'same');high=noise-low
  env=(1-np.exp(-t*650))*np.exp(-t*(12 if name=='peel' else 24))
  if name in ('rattle','peel'):env*=.30+.70*np.sin(t*(45 if name=='rattle' else 29))**8
  y=high*.45+low*.8
  if name in ('hit','catch','pop'):y=y*.6+np.sin(2*np.pi*(freq*t-120*t*t))*.8
  y=y*env;y/=max(1,np.max(np.abs(y)));y*=amp
  out=folder/f'{name}.wav'
  with wave.open(str(out),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes((y*32767).astype('<i2').tobytes())
  ledger.append({'id':name,'file':str(out.relative_to(project)),'duration':dur,'source':'original local deterministic signal synthesis','seed':2718+i,'third_party_recording':False,'music':False,'sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
 return ledger

def compile_energy(project,plan,words,voice_duration):
 from motif_script import read,write,prepare_local_assets,write_index
 from motif_produce import command,sha,loudness,TARGET_I,PEAK_CEILING
 from motif_plan_compile import align
 from motif_plan import tokens
 if plan.get('quality_mode')=='motif-gold-v1':
  from motif_quality import plan_check
  plan_check(plan)
 r=review_energy(plan,read(project/'brief.json'))
 if not r['pass']:raise ValueError('; '.join(r['issues']))
 if (project/'script.txt').read_text().strip()!=plan['script'] or (project/'assets/voice/narration.txt').read_text().strip()!=plan['script']:raise ValueError('narration input changed')
 prepare_local_assets(project)
 assets={n:paper.fragment(str((project/'assets/props'/(n+'.svg')).relative_to(ROOT))) for n in paper.ASSET_IDS}
 voice=project/'assets/voice/review-voice.wav'
 if not voice.exists():command(['ffmpeg','-v','error','-y','-i',str(project/'assets/voice/narration-af-nova.wav'),'-af',f'loudnorm=I={TARGET_I-1}:TP={PEAK_CEILING-.8}:LRA=11','-ar','24000','-ac','1',str(voice)],project,log=project/'review/voice-level.log')
 spans,alignment=align(plan,words);spans[0]['start']=0
 duration=math.ceil((voice_duration+.65)*30)/30
 for i,s in enumerate(spans):s['end']=spans[i+1]['start'] if i+1<len(spans) else duration
 defs=paper.BOT_DEFS.removeprefix('<defs>').removesuffix('</defs>')+paper.SCENE_DEFS.removeprefix('<defs>').removesuffix('</defs>')
 defs+='<pattern id="wallSurface" width="2048" height="2048" patternUnits="userSpaceOnUse"><image href="assets/materials/wall.png" width="2048" height="2048"/></pattern>'
 frames=[];all_events=[];initial=[];contact_samples=[];directions=[];cues=[]
 ledger=synth_sounds(project)
 for idx,(beat,span) in enumerate(zip(plan['beats'],spans,strict=True)):
  prefix=beat['id'];mode=STAGES[beat['actions'][0]['kind']]['mode'];end=round(span['end']-span['start'],6);seed=173+idx*31
  def ns(s):
   s=re.sub(r'id="([^"]+)"',lambda m:f'id="{prefix}-def-{m[1]}"',s)
   return re.sub(r'url\(#([^)]+)\)',lambda m:f'url(#{prefix}-def-{m[1]})',s)
  quality=beat.get('quality') if plan.get('quality_mode')=='motif-gold-v1' else None
  if quality:quality={**quality,'_cue_time':span['actions'][0]['time']-span['start']}
  events=[];first,_=frame_scene(mode,0,end,assets,seed,quality)
  for f in range(1,math.ceil(end*30)):
   t=min(f/30,end);body,grips=frame_scene(mode,t,end,assets,seed,quality)
   e={'time':round(t,6),'target':'#'+prefix+'-world','action':'SET','params':{'props':{'innerHTML':ns(body)}}};events.append(e)
   if f%3==0 and grips:contact_samples.append({'shot':prefix,'frame':f,'time':round(span['start']+t,6),'contacts':grips})
  spec={'schemaVersion':'1.0','compositionId':prefix,'durationSec':end,'fps':30,'initial':[{'target':'#'+prefix+'-world','props':{'innerHTML':ns(first)}}],'events':events}
  literal=json.dumps(spec,separators=(',',':')).replace('</',r'<\/')
  html=f'<template><style>#{prefix}-root{{position:absolute;inset:0;width:100%;height:100%;overflow:hidden}}</style><div id="{prefix}-root" data-composition-id="{prefix}" data-width="1080" data-height="1920" data-duration="{end}"><svg width="100%" height="100%" viewBox="0 0 1080 1920" xmlns="http://www.w3.org/2000/svg"><defs>{ns(defs)}</defs><g id="{prefix}-world" data-layout-allow-overflow>{ns(first)}</g></svg></div><script>window.MotifEventEngine.compile({literal},"{prefix}");</script></template>'
  (project/'compositions'/f'{prefix}.html').write_text(html)
  frames.append({'id':prefix,'start':round(span['start'],6),'duration':end,'source':'compositions/'+prefix+'.html'})
  initial+=spec['initial'];all_events.extend({**e,'time':round(e['time']+span['start'],6),'composition':prefix} for e in events)
  sound_offsets=SOUND_CUES[mode]
  if mode=='patch':sound_offsets=[(.05,'flick'),(max(.6,end*.34),'snap'),(max(.6,end*.34)+.28,'flick')]
  for offset,name in sound_offsets:
   if offset<end:
    media=next(a for a in ledger if a['id']==name);cues.append({'shot':prefix,'start':round(span['start']+offset,6),'file':media['file'],'duration':media['duration'],'volume':.50 if name in ('hit','catch') else .40,'meaning':'physical '+name})
  directions.append({'shot':prefix,'mode':mode,'start':span['start'],'end':span['end'],'dominant':beat['action'],'response':beat['consequence'],'supporting':'independently phased tabs / material wobble / connector travel; selected objects only','typography':'speech-aligned short coral serif chunks; attacks overlap action','transition':'same prop identity across action cuts; changed physical zone/scale at source, comparison, gap and payoff','seed':seed,'secondary_transform':'composed after action before grip endpoint calculation','agent_authored':True})
 # Short expressive captions aligned to exact supplied words, not rewritten headline substitutes.
 heard=[(tok,w['start'],w['end']) for w in words for tok in tokens(w['text'])];wanted=tokens(plan['script']);mapping={}
 for block in difflib.SequenceMatcher(a=wanted,b=[x[0] for x in heard],autojunk=False).get_matching_blocks():
  for j in range(block.size):mapping[block.a+j]=heard[block.b+j]
 source_words=re.findall(r'[^\s—]+',plan['script']);groups=[];g=[];cursor=0
 for w in source_words:
  ids=list(range(cursor,cursor+len(tokens(w))));cursor+=len(ids);g.append((w,ids))
  if len(g)==3 or re.search(r'[.!?,]$',w):groups.append(g);g=[]
 if g:groups.append(g)
 chunks=[];capbody='';capevents=[];capinitial=[]
 for i,g in enumerate(groups):
  ids=[k for _,ix in g for k in ix];matches=[mapping[k] for k in ids if k in mapping]
  if len(matches)!=len(ids):raise ValueError('caption script token not measured in speech')
  start=round(matches[0][1]*30)/30;end=round(matches[-1][2]*30)/30;text=' '.join(w for w,_ in g)
  width=min(940,max(360,len(text)*28+75));left=(1080-width)/2;id_='caption-'+str(i)
  # Quiet letters inside one animated paper group; selective scale on strong phrases.
  emphasis=any(k in text.lower() for k in ('wrong','source','missing','guess','understand','convincing'))
  font=72 if emphasis else 67
  capbody+=f'<g id="{id_}" class="caption-card" data-layout-allow-caption-zone>{paper.put(paper.paper(width,130,paper.CORAL),left,1632)}<text x="540" y="1723" font-family="EB Garamond" font-weight="700" font-size="{font}" fill="{paper.PAPER}" text-anchor="middle">{escape(text)}</text></g>'
  capinitial.append({'target':'#'+id_,'props':{'opacity':0,'svgOrigin':'540 1697'}})
  capevents += [{'time':start,'target':'#'+id_,'action':'CAPTION_REPLACE','params':{}},{'time':start,'target':'#'+id_,'action':'FROM_TO','params':{'from':{'scale':.78,'y':18,'rotation':-3 if i%2 else 3},'to':{'scale':1,'y':0,'rotation':0},'duration':min(.16,max(.07,end-start)),'ease':'back.out(2.2)'}}]
  chunks.append({'text':text,'start':start,'end':end,'script_indices':ids,'emphasis':emphasis})
 for i,c in enumerate(chunks):
  c['end']=min(chunks[i+1]['start'] if i+1<len(chunks) else voice_duration,max(c['end'],c['start']+.12))
  capevents.append({'time':c['end'],'target':'#caption-'+str(i),'action':'SET','params':{'props':{'opacity':0}}})
 capspec={'schemaVersion':'1.0','compositionId':'captions','durationSec':duration,'fps':30,'initial':capinitial,'events':sorted(capevents,key=lambda e:e['time'])}
 (project/'compositions/captions.html').write_text(f'<template><style>#captions-root{{position:absolute;inset:0;width:100%;height:100%}}</style><div id="captions-root" data-composition-id="captions" data-width="1080" data-height="1920" data-duration="{duration}"><svg width="100%" height="100%" viewBox="0 0 1080 1920">{capbody}</svg></div><script>window.MotifEventEngine.compile({json.dumps(capspec,separators=(",",":"))},"captions");</script></template>')
 audio={'narration':'assets/voice/narration-af-nova.wav','duration':voice_duration,'review_input':'assets/voice/review-voice.wav','review_input_measurement':loudness(voice),'review_gain_db':0,'target_lufs':TARGET_I,'peak_ceiling':PEAK_CEILING,'music':False,'sfx':True,'sfx_cues':cues,'subjective_listening':'not assessed'}
 spec={'schemaVersion':'1.0','durationSec':duration,'fps':30,'initial':initial,'events':all_events,'shots':frames}
 for filename,data in [('scene-events.json',spec),('caption-events.json',chunks),('caption-engine-events.json',capspec),('alignment-review.json',alignment),('shot-direction.json',directions),('execution-bindings.json',directions),('contact-samples.json',contact_samples),('audio-plan.json',audio),('sfx-source-manifest.json',{'method':'original local synthesis; no external samples','music':'none; no permissioned track selected','assets':ledger}),('pre-render-checks.json',r)]:write(project/filename,data)
 if plan.get('quality_mode')=='motif-gold-v1':write(project/'quality-bindings.json',{'mode':'motif-gold-v1','shots':[{'id':b['id'],'contract':b['quality'],'span':s} for b,s in zip(plan['beats'],spans)],'hook':'anchor-aware pure-frame performance/reactions','critic_consumers':['direction','story','visual']})
 write_index(project,frames,duration,voice_duration,0)
 write(project/'review-state.json',{'status':'REVIEW_REQUIRED','approval_required_before':'creative acceptance; no automatic approval','plan_sha256':sha(project/'production-plan.json'),'voice_sha256':sha(project/'assets/voice/narration-af-nova.wav'),'events_sha256':sha(project/'scene-events.json'),'saved_source_hashes':{str(p.relative_to(project)):sha(p) for folder in ('compositions','assets/props','assets/sfx') for p in (project/folder).glob('*') if p.is_file()},'duration_seconds':duration,'finishing_rule':'saved plan and measured narration; no implicit replanning','planning_provenance':'agent-directed creative reset implementing supplied treatment; not new live autonomous planning'})
 return duration
