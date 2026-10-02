#!/usr/bin/env python3
"""Verify recorded live v1.1 evidence, not synthetic critic answers."""
import sys,json,math
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from motif_quality import read,write,sha,evaluate,verify_frozen,source_freshness
import numpy as np
from PIL import Image
P=ROOT/'quality/validation/v1.1'
def reviewed(name):
 project=P/name;base=project/'quality-review/rough';manifest=read(base/'evidence.json')
 assert not source_freshness(project,manifest),'source fingerprint stale'
 expected=read(project/'expected.json');reports={}
 for role in ('story','visual'):
  invocation=read(base/(role+'-critic-invocation.json'));prompt=(base/(role+'-critic-input.txt')).read_text()
  assert invocation['exit_code']==0 and not invocation['saved_response_used'] and not invocation['model_fallback_used']
  assert invocation['input_sha256']==sha(base/(role+'-critic-input.txt'))
  assert invocation['output_schema_sha256']==sha(base/(role+'-critic-output-schema.json'))
  assert all(k not in prompt for k in ('intermediate_fault','expected_dead_hold_gate','minimal_control','withheld_from_critics')),'withheld labels leaked'
  image_paths={r['file'] for r in read(base/'image-inputs.json')};argv=invocation['argv'];supplied={argv[i+1] for i,v in enumerate(argv[:-1]) if v=='-i'}
  assert image_paths==supplied,'critic did not receive all audited images'
  reports[role]=read(base/(role+'-critic.json'))
 gate=evaluate(project,'rough');assert gate['status']=='REPLAN_REQUIRED' and not gate['publish'] and gate['human_final_approval']=='REQUIRED'
 return manifest,reports,gate

def shot_gates(reports,id_):return {g['gate']:g['status'] for report in reports.values() for a in report['shot_assessments'] if a['shot']==id_ for g in a['gates']}
def window_frame(e,shot,frame):
 w=next(w for w in e['temporal_windows'] if w['shot']==shot);offset=w['frames'].index(frame);path=w['strips_in_order'][offset//4]
 with Image.open(path) as im:return np.asarray(im.convert('RGB').crop(((offset%4)*360,28,(offset%4+1)*360,668))).astype('int16')
def main():
 temporal,reports,gate=reviewed('temporal');bad=shot_gates(reports,'t02');assert bad['physicality']=='FAIL'
 visual=reports['visual'];violations=[v for v in visual['violations'] if v['shot']=='t02' and v['gate']=='physicality'];assert any(91/30-.001<=v['timestamp']<=93/30+.001 for v in violations)
 expected=read(P/'temporal/expected.json')['intermediate_fault']['frames']
 pixels={}
 for mode in ('with_captions','without_captions'):
  e=temporal[mode];w=next(w for w in e['temporal_windows'] if w['shot']=='t02');assert w['frames']==list(range(84,97)) and set(expected)<=set(w['frames']) and w['consecutive']
  deltas={f:float(np.abs(window_frame(e,'t01',f)-window_frame(e,'t02',f+60)).mean()) for f in (25,30,31,32,33,34)}
  assert max(deltas[f] for f in (25,30,34))<.5,'before/contact/after mismatch'
  assert min(deltas[f] for f in (31,32,33))>max(deltas[f] for f in (25,30,34)), 'intermediate paint did not differ'
  pixels[mode]=deltas
 minimal,mreports,mgate=reviewed('minimal');control=shot_gates(mreports,'t01');dead=shot_gates(mreports,'t02');assert len(control)==10 and all(v=='PASS' for v in control.values());assert dead['energy']=='FAIL'
 plan=read(P/'minimal/production-plan.json');assert all(s['quality']['art_direction']['environment_mode']=='minimal-isolated' and s['quality']['environment']==[] for s in plan['shots'])
 assert all(all(v is None for k,v in s['quality']['energy'].items() if k!='dominant_action') for s in plan['shots'])
 result={'scope':'quality-system hardening fixtures, not an original-film quality guarantee','live_calls':4,'temporal':{'physicality':'FAIL correctly detected at frames 91–93','all_consecutive_frames_supplied':True,'sparse_before_contact_after_valid':True,'painted_difference_mean_abs_pixels':pixels,'gate':gate['status'],'other_control_failures':['art','composition'],'reports_sha256':{r:sha(P/'temporal/quality-review/rough'/(r+'-critic.json')) for r in reports}},'minimal':{'control_all_ten_gates':'PASS in both live critics','optional_energy_channels':None,'dead_hold_energy':'FAIL','gate':mgate['status'],'reports_sha256':{r:sha(P/'minimal/quality-review/rough'/(r+'-critic.json')) for r in mreports}},'native_media':{'temporal':temporal['with_captions']['probe'],'minimal':minimal['with_captions']['probe']},'bindings':read(P/'bindings/results.json'),'freeze':verify_frozen(),'final_human_viewing_listening':'REQUIRED','publish':False}
 write(P/'results.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
