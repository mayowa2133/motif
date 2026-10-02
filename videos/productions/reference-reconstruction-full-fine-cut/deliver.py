"""Deliver/verify the full moving fine cut; keep all candidate renders."""
from pathlib import Path
import hashlib, io, json, re, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
import numpy as np
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
BASE=P.parent/'reference-reconstruction-01-finishing'
sys.path.insert(0,str(ROOT/'scripts'))
from motif_produce import loudness
D=1262/30
def run(args):return subprocess.check_output(args,stderr=subprocess.PIPE)
def probe(path):return json.loads(run(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_type,width,height,nb_frames,r_frame_rate,duration','-of','json',str(path)]))
def stream_hash(path,kind):return run(['ffmpeg','-v','error','-i',str(path),'-map',f'0:{kind}:0','-c','copy','-f','hash','-hash','sha256','-']).decode().strip()
def frame(path,n,width=180):
    b=run(['ffmpeg','-v','error','-i',str(path),'-vf',f'select=eq(n\\,{n}),scale={width}:-1','-frames:v','1','-f','image2pipe','-vcodec','png','-'])
    return Image.open(io.BytesIO(b)).convert('RGB')
full=P/'renders/full-film-fine-cut.mp4';mobile=P/'renders/mobile.mp4';comp=P/'renders/comparison.mp4'
label=Image.new('RGB',(720,40),'#182127');ld=ImageDraw.Draw(label);lf=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',16)
ld.text((14,10),'REFERENCE · SOURCE AUDIO MUTED',font=lf,fill='white');ld.text((377,10),'MOTIF · FULL FILM FINE CUT',font=lf,fill='white');label.save(P/'review/comparison-labels.png')
# The prepared mix preserves baseline decoded samples at unity. Encode it once.
run(['ffmpeg','-v','error','-y','-i',str(P/'renders/picture-full-fine-04.mp4'),'-i',str(P/'assets/fine-mix.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-t',str(D),'-movflags','+faststart',str(full)])
run(['ffmpeg','-v','error','-y','-i',str(P/'renders/picture-mobile-fine-02.mp4'),'-i',str(full),'-map','0:v:0','-map','1:a:0','-c','copy','-t',str(D),'-movflags','+faststart',str(mobile)])
run(['ffmpeg','-v','error','-y','-i','/Users/mayowaadesanya/Downloads/igexport-Dd15NcHvlNl.mp4','-i',str(mobile),'-loop','1','-i',str(P/'review/comparison-labels.png'),'-filter_complex','[0:v]scale=360:640,setpts=PTS-STARTPTS[ref];[ref][1:v]hstack=inputs=2,pad=720:680:0:40:color=0x182127[v];[v][2:v]overlay=0:0[out]','-map','[out]','-map','1:a:0','-frames:v','1262','-r','30','-c:v','libx264','-crf','18','-c:a','copy','-movflags','+faststart',str(comp)])
report={'provenance':'Codex-assisted, reference-led production using Motif','frames':1262,'fps':30,'duration':D,'approvedReuse':[436,600],'sourceAudioUsed':False,'subjectiveListening':'unassessed','retiming':False,'media':{},'baseline':{},'cutChecks':{},'audio':loudness(full),'runtimeCheckFile':'review/check-fine-04.json','motionAssertions':'disabled by CLI; sampled decoded geometry checks and playback separately recorded','captionAlignment':'Whisper DTW on actual generated WAVs, waveform limits; automatic alignment approximate'}
assert abs(report['audio']['integrated_lufs']+16)<=.8,report['audio']
assert report['audio']['true_peak_dbtp']<=-1.5,report['audio']
for name,dims in [('full-film-fine-cut',(1080,1920)),('mobile',(360,640)),('comparison',(720,680))]:
    media=probe(P/'renders'/f'{name}.mp4');v=next(s for s in media['streams'] if s['codec_type']=='video')
    assert (v['width'],v['height'])==dims and int(v['nb_frames'])==1262 and v['r_frame_rate']=='30/1'
    assert abs(float(v['duration'])-D)<.001
    report['media'][name]=media
assert stream_hash(full,'a')==stream_hash(mobile,'a')==stream_hash(comp,'a')
report['sharedAudioPayload']=True
assert stream_hash(full,'v')==stream_hash(P/'renders/picture-full-fine-04.mp4','v')
assert stream_hash(mobile,'v')==stream_hash(P/'renders/picture-mobile-fine-02.mp4','v')
lock=json.loads((P/'baseline-lock.json').read_text())
for name,path in [('final',BASE/'renders/final.mp4'),('mobile',BASE/'renders/mobile.mp4')]:
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    assert digest==lock['files'][name]
    assert digest==hashlib.sha256((P/'assets/baseline'/f'{name}.mp4').read_bytes()).hexdigest()
    report['baseline'][name]={'originalAndReuseSha256':digest,'unchanged':True}
    assembled=full if name=='final' else mobile
    stats=P/'review'/f'baseline-{name}-ssim.log'
    proc=subprocess.run(['ffmpeg','-v','info','-i',str(assembled),'-i',str(path),'-filter_complex',f'[0:v]trim=start_frame=436:end_frame=600,setpts=PTS-STARTPTS[a];[1:v]setpts=PTS-STARTPTS[b];[a][b]ssim=stats_file={stats}', '-an','-f','null','-'],capture_output=True,text=True)
    assert proc.returncode==0,proc.stderr
    values=[float(x) for x in re.findall(r'All:([0-9.]+)',stats.read_text())]
    assert len(values)==164 and min(values)>.96,(name,len(values),min(values))
    report['baseline'][name]['deliveryReencodeSSIM']={'frames':len(values),'minimum':min(values),'mean':sum(values)/len(values),'note':'Reuse video undergoes delivery encoding; approved source files themselves are unchanged. This checks frame correspondence, not style similarity.'}
# Background color changes verify the authored source-frame scene boundaries.
shots=json.loads((P/'reconstruction-timeline.json').read_text())['shots']
boundaries=[s['frames'][0] for s in shots[1:]]
for n in boundaries:
    pixels=[]
    for f in [n-1,n]:
        im=frame(mobile,f,360);pixels.append(list(im.getpixel((350,25))))
    difference=float(np.linalg.norm(np.array(pixels[1],float)-np.array(pixels[0],float)))
    assert difference>8,(n,pixels,difference)
    report['cutChecks'][str(n)]={'beforeAfterBackgroundPixels':pixels,'difference':difference,'basis':'decoded native picture, adjacent source-frame boundaries'}
for path,digest in json.loads((P/'preservation-lock.json').read_text()).items():
    assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==digest,path
report['roughAndCanonicalFilesUnchanged']=True
# A concise whole-film sheet; context, not a substitute for moving review.
frames=[45,162,235,315,408,459,505,570,625,671,733,758,828,875,905,962,1045,1098,1178,1209,1247]
sheet=Image.new('RGB',(1260,1020),'#182127');draw=ImageDraw.Draw(sheet)
font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',12)
for i,n in enumerate(frames):
    x=(i%7)*180;y=(i//7)*340
    sheet.paste(frame(mobile,n),(x,y+20));draw.text((x+4,y+3),f'f{n} · {n/30:.2f}s',font=font,fill='white')
sheet.save(P/'review/full-film-overview.jpg',quality=93)
# Compact matched pairs: repairs, staging, cards and protected joins.
frames=[15,30,60,95,168,414,657,672,690,691,905,1098,435,436,599,600]
sheet=Image.new('RGB',(1480,1392),'#182127');draw=ImageDraw.Draw(sheet)
source=Path('/Users/mayowaadesanya/Downloads/igexport-Dd15NcHvlNl.mp4')
for i,n in enumerate(frames):
    x=(i%4)*370;y=(i//4)*348
    draw.text((x+5,y+4),f'Source | Motif · f{n} · {n/30:.2f}s',font=font,fill='white')
    sheet.paste(frame(source,n),(x+3,y+25));sheet.paste(frame(mobile,n),(x+186,y+25))
sheet.save(P/'review/repair-matching-sheet.jpg',quality=94)
(P/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'media':{k:(next(s for s in v['streams'] if s['codec_type']=='video')['nb_frames']) for k,v in report['media'].items()},'audio':report['audio'],'baseline':report['baseline'],'cuts':len(report['cutChecks'])},indent=2))
