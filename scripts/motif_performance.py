"""Named acting, using only locked Motif Bot v1 geometry and existing hands."""
import math,re
from build_motif_bot import assemble_pose
from motif_reaction import matrix,compose,grip
STATES=('talking','listening','focused','anticipating','impact-light','impact-heavy','worried','burdened','surprised','relieved','celebrating','climbing','typing')

def channels(state,t):
    if state not in STATES:raise ValueError('unsupported performance: '+state)
    t=max(0,t);w=math.exp(-t*30/8);s=math.sin(t*30*.38)
    c=dict(face='neutral',head=0,antenna=0,head_drop=0,sy=1,angle=0,l=(340,654,'mitten'),r=(684,654,'mitten'),feet=((425,861,0),(599,861,0)))
    if state=='talking':c.update(face='happy',head=7+3*s,antenna=5*math.sin(t*30*.38-1.1),angle=2,r=(711,593+9*s,'open'))
    elif state=='listening':c.update(head=-8,antenna=3,l=(362,687,'mitten'),r=(663,687,'mitten'))
    elif state=='focused':c.update(face='determined',head=8,antenna=-5,angle=3,r=(700,597,'point'))
    elif state=='anticipating':c.update(head=12,antenna=-13,sy=.87,l=(399,689,'fist'),r=(627,677,'fist'))
    elif state.startswith('impact-'):
        heavy=state=='impact-heavy';w=math.exp(-t*30/(4.8 if heavy else 2.7))
        c.update(head=(17 if heavy else -13)*w,antenna=(-27 if heavy else 21)*math.cos(t*30*.7)*w,sy=1-(.21 if heavy else .09)*w,angle=(-9 if heavy else 8)*w,l=(399-61*(1-w),702-92*(1-w),'fist' if heavy and t<.1 else 'open'),r=(681+36*w,547-50*w,'open'))
    elif state=='worried':c.update(face='worried',head=12,antenna=-18,angle=-5,sy=.9,l=(414,678,'fist'),r=(615,667,'fist'))
    elif state=='burdened':
        load=min(1,t*2);c.update(face='worried',head=18+5*load,head_drop=20+12*load,antenna=-31,sy=.84-.06*load,angle=3,l=(442,697,'fist',-25,-12),r=(590,684,'fist',22,16))
    elif state=='surprised':c.update(face='surprised',head=-17+9*math.sin(t*12)*w,antenna=20+23*math.sin(t*15.6)*w,sy=1.08+.03*w,l=(230,470+96*(1-w),'open'),r=(810,449+113*(1-w),'open'))
    elif state=='relieved':c.update(face='happy',head=-17+6*math.sin(t*12.9)*w,antenna=9+26*math.sin(t*15.6+.3)*w,sy=1.06+.07*math.sin(t*14.4)*w,angle=-3+4*math.sin(t*12.9)*w,l=(274,548+56*(1-w),'open'),r=(756,497+111*(1-w),'open'))
    elif state=='celebrating':c.update(face='excited',head=-11,antenna=16,sy=1.05,angle=3*s,l=(248,470,'open'),r=(786,460,'open'))
    elif state=='climbing':c.update(face='determined',head=-10,antenna=-8,angle=8,l=(290,430,'grip'),r=(740,530,'grip'),feet=((405,810+30*s,-12),(632,840-30*s,12)))
    elif state=='typing':c.update(face='determined',head=14,antenna=-9,sy=.94,l=(440,719+12*s,'fist'),r=(598,719-12*s,'fist'))
    return c

def render(state,t,contacts=None):
    """Canonical local coordinates. Contacts specify already-composed world matrices.

    contacts[hand] = {prop_transform, anchor, puppet_transform}. Shared attached
    renderers must pass these after computing the whole pose/reaction transform.
    """
    c=channels(state,t);o=dict(l=c['l'],r=c['r'],feet=c['feet'],head_tilt=c['head'])
    for hand,binding in (contacts or {}).items():
        if hand not in ('l','r'):raise ValueError('unknown contact hand')
        xy=grip(binding['prop_transform'],binding['anchor'],binding['puppet_transform'])
        o[hand]=(*xy,'grip')
    body,_=assemble_pose('standing',c['face'],o)
    body=re.sub(r'id="[^"]+"','',body)
    body=body.replace('data-part="head" transform="rotate(',f'data-part="head" transform="translate(0 {c["head_drop"]}) rotate(')
    def antenna(m):
        paths=re.findall(r'<path\b[^>]*?/>',m[1])
        if len(paths)!=6:raise ValueError('canonical antenna structure changed')
        a=c['antenna'];return '<g data-part="antennae">'+f'<g transform="rotate({a} 415 208)">'+''.join(paths[i] for i in (0,2,4))+'</g>'+f'<g transform="rotate({-a} 610 206)">'+''.join(paths[i] for i in (1,3,5))+'</g></g>'
    body=re.sub(r'<g\s+data-part="antennae"[^>]*>(.*?)</g>',antenna,body,flags=re.S)
    if state=='talking':body=body.replace('data-part="faceState"',f'transform="translate(0 {2*s if (s:=math.sin(t*30*.38)) else 0})" data-part="faceState"')
    return f'<g data-performance="{state}" transform="translate(512 904) rotate({c["angle"]}) scale({1/math.sqrt(c["sy"])} {math.sqrt(c["sy"])}) translate(-512 -904)">{body}</g>'
