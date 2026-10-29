exec(open('route_faction.py',encoding='utf8').read().split("e.cmd('reset'")[0])
def to_faction():
    e.cmd('reset','RESET'); state='boot'
    for i in range(400):
        e.run(30); im=scr()
        if is_faction(im): return True
        if is_menu(im):
            e.press(C,4,10)
            for j in range(60):
                e.run(20)
                if is_faction(scr()): return True
        elif i>20 and i%5==0: e.press(START,4,10)
    return False
fs=[]
for v in VARS:
    cue='D:/ss/기렌의야망/Kidou Senshi Gundam - Gihren no Yabou (Japan).cue' if v=='JP' else 'D:/ss/기렌의야망/work/variants/v_'+v+'.cue'
    e.cmd('disc '+cue,'DISC')
    ok=to_faction(); e.run(60); e.press(C,4,10); e.run(450)
    f='../shots/var_'+v+'.png'; e.shot(f); fs.append(f); print(v,ok)
if fs: grid(fs,'../shots/varg.png')
