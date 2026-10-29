import sys;sys.path.insert(0,'.')
from emu import *
e=Emu("D:/ss/기렌의야망/Kidou Senshi Gundam - Gihren no Yabou (Japan).cue","D:/ss/기렌의야망/work/bup.bin")
for i in range(16):
    e.run(150, START if i%2 and i>4 else 0); e.shot(f'../shots/boot{i:02d}.png')
e.quit()
