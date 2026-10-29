import struct
from scene import is_cont
# Container: [count][off_0..off_{n-1}][size_0] {data_0 pad4 [size_1]} {data_1 pad4 [size_2]} ... data_{n-1}
# size_i (exact data length) sits at off_i-4.
class Node:
    def __init__(s,kids=None,data=None): s.kids=kids; s.data=data
def parse(d,b=0,end=None,depth=0):
    if end is None:
        end=len(d); d=bytes(d)+bytes(256)
    if depth<6 and is_cont(d,b,end):
        c=struct.unpack_from('>I',d,b)[0]; offs=list(struct.unpack_from('>%dI'%c,d,b+4))
        kids=[]
        for i,o in enumerate(offs):
            s=b+o; sz=struct.unpack_from('>I',d,s-4)[0]
            e=b+offs[i+1]-4 if i+1<c else s+sz
            e2=min(e,s+sz) if sz<0x1000000 else e
            k=parse(d,s,e2,depth+1)
            if k.kids is None and len(k.data)<sz and sz-len(k.data)<=64: k.data=k.data+bytes(sz-len(k.data))
            kids.append(k)
        n=Node(kids=kids); n.tail=b''
        built=build(n)
        if end-b>len(built): n.tail=d[b+len(built):end]
        return n
    return Node(data=d[b:end])
def build(n):
    if n.kids is None: return n.data
    parts=[build(k) for k in n.kids]
    return pack(parts)+getattr(n,'tail',b'')
def pack(parts):
    c=len(parts); pos=4*(c+1); offs=[]; body=bytearray()
    for i,p in enumerate(parts):
        body+=struct.pack('>I',len(p)); pos+=4
        offs.append(pos); body+=p; pos+=len(p)
        if i+1<c:
            pad=-len(p)%4; body+=bytes(pad); pos+=pad
    return struct.pack('>%dI'%(c+1),c,*offs)+bytes(body)
