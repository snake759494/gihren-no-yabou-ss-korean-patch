from PIL import Image,ImageDraw,ImageFont
import numpy as np
FONTDIR='D:/ss/기렌의야망/'
_fc={}
def font(name,size):
    k=(name,size)
    if k not in _fc: _fc[k]=ImageFont.truetype(FONTDIR+name,size)
    return _fc[k]
def render_line(text,fname='NanumSquareNeo-bRg.ttf',size=15,yoff=0,maxcells=20,tracking=0,outline=False):
    f=font(fname,size)
    # measure with tracking
    W=0; xs=[]
    for ch in text:
        xs.append(W); W+=f.getlength(ch)+tracking
    W=int(np.ceil(W))
    cells=max(1,(W+15)//16)
    S=4  # supersample for crisp AA
    big=Image.new('L',(cells*16*S,16*S),0); d=ImageDraw.Draw(big)
    fb=font(fname,size*S)
    asc,desc=fb.getmetrics()
    base=(16*S-(asc+desc))//2+yoff*S
    for ch,x in zip(text,xs):
        d.text((x*S,base),ch,font=fb,fill=255)
    im=big.resize((cells*16,16),Image.LANCZOS)
    a=np.asarray(im,float)/255
    q=np.clip(np.round(a*15),0,15).astype(np.uint8)
    if outline:
        m=q>=8; o=np.zeros_like(m)
        for dy in(-1,0,1):
            for dx in(-1,0,1): o|=np.roll(np.roll(m,dy,0),dx,1)
        q=np.where(m,4,np.where(o,11,0)).astype(np.uint8)
    return q,cells
def to_strip(q):
    """convert HxW (16 x cells*16) index array -> vertical strip bytes (16 x 16*cells) 4bpp"""
    cells=q.shape[1]//16; out=bytearray()
    for c in range(cells):
        g=q[:,c*16:(c+1)*16]
        for y in range(16):
            for x in range(0,16,2): out.append((int(g[y,x])<<4)|int(g[y,x+1]))
    return bytes(out),cells
