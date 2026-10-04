"""Native static contact proofs only; preserve passing setups byte-for-byte."""
import sys,json,base64,shutil,textwrap
from pathlib import Path
import cairosvg
from PIL import Image,ImageDraw
sys.path[:0]=[str(Path(__file__).resolve().parent),str(Path(__file__).resolve().parents[4]/'scripts')]
from common import DEFS
from motif_reference import ROOT,read,write,sha

def sheet(rows,path,columns=3):
 im=Image.new('RGB',(360*columns,668*((len(rows)+columns-1)//columns)),'#eadfc9');draw=ImageDraw.Draw(im)
 for i,(label,file) in enumerate(rows):
  x=i%columns*360;y=i//columns*668
  for n,line in enumerate(textwrap.wrap(label,width=48)[:2]):draw.text((x+9,y+3+n*11),line,fill='#202c32')
  im.paste(Image.open(file),(x,y+28))
 im.save(path);return {'file':str(path.resolve()),'sha256':sha(path)}

def build():
 from connected_art import frame
 p=Path(__file__).resolve().parents[1];dest=p/'review/concepts-v2';dest.mkdir(parents=True,exist_ok=False);plan=read(p/'production-plan.json');scope=read(p/'concept-scope.json');old=Path(scope['original_project']);contract=read(p/'concept-contract.json');old_ev=read(old/'concept-evidence.json')
 material=ROOT/'videos/productions/voicestudio-craft-v6/assets/materials/world-paper.webp';defs=DEFS.replace('assets/materials/world-paper.webp','data:image/webp;base64,'+base64.b64encode(material.read_bytes()).decode())
 def render(name,body):
  svg=dest/(name+'.svg');png=dest/(name+'.png');svg.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 1280"><defs>{defs}</defs>{body}</svg>');cairosvg.svg2png(url=str(svg),write_to=str(png),output_width=360,output_height=640);return {'file':str(png.resolve()),'sha256':sha(png),'source':str(svg.resolve()),'diagnostic':False}
 previews=[];proofs=[];images=[];review_rows=[]
 for s in plan['film_structure']['setups']:
  sid=s['setup_id']
  if sid in scope['preserved_setup_ids']:
   item=next(x for x in old_ev['previews'] if x['setup_id']==sid);file=dest/(sid+'.png');shutil.copy2(item['file'],file);previews.append({'setup_id':sid,'file':str(file.resolve()),'sha256':sha(file),'inherited':True})
  else:
   bid=s['beat_ids'][0];b=next(x for x in contract['beats'] if x['beat_id']==bid)
   preview=render(sid,frame(bid,'contact',b['interactions'][0]['id'] if b['interactions'] else None));previews.append({'setup_id':sid,**preview});review_rows.append((sid,preview['file']))
 for b in contract['beats']:
  sid=next(s['setup_id'] for s in plan['film_structure']['setups'] if b['beat_id'] in s['beat_ids'])
  for action in b['interactions']:
   states={name:render(b['beat_id']+'-'+action['id']+'-'+name,frame(b['beat_id'],name,action['id'])) for name in ['before','contact','after']}
   proofs.append({'setup_id':sid,'beat_id':b['beat_id'],'interaction_id':action['id'],'frames':states})
   images.append(sheet([(b['beat_id']+' '+action['id']+' '+name,im['file']) for name,im in states.items()],dest/(b['beat_id']+'-'+action['id']+'-proof.png')))
 boundaries=[]
 for boundary in ['source-to-outline','outline-to-draft']:
  states={state:render('b04-'+boundary+'-'+state,frame('b04',boundary+'-'+state,None)) for state in ['before','contact','after']}
  boundaries.append({'beat_id':'b04','boundary':boundary,'contact':'same sustained strip/lip contact, not a new impact','frames':states})
  images.append(sheet([(boundary+' '+state,im['file']) for state,im in states.items()],dest/(boundary+'.png')))
 images.insert(0,sheet(review_rows,dest/'revised-setups.png'))
 sheet([(x['setup_id']+(' / preserved' if x.get('inherited') else ' / revised'),x['file']) for x in previews],dest/'full-context.png')
 # Additional state comparison is still evidence, never a moving preview.
 continuation=[]
 for name in ['inactive-source','inactive-outline','inactive-draft']:
  im=render('b04-'+name,frame('b04',name,None));continuation.append((name,im['file']))
 images.append(sheet(continuation,dest/'work-with-user-inactive.png'))
 sources={str(f.resolve()):sha(f) for f in (p/'source').glob('*.py')}
 for f in [p/'concept-contract.json',p/'concept-scope.json',p/'reference-calibration/beat-record.json']:sources[str(f.resolve())]=sha(f)
 ev={'caption_free':True,'phase':'static concept/contact proof only; no motion or final art','setup_ids':[s['setup_id'] for s in plan['film_structure']['setups']],'review_setup_ids':scope['review_setup_ids'],'previews':previews,'images':images,'contact_proofs':proofs,'state_boundaries':boundaries,'source_hashes':sources,'preserved_scope':scope,'inspection':'BEFORE/CONTACT/AFTER clean native images; sheet labels are outside composition; no playback/listening'}
 write(p/'concept-evidence.json',ev);return dest
if __name__=='__main__':print(build())
