"""Fail-closed bridge tests using mock files; no encode or pixel certification."""
import sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import motif_custom_authoring as task
import motif_evidence as ev
import motif_quality as quality

def fixture(root,mode='technical-fixture',ready=True):
    ev.write(root/'brief.json',{'script':'synthetic data fixture'})
    ev.write(root/'production-plan.json',{})
    ev.write(root/'scene-events.json',{'fps':30,'durationSec':1})
    ev.declare(root,'technical-fixture','TEST')
    (root/'input.json').write_text('{}');(root/'component.json').write_text('{}')
    task.start_task(root,{'requirement':{'id':'r','statement':'editable component','mode':mode,'authoring_task':'manual'},
        'inputs':[{'path':'input.json','sha256':ev.sha(root/'input.json')}],
        'expected_outputs':[{'path':'component.json'}]})
    if ready:task.checkpoint(root,'READY_FOR_SHARED_QA',None,None,'test data checkpoint')
    a,b=root/'caption.mock',root/'picture.mock';a.write_bytes(b'caption mock');b.write_bytes(b'picture mock')
    return a,b

def mock_sampler(root,phase,a,b,shots):
    base=root/'quality-review'/phase;base.mkdir(parents=True)
    manifest={'state_fingerprint':quality.state_fingerprint(root)}
    for key,path in [('with_captions',a),('without_captions',b)]:
        sheet=base/(key+'.mock');sheet.write_bytes(b'NO PIXELS')
        trace=base/(key+'-trace.json');ev.write(trace,{'frames':[]})
        manifest[key]={'video':str(path),'sheets':[str(sheet)],'motion_trace':str(trace)}
    ev.write(base/'evidence.json',manifest);return manifest

def capture(root,a,b):
    name=ev.freeze_capture(root);ev.seal_capture(root,name,[a,b])

class CustomSharedQATests(unittest.TestCase):
    def test_ready_mode_and_capture_bindings(self):
        for options in ({'ready':False},{'mode':'original-film'}):
            with self.subTest(options=options),tempfile.TemporaryDirectory() as d:
                p=Path(d);a,b=fixture(p,**options)
                with self.assertRaises(ValueError):capture(p,a,b)
        for target in ('input.json','component.json'):
            with self.subTest(target=target),tempfile.TemporaryDirectory() as d:
                p=Path(d);a,b=fixture(p);capture(p,a,b);(p/target).write_text('{"changed":true}')
                if target=='component.json':task.checkpoint(p,'READY_FOR_SHARED_QA',None,None,'new authored output')
                with self.assertRaises(ValueError):task.sample_task(p,a,b,[])

    def test_valid_sampling_is_review_required_and_complete(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);a,b=fixture(p);capture(p,a,b)
            with patch.object(quality,'evidence_bundle',mock_sampler):value=task.sample_task(p,a,b,[])
            self.assertEqual(value['status'],'SAMPLED_REVIEW_REQUIRED');self.assertFalse(value['film_approved'])
            self.assertEqual(len(value['sampled_files']),4)
            self.assertEqual(task.require_sampled_task(p),value)

    def test_stale_outputs_checkpoint_media_and_sample_files_rejected(self):
        for target in ('component.json','caption.mock','picture.mock','with_captions.mock','with_captions-trace.json'):
            for missing in (False,True):
                with self.subTest(target=target,missing=missing),tempfile.TemporaryDirectory() as d:
                    p=Path(d);a,b=fixture(p);capture(p,a,b)
                    with patch.object(quality,'evidence_bundle',mock_sampler):task.sample_task(p,a,b,[])
                    f=p/target if target in ('component.json','caption.mock','picture.mock') else p/'quality-review/rough'/target
                    if missing:f.unlink()
                    else:f.write_bytes(b'CHANGED')
                    with self.assertRaises((ValueError,FileNotFoundError)):task.require_sampled_task(p)

    def test_receipt_cannot_omit_outputs_files_or_substitute_mode(self):
        for key,value in (('output_checkpoint',[]),('sampled_files',{}),('mode','original-film')):
            with self.subTest(key=key),tempfile.TemporaryDirectory() as d:
                p=Path(d);a,b=fixture(p);capture(p,a,b)
                with patch.object(quality,'evidence_bundle',mock_sampler):task.sample_task(p,a,b,[])
                receipt=ev.read(p/'custom-shared-qa.json');receipt[key]=value;ev.write(p/'custom-shared-qa.json',receipt)
                with self.assertRaises(ValueError):task.require_sampled_task(p)

if __name__=='__main__':unittest.main()
