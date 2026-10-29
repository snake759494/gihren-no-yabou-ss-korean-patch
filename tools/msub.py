"""Movie subtitles. The movie library's per-frame task entry in the main jump table (0x060315FC+0x29C)
is redirected to msub/msub.bin (linked at 0x06009B00 inside the Korean font payload), which runs the
original task and draws the line for the current video frame into the bottom black band of the NBG0
movie bitmap. Subtitle data lives in LWRAM 0x002F3800 (copied there at boot by kfont/init.bin).
Movies are identified by the start FAD of the playing file."""
import os,struct,json,numpy as np
from PIL import Image,ImageDraw,ImageFont
W=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLE=0x060315FC+0x29C; ORIG=0x0601DBFA; CODE=0x06009B00
FPS=15.0
FONT=ImageFont.truetype(os.path.join(W,'fonts','Galmuri9.ttf'),10)
def glyph(ch):
    im=Image.new('L',(16,12),0); ImageDraw.Draw(im).text((0,0),ch,font=FONT,fill=255)
    a=np.asarray(im)>127
    assert not a[0].any() and not a[11].any(), ch
    adv=int(round(FONT.getlength(ch))) or 4
    rows=[int(''.join('1' if v else '0' for v in r),2) for r in a[1:11]]
    return rows,adv
def build(subs,fads):
    """subs: [dict(movie=int,start=sec,end=sec,ko=str)], fads: {movie number: start FAD} -> LWRAM blob"""
    movies=sorted({s['movie'] for s in subs}); mi={m:i for i,m in enumerate(movies)}
    chars=sorted({c for s in subs for c in s['ko']}); gi={c:i for i,c in enumerate(chars)}
    gly=bytearray()
    for c in chars:
        rows,adv=glyph(c); gly+=struct.pack('>11H',*rows,adv)
    txt=bytearray(); tab=bytearray()
    for s in sorted(subs,key=lambda s:(s['movie'],s['start'])):
        w=sum(glyph(c)[1] for c in s['ko']); assert w<=350 and len(s['ko'])<64, (s['ko'],w)
        off=len(txt)//2; txt+=struct.pack('>%dH'%len(s['ko']),*[gi[c] for c in s['ko']])+bytes([0xff,0xff])
        tab+=struct.pack('>4H',mi[s['movie']],int(s['start']*FPS),int(s['end']*FPS+0.5),off)
    fad=b''.join(struct.pack('>I',fads[m]) for m in movies)
    o=28; offs=[o,o+len(fad),o+len(fad)+len(tab),o+len(fad)+len(tab)+len(gly)]
    return struct.pack('>7I',0x4B535542,len(subs),len(movies),*offs)+fad+tab+gly+txt
def code(): return open(os.path.join(W,'msub','msub.bin'),'rb').read()
def patch_main(main):
    d=bytearray(main); o=TABLE-0x06010000
    assert struct.unpack_from('>I',d,o)[0]==ORIG; struct.pack_into('>I',d,o,CODE); return bytes(d)
