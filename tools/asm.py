import sys,re
f,lo,hi=sys.argv[1],int(sys.argv[2],16),int(sys.argv[3],16)
for l in open(f,encoding='utf-8-sig',errors='replace'):
    m=re.match(r'\s*([0-9a-f]+):',l)
    if m and lo<=int(m.group(1),16)<=hi: print(l.rstrip())
