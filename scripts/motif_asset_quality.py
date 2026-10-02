"""Asset lifecycle; explicit review and human promotion, never auto-canonicalize."""
import json,hashlib,re
from pathlib import Path
CHECKS=('silhouette','mobile','material','layers','anchors','geometry','interaction','alpha','provenance','licensing')
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def validate(meta,path):
    issues=[]
    for k in ('id','state','scope','materials','layers','anchors','interactions','provenance','license','sha256'):
        if k not in meta or meta[k] in ('',None,[],{}):issues.append('missing metadata: '+k)
    if meta.get('state') not in ('GENERATED','REVIEW','CANONICAL'):issues.append('invalid lifecycle state')
    if meta.get('scope') not in ('scene-specific','candidate-reusable','canonical'):issues.append('invalid reuse scope')
    if meta.get('sha256')!=digest(path):issues.append('asset hash mismatch')
    for name,xy in meta.get('anchors',{}).items():
        if not isinstance(xy,list) or len(xy)!=2 or any(not isinstance(n,(int,float)) or not 0<=n<=1 for n in xy):issues.append('invalid normalized anchor: '+name)
    if Path(path).suffix.lower()=='.svg':
        raw=Path(path).read_text();ids=set(re.findall(r'id="([^"]+)"',raw))
        if not set(meta.get('layers',[]))<=ids:issues.append('layers missing from geometry')
    else:
        from PIL import Image
        with Image.open(path) as im:
            if meta.get('background')=='transparent' and 'A' not in im.getbands():issues.append('transparent raster has no alpha')
        if meta.get('background') not in ('transparent','intentional-solid'):issues.append('raster background treatment missing')
    return issues

def transition(meta,path,requested,review=None):
    m=json.loads(json.dumps(meta))
    if requested=='REVIEW' and m.get('state')=='GENERATED':
        m['state']='REVIEW';return m
    if requested!='CANONICAL' or m.get('state')!='REVIEW':raise ValueError('lifecycle must be GENERATED → REVIEW → CANONICAL')
    problems=validate(m,path)
    if not review or review.get('asset_sha256')!=digest(path):problems.append('missing or stale asset review')
    else:
        if set(review.get('checks',{}))!=set(CHECKS) or any(v!='PASS' for v in review.get('checks',{}).values()):problems.append('all asset checks must pass separately')
        if not review.get('reviewer') or not review.get('approved_at') or review.get('human_approved') is not True:problems.append('explicit human asset approval required')
    if m.get('scope')=='scene-specific':problems.append('one-off remains scene-specific; nominate reusable candidate explicitly')
    if problems:raise ValueError('; '.join(problems))
    m.update(state='CANONICAL',scope='canonical',promotion_review=review);return m
