"""Eight finite, agent-assisted bindings requested by the live Dots planner.

SVG layers remain editable. Every state is computed from supplied setup time;
no article-specific keyword dispatch, external imagery or mutable playback state.
"""
import math
from common import *
from motif_reaction import reaction

def cue(ctx,b,n=0,default=.5):
 row=ctx.get(b,{})
 return row.get('cues',[default])[min(n,len(row.get('cues',[default]))-1)]
def start(ctx,b,default=0):return ctx.get(b,{}).get('start',default)
def label(s,x,y,size=30,color=INK):return text(s,x,y,size,color,'middle',900)
def tagged(id_,body):return f'<g data-asset="{id_}" id="{id_}">{body}</g>'
def scallop(w=390):
 d=f'M0 36Q-16 9 15 0Q29 -32 65 -15Q88 -44 120 -25Q162 -57 198 -27Q229 -43 252 -14Q299 -42 329 -16Q{w-3} -18 {w} 10Q{w+26} 40 {w-6} 54H8Z'
 return path(d,INK,0,INK,'transform="translate(5 7)" opacity=".18"')+path(d,EDGE,3,CREAM)+path(d,EDGE,0,'url(#grain)')
def taskstrip(x,y,t,w=300):
 b=card(w,44,CREAM)
 for i in range(5):
  xx=(i*62-t*55)%(w-15)+8
  b+=rect(xx,13,24,18,TEAL,4)
 return g(b,x,y)
def cloudcomputer(x,y,w=390,h=285,t=0,seat=True):
 b=card(w,h,TEAL)+rect(13,16,w-26,h-32,DARK,16)
 # Three visible draft lines grow independently; not a claimed screenshot.
 for i in range(3):
  prog=clamp((t*.58+i*.33)%1.3)
  b+=rect(33,56+i*48,(w-90)*prog,14,MINT,3)
 b+=g(scallop(w+18),-9,h+34)
 if seat:b+=dot(w*.74,h*.68,32,t)
 b+=icon('cloud',w-39,32,.65,CREAM)
 return g(b,x,y)
def sunmoon(x,y,t,r=42):
 b=f'<circle r="{r}" fill="{DARK}"/>'
 phase=int(max(0,t)/1.45)%2
 if phase:b+=f'<circle cx="-2" cy="-3" r="{r*.55}" fill="{CREAM}"/><circle cx="9" cy="-12" r="{r*.49}" fill="{DARK}"/>'
 else:
  b+=f'<circle r="{r*.39}" fill="{GOLD}"/>'
  for i in range(8):
   a=math.pi*i/4;b+=path(f'M{math.cos(a)*r*.53} {math.sin(a)*r*.53}L{math.cos(a)*r*.76} {math.sin(a)*r*.76}',GOLD,3)
 return g(b,x,y,a=1.5*math.sin(t*2))

def recess(x,y,r,response=0):
 # Explicit contact surface: token bottom meets the ellipse, not an unseen seat.
 return f'<ellipse cx="{x}" cy="{y+2*response}" rx="{r*1.17+3*response}" ry="{12-2*response}" fill="{INK}" stroke="{MINT}" stroke-width="6"/>'

