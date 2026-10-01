"""Inspect saved exports independently of the producer; never modifies a production."""
import hashlib
import io
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent

def read(path):
    return json.loads(path.read_text())

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(args):
    return subprocess.run(args, check=True, capture_output=True).stdout.decode()

def event(spec, target, action, predicate=lambda e: True):
    return next(e for e in spec['events'] if e['target'] == target and e['action'] == action and predicate(e))

def normalized(text):
    return re.findall(r'[a-z]+', text.lower())

rows = []
for slug, label in [('brief-variation-a-sync', 'SYNC'), ('brief-variation-b-review', 'REVIEW')]:
    project = ROOT / 'videos/productions' / slug
    spec = read(project / 'scene-events.json')
    scene = read(project / 'scene-data.json')
    brief = read(project / 'brief.json')
    words = read(project / 'assets/voice/transcript.json')
    narration = (project / 'assets/voice/narration.txt').read_text().strip()
    html = (project / 'index.html').read_text()
    svg = ET.fromstring(re.search(r'(<svg id="scene".*?</svg>)', html, re.S)[1].replace('data-layout-allow-overflow>', 'data-layout-allow-overflow="">'))
    texts = [''.join(n.itertext()) for n in svg.iter() if n.tag.endswith('}text')]
    by_id = {n.get('id'): n for n in svg.iter() if n.get('id')}
    card_label = ''.join(next(n for n in by_id['call-card'].iter() if n.tag.endswith('}text')).itertext())
    cap_events = [event(spec, f'#caption-{i}', 'CAPTION_REPLACE')['time'] for i in range(8)]
    anchors = [0, 2, 6, 11, 15, 20, 25, 31]
    starts = [round(words[i]['start'], 3) for i in anchors]
    press = event(spec, '#human-finger', 'TWEEN', lambda e: e['params'].get('to', {}).get('y') == 35)
    clear = event(spec, '#human-finger', 'TWEEN', lambda e: e['params'].get('to', {}).get('opacity') == 0)
    booked = event(spec, '#focus-card', 'POP_IN')
    faded = event(spec, '#proposal-slip', 'TWEEN', lambda e: e['params'].get('to', {}).get('opacity') == 0)
    timing = {
        'press_complete': round(press['time'] + press['params']['duration'], 3),
        'approval_check': event(spec, '#approval-check', 'POP_IN')['time'],
        'finger_clear': round(clear['time'] + clear['params']['duration'], 3),
        'spoken_only_then': starts[6],
        'proposal_gone': round(faded['time'] + faded['params']['duration'], 3),
        'booking_start': booked['time'],
        'booking_complete': round(booked['time'] + booked['params']['duration'], 3),
        'result_headline': event(spec, '#headline-done', 'POP_IN')['time'],
    }
    final = project / 'renders/final.mp4'
    probe = json.loads(run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=codec_type,width,height,r_frame_rate,nb_frames,duration', '-of', 'json', str(final)]))
    analysis = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', str(final), '-vn', '-af', 'loudnorm=I=-16:TP=-2:LRA=11:print_format=json', '-f', 'null', '-'], check=True, capture_output=True, text=True).stderr
    measured = json.loads(re.search(r'\{\s*"input_i".*?\}', analysis, re.S)[0])
    audio = {'integrated_lufs': float(measured['input_i']), 'true_peak_dbtp': float(measured['input_tp'])}
    def video_hash(name):
        return run(['ffmpeg', '-v', 'error', '-i', str(project / 'renders' / name), '-map', '0:v:0', '-c:v', 'copy', '-f', 'hash', '-hash', 'sha256', '-']).strip().split('=')[1]
    storyboard = (project / 'STORYBOARD_INITIAL.md').read_text()
    checks = {
        'input_scene_card_label_agree': brief['scene_data']['existing_title'] == scene['existing_title'] == card_label == label,
        'no_visible_or_storyboard_CALL': 'CALL' not in texts and not re.search(r'\bCALL\b', storyboard),
        'fixed_times_and_proposal_retained': all(t in texts for t in ['3 PM', '4 PM', 'FOCUS']) and brief['scene_data']['proposed_title'] == 'FOCUS',
        'fixed_narration_matches_transcript': normalized(narration) == normalized(' '.join(w['text'] for w in words)),
        'caption_events_follow_word_anchors': cap_events == starts == [c['start'] for c in spec['captions']],
        'press_check_clear_only_then_booking_order': timing['press_complete'] < timing['approval_check'] < timing['finger_clear'] < timing['spoken_only_then'] < timing['booking_start'],
        'proposal_gone_before_booking': timing['proposal_gone'] < timing['booking_start'],
        'booking_before_result_headline': timing['booking_complete'] < timing['result_headline'],
        'encoded_loudness_target': abs(audio['integrated_lufs'] + 16) <= .8,
        'encoded_peak_ceiling': audio['true_peak_dbtp'] <= -1.5,
        'first_final_video_stream_identical': video_hash('first.mp4') == video_hash('final.mp4'),
    }
    rows.append({'slug': slug, 'expected_existing_label': label, 'actual_card_label': card_label,
        'visible_text': texts, 'narration': narration, 'narration_sha256': sha(project / 'assets/voice/narration.txt'),
        'voice_sha256': sha(project / 'assets/voice/narration-af-nova.wav'), 'state_timing_seconds': timing,
        'caption_starts_seconds': starts, 'probe': probe, 'encoded_audio': audio,
        'final_sha256': sha(final), 'checks': checks, 'pass': all(checks.values()),
        'subjective_listening': 'not assessed'})
    assert all(checks.values()), checks
(OUT / 'supported-results.json').write_text(json.dumps(rows, indent=2) + '\n')
source_before = read(OUT / 'shared-source-hashes.json')
frozen_before = read(OUT / 'frozen-hashes-before.json')
changed_shared = [p for p, h in source_before.items() if sha(ROOT / p) != h]
changed_frozen = [p for p, h in frozen_before.items() if sha(ROOT / p) != h]
reuse = {'shared_files_checked': len(source_before), 'shared_source_changes_between_runs': changed_shared,
    'frozen_files_checked': len(frozen_before), 'changed_frozen_files': changed_frozen,
    'shared_producer_sha256': source_before['scripts/motif_produce.py'],
    'same_narration_text': rows[0]['narration_sha256'] == rows[1]['narration_sha256'],
    'same_generated_voice': rows[0]['voice_sha256'] == rows[1]['voice_sha256'],
    'manual_per_run_source_or_output_edits': [], 'pass': not changed_shared and not changed_frozen}
(OUT / 'source-reuse-and-frozen-check.json').write_text(json.dumps(reuse, indent=2) + '\n')
assert reuse['pass']

for name, times in [('mobile-story-frames', [1.6, 6.3, 8.3, 10.7, 12.5]), ('approval-detail', [8.05, 8.25, 8.65, 9.75, 10.45, 10.7])]:
    width, height, top = 360, 640, 48
    sheet = Image.new('RGB', (len(times) * width, 2 * (height + top)), '#f4eee1')
    draw = ImageDraw.Draw(sheet)
    for row, result in enumerate(rows):
        mobile = ROOT / 'videos/productions' / result['slug'] / 'renders/mobile.mp4'
        for col, second in enumerate(times):
            png = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(second), '-i', str(mobile), '-frames:v', '1', '-f', 'image2pipe', '-vcodec', 'png', '-'], check=True, capture_output=True).stdout
            frame = Image.open(io.BytesIO(png)).convert('RGB')
            sheet.paste(frame, (col * width, row * (height + top) + top))
            draw.text((col * width + 12, row * (height + top) + 16), f"{result['expected_existing_label']} / {second:.2f} s", fill='#202c32')
    sheet.save(OUT / f'{name}.jpg', quality=95)
print(json.dumps({'supported': [r['pass'] for r in rows], 'reuse': reuse}, indent=2))
