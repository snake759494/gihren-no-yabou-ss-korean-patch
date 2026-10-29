"""LZ-compressed label containers embedded in PROG overlays (phase titles etc.).
blobs(data) yields (offset of 0x1000 marker, groups, decoded bytes, end offset) for every embedded block that
decodes to a container of label bitmaps."""
import struct
from mfd import lz_dec
from cont import parse
from findimg import leaves
def labels(z):
    try: r=parse(z)
    except Exception: return None
    out=[]
    for p,x in leaves(r):
        if len(x)<12: continue
        w,h=struct.unpack_from('>HH',x,4)
        if 8<=w<=704 and 4<=h<=256 and len(x)>=8+w*h//2 and x[:4]==b'\0\0\0\0': out.append((p,w,h))
    return out or None
TITLES={0x182c:'전략 페이즈',0x1db8:'행동 설정 페이즈',0x24f0:'공격 실행 페이즈',0x2bd8:'국지전 페이즈',0x3254:'적 사고 페이즈'}
TABLE=0xf54   # PROG00 pointer table to the five blocks
def render_title(text,w,h,font='SeoulHangangEB.ttf',shear=0.22):
    """bold serif italic like the original Mincho titles: index 1 = brightest fill ... 7 = darkest edge, 0 = clear"""
    import os,numpy as np
    from PIL import Image,ImageDraw,ImageFont
    root=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    S=4; size=28
    while True:
        f=ImageFont.truetype(os.path.join(root,font),size*S)
        bb=f.getbbox(text); tw=(bb[2]-bb[0])/S+shear*h
        if tw<=w-4 or size<=14: break
        size-=1
    im=Image.new('L',(w*S,h*S),0)
    th=(bb[3]-bb[1])/S
    ImageDraw.Draw(im).text((2*S-bb[0],(h-th)/2*S-bb[1]),text,font=f,fill=255,stroke_width=3,stroke_fill=255)
    # italic: shift rows right proportional to height above baseline
    im=im.transform(im.size,Image.AFFINE,(1,shear,-shear*h*S,0,1,0),Image.BILINEAR)
    c=np.asarray(im.resize((w,h),Image.LANCZOS),np.float32)/255
    lum=np.array([216,192,144,104,80,48,8],np.float32)/216   # palette 1..7
    out=np.zeros((h,w),np.uint8)
    m=c>0.12
    out[m]=1+np.abs(c[m][:,None]-lum[None,:]).argmin(1)
    ol=np.zeros_like(m)
    for dy in (-1,0,1):
        for dx in (-1,0,1): ol|=np.roll(np.roll(m,dy,0),dx,1)
    out[ol&~m]=7
    return out
def patch_prog00(d):
    """re-render the five phase titles and repack them contiguously in their original region"""
    from cont import parse as cparse, build as cbuild
    from lzenc import compress
    from uilabel import enc_lab
    d=bytearray(d); offs=sorted(TITLES); start=offs[0]
    g=struct.unpack_from('>H',d,offs[-1]+2)[0]; _,limit=lz_dec(d,offs[-1]+4,g)
    blob=bytearray(); ptr={}
    for o in offs:
        g=struct.unpack_from('>H',d,o+2)[0]; z,_=lz_dec(d,o+4,g); r=cparse(bytes(z))
        x=r.kids[0].data; w,h=struct.unpack_from('>HH',x,4)
        r.kids[0].data=enc_lab(x,render_title(TITLES[o],w,h))
        nz=cbuild(r); cc,gg,left=compress(nz); assert left==0
        ptr[o]=start+len(blob); blob+=struct.pack('>HH',0x1000,gg)+cc; blob+=bytes(-len(blob)%2)
    assert start+len(blob)<=limit,(len(blob),limit-start)
    d[start:start+len(blob)]=blob
    for i,o in enumerate(offs):
        assert struct.unpack_from('>I',d,TABLE+4*i)[0]==0x6058000+o
        struct.pack_into('>I',d,TABLE+4*i,0x6058000+ptr[o])
    return bytes(d)
def blobs(d):
    o=0
    while True:
        o=d.find(b'\x10\x00',o)
        if o<0: return
        if o%2==0 and o+4<len(d):
            g=struct.unpack_from('>H',d,o+2)[0]
            if 0<g<2000:
                try:
                    z,end=lz_dec(d,o+4,g); z=bytes(z)
                    if len(z)>16 and labels(z): yield o,g,z,end
                except Exception: pass
        o+=2

