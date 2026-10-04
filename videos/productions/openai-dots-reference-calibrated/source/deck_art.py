"""Static compositions for the second live plan's single supported task deck.
Canonical puppet parts and contact mathematics; no timed choreography here.
"""
from art import *
from motif_reaction import inverse_point
from build_motif_bot import assemble_pose,alternate_view
import xml.etree.ElementTree as ET

def worker(contact,phase='draft'):
 x,scale,lean=(-33,.26,15) if phase=='dock' else (41,.32,9) if phase=='seat' else (401,.28,-14)
 y=910-scale*904;parent=matrix(x,y,0,scale,scale);local=compose(matrix(512,904),compose(matrix(rotation=lean),matrix(-512,-904)));xy=inverse_point(compose(parent,local),contact)
 hand='r' if phase in ('dock','seat') else 'l';overrides={'l':(290,690,'mitten'),'r':(720,700,'mitten'),'feet':((383,879,-14),(638,846,10)) if phase=='dock' else ((425,861,-5),(599,861,5)),'head_tilt':0};overrides[hand]=(*xy,'open')
 foot_xs=(75,144) if phase=='dock' else (177,234) if phase=='seat' else (518,570)
 feet=[inverse_point(compose(parent,local),(fx,910-scale*43)) for fx in foot_xs];overrides['feet']=tuple((*f,-lean) for f in feet)
 body,_=assemble_pose('standing','determined',overrides)
 # Reuse the existing locked graphic profile head. No new character geometry.
 tree=ET.fromstring('<g>'+body+'</g>');profile=ET.fromstring('<svg>'+alternate_view('left-side')+'</svg>');head=profile.find('.//g[@id="head"]')
 if phase=='draft':head.attrib['transform']='translate(1024 0) scale(-1 1)'
 for parent_node in tree.iter():
  for child in list(parent_node):
   if child.attrib.get('data-part')=='head':parent_node.remove(child);parent_node.append(head);break
 body=re.sub(r'id="[^"]+"','',ET.tostring(tree,encoding='unicode'))
 return g(f'<g transform="translate(512 904) rotate({lean}) translate(-512 -904)">{body}</g>',x,y,scale)

def brief(x,y,w=260,h=160,state='source'):
 b=card(w,h,CREAM)+path(f'M{w-31} 0L{w+17} -23V{h-25}L{w-31} {h}Z',EDGE,3,MINT)+path(f'M{w-31} 0V{h}',TEAL,4)
 b+=path('M0 15V56',TEAL,14)
 # The same two source shapes survive inside later synthesis/draft faces.
 if state=='source':b+=g(card(w*.36,h*.43,GOLD),w*.08,h*.19,a=-4)+g(card(w*.33,h*.46,SLATE),w*.5,h*.17,a=3)
 else:
  b+=rect(w*.09,h*.2,w*.12,h*.24,GOLD,3)+rect(w*.24,h*.2,w*.12,h*.24,SLATE,3)+lines(w*.4,h*.22,w*.36,2,DARK)
  b+=lines(w*.09,h*.61,w*.68,2,DARK)
  if state=='draft':b+=path(f'M{w*.76} {h}L{w*.94} {h+38}L{w*.98} {h+11}L{w*.9} {h-16}Z',EDGE,3,CORAL)+rect(w*.77,h*.66,25,25,EDGE,3)
 return g(b,x,y,a=-2)

def stage(phase='dock',engage=1,carrier=1,state='source',closed=0,acting=True,background=True):
 b=backdrop(DARK) if background else ''
 # One upright display, visibly hinged into the broad task deck.
 b+=path('M364 407L631 421L652 629L367 628Z',EDGE,6,CREAM)+path('M386 433L610 445L628 596L386 592Z',TEAL,4,INK)+icon('cloud',502,500,.9,CREAM)
 b+=path('M376 617H638L666 865L352 891Z',EDGE,6,TEAL)+path('M352 891L666 865V892L351 921Z',EDGE,4,DARK)
 b+=path('M486 915L676 898L679 938L481 953Z',EDGE,5,CREAM)+path('M516 955L533 997H655L654 942',EDGE,5,DARK)
 gap=(1-engage)*78
 b+=path(f'M{190-gap} 619L{328-gap} 615L{331-gap} 867L{195-gap} 883Z',EDGE,5,TEAL)+path(f'M{195-gap} 883L{331-gap} 867V889L{199-gap} 904Z',EDGE,4,DARK)
 b+=g(card(136,64,CREAM),197-gap,570,a=-2)+icon('folder',234-gap,600,.6,DARK)+lines(270-gap,593,46,2,DARK)
 b+=path(f'M{328-gap} 595H{413-gap}V785H{328-gap}Z',EDGE,5,MINT)+path('M412 595H481V785H412Z',DARK,8,DARK)+path('M416 604H470V776H416',CREAM,5)
 # Carrier is supported by the same wing/deck and stops against the attached lip.
 b+=path('M557 610L578 608L580 817L557 825Z',DARK,5,CREAM)
 if phase=='dock':b+=brief(200-gap,647,114,108,'source');contact=(190-gap,836)
 elif phase=='seat':b+=brief(300,641,220,151,'source');contact=(303,795)
 else:
  b+=brief(160,558,345,237,state)+g(card(87,45,CORAL),413,805)+icon('spark',456,827,.44,CREAM);contact=(453,827)
 b+=path('M581 552H625V594H581Z',DARK,6,MINT)+token(603,572,29,working=True)
 # Subordinate user sleeve stays across a gap on the foreground ledge.
 b+=g(capsule(147,87,CREAM),60,896,a=-5)+text('…',129,947,41,DARK,'middle')
 b+=path('M72 910H288L310 938H50Z',EDGE,5,CREAM)+path('M50 938L310 938L287 997H80Z',EDGE,5,DARK)
 if acting:b+=worker(contact,phase)
 return b

def framed(phase='seat'):
 body=stage(phase,.9 if phase=='dock' else 1,state='draft' if phase=='draft' else 'source',background=False)
 zoom,focus,target=(1.45,(315,697),(360,410)) if phase=='dock' else (1.1,(450,700),(360,650)) if phase=='seat' else (1.35,(400,680),(360,590))
 return backdrop(DARK)+g(body,target[0]-focus[0]*zoom,target[1]-focus[1]*zoom,zoom)

def concept_states():return [(phase,framed(phase)) for phase in ['dock','seat','draft']]
