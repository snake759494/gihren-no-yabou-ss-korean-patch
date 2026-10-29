import pickle,json,collections,os
W=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(W)
order=pickle.load(open('glyph_order.pkl','rb')); bc,bs,cfg=pickle.load(open('ocr.pkl','rb'))
fix=json.load(open('glyph_fix.json',encoding='utf8'))
lab=[fix.get(str(i),bc[i]) for i in range(len(order))]
json.dump(lab,open('glyph_labels.json','w',encoding='utf8'),ensure_ascii=False)
idx={g:i for i,g in enumerate(order)}
lines=pickle.load(open('lines.pkl','rb'))
out=[dict(file=f,path=list(path),off=off,n=n,ja=''.join(lab[idx[g]] for g in gl)) for f,path,off,n,gl in lines]
json.dump(out,open('lines_ja.json','w',encoding='utf8'),ensure_ascii=False,indent=0)
by=collections.OrderedDict()
for i,l in enumerate(out): by.setdefault(l['file'].rsplit('_',1)[0],[]).append((i,l))
for f,items in by.items():
    with open(f'ja/{f}.txt','w',encoding='utf8') as o:
        prev=None
        for i,l in items:
            pg=tuple(l['path'][:-1])
            if pg!=prev: o.write(f'# page {list(pg)}\n'); prev=pg
            o.write(f'{i}\t{l["ja"]}\n')
