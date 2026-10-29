"""msub/subs.tsv (movie, start, end, Korean) -> msub/subs.json; lines wider than the band are split
at a space into consecutive timed parts."""
import os,sys,json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import msub
W=msub.W; MAXW=340
def width(t): return sum(msub.glyph(c)[1] for c in t)
def split(t):
    if width(t)<=MAXW: return [t]
    sp=[i for i,c in enumerate(t) if c==' ']
    best=min(sp,key=lambda i:abs(width(t[:i])-width(t[i+1:])))
    return split(t[:best])+split(t[best+1:])
out=[]
for l in open(os.path.join(W,'msub','subs.tsv'),encoding='utf8'):
    if not l.strip(): continue
    m,s,e,t=l.rstrip('\n').split('\t'); s=float(s); e=float(e)
    parts=split(t); tot=sum(len(p) for p in parts); a=s
    for p in parts:
        b=a+(e-s)*len(p)/tot; out.append(dict(movie=int(m),start=round(a,2),end=round(b,2),ko=p)); a=b
json.dump(out,open(os.path.join(W,'msub','subs.json'),'w',encoding='utf8'),ensure_ascii=False,indent=0)
print(len(out),'subtitles',len({c for o in out for c in o['ko']}),'glyphs')
