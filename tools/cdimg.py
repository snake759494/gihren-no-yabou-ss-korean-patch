import struct
# ---- EDC/ECC (Mode 1) ----
_edc=[0]*256
for i in range(256):
    e=i
    for _ in range(8): e=(e>>1)^(0xD8018001 if e&1 else 0)
    _edc[i]=e
_ef=[0]*256; _eb=[0]*256
for i in range(256):
    j=(i<<1)^(0x11D if i&0x80 else 0); _ef[i]=j; _eb[i^j]=i
def edc(d):
    e=0
    for b in d: e=(e>>8)^_edc[(e^b)&0xFF]
    return e
def _ecc_pq(sec,major,minor,mmult,minc,off):
    size=major*minor
    for ma in range(major):
        idx=(ma>>1)*mmult+(ma&1); a=0;b=0
        for mi in range(minor):
            t=sec[12+idx]; idx+=minc
            if idx>=size: idx-=size
            a^=t; b^=t; a=_ef[a]
        a=_eb[_ef[a]^b]
        sec[off+ma]=a; sec[off+ma+major]=a^b
def fix_sector(sec):
    sec[0x810:0x814]=struct.pack('<I',edc(sec[0:0x810]))
    sec[0x814:0x81C]=b'\0'*8
    _ecc_pq(sec,86,24,2,86,0x81C)
    _ecc_pq(sec,52,43,86,88,0x81C+172)
def msf(lba):
    l=lba+150; return bytes([((l//4500)//10<<4)|((l//4500)%10),(((l//75)%60)//10<<4)|((l//75)%60)%10,((l%75)//10<<4)|(l%75)%10])
def make_sector(lba,data):
    s=bytearray(2352); s[0:12]=b'\x00'+b'\xff'*10+b'\x00'; s[12:15]=msf(lba); s[15]=1
    s[16:16+len(data)]=data; fix_sector(s); return s
class Image:
    def __init__(s,path):
        s.b=bytearray(open(path,'rb').read()); s.nsec=len(s.b)//2352
        s.dirty=set()
    def read(s,lba,n=1): return b''.join(bytes(s.b[(lba+i)*2352+16:(lba+i)*2352+2064]) for i in range(n))
    def write_data(s,lba,data):
        for i in range(0,len(data),2048):
            chunk=data[i:i+2048]; chunk=chunk+b'\0'*(2048-len(chunk))
            L=lba+i//2048
            if L>=s.nsec:
                s.b+=bytearray(2352*(L-s.nsec+1)); s.nsec=L+1
            s.b[L*2352:(L+1)*2352]=make_sector(L,chunk)
    def dir_entries(s):
        pvd=s.read(16); root=pvd[156:190]; res=[]
        def walk(lba,size,path):
            nsec=(size+2047)//2048
            for k in range(nsec):
                data=s.read(lba+k); i=0
                while i<2048:
                    l=data[i]
                    if l==0: break
                    e=data[i:i+l]; elba=struct.unpack('<I',e[2:6])[0]; esz=struct.unpack('<I',e[10:14])[0]
                    nl=e[32]; name=e[33:33+nl].decode('latin1'); fl=e[25]
                    if name not in('\0','\1'):
                        if fl&2: walk(elba,esz,path+name+'/')
                        else: res.append(dict(name=(path+name).split(';')[0],lba=elba,size=esz,dsec=lba+k,doff=i))
                    i+=l
        walk(struct.unpack('<I',root[2:6])[0],struct.unpack('<I',root[10:14])[0],'')
        return res
    def set_entry(s,ent,lba,size):
        sec=bytearray(s.read(ent['dsec'])); o=ent['doff']
        sec[o+2:o+10]=struct.pack('<I',lba)+struct.pack('>I',lba)
        sec[o+10:o+18]=struct.pack('<I',size)+struct.pack('>I',size)
        s.write_data(ent['dsec'],bytes(sec))
    def set_volume_size(s,n):
        pvd=bytearray(s.read(16)); pvd[80:88]=struct.pack('<I',n)+struct.pack('>I',n); s.write_data(16,bytes(pvd))
    def save(s,path): open(path,'wb').write(s.b)
