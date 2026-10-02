"""One compact native comparison sheet and three normal-speed motion excerpts."""
from pathlib import Path
import json,subprocess
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parents[1];OLD=P.parent/'voicestudio-consistency-v5';TMP=Path('/tmp/motif-v6-review')
NAMES=['Repository / weighted press','Payment / burden','Basement / startle','Menu / heavy landing','Transcript / long strip','Cancellation / release','Keyboard / rebound']
SHOTS=[2,3,5,9,12,16,19];FRAMES=json.loads((TMP/'pause-frames.json').read_text())
TIMES=[3.6,6.833,10.5,15.8,21.6,27.533,32.335]
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',16)
a=sorted((TMP/'v5-final-pauses').glob('frame-*.png'));b=sorted((TMP/'v6-final-pauses').glob('frame-*.png'));assert len(a)==len(b)==7
# Each cell remains an exact 360×640 capture: two pairs per row.
board=Image.new('RGB',(1472,2736),'#EEE5D3');draw=ImageDraw.Draw(board)
for i,(before,after) in enumerate(zip(a,b)):
 x=8+(i%2)*736;y=8+(i//2)*682
 draw.text((x,y),f'{SHOTS[i]:02d} {NAMES[i]} · {TIMES[i]:.3f}s',font=font,fill='#211923')
 draw.text((x,y+21),'v5',font=font,fill='#211923');draw.text((x+360,y+21),'v6',font=font,fill='#211923')
 left=Image.open(before).convert('RGB');right=Image.open(after).convert('RGB');assert left.size==right.size==(360,640)
 board.paste(left,(x,y+42));board.paste(right,(x+360,y+42))
# Empty final pair carries a short legend, not more film frames.
x=744;y=2054
for j,line in enumerate(['Seven selected moments only.','v5 and v6 at the same timeline time.','Each picture is native 360×640.','Caption host omitted; headline kept.','Motion clips play at 30 fps / normal speed.','REVIEW_REQUIRED — human approval pending.']):draw.text((x+16,y+42+j*30),line,font=font,fill='#211923')
board.save(P/'renders/selected-before-after.png')
comparisons=P/'renders/comparisons';comparisons.mkdir(exist_ok=True)
# Matched trims at 1×. Billing contains two explicit original-speed cuts.
clips=[('billing-and-relief',[(180,207),(806,839)]),('basement-completion',[(303,328)]),('keyboard-contact-rebound',[(958,986)])]
label=Image.new('RGB',(720,30),'#EEE5D3');d=ImageDraw.Draw(label);d.text((10,6),'v5 / 1× / native',font=font,fill='#211923');d.text((370,6),'v6 / same frames',font=font,fill='#211923');label.save(comparisons/'labels.png')
records=[]
for name,ranges in clips:
 filters=[];order=[]
 for i,(start,end) in enumerate(ranges):
  for stream in (0,1):filters.append(f'[{stream}:v]trim=start_frame={start}:end_frame={end},setpts=PTS-STARTPTS[v{stream}{i}]')
  filters.append(f'[v0{i}][v1{i}]hstack=inputs=2[p{i}]');order.append(f'[p{i}]')
 if len(ranges)>1:filters.append(''.join(order)+f'concat=n={len(ranges)}:v=1:a=0[picture]')
 else:filters.append('[p0]null[picture]')
 filters+=['[picture]pad=720:670:0:30:color=0xEEE5D3[padded]','[padded][2:v]overlay=0:0:shortest=1[out]']
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(OLD/'renders/mobile.mp4'),'-i',str(P/'renders/mobile.mp4'),'-loop','1','-i',str(comparisons/'labels.png'),'-filter_complex',';'.join(filters),'-map','[out]','-an','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-r','30','-frames:v',str(sum(z-a for a,z in ranges)),'-movflags','+faststart',str(comparisons/f'{name}.mp4')],check=True)
 records.append({'file':f'renders/comparisons/{name}.mp4','source_frames_half_open':ranges,'frames':sum(z-a for a,z in ranges),'fps':30,'playback_rate':1,'audio':'muted for picture comparison'})
(P/'review/selected-moments.json').write_text(json.dumps({'status':'REVIEW_REQUIRED','shots':SHOTS,'same_time_native_seconds':TIMES,'requested_frames':FRAMES,'sheet':'renders/selected-before-after.png','comparisons':records,'correction_passes':1,'caption_free_sheet':True},indent=2)+'\n')
print('Packaged seven native pairs and three normal-speed clips.')
