"""Explicit legacy shape augmentation; never creative approval or silent defaults."""
import copy,json
from pathlib import Path
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
SCHEMA='schemas/script-production-plan.schema.json'
RELOCATE_ROOT={'status','agent_assisted'}
RELOCATE_BEAT={'caption','duration_seconds'}

def require_complete_plan(plan):
 schema=json.loads((ROOT/SCHEMA).read_text());errors=list(Draft202012Validator(schema).iter_errors(plan))
 if errors:
  brief=['/'+('/'.join(map(str,e.absolute_path)))+': '+e.message for e in errors[:8]]
  raise ValueError('complete transfer script-production-plan required before review: '+'; '.join(brief))
 return plan

def verify_augmentation(raw,normalized):
 """Only missing required root/beat fields and listed legacy annotations move.
 Caller supplies every actual value. Existing narration/quality/structure and all
 other existing values/array ordering remain identical; no defaults are generated.
 """
 schema=json.loads((ROOT/SCHEMA).read_text());root_required=set(schema['required']);beat_required=set(schema['properties']['beats']['items']['required']);annotations=[];additions=[]
 def compare(old,new,path=()):
  if isinstance(old,dict):
   if not isinstance(new,dict):raise ValueError('shape augmentation changed existing object')
   allowed=root_required if not path else beat_required if len(path)==2 and path[0]=='beats' else {'agent_assisted'} if len(path)==2 and path[0]=='asset_usage' else set()
   relocatable=RELOCATE_ROOT if not path else RELOCATE_BEAT if len(path)==2 and path[0]=='beats' else set()
   for key,value in old.items():
    if key in relocatable:
     if key in new:raise ValueError('legacy annotation must relocate explicitly')
     annotations.append({'path':list(path+(key,)),'value':copy.deepcopy(value)});continue
    if key not in new:raise ValueError('shape augmentation removed existing semantic field: '+str(path+(key,)))
    compare(value,new[key],path+(key,))
   for key in sorted(new.keys()-old.keys()):
    if key not in allowed:raise ValueError('only missing required shape fields may be added: '+str(path+(key,)))
    additions.append({'path':list(path+(key,)),'value':copy.deepcopy(new[key])})
  elif isinstance(old,list):
   if not isinstance(new,list) or len(old)!=len(new):raise ValueError('shape augmentation changed array coverage/order')
   for index,(a,b) in enumerate(zip(old,new,strict=True)):compare(a,b,path+(index,))
  elif old!=new or type(old)!=type(new):raise ValueError('shape augmentation changed existing semantic value: '+str(path))
 compare(raw,normalized);require_complete_plan(normalized)
 from motif_structure import check_structure
 check_structure(normalized)
 return {'relocated_legacy_annotations':annotations,'explicit_added_fields':additions,'scope':'data shape only; added fields were NOT part of historical visual reviews; no PASS or budget reset'}
