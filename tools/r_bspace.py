import numpy as np
from PIL import Image
e.cmd('load '+ST,'LOADED'); e.press(B,4,40); e.run(30,B); e.run(6,B|X); e.run(70,B)
k=0
for d,n in ((DOWN,6),(LEFT,4),(UP,3),(RIGHT,8)):
    for i in range(n):
        e.run(30,B|d); e.run(30,B); e.shot(f"../vd/bs_{TAG}{k:02d}.png")
        if k==5: e.cmd(f"vdump ../vd/v5{TAG}","VDUMPED")
        k+=1
print(TAG,k)
