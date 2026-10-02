"""Editable paper UI capabilities for finite Motif productions.

Agent-authored SVG; canonical puppet imported unchanged. All inputs are explicit
frame-indexed state. No clocks, network, random playback or product integration.
Coordinates use the requested 720 x 1280 authoring grid.
"""
import math,re
from functools import lru_cache
from html import escape
from build_motif_bot import assemble_pose,DEFS as BOT_DEFS
from motif_paper_energy import living,clamp,ease,spring
CREAM='#EEE5D3'; EDGE='#CBBEAA'; INK='#211923'; PANEL='#241D29'
PINK='#F293B6'; MAGENTA='#B60B50'; CORAL='#DC8159'; GREEN='#258650'; GOLD='#E6C253'
DEFS=BOT_DEFS.removeprefix('<defs>').removesuffix('</defs>')+'''<pattern id="worldPaper" width="2048" height="2048" patternUnits="userSpaceOnUse"><image href="assets/materials/world-paper.webp" width="2048" height="2048"/></pattern><filter id="pushBlur" x="-10%" width="120%"><feGaussianBlur stdDeviation="3 0"/></filter>'''
def g(body,x=0,y=0,a=0,s=1,sy=1,opacity=1):
 return f'<g opacity="{opacity:.4f}" transform="translate({x:.3f} {y:.3f}) rotate({a:.3f}) scale({s:.5f} {s*sy:.5f})">{body}</g>'
def rect(x,y,w,h,fill,r=0,stroke=None,sw=2):
 return f'<rect x="{x:.2f}" y="{y:.2f}" width="{max(0,w):.2f}" height="{max(0,h):.2f}" rx="{r}" fill="{fill}"'+(f' stroke="{stroke}" stroke-width="{sw}"' if stroke else '')+'/>'
def path(d,color,sw=3,fill='none',extra=''):
 return f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" {extra}/>'
def txt(text,x,y,size=20,color=CREAM,weight=700,anchor='start',serif=False):
 return f'<text x="{x:.2f}" y="{y:.2f}" font-family="'+('EB Garamond' if serif else 'Inter')+f'" font-weight="{weight}" font-size="{size:.2f}" fill="{color}" text-anchor="{anchor}" data-layout-allow-overlap>{escape(text)}</text>'
def card(w,h,color=CREAM,grain=.10,r=8):
 # Dimensions/material determine a stable cut profile; texture never moves.
 v=int(w*7+h*11+sum(map(ord,color)))%7;j=.65+.2*v
 d=f'M2 {2+j}L{w*(.23+.025*v)} .5L{w-3} {j}L{w} {h*.43}L{w-1.8} {h-1}L{w*.71} {h+j*.3}L{w*.28} {h-1.2}L.5 {h-2}Z'
 return path(d,INK,1,INK,extra='transform="translate(4 6)" opacity=".15"')+path(d,EDGE,1,EDGE,extra='transform="translate(1.5 2.4)"')+path(d,color,.7,color)+path(d,color,0,'url(#worldPaper)',extra=f'opacity="{grain*.75}"')
def headline(text):
 # The longer labels use two readable lines instead of tiny one-line text.
 words=text.split();lines=[text]
 if len(text)>36:
  mid=min(range(1,len(words)),key=lambda i:abs(len(' '.join(words[:i]))-len(' '.join(words[i:]))))
  lines=[' '.join(words[:mid]),' '.join(words[mid:])]
 h=72 if len(lines)==1 else 100;y=183 if len(lines)==1 else 168
 variation=sum(map(ord,text))%5
 body=card(680,h)+g(card(62+variation,21,'#C8B078',.04),13,-7,-12+variation)+g(card(69,19,'#D0BC88',.04),598,-6,9+variation)
 for i,line in enumerate(lines):
  size=min(32,620/(max(1,len(line))*.57))
  body+=txt(line,340,46+i*34 if len(lines)==2 else 49,size,INK,900,'middle')
 return g(body,20,y,a=-.4)
def backdrop(color,kind='room',f=0):
 b=rect(0,0,720,1280,color)+rect(0,0,720,1280,'url(#worldPaper)')
 # Quiet real texture composited at reduced strength, no visible tiled blotch.
 b=rect(0,0,720,1280,color)+g(rect(0,0,720,1280,'url(#worldPaper)'),opacity=.19)
 warm=color in ['#BFA783','#B59D72','#BFA17C','#B87A54','#B49B79']
 wood='#785640' if warm else '#68716C' if color=='#91A99F' else '#626775'
 b+=path('M0 967L170 969L435 966L720 968V1280H0Z',wood,0,wood)+path('M0 971L191 973L459 970L720 972','#B59472' if warm else '#969B89',13)+path('M0 984H720','#493D36',2)
 b+=g(rect(0,987,720,293,'url(#worldPaper)'),opacity=.09)
 for i,(yy,xx) in enumerate([(991,37),(1120,288),(1248,71)]):
  b+=path(f'M{xx} {yy}Q{xx+97} {yy-3} {xx+222} {yy+1}T{min(720,xx+405)} {yy-1}', '#C7A989' if warm else '#ABB2A6',1.2,extra='opacity=".17"')
 if kind=='tiles':
  b+=rect(0,290,720,663,'#BDCFCA')
  for x in range(0,721,72):b+=path(f'M{x} 290V953','#DDE4DA',3)
  for y in range(290,953,74):b+=path(f'M0 {y}H720','#DDE4DA',3)
  b+=g(card(54,180,'#F4DFB6'),658,408)+''.join(f'<circle cx="681" cy="{437+i*26}" r="7" fill="{c}"/>' for i,c in enumerate([CORAL,GREEN,PINK,GOLD]))
 if kind=='shelves':
  for x in [0,653]:
   b+=rect(x,300,67,665,'#725343')
   for y in [390,540,690,840]:
    for k in range(4):b+=g(card(10+k%2*3,72,[CORAL,'#557C87',GREEN,GOLD][k]),x+7+k*13,y-75,a=(k-2)*2)
    b+=rect(x,y,67,10,'#B7855D')
 if kind=='notes':
  for i,(x,y) in enumerate([(12,369),(650,479),(637,778)]):b+=g(card(52,60,[GOLD,CORAL,'#A9C9B7'][i]),x,y,a=8-i*7)
 return b

def waveform(x,y,w,h,f,n=34,reveal=1,color=PINK,phase=0):
 b='';gap=w/n;visible=max(1,int(n*clamp(reveal)))
 for i in range(visible):
  envelope=.18+.82*math.sin(math.pi*(i+.5)/n)**.7
  signal=abs(math.sin(i*1.93+f*.22+phase)*.54+math.sin(i*.49-f*.13+phase)*.31+math.sin(i*.73+f*.07)*.15)
  bh=max(5,h*envelope*(.2+.8*signal));b+=rect(x+i*gap,y+(h-bh)/2,max(3,gap*.48),bh,color,3)
 return b

