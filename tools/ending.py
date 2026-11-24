"""ENDINGxx.MFD entry1: the scrolling ending text, a 280x960 4bpp image (u16 W,H + pixels).
Palette (entry0): 0 transparent, 1 white .. 14 dark grey, 15 black outline.
Original layout: title centred on row 0, lines every ~21.8 px, 16 px glyphs with a 1 px black outline."""
import struct, os, json, numpy as np
from PIL import Image, ImageDraw, ImageFont
W_=280; H_=960; PITCH=21.8; MAXW=274
FONT=os.path.join('D:/ss/기렌의야망','NanumSquareNeo-cBd.ttf')
def wrap(text,f):
    out=[]; cur=''
    for ch in text:
        if f.getlength(cur+ch)>MAXW:
            # break at the last space when it keeps the line reasonably full
            sp=cur.rfind(' ')
            if ch!=' ' and sp>len(cur)*0.6: out.append(cur[:sp]); cur=cur[sp+1:]+ch
            else: out.append(cur); cur='' if ch==' ' else ch
        else: cur+=ch
    out.append(cur)
    return [l.strip() for l in out]
def render(paras,size=15):
    S=4; f=ImageFont.truetype(FONT,size); fb=ImageFont.truetype(FONT,size*S)
    lines=[]
    for i,p in enumerate(paras):
        if i==0: lines.append(('c',p)); continue
        if not p: lines.append(('l','')); continue
        for l in wrap(p,f): lines.append(('l',l))
    big=Image.new('L',(W_*S,H_*S),0); d=ImageDraw.Draw(big)
    asc,desc=fb.getmetrics()
    for i,(al,t) in enumerate(lines):
        y=int(round(i*PITCH))
        if y+18>H_: raise ValueError('ending text too long')
        x=(W_-f.getlength(t))/2 if al=='c' else 2
        d.text((x*S,(y+1)*S+(16*S-(asc+desc))//2),t,font=fb,fill=255)
    a=np.asarray(big.resize((W_,H_),Image.LANCZOS),float)/255
    m=a>=0.45
    o=np.zeros_like(m)
    for dy in(-1,0,1):
        for dx in(-1,0,1): o|=np.roll(np.roll(m,dy,0),dx,1)
    # vertical shading like the original: brighter at the top of each line
    yy=np.arange(H_)[:,None]; ly=np.zeros((H_,1))
    for i in range(len(lines)):
        y=int(round(i*PITCH)); ly[y:y+18,0]=np.arange(min(18,H_-y))
    shade=(1+np.clip(ly*0.3,0,5)).astype(np.uint8)*np.ones((1,W_),np.uint8)
    q=np.where(m,shade,np.where(o,15,0)).astype(np.uint8)
    return q,len(lines)
def pack(q):
    flat=q.reshape(-1)
    return struct.pack('>HH',W_,H_)+bytes((flat[0::2]<<4)|flat[1::2])
def load(W):
    return json.load(open(os.path.join(W,'ending','ko.json'),encoding='utf8'))
