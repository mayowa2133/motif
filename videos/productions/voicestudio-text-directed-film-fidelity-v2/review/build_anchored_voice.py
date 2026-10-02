"""Regenerate natural clauses with local Kokoro; never stretch or truncate speech.

Each saved take is generated at its recorded cadence. Only quiet edge padding is
trimmed; measured DTW words are offset by the clause's actual placement.
"""
import json,os,subprocess,sys,wave
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parents[1]
ROOT=P.parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from motif_script import align_voice
BLOCKS=[
 (0,138,"A solo dev just open sourced a free version of ElevenLabs, and it's already past 36,000 stars."),
 (138,328,"So instead of paying ElevenLabs every month to clone your voice, you can now do it on your own computer, even on the 10 year old laptop you have sitting around in the basement."),
 (328,400,"It's called VoiceStudio, and you give it a short clip of you talking,"),
 (400,507,"and it can read anything back in your voice. And cloning your voice is just the start because"),
 (507,559,"it turns any book into an audiobook,"),
 (559,651,"types out whatever you want to say, and writes a transcript of any recording."),
 (651,790,"But here's the part that's even crazier. It can dub your videos into 646 languages,"),
 (790,878,"which means stop paying any more bills, since it runs on your computer"),
 (878,937,"and your voice never has to get uploaded anywhere."),
 (937,986,"For the link and setup, comment Voice.")
]
assert ' '.join(x[2] for x in BLOCKS)==(P/'script.txt').read_text().strip()
def readwav(p):
 with wave.open(str(p)) as w:
  assert w.getsampwidth()==2 and w.getnchannels()==1
  return np.frombuffer(w.readframes(w.getnframes()),'<i2').copy(),w.getframerate()
def writewav(p,a,sr):
 with wave.open(str(p),'wb') as w:
  w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes(a.astype('<i2').tobytes())
def quiet_crop(a,sr):
 hop=round(sr*.01);energies=[np.sqrt(np.mean(a[i:i+hop].astype(float)**2))/32768 for i in range(0,len(a),hop)]
 active=[i for i,v in enumerate(energies) if v>.0012]
 assert active
 lo=max(0,active[0]*hop-round(.035*sr));hi=min(len(a),(active[-1]+1)*hop+round(.045*sr))
 return a[lo:hi],lo,hi
env=dict(os.environ,HYPERFRAMES_PYTHON=str(Path.home()/'.cache/motif-kokoro-venv/bin/python'))
records=[];allwords=[];mix=None
for i,(start,end,text) in enumerate(BLOCKS):
 folder=P/'assets/voice/clauses'/f'{i+1:02d}';folder.mkdir(parents=True,exist_ok=True)
 (folder/'input.txt').write_text(text+'\n');target=(end-start)/30-.035;speed=1.295;takes=[];slow=None;fast=None;best=None
 for attempt in range(1,10):
  out=folder/f'take-{attempt:02d}-speed-{speed:.4f}.wav'
  if not out.exists():
   cmd=['npx','--yes','hyperframes@0.8.99','tts','--text-file='+str(folder/'input.txt'),'--voice=af_nova','--speed='+str(speed),'--output='+str(out),'--json']
   run=subprocess.run(cmd,cwd=P,env=env,text=True,capture_output=True)
   (folder/f'take-{attempt:02d}.log').write_text(run.stdout+run.stderr)
   if run.returncode:raise RuntimeError(run.stderr)
  raw,sr=readwav(out);a,lo,hi=quiet_crop(raw,sr);duration=len(a)/sr
  takes.append({'file':str(out.relative_to(P)),'speed':speed,'raw_duration':len(raw)/sr,'quiet_crop_samples':[lo,hi],'spoken_duration':duration})
  print(f'clause {i+1}, take{attempt}: {duration:.3f}s / {target:.3f}s at {speed:.4f}',flush=True)
  if duration<=target and (best is None or duration>best[0]):best=(duration,a.copy(),sr,takes[-1])
  if target-.075<=duration<=target:break
  if duration>target:slow=speed
  else:fast=speed
  speed=round((slow+fast)/2 if slow is not None and fast is not None else speed*duration/(target-.022),4)
 else:
  if best is None or target-best[0]>.20:raise ValueError('Regenerate cadence; never truncate speech')
  duration,a,sr,selected_record=best
 ramp=min(round(.003*sr),len(a)//2);a=a.astype(float)
 a[:ramp]*=np.linspace(0,1,ramp);a[-ramp:]*=np.linspace(1,0,ramp);a=a.astype('<i2')
 selected=folder/'selected.wav';writewav(selected,a,sr)
 # Reuse the installed Motif DTW alignment without contaminating old cached data.
 alignment=folder/'alignment';(alignment/'assets/voice').mkdir(parents=True,exist_ok=True)
 import shutil
 shutil.copy2(selected,alignment/'assets/voice/narration-af-nova.wav')
 words,d=align_voice(alignment)
 for w in words:
  allwords.append({**w,'start':w['start']+start/30,'end':w['end']+start/30,'centers':[c+start/30 for c in w['centers']],'clause':i+1})
 if mix is None:mix=np.zeros(round(986/30*sr),dtype='<i2')
 offset=round(start/30*sr);assert offset+len(a)<=round(end/30*sr)
 mix[offset:offset+len(a)]=a
 records.append({'id':i+1,'text':text,'start_frame':start,'end_frame':end,'actual_start':start/30,'actual_end':start/30+d,'takes':takes,'selected_generation':next(t for t in takes if abs(t['spoken_duration']-duration)<1e-6),'selected':str(selected.relative_to(P)),'edge_only_fade_ms':3})
writewav(P/'assets/voice/narration-af-nova.wav',mix,sr)
(P/'speech-timing.json').write_text(json.dumps({'method':'installed Whisper small.en DTW per saved natural clause, offset by actual assembly time','precision':'approximate measured word boundaries; no caption-only retiming','duration':len(mix)/sr,'words':allwords},indent=2)+'\n')
(P/'assets/voice/semantic-voice-manifest.json').write_text(json.dumps({'voice':'af_nova','engine':'local Kokoro-82M through pinned HyperFrames tts','script_preserved':True,'post_generation_speed_change':False,'truncated_speech':False,'blocks':records,'human_listening':'pending'},indent=2)+'\n')
