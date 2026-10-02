"""Short stable serif captions from measured local DTW voice alignment."""
from pathlib import Path
import json, subprocess, numpy as np
from fontTools.ttLib import TTFont
P=Path(__file__).resolve().parent
plan=json.loads((P/'narration-script.json').read_text())
phrases={
 'opening':[(0,3,'The source argues'),(3,5,'old instructions'),(5,7,'can hold'),(7,10,'newer models back.'),(10,12,'Rules for'),(12,14,'retired models'),(14,16,'pile up.')],
 'burden':[(0,2,'Check twice.'),(2,5,'Plan every step.'),(5,8,'That extra work'),(8,11,'slows the race.')],
 'suggestion':[(0,2,'Try prompt audit.')],
 'rituals':[(0,3,'Remove repeated checks.'),(3,6,'Stop shouting commands.'),(6,9,'Cut unnecessary steps.')],
 'permission':[(0,2,'Review changes.'),(2,4,'Nothing applies'),(4,6,'without permission.')],
 'example':[(0,3,'One developer reports'),(3,5,'seventy improvements'),(5,8,'across three files.')],
 'results':[(0,3,'A cited test claims'),(3,4,'nine percent'),(4,6,'lower cost,'),(6,8,'and roughly'),(8,10,'two points'),(10,12,'more accuracy'),(12,16,'on the same model.')],
 'ending':[(0,2,'The takeaway:'),(2,5,'audit your instructions.')]
}
f=TTFont('/Users/mayowaadesanya/.agents/skills/hyperframes-creative/frame-presets/code-editorial/fonts/EBGaramond-700.woff2');cmap=f.getBestCmap();hmtx=f['hmtx'].metrics;em=f['head'].unitsPerEm
chunks=[];records=[]
for seg in plan['segments']:
    stem=seg.get('voiceFile','fine-'+seg['id']);aligned=json.loads((P/'assets/voice'/(stem+'-aligned-words.json')).read_text());words=aligned['words'];shift=seg['frames'][0]/30+seg.get('offsetSeconds',0)
    # Clamp the first/last caption to actual waveform activity, not ASR's
    # occasionally long terminal timestamp or the cue's padded silence.
    x=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(P/'assets/voice'/(stem+'.wav')),'-ar','16000','-ac','1','-f','f32le','-']),dtype='<f4');rms=np.sqrt(np.mean(x[:len(x)//160*160].reshape(-1,160)**2,axis=1));active=np.flatnonzero(rms>.003)
    speech_start=max(0,active[0]/100-.02);speech_end=min(aligned['duration'],(active[-1]+1)/100+.10)
    assert phrases[seg['id']][-1][1]==len(words),(seg['id'],len(words))
    previous=None
    for a,z,text in phrases[seg['id']]:
        start=shift+(speech_start if a==0 else words[a]['start']);end=shift+(speech_end if z==len(words) else words[z]['start'])
        # Stable direct handoff on frame boundaries; no entrance/exit tween.
        start=round(start*30)/30;end=round(end*30)/30
        width=96+sum(hmtx[cmap.get(ord(ch),cmap[32])][0] for ch in text)*67/em
        chunks.append({'segment':seg['id'],'text':text,'start':start,'end':end,'width':round(width,2),'alignedWordRange':[a,z],'spokenTokens':[w['text'] for w in words[a:z]]})
    records.append({'id':seg['id'],'measuredSpeechActivity':[speech_start,speech_end],'dtwFile':'assets/voice/'+stem+'-dtw.json','textNormalization':'ASR merged TryPrompt → scripted Try prompt; numerical 70/9% → spoken words; missing article A restored from synthesis script.'})
assert all(c['start']<c['end'] for c in chunks)
for a,b in zip(chunks,chunks[1:]):assert a['end']<=b['start']+.00001
(P/'caption-alignment.json').write_text(json.dumps({'method':'Actual generated WAVs, installed Whisper small.en DTW with flash attention disabled; token-center midpoints, waveform speech limits, editorial phrase grouping and nearest 30fps boundary','accuracyLimit':'Automatic alignment with waveform checks; phoneme-perfect forced alignment and subjective listening are not claimed.','sourceAudioUsed':False,'approvedCaptions':'unchanged in approved clip, [436,600)','segments':records,'chunks':chunks},indent=2)+'\n')
print(len(chunks),'speech-aligned chunks')
