import sys,os,struct;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cont import parse
from uilabel import dec_lab
import numpy as np
from PIL import Image,ImageDraw
def view(dec,k,out,S=3,crop=None):
    W=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    r=parse(open(os.path.join(W,'dec',dec+'.bin'),'rb').read()); a=dec_lab(r.kids[k].data)
    if crop: x0,y0,x1,y1=crop; a=a[y0:y1,x0:x1]
    else: x0=y0=0
    h,w=a.shape
    im=Image.fromarray((a*17).astype(np.uint8)).convert('RGB').resize((w*S,h*S),Image.NEAREST)
    d=ImageDraw.Draw(im)
    for x in range(0,w,10): d.line([(x*S,0),(x*S,h*S)],fill=(255,0,0) if (x+x0)%50==0 else (90,0,0)); d.text((x*S+1,0),str(x+x0),fill=(255,255,0))
    for y in range(0,h,10): d.line([(0,y*S),(w*S,y*S)],fill=(0,255,0) if (y+y0)%50==0 else (0,90,0)); d.text((0,y*S+1),str(y+y0),fill=(0,255,255))
    im.save(out)
if __name__=='__main__':
    view(sys.argv[1],int(sys.argv[2]),sys.argv[3],crop=tuple(map(int,sys.argv[4].split(','))) if len(sys.argv)>4 else None)
