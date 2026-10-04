"""Existing Dot-token and job-brief drawings reused unchanged; no new character art."""
from common import *
def lines(x,y,w,count=4,color=SLATE):
 return ''.join(path(f'M{x} {y+i*24}h{w-(i%3)*22}',color,5) for i in range(count))
def token(x,y,r=32,t=0,working=False,name=False):
 b=dot(0,0,r,t,working)+path(f'M{-r*.44} {-r*.87}Q{-r*.7} {-r*.54} {-r*.93} {-r*.14}',TEAL,max(9,r*.3))
 if not name:b=b.replace('>DOT</text>','>•</text>')
 return g(b,x,y)
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

