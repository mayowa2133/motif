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
 d=f'M3 4L{w*.34} 0L{w-4} 3L{w} {h*.61}L{w-3} {h-1}L{w*.62} {h+2}L0 {h-2}Z'
 return path(d,EDGE,2,color,extra='transform="translate(5 7)" opacity=".28"')+path(d,color,1,color)+path(d,color,0,'url(#worldPaper)',extra=f'opacity="{grain}"')+path(f'M3 {h-2}L{w-3} {h-1}',EDGE,2)
def headline(text):
 # The longer labels use two readable lines instead of tiny one-line text.
 words=text.split();lines=[text]
 if len(text)>36:
  mid=min(range(1,len(words)),key=lambda i:abs(len(' '.join(words[:i]))-len(' '.join(words[i:]))))
  lines=[' '.join(words[:mid]),' '.join(words[mid:])]
 h=72 if len(lines)==1 else 100;y=183 if len(lines)==1 else 168
 body=card(680,h)+g(card(65,21,'#C8B078',.04),12,-8,-10)+g(card(65,21,'#C8B078',.04),600,-7,12)
 for i,line in enumerate(lines):
  size=min(32,620/(max(1,len(line))*.57))
  body+=txt(line,340,46+i*34 if len(lines)==2 else 49,size,INK,900,'middle')
 return g(body,20,y,a=-.4)
def backdrop(color,kind='room',f=0):
 b=rect(0,0,720,1280,color)+rect(0,0,720,1280,'url(#worldPaper)')
 # Quiet real texture composited at reduced strength, no visible tiled blotch.
 b=rect(0,0,720,1280,color)+g(rect(0,0,720,1280,'url(#worldPaper)'),opacity=.19)
 b+=rect(0,983,720,297,'#775340')+rect(0,967,720,22,'#B78662')+path('M0 984H720','#553C34',3)
 b+=g(rect(0,987,720,293,'url(#worldPaper)'),opacity=.16)
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
 return g(card(116,76,PINK,.05)+waveform(15,10,86,26,11,n=12)+txt(label,58,61,17,INK,700,'middle'),x,y,a,s)
def monitor(x,y,w=580,h=360,laptop=False):
 b=rect(6,8,w,h,'#121015',18)+rect(0,0,w,h,'#151318',17)+rect(14,16,w-28,h-35,PANEL,9)+path(f'M20 9H{w-24}','#4D4850',2)
 if laptop:
  b+=path(f'M0 {h-3}L-33 {h+37}L{w+33} {h+37}L{w} {h-3}Z','#999995',2,'#C5C4BE')+rect(w*.33,h+15,w*.34,15,'#ADADA8',4)+path(f'M-25 {h+38}H{w+25}','#777778',4)
 else:b+=rect(w*.43,h-2,w*.14,94,'#2B2730',3)+path(f'M{w*.29} {h+98}L{w*.73} {h+98}L{w*.65} {h+83}L{w*.36} {h+83}Z',INK,2,'#343139')
 return g(b,x,y)
def app(x,y,w,h,f,progress=None,done=False,label='Voice cloning',pressed=False):
 b=txt(label,x+28,y+50,24)+txt('Voice sample',x+w-30,y+51,16,PINK,anchor='end')+path(f'M{x+25} {y+71}H{x+w-25}','#554350',2)
 b+=txt('Voice · VoiceStudio Demo Voice',x+29,y+99,14,'#ADA2AC')+txt('Script',x+29,y+134,18)
 b+=button('Synthesize audio',x+w-236,y+h-78,206,44,pressed=pressed)+txt('Auto ▾',x+30,y+h-48,17,'#CAC1C9')
 if progress is not None:
  b+=rect(x+33,y+h-131,w-153,9,'#4C394B',5)+rect(x+33,y+h-131,(w-153)*clamp(progress),9,MAGENTA,5)+ring(x+w-66,y+h-126,22,progress,f,done)
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
  a=k*2.399+seed*.1;r=(18+85*u)*(1+.3*math.sin(k*9));xx=x+math.cos(a)*r;yy=y+math.sin(a)*r+45*u*u
  b+=g(star(0,0,.4+.5*((k*13)%9)/9,[CREAM,PINK,GOLD][k%3]),xx,yy,a=age*4+k*11,opacity=(1-u)**.7)
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
def bot(x,y,f,s=.245,face='happy',pose='standing',angle=0,jitter=True,contact=None):
 # y is feet level; override hand inverse uses exact same final world transform.
 if jitter:x+=living(f,791,1.0);y+=living(f,802,.8);angle+=living(f,821,.6)
 body=bot_body(pose,face,round(math.sin(f*.15)*2))
 if contact:
  a=math.radians(angle);dx=contact[0]-x;dy=contact[1]-y
  local=(512+(dx*math.cos(a)+dy*math.sin(a))/s,861+(-dx*math.sin(a)+dy*math.cos(a))/s,'point')
  body,_=assemble_pose(pose,face,{'tilt':0,'body_y':0,'head_tilt':0,'r':local})
  body=re.sub(r'id="[^"]+"','',body).replace('<path ','<path data-layout-ignore ')
 return g(g(body,-512,-861),x,y,angle,s)
def hop(f,start,end,x1,y1,x2,y2,height=75):
 u=clamp((f-start)/max(1,end-start));return(x1+(x2-x1)*u,y1+(y2-y1)*u-height*math.sin(math.pi*u))
def receipt(x,y,a=0):return g(card(63,65,'#F5EFDF')+txt('Starter',31,25,12,INK,anchor='middle')+txt('Paid',31,46,13,GREEN,anchor='middle'),x,y,a)
def pricing(f,cancel=False):
 b=g(card(611,463),37,330)+txt('ElevenLabs / Pricing',67,379,26,INK,900)
 b+=path('M53 405H632M329 414V748','#B7AE9B',2)
 b+=txt('Free',251,447,30,INK,900,'middle')+txt('Starter',483,447,30,INK,900,'middle')
 b+=txt('Text to speech',67,512,17,INK)+txt('Voice cloning',67,586,17,INK)
 b+=check(250,507,.58)+check(480,507,.58)+cross(251,582,.69+(0.18*math.sin((f-13)/12*math.pi) if 13<f<25 and not cancel else 0))
 accepted=cancel or f>=42
 if accepted:b+=check(480,583,.66)+token(394,611,s=.78)
 b+=txt('billed monthly',481,706,17,INK,anchor='middle')
 state='Cancelled' if cancel and f>=24 else 'Cancel plan' if cancel else 'Subscribed' if f>=38 else 'Upgrade'
 b+=button(state,389,726,189,45,color='#8D9C91' if state=='Cancelled' else GREEN if state=='Subscribed' else INK,pressed=(17<=f<=23 if cancel else 33<=f<=37))
 b+=g(path('M-14 -9A18 18 0 1 1 -16 8M-14 -9L-23 -6M-14 -9L-13 -20',INK,3),609,747,a=0 if cancel and f>=24 else f*7)
 total=5 if cancel else max(0,min(5,(f-44)//5+1))
 for i in range(total):b+=receipt(650+(i%2)*3,725+i*37,living(f,51+i,.9) if cancel else -4+i*1.6)
 return b

def chapter_row(x,y,label,f,phase=0):return g(rect(0,0,490,77,'#3F2B3B',9)+txt(label,61,32,23)+'<circle cx="29" cy="37" r="17" fill="'+MAGENTA+'"/>'+path('M24 28L37 37L24 46Z',PINK,1,PINK)+waveform(182,17,285,44,f,n=29,phase=phase),x,y)
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
