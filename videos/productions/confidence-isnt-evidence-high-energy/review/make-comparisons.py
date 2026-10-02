"""Trim semantic old/new beat excerpts at their original playback rates."""
from pathlib import Path
import subprocess,json
from PIL import Image,ImageDraw,ImageFont
p=Path(__file__).resolve().parents[1];old=p.parent/'confidence-isnt-evidence/renders/mobile.mp4';new=p/'renders/mobile.mp4'
font='/System/Library/Fonts/Supplemental/Arial.ttf'
header=Image.new('RGB',(720,64),'#203038');draw=ImageDraw.Draw(header);label_font=ImageFont.truetype(font,23)
draw.text((18,18),'OLD rejected · 1×',fill='white',font=label_font);draw.text((378,18),'NEW rebuilt · 1×',fill='white',font=label_font);header.save(p/'review/comparison-labels.png')
items=[('opening',0,0,2.8),('wording-reveal',6.34,5.13,3.1),('missing-evidence',10.33,9.76,2.94)]
for name,old_start,new_start,duration in items:
 filt=f'[0:v]setpts=PTS-STARTPTS,pad=360:704:0:64:color=0x203038[old];[1:v]setpts=PTS-STARTPTS,pad=360:704:0:64:color=0x203038[new];[old][new]hstack=inputs=2[base];[base][2:v]overlay=0:0:shortest=1[v]'
 cmd=['ffmpeg','-v','error','-y','-ss',str(old_start),'-i',str(old),'-ss',str(new_start),'-i',str(new),'-loop','1','-i',str(p/'review/comparison-labels.png'),'-filter_complex',filt,'-map','[v]','-map','1:a:0','-t',str(duration),'-r','30','-c:v','libx264','-crf','18','-c:a','aac','-b:a','192k','-movflags','+faststart',str(p/'renders'/f'compare-{name}.mp4')]
 subprocess.run(cmd,check=True)
(p/'review/comparison-ranges.json').write_text(json.dumps({'playback_rate':1,'time_stretch':False,'meaning':'semantic beat excerpts; different narration takes and natural timing','audio':'new cut only; old picture muted','clips':[{'file':f'renders/compare-{n}.mp4','old_start':o,'new_start':v,'duration':d} for n,o,v,d in items]},indent=2)+'\n')
