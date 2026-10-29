"""search a VRAM dump for rows of label bitmaps: python vfind2.py dump MFDNAME..."""
import sys,os,struct,glob
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from mfdpack import split,decode
from cont import parse
from findimg import leaves
v=open(sys.argv[1],'rb').read()
for nm in sys.argv[2:]:
    for f in sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','disc',nm+'.MFD'))):
        ents,_=split(open(f,'rb').read())
        for ei,e in enumerate(ents):
            try: root=parse(decode(e))
            except Exception: continue
            for p,x in leaves(root):
                if len(x)<24: continue
                for off,hdr in ((8,4),(4,0)):
                    w,h=struct.unpack_from('>HH',x,hdr)
                    if not(8<=w<=704 and 2<=h<=512) or len(x)<off+w*h//2: continue
                    rb=w//2; hits=[]
                    for y in range(h):
                        row=x[off+y*rb:off+(y+1)*rb]
                        if len(set(row))>=4 and len(row)>=8:
                            i=v.find(row)
                            if i>=0: hits.append(i)
                    if hits: print(os.path.basename(f),ei,p,f'{w}x{h}','rows',len(hits),'/',h,hex(min(hits)))
