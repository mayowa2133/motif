"""Reuse Motif's measured combined-mix finishing; preserve encoded picture."""
from pathlib import Path
import json,sys,shutil
P=Path(__file__).resolve().parent
ROOT=P.parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from motif_produce import loudness,probe,video_hash,command,TARGET_I,PEAK_CEILING
first=P/'renders/first.mp4'
before=loudness(first)
gain=min(TARGET_I-before['integrated_lufs'],PEAK_CEILING-.1-before['true_peak_dbtp'])
final=P/'renders/final.mp4'
duration=164/30
command(['ffmpeg','-hide_banner','-y','-i',str(first),'-map','0:v:0','-map','0:a:0','-c:v','copy','-af',f'volume={gain:.3f}dB','-c:a','aac','-b:a','192k','-t',str(duration),'-movflags','+faststart',str(final)],ROOT,log=P/'audio-finish.log')
after=loudness(final)
method='combined-mix linear gain'
if abs(after['integrated_lufs']-TARGET_I)>.8 or after['true_peak_dbtp']>PEAK_CEILING:
    candidate=P/'renders/audio-loudnorm-candidate.mp4'
    command(['ffmpeg','-hide_banner','-y','-i',str(first),'-map','0:v:0','-map','0:a:0','-c:v','copy','-af',f'loudnorm=I={TARGET_I}:TP={PEAK_CEILING-.3}:LRA=11,atrim=duration={duration}','-c:a','aac','-b:a','192k','-t',str(duration),'-movflags','+faststart',str(candidate)],ROOT,log=P/'audio-loudnorm.log')
    shutil.copy2(candidate,final);after=loudness(final);method='combined-mix loudnorm'
assert abs(after['integrated_lufs']-TARGET_I)<=.8,after
assert after['true_peak_dbtp']<=PEAK_CEILING,after
assert video_hash(first)==video_hash(final)
# The mobile picture was captured natively at 360 × 640; mux the same finished AAC, without resizing video.
mobile=P/'renders/mobile.mp4'
command(['ffmpeg','-hide_banner','-y','-i',str(P/'renders/mobile-first.mp4'),'-i',str(final),'-map','0:v:0','-map','1:a:0','-c','copy','-t',str(duration),'-movflags','+faststart',str(mobile)],ROOT,log=P/'mobile-mux.log')
result={'first_audio':before,'final_audio':after,'finishing_method':method,'initial_gain_db':gain,'encoded_picture_preserved':True,'native_mobile_picture_preserved':video_hash(mobile)==video_hash(P/'renders/mobile-first.mp4'),'source_frame_interval':[436,600],'fps':30,'expected_frame_count':164,'source_audio_used':False,'subjective_listening':'unassessed','media':{}}
for name in ('final','mobile'):
    j=probe(P/'renders'/f'{name}.mp4');v=next(s for s in j['streams'] if s['codec_type']=='video')
    assert int(v['nb_frames'])==164,(name,v)
    rate=command(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=r_frame_rate','-of','default=noprint_wrappers=1:nokey=1',str(P/'renders'/f'{name}.mp4')],ROOT).strip()
    assert rate=='30/1',(name,rate)
    result['media'][name]={'width':v['width'],'height':v['height'],'frames':int(v['nb_frames']),'picture_duration':float(v['duration']),'container_duration':float(j['format']['duration'])}
(P/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
