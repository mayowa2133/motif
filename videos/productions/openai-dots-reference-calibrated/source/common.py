"""Production-scoped paper primitives; canonical Motif puppet reused verbatim.
720×1280 authoring coordinates. Essential actions stay x48..672,y160..1055.
No mutable animation state. Choreography is a pure function of measured time.
"""
import math,re
from functools import lru_cache
from html import escape
from motif_performance import render,channels
from motif_reaction import matrix,compose
from build_motif_bot import DEFS as BOT_DEFS
INK='#202C32';CREAM='#F4EBD8';EDGE='#DCCDB3';TEAL='#56BFB1';DARK='#254D50';MINT='#A6E5D6';CORAL='#DF806B';GOLD='#EBC46B';SLATE='#64869A';PLUM='#554565'
DEFS=BOT_DEFS.removeprefix('<defs>').removesuffix('</defs>')+'<pattern id="worldPaper" width="1365" height="1365" patternUnits="userSpaceOnUse"><image href="assets/materials/world-paper.webp" width="1365" height="1365"/></pattern>'
def clamp(x):return max(0,min(1,x))
def ease(x):return 1-(1-clamp(x))**3
def ramp(t,start,d=.35):return ease((t-start)/max(.001,d))
def impulse(t,start,d=.45):
 u=(t-start)/d
 return math.sin(u*math.pi*4)*math.exp(-u*5)*(1-u) if 0<=u<=1 else 0

def g(body,x=0,y=0,s=1,a=0,opacity=1,sy=1):
 return f'<g opacity="{opacity:.5f}" transform="translate({x:.4f} {y:.4f}) rotate({a:.4f}) scale({s:.5f} {s*sy:.5f})">{body}</g>'
def path(d,color=INK,sw=3,fill='none',extra=''):
 return f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" {extra}/>'
def rect(x,y,w,h,fill,r=0):return f'<rect x="{x}" y="{y}" width="{max(0,w)}" height="{max(0,h)}" rx="{r}" fill="{fill}"/>'
def text(label,x,y,size=30,color=INK,anchor='start',weight=700,serif=False):
 return f'<text x="{x}" y="{y}" font-family="'+('EB Garamond' if serif else 'Inter')+f'" font-size="{size}" font-weight="{weight}" fill="{color}" text-anchor="{anchor}">{escape(label)}</text>'
def card(w,h,color=CREAM):
 d=f'M3 5Q{w*.26} -1 {w*.5} 2L{w-5} 1Q{w+1} 2 {w} 11L{w-2} {h-4}Q{w-1} {h+2} {w-9} {h}L{w*.45} {h-1}L2 {h}Z'
 return path(d,INK,0,INK,'transform="translate(5 7)" opacity=".15"')+path(d,EDGE,0,EDGE,'transform="translate(2 3)"')+path(d,color,0,color)+path(d,color,0,'url(#worldPaper)','opacity=".13"')
def backdrop(color=GOLD,kind='stage'):
 b=rect(0,0,720,1280,color)+g(rect(0,0,720,1280,'url(#worldPaper)'),opacity=.18)
 if kind!='isolated':
  b+=path('M0 992Q342 987 720 995L720 1280H0Z',INK,0,INK,'opacity=".12"')+path('M0 995Q341 990 720 998',CREAM,5,extra='opacity=".35"')
 return b

def dot(x=0,y=0,r=30,t=0,working=True):
 # Small cream token with an asymmetric teal notch; conceptual, not official avatar.
 d=f'M{-r} 0A{r} {r} 0 1 1 {r} 0A{r} {r} 0 1 1 {-r} 0'
 b=path(d,INK,0,INK,'transform="translate(3 5)" opacity=".16"')+path(d,EDGE,3,CREAM)
 b+=path(f'M{-r*.45} {-r*.86}Q{-r*.7} {-r*.55} {-r*.92} {-r*.2}',TEAL,max(5,r*.18))
 b+=text('DOT',0,r*.16,max(12,r*.43),INK,'middle',900)
 if working:b+=f'<circle cx="{r*.62}" cy="{r*.59}" r="{r*.09}" fill="{TEAL}"/>'
 return g(b,x,y,a=math.sin(math.floor(t*10)*.61)*1.1)

def icon(kind,x=0,y=0,s=1,color=INK):
 shapes={'mail':path('M-28 -19H28V19H-28Z M-28 -19L0 3L28 -19',color,4),'calendar':path('M-25 -22H25V24H-25Z M-25 -9H25 M-14 -30V-15M14 -30V-15 M-12 2H-6M6 2H12M-12 13H-6',color,4),'folder':path('M-29 -15H-7L1 -23H25L31 25H-31Z',color,4),'check':path('M-20 0L-5 15L25 -20',color,7),'lock':path('M-20 -5H20V26H-20Z M-13 -5V-18Q0 -40 13 -18V-5 M0 6V17',color,5),'key':path('M-11 0A17 17 0 1 1 -11 -.1M5 0H37M26 0V12M36 0V9',color,6),'cloud':path('M-25 15Q-45 15 -38 -4Q-33 -16 -19 -12Q-15 -39 8 -33Q27 -29 27 -11Q45 -9 39 12Q33 20 18 18H-25Z',color,4),'person':f'<circle cy="-15" r="13" fill="{color}"/>'+path('M-24 27Q-26 3 0 3Q26 3 24 27Z',color,0,color),'spark':path('M0 -28L7 -7L28 0L7 7L0 28L-7 7L-28 0L-7 -7Z',color,2,color)}
 if kind not in shapes:raise ValueError('unknown icon '+kind)
 return g(shapes[kind],x,y,s)

def keyboard(x,y,w=260,press=-1):
 b=card(w,60,EDGE)
 for i in range(20):
  row,col=divmod(i,10);b+=rect(10+col*(w-20)/10,9+row*21,(w-30)/10,16,TEAL if i==press else CREAM,3)
 return g(b,x,y)

def monitor(x,y,w=460,h=320,content='',cloud=False):
 b=card(w,h,INK)+rect(15,18,w-30,h-36,DARK,12)+content
 b+=rect(w*.44,h,w*.12,46,EDGE,4)+g(card(w*.4,16,CREAM),w*.3,h+38)
 if cloud:b+=g(icon('cloud',0,0,1.1,CREAM),w-50,-15)
 return g(b,x,y)

@lru_cache(maxsize=4096)
def _body(state,frame):return render(state,frame/30)
def bot(x,y,s=.34,state='focused',t=0,contacts=None,a=0):
 if state=='absent':return ''
 if contacts:
  # Include the acting body's own transform before solving hand anchors.
  c=channels(state,t);parent=matrix(x,y,a,s,s)
  local=compose(matrix(512,904),compose(matrix(rotation=c['angle'],sx=1/math.sqrt(c['sy']),sy=math.sqrt(c['sy'])),matrix(-512,-904)))
  m=compose(parent,local)
  binding={hand:{'prop_transform':matrix(px,py),'anchor':(0,0),'puppet_transform':m} for hand,(px,py) in contacts.items()}
  body=render(state,t,binding)
 else:body=_body(state,max(0,round(t*30)))
 return g(body,x,y,s,a)
