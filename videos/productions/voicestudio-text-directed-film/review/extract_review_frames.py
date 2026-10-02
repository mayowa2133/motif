"""Decode actual encoded picture frames; no composition screenshot substitution."""
from pathlib import Path
import argparse,json,subprocess
from PIL import Image,ImageDraw,ImageFont
parser=argparse.ArgumentParser();parser.add_argument('video',type=Path);parser.add_argument('--name',required=True);args=parser.parse_args()
p=Path(__file__).resolve().parents[1];plan=json.loads((p/'production-plan.json').read_text())
frames=[52,129,195,238,316,343,395,449,504,555,596,647,694,730,779,836,876,920,983]
folder=p/'review'/(args.name+'-frames');folder.mkdir(exist_ok=True)
select='+'.join(f'eq(n,{f})' for f in frames)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(args.video),'-vf',f"select='{select}',scale=360:640",'-fps_mode','vfr',str(folder/'shot-%02d.png')],check=True)
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',15)
for start in [0,6,12]:
 count=min(6,19-start);board=Image.new('RGB',(744,((count+1)//2)*674+12),'#ECE6D9');draw=ImageDraw.Draw(board)
 for j in range(count):
  im=Image.open(folder/f'shot-{start+j+1:02d}.png').convert('RGB');x=12+(j%2)*366;y=12+(j//2)*674;board.paste(im,(x,y));draw.text((x,y+642),f'{start+j+1:02d} · encoded frame {frames[start+j]}',font=font,fill='#211923')
 board.save(p/'review'/f'{args.name}-native-board-{start//6+1}.jpg',quality=93)
# Last setup gets a separate true-native proof.
Image.open(folder/'shot-19.png').save(p/'review'/f'{args.name}-final-native.png')
if args.name=='delivery':
 cols=5;tw,th=180,320;sheet=Image.new('RGB',(cols*196+16,4*348+58),'#EEE5D3');d=ImageDraw.Draw(sheet);d.text((16,12),'VoiceStudio · 19 setups · encoded delivery · REVIEW_REQUIRED',font=font,fill='#211923')
 for i in range(19):
  x=16+(i%cols)*196;y=43+(i//cols)*348;im=Image.open(folder/f'shot-{i+1:02d}.png').convert('RGB').resize((tw,th),Image.Resampling.LANCZOS);sheet.paste(im,(x,y));d.text((x,y+324),f'{i+1:02d} · frame {frames[i]}',font=font,fill='#211923')
 sheet.save(p/'renders/19-shot-contact-sheet.jpg',quality=93)
(p/'review'/(args.name+'-decoded-frame-index.json')).write_text(json.dumps({'source_video':str(args.video.resolve()),'method':'FFmpeg decode and frame-number selection; images at360x640','frames':[{'shot':s['id'],'encoded_frame':f,'file':str((folder/f'shot-{i+1:02d}.png').relative_to(p))} for i,(s,f) in enumerate(zip(plan['shots'],frames))]},indent=2)+'\n')
print(folder)
