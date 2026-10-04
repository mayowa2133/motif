"""Provisional source-authored paper silhouettes for the live plan, not final art.
All new illustration is production-scoped. No external reference pixels/assets.
"""
from common import *

def capsule(w,h,color=CREAM):
 return path(f'M{h/2} 2Q0 0 3 {h/2}Q0 {h} {h/2} {h}H{w-h/2}Q{w+2} {h} {w} {h/2}Q{w+2} 0 {w-h/2} 2Z',EDGE,4,color)+path(f'M{h/2} 2Q0 0 3 {h/2}Q0 {h} {h/2} {h}H{w-h/2}Q{w+2} {h} {w} {h/2}Q{w+2} 0 {w-h/2} 2Z',color,0,'url(#worldPaper)','opacity=".16"')
def cloud(w=520):
 return path(f'M0 95Q-25 42 44 40Q69 -43 150 13Q196 -51 269 6Q332 -30 369 36Q451 -1 {w} 66Q{w+25} 108 {w-15} 131L35 142Q-8 140 0 95Z',EDGE,5,CREAM)
def banner(label,y=113,color=CREAM):
 words=label.split();rows=[label]
 if len(label)>27:
  best=min(range(1,len(words)),key=lambda i:abs(len(' '.join(words[:i]))-len(' '.join(words[i:]))));rows=[' '.join(words[:best]),' '.join(words[best:])]
 w=min(630,max(290,max(len(r) for r in rows)*24));h=74 if len(rows)==1 else 111;font=min(38,(w-35)/(max(len(r) for r in rows)*.62))
 return g(card(w,h,color),360-w/2,y,a=-1)+''.join(text(r,360,y+46+i*43,font,INK,'middle',900) for i,r in enumerate(rows))
def lines(x,y,w,count=4,color=SLATE):
 return ''.join(path(f'M{x} {y+i*24}h{w-(i%3)*22}',color,5) for i in range(count))
def laptop(x,y,w=210,open_=1):
 h=120+140*open_;lid=path(f'M0 0L{w} 12L{w-9} {h}L-6 {h-10}Z',EDGE,5,DARK)+path(f'M12 20L{w-14} 28L{w-22} {h-16}L12 {h-20}Z',SLATE,2,INK)
 lid+=icon('mail',w*.5,h*.48,.9,CREAM)+lines(30,h*.7,w-62,2,TEAL)
 return g(lid+path(f'M-6 {h-10}L{w-9} {h}L{w+18} {h+36}L-30 {h+24}Z',EDGE,3,CREAM)+keyboard(-16,h+9,w+10),x,y,a=-4)
def computer(x=232,y=435,w=418,h=300,content='',unfold=1):
 # A hinged paper lid is a changing quadrilateral, with a visible underside.
 depth=44+max(0,unfold)*(h-44);b=path(f'M0 {h}L{w} {h-12}L{w+18} {h+90}L-27 {h+72}Z',EDGE,5,TEAL)
 b+=path(f'M0 {h}L10 {h-depth}L{w-12} {h-depth+13}L{w} {h-12}Z',EDGE,5,DARK)
 if unfold>.28:
  b+=path(f'M22 {h-22}L29 {h-depth+24}L{w-29} {h-depth+35}L{w-20} {h-33}Z',TEAL,4,INK)
  b+=g(content,42,h-depth+46,opacity=clamp((unfold-.28)/.5))
 b+=keyboard(10,h+15,w-20);b+=path(f'M4 {h+68}Q{w*.55} {h+92} {w} {h+78}',DARK,4)
 return g(b,x,y,a=2)
def assignment(x,y,w=174,h=102,stage=0,pending=True):
 b=card(w,h,CREAM)+path(f'M{w-25} 1L{w+20} -24L{w+18} {h-23}L{w-23} {h}Z',EDGE,2,MINT)+path(f'M{w-25} 1V{h}',TEAL,3)
 for i in range(3):b+=rect(18+i*38,24,27,27,TEAL if i<stage else EDGE,4)
 b+=lines(18,68,w-40,1,SLATE)
 if pending:b+=path(f'M{w+14} -21L{w+43} -13L{w+38} 16L{w+13} 8Z',EDGE,2,GOLD)
 return g(b,x,y,a=-3)
