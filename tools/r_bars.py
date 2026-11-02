import numpy as np
from PIL import Image
exec(open('r_space2.py',encoding='utf8').read().split('e.cmd("save space"')[0])
for i in range(4): e.press(DOWN,40,40)
e.shot('../vd/bar_%s.png'%TAG); a=np.array(Image.open('../vd/bar_%s.png'%TAG).convert('RGB')).astype(int)
g=((abs(a[:,:,0]-a[:,:,1])<12)&(a[:,:,0]>120)&(a[:,:,0]<220)); print(TAG,int(g[180:,:].sum()))
