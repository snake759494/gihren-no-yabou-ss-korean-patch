"""MAP*_Z entry0: global-map NBG1 frame (kid3 = 4bpp cells, kid4 = 44x28 cell map, kid5 = palette)
with the baked 拠点表示 button and L/R/START help. Same data in every MAP*_Z file."""
import struct, numpy as np
def unpack(kids):
    cb=kids[3].data; n=struct.unpack_from('>I',cb,0)[0]; cells=cb[4:4+n]
    W,H=struct.unpack_from('>HH',kids[4].data,0); mp=list(struct.unpack_from('>%dH'%(W*H),kids[4].data,4))
    img=np.zeros((H*8,W*8),np.uint8)
    for i,c in enumerate(mp):
        t=np.frombuffer(cells[c*32:c*32+32],np.uint8); a=np.empty(64,np.uint8); a[0::2]=t>>4; a[1::2]=t&15
        y,x=divmod(i,W); img[y*8:y*8+8,x*8:x*8+8]=a.reshape(8,8)
    return img,W,H
def palette(kids):
    v=struct.unpack_from('>16H',kids[5].data,4)
    return np.array([[(c&31)*8,((c>>5)&31)*8,((c>>10)&31)*8] for c in v],np.float32)
def relabel(img,P,box,text,font,align='left',thr=110):
    """erase text pixels inside box (luminance > thr) by inpainting from non-text neighbours, then draw
    text in the brightest colour the old text used."""
    from PIL import Image,ImageDraw
    x0,y0,x1,y1=box; L=P@np.array([.3,.59,.11])
    sub=img[y0:y1+1,x0:x1+1]; txt=L[sub]>thr
    ink=int(max(np.unique(sub[txt]),key=lambda c:L[c])) if txt.any() else int(L.argmax())
    big=img.copy()
    # refill with the plain brushed-metal texture from inside the empty centre box (same rows)
    sx=TEX_X0
    big[y0:y1+1,x0:x1+1]=img[y0:y1+1,sx:sx+x1-x0+1]
    shadow=int(min(np.unique(img[y0:y1+1,sx:sx+x1-x0+1]),key=lambda c:L[c]))
    im=Image.new('L',(x1-x0+1,y1-y0+1),0); d=ImageDraw.Draw(im)
    bb=font.getbbox(text); tw=font.getlength(text)
    tx=2 if align=='left' else int((x1-x0+1-tw)//2)
    ty=((y1-y0+1)-(bb[3]-bb[1]))//2-bb[1]
    d.text((tx,ty),text,font=font,fill=255)
    m=np.asarray(im)>127
    s=np.zeros_like(m); s[1:,1:]=m[:-1,:-1]
    big[y0:y1+1,x0:x1+1][s&~m]=shadow
    big[y0:y1+1,x0:x1+1][m]=ink
    return big
import os
TEX_X0=110
_W=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LABELS=[((18,180,72,192),'부대 표시','nanum','center'),((18,200,72,212),'거점 표시','nanum','center'),
        ((256,178,350,188),'L-지상','g11','left'),((256,190,350,200),'R-우주','g11','left'),((256,202,350,213),'START-전환','g11','left')]
def apply(img,P):
    from PIL import ImageFont
    F={'nanum':ImageFont.truetype(os.path.join(os.path.dirname(_W),'NanumSquareNeo-cBd.ttf'),12),
       'g11':ImageFont.truetype(os.path.join(_W,'fonts','Galmuri11.ttf'),12)}
    for box,t,f,al in LABELS: img=relabel(img,P,box,t,F[f],al)
    return img
def pack(kids,img,W,H):
    cells=[]; idx={}; mp=[]
    for i in range(W*H):
        y,x=divmod(i,W); t=img[y*8:y*8+8,x*8:x*8+8].reshape(-1)
        b=bytes((t[0::2]<<4)|t[1::2])
        if b not in idx: idx[b]=len(cells); cells.append(b)
        mp.append(idx[b])
    cb=b''.join(cells)
    kids[3].data=struct.pack('>I',len(cb))+cb+kids[3].data[4+struct.unpack_from('>I',kids[3].data,0)[0]:]
    kids[4].data=struct.pack('>HH',W,H)+struct.pack('>%dH'%len(mp),*mp)+kids[4].data[4+W*H*2:]
    return len(cells)