def job_strip(x,y,advance=0):
 # Retained multi-panel ribbon; no vanished/squashed input material.
 b=''
 for i in range(3):b+=g(assignment(0,0,115,81,min(i+1,int(advance)+1),i==2),i*116,-i*5,a=(-1)**i*3)+path(f'M{i*116+111} 19l8 -4v53l-8 4',EDGE,4)
 return g(b,x,y)
def token(x,y,r=32,t=0,working=False,name=False):
 b=dot(0,0,r,t,working)+path(f'M{-r*.44} {-r*.87}Q{-r*.7} {-r*.54} {-r*.93} {-r*.14}',TEAL,max(9,r*.3))
 if not name:b=b.replace('>DOT</text>','>•</text>')
 return g(b,x,y)
def envelope(w=330,h=185,color=CORAL,label='',house=False):
 b=card(w,h,color)+path(f'M6 10L{w*.48} {h*.53}L{w-5} 6 M4 {h-4}L{w*.36} {h*.45}M{w-4} {h-3}L{w*.64} {h*.45}',CREAM,5)
 if label:b+=g(card(w*.8,48,CREAM),w*.1,h*.6)+text(label,w/2,h*.6+34,26,INK,'middle',900)
 if house:b+=path(f'M{w*.35} {-28}L{w*.5} {-66}L{w*.65} {-28}V15H{w*.35}Z',EDGE,4,CREAM)+rect(w*.47,-21,23,36,TEAL,3)
 return b

def seam(x=70,y=340,w=530,h=480,peel=0):
 b=path(f'M0 40Q-7 0 41 4L{w-34} -7Q{w+9} 3 {w} 48L{w-9} {h-49}Q{w} {h} {w-58} {h-7}L142 {h+4}L64 {h+68}L71 {h-4}Q-11 {h+2} 0 {h-42}Z',EDGE,5,CREAM)
 b+=g(card(w-55,h-68,DARK),25,26)
 b+=path(f'M{w-62} 20Q{w-20-peel*150} {h*.3} {w-49-peel*200} {h-50}',TEAL,14)
 if peel:b+=path(f'M{w-64} 15Q{w-peel*145} 95 {w-peel*208} {h-53}L{w-peel*140} {h-25}Q{w+15-peel*74} 186 {w-12} 7Z',EDGE,4,MINT)
 return g(b,x,y,a=-2)
def connector(x,y,w=260,engage=1):
 # Two visible mating faces and unequal app tabs, all attached to the seam.
 gap=(1-engage)*55;b=''
 for i,kind in enumerate(['mail','calendar','folder']):
  b+=g(card(76,90,[TEAL,GOLD,CORAL][i]),-24+i*83,-105-(i%2)*15,a=(i-1)*4)+icon(kind,14+i*83,-58-(i%2)*15,.72,INK)
 b+=g(card(w*.5,65,TEAL),-gap,0)+path(f'M{w*.5-gap} 12l18 0v36h-18',DARK,4,MINT)
 b+=g(card(w*.5,65,CREAM),w*.5+18+gap,0)+path(f'M{w*.5+18+gap} 12h-16v36h16',DARK,4,EDGE)
 return g(b,x,y)
def fan(business=1,personal=1):
 b=path('M105 915L94 806L260 314L554 823L449 928Z',EDGE,5,DARK)
 if business:
  leaf=card(300,380,CREAM)+text('WORK',150,63,42,INK,'middle',900)+path('M48 110H245V215H48Z',SLATE,4)+rect(58,179,42,26,TEAL)+rect(117,153,42,52,GOLD)+rect(180,129,42,76,CORAL)+lines(45,264,210,3)
  b+=g(leaf,128,335,a=-14-8*(1-business),opacity=business)
 if personal:b+=g(envelope(328,210,CORAL,'ERRANDS',True),273,652,a=13+14*(1-personal),opacity=personal)
 b+=path('M255 793L278 927L365 927L389 786',EDGE,12)+path('M282 830H362V918H282Z',CREAM,7,TEAL)+icon('folder',321,867,.65,CREAM)+f'<circle cx="315" cy="930" r="20" fill="{GOLD}"/>'+path('M319 946l52 20',DARK,12)
 return b

