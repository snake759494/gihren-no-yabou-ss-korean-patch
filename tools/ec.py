# send code to server: python ec.py "code" or file
import sys,os,time,glob
Q=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','q')
src=sys.argv[1]
if os.path.exists(src): src=open(src,encoding='utf8').read()
n=len(glob.glob(os.path.join(Q,'c*.py')))
open(os.path.join(Q,f'c{n}.tmp'),'w',encoding='utf8').write(src); os.replace(os.path.join(Q,f'c{n}.tmp'),os.path.join(Q,f'c{n}.py'))
r=os.path.join(Q,f'r{n}.txt')
while not (os.path.exists(r) and open(r,encoding='utf8').read().endswith('#DONE')): time.sleep(0.1)
print(open(r,encoding='utf8').read()[:-6])
