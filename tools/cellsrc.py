"""which decoded MFD entries contain the NBG cells used at map tiles: python cellsrc.py dump.v2 mapaddr charbase tx0 ty0 tx1 ty1 [glob]"""
import sys,os,struct,glob
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from mfdpack import split,decode
v=open(sys.argv[1],'rb').read(); ma,cb=int(sys.argv[2],16),int(sys.argv[3],16)
tx0,ty0,tx1,ty1=map(int,sys.argv[4:8]); pat=sys.argv[8] if len(sys.argv)>8 else '*'
cells=set()
for ty in range(ty0,ty1):
    for tx in range(tx0,tx1):
        pn=struct.unpack_from('>H',v,ma+(ty*64+tx)*2)[0]; c=v[cb+(pn&0xfff)*32:cb+(pn&0xfff)*32+32]
        if len(set(c))>3: cells.add(c)
print('cells',len(cells))
for f in sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','disc',pat+'.MFD'))):
    try: ents,_=split(open(f,'rb').read())
    except Exception: continue
    for ei,e in enumerate(ents):
        try: d=decode(e)
        except Exception: continue
        n=sum(1 for c in cells if c in d)
        if n: print(os.path.basename(f),ei,n,len(d))
