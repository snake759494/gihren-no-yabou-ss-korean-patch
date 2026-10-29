"""find which decoded MFD entry holds a VRAM bitmap: python rowsrc.py dump.v1 addr w h [glob]"""
import sys,os,glob
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from mfdpack import split,decode
v=open(sys.argv[1],'rb').read(); a=int(sys.argv[2],16); w,h=int(sys.argv[3]),int(sys.argv[4]); pat=sys.argv[5] if len(sys.argv)>5 else '*'
rows=[v[a+y*w//2:a+(y+1)*w//2] for y in range(h)]; rows=[r for r in rows if len(set(r))>4]
for f in sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','disc',pat))):
    try: ents,_=split(open(f,'rb').read())
    except Exception: continue
    for ei,e in enumerate(ents):
        try: d=decode(e)
        except Exception: continue
        n=sum(1 for r in rows if r in d)
        if n: print(os.path.basename(f),ei,n,'/',len(rows),hex(d.find(rows[0])) if rows[0] in d else '')
