import sys,os,json,struct;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cont import parse
from retext import retext,palette,decode
import numpy as np
from PIL import Image
W=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cfg=json.load(open(os.path.join(W,'ui','ui_ko.json'),encoding='utf8'))
rows=[]
for dec,c in cfg.items():
    r=parse(open(os.path.join(W,'dec',dec+'.bin'),'rb').read())
    for k,it in c['items'].items():
        k=int(k); pi=int(c['pal'][str(k)]); pal=palette(r.kids[pi].data)
        hd=c.get('hdr',0); raw=r.kids[k].data[hd:]
        a0,_=decode(raw)
        nb,res=retext(raw,pal,it['box'],it['text'],it['font'],it['size'],it.get('align','left'),it.get('outline',True),glow=it.get('glow',False),xoff=it.get('xoff',0),rowmode=it.get('rowmode'))
        rows.append(np.hstack([pal[a0],np.zeros((a0.shape[0],4,3)),pal[res]]).astype(np.uint8))
Wd=max(x.shape[1] for x in rows); H=sum(x.shape[0]+3 for x in rows)
c=np.zeros((H,Wd,3),np.uint8); y=0
for x in rows: c[y:y+x.shape[0],:x.shape[1]]=x; y+=x.shape[0]+3
Image.fromarray(c).resize((Wd*2,H*2),Image.NEAREST).save(os.path.join(W,'shots','ui_preview.png'))
