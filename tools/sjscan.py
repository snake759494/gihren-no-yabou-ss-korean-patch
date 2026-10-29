import re,os,sys
pat=re.compile(rb'(?:[\x81-\x9f\xe0-\xef][\x40-\x7e\x80-\xfc]){4,}')
def runs(d):
    for m in pat.finditer(d):
        try: s=m.group().decode('cp932')
        except: continue
        # require some kana/kanji
        if sum(1 for ch in s if '\u3040'<=ch<='\u30ff' or '\u4e00'<=ch<='\u9fff')>=3: yield m.start(),s
if __name__=='__main__':
    tot={}
    for n in sorted(os.listdir(sys.argv[1])):
        d=open(os.path.join(sys.argv[1],n),'rb').read()
        r=list(runs(d))
        if r: tot[n]=(len(r),sum(len(s) for _,s in r),r[0][1][:30])
    for n,(a,b,c) in sorted(tot.items()): print(n,a,b,c)
