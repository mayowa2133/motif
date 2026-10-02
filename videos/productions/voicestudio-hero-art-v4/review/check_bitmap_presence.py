"""Encoded-pixel checks for the concrete disappearing-bitmap export defect.

These fixed crops sample physical materials rather than UI lettering. This is
an asset-presence gate, not a craftsmanship or motion approval.
"""
from pathlib import Path
import argparse,subprocess,json
import numpy as np
parser=argparse.ArgumentParser();parser.add_argument('video',type=Path);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--opening-only',action='store_true');args=parser.parse_args()
regions=[
 ('opening-microphone',0,75,(176,340,40,68),'dark',300),
 ('opening-monitor-rim',0,75,(41,205,4,75),'cream',150),
 ('opening-stool-seat',0,75,(80,459,50,5),'blue',70),
 ('desktop-monitor-rim',207,247,(67,216,4,88),'cream',160),
 ('vintage-computer-rim',268,327,(97,207,5,67),'cream',170),
 ('basement-stool-seat',248,327,(45,445,43,5),'blue',55),
 ('script-monitor-rim',400,454,(47,220,3,95),'cream',135),
 ('washer-casing',248,327,(132,384,5,60),'cream',200),
 ('open-book-page',521,558,(31,447,21,15),'cream',200),
]
if args.opening_only: regions=regions[:3]
records=[]
for name,a,z,(x,y,w,h),material,minimum in regions:
 filters=f"select='between(n,{a},{z})',scale=360:640,crop={w}:{h}:{x}:{y}"
 raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(args.video),'-vf',filters,'-fps_mode','vfr','-f','rawvideo','-pix_fmt','rgb24','pipe:1'])
 frames=np.frombuffer(raw,dtype=np.uint8).reshape(-1,h,w,3).astype(np.int16);assert len(frames)==z-a+1
 if material=='dark':mask=frames.mean(axis=3)<110
 elif material=='cream':mask=(frames[:,:,:,0]>200)&(frames.sum(axis=3)>600)
 else:mask=frames[:,:,:,2]>frames[:,:,:,0]+25
 count=mask.sum(axis=(1,2));failed=[a+int(i) for i in np.flatnonzero(count<minimum)]
 records.append({'asset':name,'frames_inclusive':[a,z],'crop_native':[x,y,w,h],'material':material,'minimum_required_pixels':minimum,'minimum_observed':int(count.min()),'failed_frames':failed,'pass':not failed})
data={'video':str(args.video.resolve()),'method':'FFmpeg actual encoded frames, native material crops; all frames in the stated ranges','pass':all(r['pass'] for r in records),'regions':records,'scope':'physical bitmap presence only'}
args.output.write_text(json.dumps(data,indent=2)+'\n');print(json.dumps({'pass':data['pass'],'regions':[(r['asset'],r['minimum_observed'],len(r['failed_frames'])) for r in records]}))
raise SystemExit(0 if data['pass'] else 1)
