"""State contradictions, capability failures and plan consumption before evaluation."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from motif_plan import WORLD_ASSETS, review_plan, narration, tokens
from motif_plan_compile import compile_plan, align


def fixture():
    message='An assistant proposes a reading hour and a person approves it.'
    brief={'slug':'development-approved-reading','message':message,'audience':'General viewers','intended_duration_seconds':16,'duration_tolerance_seconds':3}
    sentences=['A reading hour is free this afternoon.','The assistant proposes a quiet reading session.','A person approves the proposed reading hour.','The approved session joins the calendar now.']
    kinds=[[],[{'kind':'calendar.propose','subject':'calendar','cue':'proposes','result':'none','requires':[]}],[{'kind':'calendar.approve','subject':'calendar','cue':'approves','result':'none','requires':['proposal-visible']}],[{'kind':'calendar.commit','subject':'calendar','cue':'joins','result':'none','requires':['approved']}]]
    beats=[{'id':f'beat-{i}','subject':'calendar and person','action':'A card changes state through a human decision','before_after':'pending becomes decided','focal_detail':'card and human hand','consequence':'session added only after approval','narration':s,'caption':['An hour is free','A reading proposal','The person approves','Added after approval'][i],'headline':['OPEN HOUR','PROPOSED','YOUR DECISION',''][i],'shot':'calendar-wide' if i==0 else 'calendar-detail','actions':kinds[i]} for i,s in enumerate(sentences)]
    for i,b in enumerate(beats):
        b['focus_target']=['calendar.board','calendar.proposal','calendar.decision','calendar.booking'][i]
        b['framing']='establish' if i==0 else 'subject'
        b['headline_mode']='set' if b['headline'] else 'clear'
    plan={'schema_version':'1.1','status':'ready','capability_error':'','message':message,'audience':brief['audience'],'claims':['Illustrative approval workflow'],'illustrative_assumptions':['Reading at 4 PM, MEET at 3 PM'],'environment':'calendar','assets':WORLD_ASSETS['calendar'],'asset_requests':[],'calendar':{'existing_title':'MEET','proposed_title':'READ'},'expected_final':{'calendar':'booked','A':'untested','B':'untested','winner':'none','handoff':False},'ending_action':'Approved reading card joins the calendar','beats':beats}
    return brief,plan

class PlanTests(unittest.TestCase):
    def test_booking_without_approval_rejected(self):
        brief,plan=fixture(); plan['beats'][2]['actions'][0]['kind']='calendar.decline'
        self.assertFalse(review_plan(plan,brief)['pass'])
        self.assertIn('booking requires human approval',review_plan(plan,brief)['issues'])

    def test_unsupported_action_and_assets_cannot_disappear(self):
        brief,plan=fixture(); plan['beats'][1]['actions'][0]['kind']='run_generated_code'
        self.assertFalse(review_plan(plan,brief)['pass'])
        brief,plan=fixture(); plan['asset_requests']=['new cinematic machine']; self.assertFalse(review_plan(plan,brief)['pass'])

    def test_final_state_and_message_must_match(self):
        brief,plan=fixture(); plan['expected_final']['calendar']='unchanged'; self.assertFalse(review_plan(plan,brief)['pass'])
        brief,plan=fixture(); plan['message']='A different meaning'; self.assertFalse(review_plan(plan,brief)['pass'])

    def test_plan_content_reaches_compiled_scene(self):
        brief,plan=fixture(); self.assertTrue(review_plan(plan,brief)['pass'])
        words=[{'text':word,'start':i*.45+.05,'end':i*.45+.4} for i,word in enumerate(tokens(narration(plan)))]
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            from motif_evidence import declare
            (root/'brief.json').write_text('{"scope":"legacy unit fixture"}')
            declare(root,'technical-fixture','unit.production_plan')
            compile_plan(root,plan,words,len(words)*.45+.5,[10,22])
            html=(root/'index.html').read_text(); spec=json.loads((root/'scene-events.json').read_text())
            self.assertIn('READ',html); self.assertNotIn('FOCUS',html)
            self.assertIn('The person approves',html)
            self.assertEqual(spec['captions'][2]['start'],words[14]['start'])
            trace=json.loads((root/'action-trace.json').read_text())
            self.assertEqual([a['kind'] for a in trace],['calendar.propose','calendar.approve','calendar.commit'])
            self.assertEqual(trace[1]['cue_time'],words[16]['start'])

    def test_merged_asr_words_keep_measured_boundaries(self):
        _,plan=fixture()
        for beat,sentence in zip(plan['beats'],['Two answers.','A cross appears.','B takes a sheet.','Both need review.']):
            beat['narration']=sentence; beat['actions']=[]
        plan['beats'][2]['actions']=[{'kind':'bot.pose','subject':'bot','cue':'takes','result':'thinking','requires':[]}]
        words=[{'text':word,'start':i*.4,'end':i*.4+.35} for i,word in enumerate(['Two','answers','across','appears','Btakes','a','sheet','Both','need','review'])]
        spans,record=align(plan,words)
        self.assertEqual(record['coverage'],1)
        self.assertEqual(len(record['merged_token_groups']),2)
        self.assertEqual(spans[2]['start'],words[4]['start'])
        self.assertEqual(spans[2]['actions'][0]['time'],words[4]['start'])

    def test_failed_answer_cannot_win(self):
        brief,plan=fixture(); plan['environment']='arena'; plan['assets']=WORLD_ASSETS['arena']
        for beat in plan['beats']: beat['shot']='arena-a'; beat['actions']=[]
        plan['beats'][1]['actions']=[{'kind':'arena.check','subject':'A','result':'fail','cue':'proposes','requires':[]}]
        plan['beats'][2]['actions']=[{'kind':'arena.select','subject':'A','result':'none','cue':'approves','requires':['A-pass']}]
        self.assertIn('selection requires candidate pass',review_plan(plan,brief)['issues'])

if __name__=='__main__': unittest.main()
