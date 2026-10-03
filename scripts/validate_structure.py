#!/usr/bin/env python3
"""Run withheld-label planning fixtures through the ordinary live structure critic."""
import argparse,sys
from pathlib import Path
sys.dont_write_bytecode=True
from motif_quality import ROOT,read,write,sha,verify_frozen
from motif_structure import structure_review,require_structure,report_status,policy_hashes
from motif_direct import backend_config
P=ROOT/'quality/validation/structure-v1'

def preservation():
 baseline=read(P/'rowhouse-preservation.json');project=ROOT/baseline['project']
 now={str(p.relative_to(project)):sha(p) for p in sorted(project.rglob('*')) if p.is_file()}
 if now!=baseline['sha256']:raise ValueError('rejected rowhouse contents changed')
 negative=read(ROOT/'quality/negative/rowhouse.json')
 assert not negative['gold_art']
 assert all(sha(project/k)==v for k,v in negative['sha256'].items())
 assert all(e['clip']['file'].split('/')[2]!='every-change-should-be-reversible' for e in read(ROOT/'quality/gold/index.json')['examples'])
 return {'frozen_benchmark_and_canonical':verify_frozen(),'rowhouse_files_verified':len(now),'rowhouse_unchanged':True,'negative_not_gold':True}

def verify_fixture(folder):
 plan=read(folder/'production-plan.json');report=read(folder/'quality-structure.json');record=read(folder/'quality-structure-record.json');invocation=read(folder/'quality-structure-invocation.json')
 assert record['plan_sha256']==sha(folder/'production-plan.json')
 assert record['response_sha256']==sha(folder/'quality-structure.json') and record['invocation_sha256']==sha(folder/'quality-structure-invocation.json')
 assert record['policy_hashes']==policy_hashes()
 assert invocation['exit_code']==0 and not invocation['saved_response_used'] and not invocation['model_fallback_used']
 assert invocation['input_sha256']==sha(folder/'quality-structure-input.txt') and invocation['output_schema_sha256']==sha(folder/'quality-structure-output-schema.json')
 prompt=(folder/'quality-structure-input.txt').read_text();assert 'Withheld from independent critic' not in prompt and 'expected.json' not in prompt
 status=report_status(plan,report);expected=read(folder/'expected.json')['expected'];found={v['code'] for v in report['violations']}
 passed=status=='PASS' if expected==['PASS'] else set(expected)<=found and status=='REPLAN_REQUIRED'
 if status=='PASS':require_structure(folder)
 return {'fixture':folder.name,'expected':expected,'observed_codes':sorted(found),'gate':status,'expectation_met':passed,'plan_sha256':sha(folder/'production-plan.json'),'report_sha256':sha(folder/'quality-structure.json'),'invocation_sha256':sha(folder/'quality-structure-invocation.json')}

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--live',action='store_true');a=parser.parse_args();config=backend_config() if a.live else None
 if a.live:
  for folder in sorted((P/'fixtures-clean').iterdir()):
   if (folder/'quality-structure-record.json').exists():raise ValueError('preserve prior run; do not overwrite fixture reviews')
   try:structure_review(folder,read(folder/'production-plan.json'),config)
   except ValueError:
    if not (folder/'quality-structure-record.json').exists():raise
   print('CHECK',verify_fixture(folder),flush=True)
 results=[verify_fixture(f) for f in sorted((P/'fixtures-clean').iterdir())]
 result={'status':'PASS' if all(r['expectation_met'] for r in results) else 'FAIL','scope':'Internal planning fixtures; no film, final artwork, audio or human approval','fixtures':results,'live_calls':len(results),'preservation':preservation(),'policy_hashes':policy_hashes()}
 write(P/'results.json',result);print(result['status'],flush=True)
 if result['status']!='PASS':raise ValueError('structural fixture expectations not met; see results.json')
if __name__=='__main__':main()
