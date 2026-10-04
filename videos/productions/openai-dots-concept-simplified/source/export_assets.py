"""Three finite review-only artwork families; no registry/canonical promotion."""
import sys,base64
from pathlib import Path
sys.path[:0]=[str(Path(__file__).resolve().parent),str(Path(__file__).resolve().parents[4]/'scripts')]
from common import DEFS
from connected_art import app_terminal,computer_shell,aperture,work_strip
from motif_reference import ROOT,sha,write
p=Path(__file__).resolve().parents[1];out=p/'assets/props';out.mkdir(parents=True,exist_ok=True)
material=ROOT/'videos/productions/voicestudio-craft-v6/assets/materials/world-paper.webp'
defs=DEFS.replace('assets/materials/world-paper.webp','data:image/webp;base64,'+base64.b64encode(material.read_bytes()).decode())
assets=[('app-terminal',{'disconnected':app_terminal(False),'connected':app_terminal(True)},[54,418,620,443],{'surface':[425,737],'support':[425,807]},['agent-assisted:app-terminal-artwork','agent-assisted:terminal-contact-anchors']),('cloud-aperture',{'empty':computer_shell()+aperture()},[54,354,623,659],{'entry':[400,662],'support':[400,829],'ownership':[613,600]},['agent-assisted:cloud-aperture-artwork','agent-assisted:input-contact-anchors']),('job-strip',{'source':work_strip('before'),'outline':work_strip('source-to-outline-after'),'unfinished-draft':work_strip('after')},[-110,507,770,354],{'identity':[72,550],'captured_edge':[510,824]},['agent-assisted:job-brief-strip-artwork'])]
for name,states,box,anchors,ids in assets:
 sources={}
 for state,body in states.items():
  file=out/(name+'-'+state+'.svg');file.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="'+ ' '.join(map(str,box))+f'" width="{box[2]}" height="{box[3]}"><defs>{defs}</defs><g id="{name}-{state}">{body}</g></svg>');sources[state]={'file':str(file.relative_to(ROOT)),'sha256':sha(file)}
 write(out/(name+'.json'),{'id':name+'-concept-v1','name':name.replace('-',' '),'category':'computing','subcategory':'production-concept','concepts':['connection','assigned-work'],'keywords':[name,'paper'],'style':'reference-expressive-v1','orientation':'front','dimensions':{'width':box[2],'height':box[3],'unit':'px'},'artBox':dict(zip(['x','y','width','height'],box)),'anchors':{k:{'x':(v[0]-box[0])/box[2],'y':(v[1]-box[1])/box[3]} for k,v in anchors.items()},'compatibleCharacters':['motif-bot'],'supportedActions':['static-contact-proof'],'sourceType':'vector','source':sources,'version':1,'status':'review','license':'project-original','required_capability_ids':ids,'development':'Agent-assisted static SVG artwork only. No motion, mask/feed adapter or runtime registration implemented. Dot and job identity primitives reused unchanged. External references supply no pixels.'})
write(p/'capability-resolution.json',{'scope':'Concept only','artwork':'3 production-scoped review families','choreography_implemented':False,'canonical_changes':False,'motion':'Not authorized; contact/masking/feed adapters remain development proposals','reused_identity':['canonical Motif Bot in eight byte-preserved previews','existing Dot token','existing cream/raised-corner/teal-notch brief','approved Motif paper material'],'source_sha256':{str(f.relative_to(ROOT)):sha(f) for f in (p/'source').glob('*.py')}})
