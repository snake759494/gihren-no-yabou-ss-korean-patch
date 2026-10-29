"""render every VDP1 sprite of a VRAM dump: python v1sprites.py dump.v1 outdir"""
import sys,os,struct
from PIL import Image
v=open(sys.argv[1],'rb').read(); out=sys.argv[2]; os.makedirs(out,exist_ok=True)
a=0; seen=set(); n=0; stack=[]
for i in range(2000):
    ctrl=struct.unpack_from('>H',v,a)[0]
    if ctrl&0x8000: break
    cm=ctrl&15; jp=(ctrl>>12)&7
    pmod,colr,srca,size=struct.unpack_from('>HHHH',v,a+4)
    if cm in (0,1,2):
        w=((size>>8)&0x3f)*8; h=size&0xff; mode=(pmod>>3)&7; ca=srca*8
        key=(ca,w,h)
        if w and h and key not in seen and mode in (0,1):
            seen.add(key)
            px=v[ca:ca+w*h//2]
            im=Image.new('L',(w,h)); im.putdata([((px[(y*w+x)//2]>>(4*(1-x%2)))&15)*17 if (y*w+x)//2<len(px) else 0 for y in range(h) for x in range(w)])
            im.save(os.path.join(out,f'{n:03d}_{ca:05x}_{w}x{h}.png')); n+=1
    link=struct.unpack_from('>H',v,a+2)[0]*8; j=jp&3
    if j==0: a+=32
    elif j==1: a=link
    elif j==2: stack.append(a+32); a=link
    else: a=stack.pop() if stack else a+32
print(n)

