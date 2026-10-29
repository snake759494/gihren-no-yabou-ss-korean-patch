import sys,struct,os;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from mfd import *
from PIL import Image
PAD=bytes(64)
def sub_entries(d):
    c=struct.unpack_from('>I',d,0)[0]
    offs=struct.unpack_from('>%dI'%(c+1),d,4)
    res=[]
    for o in offs[:c]:
        sz=struct.unpack_from('>I',d,o-4)[0]
        mk,g=struct.unpack_from('>HH',d,o)
        if mk!=0x1000: res.append((o,mk,g,None,o)); continue
        out,p=lz_dec(d+PAD,o+4,g,o+sz); res.append((o,mk,g,bytes(out),p))
    return res
def to_img(out):
    w,h=struct.unpack_from('>HH',out,0)
    px=out[4:]+bytes(4)
    im=Image.new('L',(w,h))
    im.putdata([((px[(y*w+x)//2]>>(4*(1-x%2)))&15)*17 for y in range(h) for x in range(w)])
    return im
