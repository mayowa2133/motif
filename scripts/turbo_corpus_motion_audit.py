"""Private full-rate temporal audit; derived numerical metadata only is portable.

No reference frame/pixel is written to repository output. Visual judgments still
require original footage or private native strips; motion measures aren't gates.
"""
import argparse,hashlib,json,subprocess
from pathlib import Path
import numpy as np

def audit(path):
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))
 v=next(x for x in probe['streams'] if x['codec_type']=='video')
 p=subprocess.Popen(['ffmpeg','-v','error','-threads','1','-i',str(path),'-vf','scale=90:160','-an','-threads','1','-f','rawvideo','-pix_fmt','gray','-'],stdout=subprocess.PIPE)
 changes=[];previous=None;count=0
 while True:
  raw=p.stdout.read(90*160)
  if len(raw)!=90*160:break
  frame=np.frombuffer(raw,dtype=np.uint8).astype(float)
  if previous is not None:changes.append(float(np.mean(np.abs(frame-previous))))
  previous=frame;count+=1
 p.stdout.close()
 if p.wait():raise ValueError('decode failed')
 return {'id':path.stem.split('igexport-')[-1].split('(')[0],'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'picture_frames_decoded':count,'fps':v['avg_frame_rate'],'width':v['width'],'height':v['height'],'picture_duration':float(v['duration']),'container_duration':float(probe['format']['duration']),'temporal_mean_absolute_luma_difference':{'median':float(np.median(changes)),'p90':float(np.percentile(changes,90)),'maximum':max(changes)},'limits':'All frames decoded. Difference includes captions/cuts/texture and is not quality, semantic energy or playback/listening approval.'}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--sources',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();files=sorted(a.sources.glob('*.mp4'))
 if len(files)!=7:raise ValueError('exactly seven authorized files required')
 result={'private_sources':True,'pixels_in_output':False,'videos':[audit(x) for x in files]};a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n');print('Seven full-rate sources decoded; numerical audit saved.')
