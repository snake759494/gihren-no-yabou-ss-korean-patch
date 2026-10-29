import json,sys
ja=json.load(open('../kfont/ja_all.json',encoding='utf8'))['gdata']
tr={}
for l in open('../kfont/tr_g.txt',encoding='utf8'):
    l=l.rstrip('\n')
    if l: i=l.rindex('='); tr[l[:i]]=l[i+1:]
def bl(s): return sum(2 if ord(c)>=0x3000 else 1 for c in s)
print('missing',[k for k in ja if k not in tr])
for k,v in tr.items():
    if k in ja and bl(v)>ja[k]: print('LONG',k,v,bl(v),ja[k])
    if any(0xff61<=ord(c)<=0xff9f and c!='･' for c in v): print('KANA',k,v)
json.dump(tr,open('../kfont/tr_g.json','w',encoding='utf8'),ensure_ascii=False)
