import json,sys
f='glyph_fix.json'; d=json.load(open(f,encoding='utf8'))
for item in sys.argv[1:]:
    k,v=item.split('=',1); d[k]=v
json.dump(d,open(f,'w',encoding='utf8'),ensure_ascii=False,indent=0)
print(len(d))
