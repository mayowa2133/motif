#!/usr/bin/env python3
"""Saved production and explicit quality reviews; never replans or synthesizes."""
import sys,os,argparse
from pathlib import Path
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parents[1];R=P.parents[2];sys.path.insert(0,str(R/'scripts'))
from motif_quality import read,write,rough,evidence_bundle,critics,verify_frozen,direction_review,sha,require_gate
from motif_produce import command
from motif_direct import backend_config
def review_config():
 os.environ.setdefault('MOTIF_PLANNER_MODEL','gpt-5.6-sol')
 config=backend_config();config['reasoning_effort']='high';config['hyperframes']='0.8.99'
 return config
def compile_current():
 command([sys.executable,str(P/'source/build.py')],P)
 record=read(P/'compile-record.json')
 for group in ('inputs','outputs'):
  if any(not (P/n).is_file() or sha(P/n)!=h for n,h in record[group].items()):
   raise ValueError('compiled '+group+' are stale')

p=argparse.ArgumentParser();p.add_argument('action',choices=['direction','rough','critique-rough','render-saved']);a=p.parse_args()
if a.action=='direction':
 c=review_config()
 print(direction_review(P,read(P/'production-plan.json'),c))
elif a.action=='rough':
 if not read(P/'quality-direction.json')['pass']:raise ValueError('pre-animation direction blocked')
 compile_current()
 output=rough(P)
 evidence_bundle(P,'rough',output/'captions.mp4',output/'no-captions.mp4',read(P/'evidence-shots.json'))
 print(output)
elif a.action=='critique-rough':
 c=review_config()
 print(critics(P,'rough',c))
else:
 if not (P/'quality-direction.json').exists() or not read(P/'quality-direction.json')['pass']:
  raise ValueError('Saved render blocked: pre-animation direction has not passed. No planning or synthesis attempted.')
 require_gate(P,'final')
 # Rebuild finite tables from saved plan, original asset groups and measured words.
 compile_current()
 out=P/'renders/reproduced.mp4'
 command(['npm','run','check'],P)
 command(['npm','run','render','--','-o',str(out),'--skill=general-video','-q','delivery'],P)
 print(out)
print(verify_frozen())
