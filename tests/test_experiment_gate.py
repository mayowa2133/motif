"""Synthetic state-machine fixtures only. These are not research/perception results."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from motif_experiment_gate import (GUARDS, load, digest, plan_trial, assess_trial,
                                   apply_decision, verify_ref)


class GateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.policy = load(ROOT/'quality/experiment-gate/criteria.json')
        self.original = self.file('original.txt', 'synthetic baseline')
        self.brief = self.file('brief.txt', 'synthetic brief')
        self.research = self.file('research.txt', 'synthetic research, not real observations')
        self.components = {k: self.file(k+'.txt', 'synthetic component '+k) for k in ['A','B']}
        def candidate(k):
            return {'id':k,'optional':True,'verdict':'positive','evidence_scope':'synthetic unit fixture',
                    'baseline_sha256':self.original['sha256'],'artifact_sha256':self.original['sha256'],
                    'component_sha256':self.components[k]['sha256'],'known_regressions':[],
                    'dependencies':[],'effect_domains':[],'rollback_target':{'artifact_sha256':self.original['sha256']},
                    'evidence':[self.research],'eligible_scopes':list(self.policy['scopes'])}
        self.registry = {'schema_version':1,'candidates':[candidate('A'),candidate('B')]}
        self.context = {'brief_sha256':self.brief['sha256'],'baseline_artifact_sha256':self.original['sha256'],
                        'baseline_git_commit':'a'*40,'scope':'production','claims':['static_visibility'],
                        'artifact_type':'encoded_av',
                        'events':{'release':{'baseline':[3,5],'trial':[3,5]}}}
        self.state = {'last_good':{'artifact_sha256':self.original['sha256'],'enabled':[]},'history':[]}

    def file(self, name, content):
        path = self.root/name
        path.write_text(content)
        return {'path':name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}

    def trial(self, addition='A', state=None):
        state = state or self.state
        return plan_trial(self.registry,self.policy,self.context,state['last_good'],[addition],
                          state.get('blocked_combinations',[]))

    def result(self, trial, output=None):
        output = output or self.file('output-'+trial['addition']+'.txt', 'synthetic output '+trial['addition'])
        previous = next(r for r in [self.original,*[self.ref(p) for p in self.root.glob('output-*.txt')]]
                        if r['sha256']==trial['previous']['artifact_sha256'])
        comparisons=[]
        for index, target in enumerate(sorted({self.original['sha256'],previous['sha256']})):
            checks={k:{'result':'unchanged','kind':'phone_stills','observation':'synthetic unit observation'} for k in GUARDS}
            checks['clarity']['result']='improved'
            checks['technical_reliability']['kind']='execution_checks'
            checks['contact']['kind']='continuous_event_interval' if self.context['scope']=='production' else 'phone_stills'
            comparisons.append({'against_sha256':target,'checks':checks})
        result={'trial_sha256':digest(trial),'artifacts':{'brief':self.brief,'original':self.original,
                'previous':previous,'trial':output,'components':self.components},
                'research_evidence':{self.research['sha256']:self.research},'comparisons':comparisons}
        self.bind_reports(result)
        return result

    def ref(self,path):
        return {'path':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}

    def bind_reports(self,result, coverage=None):
        for i,c in enumerate(result['comparisons']):
            for check in c['checks'].values(): check.pop('report',None)
            report={'trial_sha256':result['trial_sha256'],'against_sha256':c['against_sha256'],
                    'trial_artifact_sha256':result['artifacts']['trial']['sha256'],
                    'criteria':copy.deepcopy(c['checks'])}
            if c['checks']['contact'].get('result') in {'improved','unchanged'}:
                report['event_coverage']={event:{'complete_review':True,
                    'baseline_artifact_sha256':c['against_sha256'],
                    'trial_artifact_sha256':result['artifacts']['trial']['sha256'],
                    'baseline_frame_indices':list(range(bounds['baseline'][0],bounds['baseline'][1]+1)),
                    'trial_frame_indices':list(range(bounds['trial'][0],bounds['trial'][1]+1))}
                    for event,bounds in self.context['events'].items()}
            if coverage: report.update(coverage)
            reference=self.file('review-'+str(i)+'.json',json.dumps(report,sort_keys=True))
            for check in c['checks'].values(): check['report']=reference

    def assess(self,t,r):
        return assess_trial(self.registry,self.policy,t,r,self.root)

    def regress(self,result, against=None, criterion='contact'):
        comparison=next(c for c in result['comparisons'] if against is None or c['against_sha256']==against)
        check=comparison['checks'][criterion]
        check.update(result='regressed',reproduced=True,finding_type='observed')
        self.bind_reports(result)
        return check

    def test_default_current_behavior_unchanged(self):
        p=plan_trial(self.registry,self.policy,self.context)
        self.assertFalse(p['ready']);self.assertEqual(p['enabled'],[])

    def test_positive_complete_evidence(self):
        t=self.trial(); d=self.assess(t,self.result(t))
        self.assertEqual(d['action'],'accept_in_trial');self.assertTrue(d['promotion_ready'])

    def test_all_verdict_states(self):
        for verdict in ['negative','inconclusive','unassessed']:
            self.registry['candidates'][0]['verdict']=verdict
            self.assertFalse(self.trial()['ready'])

    def test_missing_candidate_evidence_hash_and_artifact_reject(self):
        for field in ['baseline_sha256','artifact_sha256','component_sha256']:
            original=self.registry['candidates'][0][field]
            self.registry['candidates'][0][field]=None
            self.assertFalse(self.trial()['ready'])
            self.registry['candidates'][0][field]=original
        self.registry['candidates'][0]['evidence']=[]
        self.assertFalse(self.trial()['ready'])

    def test_scope_and_known_regression_block(self):
        c=self.registry['candidates'][0];c['eligible_scopes']=['visibility_only']
        self.assertFalse(self.trial()['ready'])
        c['eligible_scopes']=['production'];c['known_regressions']=[{'scopes':['production']}]
        self.assertFalse(self.trial()['ready'])

    def test_dependencies_and_multiple_additions(self):
        self.registry['candidates'][0]['dependencies']=['B']
        self.assertFalse(self.trial()['ready'])
        self.assertFalse(plan_trial(self.registry,self.policy,self.context,requested=['A','B'])['ready'])

    def test_missing_brief_and_baseline_reject(self):
        for field in ['brief_sha256','baseline_artifact_sha256','baseline_git_commit']:
            context=copy.deepcopy(self.context);context[field]=None
            if field=='baseline_git_commit':context[field]=''
            self.assertFalse(plan_trial(self.registry,self.policy,context,requested=['A'])['ready'])

    def test_missing_review_evidence_holds(self):
        t=self.trial();r=self.result(t);r['comparisons'][0]['checks']['contact'].pop('report')
        self.assertEqual(self.assess(t,r)['verdict'],'unassessed')

    def test_changed_artifact_holds(self):
        t=self.trial();r=self.result(t);(self.root/r['artifacts']['trial']['path']).write_text('changed')
        self.assertEqual(self.assess(t,r)['action'],'hold')

    def test_wrong_pair_report_holds(self):
        t=self.trial();r=self.result(t);p=self.root/r['comparisons'][0]['checks']['contact']['report']['path']
        report=load(p);report['against_sha256']='f'*64;p.write_text(json.dumps(report))
        for check in r['comparisons'][0]['checks'].values():check['report']=self.ref(p)
        self.assertEqual(self.assess(t,r)['verdict'],'unassessed')

    def test_trial_criteria_registry_binding(self):
        t=self.trial();r=self.result(t);self.policy['rules'].append('changed after freeze')
        self.assertEqual(self.assess(t,r)['action'],'hold')
        self.policy['rules'].pop();self.registry['extra']='changed after freeze'
        self.assertEqual(self.assess(t,r)['action'],'hold')

    def test_forged_ready_and_enabled_reject(self):
        t=self.trial();t['enabled'].append({'id':'B','component_sha256':self.components['B']['sha256']})
        r=self.result(t);self.assertEqual(self.assess(t,r)['action'],'hold')

    def test_tie_and_inconclusive_are_no_promotion(self):
        t=self.trial();r=self.result(t)
        r['comparisons'][0]['checks']['clarity']['result']='unchanged';self.bind_reports(r)
        self.assertEqual(self.assess(t,r)['verdict'],'inconclusive')
        r['comparisons'][0]['checks']['clarity']['result']='inconclusive';self.bind_reports(r)
        self.assertEqual(self.assess(t,r)['verdict'],'inconclusive')

    def test_one_reproducible_hard_regression_rolls_back(self):
        t=self.trial();r=self.result(t);self.regress(r)
        # Multiple improved checks cannot offset a hard failure.
        d=self.assess(t,r);self.assertEqual(d['action'],'rollback')
        self.assertEqual(apply_decision(self.state,t,r,d)['active'],self.state['last_good'])

    def test_unreproduced_or_disputed_regression_inconclusive(self):
        t=self.trial();r=self.result(t);check=self.regress(r)
        check['reproduced']=False;self.bind_reports(r)
        self.assertEqual(self.assess(t,r)['verdict'],'inconclusive')
        check['reproduced']=True;check['reviewer_disagreement']=True;self.bind_reports(r)
        self.assertEqual(self.assess(t,r)['verdict'],'inconclusive')

    def test_absence_requires_complete_event_review(self):
        t=self.trial();r=self.result(t);check=self.regress(r)
        check['absence_event']='release';check['finding_type']='absence';check['kind']='continuous_event_interval';self.bind_reports(r)
        self.assertEqual(self.assess(t,r)['verdict'],'inconclusive')
        coverage={'complete_review':True,'baseline_artifact_sha256':self.original['sha256'],
                  'baseline_frame_indices':[3,5],'trial_frame_indices':[3,4,5]}
        self.bind_reports(r,coverage);self.assertEqual(self.assess(t,r)['verdict'],'inconclusive')
        coverage['baseline_frame_indices']=[3,4,5];self.bind_reports(r,coverage)
        self.assertEqual(self.assess(t,r)['action'],'rollback')

    def test_combination_regression_preserves_A_and_scopes_B(self):
        a=self.trial();ra=self.result(a);accepted=apply_decision(self.state,a,ra,self.assess(a,ra))
        b=self.trial('B',accepted);rb=self.result(b)
        self.regress(rb,accepted['last_good']['artifact_sha256'])
        d=self.assess(b,rb);rolled=apply_decision(accepted,b,rb,d)
        self.assertEqual(rolled['active'],accepted['last_good'])
        self.assertEqual([v['id'] for v in rolled['active']['enabled']],['A'])
        self.assertEqual(self.registry['candidates'][1]['verdict'],'positive')
        self.assertFalse(self.trial('B',rolled)['ready'])
        self.context['brief_sha256']='f'*64
        self.assertTrue(self.trial('B',rolled)['ready'])

    def test_combination_needs_both_comparisons_and_incremental_gain(self):
        a=self.trial();ra=self.result(a);state=apply_decision(self.state,a,ra,self.assess(a,ra))
        b=self.trial('B',state);rb=self.result(b)
        self.assertEqual(len(rb['comparisons']),2)
        rb['comparisons'].pop();self.assertEqual(self.assess(b,rb)['action'],'hold')
        rb=self.result(b)
        for check in rb['comparisons'][0]['checks'].values():check['result']='unchanged'
        self.bind_reports(rb);self.assertEqual(self.assess(b,rb)['action'],'hold')

    def test_single_hard_failure_blocks_even_if_other_comparison_missing(self):
        a=self.trial();ra=self.result(a);state=apply_decision(self.state,a,ra,self.assess(a,ra))
        b=self.trial('B',state);rb=self.result(b)
        rb['comparisons']=[c for c in rb['comparisons'] if c['against_sha256']==state['last_good']['artifact_sha256']]
        self.regress(rb);self.assertEqual(self.assess(b,rb)['action'],'rollback')

    def test_motion_claim_needs_real_playback_report(self):
        self.context['claims']=['motion'];t=self.trial();r=self.result(t)
        self.assertEqual(self.assess(t,r)['verdict'],'unassessed')
        report={'full_speed_picture_watched':True,'audio_listened':True,
                'trial_sha256':digest(t),
                'artifact_sha256':[self.original['sha256'],r['artifacts']['trial']['sha256']]}
        r['playback']={'report':self.file('playback.json',json.dumps(report))}
        self.assertEqual(self.assess(t,r)['action'],'accept_in_trial')

    def test_source_only_not_promotion_ready(self):
        self.context['scope']='source_only';t=self.trial();r=self.result(t)
        d=self.assess(t,r);self.assertEqual(d['action'],'accept_in_trial');self.assertFalse(d['promotion_ready'])

    def test_review_cannot_be_reused_after_brief_claims_or_events_change(self):
        for changed in ['brief','claims','events']:
            with self.subTest(changed=changed):
                old_context=copy.deepcopy(self.context);old_brief=self.brief
                original_trial=self.trial();result=self.result(original_trial)
                if changed=='brief':
                    self.brief=self.file('different-brief.txt','a different synthetic task')
                    self.context['brief_sha256']=self.brief['sha256']
                elif changed=='claims':self.context['claims']=['reliability']
                else:self.context['events']['release']={'baseline':[4,6],'trial':[4,6]}
                new_trial=self.trial()
                result['trial_sha256']=digest(new_trial)
                result['artifacts']['brief']=self.brief
                decision=self.assess(new_trial,result)
                self.assertEqual(decision['action'],'hold')
                self.assertTrue(any('frozen trial' in reason for reason in decision['reasons']))
                self.context=old_context;self.brief=old_brief

    def test_playback_report_must_bind_the_frozen_trial(self):
        self.context['claims']=['motion'];old_trial=self.trial();old_result=self.result(old_trial)
        report={'trial_sha256':digest(old_trial),'full_speed_picture_watched':True,'audio_listened':True,
                'artifact_sha256':[self.original['sha256'],old_result['artifacts']['trial']['sha256']]}
        playback={'report':self.file('old-playback.json',json.dumps(report))}
        self.brief=self.file('new-motion-brief.txt','different motion task')
        self.context['brief_sha256']=self.brief['sha256']
        new_trial=self.trial();new_result=self.result(new_trial)
        new_result['playback']=playback
        self.assertEqual(self.assess(new_trial,new_result)['action'],'hold')

    def test_accepted_state_is_isolated_from_mutable_caller_objects(self):
        trial=self.trial();result=self.result(trial);decision=self.assess(trial,result)
        state=apply_decision(self.state,trial,result,decision);frozen=copy.deepcopy(state)
        trial['enabled'][0]['component_sha256']='f'*64
        trial['previous']['artifact_sha256']='e'*64
        result['artifacts']['trial']['sha256']='d'*64
        decision['reasons'].append('changed caller object')
        self.assertEqual(state,frozen)

    def test_rollback_history_and_block_are_isolated_from_caller_objects(self):
        trial=self.trial();result=self.result(trial);self.regress(result)
        decision=self.assess(trial,result)
        state=apply_decision(self.state,trial,result,decision);frozen=copy.deepcopy(state)
        decision['regressions'][0]['observation']='changed caller finding'
        trial['enabled'][0]['component_sha256']='f'*64
        result['artifacts']['trial']['sha256']='e'*64
        self.assertEqual(state,frozen)

    def test_output_preserving_technical_refactor(self):
        self.context.update(scope='output_preserving_refactor',claims=['output_preserving_refactor','reliability'])
        t=self.trial();r=self.result(t,self.original)
        for k,check in r['comparisons'][0]['checks'].items():
            check.update(result='unchanged',kind='byte_identity')
        r['comparisons'][0]['checks']['technical_reliability'].update(result='improved',kind='execution_checks')
        self.bind_reports(r);self.assertEqual(self.assess(t,r)['action'],'accept_in_trial')

    def test_source_identity_cannot_pass_visual_guards(self):
        self.context.update(scope='output_preserving_refactor',claims=['reliability'],artifact_type='source_state')
        t=self.trial();r=self.result(t,self.original)
        for check in r['comparisons'][0]['checks'].values():check.update(result='unchanged',kind='byte_identity')
        r['comparisons'][0]['checks']['technical_reliability'].update(result='improved',kind='execution_checks')
        self.bind_reports(r);self.assertEqual(self.assess(t,r)['verdict'],'unassessed')

    def test_candidate_motion_effect_requires_declared_scope(self):
        self.registry['candidates'][0]['effect_domains']=['motion']
        self.assertFalse(self.trial()['ready'])

    def test_prior_candidate_cannot_expand_scope(self):
        self.registry['candidates'][0]['eligible_scopes']=['visibility_only']
        self.context['scope']='visibility_only';a=self.trial();ra=self.result(a)
        state=apply_decision(self.state,a,ra,self.assess(a,ra))
        self.context['scope']='production'
        self.assertFalse(self.trial('B',state)['ready'])

    def test_untyped_regression_does_not_bypass_absence_rule(self):
        t=self.trial();r=self.result(t);check=self.regress(r)
        check.pop('finding_type');self.bind_reports(r)
        self.assertEqual(self.assess(t,r)['verdict'],'inconclusive')

    def test_supporting_evidence_staleness_blocks(self):
        t=self.trial();r=self.result(t)
        reference=self.file('support.json','synthetic supplementary observation')
        r['comparisons'][0]['checks']['clarity']['supporting_evidence']=[reference]
        self.bind_reports(r);(self.root/reference['path']).write_text('changed')
        self.assertEqual(self.assess(t,r)['verdict'],'unassessed')

    def test_contact_stills_cannot_clear_production_continuity(self):
        t=self.trial();r=self.result(t)
        r['comparisons'][0]['checks']['contact']['kind']='phone_stills';self.bind_reports(r)
        self.assertEqual(self.assess(t,r)['verdict'],'unassessed')

    def test_reproducible_decisions_and_idempotent_history(self):
        t=self.trial();r=self.result(t);d=self.assess(t,r)
        self.assertEqual(d,self.assess(t,copy.deepcopy(r)))
        self.assertEqual(t,self.trial())
        state=apply_decision(self.state,t,r,d)
        self.assertEqual(state,apply_decision(state,t,r,d))
        state['last_good']['artifact_sha256']='e'*64
        with self.assertRaises(ValueError):apply_decision(state,t,r,{**d,'reasons':['different']})

    def test_json_roundtrip_preserves_decision_and_log(self):
        t=self.trial();r=self.result(t)
        for check in r['comparisons'][0]['checks'].values():check['result']='unassessed'
        self.bind_reports(r);decision=self.assess(t,r)
        decoded=json.loads(json.dumps(r,sort_keys=True))
        self.assertEqual(decision,self.assess(t,decoded))
        self.assertEqual(apply_decision(self.state,t,r,decision),apply_decision(self.state,t,decoded,decision))

    def test_escape_and_symlink_evidence_rejected(self):
        with self.assertRaises(ValueError):verify_ref(self.root,{'path':'../escaped','sha256':'a'*64})
        (self.root/'escape').symlink_to('/etc/hosts')
        with self.assertRaises(ValueError):verify_ref(self.root,{'path':'escape','sha256':'a'*64})

    def test_current_registry_only_frozen_kit_source_scope_ready(self):
        current=load(ROOT/'quality/experiment-gate/registry.json')
        from motif_experiment_gate import eligibility
        ready=[c['id'] for c in current['candidates'] if not eligibility(c,'source_only')]
        self.assertEqual(ready,['frontal-kit-v012'])
        self.assertFalse(any(not eligibility(c,'production') for c in current['candidates']))

    def test_catalog_defaults_preserve_the_previous_accepted_version(self):
        current=load(ROOT/'quality/experiment-gate/registry.json')
        self.assertEqual(current['default_enabled'],[])
        self.assertIs(current['art_promotion'],False)
        kit=next(c for c in current['candidates'] if c['id']=='frontal-kit-v012')
        previous={'artifact_sha256':self.original['sha256'],
                  'enabled':[{'id':kit['id'],'component_sha256':kit['component_sha256']}]}
        context={**self.context,'scope':'source_only','claims':['reliability']}
        planned=plan_trial(current,self.policy,context,previous)
        self.assertEqual(planned['previous'],previous)
        self.assertEqual(planned['enabled'],previous['enabled'])
        self.assertIsNone(planned['addition']);self.assertFalse(planned['ready'])
        self.assertEqual(planned['rejections'],[])

    def test_catalog_preserves_disputed_transfer_negative_without_promotion(self):
        current=load(ROOT/'quality/experiment-gate/registry.json')
        candidate=next(c for c in current['candidates'] if c['id']=='visual-keypose-gate-method')
        self.assertEqual(candidate['verdict'],'inconclusive')
        self.assertEqual(candidate['eligible_scopes'],[])
        self.assertEqual(candidate['known_regressions'],[])
        self.assertTrue(candidate['disputed_regressions'][0]['reviewer_disagreement'])
        self.assertFalse(candidate['disputed_regressions'][0]['hard_regression'])
        self.assertEqual([f['verdict'] for f in candidate['scoped_findings']],['positive','inconclusive'])
        for scope in self.policy['scopes']:
            context={**self.context,'scope':scope}
            trial=plan_trial(current,self.policy,context,requested=[candidate['id']])
            self.assertFalse(trial['ready']);self.assertEqual(trial['enabled'],[])


if __name__=='__main__':
    unittest.main()