def specialist(reveal=1):
 b=g(card(550,370,DARK),80,400,a=-5)
 b+=g(path('M-52 -35H52V35H-52Z',SLATE,6,'none'),167,530)
 b+=g(path('M-38 -52L52 -20L30 50L-57 25Z',SLATE,6,'none'),561,545)
 # Compatible contours are a recess and a separate inserted company task.
 b+=g(path('M-99 -48L0 -103L99 -48L99 52L0 106L-99 52Z',EDGE,8,CREAM),370,592)
 b+=g(path('M-79 -38L0 -81L79 -38L79 40L0 83L-79 40Z',EDGE,5,TEAL),367,578,opacity=reveal)+icon('folder',366,576,1.23,DARK)
 b+=path('M293 621L294 639L370 682L446 639V621',DARK,5)
 b+=token(209,689,41,working=False)
 b+=g(card(550,83,GOLD),88,751,a=-2)+text('ENTERPRISE PREVIEW',360,808,37,INK,'middle',900)
 return b

def teams(lift=.5):
 b=g(card(532,392,CREAM),92,403,a=5)
 for x,y in [(196,515),(495,531),(355,714)]:
  b+=path(f'M{x-57} {y-32}Q{x-49} {y-58} {x+47} {y-43}L{x+60} {y+39}L{x-50} {y+45}Z',TEAL,5,'none','stroke-dasharray="12 10"')
 b+=path('M258 533L291 591 M424 555L403 600 M343 659L325 633',SLATE,5,'none','stroke-dasharray="12 10"')
 b+=path(f'M95 406L624 450L{623-lift*132} {800-lift*176}L{89+lift*113} {747-lift*211}Z',EDGE,4,CREAM,'opacity=".53"')
 b+=g(card(475,83,GOLD),127,815,a=-4)+text('PLANNED LATER',360,861,42,INK,'middle',900)
 b+=path('M320 780L347 743L393 752L408 792L379 824L335 817Z',DARK,4,GOLD)+icon('lock',364,783,.46,DARK)
 return b

def key(x=0,y=0,w=250):
 # Shape is repeated in the permission and ending worlds for a real callback.
 b=path('M-70 0A58 58 0 1 1 -70 -.01M-6 0H163V25H126V52H96V25H66V43H35V0Z',EDGE,6,TEAL)
 b+=f'<circle cx="-70" cy="0" r="28" fill="{CREAM}"/>'+path('M-22 -15H139',MINT,5)
 return g(b,x,y,w/250)
def permission(envelope_x=179,bot_age=0):
 b=path('M585 356L657 345V808H585Z',EDGE,5,DARK)+path('M604 416V721',INK,20)+path('M524 407V773',EDGE,20)+path('M532 411V777',CREAM,12)
 b+=g(envelope(315,168,CORAL,'SENSITIVE'),envelope_x,496,a=-3)
 b+=g(card(195,87,CREAM),62,886,a=3)+key(162,924,132)
 b+=g(card(183,86,CREAM),453,904,a=-3)+icon('lock',500,946,.64,DARK)+text('ASK',577,959,29,DARK,'middle',900)
 b+=watcher(263,995,.30,lean=-24,face='worried',t=bot_age)
 return b

