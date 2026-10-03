#!/usr/bin/env python3
"""Preserve and verify prior live quality evidence without rewriting old gates."""
import json,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
from jsonschema import Draft202012Validator
from motif_quality import ROOT,read,write,sha,verify_frozen
P=ROOT/'quality/validation/structure-v1'

def historical(name,relative):
 project=ROOT/relative;base=project/'quality-review/rough';record=read(base/'critics-record.json');manifest=read(base/'evidence.json');reports={}
 assert record['evidence_sha256']==sha(base/'evidence.json') and record['images_sha256']==sha(base/'image-inputs.json')
 for image in read(base/'image-inputs.json'):assert sha(image['file'])==image['sha256']
 for mode in ['with_captions','without_captions']:
  e=manifest[mode];assert sha(e['video'])==e['probe']['sha256'] and sha(e['motion_trace'])==e['trace_sha256']
 for role in ['story','visual']:
  report=read(base/(role+'-critic.json'));inv=read(base/(role+'-critic-invocation.json'))
  Draft202012Validator(read(ROOT/f'schemas/{role}-critic.schema.json')).validate(report)
  assert record['report_hashes'][role]==sha(base/(role+'-critic.json')) and record['invocation_hashes'][role]==sha(base/(role+'-critic-invocation.json'))
  assert inv['exit_code']==0 and not inv['saved_response_used'] and not inv['model_fallback_used']
  assert inv['input_sha256']==sha(base/(role+'-critic-input.txt')) and inv['output_schema_sha256']==sha(base/(role+'-critic-output-schema.json'))
  supplied={inv['argv'][i+1] for i,v in enumerate(inv['argv'][:-1]) if v=='-i'};assert supplied=={x['file'] for x in read(base/'image-inputs.json')}
  reports[role]=report
 def gates(shot):return {g['gate']:g['status'] for r in reports.values() for a in r['shot_assessments'] if a['shot']==shot for g in a['gates']}
 if name=='minimal':assert all(v=='PASS' for v in gates('t01').values()) and gates('t02')['energy']=='FAIL'
 elif name=='temporal':
  assert gates('t02')['physicality']=='FAIL'
  for mode in ['with_captions','without_captions']:
   window=next(w for w in manifest[mode]['temporal_windows'] if w['shot']=='t02');assert window['frames']==list(range(84,97)) and window['consecutive']
 else:
  assert all(v=='PASS' for v in gates('q01').values())
  for shot,expected in read(project/'expected.json')['expected_violations'].items():assert any(gates(shot).get(g)=='FAIL' for g in expected)
 old_sources=manifest.get('render_source_hashes',{});changed=[p for p,h in old_sources.items() if not Path(p).exists() or sha(p)!=h]
 allowed={str(ROOT/'scripts'/f'{n}.py') for n in ['motif_quality','motif_script']}
 assert set(changed)<=allowed,'unexpected historical renderer change'
 return {'fixture':name,'recorded_live_evidence_intact':True,'historical_expected_outcomes_verified':True,'authorized_shared_source_changes':changed,'fresh_rendered_approval':False,'note':'Recorded prior reviews remain historical. Current Python/Node regressions exercise updated code. No historical source fingerprint or critic was rewritten.'}

def main():
 proc=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=ROOT,text=True,capture_output=True);(P/'regression-tests.txt').write_text(proc.stdout+proc.stderr)
 assert proc.returncode==0,'Python regressions failed'
 node=subprocess.run(['node','--test','tests/test_frame_sequence.cjs'],cwd=ROOT,text=True,capture_output=True);(P/'frame-sequence-tests.txt').write_text(node.stdout+node.stderr);assert node.returncode==0
 result={'status':'PASS','python_regressions':'regression-tests.txt','node_seek_regression':'frame-sequence-tests.txt','historical_live_quality_evidence':[historical('original','quality/validation/fixtures'),historical('temporal','quality/validation/v1.1/temporal'),historical('minimal','quality/validation/v1.1/minimal')],'ten_gate_list_unchanged':read(ROOT/'quality/rubric/gates.json')['story']==['story','cause-effect','focal-hierarchy','continuity'] and read(ROOT/'quality/rubric/gates.json')['visual']==['character-performance','physicality','energy','art','composition','mobile'],'max_moving_repairs':read(ROOT/'quality/rubric/gates.json')['max_meaningful_repairs'],'freeze':verify_frozen()}
 assert result['ten_gate_list_unchanged'] and result['max_moving_repairs']==2
 write(P/'existing-quality-regressions.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
