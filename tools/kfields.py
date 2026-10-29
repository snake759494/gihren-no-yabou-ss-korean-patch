"""GDATA string fields: (section, record size, string offset). maxlen measured across all files."""
import struct,re
L14={2:(34,0),7:(48,0),11:(52,0),12:(26,0),13:(36,0)}
L19={2:(34,0),10:(48,0)}
def fields(d,name):
    c=struct.unpack_from('>I',d,0)[0]; offs=struct.unpack_from('>%dI'%(c+1),d,4)
    lay=L14 if c==16 else L19
    for s,(rs,o) in lay.items():
        a,b=offs[s],offs[s+1]
        for r in range((b-a)//rs):
            p=a+r*rs+o; e=d.index(b'\x00',p)
            yield (s,p,d[p:e])
def prog_strings(d):
    for m in re.finditer(rb'(?<=\x00)[\x20-\x7e\xa1-\xdf]{2,}(?=\x00)',d):
        s=m.group()
        if sum(1 for b in s if 0xa6<=b<=0xdf)>=2: yield m.start(),s
