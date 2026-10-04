#!/usr/bin/env python3
"""Live A–G semantic calibration fixtures, distinct from actual film approval."""
import argparse,json
from pathlib import Path
from motif_direct import model_call,backend_config
from motif_reference import ROOT,context,write,read,sha,require_calibration

def run(project):
 require_calibration(project,required=True);reference,images=context(project);base=ROOT/'quality/validation/reference-calibration/private';base.mkdir(parents=True,exist_ok=True);fixtures=read(ROOT/'quality/validation/reference-calibration/fixtures.json')
 cases=[{k:v for k,v in c.items() if not k.startswith('expected_')} for c in fixtures['cases']]
 prompt=(ROOT/'quality/reference-critic/PROMPT.md').read_text()+'\nThese are seven SYNTHETIC semantic rubric fixtures, not rendered productions. Decide each independently using the supplied calibration and selected visual evidence. A/C are architecture/novelty decisions (REPLAN_REQUIRED on failure); D is a hypothetical visible interaction deficiency (REPAIR_REQUIRED with REFERENCE_INTERACTION_GAP). Do not demand copied expression, clutter, a character in an absent scene, or high density during an intentional unresolved final question. Use PASS when the novel scenario meets comparable ambition. All cases required. No tools.\nCASES:'+json.dumps(cases)+reference
 r=model_call(base,'fixture-critic',prompt,'schemas/reference-fixture-review.schema.json',backend_config(),images);byid={c['id']:c for c in r['cases']}
 if set(byid)!={c['id'] for c in cases} or len(r['cases'])!=len(cases):raise ValueError('fixture coverage incomplete')
 results=[]
 for c in fixtures['cases']:
  actual=byid[c['id']];ok=actual['status']==c['expected_status'] and (not c['expected_code'] or c['expected_code'] in actual['codes']);results.append({'id':c['id'],'expected_status':c['expected_status'],'actual_status':actual['status'],'expected_code':c['expected_code'],'actual_codes':actual['codes'],'pass':ok,'evidence':actual['evidence']})
 output={'status':'PASS' if all(x['pass'] for x in results) else 'FAIL','cases':results,'live_report':str(base/'fixture-critic.json'),'report_sha256':sha(base/'fixture-critic.json'),'invocation_sha256':sha(base/'fixture-critic-invocation.json'),'scope':'live semantic fixtures; not actual film, playback, listening or proof of autonomous directing'};write(ROOT/'quality/validation/reference-calibration/results.json',output)
 if output['status']!='PASS':raise ValueError('reference fixture expectations failed: '+json.dumps(results))
 return output
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project',type=Path,required=True);print(json.dumps(run(p.parse_args().project),indent=2))