def opening(t,d,ctx):
 c1=cue(ctx,'b01',0,1.2);c2=cue(ctx,'b01',1,3.1);named=start(ctx,'b02',max(3,d-1.2))
 unfold=ramp(t,.25,1.25);seat=ramp(t,c1,.4)
 b=backdrop(GOLD)
 # Foreground user's computer remains visibly separate.
 b+=g(card(320,195,SLATE)+rect(16,17,288,154,CREAM,8)+icon('person',210,85,1.3,DARK),-135,735,a=-4)
 b+=path('M-20 945Q126 852 183 961T339 1002',INK,15)+path('M0 990L223 986L277 1068H0Z',EDGE,0,EDGE)
 station=cloudcomputer(0,0,410,300,max(0,t-c1),False)
 b+=tagged('cloud-desk',g(station,236,390+260*(1-unfold),s=1,a=-68*(1-unfold),sy=max(.09,unfold)))
 token_x=536;token_y=655-45*seat
 settle=impulse(t,c1+.4)
 b+=recess(token_x,647,37,settle)
 b+=tagged('dot-token',dot(token_x,token_y-140*(1-seat)+2*settle,37,t))
 # Rim slides down to uncover the token; it is not a new continuity object.
 rim=1-ramp(t,named,.22)
 # This narrow band covers the local name, leaving the landing surface below
 # fully exposed. Naming clears the band after the seat has been established.
 b+=g(card(100,17,TEAL),486,600+55*(1-rim),opacity=rim)
 active=max(0,t-c2)
 b+=tagged('cloud-desk.ribbon-feed',taskstrip(276,751,active,340))
 b+=sunmoon(602,292,1.5*ramp(t,c2+.04,.25))
 q=ctx.get('b02' if t>=named else 'b01',{}).get('quality',{})
 contact=c1+.4
 st='listening' if t<c1 else 'anticipating' if t<contact else q.get('performance',{}).get('state','surprised' if t<named else 'listening')
 age=max(0,t-contact)
 response=0
 if contact<=t<contact+.8:
  rr=q.get('reaction_radius',{})
  if rr.get('targets'):
   target=rr['targets'][0];v=reaction(t-contact,rr['origin'],target['position'],rr['radius'],target['relevance'],target['amplitude'],rr['duration'],target['delay']);response=v['rotation']
 if t>=named:
  # Close view of the same token; no duplicate identity in a detail plate.
  k=ramp(t,named,.2);scale=1+1.8*k
  b=g(b,(235-536*2.8)*k,(630-610*2.8)*k,s=scale)
 b+=tagged('bot',bot(390,699,.36,st,age,a=response))
 return b

def routes(t,d,ctx):
 connect=cue(ctx,'b03',0,2.0);shelf=start(ctx,'b04',max(3,d-2));land=cue(ctx,'b04',0,shelf+.5)
 b=backdrop('#CBD7D0','isolated')
 opening=ramp(t,.15,max(.7,connect-.35))
 # Split chat enclosure creates a physical exit, not a disappearing UI label.
 shell=card(225,205,CREAM)+path('M34 199L20 241L88 205',EDGE,3,CREAM)
 b+=g(shell,244-110*opening,477,a=-12*opening,opacity=1-opening)
 hub=(374,614);ends=[(134,805,'mail'),(548,739,'folder'),(218,342,'calendar')]
 for i,(x,y,kind) in enumerate(ends):
  k=ramp(t,connect+i*.12,.3)
  ex=hub[0]+(x-hub[0])*k;ey=hub[1]+(y+67-hub[1])*k
  b+=g(card(139,124,CREAM),x-68,y-59,a=[-6,5,-3][i])+icon(kind,x,y,1.25,DARK)
  # Leads cross the lower outside corner ON TOP of the tile. Painting tiles
  # above the lead had hidden the continuous end and made plugs look detached.
  b+=path(f'M{hub[0]} {hub[1]}Q{(hub[0]+ex)/2-30} {(hub[1]+ey)/2} {ex} {ey}',SLATE,18)
  squeeze=impulse(t,connect+i*.12+.3)
  b+=f'<circle cx="{x}" cy="{y+67}" r="23" fill="{DARK}" stroke="{MINT if k>=1 else CREAM}" stroke-width="{7+3*squeeze}"/>'
  b+=g(rect(-15,-9,30,18,TEAL,4),ex,ey,a=squeeze*5)
 rise=ramp(t,shelf,.55);seat=ramp(t,land,.4)
 b+=tagged('route-dock',g(cloudcomputer(0,0,315,213,max(0,t-shelf),False),291,281+155*(1-rise),sy=max(.02,rise),opacity=rise))
 b+=tagged('route-dock.socket-seams',path('M349 595H398',TEAL,12))
 x=374+140*seat;y=614-187*seat
 settle=impulse(t,land+.4)
 b+=g(recess(514,471,44,settle),opacity=rise)
 b+=tagged('dot-token',dot(x,y+2*settle,44,t))
 return b

