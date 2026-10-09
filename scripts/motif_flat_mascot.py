"""Flat binding of explicitly approved reusable front geometry; no source shots.

Retains the fixed shell/four feet/eyes/tab geometry. Connectors and target-driven
hand motion are authored fixture controls, not recovered original performance.
No rim, texture, perspective, cast shadow, side/back pose or artwork promotion.
"""
from motif_evidence import read
from motif_media_contracts import locked_resource
from pathlib import Path

CONTRACT_SHA='e530fab90984ec06e109afe937ab478b935c62a5698ac518e93bab0ba91c87d9'
COLOR='#e47d53'


def validate_binding(scene):
    record=scene['mascot_contract']
    if (not isinstance(record,dict) or not isinstance(record.get('path'),str) or not record['path'] or
            Path(record['path']).is_absolute() or '..' in Path(record['path']).parts):
        raise ValueError('explicit nonempty relative mascot resource record required')
    if record.get('sha256')!=CONTRACT_SHA:raise ValueError('unrecognized approved front geometry version')
    for node in scene['nodes']:
        if node['role'] not in ('worker','requester'):continue
        w,h=node['size']
        if abs(h-w*251/240)>1e-6 or node['color'].lower()!=COLOR:
            raise ValueError('flat mascot requires approved aspect, fixed orange and four-foot shell')


def bounds(node,grip):
    x,y=node['position'];w,h=node['size'];scale=w/240
    result=[(x,y,x+w,y+h),(x-50*scale,y+85*scale,x+2*scale,y+133*scale)]
    if grip is None:result.append((x+238*scale,y+85*scale,x+290*scale,y+133*scale))
    else:
        a,b=grip;result.append((a-26*scale,b-24*scale,a+26*scale,b+24*scale))
        # Flat authored connector is painted at 12 local-unit stroke width.
        sx,sy=x+w,y+109*scale
        result.append((min(sx,a)-6*scale,min(sy,b)-6*scale,max(sx,a)+6*scale,max(sy,b)+6*scale))
    return result


def actor(root,record,node,grip=None):
    contract=read(locked_resource(root,record));x,y=node['position'];w,h=node['size'];scale=w/240
    identifier=node['id'];body=[]
    points=' '.join(f'{x+a*scale},{y+b*scale}' for a,b in contract['shell_polygon'])
    body.append(f'<polygon id="{identifier}-shell" points="{points}" fill="{COLOR}"/>')
    for n,(a,b,c,d) in enumerate(contract['eye_rectangles']):
        body.append(f'<rect id="{identifier}-eye-{n}" x="{x+a*scale}" y="{y+b*scale}" width="{c*scale}" height="{d*scale}" fill="#171513"/>')
    for side in ('left','right'):
        a,b,c,d=contract['hand_modes']['tab'][side+'_rect']
        hx,hy=x+a*scale,y+b*scale
        if side=='right' and grip is not None:
            hx,hy=grip[0]-c*scale/2,grip[1]-d*scale/2
            body.append(f'<path id="{identifier}-connector" d="M{x+w} {y+109*scale}L{grip[0]} {grip[1]}" stroke="{COLOR}" stroke-width="{12*scale}"/>')
        hand_id=identifier+'-hand' if side=='right' else identifier+'-hand-left'
        body.append(f'<rect id="{hand_id}" x="{hx}" y="{hy}" width="{c*scale}" height="{d*scale}" fill="{COLOR}"/>')
    return ''.join(body)
