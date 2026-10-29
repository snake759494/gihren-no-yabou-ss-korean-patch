import struct,os,numpy as np
from PIL import Image,ImageDraw,ImageFont
W=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
G11=ImageFont.truetype(os.path.join(W,'fonts','Galmuri11.ttf'),12)
G9=ImageFont.truetype(os.path.join(W,'fonts','Galmuri9.ttf'),10)
def dec_lab(x):
    w,h=struct.unpack_from('>HH',x,4)
    b=np.frombuffer(x[8:8+w*h//2],np.uint8); a=np.empty(w*h,np.uint8); a[0::2]=b>>4; a[1::2]=b&15
    return a.reshape(h,w).copy()
def enc_lab(x,a):
    h,w=a.shape; f=a.reshape(-1).astype(np.uint8)
    return x[:8]+bytes((f[0::2]<<4)|f[1::2])+x[8+w*h//2:]
def text_mask(text,font,w,h,x,y):
    im=Image.new('L',(w,h),0); ImageDraw.Draw(im).text((x,y),text,font=font,fill=255)
    return np.asarray(im)>127
def label(a,text,align='center',ink=None,bg=None,xpad=1,font=None):
    h,w=a.shape
    vals,cnt=np.unique(a,return_counts=True)
    if bg is None:
        bg=int(vals[cnt.argmax()])
    if ink is None:
        nz=[(c,v) for v,c in zip(vals,cnt) if v!=bg]
        ink=int(max(nz)[1]) if nz else 7
    font=font or G11
    if font.getlength(text)>w-2*xpad: font=G9
    tw=font.getlength(text)
    bb=font.getbbox(text) if text.strip() else (0,0,0,10)
    th=bb[3]-bb[1]
    y=(h-th)//2-bb[1]
    x=xpad if align=='left' else int((w-tw)//2)
    out=np.full_like(a,bg)
    out[text_mask(text,font,w,h,x,y)]=ink
    return out
def barlabel(a,rect,text,font=None,align='left',ink=None,pad=1):
    """rect=(x0,y0,x1,y1) inclusive, inside a label bar whose background varies per row only.
    The bar end is detected automatically (first column that no longer matches the row background),
    text pixels are replaced by the row background and Korean is drawn in the dark text colour."""
    x0,y0,x1,y1=rect
    a=a.copy()
    rowbg=a[y0:y1+1,x0].copy()
    xe=x0
    for x in range(x0,x1+1):
        col=a[y0:y1+1,x]
        match=((col==rowbg)|(col<rowbg)).mean()
        if match<0.6: break
        xe=x
    sub=a[y0:y1+1,x0:xe+1]
    m=sub!=rowbg[:,None]
    if ink is None:
        vals,cnt=np.unique(sub[m],return_counts=True)
        dark=[(c,v) for v,c in zip(vals,cnt) if v<rowbg.min()]
        ink=int(max(dark)[1]) if dark else (int(vals[cnt.argmax()]) if len(vals) else 0)
    ys,xs=np.where(m)
    tx0=int(xs.min()) if len(xs) else pad
    sub[:]=rowbg[:,None]
    font=font or G11
    w=xe-x0+1; h=y1-y0+1
    if font.getlength(text)>w-tx0-1: font=G9
    bb=font.getbbox(text); th=bb[3]-bb[1]
    ty=(h-th)//2-bb[1]
    tx=tx0 if align=='left' else int((w-font.getlength(text))//2)
    mk=text_mask(text,font,w,h,tx,ty)
    sub[mk]=ink
    a[y0:y1+1,x0:xe+1]=sub
    return a
TEXTSET={1,2,3,8,12,13}
def bar2(a,y0,y1,x0,x1,text,tx=None,ink=2,font=None,clear=True,ref=None):
    if font=='g9': font=G9
    elif font=='g11': font=G11
    """Label bar background = 2-colour dither per row. Pick the cleanest column pair inside the bar as
    reference, refill the bar, then draw Korean (Galmuri) in the light text colour."""
    a=a.copy()
    best=None
    for x in range(x0,x1):
        s=sum(1 for y in range(y0,y1+1) if a[y,x] in TEXTSET or a[y,x+1] in TEXTSET)
        if best is None or s<best[0]: best=(s,x)
    rx=best[1]
    sub=a[y0:y1+1,x0:x1+1]
    m=np.isin(sub,list(TEXTSET))
    ys,xs=np.where(m)
    first=int(xs.min()) if len(xs) else 1
    src=a.copy()
    if clear:
        for y in range(y0,y1+1):
            for x in range(x0,x1+1):
                if ref: a[y,x]=src[ref[1]+(y-y0),ref[0]+((x-ref[0])%2)]
                else: a[y,x]=src[y,rx+((x-rx)%2)]
    font=font or G11
    w=x1-x0+1; h=y1-y0+1
    tx=first if tx is None else tx-x0
    if font.getlength(text)>w-tx: font=G9
    bb=font.getbbox(text); th=bb[3]-bb[1]
    ty=(h-th)//2-bb[1]
    mk=text_mask(text,font,w,h,tx,ty)
    sub=a[y0:y1+1,x0:x1+1]; sub[mk]=ink
    return a
def name_label(a,text,x=12,ink=1):
    h,w=a.shape; out=np.zeros_like(a)
    font=G11
    if font.getlength(text)>w-x-2: font=G9
    if font.getlength(text)>w-x-2: x=max(2,w-2-int(font.getlength(text)))
    bb=font.getbbox(text); th=bb[3]-bb[1]
    y=5+(15-th)//2-bb[1]
    out[text_mask(text,font,w,h,x,y)]=ink
    return out
def map_legend(a,text,x=17,ink=1):
    a=a.copy(); a[:,x-1:]=0
    font=G11 if G11.getlength(text)<=a.shape[1]-x else G9
    bb=font.getbbox(text); th=bb[3]-bb[1]; y=6+(12-th)//2-bb[1]
    a[text_mask(text,font,a.shape[1],a.shape[0],x,y)]=ink
    return a
def map_button(a,text,ink=11):
    a=a.copy(); h,w=a.shape
    t0,t1,pr=(8,19,20) if h>=24 else (3,14,15)
    for y in range(t0,t1+1):
        for xx in range(9,w-6):
            a[y,xx]=a[pr+((y-t0)%2),9+(xx%2)]
    font=G11; tw=font.getlength(text)
    bb=font.getbbox(text); th=bb[3]-bb[1]; y=t0+((t1-t0+1)-th)//2-bb[1]
    x=int((w-tw)//2)
    a[text_mask(text,font,w,h,x,y)]=ink
    return a
def map_lr(a,text,ink=8,shadow=3,bgv=5):
    a=a.copy(); h,w=a.shape
    a[np.isin(a,[3,8,14,15])]=bgv
    for i,line in enumerate(text.split('|')):
        y0=1+i*12
        m=text_mask(line,G11,w,h,1,y0-1)
        sh=np.roll(np.roll(m,1,0),1,1)
        a[sh&~m]=shadow; a[m]=ink
    return a
