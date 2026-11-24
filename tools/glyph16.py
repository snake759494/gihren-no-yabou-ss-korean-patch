"""Redraw the 16x12 kanji glyphs (ranks / terrain aptitude) of the list sprite font in DATA02 entry2."""
import struct, os, numpy as np
from PIL import Image, ImageDraw, ImageFont
FONT=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'fonts','Galmuri11.ttf')
MAP={122:'육',123:'수',124:'공',125:'중',126:'사',127:'산',128:'숲',129:'하',130:'사',131:'상',132:'사',
     133:'소',134:'대',135:'위',136:'령',137:'장',138:'우'}
def glyph(ch,w=16,h=12):
    f=ImageFont.truetype(FONT,12); im=Image.new('L',(w,h),0)
    ImageDraw.Draw(im).text((0,-1),ch,font=f,fill=255)
    m=np.asarray(im)>127
    a=np.zeros((h,w),np.uint8)
    sh=np.zeros_like(m); sh[:,1:]=m[:,:-1]; a[sh & ~m]=6
    a[m]=7
    return a
def patch(kids):
    for i,ch in MAP.items():
        b=bytearray(kids[i].data); w,h=struct.unpack_from('>HH',b,4)
        a=glyph(ch,w,h).reshape(-1)
        b[8:8+w*h//2]=bytes((a[0::2]<<4)|a[1::2]); kids[i].data=bytes(b)

# Rank names are drawn from two glyph codes (glyph = 116 + code) chosen by a switch in PROG01/PROG03:
# 伍長(13,14) 軍曹(15,16) 曹長(16,14) ... 曹 is shared by 軍曹 (중사) and 曹長 (상사), so one glyph cannot
# serve both. 軍曹 now takes 中 (code 9, already '중') for its first glyph, freeing 軍 (131), which is
# redrawn as '상' and used as the first glyph of 曹長.
RANK_OLD=bytes.fromhex('e10f2410a027e010e110')   # mov #15,r1 ... mov #16,r0 ... mov #16,r1
RANK_NEW=bytes.fromhex('e1092410a027e010e10f')   # mov #9,r1  ... mov #16,r0 ... mov #15,r1
def patch_rank(prog):
    assert prog.count(RANK_OLD)==1, prog.count(RANK_OLD)
    return prog.replace(RANK_OLD,RANK_NEW)
