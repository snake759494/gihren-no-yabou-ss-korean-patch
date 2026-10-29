import capstone as c,sys
md=c.Cs(c.CS_ARCH_SH, c.CS_MODE_SH2|c.CS_MODE_BIG_ENDIAN)
d=open(sys.argv[1],'rb').read(); a=int(sys.argv[2],16); n=int(sys.argv[3],16); B=0x6000000
for x in range(a,a+n,2):
    l=list(md.disasm(d[x-B:x-B+2],x))
    if not l: print(hex(x),'.word %04x'%int.from_bytes(d[x-B:x-B+2],'big')); continue
    i=l[0]; extra=''
    if i.mnemonic in('mov.l','mov.w') and i.op_str.startswith('0x'):
        p=int(i.op_str.split(',')[0],16); k=4 if i.mnemonic=='mov.l' else 2
        extra='   ; =%0*x'%(k*2,int.from_bytes(d[p-B:p-B+k],'big'))
    print(hex(x),i.mnemonic,i.op_str,extra)
