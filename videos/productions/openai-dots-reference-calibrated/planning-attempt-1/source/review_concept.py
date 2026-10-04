"""One bounded concept revision; uses the shared live call/schema/gate validator.

The previous responses included positive novelty observations in a blocking
warning array. Clarify that field for the independent reviewer; never edit its
verdict. Third concept attempt is the last before human art-direction input.
"""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[4]/'scripts'))
from motif_reference import read,write,sha,context,folder,require_calibration,stage_status,CONCEPT
from motif_direct import model_call,backend_config
p=Path(__file__).resolve().parents[1];base=p/'reference-gates/concept'
require_calibration(p,required=True);plan=read(p/'production-plan.json');ev=read(p/'concept-evidence.json');ref,images=context(p)
if (base/'attempt-3.json').exists():raise ValueError('bounded concept attempts exhausted; no silent additional call')
for im in ev['images']+ev['previews']:
 if sha(im['file'])!=im['sha256']:raise ValueError('changed concept evidence')
images=[Path(x['file']) for x in ev['images']]+images
previous=(base/'concept-critic-input.txt').read_text();prefix=previous.split('\nSTAGE EVIDENCE IMAGE ORDER')[0]
prompt=prefix+'\nSTAGE EVIDENCE IMAGE ORDER (first attachments):'+json.dumps(ev)+ref+'\nOutput contract clarification: novelty_warnings is a blocking warning array. Include actual unresolved novelty/structure problems only. Put positive observations, no-imitation findings and general caveats in checks/limits, not warnings. Empty array when no such problem exists. Judge the actual revised images independently; there is no requested PASS.'
write(base/'attempt-3.json',{'bounded_attempt':3,'maximum':3,'evidence_sha256':sha(p/'concept-evidence.json')})
report=model_call(base,'concept-critic',prompt,'schemas/reference-gate.schema.json',backend_config(),images)
status=stage_status(plan,report,'concept',read(folder(p)/'calibration.json')['selected_setup_ids'],ev['setup_ids'])
write(base/'record.json',{**status,'plan_sha256':sha(p/'production-plan.json'),'calibration_record_sha256':sha(folder(p)/'record.json'),'evidence_path':str(p/'concept-evidence.json'),'evidence_sha256':sha(p/'concept-evidence.json'),'response_sha256':sha(base/'concept-critic.json'),'invocation_sha256':sha(base/'concept-critic-invocation.json'),'human_approval':False})
print(json.dumps(status,indent=2))
