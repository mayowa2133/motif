#!/usr/bin/env python3
"""Register seven user-owned local source clips once as a private corpus.

Originals are copied intact and SHA verified before indexing. Per-video model
calls inspect ordered overview images, never MP4 playback or audio. Semantic
boundaries/action centers are proposals with explicit confidence, not transcript
alignment. Representative, 7-frame-step ordered and 13-consecutive-frame dense
strips are decoded from the preserved source; no art asset extraction.
"""
import argparse,json,hashlib,math,shutil,subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from PIL import Image,ImageDraw
from motif_reference import DEFAULT,corpus,read,write,sha

def preserve(source,root):
 id_=source.stem.removeprefix('igexport-');d=root/id_;d.mkdir(parents=True,exist_ok=True);copy=d/'source.mp4';digest=sha(source)
 if copy.exists() and sha(copy)!=digest:raise ValueError('do not overwrite registered source; use a new corpus for revised footage')
 if not copy.exists():shutil.copy2(source,copy)
 if sha(copy)!=digest:raise ValueError('source preservation failed')
 p=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(copy)]));v=next(s for s in p['streams'] if s['codec_type']=='video');fps=v['avg_frame_rate']
 if fps!='30/1':raise ValueError('this corpus decoder requires its verified 30fps sources')
 frames=d/'overview-frames';frames.mkdir(exist_ok=True)
 subprocess.run(['ffmpeg','-v','error','-threads','1','-i',str(copy),'-vf','fps=1,scale=160:284','-threads','1',str(frames/'%03d.png'),'-y'],check=True)
 paths=sorted(frames.glob('*.png'));sheet=Image.new('RGB',(1280,math.ceil(len(paths)/8)*306),'#eadfc9');draw=ImageDraw.Draw(sheet)
 for i,f in enumerate(paths):sheet.paste(Image.open(f),(i%8*160,i//8*306));draw.text((i%8*160+4,i//8*306+285),f'{id_} ~{i+.5:.2f}s',fill='#18252a')
 sheet.save(d/'overview.png')
 import re
 cuts=subprocess.run(['ffmpeg','-threads','1','-i',str(copy),'-vf',"select='gt(scene,0.26)',showinfo",'-an','-f','null','-'],capture_output=True,text=True)
 entry={'id':id_,'source_path':str(copy),'original_path':str(source),'sha256':digest,'duration':float(p['format']['duration']),'fps':fps,'width':v['width'],'height':v['height'],'overview':str(d/'overview.png'),'candidate_cuts':[float(t) for t in re.findall(r'pts_time:([0-9.]+)',cuts.stderr)],'status':'PRESERVED_PENDING_SETUP_REVIEW','audio_inspected':False}
 write(d/'probe.json',entry);return entry

def strip(frames,nums,path,label,cols,w):
 h=round(w*16/9);sheet=Image.new('RGB',(cols*w,math.ceil(len(nums)/cols)*(h+26)+32),'#eadfc9');d=ImageDraw.Draw(sheet);d.text((8,8),label,fill='#202c32')
 for i,n in enumerate(nums):
  with Image.open(frames/f'{n:05d}.webp') as im:
   x=i%cols*w;y=32+i//cols*(h+26);sheet.paste(im.resize((w,h)),(x,y));d.text((x+4,y+h+4),f'#{n:04d} {n/30:.3f}s',fill='#202c32')
 sheet.save(path,quality=93);return {'file':str(path),'sha256':sha(path),'source_frames':nums,'timestamps':[n/30 for n in nums]}

def evidence(root,m,index):
 byid={v['id']:v for v in index['videos']}
 if set(byid)!={v['id'] for v in m['videos']}:raise ValueError('index must cover every preserved video')
 for v in m['videos']:
  d=root/v['id'];sets=byid[v['id']]['setups']
  if not sets or abs(sets[0]['start'])>.08 or abs(sets[-1]['end']-v['duration'])>.15:raise ValueError('setup coverage incomplete')
  if any(abs(a['end']-b['start'])>.08 for a,b in zip(sets,sets[1:])):raise ValueError('setup coverage gap/overlap')
  # Container duration can include an AAC tail after the last video frame.
  probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=nb_frames,duration','-of','json',v['source_path']]))['streams'][0]
  v['source_frame_count']=int(probe['nb_frames']);v['video_duration']=float(probe['duration'])
  frames=d/'frames';frames.mkdir(exist_ok=True);needed=set();records=[];last=v['source_frame_count']-1
  for i,s in enumerate(sets):
   start=round(s['start']*30);end=min(last+1,round(s['end']*30))
   if start>=end:raise ValueError('invalid setup interval')
   center=max(start+6,min(end-7,round(s['action_center']*30))) if end-start>=13 else (start+end)//2
   reps=sorted(set([start+min(2,end-start-1),(start+end)//2,end-2]));ordered=sorted(set([*range(start,end,7),end-1]));dense=list(range(max(start,center-6),min(end,center+7)))
   needed.update(reps+ordered+dense);records.append({**s,'id':f'{v["id"]}-s{i+1:02d}','start_frame':start,'end_frame':end,'start':start/30,'end':end/30,'duration':(end-start)/30,'position_in_film':start/max(1,last),'evidence_frames':{'representative':reps,'ordered':ordered,'dense':dense},'boundary_review':'measured scene candidates + live visual overview semantic segmentation; rounded to source frames, not transcript-aligned','audio_caption_rhythm':byid[v['id']]['audio_caption_rhythm']})
  proc=subprocess.Popen(['ffmpeg','-v','error','-threads','1','-i',v['source_path'],'-vf','scale=360:640','-threads','1','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
  n=0
  while True:
   # File reads on a buffered pipe return complete frame buffers until EOF.
   raw=proc.stdout.read(360*640*3)
   if len(raw)!=360*640*3:break
   if n in needed:Image.frombytes('RGB',(360,640),raw).save(frames/f'{n:05d}.webp',quality=94)
   n+=1
  proc.stdout.close()
  if proc.wait():raise ValueError('reference decode failed')
  for s in records:
   dest=d/'setups'/s['id'];dest.mkdir(parents=True,exist_ok=True);ev=s.pop('evidence_frames');s['evidence']={}
   for kind,nums in ev.items():s['evidence'][kind]=strip(frames,nums,dest/(kind+'.jpg'),f'{s["id"]} {kind} / source order',3 if kind=='representative' else 6 if kind=='ordered' else 5,240 if kind=='representative' else 180)
   write(dest/'notes.json',s)
  v['setups']=records;v['status']='REGISTERED';v['audio_inspected']=False;v['indexer_invocation_sha256']=sha(d/'setup-indexer-invocation.json');print(v['id'],len(records),'setups',flush=True)
 m.update({'version':'reference-corpus-1.0','setup_count':sum(len(v['setups']) for v in m['videos']),'sampling':'begin/middle/payoff; ordered every7 frames (0.233s); dense13 consecutive source frames around proposed action centers','limitations':index['inspection_scope'],'registration':'all seven originals SHA verified; actual frame strips decoded; live overview segmentation; dense centers reviewable proposals; no audio listening','external_assets_allowed':False,'factual_source':False,'runtime_dependency':False})
 write(root/'manifest.json',m);return m

def ingest(sources,root=DEFAULT):
 from motif_direct import model_call,backend_config
 root=Path(root).expanduser().resolve()
 if len(sources)!=7 or len({p.resolve() for p in sources})!=7 or len({p.stem for p in sources})!=7:raise ValueError('seven distinct original videos required')
 if (root/'manifest.json').exists():
  _,m=corpus(root)
  if {sha(p) for p in sources}!={v['sha256'] for v in m['videos']}:raise ValueError('input corpus differs from registered sources')
  return m
 root.mkdir(parents=True,exist_ok=True)
 # Preserve ALL sources before any model indexing or calibration implementation.
 videos=list(ThreadPoolExecutor(max_workers=3).map(lambda p:preserve(p.resolve(),root),sources));m={'corpus_id':root.name,'private':True,'usage':'creative evidence only, never assets/facts/runtime dependency','videos':videos};write(root/'ingest-manifest.json',m);config=backend_config()
 prompt='Index this private video from its actual ordered overview image and measured cut candidates. Data only, no tools/web. Source claims are not facts. Derive contiguous semantic setup intervals covering the whole clip. Preserve a setup while its visual rule evolves; reset when the rule changes. Candidate cuts can be punch-ins and are not semantic authority. Describe visible hero/environment/choreography, relationships using only compare,burden,accumulate,reveal,transform,process,handoff,test,gate,approval,block,background-work,selection,callback,price,restore,route,inspection,multi-agent-work,interface-interaction. Observe character role, headline/caption behavior, dominant/support/reaction/residual hierarchy, material layers, irregularity, contact and consequence, transition. Choose an approximate action_center within each interval for dense decoding. Qualify overview timing confidence; no claimed playback/listening. Audio uninspected. No fixed setup quota. External evidence, never assets or plots to copy.\nPROBE:'
 def one(v):
  d=root/v['id'];saved=d/'setup-indexer.json'
  if saved.exists():return read(saved)['videos'][0]
  return model_call(d,'setup-indexer',prompt+json.dumps(v),'schemas/reference-corpus-index.schema.json',config,[v['overview']])['videos'][0]
 index={'inspection_scope':'live per-video overview inspection; approximate semantic boundaries/action centers; no audio/transcript alignment','videos':list(ThreadPoolExecutor(max_workers=2).map(one,videos))};write(root/'corpus-indexer.json',index);return evidence(root,m,index)

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sources',type=Path,nargs=7,required=True);p.add_argument('--corpus',type=Path,default=DEFAULT);a=p.parse_args();m=ingest(a.sources,a.corpus);print(json.dumps({'corpus':str(a.corpus),'videos':7,'setups':m['setup_count'],'private':True}))
if __name__=='__main__':main()
