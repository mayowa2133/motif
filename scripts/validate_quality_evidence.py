#!/usr/bin/env python3
"""Verify recorded LIVE, blind painted regressions. Does not invoke a model."""
from pathlib import Path
from motif_quality import ROOT,read,write,sha,evaluate,verify_frozen

def validate():
    p=ROOT/'quality/validation/fixtures';base=p/'quality-review/rough';expected=read(p/'expected.json')['expected_violations'];reports={role:read(base/(role+'-critic.json')) for role in ('story','visual')}
    actual={shot:set() for shot in expected}
    for role,r in reports.items():
        inv=read(base/(role+'-critic-invocation.json'))
        if inv['exit_code'] or inv['saved_response_used'] or inv['model_fallback_used']:raise ValueError('not a successful live invocation')
        if not any(a=='-i' for a in inv['argv']):raise ValueError('critic did not receive image inputs')
        text=(base/(role+'-critic-input.txt')).read_text()
        if 'expected.json' in text or 'consequence-removed' in text or 'cheerful-burden' in text:raise ValueError('expected fault labels leaked into critic input')
        for v in r['violations']:
            if v['shot'] in actual:actual[v['shot']].add(v['gate'])
    outcomes={shot:{'expected_gates':gates,'observed_failures':sorted(actual[shot]),'caught':bool(set(gates)&actual[shot])} for shot,gates in expected.items()}
    if not all(o['caught'] for o in outcomes.values()):raise ValueError('live critic missed a planted failure: '+str(outcomes))
    control={role:next(a for a in r['shot_assessments'] if a['shot']=='q01') for role,r in reports.items()}
    if any(g['status']!='PASS' for a in control.values() for g in a['gates']):raise ValueError('control did not clear critic gates')
    gate=evaluate(p,'rough')
    if gate['status']=='FINAL_ART_ALLOWED' or gate['publish']:raise ValueError('negative fixtures improperly advanced')
    result={'scope':'finite copied regressions; no claim of general original-film quality','painted_failures':outcomes,'control':'PASS in both live critics','gate':gate['status'],'review_method':read(base/'evidence.json')['inspection'],'separate_live_invocations':2,'critics_record_sha256':sha(base/'critics-record.json'),'freeze':verify_frozen(),'approval':'system ready for human review; no film acceptance/publishing','failed_backend_attempt':'retained separately; invalid schema, no output substitution','first_validation':'retained; global-only grading missed two faults, corrected with independent per-shot review and native frames'}
    write(ROOT/'quality/validation/results.json',result);return result
if __name__=='__main__':
 import json
 print(json.dumps(validate(),indent=2))
