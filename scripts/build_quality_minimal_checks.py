#!/usr/bin/env python3
"""Minimal/quiet versus dead-hold fixtures with nullable energy channels."""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import build_quality_hardening_fixtures as base
from motif_ui_components import rect,g,card,txt,path,bot,plant,INK,CREAM
from motif_quality import read,write,sha
P=ROOT/'quality/validation/v1.1/minimal'
def frame(number,f,headline,seed,transition=False):
 if number==2:f=0
 y=780-105*min(1,f/30);x=400
 b=rect(0,0,720,1280,'#BFA783')+g(rect(0,0,720,1280,'url(#worldPaper)'),opacity=.19)
 b+='<ellipse cx="205" cy="978" rx="117" ry="18" fill="#211923" opacity=".14"/>'
 b+=plant(618,934,f,.5)+bot(205,963,f,s=.43,jitter=False,contact=(x,y))
 paper=g(card(230,162,'#CBBEAA'),3,7)+g(card(230,162,'#E5D5B9'),1,3)+card(230,162)
 paper+=txt('SOURCE',111,51,32,INK,900,'middle')+path('M25 80H194M25 107H162M25 133H184','#A79C88',6)
 # One folded corner provides a physical silhouette and layer separation.
 paper+=path('M198 1L230 31L198 34Z','#CBBEAA',1,'#D8C6A5')+path('M198 1L230 31L202 27Z','#D9CBB1',1,'#FAF3DF')
 b+=g(paper,x,y-81)
 return g(b,0,-190)
def build():
 base.P=P;base.frame=frame;base.build()
 plan=read(P/'production-plan.json')
 for s in plan['shots']:
  q=s['quality'];q.update(purpose='Raise the folded source sheet, then pause briefly so the viewer can inspect its paper layers and maintained grip',hero='folded source sheet',primary_action='Lift folded source sheet into view',before='Sheet held at the lower position',after='Sheet raised for a brief deliberate inspection',environment=[],secondary_motion=[],exit_overlap=None)
  q['energy']={'dominant_action':'Raise the sheet, then allow one second to inspect the fold and grip','character_response':None,'local_reaction':None,'residual_motion':None,'next_action_overlap':None}
  q['art_direction'].update(hero_object='folded source sheet',materials=['layered printed paper','matte warm field'],depth_planes=['quiet paper field','grounding contact shadow','Bot and folded sheet'],environment_mode='minimal-isolated',environment_justification='Isolate the hand, folded sheet and readable lift at phone size; room dressing would distract from inspecting the grip',composition='Enlarged elevated Bot-sheet cluster with open upper caption area',intentional_irregularity='three offset paper layers and one raised folded corner')
 plan['asset_usage'][0]['path']='scripts/build_quality_minimal_checks.py';write(P/'production-plan.json',plan)
 write(P/'expected.json',{'withheld_from_critics':True,'minimal_control':'t01','dead_hold':'t02','expected_dead_hold_gate':'energy','optional_channels':None})
 write(P/'provenance.json',{'scope':'isolated minimal/quiet and dead-hold regressions; not a new film','agent_assisted':'one folded-paper fixture using existing components; canonical Bot unchanged','source_sha256':sha(Path(__file__))})
if __name__=='__main__':build()
