"""00000003.BIN: archive of (offset,size) u32 pairs, entries are MFD containers."""
import struct
def entries(d):
    out=[]; i=0; first=None
    while True:
        o,s=struct.unpack_from('>II',d,i*8)
        if i>0 and first is not None and i*8>=first: break
        if s and o: first=o if first is None else min(first,o)
        out.append((o,s)); i+=1
    return out
