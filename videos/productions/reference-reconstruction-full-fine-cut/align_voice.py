"""Measure generated voice with the existing local Whisper engine; freeze words."""
from pathlib import Path
import json, subprocess
P=Path(__file__).resolve().parent
plan=json.loads((P/'narration-script.json').read_text())
for s in plan['segments']:
    stem=s.get('voiceFile','fine-'+s['id'])
    dest=P/'assets/voice'/(stem+'-words.json')
    if dest.exists():continue
    with (P/'assets/voice'/(stem+'-asr.json')).open('w') as f:
        subprocess.run(['npx','--yes','hyperframes@0.8.99','transcribe',str(P/'assets/voice'/(stem+'.wav')),'--dir',str(P),'--engine','whisper','--model','small.en','--language','en','--json'],cwd=P,stdout=f,check=True)
    dest.write_bytes((P/'transcript.json').read_bytes())
    print(s['id'],json.loads(dest.read_text()),flush=True)
