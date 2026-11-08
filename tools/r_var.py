import struct
e.cmd('disc '+CUE,'DISC')
exec(open('r_strat.py',encoding='utf8').read())
for i in range(300): e.press(C,4,60)
e.cmd('save sv','SAVED'); ST='sv'
exec(open('r_bspace.py',encoding='utf8').read())
v=open(f'../vd/v5{TAG}.v1','rb').read();i=0;n=0
for k in range(400):
    w=struct.unpack('>16H',v[i:i+32])
    if w[0]&0x8000: break
    n+=(w[4]==0xff28); j=(w[0]>>12)&7; i=(w[1]*8) if j in (1,2) else i+32
print('RESULT',TAG,n)
