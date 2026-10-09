"""Bounded scene mechanics, not artistic or human comprehension scores."""
import copy
import json
import shutil
import sys
import tempfile
import unittest
import wave
from pathlib import Path
sys.path[:0]=[str(Path(__file__).resolve().parents[1]/'scripts')]
from motif_waiting import validate,state_at,svg_at,compile_waiting
from motif_evidence import declare,write,sha,freeze_capture,seal_capture,require_capture
from motif_media_contracts import reference_observation_scope,resource_inventory,native_text,saved_audio
ROOT=Path(__file__).resolve().parents[1]


def scene():return json.loads((ROOT/'quality/causal-pilot/waiting-scene.json').read_text())


def text_packet(root,text='Await input'):
    source=ROOT/'quality/validation/fixtures/assets/fonts'
    for name in ('Inter-700.woff2','OFL-inter.txt'):shutil.copyfile(source/name,root/name)
    return {'text':text,'lines':text.split('\n'),'font':{'path':'Inter-700.woff2','sha256':sha(root/'Inter-700.woff2')},
            'license':{'path':'OFL-inter.txt','sha256':sha(root/'OFL-inter.txt')},'size':28,'weight':700,
            'position':[40,120],'bounds':[20,70,340,200],'language':'en','text_policy':'simple-ltr-unshaped-v1',
            'frames':[60,179],'timing_source':'manual-lock'}


def project(root,s):
    write(root/'brief.json',{'script':s['script']});write(root/'production-plan.json',s)
    declare(root,'technical-fixture','UNIT')