def check(x,y,s=1):
 return g('<circle r="23" fill="'+GREEN+'"/>'+path('M-11 0L-3 9L13 -10','#D4F1D9',5),x,y,s=s)
def cross(x,y,s=1):return g('<circle r="22" fill="#CD573A"/>'+path('M-8 -8L8 8M8 -8L-8 8',CREAM,4),x,y,s=s)
def ring(x,y,r,progress,f,done=False):
 if done:return check(x,y,s=r/25)
 c=2*math.pi*r
 return f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="#554253" stroke-width="8"/><circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="{PINK}" stroke-width="8" stroke-dasharray="{c*clamp(progress):.2f} {c:.2f}" transform="rotate(-90 {x} {y})"/>'+g(path(f'M{-r*.35} 0A{r*.35} {r*.35} 0 1 1 {r*.35} 0',PINK,3),x,y,a=f*24)
def button(label,x,y,w=195,h=43,color=MAGENTA,pressed=False):
 lettering=INK if color=='#8D9C91' else CREAM
 return g(rect(4,6,w,h,INK,8)+rect(0,0,w,h,color,8)+txt(label,w/2,h*.66,min(21,w/max(1,len(label))/.64),lettering,700,'middle'),x,y+4*pressed,sy=.94 if pressed else 1)
def pointer(x,y,press=False):
 return g(path('M0 0L0 29L8 22L16 38L22 35L13 19L26 18Z',INK,2,'#FFFFFF'),x,y,s=.88 if press else 1)
def token(x,y,label='My Voice',s=1,a=0):
 return g(card(116,76,PINK,.05)+waveform(15,7,86,33,11,n=12,color=INK)+txt(label,58,63,18,INK,700,'middle'),x,y,a,s)
def monitor(x,y,w=580,h=360,laptop=False,old=False):
 rim='#BCB59E' if old else '#302832';under='#8C897E' if old else '#100E15'
 contour=f'M11 3L{w*.37} 0L{w-12} 4Q{w+2} 7 {w} 20L{w-2} {h-15}Q{w-3} {h+1} {w-20} {h}L17 {h-2}Q-1 {h-5} 0 {h-23}L2 19Q2 4 11 3Z'
 b=path(contour,under,2,under,extra='transform="translate(6 9)"')+path(contour,rim,2,rim)+path(contour,rim,0,'url(#worldPaper)',extra='opacity=".12"')
 inset=30 if old else 14
 b+=rect(inset,inset,w-inset*2,h-inset*2-4,PANEL,12 if old else 8)+path(f'M20 9L{w*.48} 7L{w-24} 10','#D9D2BC' if old else '#5D505C',2)
 if old:
  for i in range(6):b+=path(f'M{w-100+i*10} {h-15}V{h-8}','#736F65',3)
  b+=rect(24,h-18,22,6,'#7A8572',2)+path(f'M6 64L10 37M{w-12} 50L{w-15} 70','#7E7B6D',2)
  b+=path(f'M{w*.39} {h-1}L{w*.63} {h}L{w*.7} {h+49}L{w*.31} {h+46}Z','#8B887B',2,'#ACA68F')+path(f'M{w*.2} {h+53}L{w*.78} {h+56}L{w*.74} {h+39}L{w*.27} {h+39}Z','#807C6D',2,'#C1BAA1')
  return g(b,x,y)
 if laptop:
  b+=path(f'M0 {h-3}L-33 {h+37}L{w+33} {h+37}L{w} {h-3}Z','#999995',2,'#C5C4BE')+rect(w*.33,h+15,w*.34,15,'#ADADA8',4)+path(f'M-25 {h+38}H{w+25}','#777778',4)
 else:b+=rect(w*.43,h-2,w*.14,94,'#2B2730',3)+path(f'M{w*.29} {h+98}L{w*.73} {h+98}L{w*.65} {h+83}L{w*.36} {h+83}Z',INK,2,'#343139')
 return g(b,x,y)
def app(x,y,w,h,f,progress=None,done=False,label='Voice cloning',pressed=False,progress_focus=False):
 b=txt(label,x+28,y+50,24)+txt('Voice sample',x+w-30,y+51,16,PINK,anchor='end')+path(f'M{x+25} {y+71}H{x+w-25}','#554350',2)
 b+=txt('Voice · VoiceStudio Demo Voice',x+29,y+99,14,'#ADA2AC')+txt('Script',x+29,y+134,18)
 b+=button('Synthesize audio',x+w-236,y+h-78,206,44,pressed=pressed)+txt('Auto ▾',x+30,y+h-48,17,'#CAC1C9')
 if progress is not None:
  yy=y+h*.52 if progress_focus else y+h-131;bh=52 if progress_focus else 14
  b+=rect(x+33,yy,w-153,bh,'#4C394B',7)+rect(x+33,yy,(w-153)*clamp(progress),bh,MAGENTA,7)+ring(x+w-66,yy+bh/2,32 if progress_focus else 25,progress,f,done)
  if progress_focus:b+=txt('LOCAL PROCESSING' if not done else 'COMPLETE',x+48,yy+34,21,CREAM,900)
 return b

def ribbon(x,y,f,w=290):
 a=14*math.sin(f*.13)
 d=f'M0 0C{w*.15} {-75+a} {w*.24} {80-a} {w*.37} 5S{w*.66} {-68-a} {w*.72} 3S{w*.89} {60+a} {w} 0'
 return g(path(d,'#D76B94',20)+path(d,PINK,14)+f'<circle cx="{w}" r="8" fill="#F4A46F"/>',x,y)
def star(x,y,s=1,c=GOLD,a=0):return g(path('M0 -16L4 -4L16 0L4 4L0 16L-4 4L-16 0L-4 -4Z',c,0,c),x,y,a,s)
def burst(x,y,f,start,seed=0,count=7):
 age=f-start
 if not 0<=age<24:return ''
 b='';u=age/24
 for k in range(count):
  a=k*2.399+seed*.1;r=(15+101*u)*(1+.38*math.sin(k*9));xx=x+math.cos(a)*r;yy=y+math.sin(a)*r+54*u*u
  size=[1.25,.48,.82,.60,1.55,.53,.95][k%7]
  b+=g(star(0,0,size,[CREAM,PINK,GOLD][k%3]),xx,yy,a=age*(3+k%3)+k*11,opacity=(1-u)**.6)
 return b

