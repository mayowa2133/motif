"""Static artwork executing the accepted two-setup patch; no motion adapters.
Connection resets into a single captured-strip process. Prune the body at b04.
"""
from common import *
from identity import token,brief,lines

def support(x,y,w,color=TEAL):
 return path(f'M{x} {y}L{x+w} {y-5}L{x+w+12} {y+26}L{x-11} {y+31}Z',EDGE,4,color)+path(f'M{x-11} {y+31}L{x+w+12} {y+26}V{y+43}L{x-11} {y+48}Z',DARK,0,DARK)

def app_terminal(joined=False):
 b=path('M145 761H282V811H145Z',DARK,0,DARK)+g(card(296,337,CREAM),78,431,a=-2)+icon('folder',197,506,1.15,DARK)
 # Quiet app cue; cause and resulting link share the enlarged contact face.
 b+=path('M197 543V627H349V731',TEAL,4)
 b+=path('M334 691H425V791H334Z',EDGE,5,MINT)+path('M421 697V785',DARK,6)
 b+=f'<circle cx="354" cy="737" r="7" fill="{DARK}"/><circle cx="390" cy="737" r="7" fill="{DARK}"/>'
 if joined:b+=path('M354 737H390',DARK,7)
 b+=support(64,807,593,TEAL)
 return b

def connection(state):
 body=app_terminal(state=='after')+token(541 if state=='before' else 495,737,70,working=state!='before')
 # The clean junction is the hero; the app board is a cropped origin cue.
 return backdrop(CORAL)+g(body,-215,-405,1.5)

def computer_shell():
 # One working bay, not a second dominant monitor above the input.
 b=g(card(400,360,CREAM),264,448,a=1)
 b+=icon('cloud',458,489,.85,SLATE)+path('M337 539H493',SLATE,3)
 b+=path('M584 562H641V646H584Z',EDGE,4,TEAL)+token(613,600,31,working=True)
 b+=support(69,829,586,CREAM)
 b+=path('M580 864L599 1001H633L622 861',DARK,0,DARK)+path('M113 873L100 1001H130L143 870',EDGE,0,EDGE)
 return b

def aperture(x=400,y=619,w=245,h=211):
 return g(card(w,h,DARK),x,y)+path(f'M{x} {y+14}H{x+w-10}V{y+h-8}H{x}',MINT,6)

def input_transfer(state):
 x={'before':100,'contact':164,'after':309}[state];b=backdrop(SLATE)+computer_shell()+aperture()
 # The very same 438×285 job-brief drawing appears at a smaller camera scale.
 b+=g(brief(0,0,438,285,'source'),x,682,.52)
 b+=path('M400 822H640V852H400Z',EDGE,5,TEAL)+path('M400 635H638V652H400Z',EDGE,4,CREAM)
 b+=path('M627 637H645V838H627Z',EDGE,5,CREAM)
 b+=path('M-58 975L111 953L143 991L-68 1011Z',EDGE,5,CREAM)+path('M-33 975L116 967',SLATE,5)
 return b

def progress_spec(state):
 return {
  'before':(72,'source'),'contact':(128,'outline'),'after':(180,'draft'),
  'source-to-outline-before':(72,'source'),'source-to-outline-contact':(104,'outline-partial'),'source-to-outline-after':(128,'outline'),
  'outline-to-draft-before':(128,'outline'),'outline-to-draft-contact':(154,'draft-partial'),'outline-to-draft-after':(180,'draft'),
  'inactive-source':(72,'source'),'inactive-outline':(128,'outline'),'inactive-draft':(180,'draft')
 }[state]

def work_strip(state):
 x,phase=progress_spec(state)
 # The identity edge, notch and raised corner MOVE with one continuous strip.
 kind='source' if phase=='source' else 'synthesis'
 b=path(f'M-110 534L{x} 541V826L-110 819Z',EDGE,4,CREAM)+brief(x,541,438,285,kind)
 if phase.startswith('outline'):
  # Organization stays printed within the moving material, never floating outside.
  b+=path(f'M{x+172} 590V714M{x+172} 590H{x+207}M{x+172} 652H{x+207}M{x+172} 714H{x+207}',DARK,5)
  for i in range(2 if phase=='outline-partial' else 3):
   b+=path(f'M{x+219} {588+i*62}H{x+381}',DARK,6)+path(f'M{x+219} {607+i*62}H{x+338}',SLATE,4)
 if phase.startswith('draft'):
  # Expand the outline into two visible paragraph groups, retaining source colors.
  b+=rect(x+167,580,236,220,CREAM)
  for col,color in [(0,GOLD),(1,SLATE)]:
   px=x+175+col*114;b+=rect(px,592,93,24,color,3)
   for row in range(2 if phase=='draft-partial' else 4):b+=path(f'M{px} {635+row*28}h{88-(row%2)*14}',DARK,5)
  b+=path(f'M{x+26} 786H{x+345}',CORAL,5)
  # Pending continuation belongs to this sheet and passes UNDER the capture lip.
  b+=path(f'M{x+361} 781L{x+424} 784L{x+427} 829L{x+363} 826Z',EDGE,3,CORAL)
  b+=rect(x+378,797,22,18,EDGE,3)
 return b

def process(state,interaction=None):
 b=backdrop(DARK)+aperture(62,481,584,374)+work_strip(state)
 # The front lips stay fixed while border, source material and draft advance.
 b+=path('M63 824H645V871H63Z',EDGE,5,TEAL)+path('M63 491H645V526H63Z',EDGE,4,CREAM)
 b+=path('M627 496H649V858H627Z',EDGE,5,CREAM)
 b+=path('M582 414H638V486H582Z',EDGE,4,TEAL)+token(610,449,31,working=True)
 if state.startswith('inactive-'):b+=path('M-50 970L71 955L94 990L-58 1007Z',EDGE,4,EDGE)+path('M-23 979L70 968',SLATE,4)
 return b

def frame(beat_id,state,interaction=None):
 if beat_id=='b02':return connection(state)
 if beat_id=='b03':return input_transfer(state)
 if beat_id=='b04':return process(state,interaction)
 raise ValueError('No art adapter outside the authorized connected-work beats')
