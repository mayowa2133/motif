"""Optional utilities preserve measured timing and explicit rendered states."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from motif_frame_data import separate_frame_data
from motif_speech_markers import resolve_markers


class SpeechMarkerTests(unittest.TestCase):
    def test_exact_measured_onsets_and_uncertainty_survive_without_input_changes(self):
        words = [{'text': 'Open,', 'start': .27, 'status': 'measured'},
                 {'text': 'the', 'start': .41, 'status': 'uncertain'},
                 {'text': 'door.', 'start': 1.8, 'status': 'measured'}]
        requests = [{'id': 'open', 'phrase': 'OPEN the'},
                    {'id': 'result', 'phrase': 'door'}]
        before = copy.deepcopy((words, requests))
        result = resolve_markers(words, requests)
        self.assertEqual([r['time'] for r in result], [.27, 1.8])
        self.assertEqual(result[0]['word_range'], [0, 2])
        self.assertEqual(result[0]['alignment_states'], ['measured', 'uncertain'])
        self.assertEqual((words, requests), before)

    def test_repeated_phrase_requires_an_explicit_half_open_range(self):
        words = [{'text': 'Look', 'start': .2}, {'text': 'now', 'start': .8},
                 {'text': 'look', 'start': 2.7}, {'text': 'now!', 'start': 4.1}]
        with self.assertRaisesRegex(ValueError, '2 matches'):
            resolve_markers(words, [{'id': 'cut', 'phrase': 'look now'}])
        result = resolve_markers(words, [{'id': 'cut', 'phrase': 'look now', 'word_range': [2, 4]}])
        self.assertEqual(result[0]['time'], 2.7)
        self.assertEqual(result[0]['word_range'], [2, 4])
        self.assertEqual(result[0]['alignment_states'], ['unspecified', 'unspecified'])

    def test_invalid_schedule_and_nonfinite_onsets_cannot_be_published(self):
        words = [{'text': 'early', 'start': .4}, {'text': 'late', 'start': 1.7}]
        invalid = [[{'id': '', 'phrase': 'early'}],
                   [{'id': 'same', 'phrase': 'early'}, {'id': 'same', 'phrase': 'late'}],
                   [{'id': 'one', 'phrase': 'late'}, {'id': 'two', 'phrase': 'early'}],
                   [{'id': 'cut', 'phrase': 'missing'}],
                   [{'id': 'cut', 'phrase': '!!!'}],
                   [{'id': 'cut', 'phrase': 'early', 'word_range': [1, 1]}],
                   [{'id': 'cut', 'phrase': 'early', 'word_range': [0, 3]}]]
        for requests in invalid:
            with self.subTest(requests=requests), self.assertRaises(ValueError):
                resolve_markers(words, requests)
        for onset in (-.1, float('nan'), float('inf'), -float('inf')):
            with self.subTest(onset=onset), self.assertRaises(ValueError):
                resolve_markers([{'text': 'cut', 'start': onset}], [{'id': 'cut', 'phrase': 'cut'}])


class FrameDataTests(unittest.TestCase):
    def setUp(self):
        self.states = ['<g>first & café</g>', '<g>second "state"</g>', '<g>final</g>']
        self.spec = {'schemaVersion': '1.0', 'fps': 30, 'durationSec': .1,
                     'initial': [{'target': '#world', 'props': {'innerHTML': self.states[0]}}],
                     'events': [{'time': f / 30, 'target': '#world', 'action': 'SET',
                                 'params': {'props': {'innerHTML': self.states[f]}}} for f in (1, 2)]}
        self.raw = json.dumps(self.spec, indent=2, ensure_ascii=False)
        self.block = '<script type="application/json" id="frames">' + self.raw + '</script>'
        self.reader = "JSON.parse(document.getElementById('frames').textContent)"
        self.html = self.block + '<script>const spec=' + self.reader + ';</script>'

    def test_packed_data_preserves_states_through_existing_forward_and_reverse_seeks(self):
        for reader in (self.reader, self.reader.replace("'frames'", '"frames"')):
            html, script = separate_frame_data(self.html.replace(self.reader, reader), script_id='frames')
            self.assertIn('<script src="frame-data.js"></script>', html)
            self.assertNotIn('application/json', html)
            self.assertNotIn(reader, html)
            self.assertIn(self.raw, script)
            # Execute the packed data with the established finite-frame compiler.
            # This is a synthetic runtime probe, not a render or creative review.
            probe = r'''
const fs=require('node:fs'),vm=require('node:vm');
const input=JSON.parse(fs.readFileSync(0,'utf8'));
const element={innerHTML:''};let current=0,update,compiles=0;
const tl={time:()=>current,eventCallback:(_,fn)=>{update=fn;}};
const context={window:{MotifEventEngine:{compile:spec=>{compiles++;element.innerHTML=spec.initial[0].props.innerHTML;return tl;}}},document:{querySelector:()=>element}};
vm.runInNewContext(input.script,context);
vm.runInNewContext(fs.readFileSync(input.compiler,'utf8'),context);
context.window.MotifEventEngine.compileFrames(context.window.MotifFrameTables.frames,'unit');
const states=[];for(const time of [0,1/30,2/30,.1,0,1/30,1/30]){current=time;update();states.push(element.innerHTML);}
process.stdout.write(JSON.stringify({spec:context.window.MotifFrameTables.frames,states,compiles}));
'''
            run = subprocess.run(['node', '-e', probe], input=json.dumps({'script': script, 'compiler': str(ROOT / 'assets/runtime/motif-frame-sequence.js')}), text=True, capture_output=True, check=True)
            result = json.loads(run.stdout)
            self.assertEqual(result['spec'], self.spec)
            self.assertEqual(result['states'], [self.states[i] for i in (0, 1, 2, 2, 0, 1, 1)])
            self.assertEqual(result['compiles'], 1)

    def test_mixed_reader_quotes_execute_in_returned_html_load_order(self):
        double_reader = self.reader.replace("'frames'", '"frames"')
        source = self.block + '<script>window.results=[' + self.reader + ',' + double_reader + '];</script>'
        html, script = separate_frame_data(source, script_id='frames')
        probe = r'''
const fs=require('node:fs'),vm=require('node:vm');
const input=JSON.parse(fs.readFileSync(0,'utf8'));
const context={window:{},document:{getElementById:id=>{throw new Error('Removed inline data queried: '+id);}}};
for(const tag of input.html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/g)){
  const src=/\bsrc="([^"]+)"/.exec(tag[1]);
  vm.runInNewContext(src?input.files[src[1]]:tag[2],context);
}
process.stdout.write(JSON.stringify(context.window.results));
'''
        run = subprocess.run(['node', '-e', probe], input=json.dumps({'html': html, 'files': {'frame-data.js': script}}), text=True, capture_output=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(json.loads(run.stdout), [self.spec, self.spec])

    def test_missing_duplicate_or_unsupported_declared_data_stops(self):
        invalid = [self.html.replace(self.block, ''), self.block + self.html,
                   self.html.replace(self.reader, 'unsupportedReader()'),
                   self.html.replace('"schemaVersion": "1.0"', '"schemaVersion": "2.0"'),
                   self.html.replace('"fps": 30', '"fps": 60')]
        for html in invalid:
            with self.subTest(html=html), self.assertRaises(ValueError):
                separate_frame_data(html, script_id='frames')

    def test_output_name_is_one_local_script_basename(self):
        for filename in ('../frames.js', '/frames.js', 'frames.txt', 'bad".js', 'bad\\name.js'):
            with self.subTest(filename=filename), self.assertRaises(ValueError):
                separate_frame_data(self.html, script_id='frames', filename=filename)
        html, _ = separate_frame_data(self.html, script_id='frames', filename='shot.frames-01.js')
        self.assertIn('src="shot.frames-01.js"', html)


if __name__ == '__main__':
    unittest.main()