def plant(x,y,f=0,s=1):
 b=path('M0 0L12 61L63 61L77 0Z','#C6845D',2,'#C6845D')+rect(-4,-8,87,14,'#DD9A6D',4)
 for i in range(5):
  xx=38+(i-2)*15;yy=-28-(2-abs(i-2))*26;a=(i-2)*18+math.sin(f*.07+i)*3
  b+=path(f'M38 -2Q{xx} -30 {xx} {yy}','#537C58',4)+g(path('M0 0Q-30 -45 0 -50Q30 -35 0 0Z','#547C56',0,'#547C56'),xx,yy+14,a)
 return g(b,x,y,s=s)
def mug(x,y,color='#7198A0',s=1):
 return g(path('M45 10Q83 6 76 34Q68 46 47 39',color,8)+rect(0,0,49,58,color,10)+path('M5 4H44','#BACBC7',3)+path('M20 -11Q5 -24 22 -34','#CCC0AC',3),x,y,s=s)
def lamp(x,y,s=1):return g(path('M0 0L13 18H75L87 0Z',GREEN,2,GREEN)+path('M44 17V100M14 100H76',INK,7),x,y,s=s)
def mic(x,y,s=1):
 b=rect(0,0,52,82,'#ABA8A2',25,INK,3)
 for i in range(6):b+=path(f'M5 {15+i*10}H47','#686874',1.4)
 for i in range(5):b+=path(f'M{8+i*9} 11V71','#686874',1.2)
 b+=path('M-7 48V72Q26 109 59 72V48M26 97V155M26 155L-6 185M26 155L58 185',INK,7)
 return g(b,x,y,s=s)
def clock(x,y,s=1):return g('<circle r="35" fill="'+CREAM+'" stroke="'+EDGE+'" stroke-width="4"/>'+path('M0 0L-12 -15M0 0L23 0',INK,4),x,y,s=s)
@lru_cache(maxsize=512)
def bot_body(pose,face,head):
 body,parts=assemble_pose(pose,face,{'tilt':0,'body_y':0,'head_tilt':head})
 return re.sub(r'id="[^"]+"','',body).replace('<path ','<path data-layout-ignore ')
def bot(x,y,f,s=.245,face='happy',pose='standing',angle=0,jitter=True,contact=None,performance=None,impact=0,stretch=1):
 # y is feet level; override hand inverse uses exact same final world transform.
 if jitter:x+=living(f,791,1.0);y+=living(f,802,.8);angle+=living(f,821,.6)
 head=round(math.sin(f*.15)*2)
 if performance=='talking':
  face='excited' if f%9<5 else 'neutral';head=round(-5+math.sin(f*.4)*3);angle+=5
 elif performance=='strained':pose='thinking';face='worried';head=5;angle-=6
 elif performance=='relieved':pose='celebrating' if f<34 else 'presenting';face='proud';head=-4;angle+=3*math.exp(-max(0,f-24)/8)
 body=bot_body(pose,face,head)
 if contact:
  a=math.radians(angle);dx=contact[0]-x;dy=contact[1]-y
  local=(512+(dx*math.cos(a)+dy*math.sin(a))/s,861+(-dx*math.sin(a)+dy*math.cos(a))/s,'point')
  body,_=assemble_pose(pose,face,{'tilt':0,'body_y':0,'head_tilt':0,'r':local})
  body=re.sub(r'id="[^"]+"','',body).replace('<path ','<path data-layout-ignore ')
 # Follow-through rotates existing antennae as one piece. Geometry is locked.
 antenna=round((math.sin(f*.38-1)*2 if performance=='talking' else 0)+impact*18,2)
 body=body.replace('data-part="antennae">',f'data-part="antennae" transform="rotate({antenna} 512 207)">')
 squash=1-.18*impact
 return g(g(g(body,-512,-861),s=1/math.sqrt(squash),sy=squash*math.sqrt(squash)),x,y,angle,s,sy=stretch)
def hop_impact(f,start,end):
 """Feet-anchored compression, takeoff stretch and damped landing response."""
 if f<start+2:return .75*clamp((f-start+1)/2)
 if f<end:return -.32*math.sin(math.pi*clamp((f-start-2)/max(1,end-start-2)))
 age=f-end
 return .9*math.cos(age*.8)*math.exp(-age/4) if age<10 else 0
def hop(f,start,end,x1,y1,x2,y2,height=75):
 u=clamp((f-start)/max(1,end-start));return(x1+(x2-x1)*u,y1+(y2-y1)*u-height*math.sin(math.pi*u))
