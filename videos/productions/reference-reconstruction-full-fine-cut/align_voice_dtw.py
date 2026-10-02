"""Actual voice token alignment using the installed local Whisper model.

Disable flash attention for this invocation so the DTW output contains real
alignment centers (the default CLI invocation returned t_dtw=-1).
No new engine, model or production runtime dependency.
"""
from pathlib import Path
import json,subprocess
P=Path(__file__).resolve().parent
plan=json.loads((P/'narration-script.json').read_text())
model='/Users/mayowaadesanya/.cache/hyperframes/whisper/models/ggml-small.en.bin'
for seg in plan['segments']:
    stem=seg.get('voiceFile','fine-'+seg['id']);base=P/'assets/voice'/stem
    audio=base.with_suffix('.wav');raw=base.with_name(stem+'-dtw.json')
    if not raw.exists():
        prepared=base.with_name(stem+'-alignment16.wav')
        subprocess.run(['ffmpeg','-v','error','-y','-i',str(audio),'-ar','16000','-ac','1',str(prepared)],check=True)
        with base.with_name(stem+'-dtw.log').open('w') as f:
            subprocess.run(['/opt/homebrew/bin/whisper-cli','-m',model,'-f',str(prepared),'-ojf','-of',str(raw.with_suffix('')),'--dtw','small.en','--no-flash-attn','--suppress-nst','-l','en'],stdout=f,stderr=f,check=True)
    native=json.loads(raw.read_text());words=[]
    for phrase in native['transcription']:
        for tok in phrase['tokens']:
            text=tok['text']
            if text.startswith('['):continue
            if text.strip() in ['.',',',':',';','!','?']:
                if words:words[-1]['text']+=text.strip()
                continue
            assert tok['t_dtw']>=0,(stem,text)
            center=tok['t_dtw']/100
            if text.startswith(' ') or not words:
                words.append({'text':text.strip(),'centers':[center]})
            else:
                words[-1]['text']+=text;words[-1]['centers'].append(center)
    d=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(audio)]))
    for i,w in enumerate(words):
        w['start']=max(0,(words[i-1]['centers'][-1]+w['centers'][0])/2 if i else w['centers'][0]-.12)
        w['end']=min(d,(w['centers'][-1]+words[i+1]['centers'][0])/2 if i<len(words)-1 else w['centers'][-1]+.12)
        assert w['start']<w['end']
    base.with_name(stem+'-aligned-words.json').write_text(json.dumps({'method':'Whisper small.en DTW token centers; adjacent center midpoints for word boundaries; local no-flash-attn invocation','duration':d,'words':words},indent=2)+'\n')
    print(seg['id'],[(w['text'],w['start'],w['end']) for w in words],flush=True)
