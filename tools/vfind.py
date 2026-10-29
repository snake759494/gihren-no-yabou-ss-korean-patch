"""find label bitmaps of a decoded MFD entry inside a VDP1 VRAM dump: python vfind.py dump.v1 MAP0_Z [entry]"""
import sys,os,struct,glob
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from mfdpack import split,decode
from cont import parse
from findimg import leaves
v=open(sys.argv[1],'rb').read()
for nm in sys.argv[2:]:
    for f in sorted(glob.glob(os.path.join(os.path.dirname(__file__),'..','disc',nm+'.MFD'))):
        ents,_=split(open(f,'rb').read())
        for ei,e in enumerate(ents):
            for p,x in leaves(parse(decode(e))):
                if len(x)<40: continue
                k=x[8:40]
                i=v.find(k)
                if i>=0: print(os.path.basename(f),ei,p,len(x),hex(i))
