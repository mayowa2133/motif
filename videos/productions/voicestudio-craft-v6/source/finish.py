"""Keep the finished baseline AAC stream; verify final media and preservation."""
from pathlib import Path
import json,hashlib,subprocess,sys
P=Path(__file__).resolve().parents[1];OLD=P.parent/'voicestudio-consistency-v5'
def run(args):return subprocess.check_output(args)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def audio(p):return hashlib.sha256(run(['ffmpeg','-v','error','-i',str(p),'-map','0:a:0','-c:a','copy','-f','adts','pipe:1'])).hexdigest()
def probe(p):
 d=json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]));v=next(s for s in d['streams'] if s['codec_type']=='video')
 assert int(v['nb_frames'])==986 and v['r_frame_rate']=='30/1' and abs(float(v['duration'])-986/30)<.00001
 return {'width':v['width'],'height':v['height'],'frames':int(v['nb_frames']),'fps':v['r_frame_rate'],'duration':v['duration'],'audio_sha256':audio(p),'bytes':p.stat().st_size}
for raw,final in [('picture-full.mp4','moving-preview.mp4'),('picture-native.mp4','mobile.mp4')]:
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(P/'renders'/raw),'-i',str(OLD/'renders/moving-preview.mp4'),'-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',str(P/'renders'/final)],check=True)
baseline=audio(OLD/'renders/moving-preview.mp4');full=probe(P/'renders/moving-preview.mp4');native=probe(P/'renders/mobile.mp4');assert full['audio_sha256']==native['audio_sha256']==baseline
assert (full['width'],full['height'])==(1080,1920) and (native['width'],native['height'])==(360,640)
preserved=json.loads((P/'review/preserved-v5.json').read_text());changed=[name for name,digest in preserved['sha256'].items() if not (OLD/name).exists() or sha(OLD/name)!=digest];assert not changed,changed
unchanged={n:sha(P/'compositions'/f'shot-{n:02}.html')==sha(OLD/'compositions'/f'shot-{n:02}.html') for n in range(1,20) if n not in [2,3,5,9,12,16,19]};assert all(unchanged.values())
artwork={str(f.relative_to(P)):sha(f)==sha(OLD/f.relative_to(P)) for f in (P/'assets/art-v4').rglob('*') if f.is_file()};assert all(artwork.values())
report={'status':'REVIEW_REQUIRED','full':full,'native':native,'baseline_audio_sha256':baseline,'preserved_v5_files':len(preserved['sha256']),'preserved_v5_changed_files':changed,'unchanged_composition_bytes_identical':unchanged,'hero_artwork_bytes_identical':artwork,'subjective_listening':'not reassessed; baseline AAC stream reused exactly','source_scene_frame_schedule':'986 frames / 30 fps, nineteen fixed shots'}
(P/'review/encoded-final.json').write_text(json.dumps(report,indent=2)+'\n')
state=json.loads((P/'review-state.json').read_text());state['final_verification']=report
state['saved_source_hashes'].update({str(p.relative_to(P)):sha(p) for p in (P/'source').glob('*.py')});(P/'review-state.json').write_text(json.dumps(state,indent=2)+'\n')
print(json.dumps(report,indent=2))
