import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from motif_custom_authoring import resolve_requirement,start_task,checkpoint
from motif_evidence import sha


class CustomAuthoringTests(unittest.TestCase):
    def test_capability_modes_and_explicit_custom_route(self):
        req={'id':'r','statement':'visible waiting','mode':'technical-fixture','capability':'waiting-1.0'}
        self.assertEqual(resolve_requirement(req)['route'],'registered-capability')
        req['mode']='original-film'
        with self.assertRaisesRegex(ValueError,'unsupported'):resolve_requirement(req)
        req['authoring_task']='approved-artwork-needed'
        self.assertEqual(resolve_requirement(req)['route'],'scoped-custom-authoring')
        self.assertEqual(resolve_requirement(req)['fulfillment'],'UNASSESSED')

    def test_returned_resolution_cannot_mutate_capability_policy(self):
        req={'id':'r','statement':'visible waiting','mode':'technical-fixture','capability':'waiting-1.0'}
        resolution=resolve_requirement(req);resolution['modes'].append('original-film')
        resolution['requirement']['mode']='original-film'
        self.assertEqual(req['mode'],'technical-fixture')
        req['mode']='original-film'
        with self.assertRaisesRegex(ValueError,'unsupported'):resolve_requirement(req)

    def test_resume_outputs_intervention_and_stale_input_failure(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'input.json').write_text('{}')
            spec={'requirement':{'id':'r','statement':'a novel non-tournament cause','mode':'original-film','authoring_task':'novel-scene'},
                  'inputs':[{'path':'input.json','sha256':sha(root/'input.json')}],
                  'expected_outputs':[{'path':'scene.json','kind':'native-composition'}]}
            start_task(root,spec)
            with self.assertRaisesRegex(ValueError,'exists'):start_task(root,spec)
            checkpoint(root,'BUILD',4,7,'manual geometry authoring')
            with self.assertRaisesRegex(ValueError,'missing'):checkpoint(root,'READY_FOR_SHARED_QA',1,2,'inspect outputs')
            (root/'scene.json').write_text(json.dumps({'native_ids':['worker']}))
            task=checkpoint(root,'READY_FOR_SHARED_QA',1,2,'build complete; shared QA pending')
            self.assertEqual(task['quality_status'],'UNASSESSED');self.assertEqual(len(task['history']),2)
            self.assertEqual(task['history'][-1]['outputs'][0]['sha256'],sha(root/'scene.json'))
            with self.assertRaisesRegex(ValueError,'backward'):checkpoint(root,'BUILD',1,1,'restart')
            (root/'input.json').write_text('{"changed":true}')
            with self.assertRaisesRegex(ValueError,'missing or changed'):checkpoint(root,'READY_FOR_SHARED_QA',1,1,'stale resume')

    def test_measurement_and_path_rejections(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'input.json').write_text('{}')
            spec={'requirement':{'id':'r','statement':'author scene','mode':'technical-fixture','authoring_task':'task'},
                  'inputs':[{'path':'input.json','sha256':sha(root/'input.json')}],
                  'expected_outputs':[{'path':'../escape.json','kind':'native-composition'}]}
            with self.assertRaisesRegex(ValueError,'relative'):start_task(root,spec)
            spec['expected_outputs'][0]['path']='scene.json';start_task(root,spec)
            for active,elapsed in [(True,1),(3,1),(float('nan'),1)]:
                with self.assertRaisesRegex(ValueError,'measured'):checkpoint(root,'BUILD',active,elapsed,'test')

    def test_bookkeeping_and_alias_cannot_be_declared_output(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'input.json').write_text('{}')
            spec={'requirement':{'id':'r','statement':'author scene','mode':'technical-fixture','authoring_task':'task'},
                  'inputs':[{'path':'input.json','sha256':sha(root/'input.json')}],
                  'expected_outputs':[{'path':'custom-authoring-task.json','kind':'native-composition'}]}
            with self.assertRaisesRegex(ValueError,'bookkeeping'):start_task(root,spec)
            (root/'alias.json').symlink_to(root/'custom-authoring-task.json')
            spec['expected_outputs'][0]['path']='alias.json'
            with self.assertRaisesRegex(ValueError,'bookkeeping'):start_task(root,spec)
            spec['expected_outputs'][0]['path']='scene.json';start_task(root,spec)
            os.link(root/'custom-authoring-task.json',root/'scene.json')
            with self.assertRaisesRegex(ValueError,'bookkeeping'):checkpoint(root,'READY_FOR_SHARED_QA',0,0,'test')

    def test_dangling_bookkeeping_symlink_cannot_write_outside_root(self):
        with tempfile.TemporaryDirectory() as d:
            base=Path(d);root=base/'project';root.mkdir();(root/'input.json').write_text('{}')
            outside=base/'outside.json';(root/'custom-authoring-task.json').symlink_to(outside)
            spec={'requirement':{'id':'r','statement':'author scene','mode':'technical-fixture','authoring_task':'task'},
                  'inputs':[{'path':'input.json','sha256':sha(root/'input.json')}],
                  'expected_outputs':[{'path':'scene.json','kind':'native-composition'}]}
            with self.assertRaisesRegex(ValueError,'symlink'):start_task(root,spec)
            with self.assertRaisesRegex(ValueError,'symlink'):checkpoint(root,'BUILD',0,0,'test')
            self.assertFalse(outside.exists())

    def test_unavailable_effort_is_explicit_and_never_zero(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'input.json').write_text('{}')
            spec={'requirement':{'id':'r','statement':'author scene','mode':'technical-fixture','authoring_task':'task'},
                  'inputs':[{'path':'input.json','sha256':sha(root/'input.json')}],
                  'expected_outputs':[{'path':'scene.json','kind':'native-composition'}]}
            start_task(root,spec);task=checkpoint(root,'BUILD',None,None,'author effort was not instrumented')
            self.assertIsNone(task['history'][-1]['active_seconds'])
            self.assertEqual(task['history'][-1]['measurement'],'UNAVAILABLE')
            with self.assertRaisesRegex(ValueError,'measured'):checkpoint(root,'BUILD',None,1,'partial unknown timing')


if __name__=='__main__':unittest.main()
