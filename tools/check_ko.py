import sys,os,json,glob
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from render import render_line
W=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L=json.load(open(os.path.join(W,'lines_ja.json'),encoding='utf8'))
files=sys.argv[1:] or sorted(glob.glob(os.path.join(W,'ko','*.json')))
bad=0
for f in files:
    d=json.load(open(f,encoding='utf8'))
    for k,v in d.items():
        i=int(k)
        if not (0<=i<len(L)): print(f,'BAD INDEX',k); bad+=1; continue
        q,c=render_line(v,'NanumSquareNeo-cBd.ttf',15)
        if c>20: print(f,k,'TOO LONG',c,v); bad+=1
        for ch in v:
            if ord(ch)<32: print(f,k,'CTRL'); bad+=1
print('problems',bad)
