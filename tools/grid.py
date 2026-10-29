from PIL import Image
import sys
def grid(files,out,cols=4,w=320,h=224):
    ims=[Image.open(f).convert('RGB').resize((w,h)) for f in files]
    rows=(len(ims)+cols-1)//cols
    c=Image.new('RGB',(w*cols,h*rows))
    for i,im in enumerate(ims): c.paste(im,((i%cols)*w,(i//cols)*h))
    c.save(out)