def job(t,d,ctx):
 begin=max(.1,cue(ctx,'b05',0,.4)-.8);u=clamp((t-begin)/max(1,d-begin-.45))
 b=backdrop(DARK,'isolated')
 # Accordion folds progress down the diagonal; completed folds compact behind.
 x0,y0=124,318
 b+=tagged('dot-token',dot(x0,y0,42,t))
 stops=[(221,470,'folder'),(337,659,'calendar'),(493,834,'mail')]
 for i,(x,y,kind) in enumerate(stops):
  prog=clamp(u*3-i)
  previous=(x0,y0) if i==0 else stops[i-1][:2]
  px,py=previous
  compact=ramp(prog,.8,.2)
  fx=px+(x-px)*compact*.82;fy=py+(y-py)*compact*.82
  b+=path(f'M{fx+20} {fy+50*(1-compact)}L{x-30} {y-35}',EDGE,52)
  for j in range(4):
   v=(j+.5)/4;xx=fx+(x-fx)*v;yy=fy+(y-fy)*v
   b+=path(f'M{xx-21} {yy-10}L{xx+28} {yy+10}',TEAL if compact>.5 else CREAM,5)
  b+=g(card(150,118,CREAM),x-75,y-59,a=-8+i*5)
  b+=icon(kind,x,y,1.05,DARK)
  if prog>0:
   p=prog;sheet=card(86,76,MINT)+path('M14 22H64M14 42H56',DARK,5)
   b+=g(sheet,px+(x-px)*p-43,py+(y-py)*p-38,a=-6+12*p)
  if prog>=1:b+=icon('check',x+48,y+38,.6,TEAL)
 # Actual draft replaces empty exit after the ordered process, and stays unsent.
 final=begin+max(1,d-begin-.45)
 out=ramp(t,final+.1,.23)
 b+=tagged('job-fold.draft-exit',g(card(161,137,CREAM)+label('DRAFT',80,41,26,DARK)+path('M22 70H131M22 93H117M22 115H137',SLATE,7),440,943-110*out,a=6,s=max(.01,out)))
 # Separate foreground page turns, leaving the process aperture unoccluded.
 page=card(240,289,CORAL)+path('M26 45H190M26 78H168M26 111H190',CREAM,7)
 b+=g(page,-82,774,a=-8)
 turn=ramp(t,.4,.7);again=ramp(t,1.9,.7)
 leaf=card(183,238,CREAM)+path('M24 38H153M24 71H131M24 103H149',SLATE,7)
 b+=g(leaf,103-163*turn,795,a=-8-35*turn,sy=max(.1,1-.83*turn))
 b+=g(leaf,103-163*again,795,a=-8-35*again,sy=max(.1,1-.83*again),opacity=ramp(t,1.5,.2))
 return tagged('job-fold',b)

def specialist_panel(t,kind='specialist'):
 if kind=='specialist':
  b=card(445,285,SLATE)
  # Company-document inspection jig: raw company pages enter a stencil and
  # become one proposed review sheet. This conceptual preview is not live work.
  process=ramp(t,.2,.9);inspection=ramp(t,.3,.75)
  firm=path('M-35 -20L0 -39L35 -20H-35M-29 -10V26M-10 -10V26M10 -10V26M29 -10V26M-36 34H36',DARK,7)
  for i in range(3):
   doc=card(168,176,CREAM)+g(firm,84,55,s=1.05)+path('M20 115H147M20 149H135',DARK,9)
   b+=g(doc,18+i*12+26*process,78+i*6-6*process,a=-5+i*3)
  b+=g(card(58,184,TEAL)+path('M13 15V166M39 15V166',MINT,8),192,77)
  reader_y=98+116*inspection
  b+=g(card(222,32,MINT)+path('M13 16H205',DARK,7),53,reader_y)
  report=card(140,153,CREAM)+g(firm,70,34,s=.35)
  output=ramp(t,1.12,.45)
  for i in range(3):report+=g(icon('check',27,71+i*31,.52,DARK)+path(f'M51 {68+i*31}H121',DARK,8),opacity=ramp(t,1.27+i*.12,.15))
  b+=g(report,244+18*output,102-10*output,a=4,opacity=output)
  veil=path('M10 0H400V227H0V10Z',CREAM,4,CREAM,extra='fill-opacity=".28"')
  veil+=path('M356 0V42H400M356 0L400 42',EDGE,3,CREAM,extra='fill-opacity=".6"')
  b+=g(veil,21,29)
  b+=g(card(315,59,CREAM)+label('PREVIEW',157,43,38,DARK),63,9,a=-3)
  return b
 b=card(447,258,PLUM)
 # Closed perforated cover, with empty team sockets in windows, no active team.
 for i in range(3):
  x=44+i*127
  b+=rect(x,101,96,99,CREAM,16)+f'<circle cx="{x+48}" cy="149" r="28" fill="none" stroke="{SLATE}" stroke-width="5" stroke-dasharray="8 6"/>'
 b+=path('M105 216H338',EDGE,7)+g(card(327,62,CREAM)+label('PLANNED',164,44,36,PLUM),60,16,a=2)
 b+=path('M12 239H436',EDGE,4,extra='stroke-dasharray="13 9"')
 return b

