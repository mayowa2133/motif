"""Verify the saved evaluated productions; no production edits or model calls."""
import hashlib
import io
import json
import re
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'scripts'))
from motif_plan import narration, review_plan, tokens

def read(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def command(args): return subprocess.run(args,check=True,capture_output=True,text=True).stdout

results=[]
for slug in ('planned-calendar-declined','planned-arena-no-winner'):
    p=ROOT/'videos/productions'/slug; plan=read(p/'production-plan.json'); brief=read(p/'brief.json')
    trace=read(p/'action-trace.json'); spec=read(p/'scene-events.json'); labels=read(p/'label-timing.json')
    verify=read(p/'verification.json'); final=p/'renders/final.mp4'
    expected={'calendar':'unchanged','A':'untested','B':'untested','winner':'none','handoff':False} if plan['environment']=='calendar' else {'calendar':'unchanged','A':'fail','B':'fail','winner':'none','handoff':True}
    deterministic=review_plan(plan,brief)
    audio_command=subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',str(final),'-vn','-af','loudnorm=I=-16:TP=-2:LRA=11:print_format=json','-f','null','-'],check=True,capture_output=True,text=True)
    meter=json.loads(re.search(r'\{\s*"input_i".*?\}',audio_command.stderr,re.S)[0])
    measured={'integrated_lufs':float(meter['input_i']),'true_peak_dbtp':float(meter['input_tp'])}
    probe=json.loads(command(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_type,width,height,r_frame_rate,nb_frames,duration','-of','json',str(final)]))
    def vhash(path): return command(['ffmpeg','-v','error','-i',str(path),'-map','0:v:0','-c:v','copy','-f','hash','-hash','sha256','-']).strip().split('=')[1]
    source=read(p/'source-hashes.json'); current={name:sha(ROOT/name) for name in source}
    html=(p/'index.html').read_text()
    checks={
      'expected_outcome_matches_simulated_final':deterministic['pass'] and deterministic['final']==expected,
      'accepted_live_model_review':read(p/'planning-review.json')['pass'],
      'script_from_plan':(p/'assets/voice/narration.txt').read_text().strip()==narration(plan),
      'all_captions_and_headlines_consumed':all(b['caption'] in html and b['headline'] in html for b in plan['beats']),
      'headlines_follow_completed_evidence':all(label['headline_start'] is None or label['headline_start']>=max([a['complete'] for a in trace if a['beat']==label['beat'] and a['kind']!='bot.pose'] or [label['caption_start']]) for label in labels),
      'no_commit_or_selection_in_evaluated_ending':not any(a['kind'] in ('calendar.commit','arena.select') for a in trace),
      'first_final_encoded_video_equal':vhash(p/'renders/first.mp4')==vhash(final),
      'audio_target':abs(measured['integrated_lufs']+16)<=.8,
      'audio_peak_ceiling':measured['true_peak_dbtp']<=-1.5,
      'source_unchanged':source==current,
      'duration_in_explicit_range':brief['intended_duration_seconds']-brief['duration_tolerance_seconds']<=float(probe['format']['duration'])<=brief['intended_duration_seconds']+brief['duration_tolerance_seconds'],
    }
    assert all(checks.values()),checks
    samples=[]
    for label in labels:
        # Show completed physical evidence, or the middle of a pure hold beat.
        action_ends=[a['complete'] for a in trace if a['beat']==label['beat'] and a['kind']!='bot.pose']
        t=min(label['beat_end']-.15,max(action_ends)+.25 if action_ends else (label['caption_start']+label['beat_end'])/2)
        samples.append(round(t,3))
    samples.append(round(float(probe['format']['duration'])-.5,3))
    sheet=Image.new('RGB',(360*len(samples),688),'#f4eee1'); draw=ImageDraw.Draw(sheet)
    for i,t in enumerate(samples):
        pixels=subprocess.run(['ffmpeg','-v','error','-ss',str(t),'-i',str(p/'renders/mobile.mp4'),'-frames:v','1','-f','image2pipe','-vcodec','png','-'],check=True,capture_output=True).stdout
        sheet.paste(Image.open(io.BytesIO(pixels)).convert('RGB'),(i*360,48)); draw.text((i*360+10,16),f'{slug} / {t:.2f}s',fill='#202c32')
    sheet.save(OUT/(slug+'-mobile.jpg'),quality=95)
    results.append({'slug':slug,'backend':read(p/'backend.json'),'narration':narration(plan),'plan_hash':sha(p/'production-plan.json'),'initial_plan_hash':sha(p/'initial-plan.json'),'final_sha256':sha(final),'expected_final':expected,'actual_final':deterministic['final'],'actions':trace,'caption_and_headline_times':labels,'encoded_probe':probe,'encoded_audio':measured,'checks':checks,'frame_samples':samples,'subjective_listening':'not assessed','plan_corrections':read(p/'planning-review.json')['corrections']})
assert results[0]['narration']!=results[1]['narration']
assert read(ROOT/'videos/productions/planned-calendar-declined/source-hashes.json')==read(ROOT/'videos/productions/planned-arena-no-winner/source-hashes.json')==read(OUT/'shared-source-before-runs.json')
frozen=read(OUT/'frozen-before.json')
changed=[p for p,h in frozen.items() if sha(ROOT/p)!=h]
assert not changed,changed
write={'productions':results,'different_scripts':True,'same_shared_source':True,'frozen_files_checked':len(frozen),'frozen_changed':changed,'manual_per_run_plan_or_source_edits':[]}
(OUT/'results.json').write_text(json.dumps(write,indent=2)+'\n')
print(json.dumps({'checks':'PASS','different_scripts':True,'same_shared_source':True,'frozen_files':len(frozen),'outputs':[(r['slug'],r['encoded_audio'],r['encoded_probe']['format']) for r in results]},indent=2))
