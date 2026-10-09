"""Regressions for the audited pixel-binding gaps, using saved speech data."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from motif_plan import ROOT, ASSETS, review_plan
from motif_plan_compile import compile_plan
from motif_framing import camera_for, contains, SAFE


def upgraded(slug):
    folder=ROOT/'videos/productions'/slug
    plan=json.loads((folder/'production-plan.json').read_text())
    plan['schema_version']='1.1'
    for beat in plan['beats']:
        beat['headline_mode']='set' if beat['headline'] else 'clear'
        shot=beat['shot']
        target={'arena-pair':'arena.answers','arena-a':'answer-A.connection','arena-b':'answer-B.connection','arena-review':'arena.handoff','calendar-wide':'calendar.board','calendar-detail':'calendar.proposal'}[shot]
        for action in beat['actions']:
            if action['kind'] in ('calendar.approve','calendar.decline'): target='calendar.decision'
        beat['focus_target']=target
        beat['framing']='detail' if shot in ('arena-a','arena-b') else 'subject'
    return folder,plan


def compile_saved(folder,plan,dest):
    from motif_evidence import declare
    (dest/'brief.json').write_text('{"scope":"legacy unit fixture"}')
    declare(dest,'technical-fixture','unit.compile_saved')
    words=json.loads((folder/'assets/voice/transcript.json').read_text())
    voice=json.loads((folder/'audio-plan.json').read_text())['tracks'][0]['duration']
    compile_plan(dest,plan,words,voice,[10,22])
    return json.loads((dest/'scene-events.json').read_text())


class DirectingTests(unittest.TestCase):
    def test_one_framing_field_changes_camera_with_same_assets_and_speech(self):
        folder,plan=upgraded('planned-arena-no-winner')
        other=copy.deepcopy(plan); other['beats'][1]['framing']='subject'
        with tempfile.TemporaryDirectory() as tmp:
            a=Path(tmp)/'a'; b=Path(tmp)/'b'; a.mkdir(); b.mkdir()
            left=compile_saved(folder,plan,a); right=compile_saved(folder,other,b)
            self.assertNotEqual(left,right)
            self.assertEqual(left['captions'],right['captions'])
            self.assertEqual((a/'audio-plan.json').read_bytes(),(b/'audio-plan.json').read_bytes())
            changes=[(x,y) for x,y in zip(left['events'],right['events'],strict=True) if x!=y]
            self.assertEqual(len(changes),1)
            self.assertEqual(changes[0][0]['target'],'#camera-arena-a')

    def test_A_B_diagnostic_fits_match_and_protect_identity_and_marks(self):
        _,plan=upgraded('planned-arena-no-winner')
        a=camera_for(plan['beats'][1],ASSETS); b=camera_for(plan['beats'][2],ASSETS)
        self.assertEqual(a['camera'],b['camera'])
        self.assertEqual(a['projected_target_bounds'],b['projected_target_bounds'])
        self.assertTrue(contains(SAFE,a['projected_critical_bounds']))
        self.assertGreater(a['projected_target_bounds'][2],760) # enlarged actual diagnostic, not entire sheet

    def test_decline_clears_PROPOSED_without_editing_old_export(self):
        folder,plan=upgraded('planned-calendar-declined')
        plan['beats'][2]['headline_mode']='clear'
        with tempfile.TemporaryDirectory() as tmp:
            spec=compile_saved(folder,plan,Path(tmp))
            labels=json.loads((Path(tmp)/'label-timing.json').read_text())
            clears=[e for e in spec['events'] if e['target']=='#headline-1' and e['action']=='SET' and e['params']['props'].get('opacity')==0]
            self.assertIn(labels[2]['caption_start'],[e['time'] for e in clears])
            self.assertLess(labels[2]['caption_start'],7.99)
        plan['beats'][2]['headline_mode']='keep'
        brief=json.loads((folder/'brief.json').read_text())
        self.assertIn('state action cannot keep a previous headline',review_plan(plan,brief)['issues'])

    def test_selection_subject_changes_attached_stamp_events(self):
        folder,plan=upgraded('planned-arena-no-winner')
        for beat in plan['beats']:
            for action in beat['actions']:
                if action['kind']=='arena.check': action['result']='pass'
        ending=plan['beats'][-1]
        ending.update(shot='arena-pair',focus_target='arena.answers',framing='detail')
        action=ending['actions'][0]; action.update(kind='arena.select',subject='A',requires=['A-pass'])
        other=copy.deepcopy(plan); other['beats'][-1]['actions'][0].update(subject='B',requires=['B-pass'])
        with tempfile.TemporaryDirectory() as tmp:
            a=Path(tmp)/'a'; b=Path(tmp)/'b'; a.mkdir(); b.mkdir()
            left=compile_saved(folder,plan,a); right=compile_saved(folder,other,b)
            bindings=lambda spec:[e['target'] for e in spec['events'] if e['target'].endswith('-selected')]
            self.assertEqual(bindings(left),['#pair-A-selected','#close-A-selected','#review-A-selected'])
            self.assertEqual(bindings(right),['#pair-B-selected','#close-B-selected','#review-B-selected'])
            self.assertEqual([e for e in left['events'] if not e['target'].endswith('-selected')],[e for e in right['events'] if not e['target'].endswith('-selected')])

    def test_hidden_selection_and_freeform_focus_are_rejected(self):
        _,plan=upgraded('planned-arena-no-winner')
        with self.assertRaisesRegex(ValueError,'hidden'):
            camera_for(plan['beats'][1],ASSETS,'B')
        beat=copy.deepcopy(plan['beats'][1]); beat['focus_target']='#anything'
        with self.assertRaisesRegex(ValueError,'unsupported focus'):
            camera_for(beat,ASSETS)

    def test_stage_instruction_narration_is_not_accepted_as_audience_script(self):
        folder,plan=upgraded('planned-arena-no-winner')
        brief=json.loads((folder/'brief.json').read_text())
        self.assertTrue(any('audience narration' in issue for issue in review_plan(plan,brief)['issues']))


if __name__=='__main__': unittest.main()