def folio(t,d,ctx):
 workcue=cue(ctx,'b06',0,.5);future=start(ctx,'b07',max(3,d-3));preview=cue(ctx,'b07',0,future+.4);team=cue(ctx,'b07',1,future+1.7)
 b=backdrop('#64869A','isolated')
 open_=ramp(t,.12,.55);fold=1-ramp(t,future,.35)
 cover=card(510,535,TEAL)+path('M34 28V508',DARK,11)
 b+=g(cover,104,365,a=-7)
 left=card(265,413,CREAM)+icon('folder',133,77,1.5,DARK)
 # Papers feed and visibly consolidate into a work folio, rather than just labels.
 settle=sum(impulse(t,workcue-1.2+i*.2+.65) for i in range(3))
 for i in range(3):
  p=clamp((t-(workcue-1.2+i*.2))/.65)
  left+=g(card(123,94,CREAM)+path('M16 28H102M16 49H88',SLATE,6),-95+55*i+(155-47*i)*p,94+48*i+(184-48*i)*p+2*settle,a=(-11+i*9)*(1-p))
 # Open-faced retaining pocket: every bottom edge and its caused stop remain
 # visible through the aperture, rather than disappearing behind an opaque lip.
 pocket=path('M0 4V90H194V4',TEAL,14)+path('M0 4H37M157 4H194',MINT,7)
 left+=g(pocket,34,282+2*settle)
 right=card(250,350,GOLD)+icon('calendar',125,92,1.8,DARK)
 for i in range(3):
  k=ramp(t,workcue+.05+i*.22,.25)
  right+=g(card(155,49,CREAM)+icon('check',20,24,.35,TEAL)+rect(43,17,95,10,DARK,2),48,175+i*51,a=impulse(t,workcue+.75+i*.22)*4,opacity=k)
 b+=tagged('preview-folio',g(left,92,399,s=max(.02,open_*fold),a=-9))+g(right,362,506,s=max(.02,open_*fold),a=7)
 b+=path('M347 402L345 898',DARK,9)
 if t<future:
  travel=ramp(t,workcue+.3,.7);b+=dot(211+291*travel,794+71*travel,39,t)
 if t>=future:
  k=ramp(t,preview-.25,.4);after=ramp(t,team-.35,max(.65,d-team+.15))
  b+=g(specialist_panel(max(0,t-preview+.25)),115-20*after,389-74*after,s=max(.01,1.12*k),a=-5)
  b+=g(specialist_panel(t,'team'),126,757-145*after,s=max(.01,after),a=4)
 return b

def handkey(x,y,a=0,s=1):
 # Key and hand share a parent: no independently animated grip can drift.
 hand=path('M-260 60L-54 32Q-30 12 -7 19L67 21Q91 25 90 41Q85 57 51 55L16 82Q-9 98 -62 86L-260 131Z',EDGE,3,CREAM)
 hand+=path('M-259 63L-195 57L-191 119L-260 133Z',SLATE,0,SLATE)
 key=path('M43 11A35 35 0 1 1 43 12M77 12H246V37H216V57H189V35H77Z',INK,0,INK,'transform="translate(4 6)" opacity=".18"')
 key+=path('M43 11A35 35 0 1 1 43 12M77 12H246V37H216V57H189V35H77Z',EDGE,3,GOLD)
 key+=f'<circle cx="43" cy="11" r="16" fill="{CREAM}"/>'
 # Fingers overlap ring lower edge, visibly holding it.
 fingers=path('M-7 41L62 41Q76 47 64 62L13 69Q-5 61 -7 41Z',EDGE,3,CREAM)
 return g(key+hand+fingers,x,y,s,a)
