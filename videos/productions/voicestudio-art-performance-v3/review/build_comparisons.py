"""Matching encoded frames and 1x clips. No source-frame substitution."""
from pathlib import Path
import subprocess,json
from PIL import Image,ImageDraw,ImageFont
p=Path(__file__).resolve().parents[1]
old=p.parent/'voicestudio-text-directed-film-fidelity-v2/renders/mobile.mp4'
new=p/'renders/mobile.mp4'
out=p/'renders/comparisons';out.mkdir(exist_ok=True)
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',16)
def run(args):subprocess.run(['ffmpeg','-v','error','-y',*args],check=True)
stills=[('opening',45),('basement',316),('menu',505),('ending',983)]
for name,frame in stills:
 board=Image.new('RGB',(736,678),'#EEE5D3');d=ImageDraw.Draw(board)
 for i,(label,video) in enumerate([('v2',old),('v3',new)]):
  file=out/f'{name}-{label}-f{frame}.png'
  run(['-i',str(video),'-vf',f"select='eq(n,{frame})'",'-frames:v','1',str(file)])
  board.paste(Image.open(file),(8+368*i,30));d.text((8+368*i,8),f'{label} · frame {frame} · 360×640',font=font,fill='#211923')
 board.save(out/f'{name}-before-after.png')
header=Image.new('RGB',(720,32),'#EEE5D3');d=ImageDraw.Draw(header)
d.text((8,7),'v2 · previous artwork',font=font,fill='#211923');d.text((368,7),'v3 · art and performance',font=font,fill='#211923');header.save(out/'comparison-labels.png')
clips=[('recording',0,76),('menu-contacts',455,507),('keyboard-contacts',937,986)]
for name,start,end in clips:
 # setpts only resets each source's origin. Source cadence is 30fps / 1x.
 filters=f'[0:v]trim=start_frame={start}:end_frame={end},setpts=PTS-STARTPTS[l];[1:v]trim=start_frame={start}:end_frame={end},setpts=PTS-STARTPTS[r];[l][r]hstack,pad=iw:ih+32:0:32:color=0xEEE5D3[b];[b][2:v]overlay=0:0[v]'
 run(['-i',str(old),'-i',str(new),'-i',str(out/'comparison-labels.png'),'-filter_complex',filters,'-map','[v]','-an','-frames:v',str(end-start),'-c:v','libx264','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart',str(out/f'{name}-before-after.mp4')])
(out/'index.json').write_text(json.dumps({'sources':{'v2':str(old),'v3':str(new)},'native_source_size':[360,640],'stills':dict(stills),'clips':[{'name':name,'start_frame':a,'end_frame_exclusive':z,'fps':30,'speed':1,'audio':'muted visual comparison'} for name,a,z in clips]},indent=2)+'\n')
print(out)
