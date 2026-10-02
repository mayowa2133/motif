from pathlib import Path
import json, os, subprocess
P=Path(__file__).resolve().parent
plan=json.loads((P/'narration-script.json').read_text())
env=dict(os.environ,HYPERFRAMES_PYTHON='/Users/mayowaadesanya/.cache/motif-kokoro-venv/bin/python')
for s in plan['segments']:
    stem=P/'assets/voice'/s.get('voiceFile','fine-'+s['id'])
    if stem.with_suffix('.wav').exists(): continue
    cmd=['npx','--yes','hyperframes@0.8.99','tts','--text-file',str(stem.with_suffix('.txt')),'--voice',plan['voice'],'--speed',str(plan['speed']),'--output',str(stem.with_suffix('.wav')),'--json']
    with stem.with_name(stem.name+'-generation.json').open('w') as f: subprocess.run(cmd,cwd=P,env=env,stdout=f,check=True)
    print(s['id'],flush=True)
