"""render NBG pages from a VDP2 VRAM dump (1-word PN, 12-bit char, 1x1 cells): python v2nbg.py dump.v2 mapaddr charbase bpp out.png"""
import sys,struct
from PIL import Image
v=open(sys.argv[1],'rb').read(); ma=int(sys.argv[2],16); cb=int(sys.argv[3],16); bpp=int(sys.argv[4])
im=Image.new('L',(512,512))
for ty in range(64):
    for tx in range(64):
        pn=struct.unpack_from('>H',v,ma+(ty*64+tx)*2)[0]
        c=cb+(pn&0xfff)*32
        for y in range(8):
            for x in range(8):
                if bpp==4: b=v[c+y*4+x//2]; p=(b>>(4*(1-x%2)))&15; p*=17
                else: p=v[c+y*8+x]
                im.putpixel((tx*8+x,ty*8+y),p)
im.save(sys.argv[5])
