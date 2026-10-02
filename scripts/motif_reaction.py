"""Deterministic, selected local response. No DOM discovery or random shake."""
import math

def reaction(age, origin, position, radius, relevance, amplitude, duration=.6, delay=0):
    if not 0 < radius <= 2000 or not 0 < duration <= 1.2 or not 0 <= delay <= .3 or not 0 <= relevance <= 1:
        raise ValueError('reaction outside bounded contract')
    if set(amplitude) != {'x','y','rotation'} or any(abs(amplitude[k]) > (12 if k=='rotation' else 30) for k in amplitude):
        raise ValueError('reaction amplitude outside bounds')
    t=age-delay
    if not 0 <= t < duration:return dict(x=0.,y=0.,rotation=0.)
    distance=math.dist(origin,position)
    gain=max(0,1-distance/radius)**.65*relevance
    # v6 decay/oscillation expressed in seconds; window reaches zero continuously.
    pulse=math.exp(-t*30/5.2)*math.cos(t*30*.72)*(1-t/duration)**2
    return {k:round(v*gain*pulse,6) for k,v in amplitude.items()}

def matrix(x=0,y=0,rotation=0,sx=1,sy=1):
    a=math.radians(rotation);c,s=math.cos(a),math.sin(a)
    return (c*sx,s*sx,-s*sy,c*sy,x,y)

def compose(main,local):
    a,b,c,d,e,f=main;g,h,i,j,k,l=local
    return (a*g+c*h,b*g+d*h,a*i+c*j,b*i+d*j,a*k+c*l+e,b*k+d*l+f)

def point(m,p):
    a,b,c,d,e,f=m;x,y=p;return (a*x+c*y+e,b*x+d*y+f)

def inverse_point(m,p):
    a,b,c,d,e,f=m;det=a*d-b*c
    if abs(det)<1e-9:raise ValueError('singular contact transform')
    x,y=p[0]-e,p[1]-f;return ((d*x-c*y)/det,(-b*x+a*y)/det)

def grip(prop_transform,anchor,puppet_transform):
    """Call after composing BOTH reaction and main transforms."""
    return inverse_point(puppet_transform,point(prop_transform,anchor))
