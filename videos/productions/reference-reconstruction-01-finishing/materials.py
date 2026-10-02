"""Quiet full-canvas materials; deterministic and original, no extracted pixels."""
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
P=Path(__file__).resolve().parent/'assets/materials'
P.mkdir(parents=True,exist_ok=True)
N=2048
for index,name in enumerate(('paper','card','wood','wall')):
    rng=np.random.default_rng(90713+index)
    rgba=np.zeros((N,N,4),dtype=np.uint8)
    field=rng.normal(0,1,(N,N))
    cloud=np.asarray(Image.fromarray(np.uint8(rng.random((5,5))*255)).resize((N,N),Image.Resampling.BICUBIC),dtype=float)-127.5
    field=field*({'paper':1.3,'card':.8,'wood':1.2,'wall':1.1}[name])+cloud*.012
    light=np.where(field>0,242,37).astype(np.uint8)
    rgba[:,:,:3]=light[:,:,None]
    rgba[:,:,3]=np.clip(np.abs(field)*2,0,9).astype(np.uint8)
    im=Image.fromarray(rgba);draw=ImageDraw.Draw(im)
    if name=='paper':
        for _ in range(2100):
            x,y=rng.integers(0,N,2);length=int(rng.integers(2,9))
            draw.line((int(x),int(y),int(x)+length,int(y)-1),fill=(110,89,68,9),width=1)
    elif name=='wood':
        for i in range(100):
            y=int(rng.integers(0,N));x=int(rng.integers(0,N-250));length=int(rng.integers(80,400))
            draw.line((x,y,x+length,y+int(rng.integers(-3,4))),fill=(205,177,140,7),width=1)
    im.save(P/(name+'.png'))
print('Quiet 2048px materials created; no 512px repetition.')
