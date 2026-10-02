"""Prepare shot-length scratch cues; reuse approved audio at unity gain.

Only new narration is fitted/normalized. No process touches baseline movies.
Master uses the same prepared stems as the framework-owned Studio audio clips.
"""
from pathlib import Path
import hashlib, json, subprocess, sys
import numpy as np
P=Path(__file__).resolve().parent
ROOT=P.parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from motif_produce import loudness
D=1262/30
RATE=48000
def run(args):return subprocess.check_output(args,stderr=subprocess.PIPE)
def decode(path):
    return np.frombuffer(run(['ffmpeg','-v','error','-i',str(path),'-f','f32le','-ar',str(RATE),'-ac','2','-']),dtype='<f4').reshape(-1,2)
def duration(path):
    return float(run(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(path)]))
plan=json.loads((P/'voice-plan.json').read_text())
master=np.zeros((round(D*RATE),2),dtype=np.float32)
tracks=[];fits=[]
for seg in plan['segments']:
    name=seg['id'];a,z=seg['frames'];slot=(z-a)/30
    source=P/'assets/voice'/f'{name}.wav';out=P/'assets/voice'/f'{name}-fitted.wav'
    source_d=duration(source)
    rate=max(1,source_d/(slot-.06))
    run(['ffmpeg','-hide_banner','-y','-i',str(source),'-af',f'atempo={rate:.8f},loudnorm=I=-16:TP=-1.8:LRA=11,apad,atrim=duration={slot}', '-ar',str(RATE),'-ac','2','-c:a','pcm_f32le',str(out)])
    data=decode(out);start=round(a/30*RATE);length=min(len(data),round(slot*RATE))
    master[start:start+length]+=data[:length]
    fits.append({'id':name,'sourceDuration':source_d,'slotDuration':slot,'atempo':rate,'status':'scratch cue; not final performance'})
    tracks.append({'src':str(out.relative_to(P)),'start':a/30,'duration':length/RATE,'volume':1,'kind':'narration','id':name})
baseline=P/'assets/baseline/final.mp4'
data=decode(baseline)[:round(164/30*RATE)]
start=round(436/30*RATE);master[start:start+len(data)]=data
assert np.array_equal(master[start:start+len(data)],data)
tracks.append({'src':'assets/baseline/final.mp4','start':436/30,'duration':164/30,'volume':1,'kind':'approved soundtrack','id':'locked-soundtrack'})
# Sparse existing cleared effects, only on actual physical consequences.
for name,frame,gain in [('click-soft',221,.10),('whoosh-short',747,.07),('pop',960,.06),('click-soft',1010,.10),('pop',1138,.08),('pop',1155,.08),('pop',1175,.08)]:
    source=P/'assets/sfx'/f'{name}.mp3';data=decode(source);start=round(frame/30*RATE)
    length=min(len(data),len(master)-start);master[start:start+length]+=data[:length]*gain
    tracks.append({'src':str(source.relative_to(P)),'start':frame/30,'duration':length/RATE,'volume':gain,'kind':'effect','id':f'{name}-{frame}'})
out=P/'assets/rough-mix.wav'
proc=subprocess.run(['ffmpeg','-v','error','-y','-f','f32le','-ar',str(RATE),'-ac','2','-i','-','-c:a','pcm_f32le',str(out)],input=master.astype('<f4').tobytes(),capture_output=True)
assert proc.returncode==0,proc.stderr
report={'tracks':tracks,'fitting':fits,'approvedIntervalDecodedSamplesPreservedAtUnityBeforeAAC':True,'sourceAudioUsed':False,'provider':'local Kokoro af_nova','subjectiveListening':'unassessed','mixMeasurement':loudness(out),'mixSha256':hashlib.sha256(out.read_bytes()).hexdigest(),'captionTiming':'rough phrase blocks per shot, not forced word alignment'}
(P/'audio-plan.json').write_text(json.dumps(report,indent=2)+'\n')
# Rebuild the editable root audio clips from the saved plan.
subprocess.run([sys.executable,str(P/'build.py')],cwd=ROOT,check=True)
print(json.dumps({'cues':len(tracks),'mix':report['mixMeasurement'],'baseline':'unity gain, decoded sample equality before AAC encoding'},indent=2))
