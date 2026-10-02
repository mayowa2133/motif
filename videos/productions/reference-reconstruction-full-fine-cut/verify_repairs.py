"""Bounded encoded-pixel proofs for the two observed rough defects."""
from pathlib import Path
import json,math,subprocess
import numpy as np
P=Path(__file__).resolve().parent
checks={}
for name,scale in [('full-film-fine-cut',1),('mobile',1/3)]:
    path=P/'renders'/(name+'.mp4')
    x0=round(703*scale);y0=round(510*scale);w=round(260*scale)//2*2;h=round(280*scale)//2*2
    raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-vf',f'trim=end_frame=110,crop={w}:{h}:{x0}:{y0},format=rgb24','-f','rawvideo','-'])
    frames=np.frombuffer(raw,dtype=np.uint8).reshape(110,h,w,3);pixels=[]
    for f,im in enumerate(frames):
        q=max(0,min(1,(f/30-.9)/1.7));angle=math.radians(117*(1-(1-q)**3))
        px=-89*math.cos(angle)+56*math.sin(angle);py=-89*math.sin(angle)-56*math.cos(angle)
        cx=round((833+.75*px)*scale)-x0;cy=round((650+.75*py)*scale)-y0;r=3 if scale<1 else 7
        patch=im[cy-r:cy+r+1,cx-r:cx+r+1];n=int(np.sum(np.max(patch,axis=2)<90))
        assert n>= (2 if scale<1 else 10),(name,f,n)
        pixels.append(n)
    # Native/full common-baseline bar heights from an unlabelled interior column.
    raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-vf','select=eq(n\\,1098),format=rgb24','-frames:v','1','-f','rawvideo','-'])
    iw=round(1080*scale);ih=round(1920*scale);im=np.frombuffer(raw,dtype=np.uint8).reshape(ih,iw,3)
    bars=[]
    for x,rgb in [(265,[181,87,59]),(700,[109,171,161])]:
        col=im[:,round(x*scale)].astype(float);near=(np.linalg.norm(col-np.array(rgb),axis=1)<45) & ((col[:,0]-col[:,1]>45) if rgb[0]>rgb[1] else (col[:,1]-col[:,0]>35))
        a=None;runs=[]
        for i,v in enumerate(near):
            if v and a is None:a=i
            elif not v and a is not None:runs.append((a,i));a=None
        if a is not None:runs.append((a,len(col)))
        top,bottom=max(runs,key=lambda v:v[1]-v[0]);bars.append({'top':top,'baselineEdge':bottom,'height':bottom-top})
    ratio=bars[1]['height']/bars[0]['height'];assert .895<ratio<.925,(name,bars,ratio)
    assert abs(bars[0]['baselineEdge']-bars[1]['baselineEdge'])<=2
    checks[name]={'gymNeedle':{'framesChecked':110,'visibleAtPredictedNeedleRegionEveryFrame':True,'minimumDarkPixels':min(pixels),'basis':'decoded pixels near 75% of fixed-pivot pointer length; dark-ink threshold','limit':'bounded needle check, not all motion/contact assertions'},'cost':{'decodedBars':bars,'heightRatio':ratio,'authoredHeightRatio':.91,'sameBaselineWithinPixels':abs(bars[0]['baselineEdge']-bars[1]['baselineEdge']),'qualifier':'Illustrative source-claim index; no measured product cost result'}}
(P/'review/encoded-repairs.json').write_text(json.dumps(checks,indent=2)+'\n')
print(json.dumps(checks,indent=2))
