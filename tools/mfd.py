import struct
def lz_dec(d,pos,groups,end=None):
    """Word-flag LZ as used by the game's streaming decoder (mark 0x1000).
    groups full 16-item groups, then trailer [A][B]: if B>0 a final group of B-1 items (+2 pad bytes);
    finally A bytes are trimmed from the output."""
    out=bytearray()
    d=bytes(d)+bytes(64)
    def item(bit,pos):
        if bit: out.extend(d[pos:pos+2]); return pos+2
        b1=d[pos]; b2=d[pos+1]; pos+=2
        if b1&0xF0==0: out.extend(bytes([out[-1] if out else 0])*(((b1<<8)|b2)+3))
        else:
            ln=(b1>>4)+2; off=((b1&15)<<8)|b2
            for i in range(ln): out.append(out[-off] if off<=len(out) else 0)
        return pos
    for _ in range(groups):
        fl=(d[pos]<<8)|d[pos+1]; pos+=2
        for k in range(16): pos=item(fl>>k&1,pos)
    A=d[pos]; B=d[pos+1]; pos+=2
    if B>0:
        fl=(d[pos]<<8)|d[pos+1]; pos+=2
        for k in range(B): pos=item(fl>>k&1,pos)
    if A: del out[len(out)-A:]
    return out,pos
def parse(d):
    c=struct.unpack_from('>I',d,0)[0]
    offs=struct.unpack_from('>%dI'%c,d,4); ents=[]
    for o in offs:
        sz=struct.unpack_from('>I',d,o-4)[0]
        typ,dest=struct.unpack_from('>II',d,o)
        if typ>>24==1:
            mark,groups=struct.unpack_from('>HH',d,o+8)
            data,end=lz_dec(d,o+12,groups,o+sz)
            ents.append(dict(off=o,typ=typ,dest=dest,comp=True,mark=mark,data=bytes(data),end=end))
        else:
            ents.append(dict(off=o,typ=typ,dest=dest,comp=False,data=d[o+8:o+sz],end=o+sz))
    return ents,None
def lz_dec_b(d,pos,groups,end=None):
    """byte-mode variant (mark bit0=1): ref = 1 byte (len=(b1>>4)+1) or 0x1x long form (len=b3+17)."""
    out=bytearray(); d=bytes(d)+bytes(64)
    def item(bit,pos):
        if bit: out.extend(d[pos:pos+2]); return pos+2
        b1=d[pos]; pos+=1
        if b1&0xF0==0:
            b2=d[pos]; pos+=1; out.extend(bytes([out[-1] if out else 0])*(((b1<<8)|b2)+3)); return pos
        if b1&0xF0==0x10:
            b2=d[pos]; b3=d[pos+1]; pos+=2; ln=b3+17
        else:
            b2=d[pos]; pos+=1; ln=(b1>>4)+1
        off=((b1&15)<<8)|b2
        for i in range(ln): out.append(out[-off] if off<=len(out) else 0)
        return pos
    for _ in range(groups):
        fl=(d[pos]<<8)|d[pos+1]; pos+=2
        for k in range(16): pos=item(fl>>k&1,pos)
    A=d[pos]; B=d[pos+1]; pos+=2
    if B>0:
        fl=(d[pos]<<8)|d[pos+1]; pos+=2
        for k in range(B): pos=item(fl>>k&1,pos)
    if A: del out[len(out)-A:]
    return out,pos
