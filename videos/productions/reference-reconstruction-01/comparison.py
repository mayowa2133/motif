"""Create synchronized review artifacts. Run from the Motif repository root."""
from pathlib import Path
import json, subprocess, io
from PIL import Image, ImageDraw, ImageFont
P=Path(__file__).resolve().parent
ROOT=P.parents[2]
source=ROOT/'references/reconstruction/study/selected-mobile.mp4'
mobile=P/'renders/mobile.mp4'
comparison=P/'renders/comparison.mp4'
def run(args):
    return subprocess.check_output(args,stderr=subprocess.PIPE)
run(['ffmpeg','-hide_banner','-y','-i',str(source),'-i',str(mobile),'-loop','1','-i',str(P/'review/comparison-labels.png'),'-filter_complex','[0:v][1:v]hstack=inputs=2,pad=720:680:0:40:color=0x1b2528[v];[v][2:v]overlay=0:0[out]','-map','[out]','-map','1:a:0','-frames:v','164','-c:v','libx264','-crf','18','-c:a','copy','-movflags','+faststart',str(comparison)])
frames=[9,24,76,105,128,156]
sheet=Image.new('RGB',(760,1104),'#1b2528')
draw=ImageDraw.Draw(sheet)
font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',13)
for i,n in enumerate(frames):
    x=(i%2)*380;y=(i//2)*368
    draw.text((x+8,y+6),f'Reference | Motif   local {n/30:.2f}s / source {(436+n)/30:.2f}s',fill='white',font=font)
    for j,path in enumerate((source,mobile)):
        data=run(['ffmpeg','-v','error','-i',str(path),'-vf',f'select=eq(n\\,{n})','-frames:v','1','-f','image2pipe','-vcodec','png','-'])
        im=Image.open(io.BytesIO(data)).convert('RGB')
        im.save(P/'review'/f'keyframe-{n:03d}-{("reference","motif")[j]}.png')
        sheet.paste(im.resize((180,320),Image.Resampling.LANCZOS),(x+8+j*184,y+30))
sheet.save(P/'review/keyframe-comparison.jpg',quality=93)
j=json.loads(run(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_type,width,height,nb_frames,r_frame_rate,duration','-of','json',str(comparison)]))
v=next(s for s in j['streams'] if s['codec_type']=='video')
assert (v['width'],v['height'],int(v['nb_frames']),v['r_frame_rate'])==(720,680,164,'30/1'),v
assert abs(float(v['duration'])-164/30)<.001
result={'normalSpeed':True,'retiming':False,'sourceFrames':[436,600],'referenceSideAudio':False,'soundtrack':'reconstruction only','keyframes':frames,'comparison':j}
(P/'comparison-verification.json').write_text(json.dumps(result,indent=2)+'\n')
(P/'review/final-moving-review.html').write_text('<!doctype html><html><head><meta charset="utf-8"></head><body style="margin:8px;background:#182127;color:white;font-family:sans-serif"><h2>Reference / Motif · final · normal speed</h2><video controls autoplay loop muted style="width:100%;max-width:720px" src="../renders/comparison.mp4"></video><p>Left: supplied reference. Right: Motif. Both 1×, aligned source frames 436–599. Unmute for Motif audio only.</p></body></html>')
print(json.dumps(result,indent=2))
