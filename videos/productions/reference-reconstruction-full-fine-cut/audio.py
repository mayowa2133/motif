"""Finish only new audio around the locked approved soundtrack at unity."""
from pathlib import Path
import hashlib,json,subprocess,sys
import numpy as np
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from motif_produce import loudness
D=1262/30;RATE=48000
def run(args):return subprocess.check_output(args,stderr=subprocess.PIPE)
def decode(path):return np.frombuffer(run(['ffmpeg','-v','error','-i',str(path),'-f','f32le','-ar',str(RATE),'-ac','2','-']),dtype='<f4').reshape(-1,2)
def duration(path):return float(run(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(path)]))
plan=json.loads((P/'narration-script.json').read_text())
master=np.zeros((round(D*RATE),2),dtype=np.float32);tracks=[];fits=[]
for seg in plan['segments']:
    name=seg.get('voiceFile','fine-'+seg['id']);a,z=seg['frames'];start_time=a/30+seg.get('offsetSeconds',0)
    source=P/'assets/voice'/(name+'.wav');out=P/'assets/voice'/(name+'-mixed.wav');d=duration(source)
    assert start_time+d<=z/30+.00005,(name,start_time+d,z/30)
    run(['ffmpeg','-v','error','-y','-i',str(source),'-af',f'afade=t=in:d=0.008,afade=t=out:st={d-.008}:d=0.008,loudnorm=I=-14.9:TP=-2.1:LRA=11', '-ar',str(RATE),'-ac','2','-c:a','pcm_f32le',str(out)])
    data=decode(out);start=round(start_time*RATE)
    master[start:start+len(data)]+=data
    fits.append({'id':seg['id'],'duration':d,'start':start_time,'atempo':1,'synthesisSpeed':plan['speed'],'text':seg['text']})
    tracks.append({'src':str(out.relative_to(P)),'start':start_time,'duration':len(data)/RATE,'volume':1,'kind':'narration','id':seg['id']})
# Contact effects are the cleared existing files; none enters the locked interval.
for name,frame,gain in [('click-soft',153,.065),('click-soft',221,.10),('whoosh-short',390,.055),('click-soft',658,.06),('whoosh-short',747,.055),('pop',960,.05),('click-soft',1010,.09),('pop',1138,.07),('pop',1155,.07),('pop',1175,.07)]:
    source=P/'assets/sfx'/(name+'.mp3');data=decode(source)*gain;start=round(frame/30*RATE);length=min(len(data),len(master)-start)
    assert start+length<=round(436/30*RATE) or start>=round(600/30*RATE)
    master[start:start+length]+=data[:length]
    tracks.append({'src':str(source.relative_to(P)),'start':frame/30,'duration':length/RATE,'volume':gain,'kind':'contact effect','id':f'{name}-{frame}'})
# No whole-film limiter or gain. The approved decoded PCM occupies its interval verbatim.
base=decode(P/'assets/baseline/final.mp4')[:round(164/30*RATE)];start=round(436/30*RATE)
assert np.count_nonzero(master[start:start+len(base)])==0
master[start:start+len(base)]=base
assert np.array_equal(master[start:start+len(base)],base)
tracks.append({'src':'assets/baseline/final.mp4','start':436/30,'duration':164/30,'volume':1,'kind':'approved soundtrack','id':'locked-soundtrack'})
out=P/'assets/fine-mix.wav'
r=subprocess.run(['ffmpeg','-v','error','-y','-f','f32le','-ar',str(RATE),'-ac','2','-i','-','-c:a','pcm_f32le',str(out)],input=master.astype('<f4').tobytes(),capture_output=True)
assert r.returncode==0,r.stderr
report={'tracks':tracks,'performance':fits,'approvedIntervalDecodedSamplesPreservedAtUnityBeforeAAC':True,'approvedPcmSha256':hashlib.sha256(base.tobytes()).hexdigest(),'sourceAudioUsed':False,'provider':'local Kokoro ONNX af_nova','subjectiveListening':'unassessed','music':'omitted; no suitable cleared bed selected','mixMeasurement':loudness(out),'mixSha256':hashlib.sha256(out.read_bytes()).hexdigest(),'captionTiming':'Local Whisper small.en word onsets from actual generated WAV; editorial short chunks; no fixed shot-window spreading','target':{'integratedLufs':-16,'tolerance':.8,'truePeakCeilingDbtp':-1.5},'processingScope':'new voice cues only; edge fades and loudnorm; approved PCM copied at unity'}
(P/'audio-plan.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report['mixMeasurement']))