def latch(t,d,ctx,ending=False):
 b=backdrop('#CBD7D0','isolated')
 event=cue(ctx,'b12' if ending else 'b08',0,1)
 response=0 if ending else impulse(t,event,.45)*2
 b+=g(card(120,549,CORAL),390+response,327)
 # Corrugated stop edge and lock visibly remain closed.
 for i in range(8):b+=path(f'M493 {366+i*57}L508 {365+i*57}',CREAM,4)
 lock=(449+response,657)
 b+=icon('lock',*lock,1.5,INK)
 b+=dot(605,423,38,t,False)
 if not ending:
  u=clamp((t-.2)/max(.5,event-.2))
  b+=g(card(191,25,TEAL),510,648)
  slip=card(135,116,CREAM)+icon('mail',67,62,1.1,DARK)
  b+=tagged('permission-latch.slip-stop',g(g(slip,0,-58),608-98*u+response,586,a=impulse(t,event,.45)*3))
  # A second queued proposal meets the same rule, expressing continuing pending work.
  q=ramp(t,event+.18,.4);b+=g(card(83,70,CREAM)+icon('mail',42,35,.55,DARK),634-17*q,719-61*q,a=6,opacity=q)
  b+=handkey(108,825,a=-11,s=.65)
 else:
  u=ramp(t,event-.3,min(.65,max(.3,d-.7)))
  # Same held key advances; final rightmost tooth stops short of the lock.
  b+=tagged('permission-latch.key-contact',handkey(12+17*u,830-140*u,a=-13+6*u,s=1.05))
 return tagged('permission-latch',b)

def access(t,d,ctx):
 paid=cue(ctx,'b09',0,.5);free=cue(ctx,'b09',1,max(2,d-1.7))
 b=backdrop(PLUM,'isolated')
 # Access is a visible required ticket vs an open entrance, not a scored race.
 b+=g(card(258,310,TEAL),66,465,a=-3)+g(card(254,261,SLATE),403,625,a=4)
 b+=g(card(274,69,CREAM),58,778,a=-3)+g(card(275,67,CREAM),393,890,a=4)
 b+=rect(126,502,133,238,DARK,54)+rect(457,667,147,195,DARK,50)
 k=ramp(t,paid-.45,.5);z=ramp(t,free-.4,.5)
 # Dots slot remains blocked; eligible ticket is shown alongside, never inserted.
 for i in range(3):b+=g(card(49,202,CREAM),130+i*43,535,a=-2,opacity=.9)
 b+=tagged('access-ledges.ticket-slot',g(card(204,64,CREAM),92,647)+rect(102,671,184,18,INK,4)+path('M103 669H286',GOLD,5))
 ticket=card(171,117,GOLD)+label('ELIGIBLE',85,42,27,DARK)+label('PAID PLAN',85,84,27,DARK)
 approach=clamp((t-.25)/max(.8,free-.7))
 b+=g(ticket,49+10*approach,337+153*approach,a=-6*(1-approach),opacity=ramp(t,.1,.3))
 b+=path('M169 621L194 646M180 645L194 646L193 632',GOLD,5,extra=f'opacity="{approach}"')
 prepare=ramp(t,paid+.5,max(.5,free-paid-.6))
 b+=tagged('access-ledges.free-entry',g(card(134,241,SLATE),456+141*z,654,a=4*prepare+8*z,opacity=1-z))
 b+=g(card(179,97,CREAM)+label('FREE TIER',89,61,30,DARK),438,476,a=3,opacity=z)
 extras=ramp(t,free+.6,max(.4,d-free-.8))
 b+=g(card(146,112,GOLD)+label('MORE',73,40,23,DARK)+label('Paid extras',73,91,21,DARK),502,322+48*(1-extras),a=8+13*(1-extras),opacity=extras)
 b+=label('DOTS',193,865,40,CREAM)+label('MUSE',530,999,40,CREAM)
 b+=g(card(155,44,CREAM)+label('Rollout varies',77,30,18,DARK),91,733,a=-3,opacity=.86*k)
 # Rejected ticket sits in front of the barred slot, showing no granted access.
 b+=dot(186,931,35,t,False)
 return tagged('access-ledges',b)

