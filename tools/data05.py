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
def unpack_kids(kids,base=2):
    """same layout as a parsed container: kid0 = len + 8bpp cells, kid1 = W,H + map, kid2 = palette.
    base: map value of cell 0. The production dock (DATA01) loads its cells at the character base,
    so map value n is cell n//2 (base=0, value 0 is a real cell)."""
    cb=kids[0].data; nb=struct.unpack_from('>I',cb,0)[0]; cells=cb[4:4+nb]
    W,H=struct.unpack_from('>HH',kids[1].data,0); mp=list(struct.unpack_from('>%dH'%(W*H),kids[1].data,4))
    img=np.zeros((H*8,W*8),np.uint8)
    for i,n in enumerate(mp):
        if n==0 and base: continue
        k=(n-base)//2; t=np.frombuffer(cells[k*64:k*64+64],np.uint8).reshape(8,8)
        y,x=divmod(i,W); img[y*8:y*8+8,x*8:x*8+8]=t
    return img,W,H,mp
def limit_cells(img,W,H,mp_old,maxcells):
    """merge the most similar 8x8 cells (fewest differing pixels) until the unique count fits the
    original VRAM budget; returns the image with merged cells written back"""
    img=img.copy()
    def uniq():
        u={}
        for i in range(W*H):
            y,x=divmod(i,W); t=img[y*8:y*8+8,x*8:x*8+8].tobytes()
            if mp_old[i]==0 and not any(t): continue
            u.setdefault(t,[]).append((y,x))
        return u
    u=uniq()
    while len(u)>maxcells:
        keys=list(u); A=np.frombuffer(b''.join(keys),np.uint8).reshape(-1,64)
        best=None
        for i in range(len(A)):
            d=(A[i+1:]!=A[i]).sum(1)
            if len(d):
                j=int(d.argmin())
                if best is None or d[j]<best[0]: best=(int(d[j]),i,i+1+j)
        _,i,j=best
        # keep the cell used more often, rewrite the other one's positions
        a,b=(i,j) if len(u[keys[i]])>=len(u[keys[j]]) else (j,i)
        cell=np.frombuffer(keys[a],np.uint8).reshape(8,8)
        for y,x in u[keys[b]]: img[y*8:y*8+8,x*8:x*8+8]=cell
        u=uniq()
    return img
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
def pack_kids_keep(kids,img,W,H,mp_old,maxcells=None,base=2):
    """like pack_kids, but every unchanged map position keeps its original cell number.
    The game writes run-time text (dock no., funds) straight into fixed cell numbers, so the
    original numbering must survive; only positions whose 8x8 tile changed get a cell that is
    no longer referenced by any unchanged position (or a new one at the end)."""
    cb=kids[0].data; nb=struct.unpack_from('>I',cb,0)[0]
    cells=[cb[4+k*64:4+k*64+64] for k in range(nb//64)]
    mp=list(mp_old); changed=[]
    for i in range(W*H):
        y,x=divmod(i,W); t=img[y*8:y*8+8,x*8:x*8+8].tobytes()
        n=mp_old[i]
        if base and n==0 and not any(t): continue
        if (n or not base) and cells[(n-base)//2]==t: continue
        changed.append((i,t))
    chg={i for i,_ in changed}
    keep={(mp_old[i]-base)//2 for i in range(W*H) if (mp_old[i] or not base) and i not in chg}
    # cells still used by an unchanged position stay; cells used only by changed positions are free,
    # except ones never referenced at all in the original map (run-time scratch cells)
    ref={(n-base)//2 for n in mp_old if n or not base}
    free=sorted(ref-keep)
    have={cells[k]:k for k in sorted(keep)}
    newt=[]
    for i,t in changed:
        if t not in have and t not in newt: newt.append(t)
    sub={}
    over=len(keep)+len(newt)+(len(cells)-len(ref))-(maxcells or 10**9)
    if over>0:
        # out of VRAM budget: the new tiles closest to an existing kept cell reuse that cell
        ks=sorted(keep); A=np.frombuffer(b''.join(cells[q] for q in ks),np.uint8).reshape(-1,64)
        sc=[]
        for t in newt:
            d=(A!=np.frombuffer(t,np.uint8)).sum(1); j=int(d.argmin()); sc.append((int(d[j]),t,ks[j]))
        for dd,t,k in sorted(sc,key=lambda z:z[0])[:over]: sub[t]=k
    for i,t in changed:
        if t in sub: k=sub[t]
        elif t in have: k=have[t]
        elif free: k=free.pop(0); cells[k]=t; have[t]=k
        else: k=len(cells); cells.append(t); have[t]=k
        mp[i]=base+k*2
    cb2=b''.join(cells)
    kids[0].data=struct.pack('>I',len(cb2))+cb2
    kids[1].data=struct.pack('>HH',W,H)+struct.pack('>%dH'%len(mp),*mp)+kids[1].data[4+W*H*2:]
    return len(cells)
