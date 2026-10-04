"""Static artwork executing the accepted two-setup patch; no motion adapters.
Connection resets into a single captured-strip process. Prune the body at b04.
"""
from common import *
from identity import token,brief,lines

def support(x,y,w,color=TEAL):
 return path(f'M{x} {y}L{x+w} {y-5}L{x+w+12} {y+26}L{x-11} {y+31}Z',EDGE,4,color)+path(f'M{x-11} {y+31}L{x+w+12} {y+26}V{y+43}L{x-11} {y+48}Z',DARK,0,DARK)

def app_terminal(joined=False):
 b=path('M145 761H282V811H145Z',DARK,0,DARK)+g(card(296,337,CREAM),78,431,a=-2)+icon('folder',197,506,1.45,DARK)
 # Two printed circuit termini join only after the clean physical contact.
 b+=path('M147 591H211M260 591H308V733H374',TEAL,12)
 b+=f'<circle cx="211" cy="591" r="14" fill="{TEAL}"/><circle cx="260" cy="591" r="14" fill="{TEAL}"/>'
 if joined:b+=path('M211 591H260',TEAL,12)
 b+=path('M365 691H425V791H365Z',EDGE,5,MINT)+path('M421 697V785',DARK,6)
 b+=support(64,807,593,TEAL)
 return b

def connection(state):
 b=backdrop(CORAL)+app_terminal(state=='after')
 b+=token(563 if state=='before' else 495,737,70,working=state!='before')
 # Original conversation pocket is inactive, tiny and cropped before engagement.
 b+=g(card(100,71,EDGE),-69,375,a=-4)+text('…',4,414,25,SLATE,'middle')
 return b

def computer_shell():
 b=g(card(400,390,CREAM),264,370,a=1)+g(card(354,225,INK),283,389,a=1)
 b+=icon('cloud',458,439,1.2,CREAM)+path('M316 499H543M316 532H588',TEAL,7)
 b+=g(card(398,71,TEAL),264,740)+path('M287 757H631',DARK,7)
 # Ownership token stays attached and subordinate, never pushing the brief.
 b+=path('M584 562H641V646H584Z',EDGE,4,TEAL)+token(613,600,31,working=True)
 b+=support(69,829,586,CREAM)
 b+=path('M580 864L599 1001H633L622 861',DARK,0,DARK)+path('M113 873L100 1001H130L143 870',EDGE,0,EDGE)
 return b

def aperture(x=334,y=619,w=306,h=211):
 # A recessed bay with a broad open side and planar foreground lips.
 return g(card(w,h,DARK),x,y)+path(f'M{x} {y+14}H{x+w-10}V{y+h-8}H{x}',MINT,6)

def input_transfer(state):
 x={'before':77,'contact':109,'after':243}[state];b=backdrop(SLATE)+computer_shell()+aperture()
 b+=brief(x,650,224,172,'source')
 # Contact at the open side precedes partial capture beneath the same bay lip.
 b+=path('M334 822H640V852H334Z',EDGE,5,TEAL)+path('M334 635H638V652H334Z',EDGE,4,CREAM)
 b+=path('M627 637H645V838H627Z',EDGE,5,CREAM)
 # The user computer is separated, closed and inactive throughout capture.
 b+=path('M-58 975L111 953L143 991L-68 1011Z',EDGE,5,CREAM)+path('M-33 975L116 967',SLATE,5)
 return b

def work_strip(state):
 # Preserve cream stock, raised mint corner, teal notch and the same source shapes.
 kind='source' if state in ('before','source-edge','chat-open','source-to-outline-before') else 'synthesis' if state in ('contact','outline-edge','chat-closed-early','source-to-outline-contact','source-to-outline-after','outline-to-draft-before') else 'draft'
 b=brief(104,541,438,285,kind)
 # Output remains visibly unfinished; a pending border feeds in from the left.
 b+=path('M46 534L104 541L105 826L47 819Z',EDGE,4,CREAM)+path('M59 550V792',TEAL,8)
 if state in ('contact','outline-edge','source-to-outline-contact'):
  # Outgoing source excerpt is part of the strip, not a separate apparatus.
  b+=g(card(57,64,GOLD),498,568,a=-2)+g(card(52,68,SLATE),550,565,a=2)
 if state=='outline-to-draft-contact':b+=lines(481,559,121,3,SLATE)
 if kind=='draft':b+=path('M534 783L584 813L602 790L558 760Z',EDGE,4,CORAL)
 return b

def process(state,interaction=None):
 # Tight crop of the SAME aperture: no computer master, input tray or app terminal.
 b=backdrop(DARK)+aperture(62,481,584,374)+work_strip(state)
 # Continuous front overlap is the captured strip's contact and support.
 b+=path('M63 824H645V871H63Z',EDGE,5,TEAL)+path('M63 491H645V526H63Z',EDGE,4,CREAM)
 b+=path('M627 496H649V858H627Z',EDGE,5,CREAM)
 b+=path('M582 414H638V486H582Z',EDGE,4,TEAL)+token(610,449,31,working=True)
 # A small closed user-side edge may appear in state comparisons only; crop it
 # out of the three primary proofs so obsolete geometry does not compete.
 if state.startswith('chat-'):b+=path('M-50 970L71 955L94 990L-58 1007Z',EDGE,4,EDGE)+path('M-23 979L70 968',SLATE,4)
 return b

def frame(beat_id,state,interaction=None):
 if beat_id=='b02':return connection(state)
 if beat_id=='b03':return input_transfer(state)
 if beat_id=='b04':return process(state,interaction)
 raise ValueError('No art adapter outside the authorized connected-work beats')
