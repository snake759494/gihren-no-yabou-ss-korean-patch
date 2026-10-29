import struct,numpy as np
from PIL import Image,ImageDraw,ImageFont
import os
W=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FB=ImageFont.truetype(os.path.join(W,'fonts','Galmuri11.ttf'),12)
FS=ImageFont.truetype(os.path.join(W,'fonts','Galmuri9.ttf'),10)
INK=2
def arr_from(out):
    w,h=struct.unpack_from('>HH',out,0); px=out[4:]+b'\0'*(w*h//2+8)
    b=np.frombuffer(px[:w*h//2],np.uint8)
    a=np.empty(w*h,np.uint8); a[0::2]=b>>4; a[1::2]=b&15
    return a.reshape(h,w)
def bytes_from(a):
    h,w=a.shape; f=a.reshape(-1)
    return struct.pack('>HH',w,h)+bytes(((f[0::2]<<4)|f[1::2]).astype(np.uint8))
def wrap(text,font,width):
    lines=[]
    for para in text.split('\n'):
        lead=len(para)-len(para.lstrip(' '))
        indent=font.getlength(' ')*lead
        words=para.strip(' ').split(' ')
        cur=' '*lead
        for wd in words:
            t=(cur+(' ' if cur.strip() else '')+wd)
            if font.getlength(t)<=width or not cur.strip(): cur=t
            else:
                # word too long for remaining: try char-level break for long words
                lines.append(cur); cur=' '*lead+wd
            while font.getlength(cur)>width:
                # hard split
                k=len(cur)
                while k>0 and font.getlength(cur[:k])>width: k-=1
                lines.append(cur[:k]); cur=' '*lead+cur[k:]
        lines.append(cur)
    return lines
def draw_text(a,x,y,text,font,ink=INK):
    h,w=a.shape
    im=Image.new('L',(w,h),0); ImageDraw.Draw(im).text((x,y),text,font=font,fill=255)
    m=np.asarray(im)>127
    a[m]=ink
def render(out,title,body):
    a=arr_from(out).copy(); h,w=a.shape
    # --- title bar ---
    has_title = a[10,7]==13 and a[5,7]==12
    if title is not None and has_title:
        x1=6
        while x1<w and a[5,x1]==12: x1+=1
        for x in range(6,x1-1):
            a[6,x]=12 if x%2==0 else 13; a[16,x]=12 if x%2==0 else 13
            a[7:16,x]=13
        draw_text(a,10,5,title,FB)
    # --- body ---
    y0=23
    # body rows: find bottom frame (row where col 10 != 14 below y0)
    y1=y0
    while y1<h and a[y1,8]==14: y1+=1
    # clear text within body (non-14 pixels between x=7..w-8, rows y0..y1)
    x0=7; xr=w-1
    while xr>x0 and a[(y0+y1)//2,xr]!=14: xr-=1
    sub=a[y0:y1,x0:xr+1]; sub[sub!=14]=14
    width=xr-x0-6
    for font,pitch,top in [(FB,15,27),(FB,13,26),(FS,12,26),(FS,11,25)]:
        lines=wrap(body,font,width)
        cap=(y1-top-11)//pitch+1
        if len(lines)<=cap: break
    else:
        raise ValueError(f'overflow {len(lines)}>{cap}: {body[:30]}')
    for i,l in enumerate(lines):
        draw_text(a,x0+3,top-1+i*pitch,l,font)
    return bytes_from(a),(font is FB,pitch,len(lines),cap)
