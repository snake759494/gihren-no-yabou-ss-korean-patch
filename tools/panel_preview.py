import sys,json,os;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cont import parse
from uilabel import *
import numpy as np
from PIL import Image
W=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P=json.load(open(os.path.join(W,'ui','panels_ko.json'),encoding='utf8'))
outs=[]
for f,c in P.items():
    r=parse(open(os.path.join(W,'dec',f+'.bin'),'rb').read())
    for k,items in c.items():
        a=dec_lab(r.kids[int(k)].data); n=a
        for it in items:
            y0,y1,x0,x1,t=it[:5]; tx=it[5] if len(it)>5 else None; fn=it[6] if len(it)>6 else None; rf=it[7] if len(it)>7 else None
            n=bar2(n,y0,y1,x0,x1,t,tx,font=fn,ref=rf)
        outs.append(np.hstack([a,np.zeros((a.shape[0],3),np.uint8),n]))
Wd=max(o.shape[1] for o in outs); H=sum(o.shape[0]+3 for o in outs)
c=np.zeros((H,Wd),np.uint8); y=0
for o in outs: c[y:y+o.shape[0],:o.shape[1]]=o; y+=o.shape[0]+3
Image.fromarray((c*17).astype(np.uint8)).resize((Wd*2,H*2),Image.NEAREST).save(os.path.join(W,'shots','panel_preview.png'))
im=Image.open(os.path.join(W,'shots','panel_preview.png')); h=im.height
im.crop((0,0,im.width,h//2+10)).save(os.path.join(W,'shots','pp1.png')); im.crop((0,h//2-10,im.width,h)).save(os.path.join(W,'shots','pp2.png'))
