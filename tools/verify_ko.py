import json,glob,os,re,sys,collections
W=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L=json.load(open(os.path.join(W,'lines_ja.json'),encoding='utf8'))
by=collections.defaultdict(list)
for i,l in enumerate(L): by[l['file'].rsplit('_',1)[0]].append(i)
chunks=sys.argv[1:]
names=[]
for c in chunks: names+=open(os.path.join(W,c)).read().split()
tot=miss=jp=0
for n in names:
    p=os.path.join(W,'ko',n+'.json')
    if not os.path.exists(p): print('MISSING FILE',n); miss+=len(by[n]); continue
    d=json.load(open(p,encoding='utf8'))
    for i in by[n]:
        tot+=1
        if str(i) not in d: miss+=1; print('missing',n,i)
        elif re.search(r'[\u3040-\u30ff\u4e00-\u9fff]',d[str(i)]): jp+=1; print('JP',n,i,d[str(i)])
print('total',tot,'missing',miss,'jp',jp)
