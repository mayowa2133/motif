"""v5 art layouts with selected v6 repository, billing and transcript craft.

All new paper geometry is production-local. No new planner, renderer or timing.
"""
import math
from motif_art_v4_components import *
from motif_art_v4_actions import scene as baseline_scene, KINDS, COLORS
CHANGED=(2,3,6,8,11,12,13,14,15,16,18)

def cut(d,c,grain=.045,edge='#B9AA91'):
 return path(d,INK,0,INK,extra='transform="translate(3 5)" opacity=".16"')+path(d,edge,.8,edge,extra='transform="translate(1 2.5)"')+path(d,c,.65,c)+path(d,c,0,'url(#worldPaper)',extra=f'opacity="{grain}"')

def pin(x,y):
 return g(path('M-9 -3Q0 -9 9 -3L8 3H-8Z','#718C8B',1,'#BDCEC3')+path('M0 3V17','#344952',2),x,y)

def edge_shelf(x,y,w,c='#B4845A'):
 return g(cut(f'M0 0L{w-3} -2L{w+4} 11L3 16Z',c,.05)+path(f'M4 12L{w} 9','#624A38',3),x,y)

def paper_star(x,y,size=20,a=0,c=GOLD):
 d='M0 -20L6 -7L20 -5L10 5L13 20L0 13L-14 20L-11 5L-21 -5L-6 -8Z'
 return g(cut(d,c,.025)+path('M-4 -5L1 -12','#FFF0B0',2),x,y,a=a,s=size/20)

def repo(f,seed):
 b=backdrop(COLORS[1],'room',f)
 # Tabbed software dossier, a fold-over binding and a pressable star ledge.
 b+=g(cut('M0 22L19 1L162 0L180 23L548 27L552 477L6 475Z','#7E99A0'),91,315,a=3)
 tag_react=reaction(f,49,(535,706),(554,310),radius=470,relevance=.35,delay=2,amplitude=9)
 b+=g(card(185,62,'#AAB997'),462,278-tag_react,a=5+tag_react*.45)+g(tape(71,22),495,275,a=12)
 b+=g(cut('M0 30L17 2L160 0L182 26L602 26L625 48L621 482L604 514L4 505Z',CREAM),45,295,a=living(f,seed,.35))
 b+=path('M62 344L65 775','#B7A98F',5)+path('M70 341L72 775','#F9F2E2',2)
 b+='<circle cx="105" cy="363" r="25" fill="'+INK+'"/>'+path('M91 375V357L96 345L103 352L111 352L118 345L122 358V374',CREAM,3)
 b+=txt('Public',616,359,18,INK,anchor='end')+txt('OPEN SOURCE',152,372,20,INK,900)
 b+=txt('The open-source, fully-local',87,421,29,INK,900)+txt('ElevenLabs alternative',87,465,31,INK,900)
 b+=g(card(103,38,'#D6CCB7')+txt('Watch',51,26,18,INK,900,'middle'),421,523,a=-1)+g(card(95,38,'#D6CCB7')+txt('Fork',47,26,18,INK,900,'middle'),538,522,a=1)
 b+=path('M77 649L644 645L647 770L80 775Z','#B5A58B',1,'#B5A58B')
 ledge=reaction(f,28,(197,670),(197,690),radius=230,amplitude=10)
 b+=g(cut('M0 12L21 0L549 2L572 17L568 101L8 106Z','#FAF5E9'),70,665+ledge,a=ledge*.06)
 count=0;checkpoints=[(22,33933),(30,36082),(38,36204),(45,36287),(53,36311)]
 if f>=22:
  count=36311
  for (a,ca),(z,cz) in zip(checkpoints,checkpoints[1:]):
   if a<=f<z:count=round(ca+(cz-ca)*(f-a)/(z-a));break
 b+=paper_star(111,718,26,-5,GOLD if f>=49 else '#B5AB8E')+txt('Starred' if f>=49 else 'Star',151,736,29,INK,900)
 count_react=reaction(f,49,(535,706),(493,710),radius=210,delay=1,amplitude=9)
 b+=g(card(231,72,'#E5DDCA')+txt(f'{count:,}' if f>=22 else '—',209,51,42,INK,900,'end'),390,682-count_react,a=count_react*.2)
 x,y=hop(f,12,28,219,648,197,670,79)
 if f>=29:x,y=197,670+4*math.sin((f-29)*.4)*math.exp(-(f-29)/7)
 b+=bot(x,y,f,s=.258,jitter=False,performance='anticipating' if f<13 else 'focused' if f<28 else 'impact' if f<32 else 'relieved',acting_frame=f-28 if f>=28 else f,craft='heavy' if 28<=f<35 else None,craft_age=f-28)
 # Two event-specific bursts; one hero, two medium and three supporting stars.
 for birth,origin in [(28,(183,682)),(49,(585,716))]:
  for i,(dx,dy,size,delay,life) in enumerate([(-69,-56,40,0,22),(65,-93,23,1,16),(-31,38,19,3,14),(94,6,9,2,10),(-94,-14,8,4,11),(20,-105,11,5,9)]):
   age=f-birth-delay
   if not 0<=age<life:continue
   u=clamp(age/11);xx=origin[0]+dx*ease(u);yy=origin[1]+dy*u-21*math.sin(math.pi*u)
   b+=g(paper_star(0,0,size,-17+i*19+age*(3 if i%2 else -2)),xx,yy,s=.65+.35*clamp(age/2),opacity=clamp((life-age)/4))
 b+=g(card(121,61,'#A9BCB4'),58,865,a=-9)+g(card(131,54,'#CBB37E'),75,880,a=5)+edge_shelf(15,943,202)
 for xx,yy,ss,aa in [(54,895,16,-12),(94,920,23,8),(157,919,13,26)]:b+=paper_star(xx,yy,ss,aa)
 b+=g(card(128,78,'#63868C')+path('M15 23H111M17 42H90M19 61H106','#ADBCB0',3),552,858,a=4)+edge_shelf(523,944,192)
 return b

