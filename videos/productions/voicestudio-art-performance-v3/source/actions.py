"""Finite, frame-seekable interactive UI action bindings for Motif.

Recipes are explicit agent-assisted choreography, not autonomous planning.
Shared components remain separate editable SVG elements inside each state.
"""
import math
from motif_art_v3_components import *
KINDS=('record-and-complete','star-and-count','reject-free-subscribe','sample-type-synthesize','dusty-cpu-laundry','dock-name-reveal','record-to-sample','script-scrap-output','model-row-hops','book-to-chapters','floating-mic-type','upload-speaker-strips','workflow-step-hops','dual-player','language-scroll-count','cancel-subscription','wifi-off-local-complete','blocked-upload','comment-keyboard')
COLORS=['#91A99F','#19243B','#BFA783','#B59D72','#6D7882','#8899A8','#30243E','#91A99F','#345D8D','#BFA17C','#B3B2A5','#B59D72','#B87A54','#91A99F','#B49B79','#BFA783','#19243B','#BDAD96','#B6CFD2']
def scene(number,f,headline_text,seed=5107,transition=True):
 """One deterministic local frame, including physical room and UI state."""
 kind={3:'tiles',16:'tiles',10:'shelves',11:'notes',14:'notes'}.get(number,'room')
 b=backdrop(COLORS[number-1],kind,f);top=headline(headline_text)
 if number==1:
  # Full illustration: acoustic strips, warm desk edge, paper device and
  # weighted foreground performer. The screen and bezel are independent.
  for i,c in enumerate(['#A6C3CA','#C59187','#A8BAA5']):
   x=[24,309,620][i];b+=g(card(68,437,c,.08),x,291,a=[-1,0,1][i])
   for yy in [318,457,600]:b+=path(f'M{x+14} {yy}V{yy+92}','#566E66',2,extra='opacity=".17"')
  b+=path('M0 735Q340 732 720 737V764H0Z','#A77D5D',0,'#A77D5D')+path('M0 764H720','#685143',5)
  ui=txt('VoiceStudio',113,389,28,CREAM,900)+txt('Voice sample',635,386,18,PINK,anchor='end')+path('M112 401H638','#554350',2)
  ui+=rect(112,408,76,28,'#4E3143',14)+txt('● REC',150,429,16,PINK,anchor='middle')
  ui+=waveform(115,432,410,164,f,reveal=.18+.82*clamp((f-4)/29))+ring(585,513,40,clamp(f/33),f,f>=33)
  b+=physical_monitor(80,337,580,282,ui)
  b+=path('M365 903C420 945 492 942 529 859Q551 799 630 806L641 620','#263538',6)+path('M370 904C419 938 482 937 517 906','#46615A',2)
  b+=stool(104,895,207,123)+mic(357,670,s=1.18)
  b+=path('M153 909Q206 916 257 907','#273F48',8,extra='opacity=".24"')
  b+=bot(209,907,f,s=.332,pose='standing' if f<60 else 'presenting',face='proud',performance='talking' if f<30 else 'record-anticipation' if f<33 else 'accepted-speaking' if f<60 else None,jitter=False)
  tag=card(146,59)+txt('OPEN SOURCE',73,38,17,INK,900,'middle')
  b+=path('M80 343L98 326',CREAM,3)+g(tag,24,278,a=-6+math.sin(f*.15)*2)
  if 8<f<60:b+=path(f'M292 {704+math.sin(f*.6)*5}Q310 687 326 704',PINK,4)
  for i in range(3):
   u=((f-i*8)%30)/30
   if f>8:b+=star(351+283*u,910-260*u,.35,CREAM)
  if f>=33:b+=ribbon(353,315,f,255)+burst(585,513,f,33)
  if f>=44:b+=g(card(143,71,GREEN,.04)+txt('FREE',71,52,40,CREAM,900,'middle'),504,274,a=4,s=.78+.22*spring((f-44)/9))
  if f>=60:b+=g(card(126,39)+txt('ElevenLabs',63,26,17,INK,anchor='middle'),488+78*ease((f-60)/12),893-31*ease((f-60)/12),a=-8)
 elif number==2:
  b+=g(card(78,80,GOLD),23,324,a=-12)+g(card(80,72,PINK),611,548,a=9)
  b+=g(card(625,515),45,300,a=living(f,seed,.35))
  b+='<circle cx="92" cy="348" r="22" fill="'+INK+'"/>'+path('M80 359V342L84 331L90 337L98 337L105 331L110 343V360',CREAM,3)
  b+=rect(129,334,305,26,'#CEC8B9',5)+txt('Public',621,353,17,INK,anchor='end')
  b+=txt('The open-source, fully-local',78,418,29,INK,900)+txt('ElevenLabs alternative',78,461,31,INK,900)
  b+=button('Watch',452,512,83,36,'#817E73')+button('Fork',548,512,83,36,'#817E73')
  b+=g(card(573,102,'#FAF5E9'),70,665)
  count=0
  checkpoints=[(22,33933),(30,36082),(38,36204),(45,36287),(53,36311)]
  if f>=22:
   count=36311
   for (a,ca),(z,cz) in zip(checkpoints,checkpoints[1:]):
    if a<=f<z:count=round(ca+(cz-ca)*(f-a)/(z-a));break
  b+=star(110,716,1.20,GOLD if f>=49 else '#B5AB8E')+txt('Starred' if f>=49 else 'Star',149,731,29,INK,900)+txt(f'{count:,}' if f>=22 else '—',596,735,42,INK,900,'end')
  x,y=hop(f,12,28,219,648,197,670,79)
  if f>=29:x,y=197,670+4*math.sin((f-29)*.4)*math.exp(-(f-29)/7)
  b+=bot(x,y,f,s=.19,face='excited',jitter=False)
  for i in range(10):
   u=((f+i*4)%62)/62;b+=star(70+(i*73)%530+20*math.sin(f*.09+i),566+220*u,.38+(i%3)*.1,GOLD,a=f*2+i*17)
  b+=burst(110,716,f,28,seed)+burst(592,711,f,49,seed,count=11)+mug(48,909)+lamp(619,871,.83)
 elif number in (3,16):
  cancel=number==16;b+=pricing(f,cancel)
  if not cancel:
   if f<26:
    if f<14:x=533-336*ease(f/14);y=855-302*ease(f/14)
    else:u=clamp((f-14)/12);x=197-45*u;y=553+130*u
    b+=token(x,y,s=.75,a=-6+11*math.sin(f*.17))
   elif f<42:
    u=clamp((f-26)/16);b+=token(152+243*u,683-72*u,s=.78,a=6*(1-u))
   x,y=hop(f,25,34,534,965,480,727,60)
   if f<25:x,y=533,965
   if f>39:x,y=hop(f,39,51,480,727,550,963,30)
   b+=bot(x,y,f,s=.25,face='worried' if f>=42 else 'surprised' if 14<f<26 else 'determined',pose='thinking' if f>=42 else 'standing',angle=-7 if f>=42 else 0,jitter=False,performance='strained' if f>=48 else None,impact=hop_impact(f,25,34) if 25<=f<=39 else 0)
   if f>48:
    for i in range(2):b+=path('M0 -10Q-10 4 0 10Q10 4 0 -10Z','#83B9CE',0,'#83B9CE',extra=f'transform="translate({627+i*19} {814+12*math.sin(f*.4+i)})"')
   b+=burst(479,727,f,38,seed)
  else:
   x,y=hop(f,1,17,530,960,480,727,60)
   if f>24:x,y=hop(f,24,33,480,727,545,960,35)
   b+=bot(x,y,f,s=.25,face='proud' if f>=24 else 'determined',jitter=False,performance='relieved' if f>=24 else None,impact=hop_impact(f,1,17) if f<=23 else 0)+burst(480,744,f,24,seed)
 elif number==4:
  b+=g(card(113,125,'#B3C0A9'),14,319)+rect(24,329,92,103,'#9DBAAE')+path('M29 405L58 365L84 394L111 347','#638F83',4)
  b+=workbench(119,870,555)+plant(636,815,f,.85)+monitor(130,360,510,355)+app(130,360,510,355,f,pressed=25<=f<=27)
  u=ease(f/11)
  if f<12:b+=token(80+360*u,856-450*u,s=.75,a=-13+20*u)
  else:b+=check(588,408,.5)
  text='Every voice has a story';n=int(len(text)*clamp((f-11)/14))
  b+=txt(text[:n],162,555,27)+path(f'M{163+min(n,24)*13.7} 533V561',PINK,2) if f%16<10 else txt(text[:n],162,555,27)
  u=ease((f-18)/10);b+=pointer(335+200*u,558+106*u,25<=f<=29)
  if f>=28:b+=ring(196,631,17,.3,f)+burst(548,656,f,27,seed)
  b+=bot(84,960,f,s=.24,face='happy' if f>28 else 'thinking',pose='pointing')+g(path('M0 0Q33 -21 43 10V30H0Z','#CDCEC2',2,'#CDCEC2'),217,838)
 elif number==5:
  b+=path('M-10 286H599Q620 286 620 311V329H730','#3D4852',19)+path('M-10 280H599Q626 280 626 306V323H730','#9EA7A3',13)
  for x,y in [(38,281),(411,281),(625,318)]:b+=g(card(24,27,'#BFC4B8',.08),x,y-12)
  washer=path('M5 10Q2 1 19 1L460 4Q485 3 488 24L486 199Q482 220 460 221L19 218Q0 216 1 190Z','#87908C',2,'#D4D5C9')+path('M5 207L481 209','#A2A89A',8)+g(card(463,35,'#ABB5AC',.05),13,13)
  washer+=rect(28,22,104,13,'#E5E6D7',2)+'<circle cx="425" cy="30" r="12" fill="#EAE9DC" stroke="#7B8982" stroke-width="3"/>'+path('M425 21V30','#6B7670',3)
  washer+='<circle cx="247" cy="133" r="78" fill="#A5B2B0" stroke="#F0EBDA" stroke-width="14"/><circle cx="247" cy="135" r="64" fill="#344B58" stroke="#6E858A" stroke-width="6"/>'+path('M314 126Q327 133 313 142','#EEE5D3',7)
  b+=g(washer,115,747)
  clothes=''
  for i,c in enumerate([CORAL,'#95BEB1','#CDDCE0',GOLD]):clothes+=g(card(42,57,c),-35+(i%2)*42,-50+(i//2)*50,a=i*17)
  b+=g(clothes,362,882,a=f*6.5)
  oldui=txt('VoiceStudio',184,407,26,CREAM,900)+txt('Local processor',184,440,18,'#BBAFBA')+waveform(187,461,289,51,f,n=23)
  oldui+=rect(188,537,270,22,'#4C394B',7)+rect(188,537,270*clamp((f-17)/46),22,MAGENTA,7)+ring(506,548,23,clamp((f-17)/46),f,f>=63)
  oldui+=button('Synthesize audio',217,561,230,42,pressed=16<=f<=18)
  b+=physical_monitor(143,349,434,292,oldui,old=True)
  # Cobweb remains attached to old screen corner, not a free-floating sticker.
  b+=path('M572 350L523 409M572 350L572 418M572 350L504 350M526 350Q524 382 572 394M548 350Q549 369 572 373','#C1C3B9',2)
  if f<20:
   u=ease(f/20);b+=g(path('M0 0Q100 -28 236 -8L441 7L457 341Q333 308 229 345Q101 320 -10 351Z','#D3D0C8',2,'#D3D0C8'),137-290*u,335-500*u,a=-31*u,opacity=1-.4*u)
  for i in range(3):
   age=f-i*11
   if 0<=age<35:
    u=age/35;b+=g(path('M-30 0Q-52 -25 -13 -27Q0 -55 22 -27Q66 -29 45 4Q24 27 -30 0Z','#CED0C3',0,'#CED0C3'),200+i*151+u*44,393-u*135,s=.4+u,opacity=.5*(1-u))
  a=math.sin(f*.22)*2
  recoil=clamp((f-63)/4)*(1-clamp((f-69)/7)) if f>=63 else 0
  b+=stool(55,870,151,120)+bot(124,881,f,s=.26,jitter=False,pose='thinking' if f<63 else 'standing',face='proud' if f>=74 else 'worried',performance='startled-planted' if 63<=f<74 else 'strained' if f<63 else 'relieved',impact=.12*recoil)
  b+=g(card(110,88,'#678E9B'),568,881)+path('M568 903H678M568 926H678','#B2CCD0',3)
  cat=path('M-54 19Q-72 -7 -48 -28Q-12 -58 31 -30Q57 -32 63 -12Q73 16 48 26L-27 30Z','#1D2930',2,'#1D2930')+path('M-47 14Q-9 39 35 20Q60 4 36 -9','#34424A',9)+path('M24 -24L27 -46L42 -34L57 -44L62 -17Z','#1D2930',1,'#1D2930')+path('M31 -14Q35 -10 40 -14M48 -14Q52 -10 57 -14','#9EAB9E',2)
  if f>=63:cat=path('M-43 26Q-63 -3 -33 -30Q-12 -44 6 -29L20 -64L36 -43L59 -58L65 -22Q84 0 55 28Z','#1D2930',2,'#1D2930')+path('M-39 20Q-101 -5 -77 -61','#1D2930',13)+'<ellipse cx="32" cy="-22" rx="4" ry="7" fill="'+GOLD+'"/><ellipse cx="53" cy="-23" rx="4" ry="7" fill="'+GOLD+'"/>'+path('M-35 -12L-46 -24M-13 -25L-18 -41','#1D2930',5)
  else:cat+=txt('z',49,-56,20,CREAM)
  startle=65*math.sin(math.pi*clamp((f-63)/9)) if 63<=f<=72 else 0
  b+=g(cat,621,910-startle,a=-12*math.sin((f-63)*.6)*math.exp(-max(0,f-63)/9) if f>=63 else 0)
  if 63<=f<73:b+=path('M596 808L582 792M624 800V781M652 808L665 790',GOLD,4)
  for i,c in enumerate([CORAL,'#A9BB8C','#94B2BD']):
   xx=12+i*35;b+=path(f'M{xx+8} 393L{xx+8} 382H{xx+22}V393Q{xx+31} 398 {xx+28} 411L{xx+29} 456H{xx+1}L{xx+2} 410Q{xx} 399 {xx+8} 393Z',c,1,c)+g(card(20,24,'#DEDAC3',.06),xx+5,416)+rect(xx+7,376,17,10,'#CECEB8',2)
  b+=rect(0,463,118,11,'#A27B54')
  if f>=63:b+=ribbon(259,327,f,280)+burst(538,597,f,63,seed)
 elif number==6:
  b+=g(card(622,496,'#BEA48A',.08),49,312)+path('M52 732L173 544L377 703L536 527L669 719V808H52Z','#7B7D98',0,'#7B7D98')
  b+='<circle cx="481" cy="427" r="58" fill="#E7B686"/>'
  b+=g(card(550,95,'#F3EEDF'),85,727)
  for i,c in enumerate([GREEN,CORAL,INK,GOLD,'#7392BF']):
   y=751-48*math.sin(math.pi*clamp(f/17)) if i==2 else 750
   if i==2:
    b+=g(card(142,133,INK,.04)+waveform(17,24,108,82,f,n=10),295,y-70,a=-2)
   else:b+=g(card(54,57,c,.05),112+i*109,y)
  b+=pointer(372,895-117*ease(f/8))
  if f>=8:b+=g(card(235,61,CREAM)+txt('VoiceStudio',117,43,37,INK,900,'middle'),245,579,a=-1)
  b+=bot(116,968,f,s=.245,face='excited',pose='presenting')
 elif number==7:
  for i in range(2):b+=g(card(65,474,'#CA7F75'),[10,650][i],329,a=-4+i*8)
  b+=path('M0 272Q365 384 720 271',INK,3)
  for i,c in enumerate([GOLD,PINK,'#8CC5B5',CORAL,GOLD]):b+=g('<ellipse rx="12" ry="18" fill="'+c+'"/>',85+i*130,300+25*math.sin(i*.7),a=math.sin(f*.11+i)*5)
  b+=monitor(90,340,565,395,True)+app(90,340,565,395,f,label='Voice')
  b+=rect(178,513,322,87,'#2D6047',5)+txt('5–15 s',337,541,30,CREAM,900,'middle')
  collapse=clamp((f-25)/6)
  if collapse<1:
   frozen=min(f,21);b+=g(waveform(-224.5,-38,449,76,frozen,reveal=.2+.8*clamp(f/22)),358.5,597,s=1-.66*collapse,sy=1-.3*collapse,opacity=1-collapse)
   b+=g(path(f'M{136+420*clamp(f/28)} 545V638',CREAM,2),opacity=1-collapse)
  b+=txt('0',134,650,18)+txt('20',584,650,18,anchor='end')
  b+=bot(218,962,f,s=.285,face='happy' if f>=32 else 'excited',pose='standing' if f<25 else 'presenting',performance='talking' if f<21 else None)+mic(354,786,.8)
  if f<21:b+=path(f'M298 {827+6*math.sin(f*.8)}Q322 809 341 825',PINK,4)
  if f>=21:b+=check(506,548,.8)+burst(506,548,f,21,seed)
  if f>=25:
   u=ease((f-30)/15);x=298+197*u;y=566-180*u-82*math.sin(math.pi*u);b+=token(x,y,s=.85*clamp((f-25)/5),a=-6+10*u)
   if f>=45:b+=check(604,391,.48)
 elif number==8:
  b+=workbench(73,897,600)+monitor(90,350,570,380)+txt('Script',120,404,26)+txt('Import script   Paste   Insert',123,440,16,'#B8ACB6')+button('Synthesize audio',413,657,211)
  b+=g(card(69,115,'#A6B1A0'),9,407,a=-3)+lamp(667,615,.6)+rect(581,811,85,150,INK,9)
  for yy in [854,919]:b+=f'<circle cx="623" cy="{yy}" r="23" fill="#766778"/>'
  phase=0 if f<14 else 1 if f<28 else 2;starts=[0,14,28];age=f-starts[phase]
  phrases=[['milk, eggs,','bread, coffee'],['Roses are red,','my voice is my own'],['Local cat wins','the election']]
  for i,line in enumerate(phrases[phase]):b+=txt(line,123,526+i*46,31)
  if age<11:
   u=ease(age/11);label=['SHOPPING','POEM','NEWS'][phase]
   scrap=card(150,120,[CREAM,PINK,'#E8DEBE'][phase])+txt(label,75,35,19,INK,900,'middle')+path('M18 61H131M18 80H110M18 99H128','#A79C88',3)
   b+=g(scrap,82+178*u,866-344*u-75*math.sin(math.pi*u),a=-13+21*u,s=.85)
  b+=ribbon(438,775,f,263)+bot(120,965,f,s=.26,face='happy',pose='presenting')
 elif number==9:
  b+=g(card(63,109,GOLD),17,397,a=-3)+plant(640,902,f,.85)
  b+=g(card(397,640,INK,.07),100,309)+txt('Models',129,363,30,CREAM,900)
  rows=['LLM','Translation','Diarisation','Dictation','ASR','TTS'];land=[49,44,35,27,18,8]
  for i,label in enumerate(rows):
   y=388+i*86;selected=f>land[i];compression=2.5*math.exp(-max(0,f-land[i])/2) if 0<=f-land[i]<6 else 0
   b+=g(card(395,71,'#533749' if selected else '#362638',.04),116,y+compression)+path(f'M119 {y+68+compression}H510',PINK if selected else '#71606A',3)+txt(label,136,y+45,24)
   b+=burst(510,y+53,f,land[i]+1,seed+i,count=5)
  stages=[(0,8,966,886),(8,18,886,800),(18,27,800,714),(27,35,714,628),(35,44,628,542),(44,49,542,456)]
  stage=next((v for v in stages if v[0]<=f<v[1]),stages[-1]);x,y=hop(f,stage[0]+2,stage[1],481,stage[2],481,stage[3],39+stage[0]%3*5)
  impact=hop_impact(f,stage[0],stage[1]);b+=bot(x,y,f,s=.185,face='thinking' if f<stage[0]+2 else 'determined' if f<stage[1] else 'proud',pose='standing',jitter=False,impact=impact)
 elif number==10:
  b+=g(card(565,468,'#40313D',.06),115,345)+path('M126 357L665 359','#74616D',2)+txt('The Librarian',143,395,32,CREAM,900)+txt('Warm UK audiobook narrator',145,423,15,'#BDB2B5')+txt('measured, atmospheric · Use this design →',145,446,13,'#BDB2B5')
  for i,start in enumerate([23,34,43]):
   if f>=start:
    u=spring((f-start)/6);b+=g(chapter_row(0,0,f'Chapter {i+1}',f,phase=i*2.1),140,480+i*97+14*(1-u),opacity=clamp(u))
  closed=path('M3 4L170 0L177 93L8 104Z','#763D34',2,'#B95648')+path('M15 9L158 7L164 85L21 91Z','#D6A183',2)+txt('BOOK',90,60,25,CREAM,900,'middle')+path('M7 98L174 88',CREAM,6)+path('M11 9L16 91','#803F37',8)
  opened=path('M-4 3Q40 -19 84 3Q135 -18 176 0L180 105Q135 89 87 112Q41 90 -3 108Z','#884B3D',7,'#884B3D')+path('M0 0Q45 -17 83 5Q120 -16 169 0V97Q125 82 84 102Q40 82 0 97Z',EDGE,2,CREAM)+path('M84 6V99','#AE9C83',3)
  for i in range(4):opened+=path(f'M14 {22+i*16}Q45 {16+i*16} 70 {24+i*16}M99 {24+i*16}Q128 {15+i*16} 153 {22+i*16}','#BDAF98',2)
  b+=g(closed if f<10 else opened,38,845,s=1.16,sy=max(.35,abs(math.cos(f/14*math.pi))) if f<14 else 1,a=-6)
  # Three chapter arrivals are caused by three page flights. Early rows stay live.
  for i,(start,arrival) in enumerate([(9,23),(17,34),(27,43)]):
   age=f-start
   if 0<=age<arrival-start:
    u=age/(arrival-start);desty=484+i*97;x=104+402*u+(i-1)*57*math.sin(math.pi*u);y=862+(desty-862)*u-[165,112,210][i]*math.sin(math.pi*u)
    page=card(65+i*6,83-i*5,CREAM)+path('M10 19H49M10 35H46M10 51H48','#A49A86',2)+path('M50 1L64 16L49 17Z','#CEBDA0',1,'#DDD2BC')
    b+=g(page,x,y,a=[-27,18,-12][i]+[69,-52,104][i]*u+9*math.sin(age*.7),s=1-.20*u,sy=1-.16*math.sin(math.pi*u))
   if arrival<=f<arrival+6:b+=burst(546,520+i*97,f,arrival,seed+i,count=4)
  b+=bot(262,967,f,s=.22,face='excited',pose='presenting')
 elif number==11:
  b+=rect(0,693,720,274,'#789AA8')+g(card(597,458,'#F4F0E7'),63,329)+rect(80,345,563,52,'#E7E3D6',8)
  for i,c in enumerate(['#D97057',GOLD,GREEN]):b+=f'<circle cx="{99+i*22}" cy="369" r="7" fill="{c}"/>'
  b+=txt('Notes',359,378,23,INK,anchor='middle')
  text='types out whatever you want to say';n=int(len(text)*clamp((f+3)/37));visible=text[:n]
  # Stable wraps keep caret attached to the growing phrase.
  line1=visible[:22];line2=visible[22:].lstrip()
  b+=txt(line1,95,490,33,INK,900)+txt(line2,95,543,33,INK,900)
  if f%12<8:
   cx=95+len(line2 if len(visible)>22 else line1)*17;cy=543 if len(visible)>22 else 490;b+=path(f'M{cx} {cy-29}V{cy+4}',MAGENTA,2)
  b+=g(rect(0,0,258,79,INK,39)+'<circle cx="43" cy="39" r="26" fill="'+MAGENTA+'"/>'+path('M37 27V43Q43 50 49 43V27M43 50V58',CREAM,3)+waveform(84,20,151,40,f,n=22),386,730,a=living(f,seed,.7))
  b+=bot(118,965,f,s=.26,face='excited',pose='presenting')+mug(617,908,GREEN)
 elif number==12:
  b+=clock(52,430,.88)+rect(624,400,85,302,'#48705E',6)
  for yy in [445,476,507,538]:b+=path(f'M636 {yy}H695','#95B894',2)
  b+=g(card(546,365,'#332636',.05),92,337)+txt('Upload & Transcribe',124,390,30,CREAM,900)
  b+=rect(125,422,479,144,'#332435',8,PINK,2)+txt('Choose file…',363,454,21,CREAM,anchor='middle')+txt('Drop video or audio here',363,491,22,CREAM,anchor='middle')+txt('…or paste YouTube / video URL',363,536,13,'#B6A2AF',anchor='middle')+txt('Spoken language',125,606,17)
  b+=rect(125,641,479,8,'#53404F',4)+rect(125,641,479*clamp(f/17),8,MAGENTA,4)
  u=ease(f/12);b+=g(card(149,66,PINK)+txt('recording.wav',74,40,17,INK,anchor='middle'),495-215*u,769-231*u-55*math.sin(math.pi*u),a=8*(1-u))
  for i,start in enumerate([19,27,35,43]):
   if f>=start:
    u=ease((f-start)/7);b+=transcript(84+(1-u)*100,726+i*57-10*clamp((f-42)/8),f'Speaker {i%2+1}',['#568CAF',CORAL][i%2],f)
  b+=bot(638,965-8*math.sin(f*.12),f,s=.20,face='happy',pose='pointing')
 elif number==13:
  b+='<circle cx="37" cy="493" r="40" fill="#D2B7A0"/>'
  for i in range(4):b+=f'<circle cx="{37+22*math.cos(i*math.pi/2)}" cy="{493+22*math.sin(i*math.pi/2)}" r="10" fill="#8D6659"/>'
  b+=g(card(605,536,INK,.04),75,340)+ring(356,422,43,clamp(f/42),f,f>=42)
  labels=['3 Generate Dub','2 Translate','1 Upload & Transcribe'];fin=[40,29,14]
  for i,label in enumerate(labels):
   y=492+i*104;p=clamp((f-[30,15,0][i])/14)
   b+=rect(99,y,553,86,'#3A2639',9)+txt(label,122,y+40,24)+rect(120,y+62,458,6,'#634158',3)+rect(120,y+62,458*p,6,MAGENTA,3)
   if f>fin[i]:b+=check(615,y+40,.63)+burst(611,y+33,f,fin[i]+1,seed+i,count=5)
  x,y=(123,963)
  if f<=15:x,y=hop(f,2,14,123,963,146,700,55)
  elif f<=30:x,y=hop(f,17,29,146,700,159,596,52)
  elif f<=40:x,y=hop(f,32,40,159,596,176,492,52)
  else:x,y=hop(f,42,51,176,492,598,939,110)
  stage=(0,14) if f<15 else (15,29) if f<30 else (30,40) if f<41 else (40,51)
  b+=bot(x,y,f,s=.175,face='determined' if f<stage[1] else 'proud',jitter=False,impact=hop_impact(f,*stage))
  clap=rect(0,0,122,91,INK,5)+rect(0,-15,122,25,CREAM,2)
  for i in range(5):clap+=path(f'M{i*27} -15L{i*27+21} 10',INK,11)
  b+=g(clap,563,882,a=math.sin(f*.2)*2)
  if f>=38:
   u=spring((f-38)/8);b+=g(star(0,0,7,PINK),360,552,s=u*.9,opacity=.70)
   b+=g(card(480,110,CREAM)+txt('Video Dubbing Studio',240,53,30,INK,900,'middle')+txt('MP4 · MOV · MKV · WEBM · MP3 · WAV · FLAC · M4A',240,83,12,INK,anchor='middle'),91,520,s=.83+.17*u)
   b+=burst(570,577,f,40,seed,count=12)
 elif number==14:
  b+=g(card(503,632,'#2D2B35',.04),144,320)+txt('English',179,376,30,CREAM,900)+txt('ORIGINAL',605,375,16,'#ACA0A8',anchor='end')
  b+=rect(164,402,463,202,'#362B37',8)+waveform(185,446,421,105,f,n=45,color='#B9ADB6',phase=.4)+path(f'M{186+417*clamp(f/35)} 421V585',PINK,2)
  b+=txt('Español',179,660,32,PINK,900)+txt('DUBBED',606,658,17,PINK,anchor='end')
  b+=rect(164,680,463,183,'#372332',8,PINK if f>=8 else '#4A3948',2)+waveform(185,712,421,99,f,n=45,color=PINK,phase=2.1)+path(f'M{186+417*clamp((f-8)/27)} 699V847',CREAM,2)
  b+=txt('Español',177,914,19,PINK)+txt('Français',299,914,17)+txt('中文',429,914,17)+txt('日本語',523,914,17)
  if f>=24:b+=path('M177 923H253',PINK,4)
  b+=bot(91,946,f,s=.19,face='happy',pose='pointing',contact=(165,790))+plant(660,938,f,.52)
 elif number==15:
  b+=g(card(702,673,'#AA8766',.17),9,293)+clock(675,339,.75)+plant(643,936,f,.85)
  b+=g(card(241,525),50,360,a=-2)+txt('ElevenLabs',73,416,28,INK,900)+txt('Dubbing',74,464,28,INK,900)+txt('90+',168,598,70,MAGENTA,900,'middle')+txt('languages',168,653,25,INK,anchor='middle')+txt('and accents',168,692,22,INK,anchor='middle')
  b+=rect(325,370,328,548,INK,12)+txt('Manage languages ▾',344,413,18)
  count=int(152*f/12) if f<=12 else int(152+305*(f-12)/15) if f<=27 else int(457+189*ease((f-27)/13));count=min(646,count)
  b+=g(card(241,75,'#793249',.06)+txt(str(count),120,56,51,CREAM,900,'middle'),368,279,a=living(f,seed,.55))
  names=['English','Español','Français','Deutsch','Italiano','Português','Русский','Kiswahili','Tagalog','Türkçe','Tiếng Việt','Yorùbá','Polski','ไทย','한국어','Ελληνικά','Svenska','isiZulu','Suomi','Magyar','Cymraeg','Íslenska','Quechua']
  scroll=clamp(f/43)*820
  for i,name in enumerate(names):
   yy=449+i*53-scroll
   if 437<yy<897:b+=rect(341,yy-17,17,17,'#423546',3,PINK,1)+txt(name,371,yy,21)
  b+=bot(321,911-38*math.sin(f*.14),f,s=.17,face='excited',pose='presenting')
  for x,y in [(51,365),(287,385),(325,362),(644,920)]:b+='<circle cx="'+str(x)+'" cy="'+str(y)+'" r="5" fill="'+CORAL+'"/>'
 elif number==17:
  # Illustrative offline UI: progress never restarts when the switch changes.
  b+=rect(28,280,664,620,'#273D5F',8)
  for i in range(13):b+=star(42+(i*87)%615,296+(i*107)%342,.23,CREAM)
  b+=path('M28 858L77 627L110 760L176 578L234 817L282 631L346 857L434 666L491 806L588 572L663 858Z','#172B32',0,'#172B32')
  for i in range(2):
   b+=g(card(58,619,'#D1B457',.10),[0,662][i],281,a=math.sin(f*.10+i)*.8)
   for xx in [14,33,46]:b+=path(f'M{[0,662][i]+xx} 296V881','#B69A45',2)
  b+=monitor(60,340,610,455,True)+app(60,371,610,424,f,progress=.1+.9*clamp(f/36),done=f>=36,progress_focus=True)
  b+=rect(80,357,570,30,'#D6D5CE',4)+txt('VoiceStudio   File   Edit   View',90,378,15,INK)+path('M602 367Q612 360 622 367M605 372Q612 367 619 372M610 377H614',INK,2)
  b+=txt('NLLB-200 (Local, Heavy) · Offline',94,704,17,'#CDBFCA')
  px,py=hop(f,0,12,385,643,608,365,0)
  if f>=12:px,py=608,365
  if f>=12:
   b+=g(card(202,91,'#DFDED8')+txt('Wi-Fi',16,33,23,INK,900)+rect(133,12,55,27,'#8C9392' if f>=23 else '#347BA4',15)+f'<circle cx="{147 if f>=23 else 174}" cy="25" r="10" fill="#F5F1E5"/>'+txt('OFF' if f>=23 else 'ON',102,76,23,INK,900),427,390)
   px=603;py=418
  b+=pointer(px,py,21<=f<=23)+bot(111,961,f,s=.245,face='happy' if f>=36 else 'thinking')
  if f>=36:b+=ribbon(194,310,f,328)+burst(604,617,f,36,seed)
 elif number==18:
  b=rect(0,0,720,1280,'#BDAD96')+g(rect(0,0,720,1280,'url(#worldPaper)'),opacity=.17)
  for i in range(10):
   x=i*78-15;y=470+((i*31)%5)*38;b+=rect(x,y,69,470,'#293B59')
   for k in range(4):
    for j in range(3):b+=rect(x+10+j*17,y+35+k*49,8,11,GOLD)
  b+=rect(0,919,720,61,'#A28A78')+rect(0,980,720,300,'#809AA4')
  for x in range(0,720,94):b+=path(f'M{x} 927V975','#736A64',2)
  b+=path('M0 945H720','#736A64',2)
  cloud=path('M-80 15Q-115 -31 -53 -46Q-36 -105 22 -79Q86 -95 93 -39Q147 -16 111 20Z','#E8E0D0',2,'#E8E0D0')
  b+=g(cloud,363,300,a=living(f,seed,.5))+monitor(70,365,590,459,True)
  lines=['It runs entirely','on your machine.','No accounts,','no cloud, no API keys.']
  for i,line in enumerate(lines):b+=txt(line,100,443+i*49,29 if i<2 else 27,CREAM,900)
  for i,start in enumerate([16,23,29,35]):
   if f>=start:b+=path(f'M100 {454+i*49}H{100+[267,285,191,342][i]*ease((f-start)/7)}',MAGENTA,4)
  b+=path('M391 706V670M371 690L391 670L411 690',CREAM,5)+g(cloud,391,660,s=.18)
  b+=g(card(81,50,CREAM)+txt('0%',40,35,29,INK,900,'middle'),471,695)
  if f<14:b+=ring(430,722,21,.13,f)
  else:b+=cross(430,722,.84)
  u=clamp(f/13)
  if f<14:b+=token(267+69*u,780-72*u,s=.66,a=-3)
  elif f<28:b+=token(336+13*(f-14),708+((f-14)/14)**2*225,s=.66,a=(f-14)*6)
  b+=bot(626,924,f,s=.21,face='happy' if f>=16 else 'determined',pose='pointing')
  if transition and f>=47:
   u=ease((f-47)/12);incoming=scene(19,f-59,'COMMENT VOICE FOR THE SETUP',seed+101,False)
   b=g(b+top,-720*u,0)+g(incoming,720*(1-u),0)
   if 48<f<57:b='<g filter="url(#pushBlur)">'+b+'</g>'
   return b
 elif number==19:
  b+=rect(39,311,641,396,'#D0DDD4',6)+rect(58,334,603,351,'#66866D')
  for x in [67,251,444,639]:b+=rect(x,336,12,354,'#315A4C')
  b+=rect(58,487,602,13,'#315A4C')
  for i in range(12):b+=rect(22+i*57,278,57,45,'#B95548' if i%2==0 else '#F0E8D6')+path(f'M{22+i*57} 324Q{50+i*57} 354 {79+i*57} 324','#945C50' if i%2==0 else '#D5CABA',1,'#B95548' if i%2==0 else '#F0E8D6')
  phone=path('M174 282Q144 283 141 318L139 919Q140 973 178 980L548 977Q586 973 587 929L584 322Q583 283 548 279Z','#A3ACA2',2,'#A3ACA2')+path('M173 286Q147 288 146 320L146 924Q145 966 179 970H546Q578 968 579 929L577 321Q576 289 546 286Z',INK,2,INK)+rect(155,298,414,661,'#F4EFDF',30)+path('M147 385V496','#CDD2C4',3)+rect(290,298,145,26,INK,13)
  b+=phone
  b+=txt('Comments',362,372,32,INK,900,'middle')+path('M172 395H552','#CEC5B4',2)
  for i in range(2):
   yy=432+i*75;b+=f'<circle cx="192" cy="{yy}" r="16" fill="#B6B4AA"/>'+rect(227,yy-13,242-i*41,10,'#C7C3B6',5)+rect(227,yy+10,177+i*40,9,'#D2CDBF',5)
  b+=path('M172 576H550','#CEC5B4',2)+'<circle cx="193" cy="599" r="18" fill="#C88752"/>'
  # Source prescription f965 = local28; five distinct actual key contacts.
  n=0 if f<28 else min(5,1+(f-28)//2);word='VOICE'[:n]
  b+=txt(word if word else 'Add a comment…',227,606,32 if word else 21,INK,900 if word else 700)+txt('Post',517,680,24,'#2D77AD',900,'end')
  active='VOICE'[min(4,max(0,(f-28)//2))] if 28<=f<38 and f%2==0 else None
  keys,positions=keyboard(188,732,active);b+=g(card(388,222,'#DCD8CB',.06),168,706)+keys+g(card(226,29,'#FAF6E9',.03),247,888)
  if f<25:x,y=hop(f,0,16,638,958,400,731,80)
  elif f<28:x,y=hop(f,25,28,400,731,*positions['V'],32)
  elif f<38:
   letter='VOICE'[min(4,(f-28)//2)];xx,yy=positions[letter];x,y=xx,yy
  else:x,y=hop(f,38,48,positions['E'][0],positions['E'][1],616,963,46)
  if 28<=f<38 and f%2:
   previous='VOICE'[(f-28)//2];following='VOICE'[min(4,(f-28)//2+1)]
   xx,yy=positions[previous];nx,ny=positions[following];x=(xx+nx)/2;y=(yy+ny)/2-38
  impact=.75 if 28<=f<38 and not f%2 else -.27 if 28<=f<38 else .6*clamp((f-25)/3) if 25<=f<28 else hop_impact(f,38,48) if f>=38 else 0
  b+=bot(x,y,f,s=.165,face='determined' if f<38 else 'excited',jitter=False,impact=impact)
  if f>=7:
   u=spring((f-7)/7);b+=g(card(95,61,'#78A5C1')+path('M18 24L42 14L58 28L34 41Z',CREAM,3),36,389,s=.85+.15*u,a=-9)
  if f>=13:
   u=spring((f-13)/7);clip=card(91,118,CREAM)+rect(27,-6,38,16,'#B9AD94',3)
   for i in range(3):clip+=check(21,32+i*30,.27)+path(f'M39 {32+i*30}H74','#A39D88',3)
   b+=g(clip,610,408,s=.83+.17*u,a=7)
  if f>=38:
   # Three silhouette-readable heroes and five smaller satellites, all from VOICE.
   destinations=[(186,428),(439,396),(327,456),(512,516),(204,523),(425,492),(284,409),(365,523)]
   for i,(dx,dy) in enumerate(destinations):
    age=f-38-[0,1,2,0,2,3,1,4][i]
    lifetime=[26,24,22,9,10,8,9,7][i]
    if age<0 or age>=lifetime:continue
    u=ease(age/[11,10,9,12,10,8,11,8][i]);size=[82,91,75,43,47,37,42,40][i]
    x=356+(dx-356)*u;y=546+(dy-546)*u-38*math.sin(math.pi*u)
    tile=card(size,size*.88,INK,.03)+waveform(size*.13,size*.15,size*.74,size*.55,i*7,n=7)
    angle=[-13,17,-6,22,-20,9,-24,15][i]*u
    b+=g(tile,x,y,a=angle,s=.30+.70*clamp(age/3),opacity=clamp((lifetime-age)/2))
  b+=mug(653,904,'#CD854B',.92)
 else:raise ValueError('unsupported finite scene')
 return b+top
