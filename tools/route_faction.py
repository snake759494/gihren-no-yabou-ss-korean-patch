from grid import grid
import importlib,emu; importlib.reload(emu); e.__class__=emu.Emu
from PIL import Image
def scr():
    e.shot('../shots/t.png'); return Image.open('../shots/t.png').convert('RGB')
def is_faction(im): return im.width>=340 and sum(1 for x in range(20,190,10) if (lambda p:p[0]>100 and p[2]<40 and p[0]>2*p[1])(im.getpixel((x,98))))>8
def is_menu(im):
    if im.width<240: return False
    return any((lambda p:p[0]>150 and p[1]>120 and p[2]<90)(im.getpixel((x,147))) for x in range(120,230))
e.cmd('reset','RESET')
state='boot'
for i in range(400):
    e.run(30); im=scr()
    if is_faction(im): state='faction'; break
    if is_menu(im):
        e.press(C,4,10)
        for j in range(60):
            e.run(20); im=scr()
            if is_faction(im): state='faction'; break
        if state=='faction': break
    elif i>20 and i%5==0: e.press(START,4,10)
print('state',state,i)
e.run(60); e.shot('../shots/pre_c.png')
e.cmd('save faction','SAVED')
