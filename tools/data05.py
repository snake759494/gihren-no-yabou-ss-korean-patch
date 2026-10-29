"""DATA05 entry0: development-screen NBG1 frame (8bpp cells + 44x28 map + palette) with baked labels."""
import struct, numpy as np
def unpack(d):
    nb=struct.unpack_from('>I',d,0x14)[0]; cells=d[0x18:0x18+nb]
    W,H=struct.unpack_from('>HH',d,0x521c-0x5204+0x14+nb+4) if False else struct.unpack_from('>HH',d,0x18+nb+4)
    mo=0x18+nb+8; mp=list(struct.unpack_from('>%dH'%(W*H),d,mo))
    po=mo+W*H*2; po+=-po%4
    pal=d[po+4:]; pal=pal+bytes(0x204-len(pal))
    img=np.zeros((H*8,W*8),np.uint8)
    for i,n in enumerate(mp):
        if n==0: continue
        k=(n-2)//2; t=np.frombuffer(cells[k*64:k*64+64],np.uint8).reshape(8,8)
        y,x=divmod(i,W); img[y*8:y*8+8,x*8:x*8+8]=t
    return img,W,H,mp,pal
def unpack_kids(kids):
    """same layout as a parsed container: kid0 = len + 8bpp cells, kid1 = W,H + map, kid2 = palette"""
    cb=kids[0].data; nb=struct.unpack_from('>I',cb,0)[0]; cells=cb[4:4+nb]
    W,H=struct.unpack_from('>HH',kids[1].data,0); mp=list(struct.unpack_from('>%dH'%(W*H),kids[1].data,4))
    img=np.zeros((H*8,W*8),np.uint8)
    for i,n in enumerate(mp):
        if n==0: continue
        k=(n-2)//2; t=np.frombuffer(cells[k*64:k*64+64],np.uint8).reshape(8,8)
        y,x=divmod(i,W); img[y*8:y*8+8,x*8:x*8+8]=t
    return img,W,H,mp
def pack_kids(kids,img,W,H,mp_old):
    cells=[]; idx={}; mp=[]
    for i in range(W*H):
        y,x=divmod(i,W); t=img[y*8:y*8+8,x*8:x*8+8].tobytes()
        if mp_old[i]==0 and not any(t): mp.append(0); continue
        if t not in idx: idx[t]=len(cells); cells.append(t)
        mp.append(2+idx[t]*2)
    cb=b''.join(cells)
    kids[0].data=struct.pack('>I',len(cb))+cb
    kids[1].data=struct.pack('>HH',W,H)+struct.pack('>%dH'%len(mp),*mp)+kids[1].data[4+W*H*2:]
    return len(cells)
def palette(pal):
    v=struct.unpack_from('>256H',pal,4)
    return np.array([[(c&31)*8,((c>>5)&31)*8,((c>>10)&31)*8] for c in v],np.float32)
def pack(img,W,H,mp_old,pal):
    import cont
    cells=[]; idx={}; mp=[]
    for i in range(W*H):
        y,x=divmod(i,W); t=img[y*8:y*8+8,x*8:x*8+8].tobytes()
        if mp_old[i]==0 and not any(t): mp.append(0); continue
        if t not in idx: idx[t]=len(cells); cells.append(t)
        mp.append(2+idx[t]*2)
    cb=b''.join(cells)
    e0=struct.pack('>I',len(cb))+cb
    e1=struct.pack('>HH',W,H)+struct.pack('>%dH'%len(mp),*mp)
    return cont.pack([e0,e1,pal]),len(cells)
