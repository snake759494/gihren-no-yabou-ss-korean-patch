import sys,json,glob,struct,os,collections;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from img4 import sub_entries
from helpimg import *
from PIL import Image
W=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ko={}
for f in glob.glob(os.path.join(W,'help','*.json')): ko.update(json.load(open(f,encoding='utf8')))
os.makedirs(os.path.join(W,'shots','help_ko'),exist_ok=True)
res=[]
for key,v in sorted(ko.items()):
    fam,e,i=key.rsplit('_',2)
    d=open(os.path.join(W,'dec',f'{fam}_{e}.bin'),'rb').read()
    out=sub_entries(d)[int(i)][3]
    w,h=struct.unpack_from('>HH',out,0); out=out+b'\0'*max(0,w*h//2+4-len(out))
    try:
        nb,info=render(out,v['title'],v['body'])
        Image.fromarray((arr_from(nb)*17).astype('uint8')).save(os.path.join(W,'shots','help_ko',key+'.png')); res.append((key,info))
    except Exception as ex: print('ERR',key,ex)
print(collections.Counter((i[0],i[1]) for k,i in res))
