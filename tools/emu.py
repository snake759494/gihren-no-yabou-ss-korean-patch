import subprocess,sys,os
from PIL import Image
EXE=os.path.join(os.path.dirname(os.path.abspath(__file__)),'gverify.exe')
class Emu:
    def __init__(s,cue,bup=None):
        a=[EXE,cue]+([bup] if bup else [])
        s.p=subprocess.Popen(a,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True,creationflags=0x08000000)
        s.wait('READY')
    def wait(s,tok):
        while True:
            l=s.p.stdout.readline()
            if not l: raise RuntimeError('emu died')
            if l.startswith(tok): return l.strip()
    def cmd(s,c,tok):
        s.p.stdin.write(c+'\n');s.p.stdin.flush();return s.wait(tok)
    def run(s,n,mask=0): return s.cmd(f'run {n} {mask}','FRAME')
    def press(s,mask,hold=4,after=20): s.run(hold,mask);s.run(after,0)
    def shot(s,png):
        import time
        ppm=png+'.ppm';r=s.cmd('shot '+ppm,'SHOT')
        w,h=map(int,r.split()[-1].split('x'))
        for _ in range(100):
            try:
                if os.path.getsize(ppm)>=w*h*3: break
            except OSError: pass
            time.sleep(0.02)
        for _ in range(50):
            try:
                with Image.open(ppm) as im: im.load(); im.save(png)
                os.remove(ppm); break
            except OSError: time.sleep(0.05)
    def peek(s,a,n): return bytes(int(x,16) for x in s.cmd(f'peek {a:x} {n:x}','').split())
    def quit(s):
        try: s.p.stdin.write('quit\n');s.p.stdin.flush();s.p.wait(10)
        except Exception: s.p.kill()
# Saturn pad bits (active-low mask set): Right=0x8000? use ymir Button enum
RIGHT,LEFT,DOWN,UP,START,A,C,B,R,X,Y,Z,L=[1<<i for i in (15,14,13,12,11,10,9,8,7,6,5,4,3)]
