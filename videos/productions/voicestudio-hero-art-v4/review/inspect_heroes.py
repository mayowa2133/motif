from pathlib import Path
import subprocess,json
from PIL import Image,ImageDraw,ImageFont
p=Path(__file__).resolve().parents[1];out=p/'review/hero-pause-frames';out.mkdir(exist_ok=True)
frames=[('opening',23),('basement',316),('menu',505),('audiobook',555),('ending',985)]
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',16)
board=Image.new('RGB',(1840,680),'#EEE5D3');d=ImageDraw.Draw(board)
for i,(name,f) in enumerate(frames):
 file=out/f'{name}-f{f}.png';subprocess.run(['ffmpeg','-v','error','-y','-i',str(p/'review/picture-only-raw.mp4'),'-vf',f"select='eq(n,{f})'",'-frames:v','1',str(file)],check=True)
 im=Image.open(file);assert im.size==(360,640);board.paste(im,(i*368+4,32));d.text((i*368+4,8),f'{name} · f{f} · no captions',font=font,fill='#211923')
board.save(p/'review/hero-paused-native.png')
(p/'review/hero-pause-index.json').write_text(json.dumps(dict(frames),indent=2)+'\n')