class WaitingTests(unittest.TestCase):
    def test_exact_event_boundaries_repeated_and_reverse_seeks(self):
        s=scene();validate(s)
        frames=[0,29,30,59,60,149,150,179,180,209,210,239,150,60,60,0]
        states=[state_at(s,n) for n in frames]
        self.assertEqual([x['status'] for x in states[:12]],['working']*4+['pending']*4+['working']*2+['complete']*2)
        self.assertEqual(states[4],states[13]);self.assertEqual(states[13],states[14]);self.assertEqual(states[0],states[-1])
        pending=[state_at(s,n) for n in range(60,180)]
        self.assertEqual(len({x['progress'] for x in pending}),1)
        self.assertTrue(all(state_at(s,n)['result_visible'] for n in range(210,240)))

    def test_diagnostic_controls_are_failures_not_method_winners(self):
        s=scene()
        self.assertTrue(state_at(s,40)['request_visible'])
        self.assertFalse(state_at(s,40,'no-stimulus')['request_visible'])
        self.assertNotEqual(state_at(s,80,'continues-pending')['progress'],state_at(s,140,'continues-pending')['progress'])

    def test_native_ids_contact_center_and_mobile_bounds(self):
        s=scene();body,_=svg_at(s,0)
        for n in s['nodes']:self.assertIn('id="'+n['id']+'"',body)
        self.assertIn('id="worker-hand" cx="145" cy="411.0"',body)
        malformed=copy.deepcopy(s);malformed['nodes'][0]['position'][0]=340
        with self.assertRaisesRegex(ValueError,'clipped'):validate(malformed)

    def test_malformed_and_unresolved_inputs_rejected(self):
        s=scene()
        variants=[]
        for mutation in (lambda x:x['events'].update(stop=150),lambda x:x.update(frames=True),lambda x:x['nodes'][0].update(size=[float('nan'),14]),lambda x:x['nodes'][0].update(id='bad id'),lambda x:x['nodes'][0].update(layer=1)):
            changed=copy.deepcopy(s);mutation(changed);variants.append(changed)
        for changed in variants:
            with self.assertRaises(ValueError):validate(changed)

    def test_shared_compiler_dispatch_and_fixture_only_scope(self):
        from motif_plan_compile import compile_plan
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);s=scene();write(p/'brief.json',{'script':s['script']});write(p/'production-plan.json',s)
            declare(p,'technical-fixture','UNIT')
            result=compile_plan(p,s,[],0,None)
            self.assertEqual(result['status'],'TECHNICAL_FIXTURE_COMPILED')
            self.assertEqual(json.loads((p/'scene-events.json').read_text())['state_trace'][60]['status'],'pending')
            (p/'production-scope.json').unlink();s['quality_mode']='motif-gold-v1';write(p/'production-plan.json',s)
            declare(p,'original-film','UNIT')
            with self.assertRaisesRegex(ValueError,'fixture-only'):compile_waiting(p,s)

    def test_sparse_observation_cannot_claim_motion_or_raster_editability(self):
        packet={'source_sha256':'0'*64,'authorization':'UNIT','observed_frames':[0,30],
                'requested_mode':'faithful-editable','native_element_ids':['native'],'raster_only':False}
        result=reference_observation_scope(packet,range(31))
        self.assertEqual(result['motion_fidelity'],'UNASSESSED')
        packet['raster_only']=True
        with self.assertRaisesRegex(ValueError,'flattened'):reference_observation_scope(packet,range(31))

    def test_relative_resource_inventory_fails_instead_of_substitution(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            with self.assertRaises(ValueError):resource_inventory(p,[{'path':'missing.ttf','sha256':'UNIT'}])
            with self.assertRaisesRegex(ValueError,'relative'):resource_inventory(p,[{'path':'../font.ttf','sha256':'UNIT'}])

    def test_input_must_equal_saved_plan_before_compilation(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);s=scene();project(p,s);s['nodes'][1]['color']='#FF0000'
            with self.assertRaisesRegex(ValueError,'differs from saved'):compile_waiting(p,s)
            self.assertFalse((p/'scene-events.json').exists())

    def test_generated_geometry_ids_and_event_map_boundaries(self):
        for mutation,error in ((lambda x:x['nodes'][1].update(size=[140,45]),'body'),
                               (lambda x:x['nodes'][4].update(position=[0,380]),'painted'),
                               (lambda x:x['nodes'][4].update(id='worker-hand'),'generated'),
                               (lambda x:x['nodes'][4].update(id='work-progress'),'generated'),
                               (lambda x:x['nodes'][1].update(position=[70,0],size=[2,100]),'painted'),
                               (lambda x:x['events'].update(stop=61),'causal map')):
            s=scene();mutation(s)
            with self.assertRaisesRegex(ValueError,error):validate(s)

    def test_real_font_caption_recolor_and_retime_source_edits(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);s=scene();s['text']=[text_packet(p)];project(p,s);compile_waiting(p,s)
            before,_=svg_at(s,60,p,captions=True)
            self.assertIn('aria-label="Await input"',before)
            edited=copy.deepcopy(s);edited['text'][0].update(text='Input ready',lines=['Input ready'])
            edited['nodes'][1]['color']='#FF0000';edited['events'].update(stop=70,response=160,resume=190,complete=220)
            edited['causal_map']['propositions'][0]['action_frame']=70
            edited['text'][0]['frames']=[70,189];write(p/'production-plan.json',edited);compile_waiting(p,edited)
            after,_=svg_at(edited,70,p,captions=True)
            self.assertIn('aria-label="Input ready"',after);self.assertIn('fill="#FF0000"',after)
            self.assertNotIn('aria-label=',svg_at(edited,69,p,captions=True)[0])
            self.assertEqual(state_at(edited,60)['status'],'working');self.assertEqual(state_at(edited,70)['status'],'pending')

    def test_text_bounds_glyphs_weight_and_speech_provenance_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);label=text_packet(p)
            for mutation,error in ((lambda x:x.update(bounds=[-30,0,360,640]),'canvas'),
                                   (lambda x:x.update(position=[-20,120]),'fit'),
                                   (lambda x:x.update(bounds=[0,0,360]),'four'),
                                   (lambda x:x.update(weight=900),'weight'),
                                   (lambda x:x.update(text='\U0001f984',lines=['\U0001f984']),'glyph'),
                                   (lambda x:x.update(text='\u062a',lines=['\u062a']),'shaping')):
                changed=copy.deepcopy(label);mutation(changed)
                with self.assertRaisesRegex(ValueError,error):native_text(p,changed)
            label.update(timing_source='measured-speech',marker_evidence_sha256='not-a-hash')
            s=scene();s['text']=[label]
            with self.assertRaisesRegex(ValueError,'manual-lock'):validate(s)

    def test_relative_symlink_escape_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);root=p/'project';root.mkdir();outside=p/'outside.txt';outside.write_text('synthetic')
            (root/'resource.txt').symlink_to(outside)
            with self.assertRaisesRegex(ValueError,'escapes'):resource_inventory(root,[{'path':'resource.txt','sha256':sha(outside)}])

    def test_capture_config_mutation_invalidates_frozen_encode(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);s=scene();project(p,s);compile_waiting(p,s);write(p/'render-config.json',{'captions':False})
            capture=freeze_capture(p);artifact=p/'UNIT';artifact.write_bytes(b'synthetic')
            seal_capture(p,capture,[artifact]);require_capture(p,artifacts=[artifact])
            write(p/'render-config.json',{'captions':True})
            with self.assertRaisesRegex(ValueError,'changed'):require_capture(p,artifacts=[artifact])

    def test_saved_mix_integer_samples_and_resource_freshness(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);s=scene()
            with wave.open(str(p/'mix.wav'),'wb') as track:
                track.setparams((1,2,48000,384000,'NONE','not compressed'));track.writeframes(b'\0\0'*384000)
            s['audio']={'role':'synthetic-tone','resource':{'path':'mix.wav','sha256':sha(p/'mix.wav')},
                        'sample_rate':48000,'sample_frames':384000}
            self.assertEqual(saved_audio(p,s)['sample_frames'],384000)
            project(p,s);compile_waiting(p,s);capture=freeze_capture(p);artifact=p/'UNIT';artifact.write_bytes(b'synthetic')
            seal_capture(p,capture,[artifact]);(p/'mix.wav').write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'missing or changed'):require_capture(p)
            s['audio']['sample_frames']=383999
            s['audio']['resource']['sha256']=sha(p/'mix.wav')
            with self.assertRaisesRegex(ValueError,'sample authority'):saved_audio(p,s)

    def test_declared_relative_rebuild_in_two_locations(self):
        with tempfile.TemporaryDirectory() as a,tempfile.TemporaryDirectory() as b:
            outputs=[];events=[]
            for directory in (a,b):
                p=Path(directory);s=scene();s['text']=[text_packet(p,'Réponse reçue')]
                project(p,s);compile_waiting(p,s);outputs.append(svg_at(s,60,p,captions=True)[0])
                events.append((p/'scene-events.json').read_bytes())
            self.assertEqual(outputs[0],outputs[1]);self.assertEqual(events[0],events[1])


if __name__=='__main__':unittest.main()
