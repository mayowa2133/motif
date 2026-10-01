#!/usr/bin/env python3
"""Five original modular paper props, authored after the live concept choice.

Does not regenerate the canonical Bot or any accepted scene assets.
"""
import json
from pathlib import Path
from build_scene_01 import DEFS, card, paper_path, line, svg

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'assets/scenes/book-workshop'

def part(name, body):
    return f'<g id="{name}" transform="translate(256 256)">{body}</g>'

def kit():
    cover = paper_path('M-105 -133 Q-2 -138 108 -130 L107 133 Q2 139 -104 131 Z','#EBC46B')
    cover += '<g id="cover-flap">'+paper_path('M-97 -126 Q0 -131 105 -126 L104 126 Q0 132 -96 124 Z','#EBC46B')
    cover += line('M22 -28 L53 0 L22 28','#254D50',13)+'</g>'
    pages = ''.join(f'<g id="page-{i}">'+card(-87,-111+i*5,175,222,7,'#F4EBD8')+'</g>' for i in range(3))
    pages += line('M-4 -29 V29','#254D50',9)
    # The binding has one continuous silhouette; unrolling is a seekable path
    # morph between equal command counts, not a replacement finished-book icon.
    curled='M-105 -126 Q-135 -150 -137 -110 L-135 116 Q-120 151 -96 127 L-73 126 Q-103 104 -101 80 L-102 -94 Q-102 -116 -73 -126 Z'
    straight='M-105 -126 Q-108 -133 -110 -126 L-110 123 Q-108 131 -96 127 L-73 126 Q-79 104 -79 80 L-79 -94 Q-79 -116 -73 -126 Z'
    binding=f'<path id="binding-shape" d="{curled}" fill="#56BFB1" stroke="#318E85" stroke-width="3"/>'
    binding+=f'<path id="binding-grain" d="{curled}" fill="url(#paperSpeckle)" opacity=".65"/>'
    binding+=line('M-83 -28 L-101 0 L-83 28','#254D50',9)
    return {'project-folio-kit':(part('pages',pages)+part('cover',cover)+part('binding',binding),['dispatch','fold','press','unroll','assemble','deliver'],{'grip':[.5,.74],'spine':[.30,.5]}),
            'hinged-crease-jig':(part('jig',card(-132,-25,264,64,10,'#CBD7D0')+line('M0 -21 V32','#64869A',7)+'<g id="jig-leaf">'+card(-120,-39,116,39,6,'#F4EBD8')+'</g>'+line('M-116 47 H115','#64869A',6)),['feed','crease','release'],{'hinge':[.5,.45]}),
            'tabletop-page-press':(part('press',card(-130,25,260,45,10,'#64869A')+line('M-109 -113 V36 M109 -113 V36','#254D50',12)+'<g id="press-plate">'+card(-131,-113,262,35,9,'#CBD7D0')+'</g>'),['press','align','release'],{'contact':[.5,.35]}),
            'assembly-cradle':(part('cradle',paper_path('M-155 -17 L-128 -49 L-111 -43 L-109 -6 H107 L111 -43 L130 -49 L156 -15 L145 38 Q0 44 -144 36 Z','#DCCDB3')+line('M-109 -6 H107','#725343',6)),['receive','join','release'],{'join':[.5,.5]}),
            'receiving-hands':(part('hands','<g id="receiving-left">'+paper_path('M-232 168 L-232 72 Q-229 49 -207 51 L-165 94 L-163 41 Q-161 19 -141 23 Q-127 26 -123 47 L-110 108 Q-104 116 -79 112 L-12 86 Q11 81 17 100 Q22 119 5 130 L-66 169 L-81 223 L-209 223 Z','#F4EBD8')+'</g><g id="receiving-right" transform="scale(-1 1)">'+paper_path('M-232 168 L-232 72 Q-229 49 -207 51 L-165 94 L-163 41 Q-161 19 -141 23 Q-127 26 -123 47 L-110 108 Q-104 116 -79 112 L-12 86 Q11 81 17 100 Q22 119 5 130 L-66 169 L-81 223 L-209 223 Z','#F4EBD8')+'</g>'),['receive','hold','withdraw'],{'contact':[.5,.69]})}

CURL='M-105 -126 Q-135 -150 -137 -110 L-135 116 Q-120 151 -96 127 L-73 126 Q-103 104 -101 80 L-102 -94 Q-102 -116 -73 -126 Z'
STRAIGHT='M-105 -126 Q-108 -133 -110 -126 L-110 123 Q-108 131 -96 127 L-73 126 Q-79 104 -79 80 L-79 -94 Q-79 -116 -73 -126 Z'

def build():
    import cairosvg
    from PIL import Image, ImageDraw
    OUT.mkdir(parents=True,exist_ok=True)
    tiles=[]
    for name,(body,actions,anchors) in kit().items():
        target=OUT/(name+'.svg'); target.write_text(svg(512,512,body,name.replace('-',' ')))
        preview=OUT/(name+'.png'); cairosvg.svg2png(url=str(target),write_to=str(preview))
        meta={'id':name,'name':name.replace('-',' ').title(),'category':'prop','subcategory':'paper-workshop','concepts':['parallel work','assembly','delivery'],'keywords':[name,'paper','workshop'],'style':'motif-default-v1','orientation':'front','dimensions':{'width':512,'height':512,'unit':'px'},'artBox':{'x':0,'y':0,'width':512,'height':512},'anchors':{k:{'x':v[0],'y':v[1]} for k,v in anchors.items()},'compatibleCharacters':['motif-bot'],'supportedActions':actions,'sourceType':'vector','source':{'file':str(target.relative_to(ROOT)),'reference':'Live Little Book Workshop concept; agent-authored geometry using existing paper material helpers'},'version':1,'status':'review','preview':str(preview.relative_to(ROOT)),'license':'project-original'}
        (OUT/(name+'.json')).write_text(json.dumps(meta,indent=2)+'\n')
        tile=Image.new('RGB',(320,370),'#F4EBD8'); im=Image.open(preview).convert('RGBA'); im.thumbnail((290,290));tile.paste(im,((320-im.width)//2,10),im)
        ImageDraw.Draw(tile).text((12,325),name,fill='#202C32');tiles.append(tile)
    sheet=Image.new('RGB',(960,740),'#DCCDB3')
    for i,tile in enumerate(tiles):sheet.paste(tile,((i%3)*320,(i//3)*370))
    sheet.save(OUT/'contact-sheet.jpg')

if __name__=='__main__':build()
