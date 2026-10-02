"""Original deterministic cut-paper surfaces; no extracted reference pixels."""
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter
P=Path(__file__).resolve().parent/'assets/materials'
P.mkdir(parents=True,exist_ok=True)
for index,name in enumerate(('paper','card','wood','wall')):
    rng=np.random.default_rng(713+index)
    field=np.zeros((512,512),dtype=float)
    for dimension,weight in ((8,1.2),(22,.8),(78,.4),(512,.25)):
        low=Image.fromarray(np.uint8(rng.random((dimension,dimension))*255)).resize((512,512),Image.Resampling.BICUBIC)
        field+=(np.asarray(low,dtype=float)-127.5)*weight
    field+=rng.normal(0,8,(512,512))
    if name=='wood':
        y,x=np.mgrid[0:512,0:512]
        field+=np.sin(y*.21+np.sin(x*.012)*2)*17
    if name=='paper':
        field=field*.5+rng.normal(0,5,(512,512))
    if name=='card':field*=.7
    rgba=np.zeros((512,512,4),dtype=np.uint8)
    light=np.where(field>0,238,41).astype(np.uint8)
    rgba[:,:,:3]=light[:,:,None]
    rgba[:,:,3]=np.clip(np.abs(field)*({'wall':.35,'wood':.27,'card':.22,'paper':.14}[name]),0,32).astype(np.uint8)
    Image.fromarray(rgba).save(P/(name+'.png'))
print('Created four distinct original material tiles')
