"""2-byte Korean support for the 8x8 list font.
Encoding: Hangul syllable k (index in the glyph bank) -> bytes (0x80 + k//255, 1 + k%255).
The wrapper (kfont/kfont.bin), glyph count, 8x8 4bpp glyphs and relocated strings live in the unused
tail of the GFS directory table (0x06006E00..0x06009FF0), the only spot no game mode overwrites.
They ride at the end of 0.BIN and a boot hook (kfont/init.bin, entry literal at 0x0601000C) copies them there. The list-font tables in PROG01/03/04/05 map lead bytes 0x80..0x9F
to 0x4000+n so the wrapper recognises them."""
import os,struct,numpy as np
from PIL import Image,ImageDraw,ImageFont
W=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
G7=ImageFont.truetype(os.path.join(W,'fonts','Galmuri7.ttf'),8)
CODE_ADDR=0x06006E00; KNUM_ADDR=0x06006FFC; GLYPH_ADDR=0x06007000; LIMIT=0x06009FF0
TEMP_ADDR=0x06046000; ENTRY_LIT=0x0601000C; MAIN_INIT=0x0601125C
DRAW_PTR=0x06031708; ORIG_DRAW=0x0601462C
INK=7
def is_hangul(ch): return 0xAC00<=ord(ch)<=0xD7A3
def build_bank(syllables):
    out=bytearray()
    for ch in syllables:
        im=Image.new('L',(8,8),0); ImageDraw.Draw(im).text((0,0),ch,font=G7,fill=255)
        a=(np.asarray(im)>127).astype(np.uint8)*INK
        for y in range(8):
            for x in range(0,8,2): out.append((int(a[y,x])<<4)|int(a[y,x+1]))
    return bytes(out)
class Encoder:
    def __init__(s,syllables): s.idx={c:i for i,c in enumerate(syllables)}
    def enc(s,text):
        b=bytearray()
        for ch in text:
            if is_hangul(ch):
                k=s.idx[ch]; b+=bytes([0x80+k//255,1+k%255])
            else:
                o=ord(ch)
                if 0xff61<=o<=0xff9f: b+=ch.encode('cp932'); continue
                if not (0x20<=o<0x7f): raise ValueError(f'unsupported char {ch!r} in {text!r}')
                b.append(o)
        return bytes(b)
def pool_base(bank): return (GLYPH_ADDR+len(bank)+3)&~3
MSUB_CODE=0x06009B00; LW_ADDR=0x002F3800; LW_LIMIT=0x002FB000
def patch_main(main,bank,code,init,pool,mcode=b'',lw=b''):
    """mcode: movie subtitle code linked at MSUB_CODE (inside the payload); lw: data copied to LWRAM."""
    d=bytearray(main)
    assert struct.unpack_from('>I',d,DRAW_PTR-0x06010000)[0]==ORIG_DRAW
    assert struct.unpack_from('>I',d,ENTRY_LIT-0x06010000)[0]==MAIN_INIT
    struct.pack_into('>I',d,DRAW_PTR-0x06010000,CODE_ADDR)
    struct.pack_into('>I',d,ENTRY_LIT-0x06010000,TEMP_ADDR)
    pay=bytearray(code); pay+=bytes(KNUM_ADDR-CODE_ADDR-len(pay)); pay+=struct.pack('>I',len(bank)//32)
    pay+=bank; pay+=bytes(pool_base(bank)-CODE_ADDR-len(pay)); pay+=pool
    if mcode:
        assert CODE_ADDR+len(pay)<=MSUB_CODE, 'Korean payload overlaps the subtitle code'
        pay+=bytes(MSUB_CODE-CODE_ADDR-len(pay)); pay+=mcode+bytes(16)
    pay+=bytes(-len(pay)%4)
    assert CODE_ADDR+len(pay)<=LIMIT, 'Korean payload too large'
    lw=bytes(lw)+bytes(-len(lw)%4); assert LW_ADDR+len(lw)<=LW_LIMIT, 'subtitle data too large'
    ini=bytearray(init); struct.pack_into('>I',ini,0x30,len(pay)//4); struct.pack_into('>I',ini,0x38,len(lw)//4)
    d+=bytes(TEMP_ADDR-0x06010000-len(d)); d+=ini; d+=bytes(0x60-len(ini)); d+=pay; d+=lw
    return bytes(d)
TABLE_SIG=bytes.fromhex('ffffffffffffffffffff005effffffff')
def patch_table(prog):
    d=bytearray(prog); i=d.find(TABLE_SIG)
    assert i>=0 and d.find(TABLE_SIG,i+1)<0
    for c in range(0x80,0xA0):
        o=i+(c-0x20)*2
        assert struct.unpack_from('>h',d,o)[0]==-1
        struct.pack_into('>H',d,o,0x4000+(c-0x80))
    return bytes(d)