def long_receipt(x,y,i=0,stopped=False):
 w=95;h=158
 d='M0 6L10 0L19 7L29 1L39 7L49 1L59 6L70 0L80 6L93 1L95 149L83 158L72 151L61 158L50 150L39 156L28 150L16 156L4 151Z'
 if i%5==4:d='M0 6L10 0L19 7L29 1L39 7L49 1L59 6L70 0L80 6L93 1L96 178L88 185L78 181L65 194L51 185L39 192L27 180L16 188L4 183Z'
 b=cut(d,'#F8F0DC',.04)+txt('STARTER',47,29,15,INK,900,'middle')+path('M12 42H82M12 59H69M12 70H82M12 82H77','#BAAA91',2)
 b+=txt('MONTHLY',47,104,13,INK,900,'middle')+path('M12 115H83','#B7A586',1)
 if stopped:b+=g(card(78,25,'#9BB69D')+txt('STOPPED',39,18,12,INK,900,'middle'),8,123,a=-4)
 else:b+=txt('Paid',47,140,18,GREEN,900,'middle')
 return g(b,x,y,a=[-7,5,-3,9,-12][i%5])

def price_world(f,cancel=False):
 b=backdrop(COLORS[15 if cancel else 2],'tiles',f)
 # Two hinged placards; the earlier control and rejection anchors are retained.
 b+=g(cut('M0 12L15 0L589 4L613 22L610 444L5 451Z','#799792'),38,345)
 b+=g(card(292,420,'#F4EBD7'),49,378,a=-.4)+g(card(291,420,'#EEE3CD'),346,378,a=.5)
 b+=g(card(579,65,'#CFB587')+txt('ElevenLabs / Pricing',289,44,28,INK,900,'middle'),54,326,a=-1)
 for xx in [185,470]:b+=g(path('M-6 0Q0 -18 6 0V22M-6 22Q0 34 6 22','#746C5C',5)+path('M-4 -1V22','#E2DBC3',2),xx,382)
 b+=txt('Free',251,450,32,INK,900,'middle')+txt('Starter',481,450,32,INK,900,'middle')
 b+=txt('Text to speech',70,508,17,INK)+txt('Voice cloning',70,585,17,INK)+path('M68 542H319M365 542H615','#C3B394',1.5)
 b+=check(250,507,.75)+check(480,507,.75)+cross(251,582,.98+(.27*math.sin((f-13)/12*math.pi) if 13<f<25 and not cancel else 0))
 accepted=cancel or f>=42
 if accepted:b+=check(480,583,.97)+token(394,611,s=.78)
 b+=txt('billed monthly',481,706,17,INK,anchor='middle')
 state='Cancelled' if cancel and f>=24 else 'Cancel plan' if cancel else 'Subscribed' if f>=38 else 'Upgrade'
 b+=button(state,389,726,189,45,color='#8D9C91' if state=='Cancelled' else GREEN if state=='Subscribed' else INK,pressed=(17<=f<=23 if cancel else 33<=f<=37))
 b+=g(path('M-14 -9A18 18 0 1 1 -16 8M-14 -9L-23 -6M-14 -9L-13 -20',INK,3),609,747,a=0 if cancel and f>=24 else f*7)
 total=5 if cancel else max(0,min(5,(f-44)//5+1))
 # Unchanged five billing arrivals, spatially collected rather than UI badges.
 for i in range(total):
  event=24 if cancel else 44+i*5
  response=reaction(f,event,(640,782),(646-i*8,827+i*15),radius=200,relevance=1 if i==total-1 else .65,delay=1 if cancel else 0,amplitude=12)
  b+=g(long_receipt(0,0,i,cancel and f>=24),625-i*9,759+i*15+(13 if i==4 else 0)+response,a=response*.55)

 if total:
  b+=edge_shelf(44,956,214)+g(cut('M0 9L110 0L163 12L156 37L14 42Z','#5B7F80'),58,922)
  for i in range(min(3,total)):
   settle=reaction(f,24 if cancel else 44+5*(total-1),(148,901),(96+i*32,888),radius=190,relevance=.6,delay=3,amplitude=8)
   b+=g(long_receipt(0,0,i,cancel and f>=24),67+i*32,851+i*13-settle,a=-12+i*10+settle*.7,s=.72,sy=.7)
 if cancel and f>=24:
  b+=path('M606 770L688 741','#7D5146',4)+g(tape(62,20,'#ADB8A1'),606,744,a=-18)
 return b

def price_action(f,cancel,seed):
 b=price_world(f,cancel)
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
  state='worried' if f>=42 else 'surprised' if 14<f<26 else 'focused'
  b+=bot(x,y,f,s=.29,jitter=False,performance=state,angle=-7 if f>=42 else 0,impact=hop_impact(f,25,34) if 25<=f<=39 else 0,craft='burden' if f>=44 else None,craft_age=f-44,gaze=1)
  if f>48:b+=path('M625 807L639 788M635 822L653 816',CORAL,4)
 else:
  x,y=hop(f,1,17,530,960,480,727,60)
  if f>24:x,y=hop(f,24,33,480,727,545,960,35)
  b+=bot(x,y,f,s=.29,jitter=False,performance='relieved' if f>=24 else 'focused',impact=hop_impact(f,1,17) if f<=23 else 0,acting_frame=f-24 if f>=24 else f,craft='release' if f>=24 else None,craft_age=f-24)
  if 24<=f<33:b+=path('M627 813L639 821M649 807L656 811',GREEN,3)
 return b

def speaker(x,y,f):
 d='M5 6L71 0L86 9L84 153L74 166L2 161L0 17Z'
 b=cut(d,'#566C72',.05)+g(card(68,145,INK,.02),8,9)
 for yy,r in [(48,21),(111,30)]:
  b+=f'<circle cx="42" cy="{yy}" r="{r+4}" fill="#857B87"/><circle cx="42" cy="{yy}" r="{r}" fill="#39343D"/>'+path(f'M{42-r*.4} {yy-r*.5}Q42 {yy-r*.8} {42+r*.5} {yy-r*.2}','#A695A1',1.5)
 b+=rect(33,149,19,4,GREEN,2)
 return g(b,x,y)

def launch_dock(f,seed):
 b=backdrop(COLORS[5],'room',f)
 b+=g(cut('M0 9L13 0L601 3L622 20L619 482L604 498L5 490Z','#627C85'),49,312)
 b+=g(cut('M0 5L589 0L600 16L595 473L3 478Z','#BEA48A'),61,323)
 b+=path('M63 732L173 544L377 703L536 527L654 719V796H63Z','#7B7D98',0,'#7B7D98')
 b+='<circle cx="481" cy="427" r="58" fill="#E7B686"/>'
 b+=g(tape(76,21),51,318,a=-13)+g(tape(74,20,'#D8C595'),580,315,a=9)
 b+=g(cut('M0 7L21 0L535 2L554 22L549 98L12 102L0 87Z','#F3EEDF'),85,727)+path('M95 827H629','#998A77',3)
 for i,c in enumerate([GREEN,CORAL,INK,GOLD,'#7392BF']):
  y=751-48*math.sin(math.pi*clamp(f/17)) if i==2 else 750
  if i==2:b+=g(card(142,133,INK,.04)+waveform(17,24,108,82,f,n=10),295,y-70,a=-2)
  elif i==0:
   b+=g(cut('M0 10L5 1H19L25 9H53L57 16L52 53H2Z',c,.018)+path('M4 23H49','#9DB6A2',2),112+i*109,y)
  elif i==1:
   b+=g(cut('M0 1H39L54 15V57H2Z',c,.018)+path('M39 1V15H54M10 29H40M10 40H32',CREAM,2),112+i*109,y,a=3)
  elif i==3:
   b+=g(cut('M1 2L24 6L52 0V51L26 57L0 52Z',c,.02)+path('M26 8V52M7 18L20 21M31 20L46 16',INK,1.5),112+i*109,y,a=-4)
  else:b+=g(cut('M0 0H54L57 10V52L48 58H0Z',c,.018)+path('M9 15L18 24L9 32M25 35H43',CREAM,3),112+i*109,y)
 b+=pointer(372,895-117*ease(f/8))
 if f>=8:b+=g(card(235,61,CREAM)+txt('VoiceStudio',117,43,37,INK,900,'middle'),245,579,a=-1)
 b+=edge_shelf(53,839,614)+g(card(91,68,'#B4C7B7')+path('M12 22H71M12 40H60',INK,2),19,866,a=-8)+g(tape(35,13),36,864,a=9)
 return b

def writing_voice(f,seed):
 b=backdrop(COLORS[7],'room',f)
 b+=path('M0 575L62 566L68 764H0Z','#77948A',1,'#ADC1A4')+g(tape(36,14),12,579,a=-8)
 # The source papers form an input tray. The speaker prints a scalloped output.
 b+=g(card(148,140,'#648B8D'),9,728,a=-6)
 for i,(c,a) in enumerate([(CREAM,-9),('#DAC393',4),(PINK,-3)]):b+=g(card(120,114,c)+path('M16 31H96M16 51H86M16 71H100','#998A78',2),21+i*7,748+i*12,a=a)
 b+=edge_shelf(0,889,187)
 b+=workbench(73,897,600)+monitor(90,350,570,380)+txt('Script',120,404,26)+txt('Import script   Paste   Insert',123,440,16,'#B8ACB6')+button('Synthesize audio',413,657,211)
 phase=0 if f<14 else 1 if f<28 else 2;age=f-[0,14,28][phase]
 phrases=[['milk, eggs,','bread, coffee'],['Roses are red,','my voice is my own'],['Local cat wins','the election']]
 for i,line in enumerate(phrases[phase]):b+=txt(line,123,526+i*46,31)
 if age<11:
  u=ease(age/11);scrap=cut('M0 0L137 2L150 16L146 120L4 119Z',[CREAM,PINK,'#E8DEBE'][phase])+txt(['SHOPPING','POEM','NEWS'][phase],73,34,18,INK,900,'middle')+path('M18 60H130M18 80H110M18 99H128','#A79C88',3)
  b+=g(scrap,82+178*u,866-344*u-75*math.sin(math.pi*u),a=-13+21*u,s=.85)
 b+=speaker(577,809,f)+path('M571 932Q564 946 557 964','#293B40',4)
 # Existing sound-ribbon cadence, now a printed paper tongue linked to the speaker.
 wave=cut('M0 17Q48 -7 104 16T210 13L205 75Q145 53 103 76T0 71Z',PINK,.02)
 wave+=waveform(17,22,170,38,f,n=24,color=INK,phase=1.4)
 b+=g(wave,424,764,a=2*math.sin(f*.12),s=.92)
 b+=bot(133,965,f,s=.30,performance='relieved',pose='presenting',gaze=1)
 return b

def dictation(f,seed):
 b=backdrop(COLORS[10],'room',f)+rect(0,725,720,242,'#789AA8')
 b+=g(card(587,444,'#768985'),83,354,a=2)
 b+=g(cut('M7 0L562 2L584 20L580 429L552 453L523 443L470 452L7 446L0 13Z','#F4F0E7'),63,329)
 b+=g(card(555,53,'#E3DFCF'),80,344)+txt('Notes',359,381,25,INK,900,'middle')
 for x in [104,137,170,203,236,269]:
  b+=g(path('M0 0V-20Q11 -32 22 -20V1','#64766D',5)+path('M3 -20Q11 -27 19 -20','#C6D5C7',2),x,344)
 b+=path('M88 413V743','#CDB4A5',2)
 for yy in [498,550,602,654,706]:b+=path(f'M99 {yy+8}H611','#E0DBCE',1.2)
 text='types out whatever you want to say';n=int(len(text)*clamp((f+3)/37));visible=text[:n];line1=visible[:22];line2=visible[22:].lstrip()
 b+=txt(line1,105,490,33,INK,900)+txt(line2,105,543,33,INK,900)
 if f%12<8:
  cx=105+len(line2 if len(visible)>22 else line1)*17;cy=543 if len(visible)>22 else 490;b+=path(f'M{cx} {cy-29}V{cy+4}',MAGENTA,2)
 b+=g(cut('M5 0L108 0L128 21L121 107L6 108Z','#DAC48E'),569,666,a=6)+path('M579 691H635M581 710H620','#A48B5F',2)
 # Floating input microphone remains the actual cause; remove decorative Bot.
 capsule=cut('M35 0L218 1Q256 1 258 36Q255 80 217 79H36Q0 77 0 39Q1 1 35 0Z',INK,.015)+'<circle cx="43" cy="39" r="26" fill="'+MAGENTA+'"/>'+path('M37 27V43Q43 50 49 43V27M43 50V58',CREAM,3)+waveform(84,20,151,40,f,n=22)
 b+=g(capsule,386,730,a=living(f,seed,.7))
 b+=g(cut('M0 0L160 0L177 16L173 81L0 80Z','#607D7A'),39,868,a=-6)+g(card(168,67,CREAM)+path('M14 22H149M14 42H130','#C1B498',3),60,887,a=5)+edge_shelf(16,950,243)
 b+=g(path('M0 0L18 -7L27 139L14 154L5 140Z','#A27945',1,'#D0A462')+path('M7 9L19 131','#E5C180',2)+path('M14 154L11 168L23 154Z','#34434B',1,'#34434B'),305,804,a=18)
 b+=mug(646,909,GREEN)
 return b

def transcribe(f,seed):
 b=backdrop(COLORS[11],'room',f)
 b+=g(card(94,273,'#688875'),614,398,a=3)+g(card(57,102,CREAM),641,390,a=5)+g(tape(45,17),636,390,a=-6)
 b+=clock(46,415,.75)
 # A tape-fed listening deck with a loading mouth and a separate output lip.
 b+=g(cut('M0 22L24 0L502 3L543 32L546 315L518 365L13 361L0 331Z','#577982'),92,337)
 b+=g(card(515,325,'#332636',.02),105,348)+txt('Upload & Transcribe',124,391,29,CREAM,900)
 b+=g(cut('M0 2L456 0L475 14L475 137L460 146L0 145Z','#493449',.012),125,422)+path('M130 440H595',PINK,2)
 b+=txt('Choose file…',363,462,21,CREAM,anchor='middle')+txt('Drop video or audio here',363,500,22,CREAM,anchor='middle')+txt('…or paste YouTube / video URL',363,541,13,'#B6A2AF',anchor='middle')+txt('Spoken language',125,606,17)
 b+=rect(125,641,479,8,'#53404F',4)+rect(125,641,479*clamp(f/17),8,MAGENTA,4)
 u=ease(f/12);file=cut('M0 0L132 0L149 16V66H0Z',PINK,.025)+txt('recording.wav',74,41,17,INK,anchor='middle')+path('M132 1V16H148','#AA6C89',1,'#D97EA1')
 b+=g(file,495-215*u,769-231*u-55*math.sin(math.pi*u),a=8*(1-u))
 lip=reaction(f,43,(605,906),(589,701),radius=280,relevance=.7,amplitude=6)
 b+=g(path('M127 689L608 687L624 705L115 708Z','#A7B8AC',1,'#A7B8AC')+path('M131 694H602','#253C43',5),y=lip)
 for i,start in enumerate([19,27,35,43]):
  if f>=start:
   u=ease((f-start)/7);x=84+(1-u)*100;y=726+i*57-10*clamp((f-42)/8)
   strip=cut('M0 5L13 0L585 3L599 12L598 59L576 62L19 60L0 63Z' if i==3 else 'M0 5L13 0L535 3L549 12L548 59L526 62L19 60L0 63Z',CREAM,.03)
   flutter=reaction(f,43,(605,906),(470,y),radius=260,relevance=.65,delay=max(0,3-i),amplitude=8) if i<3 else 0
   y+=flutter
   strip+=g(card(137,43,['#568CAF',CORAL][i%2])+txt(f'Speaker {i%2+1}',68,30,19,CREAM,900,'middle'),8,9)+path('M161 25H516M161 43H443','#B9B2A2',5)
   strip+=path('M536 14V47','#AA9B83',1)
   b+=g(strip,x+[0,-19,9,-27][i],y,a=[-1.4,1.1,-.6,2.8][i]*u)
   if i==3:
    b+=g(cut('M0 0L18 4L20 46L9 57L-2 51Z','#D7CCB5',.02)+path('M2 3Q13 19 9 54','#AEA28E',1.5),x+559,y+8,a=2.8*u)
 state='focused' if f<43 else 'relieved'
 b+=bot(645,965,f,s=.265,performance=state,gaze=-1,contact=(609,907) if f>=43 else None,contact_hand='l',jitter=False,acting_frame=f-43 if f>=43 else f)
 return b

def workflow(f,seed):
 b=backdrop(COLORS[12],'room',f)
 b+=g(cut('M0 0L24 2L28 524L2 532Z','#617F82'),76,342)+g(cut('M0 2L26 0L24 523L1 531Z','#617F82'),650,342)
 b+=g(cut('M0 16L20 0L223 3L241 19L237 99L7 97Z','#D2B691'),239,369)
 b+='<circle cx="35" cy="443" r="34" fill="#D2B7A0"/>'
 for i in range(4):b+=f'<circle cx="{35+19*math.cos(i*math.pi/2)}" cy="{443+19*math.sin(i*math.pi/2)}" r="8" fill="#8D6659"/>'
 b+=path('M81 873H673','#40585E',5)+edge_shelf(36,948,643)
 b+=path('M24 477Q4 561 40 604T35 773Q29 820 16 870','#392C38',16)
 for yy in [501,540,579,618,657,696,735,774,813,852]:b+=rect(26,yy,6,6,CREAM,1)
 b+=ring(356,422,43,clamp(f/42),f,f>=42)
 labels=['3 Generate Dub','2 Translate','1 Upload & Transcribe'];fin=[40,29,14]
 for i,label in enumerate(labels):
  y=492+i*104;p=clamp((f-[30,15,0][i])/14)
  shell=cut('M0 7L11 0L539 1L553 12L552 80L538 89L0 86Z',['#75536C','#536C78','#7D6653'][i],.025)
  shell+=g(card(405,75,'#302331',.02),139,5)+txt(label,147,37,23)+rect(154,60,391,7,'#634158',3)+rect(154,60,391*p,7,MAGENTA,3)
  if i==2:
   shell+=rect(18,17,83,47,INK,3)+path('M59 24V50M47 36L59 24L71 36',CREAM,4)
   for xx in [24,48,72]:shell+=path(f'M{xx} 12L{xx+12} 5',CREAM,5)
  elif i==1:
   shell+=g(card(51,42,CREAM)+txt('EN',25,29,21,INK,900,'middle'),17,19,a=-6)+g(card(51,42,PINK)+txt('ES',25,29,21,INK,900,'middle'),68,23,a=7)
  else:shell+=waveform(18,17,103,47,f,n=16)+path('M18 73H119',CREAM,2)
  b+=g(shell,99,y)+path(f'M101 {y}L650 {y-1}','#B8A98C',3)
  if f>fin[i]:b+=check(615,y+39,.63)
 x,y=123,963
 if f<=15:x,y=hop(f,2,14,123,963,146,700,55)
 elif f<=30:x,y=hop(f,17,29,146,700,159,596,52)
 elif f<=40:x,y=hop(f,32,40,159,596,176,492,52)
 else:x,y=hop(f,42,51,176,492,598,939,110)
 stage=(0,14) if f<15 else (15,29) if f<30 else (30,40) if f<41 else (40,51)
 b+=bot(x,y,f,s=.235,jitter=False,performance='impact' if f==stage[1] else 'relieved' if f>40 else 'focused',impact=hop_impact(f,*stage),acting_frame=0 if f==stage[1] else f)
 clap=cut('M0 0H122V91L5 94Z',INK,.015)+rect(0,-15,122,25,CREAM,2)
 for i in range(5):clap+=path(f'M{i*27} -15L{i*27+21} 10',INK,11)
 b+=g(clap,563,862,a=math.sin(f*.2)*2)
 if f>=38:
  u=spring((f-38)/8);b+=g(cut('M0 9L12 0L414 1L434 19L432 103L7 109Z',CREAM)+g(tape(55,17),23,-4,a=-7)+txt('Video Dubbing Studio',219,48,28,INK,900,'middle')+txt('MP4 · MOV · MKV · WEBM · MP3 · WAV · FLAC · M4A',218,80,11,INK,anchor='middle'),95,836,s=.83+.17*u)
 return b

def bilingual(f,seed):
 b=backdrop(COLORS[13],'room',f)
 b+=g(cut('M0 17L18 0L474 3L502 25L505 600L480 632L9 628Z','#849592'),144,320)
 for i,(label,tag,y,col,phase) in enumerate([('English','ORIGINAL',402,'#B9ADB6',.4),('Español','DUBBED',680,PINK,2.1)]):
  b+=g(card(478,230,'#342B36',.02),156,y-51)
  b+=g(cut('M0 0L78 0L88 10L83 62L5 64Z',CREAM if i==0 else PINK,.025)+txt('EN' if i==0 else 'ES',42,43,29,INK,900,'middle'),100,y-33,a=-4 if i==0 else 5)
  b+=txt(label,203,y-27,30,col,900)+txt(tag,606,y-27,16,col,anchor='end')
  b+=rect(177,y+10,436,155,'#362B37' if not i else '#372332',8,PINK if i and f>=8 else '#68515F',2)
  b+=waveform(192,y+40,406,102,f,n=45,color=col,phase=phase)+path(f'M{192+404*clamp((f-8*i)/(35 if not i else 27))} {y+24}V{y+152}',PINK if not i else CREAM,2)
  b+=path(f'M181 {y+171}L601 {y+172}','#908375',2)
 b+=g(card(463,48,'#342B36',.012),164,884)
 b+=txt('Español',177,914,19,PINK)+txt('Français',299,914,17)+txt('中文',429,914,17)+txt('日本語',523,914,17)
 if f>=24:b+=path('M177 923H253',PINK,4)
 b+=speaker(8,460,f)+edge_shelf(0,639,115)
 b+=g(card(81,68,'#D1B981')+path('M12 22H63M12 43H54','#9B865F',2),613,879,a=7)
 b+=bot(91,962,f,s=.255,performance='focused' if f<24 else 'relieved',pose='pointing',contact=(165,790),jitter=False,gaze=1)
 return b

def languages(f,seed):
 b=backdrop(COLORS[14],'room',f)
 b+=g(cut('M0 5L209 0L232 23L240 508L219 527L16 521L0 498Z','#D9C19C'),51,360,a=-2)
 b+=g(cut('M0 0L210 3L235 19L231 464L213 477L195 469L175 478L153 470L135 478L115 470L96 478L76 470L57 479L38 470L20 479L0 466Z',CREAM),62,370,a=-2)
 b+=g(tape(79,23),111,360,a=-8)+txt('ElevenLabs',79,423,27,INK,900)+txt('Dubbing',80,469,28,INK,900)+txt('90+',177,596,79,MAGENTA,900,'middle')+txt('languages',177,651,25,INK,anchor='middle')+txt('and accents',177,690,22,INK,anchor='middle')
 # A tabbed, deeply stacked language index; no decorative small mascot.
 b+=g(cut('M0 34L20 3L78 0L94 29L311 27L333 45L331 557L313 578L7 572Z','#597781'),322,353)
 for i in range(4):b+=g(card(47,64,['#C9B482','#CF9D8C','#9DB79A','#82A5B4'][i])+path('M10 17H31M10 29H26',INK,2),636,454+i*98,a=[5,-3,7,1][i])
 b+=g(card(310,511,'#2B2331',.018),331,394)+txt('Manage languages ▾',350,427,18)
 count=int(152*f/12) if f<=12 else int(152+305*(f-12)/15) if f<=27 else int(457+189*ease((f-27)/13));count=min(646,count)
 b+=g(cut('M0 13L19 0L261 2L283 20L279 99L13 103L0 88Z','#793249',.025)+txt(str(count),139,69,66,CREAM,900,'middle'),342,277,a=living(f,seed,.55))
 b+=path('M354 378H611','#A38666',4)
 names=['English','Español','Français','Deutsch','Italiano','Português','Русский','Kiswahili','Tagalog','Türkçe','Tiếng Việt','Yorùbá','Polski','ไทย','한국어','Ελληνικά','Svenska','isiZulu','Suomi','Magyar','Cymraeg','Íslenska','Quechua'];scroll=clamp(f/43)*820
 for i,name in enumerate(names):
  yy=449+i*53-scroll
  if 437<yy<897:
   tab=cut('M0 0L263 1L276 12L270 42L3 44Z',['#5A4E59','#3D4D50','#584251'][i%3],.012)+rect(10,11,16,17,'#2E2430',3,PINK,1)+txt(name,40,30,21)
   b+=g(tab,343+[0,5,-3][i%3],yy-22)
 b+=edge_shelf(26,945,669)+g(card(121,38,'#668786'),60,907,a=-8)+g(card(109,35,'#D4C29C'),65,915,a=4)
 return b

def privacy(f,seed,transition=True):
 b=rect(0,0,720,1280,'#BDAD96')+g(rect(0,0,720,1280,'url(#worldPaper)'),opacity=.17)
 for i in range(10):
  x=i*78-15;y=470+((i*31)%5)*38;b+=rect(x,y,69,470,'#293B59')
  for k in range(4):
   for j in range(3):b+=rect(x+10+j*17,y+35+k*49,8,11,GOLD)
 b+=rect(0,919,720,61,'#A28A78')+rect(0,980,720,300,'#809AA4')
 for x in range(0,720,94):b+=path(f'M{x} 927V975','#736A64',2)
 b+=path('M0 945H720','#736A64',2)
 cloud=cut('M-80 15Q-115 -31 -53 -46Q-36 -105 22 -79Q86 -95 93 -39Q147 -16 111 20Z','#E8E0D0',.02)
 b+=g(cloud,363,300,a=living(f,seed,.5))+path('M480 315H668V664H636','#786E63',3)
 b+=monitor(70,365,590,459,True)
 lines=['It runs entirely','on your machine.','No accounts,','no cloud, no API keys.']
 for i,line in enumerate(lines):b+=txt(line,100,443+i*49,29 if i<2 else 27,CREAM,900)
 for i,start in enumerate([16,23,29,35]):
  if f>=start:b+=path(f'M100 {454+i*49}H{100+[267,285,191,342][i]*ease((f-start)/7)}',MAGENTA,4)
 b+=g(cut('M0 11L10 0H81L93 12V109H0Z','#493B49',.012)+path('M41 65V22M22 43L41 22L60 43',CREAM,5),350,645)
 b+=g(cloud,391,650,s=.14)+g(card(81,50,CREAM)+txt('0%',40,35,29,INK,900,'middle'),471,695)
 if f<14:b+=ring(430,722,21,.13,f)
 else:
  b+=g(cut('M0 0L107 1L116 14L109 29L4 26Z','#CA8A72',.025)+path('M16 6L6 21M41 7L31 22M66 7L56 22M91 7L81 23','#74513F',3),341,687)+cross(430,722,.84)
 # A local output pocket receives the unchanged rejected token trajectory.
 pocket=cut('M0 15L15 0L165 2L182 19L175 146L6 144Z','#607F7D',.03)+g(card(151,108,'#D2C3A7'),14,18)+txt('LOCAL',87,136,20,CREAM,900,'middle')
 b+=g(pocket,425,800)
 u=clamp(f/13)
 if f<14:b+=token(267+69*u,780-72*u,s=.66,a=-3)
 elif f<28:b+=token(336+13*(f-14),708+((f-14)/14)**2*225,s=.66,a=(f-14)*6)
 else:b+=token(492,880,s=.66,a=-4)
 # The physical front lip is always separate from the retained data token.
 b+=g(cut('M0 0L162 1L176 14L169 44L6 46Z','#799590',.025)+path('M19 12H145','#ABC1AC',2),429,902)
 b+=bot(641,959,f,s=.265,jitter=False,performance='focused' if f<16 else 'relieved',gaze=-1,contact=(602,899) if f>=28 else None,contact_hand='l',acting_frame=f-16 if f>=16 else f)
 if transition and f>=47:
  u=ease((f-47)/12);incoming=baseline_scene(19,f-59,'COMMENT VOICE FOR THE SETUP',seed+101,False)
  b=g(b+headline('YOUR RECORDINGS STAY ON YOUR MACHINE'),-720*u,0)+g(incoming,720*(1-u),0)
  if 48<f<57:b='<g filter="url(#pushBlur)">'+b+'</g>'
  return b
 return b

def scene(number,f,headline_text,seed=5107,transition=True):
 if number not in CHANGED:return baseline_scene(number,f,headline_text,seed,transition)
 renderer={2:repo,6:launch_dock,8:writing_voice,11:dictation,12:transcribe,13:workflow,14:bilingual,15:languages}
 if number in (3,16):b=price_action(f,number==16,seed)
 elif number==18:
  b=privacy(f,seed,transition)
  if transition and f>=47:return b
 else:b=renderer[number](f,seed)
 return b+headline(headline_text)
