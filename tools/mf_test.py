import sys,os;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from mfdpack import split,decode;from cont import parse
import mapframe as M
from PIL import Image,ImageFont
W=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ents,_=split(open(os.path.join(W,'disc','MAP0_Z.MFD'),'rb').read()); r=parse(decode(ents[0]))
img,w,h=M.unpack(r.kids); P=M.palette(r.kids)
img=M.apply(img,P)
Image.fromarray(P[img].astype('uint8')).crop((0,168,352,224)).resize((1056,168),0).save(os.path.join(W,'shots','mf2.png'))
print(M.pack(r.kids,img,w,h))
