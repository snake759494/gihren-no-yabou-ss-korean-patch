import sys,os,struct;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image
def load(r):
    mp=r.kids[1].data; w,h=struct.unpack_from('>HH',mp,0); m=np.array(struct.unpack_from('>%dH'%(w*h),mp,4)).reshape(h,w)
    cells=r.kids[2].data; sz=struct.unpack_from('>I',cells,0)[0]; cd=cells[4:4+sz]
    v=struct.unpack_from('>256H',r.kids[0].data,4); pal=np.array([[(c&31)*8,((c>>5)&31)*8,((c>>10)&31)*8] for c in v],np.float32)
    img=np.zeros((h*8,w*8),np.uint8)
    for y in range(h):
        for x in range(w):
            ci=m[y,x]//2; img[y*8:y*8+8,x*8:x*8+8]=np.frombuffer(cd[ci*64:ci*64+64],np.uint8).reshape(8,8)
    return img,pal,m
def store(r,img):
    h,w=img.shape[0]//8,img.shape[1]//8
    cells=[]; idx={}; m=np.zeros((h,w),int)
    for y in range(h):
        for x in range(w):
            t=img[y*8:y*8+8,x*8:x*8+8].tobytes()
            if t not in idx: idx[t]=len(cells); cells.append(t)
            m[y,x]=idx[t]*2
    mp=r.kids[1].data
    r.kids[1].data=mp[:4]+struct.pack('>%dH'%(w*h),*m.reshape(-1))+mp[4+w*h*2:]
    cd=b''.join(cells); old=r.kids[2].data; oldsz=struct.unpack_from('>I',old,0)[0]
    r.kids[2].data=struct.pack('>I',len(cd))+cd+old[4+oldsz:]
    return len(cells)
from PIL import ImageDraw,ImageFont
W=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT=os.path.join(os.path.dirname(W),'NanumSquareNeo-cBd.ttf')
def wrap(text,font,width):
    lines=[]
    for para in text.split('\n'):
        cur=''
        for wd in para.split(' '):
            t=(cur+' '+wd) if cur else wd
            if font.getlength(t)<=width: cur=t
            else: lines.append(cur); cur=wd
        lines.append(cur)
    return lines
def retext_bram(img,pal,text,rect=(18,58,226,178),top=66,pitch=16,size=14,highlight=None,wrapw=188):
    x0,y0,x1,y1=rect
    rgb=pal[img]
    sub=rgb[y0:y1,x0:x1]
    green=(sub[...,1]>sub[...,0]+8)&(sub[...,1]>sub[...,2]+8)&(sub[...,0]<150)
    red=(sub[...,0]>sub[...,1]+60)&(sub[...,0]>sub[...,2]+60)
    vals,cnt=np.unique(img[y0:y1,x0:x1],return_counts=True); black=int(vals[cnt.argmax()])
    gi=img[y0:y1,x0:x1][green]; gv,gc=np.unique(gi,return_counts=True); ink=int(gv[gc.argmax()])
    out=img.copy(); s=out[y0:y1,x0:x1]
    s[green|red]=black
    font=ImageFont.truetype(FONT,size)
    lines=wrap(text,font,wrapw or (x1-x0-6))
    S=4; big=Image.new('L',((x1-x0)*S,(y1-y0)*S),0); d=ImageDraw.Draw(big); fb=ImageFont.truetype(FONT,size*S)
    for i,l in enumerate(lines):
        d.text((3*S,(top-y0+i*pitch)*S),l,font=fb,fill=255)
    al=np.asarray(big.resize((x1-x0,y1-y0),Image.LANCZOS),np.float32)/255
    used=np.unique(img); up=pal[used]
    tgt=pal[black]*(1-al[...,None])+pal[ink]*al[...,None]
    q=used[((tgt[...,None,:]-up[None,None,:,:])**2).sum(-1).argmin(-1)]
    canw=(s==black)
    s[canw&(al>0.15)]=q[canw&(al>0.15)]
    return out,len(lines)
