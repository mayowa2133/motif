"""Mux unchanged approved soundtrack, verify encoded cuts, build review artifacts."""
from pathlib import Path
import json,subprocess,io,sys,hashlib
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent
ROOT=P.parents[2]
OLD=P.parent/'reference-reconstruction-01'
source=ROOT/'references/reconstruction/study/selected-mobile.mp4'
duration=164/30
sys.path.insert(0,str(ROOT/'scripts'))
from motif_produce import loudness
def run(args):return subprocess.check_output(args,stderr=subprocess.PIPE)
def stream_hash(path,kind):
    return run(['ffmpeg','-v','error','-i',str(path),'-map',f'0:{kind}:0','-c','copy','-f','hash','-hash','sha256','-']).decode().strip()
def probe(path):
    return json.loads(run(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_type,width,height,nb_frames,r_frame_rate,duration','-of','json',str(path)]))
def frame(path,n,width=360):
    data=run(['ffmpeg','-v','error','-i',str(path),'-vf',f'select=eq(n\\,{n}),scale={width}:-1','-frames:v','1','-f','image2pipe','-vcodec','png','-'])
    return Image.open(io.BytesIO(data)).convert('RGB')
def scene(im):
    r,g,b=im.getpixel((im.width//2,im.height//16))
    return ('terminal' if max(r,g,b)<100 else 'scanner' if r>g*1.05 else 'wash'),[r,g,b]
for name,first in [('final',P/'renders/picture-full-coordinated.mp4'),('mobile',P/'renders/picture-mobile-coordinated.mp4')]:
    output=P/'renders'/f'{name}.mp4'
    run(['ffmpeg','-hide_banner','-y','-i',str(first),'-i',str(OLD/'renders/final.mp4'),'-map','0:v:0','-map','1:a:0','-c','copy','-t',str(duration),'-movflags','+faststart',str(output)])
    assert stream_hash(first,'v')==stream_hash(output,'v')
    assert stream_hash(OLD/'renders/final.mp4','a')==stream_hash(output,'a')
labels=P/'review/comparison-labels.png'
shutil_labels=OLD/'review/comparison-labels.png'
labels.write_bytes(shutil_labels.read_bytes())
comp=P/'renders/comparison.mp4'
run(['ffmpeg','-hide_banner','-y','-i',str(source),'-i',str(P/'renders/mobile.mp4'),'-loop','1','-i',str(labels),'-filter_complex','[0:v][1:v]hstack=inputs=2,pad=720:680:0:40:color=0x1b2528[v];[v][2:v]overlay=0:0[out]','-map','[out]','-map','1:a:0','-frames:v','164','-c:v','libx264','-crf','18','-c:a','copy','-movflags','+faststart',str(comp)])
assert stream_hash(comp,'a')==stream_hash(OLD/'renders/final.mp4','a')
result={'frames':164,'fps':30,'sourceInterval':[436,600],'unchangedSoundtrack':True,'retiming':False,'cuts':{},'media':{},'audio':loudness(P/'renders/final.mp4'),'subjectiveListening':'unassessed'}
assert abs(result['audio']['integrated_lufs']+16)<=.8
assert result['audio']['true_peak_dbtp']<=-1.5
for name,dims in [('final',(1080,1920)),('mobile',(360,640)),('comparison',(720,680))]:
    j=probe(P/'renders'/f'{name}.mp4');v=next(s for s in j['streams'] if s['codec_type']=='video')
    assert (v['width'],v['height'])==dims
    assert int(v['nb_frames'])==164 and v['r_frame_rate']=='30/1'
    assert abs(float(v['duration'])-duration)<.001
    result['media'][name]=j
font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',13)
expected={49:'wash',50:'terminal',51:'terminal',87:'terminal',88:'scanner',89:'scanner'}
sheet=Image.new('RGB',(570,358*6),'#182127');d=ImageDraw.Draw(sheet)
for row,(n,kind) in enumerate(expected.items()):
    result['cuts'][str(n)]={}
    for col,(name,path) in enumerate([('reference',source),('full',P/'renders/final.mp4'),('mobile',P/'renders/mobile.mp4')]):
        im=frame(path,n);label,color=scene(im)
        assert label==kind,(name,n,label,kind,color)
        result['cuts'][str(n)][name]={'scene':label,'backgroundPixel':color}
        im.save(P/'review'/f'cut-{n}-{name}.png')
        sheet.paste(im.resize((180,320),Image.Resampling.LANCZOS),(col*190,row*358+29))
        d.text((col*190+4,row*358+5),f'{name} / frame {n}',font=font,fill='white')
sheet.save(P/'review/cut-verification.jpg',quality=93)
# Six decisive comparisons plus both sides of the first cut.
selected=[49,50,51,79,88,132,144,156]
sheet=Image.new('RGB',(760,368*4),'#182127');d=ImageDraw.Draw(sheet)
for i,n in enumerate(selected):
    x=(i%2)*380;y=(i//2)*368
    d.text((x+8,y+6),f'Reference | Motif   local f{n} / {n/30:.2f}s',font=font,fill='white')
    for col,path in enumerate((source,P/'renders/mobile.mp4')):
        im=frame(path,n);im.save(P/'review'/f'pair-{n}-{col}.png')
        sheet.paste(im.resize((180,320),Image.Resampling.LANCZOS),(x+8+col*184,y+30))
sheet.save(P/'review/matching-frames.jpg',quality=93)
(P/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
(P/'review/playback.html').write_text('''<!doctype html><html><head><meta charset="utf-8"></head><body style="margin:8px;background:#182127;color:white;font-family:sans-serif"><h2>Reference / Motif finishing pass · 1×</h2><video controls autoplay loop muted style="width:100%;max-width:720px" src="../renders/comparison.mp4"></video><p>Reference left, Motif right. Same 164 frames, reconstruction audio only.</p><h2>Native 360 × 640</h2><video controls autoplay loop muted width="360" height="640" src="../renders/mobile.mp4"></video></body></html>''')
print(json.dumps({'audio':result['audio'],'encodedCuts':'all six expected boundary frames match source in full and mobile','duration':duration,'soundtrack':'unchanged AAC'},indent=2))
