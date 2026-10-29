import sys,os,struct;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cont import parse
from mfd import lz_dec
def leaves(n,path=()):
    if n.kids is None: yield path,n.data; return
    for i,k in enumerate(n.kids): yield from leaves(k,path+(i,))
def images(d):
    """yield (path, w, h, bpp, pixelbytes)"""
    for path,data in leaves(parse(d)):
        cand=[(path,data)]
        if len(data)>8 and data[:2]==b'\x10\x00':
            g=struct.unpack_from('>H',data,2)[0]
            try: cand.append((path+('z',),bytes(lz_dec(data+bytes(64),4,g)[0])))
            except Exception: pass
        for p,x in cand:
            if len(x)<8: continue
            w,h=struct.unpack_from('>HH',x,0)
            if 8<=w<=704 and 4<=h<=512:
                if abs(len(x)-4-w*h//2)<=8: yield p,w,h,4,x[4:4+w*h//2]
                elif abs(len(x)-4-w*h)<=8: yield p,w,h,8,x[4:4+w*h]
