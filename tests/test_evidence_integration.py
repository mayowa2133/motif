"""Exercise production boundaries without capture or manufactured reviews."""
import copy
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from motif_evidence import declare,write,sha,evidence_inputs,technical_binding,compile_scope,freeze_capture,seal_capture,require_capture,evidence_shots
from motif_quality import technical,TECHNICAL,require_gate,rough
from motif_plan_finish import finish
from test_causal_evidence import causal_map


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.p=Path(self.tmp.name)
        write(self.p/'brief.json',{'script':'Wait for input'})
        write(self.p/'production-plan.json',{'quality_mode':'motif-gold-v1','script':'Wait for input','beats':[{'id':'wait'}]})
        write(self.p/'scene-events.json',{'fps':30,'durationSec':1})

    def test_all_advancement_boundaries_require_scope_before_commands(self):
        with patch('motif_quality.cmd') as command:
            for call in (lambda:require_gate(self.p,'rough'),lambda:rough(self.p),lambda:finish(self.p,self.p/'missing.mp4',[1,2])):
                with self.assertRaisesRegex(ValueError,'scope missing'):call()
            command.assert_not_called()
        with self.assertRaisesRegex(ValueError,'missing compile quality'):compile_scope(self.p,{})
        declare(self.p,'technical-fixture','UNIT')
        compile_scope(self.p,{})

    def test_missing_causal_mapping_stops_before_capture(self):
        declare(self.p,'original-film','UNIT')
        with patch('motif_quality.cmd') as command:
            with self.assertRaises(FileNotFoundError):rough(self.p)
            command.assert_not_called()

    def test_compile_argument_cannot_bypass_saved_gold_plan(self):
        declare(self.p,'original-film','UNIT')
        with self.assertRaisesRegex(ValueError,'saved Gold'):compile_scope(self.p,{})
        with self.assertRaisesRegex(ValueError,'saved Gold'):compile_scope(self.p,{'quality_mode':'motif-gold-v1','changed':True})

    def test_required_frames_come_from_frozen_map_not_review_request(self):
        declare(self.p,'original-film','UNIT')
        write(self.p/'causal-map.json',causal_map())
        write(self.p/'critical-intervals.json',[{'id':'wait','critical_intervals':[[0,29]]}])
        self.assertEqual(evidence_inputs(self.p)['status'],'DATA_VALID')
        write(self.p/'critical-intervals.json',[{'id':'wait','critical_intervals':[[0,0]]}])
        with self.assertRaisesRegex(ValueError,'frozen causal map'):evidence_inputs(self.p)
        m=causal_map();m['propositions'][0]['review_interval']=[20,29]
        write(self.p/'causal-map.json',m)
        with self.assertRaisesRegex(ValueError,'include stimulus'):evidence_inputs(self.p)

    def test_post_capture_map_edits_cannot_redefine_frozen_requirements(self):
        declare(self.p,'original-film','UNIT')
        write(self.p/'causal-map.json',causal_map())
        write(self.p/'critical-intervals.json',[{'id':'wait','critical_intervals':[[0,29]]}])
        artifact=self.p/'unit.bin';artifact.write_bytes(b'UNIT')
        name=freeze_capture(self.p);record=seal_capture(self.p,name,[artifact])
        require_capture(self.p,record,[artifact])
        m=causal_map();m['propositions'][0].update(review_interval=[0,9],persistent_until_frame=9)
        write(self.p/'causal-map.json',m)
        write(self.p/'critical-intervals.json',[{'id':'wait','critical_intervals':[[0,9]]}])
        with self.assertRaisesRegex(ValueError,'since frozen'):require_capture(self.p,record,[artifact])

    def test_ui_sampler_uses_saved_frame_schedule(self):
        shots=evidence_shots({'shots':[{'id':'ui','contract':{}}]}, {'shots':[{'id':'ui','startFrame':0,'endFrame':30}]})
        self.assertEqual(shots,[{'id':'ui','startFrame':0,'endFrame':30,'contacts':[]}])

    def test_technical_source_content_and_check_identity_are_bound(self):
        source=self.p/'check.json'
        record={'status':'PASS','events_sha256':'E','video_sha256':'V','observation':'UNIT',
                'coverage':{'enabled':True,'required':2,'checked':2,'scope':'UNIT'}}
        write(source,dict(record,check='caption-overflow'))
        record.update(file=str(source),sha256=sha(source))
        technical_binding('caption-overflow',record,'E','V')
        with self.assertRaisesRegex(ValueError,'different check'):technical_binding('anchors',record,'E','V')
        changed=copy.deepcopy(record);changed['coverage']['checked']=3
        with self.assertRaisesRegex(ValueError,'result differs'):technical_binding('caption-overflow',changed,'E','V')

    def test_complete_labels_do_not_replace_source_coverage(self):
        declare(self.p,'original-film','UNIT')
        video=self.p/'unit-media';video.write_bytes(b'UNIT_ONLY')
        checks=self.p/'checks.json';supplied={}
        for name in set(TECHNICAL)-{'frame-count','fps','dimensions','duration','loudness','true-peak'}:
            source=self.p/(name+'.json')
            record={'status':'PASS','events_sha256':sha(self.p/'scene-events.json'),'video_sha256':sha(video),
                    'observation':'UNIT_ONLY','coverage':{'enabled':True,'required':1,'checked':1,'scope':'UNIT'}}
            write(source,dict(record,check=name))
            supplied[name]=dict(record,file=str(source),sha256=sha(source))
        write(checks,supplied)
        probe={'width':360,'height':640,'fps':30,'frames':30,'duration':1,'sha256':sha(video)}
        with patch('motif_quality.probe_video',return_value=probe),patch('motif_produce.loudness',return_value={'integrated_lufs':-15,'true_peak_dbtp':-2}):
            result=technical(self.p,video,checks)
            self.assertEqual(result['supplemental']['sha256'],sha(checks))
            supplied['caption-overflow']['coverage']['checked']=0;write(checks,supplied)
            with self.assertRaisesRegex(ValueError,'coverage'):technical(self.p,video,checks)


if __name__=='__main__':unittest.main()
