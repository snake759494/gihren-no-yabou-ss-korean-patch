import os,sys,struct,numpy as np
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from PIL import Image,ImageDraw,ImageFont
from uilabel import G11,G9,text_mask
from mfd import lz_dec
from lzenc import compress
def decode_kid(x):
    mark,g=struct.unpack_from('>HH',x,0); out=bytes(lz_dec(x,4,g,len(x))[0])
    w,h=struct.unpack_from('>HH',out,4); pix=out[8:]+bytes(w*h//2)
    b=np.frombuffer(pix[:w*h//2],np.uint8); a=np.empty(w*h,np.uint8); a[0::2]=b>>4; a[1::2]=b&15
    return mark,out[:8],a.reshape(h,w)
def encode_kid(mark,hdr,a):
    f=a.reshape(-1).astype(np.uint8); out=hdr+bytes((f[0::2]<<4)|f[1::2])
    c,g,_=compress(out); return struct.pack('>HH',mark,g)+c
def wrap(text,font,width):
    lines=[];cur=''
    for wd in text.split(' '):
        t=(cur+' '+wd) if cur else wd
        if font.getlength(t)<=width: cur=t; continue
        if cur: lines.append(cur)
        cur=wd
        while font.getlength(cur)>width:
            k=len(cur)
            while k>1 and font.getlength(cur[:k])>width: k-=1
            lines.append(cur[:k]); cur=cur[k:]
    if cur: lines.append(cur)
    return lines
def render(a,title,body,ink=1,bg=15):
    h,w=a.shape
    out=np.full_like(a,bg)
    out[23]=a[23]          # keep the title underline
    tf=G11 if G11.getlength(title)<=w-4 else G9
    bb=tf.getbbox(title); th=bb[3]-bb[1]
    out[text_mask(title,tf,w,h,3,9+(12-th)//2-bb[1])]=ink
    for font,pitch,top in ((G11,15,30),(G11,14,29),(G11,13,28),(G9,12,28),(G9,11,27)):
        lines=wrap(body,font,w-6)
        if top+pitch*(len(lines)-1)+12<=h: break
    for i,l in enumerate(lines):
        out[text_mask(l,font,w,h,3,top+i*pitch)]=ink
    return out,(font is G11,pitch,len(lines))
