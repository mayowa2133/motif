"""Caption-free representative concepts; local qualification labels stay visible."""
import sys,json,base64
from pathlib import Path
import cairosvg
from PIL import Image,ImageDraw
sys.path[:0]=[str(Path(__file__).resolve().parent),str(Path(__file__).resolve().parents[4]/'scripts')]
from art import concept
from common import DEFS
from motif_quality import ROOT,write,read,sha

def build(project):
 p=Path(project).resolve();plan=read(p/'production-plan.json');dest=p/'review/concepts';dest.mkdir(parents=True,exist_ok=True)
 material=ROOT/'videos/productions/voicestudio-craft-v6/assets/materials/world-paper.webp'
 defs=DEFS.replace('assets/materials/world-paper.webp','data:image/webp;base64,'+base64.b64encode(material.read_bytes()).decode());previews=[];setups=plan['film_structure']['setups']
 for s in setups:
  id_=s['setup_id'];svg=dest/(id_+'.svg');png=dest/(id_+'.png');svg.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 1280"><defs>{defs}</defs>{concept(id_)}</svg>');cairosvg.svg2png(url=str(svg),write_to=str(png),output_width=360,output_height=640);previews.append({'setup_id':id_,'file':str(png),'sha256':sha(png),'source':str(svg)})
 sheets=[]
 for page,offset in enumerate(range(0,len(previews),6)):
  rows=previews[offset:offset+6];im=Image.new('RGB',(1080,1336),'#eadfc9');draw=ImageDraw.Draw(im)
  for i,item in enumerate(rows):
   x=i%3*360;y=i//3*668;draw.text((x+9,y+7),item['setup_id'],fill='#202c32');im.paste(Image.open(item['file']),(x,y+28))
  file=dest/f'contact-{page+1}.png';im.save(file);sheets.append({'file':str(file),'sha256':sha(file)})
 write(p/'concept-evidence.json',{'caption_free':True,'phase':'prebuild rough silhouettes, not final artwork or animation','setup_ids':[s['setup_id'] for s in setups],'previews':previews,'images':sheets,'inspection':'actual authored static concept images; no playback; local conditional qualifications are not narration captions'})
 return dest
if __name__=='__main__':print(build(Path(__file__).resolve().parents[1]))
