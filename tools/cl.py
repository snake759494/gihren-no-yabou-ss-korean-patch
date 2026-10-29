import sys,os,time,glob
Q=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','q')
n=len(glob.glob(os.path.join(Q,'c*.py')))
src=open(sys.argv[1],encoding='utf8').read() if len(sys.argv)>1 and os.path.exists(sys.argv[1]) else sys.argv[1]
open(os.path.join(Q,f'c{n}.tmp'),'w',encoding='utf8').write(src); os.replace(os.path.join(Q,f'c{n}.tmp'),os.path.join(Q,f'c{n}.py'))
r=os.path.join(Q,f'r{n}.txt')
while True:
    if os.path.exists(r):
        t=open(r,encoding='utf8').read()
        if t.endswith('#DONE'): print(t[:-5]); break
    time.sleep(0.1)