def admission(dots_open=1,muse_open=1):
 b=g(card(474,235,DARK),68,330,a=-3)+g(card(474,235,DARK),151,660,a=4)
 for x,y,name,open_,accent in [(68,330,'DOTS',dots_open,TEAL),(151,660,'MUSE',muse_open,CORAL)]:
  face=card(474,235,CREAM)+text(name,42,60,45,INK,weight=900)
  face+=g(card(421,71,accent),27,95)+text('ELIGIBLE PAID PLAN' if name=='DOTS' else 'FREE TIER',237,145,32,INK,'middle',900)
  face+=text('REGION / ROLLOUT APPLY' if name=='DOTS' else 'EXTRAS VIA SUBSCRIPTION',237,207,23,INK,'middle',700)
  # Keep the revealed face rigid; a separate diagonal cover peels aside.
  b+=g(face,x,y,a=-3 if name=='DOTS' else 4)
  if open_<1:b+=g(path(f'M0 0H474L{474-open_*400} 235H0Z',EDGE,4,TEAL if name=='DOTS' else GOLD),x,y,a=-3 if name=='DOTS' else 4)
 b+=g(card(133,59,CORAL),501,894,a=4)+text('+ EXTRAS',568,935,22,INK,'middle',900)
 return b

def editorial(open_=1,task=1):
 b=path('M85 468L266 339L623 442L632 876L269 988L89 850Z',EDGE,5,DARK)
 # Work is an attached accordion, not another dashboard window.
 b+=path('M273 487L579 440L621 596L319 641Z',EDGE,6,TEAL)
 b+=path('M319 641L621 596L582 797L286 849Z',EDGE,6,CREAM)
 b+=path('M286 849L582 797L607 884L299 950Z',EDGE,5,MINT)
 b+=path('M319 641L621 596M286 849L582 797',DARK,5)
 b+=g(assignment(0,0,197,126,2,True),349,682,a=-8,opacity=open_)
 width=260*(1-open_*.65);leaf=path(f'M0 0L{width} {-25*open_}L{width} {366-25*open_}L0 366Z',EDGE,5,CREAM)
 leaf+=g(capsule(max(55,width-30),140,DARK),15,42)+text('…',max(32,width/2),136,55,CREAM,'middle')
 b+=g(leaf,93,485,a=-6)+path('M268 439L272 950',EDGE,8)
 if task:b+=path('M529 563l42 -7l4 48l-43 8Z',DARK,6,MINT)+token(549,577,36,working=True)
 return b

def ending(progress=1):
 b=g(card(231,124,CREAM),48,666,a=-6)+key(128+progress*80,626,245)
 b+=token(531,626,99,working=False,name=False)+path('M434 585H473V605H451V622H477V641H451V660H473V682H434Z',EDGE,4,DARK)+path('M449 610H465M449 654H465',MINT,6)+g(card(121,47,CREAM),470,771,a=3)+text('ACCESS',532,804,24,INK,'middle',900)
 b+=watcher(55,995,.29,lean=8,face='neutral')
 return b

def watcher(x,floor,s=.29,lean=0,face='neutral',t=0):
 from build_motif_bot import assemble_pose
 # Existing locked head/body/hands; poses change only their transforms.
 body,_=assemble_pose('standing',face,{'l':(310,682,'open'),'r':(716,619,'open'),'head_tilt':-16 if lean<0 else 12,'feet':((425,851 if lean<0 else 861,-9 if lean<0 else 0),(599,861,0))})
 body=re.sub(r'id="[^"]+"','',body)
 return g(f'<g transform="translate(512 904) rotate({lean}) translate(-512 -904)">{body}</g>',x,floor-904*s,s)

def cloud_easel(x=257,y=427,work=1):
 b=path('M22 365L142 34L328 349Z',EDGE,6,DARK)+path('M17 362L376 353L401 393L-7 401Z',EDGE,5,TEAL)
 b+=path('M66 34L357 3L389 295L86 332Z',EDGE,6,CREAM)+path('M88 61L337 34L363 270L107 299Z',TEAL,4,DARK)
 b+=icon('cloud',227,98,.74,CREAM)
 b+=path('M122 246L339 225L349 281L133 301Z',DARK,9,MINT)
 if work:b+=g(assignment(0,0,158,97,2,True),140,146,a=-5)
 b+=path('M141 288L356 268L386 347L172 369Z',EDGE,4,CREAM)+path('M172 369L386 347L358 457L153 471Z',EDGE,4,TEAL)+path('M153 471L358 457L387 533L177 551Z',EDGE,4,CREAM)
 b+=rect(213,378,33,33,CREAM,4)+path('M219 394h18',TEAL,4)+rect(222,493,29,29,EDGE,3)
 return g(b,x,y,a=-2)