def workplane(t,d,ctx):
 foldcue=cue(ctx,'b10',0,.7);seatstart=start(ctx,'b11',max(3,d-3));seatcue=cue(ctx,'b11',0,seatstart+.5)
 b=backdrop('#EBC46B','isolated')
 k=ramp(t,foldcue-.6,.75)
 podium=card(217,374,SLATE)+g(card(168,110,CREAM),24,26)+label('?',110,108,64,DARK)+path('M55 207H163M55 239H145',CREAM,12)
 for i in range(2):
  flow=clamp((t-i*.55)/max(.7,foldcue-.6));podium+=g(card(87,63,CREAM)+path('M15 22H69M15 41H54',DARK,5),60,141+104*flow,a=-5+6*flow,opacity=(1-k)*clamp((t-i*.55)*4))
 # Bottom edge stays fixed. The same blue face folds to table depth; both
 # cream wings grow from its attached edges, never replacing it with a desk.
 sy=1-(1-116/374)*k
 wings=g(card(75*k,116,CREAM),151-75*k,698)+g(card(274*k,116,CREAM),368,698)
 b+=g(wings,opacity=k)
 b+=g(g(podium,0,-374),151,814,sy=sy)
 b+=tagged('coworker-shift.pedestal-hinge',path('M151 814H368',MINT,9))
 b+=g(card(40,159,PLUM),127,814,opacity=k)+g(card(44,159,PLUM),551,814,opacity=k)
 if t>=seatstart-.2:
  q=ramp(t,seatstart-.2,.6);land=ramp(t,seatcue-.35,.55)
  # User papers remain one near-side task position; Dot has its OWN computer.
  for i in range(3):b+=g(card(166,124,SLATE if i==0 else CREAM)+path('M23 43H137M23 74H119',DARK,7),91+i*6,700-i*33*q,a=-6+i*4,opacity=q)
  b+=g(cloudcomputer(0,0,294,238,max(0,t-seatstart),False),357,462+106*(1-q),s=max(.01,q))
  settle=impulse(t,seatcue+.2)
  b+=g(recess(565,674,36,settle),opacity=q)
  b+=g(dot(565,658-20*land-130*(1-land)+2*settle,36,t),opacity=q)
  b+=taskstrip(295,814,max(0,t-seatcue),272)
  b+=sunmoon(549,320,max(0,t-seatstart),58)
 return tagged('coworker-shift',b)

RENDERERS={'s01':opening,'s02':routes,'s03':job,'s04':folio,'s05':latch,'s06':access,'s07':workplane,'s08':lambda t,d,c:latch(t,d,c,True)}
def frame(setup,t,d,ctx):
 if setup not in RENDERERS:raise ValueError('agent-assisted binding missing for setup '+setup)
 return RENDERERS[setup](t,d,ctx)

# Exposed finite contracts, independent of a generic keyword/template dispatcher.
BEAT_BINDINGS={
 'b01':('s01','cloud-desk.station-separation','establish',['requested:dots-cloud-seat-v1','requested:dots-ribbon-advance-v1']),
 'b02':('s01','dot-token.notch','detail',['requested:dots-cloud-seat-v1']),
 'b03':('s02','route-dock.socket-seams','subject',['requested:dots-route-connect-v1']),
 'b04':('s02','route-dock.cloud-seat-gap','detail',['requested:dots-route-connect-v1']),
 'b05':('s03','job-fold.draft-exit','subject',['requested:dots-ribbon-advance-v1']),
 'b06':('s04','preview-folio.task-pockets','establish',['requested:dots-folio-reveal-v1']),
 'b07':('s04','preview-folio.status-boundary','subject',['requested:dots-folio-reveal-v1','requested:dots-folio-reveal-v1']),
 'b08':('s05','permission-latch.slip-stop','detail',['requested:dots-permission-stop-v1']),
 'b09':('s06','access-ledges.entry-comparison','subject',['requested:dots-access-compare-v1','requested:dots-access-compare-v1']),
 'b10':('s07','coworker-shift.pedestal-hinge','establish',['requested:dots-workplane-shift-v1']),
 'b11':('s07','coworker-shift.independent-seat','subject',['requested:dots-workplane-shift-v1']),
 'b12':('s08','permission-latch.key-contact','detail',['requested:dots-human-key-offer-v1'])}
def validate_bindings(plan):
 assigned={b:s['setup_id'] for s in plan['film_structure']['setups'] for b in s['beat_ids']}
 if set(assigned)!=set(BEAT_BINDINGS):raise ValueError('New beats need explicit agent-assisted binding development')
 for b in plan['beats']:
  setup,focus,framing,actions=BEAT_BINDINGS[b['id']]
  if (assigned[b['id']],b['focus_target'],b['framing'],[a['kind'] for a in b['actions']])!=(setup,focus,framing,actions):raise ValueError('Unresolved action/focus/framing: '+b['id'])
  q=b['quality'];present=setup=='s01'
  if (q['performance']['state']!='absent')!=present or (q['performance']['target']=='bot')!=present:raise ValueError('Unbound character channel: '+b['id'])
