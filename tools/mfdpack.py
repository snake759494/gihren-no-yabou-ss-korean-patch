import struct
from mfd import lz_dec,lz_dec_b
from lzenc import compress,compress_b
from cont import pack
def split(d):
    c=struct.unpack_from('>I',d,0)[0]; offs=struct.unpack_from('>%dI'%c,d,4)
    ents=[]
    for o in offs:
        sz=struct.unpack_from('>I',d,o-4)[0]
        raw=d[o:o+sz]; raw=raw+bytes(sz-len(raw))
        typ,dest=struct.unpack_from('>II',raw,0)
        ents.append(dict(raw=raw,typ=typ,dest=dest,comp=(typ>>24)==1))
    return ents,None
def decode(ent):
    raw=ent['raw']
    if ent['comp']:
        mark,g=struct.unpack_from('>HH',raw,8)
        return bytes((lz_dec_b if mark&1 else lz_dec)(raw,12,g,len(raw))[0])
    return raw[8:]
def encode(ent,data):
    if ent['comp']:
        mark=struct.unpack_from('>H',ent['raw'],8)[0]
        c,g,left=(compress_b if mark&1 else compress)(data)
        return struct.pack('>IIHH',ent['typ'],ent['dest'],mark,g)+c
    return struct.pack('>II',ent['typ'],ent['dest'])+data
def join(raws,first=None):
    return pack(raws)