def connected(peel=1,engage=1,passage=1,fold=1,close=0,t=0):
 b=backdrop(DARK)
 b+=g(capsule(290,248,CREAM),73,340,a=-5)+g(capsule(230,94,SLATE),96,380,a=-5)+text('…',204,449,62,CREAM,'middle')
 b+=path('M329 335L344 348L326 386L343 426L326 469L342 510L325 563',TEAL,14)
 b+=path(f'M336 335Q{399-peel*55} 409 {373-peel*48} 565L393 580Q431 436 366 319Z',EDGE,4,MINT)
 for i,k in enumerate(['mail','calendar','folder']):b+=g(card(72,83,[TEAL,GOLD,CORAL][i]),379+i*77,399-(i%2)*12,a=(i-1)*3)+icon(k,415+i*77,440-(i%2)*12,.7,DARK)
 b+=path('M477 491V592M559 490V574',CREAM,8)
 gap=(1-engage)*65
 b+=g(card(174,111,TEAL),224-gap,586)+path(f'M{398-gap} 606h45v63h-45',EDGE,5,MINT)
 b+=g(card(172,111,CREAM),443+gap,586)+path(f'M{443+gap} 607h22v61h-22',DARK,6,DARK)
 b+=path('M485 697L620 681L638 855L477 881Z',EDGE,6,TEAL)+path('M500 713L609 703L615 775L497 790Z',DARK,5,CREAM)
 b+=g(assignment(0,0,130,92,1,True),491,725,a=-5)
 b+=path('M496 804L619 787L637 881L511 899Z',EDGE,5,CREAM)+path('M511 899L637 881L616 973L489 987Z',EDGE,5,CORAL)+rect(541,921,32,32,CREAM,3)
 b+=g(assignment(0,0,125,87,0,True),287+passage*99,733-passage*22,a=-4)
 # Brace an actual torn edge, close enough to keep a readable arm silhouette.
 b+=path('M228 680L266 686L260 728L224 722Z',EDGE,4,MINT)
 b+=bot(-35,995-.32*904,.32,'focused',t,{'r':(245,708)})
 return b

def concept(id_):
 if id_=='s01-agency':
  b=backdrop(SLATE)+g(cloud(420),164,288,a=2)+path('M48 973Q376 944 687 976',EDGE,24)+cloud_easel()
  # User computer is a low closing clamshell, subordinate to the standing worker.
  b+=g(path('M0 0L169 15L201 70L-26 50Z',EDGE,5,DARK)+path('M-26 50L201 70L180 90L-40 69Z',EDGE,4,CREAM),61,828,a=-5)
  b+=token(397,674,44,working=True)+g(card(124,44,CREAM),70,948,a=-4)+text('OFFLINE',133,978,20,INK,'middle',900)
  return b
 if id_=='s02-connected-work':return connected(t=.6)
 if id_=='s03-use-pitch':return backdrop(GOLD)+path('M52 1013Q355 970 677 1010',CREAM,20)+fan()
 if id_=='s04-specialists':return backdrop(PLUM)+specialist()
 if id_=='s05-planned-teams':return backdrop(SLATE)+teams(.6)
 if id_=='s06-permission':return backdrop(PLUM)+permission()
 if id_=='s07-commercial-access':return backdrop(GOLD)+admission()
 if id_=='s08-editorial-reframe':return backdrop(DARK)+editorial()
 if id_=='s09-unresolved-keys':return backdrop(SLATE)+ending()
 raise ValueError('unbound concept '+id_)
