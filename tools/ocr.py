import pickle,numpy as np
from PIL import Image,ImageDraw,ImageFont
order=pickle.load(open('glyph_order.pkl','rb'))
def garr(g):
    a=np.array([((g[(y*16+x)//2]>>(4*(1-x%2)))&15) for y in range(16) for x in range(16)],float).reshape(16,16)/15
    return a
# candidate chars
cands=[]
for hi in list(range(0x81,0xa0))+list(range(0xe0,0xeb)):
    for lo in list(range(0x40,0x7f))+list(range(0x80,0xfd)):
        try: ch=bytes([hi,lo]).decode('cp932')
        except: continue
        if ch.isprintable() and ch.strip(): cands.append(ch)
cands+=list('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz')
print(len(cands))
fonts=[('C:/Windows/Fonts/msgothic.ttc',0),('C:/Windows/Fonts/YuGothM.ttc',0),('C:/Windows/Fonts/meiryo.ttc',0),('C:/Windows/Fonts/BIZ-UDGothicR.ttc',0)]
def render(ch,font,size,dx,dy):
    im=Image.new('L',(16,16),0); ImageDraw.Draw(im).text((dx,dy),ch,font=font,fill=255); return np.asarray(im,float)/255
G=np.stack([garr(g) for g in order])  # N,16,16
best_s=np.full(len(order),-1.0); best_c=['']*len(order); best_cfg=[None]*len(order)
Gv=G.reshape(len(order),-1); Gv=Gv-Gv.mean(1,keepdims=True); Gn=Gv/ (np.linalg.norm(Gv,axis=1,keepdims=True)+1e-9)
for fp,idx in fonts:
    for size in (14,15,16):
        font=ImageFont.truetype(fp,size,index=idx)
        for dx,dy in [(0,0),(0,-1),(1,0),(0,1),(1,-1),(1,1),(-1,0),(0,-2),(1,-2)]:
            C=np.stack([render(ch,font,size,dx,dy) for ch in cands]).reshape(len(cands),-1)
            C=C-C.mean(1,keepdims=True); Cn=C/(np.linalg.norm(C,axis=1,keepdims=True)+1e-9)
            S=Gn@Cn.T
            bi=S.argmax(1); bs=S.max(1)
            for i in np.where(bs>best_s)[0]:
                best_s[i]=bs[i]; best_c[i]=cands[bi[i]]; best_cfg[i]=(fp[-12:],size,dx,dy)
        print(fp,size,np.mean(best_s))
pickle.dump((best_c,best_s,best_cfg),open('ocr.pkl','wb'))
