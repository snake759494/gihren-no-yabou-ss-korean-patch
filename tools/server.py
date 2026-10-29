import sys,os,time,traceback,io,contextlib
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from emu import *
Q=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','q')
os.makedirs(Q,exist_ok=True)
cue=sys.argv[1] if len(sys.argv)>1 else "D:/ss/기렌의야망/Kidou Senshi Gundam - Gihren no Yabou (Japan).cue"
e=Emu(cue,"D:/ss/기렌의야망/work/bup.bin")
g={'e':e,**{k:v for k,v in globals().items()}}
n=0
open(os.path.join(Q,'ready'),'w').write('1')
while True:
    f=os.path.join(Q,f'c{n}.py')
    if os.path.exists(f):
        time.sleep(0.05);src=open(f,encoding='utf8').read();buf=io.StringIO()
        try:
            with contextlib.redirect_stdout(buf): exec(src,g)
        except SystemExit: e.quit();break
        except Exception: buf.write(traceback.format_exc())
        open(os.path.join(Q,f'r{n}.txt'),'w',encoding='utf8').write(buf.getvalue()+'\n#DONE')
        n+=1
    else: time.sleep(0.05)
