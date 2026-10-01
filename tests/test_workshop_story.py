"""State-order and concurrency safeguards for the new physical workflow."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from motif_plan import review_plan
from motif_workshop import perform

class WorkshopStoryTests(unittest.TestCase):
    def test_assembly_cannot_skip_the_independent_jobs(self):
        folder=ROOT/'videos/productions/little-book-workshop'
        plan=json.loads((folder/'initial-plan.json').read_text())
        brief=json.loads((folder/'brief.json').read_text())
        self.assertTrue(review_plan(plan,brief)['pass'])
        invalid=copy.deepcopy(plan)
        invalid['beats'][1],invalid['beats'][2]=invalid['beats'][2],invalid['beats'][1]
        report=review_plan(invalid,brief)
        self.assertFalse(report['pass'])
        self.assertTrue(any('requires' in i for i in report['issues']))

    def test_three_jobs_have_common_active_time_and_same_pieces_are_delivered(self):
        events=[];sfx=[]
        emit=lambda t,id_,action,**p:events.append({'time':t,'target':id_,'action':action,'params':p})
        _,detail=perform('workshop.work_parallel',3,8,emit,sfx)
        windows=list(detail['simultaneous_job_windows'].values())
        overlap=min(w[1] for w in windows)-max(w[0] for w in windows)
        self.assertGreater(overlap,1)
        targets={e['target'] for e in events}
        self.assertTrue({'cover-flap','press-plate','binding-shape'}<=targets)
        constituents=detail['constituent_ids']
        for kind in ('workshop.dispatch','workshop.assemble','workshop.deliver'):
            events.clear();_,next_detail=perform(kind,0,5,emit,sfx)
            self.assertEqual(constituents,next_detail['constituent_ids'])
        self.assertTrue(any(e['target']=='book-carrier' for e in events))
        self.assertFalse(any('finished-book' in e['target'] for e in events))

if __name__=='__main__':unittest.main()
