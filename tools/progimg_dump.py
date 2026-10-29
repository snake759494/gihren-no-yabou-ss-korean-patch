import sys,glob,os;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from mfdpack import split,decode
import progimg
from uilabel import dec_lab
from cont import parse
from findimg import leaves
from PIL import Image
W=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out=os.path.join(W,'shots','pi'); os.makedirs(out,exist_ok=True)
for f in sorted(glob.glob(os.path.join(W,'disc','PROG*.MFD'))+glob.glob(os.path.join(W,'disc','0000000[12].BIN'))):
    raw=open(f,'rb').read()
    try: ds=[decode(e) for e in split(raw)[0]]
    except Exception: ds=[raw]
    for i,d in enumerate(ds):
        for o,g,z,end in progimg.blobs(d):
            L=progimg.labels(z); nm=os.path.basename(f)[:-4]
            print(nm,i,hex(o),g,len(z),[(w,h) for p,w,h in L])
            for p,w,h in L:
                x=parse(z)
                for k in p: x=x.kids[k]
                x=x.data
                a=dec_lab(x); Image.fromarray((a*17).astype('uint8')).save(os.path.join(out,f'{nm}_{i}_{o:x}_{"_".join(map(str,p))}.png'))

