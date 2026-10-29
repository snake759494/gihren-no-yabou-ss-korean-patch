import struct
def tbl(d,base=0):
    c=struct.unpack_from('>I',d,base)[0]; v=struct.unpack_from('>%dI'%(c+1),d,base+4); return c,v
def is_cont(d,b,end):
    if b+8>end: return False
    c=struct.unpack_from('>I',d,b)[0]
    if not 0<c<300 or b+4*(c+2)>end: return False
    v=struct.unpack_from('>%dI'%(c+1),d,b+4)
    offs=v[:c]
    if offs[0]!=4*(c+2): return False
    if any(b+o>=end for o in offs): return False
    if list(offs)!=sorted(offs): return False
    return True
def walk(d,b=0,end=None,path=()):
    """yield (path, offset, w, h) for 16-wide glyph strips found recursively"""
    end=len(d) if end is None else end
    if not is_cont(d,b,end): return
    c,v=tbl(d,b); offs=list(v[:c])
    for i,o in enumerate(offs):
        s=b+o; e=b+offs[i+1] if i+1<c else end
        if is_cont(d,s,e):
            yield from walk(d,s,e,path+(i,))
        elif e-s>=4:
            w,h=struct.unpack_from('>HH',d,s)
            if w==16 and h>=16 and h%16==0 and e-s>=4+w*h//2 and e-s<=4+w*h//2+8:
                yield (path+(i,),s,w,h)
