import sys,struct
f=open(sys.argv[1],'rb')
def sec(n):
    f.seek(n*2352+16);return f.read(2048)
pvd=sec(16)
root=pvd[156:190]
def walk(lba,size,path):
    data=b''.join(sec(lba+i) for i in range((size+2047)//2048))
    i=0
    while i<len(data):
        l=data[i]
        if l==0: i=(i//2048+1)*2048; continue
        e=data[i:i+l]; elba=struct.unpack('<I',e[2:6])[0]; esz=struct.unpack('<I',e[10:14])[0]
        nl=e[32]; name=e[33:33+nl]; fl=e[25]
        if name not in(b'\0',b'\1'):
            n=name.decode('latin1')
            if fl&2: walk(elba,esz,path+n+'/')
            else: print(f"{elba:7d} {esz:10d} {path}{n}")
        i+=l
walk(struct.unpack('<I',root[2:6])[0],struct.unpack('<I',root[10:14])[0],'/')
