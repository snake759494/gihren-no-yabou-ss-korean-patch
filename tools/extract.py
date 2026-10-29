import sys,os
img=open(sys.argv[1],'rb'); out=sys.argv[2]; os.makedirs(out,exist_ok=True)
for line in open('files.txt'):
    lba,sz,name=line.split(); lba=int(lba); sz=int(sz); name=name.strip('/').split(';')[0]
    if name.endswith('.CAK') or name.endswith('.ADX') or name=='00000003.BIN': continue
    d=bytearray()
    for i in range((sz+2047)//2048):
        img.seek((lba+i)*2352+16); d+=img.read(2048)
    open(os.path.join(out,name),'wb').write(d[:sz])
