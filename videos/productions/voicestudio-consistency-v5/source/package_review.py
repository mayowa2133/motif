"""Caption-free native pause sheets from the existing HyperFrames timeline."""
from pathlib import Path
import json,shutil
from PIL import Image,ImageDraw,ImageFont,ImageChops
P=Path(__file__).resolve().parents[1];tmp=Path('/tmp/motif-v5-review');out=P/'renders';pairs=out/'comparisons';pairs.mkdir(exist_ok=True);pauses=out/'caption-free';pauses.mkdir(exist_ok=True)
CHANGED=[2,3,6,8,11,12,13,14,15,16,18];HERO=[1,5,9,10,19]
NAMES=['Recording','Repository stars','Pricing','Desktop app','Basement','App reveal','Short recording','Text to voice','Model menu','Audiobook','Dictation','Transcription','Dubbing process','Bilingual audio','Language count','Cancellation','Offline','Privacy','VOICE ending']
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',16)
old=sorted((tmp/'v4-pauses').glob('frame-*.png'));new=sorted((tmp/'v5-pauses').glob('frame-*.png'));assert len(old)==len(new)==19
frames=json.loads((tmp/'pause-frames.json').read_text());identical={}
board=Image.new('RGB',(1856,2736),'#EEE5D3');draw=ImageDraw.Draw(board)
for n,(before,after) in enumerate(zip(old,new),1):
 image=Image.open(after).convert('RGB');previous=Image.open(before).convert('RGB');assert image.size==previous.size==(360,640)
 if n not in CHANGED:
  identical[str(n)]=ImageChops.difference(image,previous).getbbox() is None
  assert identical[str(n)],f'unchanged shot {n} has changed pause pixels'
 shutil.copy2(after,pauses/f'{n:02d}-{NAMES[n-1].lower().replace(" ","-")}.png')
 col=(n-1)%5;row=(n-1)//5;x=8+col*370;y=8+row*682
 status='HERO · unchanged' if n in HERO else 'revised' if n in CHANGED else 'kept'
 draw.text((x,y),f'{n:02d} {NAMES[n-1]} · {status}',font=font,fill='#211923');board.paste(image,(x,y+29))
 if n in CHANGED:
  pair=Image.new('RGB',(736,678),'#EEE5D3');d=ImageDraw.Draw(pair)
  pair.paste(previous,(8,30));pair.paste(image,(368,30));d.text((8,8),'v4 · before · 360×640',font=font,fill='#211923');d.text((368,8),'v5 · after · 360×640',font=font,fill='#211923')
  pair.save(pairs/f'{n:02d}-{NAMES[n-1].lower().replace(" ","-")}-before-after.png')
board.save(out/'all-scenes-caption-free.png')
index={'native_size':[360,640],'caption_free':True,'source':'Pinned HyperFrames snapshots of native timelines, same times; caption host omitted, headline preserved','frames':frames,'heroes':HERO,'changed':CHANGED,'identical_unchanged_pause_pixels':identical}
(out/'pause-index.json').write_text(json.dumps(index,indent=2)+'\n');print(out/'all-scenes-caption-free.png')