def receipt(x,y,a=0):return g(card(63,65,'#F5EFDF')+txt('Starter',31,25,12,INK,anchor='middle')+txt('Paid',31,46,13,GREEN,anchor='middle'),x,y,a)
def pricing(f,cancel=False):
 b=g(card(611,463),37,330)+txt('ElevenLabs / Pricing',67,379,26,INK,900)
 b+=path('M53 405H632M329 414V748','#B7AE9B',2)
 b+=txt('Free',251,447,30,INK,900,'middle')+txt('Starter',483,447,30,INK,900,'middle')
 b+=txt('Text to speech',67,512,17,INK)+txt('Voice cloning',67,586,17,INK)
 b+=check(250,507,.75)+check(480,507,.75)+cross(251,582,.98+(0.27*math.sin((f-13)/12*math.pi) if 13<f<25 and not cancel else 0))
 accepted=cancel or f>=42
 if accepted:b+=check(480,583,.97)+token(394,611,s=.78)
 b+=txt('billed monthly',481,706,17,INK,anchor='middle')
 state='Cancelled' if cancel and f>=24 else 'Cancel plan' if cancel else 'Subscribed' if f>=38 else 'Upgrade'
 b+=button(state,389,726,189,45,color='#8D9C91' if state=='Cancelled' else GREEN if state=='Subscribed' else INK,pressed=(17<=f<=23 if cancel else 33<=f<=37))
 b+=g(path('M-14 -9A18 18 0 1 1 -16 8M-14 -9L-23 -6M-14 -9L-13 -20',INK,3),609,747,a=0 if cancel and f>=24 else f*7)
 total=5 if cancel else max(0,min(5,(f-44)//5+1))
 for i in range(total):b+=receipt(650+(i%2)*3,725+i*37,living(f,51+i,.9) if cancel else -4+i*1.6)
 return b

def chapter_row(x,y,label,f,phase=0):return g(rect(0,0,490,83,'#3F2B3B',9)+txt(label,61,33,24)+'<circle cx="29" cy="40" r="18" fill="'+MAGENTA+'"/>'+path('M24 30L38 40L24 50Z',PINK,1,PINK)+waveform(176,8,292,67,f,n=29,phase=phase),x,y)
def transcript(x,y,speaker,color,f=0):
 return g(card(550,63)+rect(10,9,134,44,color,5)+txt(speaker,77,39,19,CREAM,anchor='middle')+path('M161 25H516M161 43H443','#B9B2A2',6),x,y,a=living(f,12+len(speaker),.5))
def keyboard(x,y,active=None):
 rows=['QWERTYUIOP','ASDFGHJKL','ZXCVBNM'];b='';positions={}
 for row,letters in enumerate(rows):
  offset=(10-len(letters))*17
  for k,letter in enumerate(letters):
   xx=x+offset+k*34;yy=y+row*49;pressed=active==letter
   b+=rect(xx+2,yy+4,29,40,'#B9B2A3',5)+rect(xx,yy+(3 if pressed else 0),29,40,GOLD if pressed else '#FAF6E9',5)+txt(letter,xx+14.5,yy+27,18,INK,anchor='middle')
   positions[letter]=(xx+15,yy)
 return b,positions

# Production-scoped v3 masters. Generated physical props remain independent
# transparent files; precise interfaces and the locked puppet remain SVG.
DEFS+='''
<clipPath id="artMonitor"><path d="M72 93Q67 31 145 18L1319 20Q1468 33 1513 169L1520 680Q1511 741 1424 746H932L927 850L1100 881L1119 967H452L475 880L649 849V746H173Q87 739 73 659Z"/></clipPath>
<clipPath id="artOld"><path d="M278 96Q285 24 364 20H1173Q1293 29 1307 118L1314 716Q1300 774 1213 776H917L929 859L1115 900L1127 970H453L473 887L644 856L650 776H347Q273 766 269 693Z"/></clipPath>
<clipPath id="artStool"><path d="M102 159Q163 95 327 105L1067 129Q1209 149 1269 223L1273 350Q1247 425 1106 443L1119 489L1220 998Q1222 1073 1148 1090L1065 1088Q1011 1057 1004 984L950 743L473 735L392 1006Q377 1098 305 1093L247 1086Q195 1064 209 989L338 459L212 423Q102 401 99 343Z"/></clipPath>
<clipPath id="artMic"><path d="M509 24Q291 25 232 190Q212 263 225 832Q235 912 333 930L690 935Q790 923 800 832L800 258Q797 72 605 31Z"/><path d="M114 486Q108 455 153 457L213 466L215 884Q221 968 421 991H604Q817 972 819 884V466L882 457Q921 457 922 495L911 904Q888 1010 600 1020H418Q133 1010 116 909Z"/><path d="M439 1003H588L592 1162L744 1264L966 1346Q986 1386 938 1405L861 1400L595 1300L614 1480Q609 1520 548 1523H453Q405 1508 408 1467L431 1299L176 1401L81 1400Q29 1378 62 1340L286 1267L437 1160Z"/></clipPath>
<clipPath id="artLaptop"><path d="M72 93Q67 31 145 18L1319 20Q1468 33 1513 169L1520 680Q1511 741 1424 746H173Q87 739 73 659Z"/></clipPath>
</defs><defs>
'''.replace('</defs><defs>','')
def image_prop(name,x,y,w,h,clip,layer="backing"):
 dimensions={'monitor':(1586,992),'old-computer':(1585,992),'microphone':(1024,1536),'stool':(1374,1145)}
 iw,ih=dimensions[name]
 # HTML background decoding is awaited by the pinned renderer before capture.
 # Keep the authored SVG mask and the exact lossless master pixels.
 bitmap=f'<foreignObject width="{iw}" height="{ih}"><img xmlns="http://www.w3.org/1999/xhtml" width="{iw}" height="{ih}" src="/assets/art-v3/{name}.webp?layer={layer}" style="width:{iw}px;height:{ih}px;background-image:url(/assets/art-v3/{name}.webp?layer={layer});background-size:100% 100%;background-repeat:no-repeat"/></foreignObject>'
 return g(f'<g clip-path="url(#{clip})">{bitmap}</g>',x,y,s=w/iw,sy=(h/ih)/(w/iw))

def card(w,h,color=CREAM,grain=.10,r=8):
 v=int(w*7+h*11+sum(map(ord,color)))%7
 # Intentional cut corners and bottom paper strata, no animated noise.
 d=f'M1 {4+v*.2}Q2 1 8 1L{w*.42} .5L{w-7} 2L{w-1} 7L{w-.6} {h*.58}L{w-3} {h-2}L{w*.64} {h+1}L6 {h-1}L.5 {h-7}Z'
 b=path(d,'#3A2F28',0,'#3A2F28',extra='transform="translate(3 6)" opacity=".17"')+path(d,EDGE,1,EDGE,extra='transform="translate(1 3)"')+path(d,color,.6,color)
 b+=path(d,color,0,'url(#worldPaper)',extra=f'opacity="{grain*.8}"')
 if w>70 and h>38:b+=path(f'M8 {h-3}Q{w*.29} {h-1} {w*.47} {h-2}',EDGE,.8,extra='opacity=".48"')+path(f'M{w-5} 11L{w-4} {min(h-12,32)}','#FFFFFF',1,extra='opacity=".18"')
 return b

def monitor(x,y,w=580,h=360,laptop=False,old=False):
 # Screen bounds remain a predictable editable coordinate system. Master art
 # is mapped from its display window, separately from the foreground rim.
 if old:
  sx=(w-60)/815;sy=(h-60)/540
  return image_prop('old-computer',x+30-380*sx,y+30-114*sy,1585*sx,992*sy,'artOld')
 sx=(w-28)/1343;sy=(h-32)/594
 b=image_prop('monitor',x+14-117*sx,y+14-58*sy,1586*sx,992*sy,'artLaptop' if laptop else 'artMonitor')
 if laptop:
  deck=path(f'M0 0L-24 43Q{w/2} 55 {w+24} 43L{w} 0Z','#A79F8D',2,'#D7D0BF')+path(f'M{w*.38} 32H{w*.62}','#B6AE9D',10)+path(f'M-21 44Q{w*.4} 54 {w+21} 44','#8E8778',4)
  for i in range(11):deck+=path(f'M{w*.10+i*w*.073} 9L{w*.08+i*w*.077} 22','#A69D8C',4)
  b+=g(deck,x,y+h+51)
 return b

def physical_monitor(x,y,w,h,content,old=False):
 inset=30 if old else 14
 # Explicit content mask + bezel. Hole mask reconstructs only the screen;
 # original generated bitmap remains unmodified on disk.
 name='old-computer' if old else 'monitor';iw=1585 if old else 1586
 if old:sx=(w-60)/815;sy=(h-60)/540;ix=x+30-380*sx;iy=y+30-114*sy;clip='artOld'
 else:sx=(w-28)/1343;sy=(h-32)/594;ix=x+14-117*sx;iy=y+14-58*sy;clip='artMonitor'
 uid='screenContentOld' if old else 'screenContent'
 defs=f'<defs><clipPath id="{uid}">{rect(x+inset,y+inset,w-inset*2,h-inset*2-4,"white",8)}</clipPath><mask id="{uid}Bezel" maskUnits="userSpaceOnUse" x="0" y="0" width="720" height="1280">{rect(0,0,720,1280,"white")}{rect(x+inset,y+inset,w-inset*2,h-inset*2-4,"black",8)}</mask></defs>'
 return defs+monitor(x,y,w,h,old=old)+f'<g clip-path="url(#{uid})">{content}</g>'+f'<g mask="url(#{uid}Bezel)">'+image_prop(name,ix,iy,iw*sx,992*sy,clip,layer="foreground-bezel")+'</g>'

def mic(x,y,s=1):
 # Original capsule on its authored silhouette; the rejected cleanup PNG is
 # not used. Transparent negative space in the U mount remains intact.
 return image_prop('microphone',x-43*s,y,139*s,209*s,'artMic')
def stool(x,y,w=205,h=145):
 return image_prop('stool',x,y,w,h,'artStool')

def workbench(x,y,w,ground=967):
 depth=max(25,ground-y)
 b=path(f'M29 12L49 13L43 {depth}H25Z','#614E41',1,'#80634D')+path(f'M{w-48} 13H{w-28}L{w-22} {depth}H{w-41}Z','#614E41',1,'#80634D')
 b+=path(f'M42 {depth*.58}L{w-37} {depth*.58+2}','#95795E',10)+path(f'M0 3L{w*.36} 0L{w} 2L{w-2} 20L3 18Z','#6D5745',1,'#A88666')+path(f'M4 5Q{w*.37} 2 {w-4} 6','#D8B28C',3)
 b+=path(f'M15 14Q{w*.27} 11 {w*.49} 14M{w*.63} 14L{w-12} 13','#715540',1,extra='opacity=".45"')
 return g(b,x,y)

_base_backdrop=backdrop
def backdrop(color,kind='room',f=0):
 b=_base_backdrop(color,kind,f)
 # Large cut-paper wall panels, skirting and real wood direction. Materials
 # are quiet behind interfaces, richer at the room's exposed edge.
 if kind!='tiles':
  b+=path('M9 272L9 955M710 272L710 955','#EEE5D3',2,extra='opacity=".17"')
  b+=path('M0 958Q210 954 430 958L720 955V970H0Z','#514B47',0,'#514B47')
 else:
  for j,(x,y) in enumerate([(72,364),(288,512),(576,734),(144,882)]):
   b+=path(f'M{x+5} {y+7}L{x+59} {y+6}M{x+7} {y+10}V{y+61}','#F2EADC',2,extra='opacity=".45"')
 for i in range(5):
  xx=39+i*146;yy=989+(i%3)*16
  b+=path(f'M{xx} {yy}Q{xx+35} {yy-3} {xx+62} {yy+1}M{xx+3} {yy+6}Q{xx+30} {yy+3} {xx+67} {yy+6}','#A69C85',1,extra='opacity=".25"')
 return b

def speaking_face(f,pleased=False):
 mint='#A6E5D6';phase=[0,1,2,1,3,2,0,1][(f//3)%8]
 blink=f%53 in (20,21)
 gaze=13 if f%24<17 else 2
 eyes=(path('M394 337L449 337M575 337L630 337',mint,13) if blink else f'<ellipse cx="{419+gaze}" cy="335" rx="13" ry="23" fill="{mint}"/><ellipse cx="{601+gaze}" cy="335" rx="13" ry="23" fill="{mint}"/>')
 if pleased:eyes=path('M386 341Q419 303 454 341M567 341Q601 303 636 341',mint,16)
 mouth=[path('M483 402Q515 419 547 402',mint,12),'<ellipse cx="516" cy="402" rx="21" ry="28" fill="'+mint+'"/>',path('M483 385Q518 375 550 386Q538 434 514 433Q490 432 483 385Z',mint,1,mint),path('M485 402L545 402',mint,15)][phase]
 return f'<g data-part="faceState" data-state="speaking-{phase}">{eyes}{mouth}<ellipse cx="360" cy="386" rx="13" ry="8" fill="{CORAL}"/><ellipse cx="666" cy="386" rx="13" ry="8" fill="{CORAL}"/></g>'

def bot(x,y,f,s=.245,face='happy',pose='standing',angle=0,jitter=True,contact=None,performance=None,impact=0,stretch=1):
 # The new feet anchor is the canonical shoe underside (904), not its joint
 # (861). Impact and secondary acting are deterministic and local.
 head=round(math.sin(f*.14)*1.4,1);over={'tilt':0,'body_y':0,'head_tilt':head}
 if performance in ('talking','accepted-speaking'):
  head=round(5+math.sin(f*.32)*3,1);over.update(head_tilt=head,l=(359,669,'mitten'),r=(683,617+12*math.sin(f*.26),'open'));pose='standing';face='neutral';jitter=False
  if performance=='accepted-speaking':over.update(head_tilt=-4+2*math.sin(f*.26),l=(350,600,'open'),r=(683,577,'open'));face='proud'
 elif performance=='strained':
  pose='thinking';face='worried';over.update(head_tilt=9,l=(393,659,'fist'),r=(643,646,'fist'));angle=0;jitter=False
  impact=max(impact,.19+.035*math.sin(f*.39))
 elif performance=='record-anticipation':
  pose='standing';face='thinking';over.update(head_tilt=6,l=(377,652,'mitten'),r=(657,631,'mitten'));impact=.21;jitter=False
 elif performance=='relieved':
  pose='celebrating';face='proud';over.update(head_tilt=-4,l=(339,594,'open'),r=(685,581,'open'));jitter=False
 elif performance=='startled-planted':
  pose='standing';face='shocked';over.update(head_tilt=-8,l=(350,547,'open'),r=(685,561,'open'));angle=0;jitter=False
 if contact:
  a=math.radians(angle);dx=contact[0]-x;dy=contact[1]-y
  over['r']=(512+(dx*math.cos(a)+dy*math.sin(a))/s,904+(-dx*math.sin(a)+dy*math.cos(a))/s,'point')
 body,_=assemble_pose(pose,face,over)
 body=re.sub(r'id="[^"]+"','',body).replace('<path ','<path data-layout-ignore ')
 if performance in ('talking','accepted-speaking'):
  facial=speaking_face(f,performance=='accepted-speaking')
  body,replacements=re.subn(r'<g\s+data-part="faceState"[^>]*>.*?</g>',facial,body,flags=re.S)
  if replacements!=1:raise RuntimeError('Speaking face must replace exactly one canonical face group')
 antenna=(math.sin(f*.32-.8)*3 if performance in ('talking','accepted-speaking') else 0)+impact*13
 body=body.replace('data-part="antennae">',f'data-part="antennae" transform="rotate({antenna:.2f} 512 207)">')
 squash=1-.13*max(-.5,min(.85,impact))
 return g(g(g(body,-512,-904),s=1/math.sqrt(squash),sy=squash*math.sqrt(squash)),x,y,angle,s,sy=stretch)

def caption_frame(groups,f,font):
 from motif_ui_production import font_width
 t=f/30;c=next((c for c in groups if c['start']<=t<c['end']),None)
 if c is None:return ''
 visible=[w for w in c['words'] if t+.0001>=w['start']]
 if not visible:return ''
 size=51;full=sum(font_width(font,w['text'],size)+18 for w in c['words'])+6*(len(c['words'])-1)
 if full>650:size*=650/full
 widths=[font_width(font,w['text'],size)+18 for w in visible];x=(720-sum(widths)-6*(len(widths)-1))/2;b=''
 for i,(w,width) in enumerate(zip(visible,widths)):
  age=(t-w['start'])*30;scale=.82+.18*spring(age/6);angle=[-1.7,1.0,-.65,1.45][i%4]
  tile=card(width,65,'#CC744F',.07)+txt(w['text'],width/2,48,size,'#FFF4DD',700,'middle',True)
  b+=g(g(tile,-width/2,-32),x+width/2,1040,angle,scale);x+=width+6
 return b

def keyboard(x,y,active=None):
 rows=['QWERTYUIOP','ASDFGHJKL','ZXCVBNM'];b='';positions={}
 for row,letters in enumerate(rows):
  offset=(10-len(letters))*17
  for k,letter in enumerate(letters):
   xx=x+offset+k*34;yy=y+row*49;pressed=active==letter;dy=6 if pressed else 0
   b+=path(f'M{xx+1} {yy+8}L{xx+29} {yy+7}L{xx+30} {yy+44}L{xx+2} {yy+45}Z','#ABA794',1,'#ABA794')
   b+=g(card(29,37,GOLD if pressed else '#FAF6E9',.04),xx,yy+dy)+txt(letter,xx+14.5,yy+26+dy,18,INK,anchor='middle')
   positions[letter]=(xx+15,yy+dy)
 return b,positions
# ---------------------------------------------------------------------------
# v4: local hero art direction. Canonical geometry and engine remain unchanged.
# ---------------------------------------------------------------------------
import json
from pathlib import Path
_v3_image_prop=image_prop
_v3_monitor=monitor
_v3_mic=mic
_v3_stool=stool
_v3_waveform=waveform
ART=Path(__file__).resolve().parents[1]/'assets/art-v4'
BITMAPS=json.loads((ART/'bitmap-layouts.json').read_text()) if (ART/'bitmap-layouts.json').exists() else {}

def art_bitmap(name,x,y,w,h,layer='backing',crop_height=None):
 iw,ih=BITMAPS[name]['dimensions']
 # The renderer awaits these HTML background decodes before screenshotting.
 url=f'/assets/art-v4/{name}.webp?layer={layer}'
 body=f'<foreignObject width="{iw}" height="{ih}"><img xmlns="http://www.w3.org/1999/xhtml" src="{url}" width="{iw}" height="{ih}" style="width:{iw}px;height:{ih}px;background-image:url({url});background-size:100% 100%;background-repeat:no-repeat"/></foreignObject>'
 if crop_height is not None:
  uid='v4LaptopCase'
  body=f'<defs><clipPath id="{uid}">{rect(0,0,iw,crop_height,"white")}</clipPath></defs><g clip-path="url(#{uid})">{body}</g>'
 return g(body,x,y,s=w/iw,sy=(h/ih)/(w/iw))

def tape(w=64,h=20,c='#C6AE78'):
 d=f'M1 2L{w*.29} 0L{w-2} 2L{w} {h-3}L{w*.64} {h}L2 {h-1}L0 8Z'
 return path(d,'#716049',0,'#716049',extra='transform="translate(1 2)" opacity=".12"')+path(d,c,0,c,extra='opacity=".87"')+path(f'M5 4L{w-6} 5',CREAM,.8,extra='opacity=".33"')

def card(w,h,color=CREAM,grain=.10,r=8):
 k=int(w*3+h*5+sum(map(ord,color)))%5
 cut=min(5,h*.10)
 d=f'M1 {cut+1}Q2 1 7 1L{w*.34} .3L{w-8} 1.7L{w-1} {cut+2}L{w-.3} {h*.63}L{w-3} {h-1}L{w*.59} {h+.7}L7 {h-1}L.5 {h-cut}Z'
 b=path(d,'#31291F',0,'#31291F',extra='transform="translate(2 4)" opacity=".14"')+path(d,'#B8AA91',.7,'#CCBDA3',extra='transform="translate(.6 2.3)"')+path(d,color,.5,color)
 # Local paper print, not a new global grain layer.
 if color not in (INK,PANEL,'#241D29'):b+=path(d,color,0,'url(#worldPaper)',extra=f'opacity="{grain*.43}"')
 if w>65 and h>35:b+=path(f'M7 {h-2}Q{w*.22} {h-.2} {w*.48} {h-1.5}M{w*.72} {h-2}L{w-6} {h-3}','#AF9F83',.65,extra='opacity=".43"')
 return b

def headline(text):
 words=text.split();lines=[text]
 if len(text)>36:
  mid=min(range(1,len(words)),key=lambda i:abs(len(' '.join(words[:i]))-len(' '.join(words[i:]))));lines=[' '.join(words[:mid]),' '.join(words[mid:])]
 h=72 if len(lines)==1 else 100;y=183 if len(lines)==1 else 168
 body=card(680,h)+g(tape(64,21),13,-7,a=-12)+g(tape(69,19,'#D0BC88'),598,-6,a=9)
 for i,line in enumerate(lines):body+=txt(line,340,46+i*34 if len(lines)==2 else 49,min(32,620/(max(1,len(line))*.57)),INK,900,'middle')
 return g(body,20,y,a=-.4)

def monitor(x,y,w=580,h=360,laptop=False,old=False):
 if old or 'monitor' not in BITMAPS:return _v3_monitor(x,y,w,h,laptop,old)
 iw,ih=BITMAPS['monitor']['dimensions'];left,top,right,bottom=BITMAPS['monitor']['screen']
 sx=(w-28)/(right-left);sy=(h-32)/(bottom-top)
 b=art_bitmap('monitor',x+14-left*sx,y+14-top*sy,iw*sx,ih*sy,layer='laptop-shell' if laptop else 'backing',crop_height=778 if laptop else None)
 if laptop:
  deck=path(f'M0 0L-24 43Q{w/2} 54 {w+24} 43L{w} 0Z','#9A907A',1,'#D9D0BC')+path(f'M-18 42L{w+17} 42','#8D806E',4)+path(f'M{w*.39} 32H{w*.61}','#B9AE98',9)
  for i in range(11):deck+=path(f'M{w*.10+i*w*.073} 9L{w*.08+i*w*.077} 22','#A69D8C',3)
  b+=g(deck,x,y+h+51)
 return b

def physical_monitor(x,y,w,h,content,old=False):
 inset=30 if old else 14;uid='v4OldDisplay' if old else 'v4Display'
 backing=monitor(x,y,w,h,old=old)
 mask=rect(x+inset,y+inset,w-2*inset,h-2*inset-4,'white',8)
 defs=f'<defs><clipPath id="{uid}">{mask}</clipPath><mask id="{uid}Rim" maskUnits="userSpaceOnUse" x="0" y="0" width="720" height="1280">{rect(0,0,720,1280,"white")}{rect(x+inset,y+inset,w-2*inset,h-2*inset-4,"black",8)}</mask></defs>'
 foreground=backing.replace('?layer=backing','?layer=foreground-bezel')
 # Raster backing, exact editable display, separately masked foreground rim.
 b=defs+backing+f'<g clip-path="url(#{uid})">{content}</g>'+f'<g mask="url(#{uid}Rim)">{foreground}</g>'
 if old:
  b+=g(tape(45,15,'#C0B496'),x+31,y+h-19,a=-4)+path(f'M{x+w-65} {y+h-15}h20m-20 5h20','#786B55',1)
 return b

def mic(x,y,s=1):
 b=_v3_mic(x,y,s)
 # Deliberate socket and layered mount pin; connection is a physical point.
 b+=g(path('M35 123L42 122L44 132L37 134Z','#735F48',1,'#CDBA9B')+path('M41 130L44 143','#213E42',4)+path('M-23 86L-18 86M-18 87V99','#CDBBA0',2),x,y,s=s)
 return b

def stool(x,y,w=205,h=145):
 b=_v3_stool(x,y,w,h)
 # Supporting feet and one offset brace deepen the original paper-wood master.
 b+=g(path('M19 135L46 134L48 144L17 145Z','#293F50',1,'#496D83')+path('M158 132L185 134L188 143L158 142Z','#293F50',1,'#496D83')+path('M40 99L160 96','#8EACB5',3)+path('M43 102L157 99','#3D6377',3),x,y,s=w/205,sy=(h/145)/(w/205))
 return b

def voice_wave(x,y,w,h,f,reveal=1):
 b='';n=39;visible=max(1,int(n*clamp(reveal)))
 for i in range(visible):
  envelope=[.43,.78,.55,1,.65,.84,.45][i%7]*(.3+.7*math.sin(math.pi*(i+.5)/n)**.5)
  signal=.30+.70*abs(math.sin(i*1.73-f*.27)*.67+math.sin(i*.46+f*.12)*.33)
  bh=max(8,h*envelope*signal);xx=x+i*w/n+[0,.6,-.4,.2][i%4]
  b+=rect(xx,y+(h-bh)/2,[4.5,5.8,4.8,5.1][i%4],bh,PINK,2.5)
 return b

def impact_marks(x,y,f,start,kind='paper',variant=0,weight=1):
 age=f-start
 if age<0:return ''
 # Authored distributions: one hero, two medium, three short supporting marks.
 params=[(-.95,70,1.75,15,-23),(.31,46,.85,10,17),(2.63,39,.70,13,-34),(-2.07,53,.28,7,11),(.91,49,.36,8,-16),(3.38,38,.25,6,27)]
 b=''
 for i,(theta,travel,size,life,spin) in enumerate(params):
  if age>=life:continue
  u=age/life;theta+=variant*.43;distance=10+travel*(1-(1-u)**2)
  xx=x+math.cos(theta)*distance;yy=y+math.sin(theta)*distance+18*u*u
  c=[GOLD,PINK,CREAM,GOLD,CREAM,PINK][i];alpha=min(1,(life-age)/3)
  if kind=='voice':mark=path('M-12 -3Q-5 -17 0 0Q6 17 14 -2',c,5)+path('M-3 -8L-1 7',c,2)
  elif i==0:mark=path('M0 -19L7 -7L22 -3L9 6L5 21L-3 9L-18 8L-9 -3L-11 -17Z',c,0,c)
  elif i<3:mark=star(0,0,1,c)
  else:mark=path('M-4 -6L4 5M-6 3L5 -2',c,2)
  b+=g(mark,xx,yy,a=spin*u+variant*11,s=size*weight*(.65+.35*math.sin(math.pi*clamp(age/3))),opacity=alpha)
 return b

def burst(x,y,f,start,seed=0,count=7):
 return impact_marks(x,y,f,start,'paper',seed%5,weight=.9 if count<6 else 1)

PERFORMANCES=('talking','anticipating','impact','worried','relieved','surprised','focused')
def performance_face(state,f,gaze=1):
 c='#A6E5D6';dx=12*gaze if state in ('focused','talking') else 0
 if state=='talking':return speaking_face(f,False)
 if state=='relieved':eyes=path('M383 340Q419 298 456 340M564 340Q601 298 638 340',c,18);mouth=path('M479 391Q515 430 552 391',c,14)
 elif state=='worried':eyes=path('M385 321Q415 302 451 322M569 322Q602 301 638 321',c,15);mouth=path('M483 420Q516 394 550 420',c,14)
 elif state=='surprised':eyes=f'<ellipse cx="419" cy="333" rx="19" ry="29" fill="{c}"/><ellipse cx="601" cy="333" rx="19" ry="29" fill="{c}"/>';mouth=f'<ellipse cx="514" cy="408" rx="24" ry="30" fill="{c}"/>'
 elif state=='impact':eyes=path('M384 337L452 331M568 331L635 337',c,17);mouth=path('M490 406Q516 414 543 406',c,15)
 elif state=='anticipating':eyes=path('M383 329L451 342M568 342L636 329',c,15);mouth=path('M491 406L543 406',c,13)
 else:eyes=f'<ellipse cx="{419+dx}" cy="337" rx="18" ry="17" fill="{c}"/><ellipse cx="{601+dx}" cy="337" rx="18" ry="17" fill="{c}"/>';mouth=path('M486 408Q515 421 544 406',c,12)
 return f'<g data-part="faceState" data-state="v4-{state}">{eyes}{mouth}</g>'

def bot(x,y,f,s=.245,face='happy',pose='standing',angle=0,jitter=True,contact=None,performance=None,impact=0,stretch=1,acting_frame=None,contact_hand='r',gaze=1):
 state={'strained':'worried','startled-planted':'surprised','record-anticipation':'anticipating','accepted-speaking':'relieved'}.get(performance,performance)
 if state not in PERFORMANCES:state='worried' if face=='worried' else 'surprised' if face in ('shocked','surprised') else 'focused' if face in ('thinking','determined') else None
 t=f if acting_frame is None else acting_frame;head=0;antenna=0;over={'tilt':0,'body_y':0}
 if state=='talking':
  head=7+3*math.sin(t*.38);antenna=5*math.sin(t*.38-1.1);over.update(l=(351,683,'mitten'),r=(711,593+9*math.sin(t*.24),'open'));pose='standing';angle+=2
 elif state=='anticipating':
  head=12;antenna=-13;over.update(l=(399,689,'fist'),r=(627,677,'fist'));pose='standing';impact=max(impact,.74)
 elif state=='impact':
  head=-8*math.exp(-max(0,t)/4);antenna=17*math.exp(-max(0,t)/5);over.update(l=(347,633,'open'),r=(699,621,'open'));pose='standing';impact=max(impact,.80*math.exp(-max(0,t)/3))
 elif state=='worried':
  head=12;antenna=-18;over.update(l=(414,678,'fist'),r=(615,667,'fist'));pose='standing';impact=max(impact,.66);angle-=5
 elif state=='relieved':
  head=-9+2*math.sin(t*.17);antenna=4;over.update(l=(309,580,'open'),r=(726,559,'open'));pose='standing';impact=min(impact,-.16)
 elif state=='surprised':
  head=-11;antenna=19;over.update(l=(326,513,'open'),r=(716,512,'open'));pose='standing';impact=min(impact,-.28)
 elif state=='focused':
  head=8;antenna=-5;over.update(l=(357,663,'mitten'),r=(700,597,'point'));pose='standing';angle+=3
 over['head_tilt']=round(head,2)
 # Held/contact hand uses inverse of the resulting whole-pose transform.
 squash=1-.18*max(-.32,min(.9,impact));sx=1/math.sqrt(squash);sy=squash*sx
 if contact:
  a=math.radians(angle);dx=contact[0]-x;dy=contact[1]-y
  over[contact_hand]=(512+(dx*math.cos(a)+dy*math.sin(a))/(s*sx),904+(-dx*math.sin(a)+dy*math.cos(a))/(s*sy*stretch),'point')
 body,_=assemble_pose(pose,face if state is None else 'neutral',over);body=re.sub(r'id="[^"]+"','',body).replace('<path ','<path data-layout-ignore ')
 if state:
  facial=speaking_face(t,True) if performance=='accepted-speaking' else performance_face(state,t,gaze)
  body,n=re.subn(r'<g\s+data-part="faceState"[^>]*>.*?</g>',facial,body,flags=re.S);assert n==1
 body=body.replace('data-part="antennae">',f'data-part="antennae" transform="rotate({antenna:.2f} 512 207)">')
 return g(g(g(body,-512,-904),s=sx,sy=sy/sx),x,y,angle,s,sy=stretch)

def free_ticket(f):
 u=spring((f-44)/7)
 # Die-cut price ticket, tan backing, punched edge and overlapping tape.
 d='M0 7L145 0L170 13L174 72L159 82L9 80L-5 61L0 48L-4 34L1 22Z'
 b=path(d,'#1C4C38',1,'#1C4C38',extra='transform="translate(3 5)"')+path(d,'#247648',1,'#2A915A')+path('M9 68L158 70','#8ACA91',2)
 b+=txt('FREE',84,57,47,CREAM,900,'middle')+g(tape(41,15,'#B3C6AA'),16,-7,a=-6)
 return g(b,489,265,a=-8+8*math.exp(-max(0,f-44)/4),s=.64+.36*u)

def page_piece(i):
 w=[74,61,83][i];h=[88,81,91][i]
 d=f'M1 5Q20 -3 {w-17} 1L{w-1} 17L{w+2} {h-7}Q{w*.55} {h+5} 3 {h-2}L-2 {h*.48}Z'
 b=path(d,'#9D8970',1,'#CEBFA4',extra='transform="translate(1 3)"')+path(d,'#C1B299',.8,CREAM)
 b+=path(f'M{w-17} 1Q{w-20} 15 {w-1} 17L{w-17} 17Z','#B5A68A',1,'#DFD0B4')
 for j in range(3):b+=path(f'M11 {27+j*14}Q{w*.43} {23+j*14} {w-15} {27+j*14}','#B5AA96',2)
 return b

def book_art(x,y,w=279,h=153,opened=True):
 if opened and 'book' in BITMAPS:return art_bitmap('book',x,y,w,h)
 b=path('M3 5L199 0L207 126L11 136Z','#743E37',2,'#B9604D')+path('M8 131L202 121',CREAM,8)+path('M14 12L19 125','#663B37',9)+path('M26 14L188 9L196 112L33 122Z','#CB8165',2)
 b+=path('M60 39L149 34M66 52L147 49','#E9CDB1',2)+txt('BOOK',111,89,30,CREAM,900,'middle')
 return g(b,x,y,s=w/207,sy=(h/136)/(w/207))

def phone_shell():
 # A physical comment kiosk: blue card backing, pale front rim, lower foot.
 d='M173 281Q143 284 140 319L143 919Q142 970 177 982L548 978Q588 972 589 930L583 323Q582 285 548 279Z'
 b=path(d,'#3D6371',1,'#567D88',extra='transform="translate(7 6)"')+path(d,'#B7B19F',1,'#E9DECA')
 b+=path('M173 301Q156 302 157 329L155 919Q155 953 182 958H542Q568 952 567 924L566 329Q566 304 542 301Z',INK,1,INK)
 b+=rect(164,308,395,640,'#F4EFDF',25)+path('M175 947L548 945','#B4A58F',4)+rect(292,308,142,22,INK,10)
 b+=g(tape(48,17,'#B8C7B4'),147,373,a=-4)+path('M578 439V468','#5F757C',6)+path('M578 488V507','#5F757C',6)
 b+=path('M174 974L146 995L586 996L547 974Z','#597C80',1,'#779995')+path('M157 995H575','#3F6063',5)
 return b
